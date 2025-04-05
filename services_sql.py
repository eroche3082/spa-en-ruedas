import uuid
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from models_sql import db, Servicio, Ubicacion, Evento, Reservacion, Cliente, Pago, Mensaje, Usuario

def get_all_services() -> List[Dict[str, Any]]:
    """Obtener todos los servicios de spa activos."""
    servicios = Servicio.query.filter_by(activo=True).all()
    return [
        {
            "id": servicio.id,
            "nombre": servicio.nombre,
            "descripcion": servicio.descripcion,
            "precio": servicio.precio,
            "duracion": servicio.duracion,
            "imagen": servicio.imagen,
            "categoria": servicio.categoria
        }
        for servicio in servicios
    ]

def get_service_by_id(service_id: int) -> Optional[Dict[str, Any]]:
    """Obtener un servicio por ID."""
    servicio = Servicio.query.get(service_id)
    if not servicio:
        return None
        
    return {
        "id": servicio.id,
        "nombre": servicio.nombre,
        "descripcion": servicio.descripcion,
        "precio": servicio.precio,
        "duracion": servicio.duracion,
        "imagen": servicio.imagen,
        "categoria": servicio.categoria
    }

def get_all_events() -> List[Dict[str, Any]]:
    """Obtener todos los eventos futuros."""
    hoy = datetime.now().date()
    eventos = Evento.query.filter(Evento.fecha >= hoy).order_by(Evento.fecha).all()
    
    return [
        {
            "id": evento.id,
            "titulo": evento.titulo,
            "descripcion": evento.descripcion,
            "fecha": evento.fecha.strftime("%Y-%m-%d"),
            "ubicacion_id": evento.ubicacion_id,
            "ubicacion_nombre": evento.ubicacion.nombre
        }
        for evento in eventos
    ]

def get_all_locations() -> List[Dict[str, Any]]:
    """Obtener todas las ubicaciones activas."""
    ubicaciones = Ubicacion.query.filter_by(activo=True).all()
    
    return [
        {
            "id": ubicacion.id,
            "nombre": ubicacion.nombre,
            "direccion": ubicacion.direccion,
            "descripcion": ubicacion.descripcion,
            "imagen": ubicacion.imagen
        }
        for ubicacion in ubicaciones
    ]

def create_or_get_client(client_data: Dict[str, Any]) -> Cliente:
    """Crear un nuevo cliente o recuperar uno existente."""
    # Verificar si el cliente ya existe por email
    cliente = Cliente.query.filter_by(email=client_data["email"]).first()
    
    if not cliente:
        # Crear nuevo cliente
        cliente = Cliente(
            nombre=client_data["nombre"],
            email=client_data["email"],
            telefono=client_data.get("telefono", "")
        )
        db.session.add(cliente)
        db.session.commit()
        
    return cliente

def generate_confirmation_code() -> str:
    """Generar un código de confirmación único."""
    # Generamos un código alfanumérico de 8 caracteres
    chars = string.ascii_uppercase + string.digits
    code = 'SR-' + ''.join(random.choice(chars) for _ in range(8))
    
    # Verificar que el código no exista
    while Reservacion.query.filter_by(codigo_confirmacion=code).first():
        code = 'SR-' + ''.join(random.choice(chars) for _ in range(8))
        
    return code

def create_booking(booking_data: Dict[str, Any]) -> Dict[str, Any]:
    """Crear una nueva reservación."""
    # Crear o recuperar cliente
    cliente = create_or_get_client({
        "nombre": booking_data["nombre"],
        "email": booking_data["email"],
        "telefono": booking_data.get("telefono", "")
    })
    
    # Convertir string de fecha y hora a objetos datetime
    fecha = datetime.strptime(booking_data["fecha"], "%Y-%m-%d").date()
    hora = datetime.strptime(booking_data["hora"], "%H:%M").time()
    
    # Crear la reservación
    reservacion = Reservacion(
        cliente_id=cliente.id,
        servicio_id=booking_data["servicio_id"],
        ubicacion_id=booking_data["ubicacion_id"],
        fecha=fecha,
        hora=hora,
        estado="pendiente",
        comentarios=booking_data.get("comentarios", ""),
        codigo_confirmacion=generate_confirmation_code()
    )
    
    db.session.add(reservacion)
    db.session.commit()
    
    # Obtener nombres de servicio y ubicación
    servicio = Servicio.query.get(reservacion.servicio_id)
    ubicacion = Ubicacion.query.get(reservacion.ubicacion_id)
    
    return {
        "id": reservacion.id,
        "cliente": {
            "id": cliente.id,
            "nombre": cliente.nombre,
            "email": cliente.email,
            "telefono": cliente.telefono
        },
        "servicio": {
            "id": servicio.id,
            "nombre": servicio.nombre,
            "precio": servicio.precio
        },
        "ubicacion": {
            "id": ubicacion.id,
            "nombre": ubicacion.nombre
        },
        "fecha": fecha.strftime("%Y-%m-%d"),
        "hora": hora.strftime("%H:%M"),
        "estado": reservacion.estado,
        "codigo_confirmacion": reservacion.codigo_confirmacion,
        "fecha_creacion": reservacion.fecha_creacion.isoformat()
    }

def get_booking(booking_id: int) -> Optional[Dict[str, Any]]:
    """Obtener una reservación por ID."""
    reservacion = Reservacion.query.get(booking_id)
    if not reservacion:
        return None
        
    cliente = Cliente.query.get(reservacion.cliente_id)
    servicio = Servicio.query.get(reservacion.servicio_id)
    ubicacion = Ubicacion.query.get(reservacion.ubicacion_id)
    
    return {
        "id": reservacion.id,
        "cliente": {
            "id": cliente.id,
            "nombre": cliente.nombre,
            "email": cliente.email,
            "telefono": cliente.telefono
        },
        "servicio": {
            "id": servicio.id,
            "nombre": servicio.nombre,
            "precio": servicio.precio
        },
        "ubicacion": {
            "id": ubicacion.id,
            "nombre": ubicacion.nombre
        },
        "fecha": reservacion.fecha.strftime("%Y-%m-%d"),
        "hora": reservacion.hora.strftime("%H:%M"),
        "estado": reservacion.estado,
        "codigo_confirmacion": reservacion.codigo_confirmacion,
        "fecha_creacion": reservacion.fecha_creacion.isoformat()
    }

def get_booking_by_confirmation(confirmation_code: str) -> Optional[Dict[str, Any]]:
    """Obtener una reservación por código de confirmación."""
    reservacion = Reservacion.query.filter_by(codigo_confirmacion=confirmation_code).first()
    if not reservacion:
        return None
    
    return get_booking(reservacion.id)

def process_payment(payment_data: Dict[str, Any]) -> Dict[str, Any]:
    """Procesar un pago."""
    reservacion_id = payment_data["reservacion_id"]
    
    # Generar referencia
    reference = payment_data.get("referencia")
    if not reference:
        # Si no hay referencia (ej. de Stripe), generar una
        reference = f"PAY-{uuid.uuid4().hex[:8].upper()}"
    
    # Crear registro de pago
    pago = Pago(
        reservacion_id=reservacion_id,
        monto=payment_data["monto"],
        metodo=payment_data["metodo"],
        estado="completado",
        referencia=reference
    )
    
    db.session.add(pago)
    
    # Actualizar estado de la reservación
    reservacion = Reservacion.query.get(reservacion_id)
    reservacion.estado = "confirmada"
    
    db.session.commit()
    
    return {
        "payment_id": pago.id,
        "status": "success",
        "amount": pago.monto,
        "reference": pago.referencia,
        "timestamp": pago.fecha.isoformat(),
        "metodo": pago.metodo,
        "confirmation_code": reservacion.codigo_confirmacion,
        "fecha": pago.fecha.strftime("%d/%m/%Y %H:%M")
    }

def get_available_slots(date_str: str, location_id: int) -> List[str]:
    """Obtener slots de tiempo disponibles para una fecha y ubicación específica."""
    fecha = datetime.strptime(date_str, "%Y-%m-%d").date()
    
    # Horarios base (9am a 6pm, saltando de hora en hora)
    all_slots = ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00"]
    
    # Obtener reservaciones existentes para esa fecha y ubicación
    reservaciones = Reservacion.query.filter_by(
        fecha=fecha, 
        ubicacion_id=location_id,
        estado="confirmada"
    ).all()
    
    # Convertir horas de reservaciones a strings (formato HH:MM)
    reserved_times = [r.hora.strftime("%H:%M") for r in reservaciones]
    
    # Filtrar slots disponibles
    available_slots = [slot for slot in all_slots if slot not in reserved_times]
    
    return available_slots

def create_contact_message(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Crear un nuevo mensaje de contacto."""
    mensaje = Mensaje(
        nombre=message_data["nombre"],
        email=message_data["email"],
        asunto=message_data.get("asunto", "Contacto desde la web"),
        mensaje=message_data["mensaje"]
    )
    
    db.session.add(mensaje)
    db.session.commit()
    
    return {
        "id": mensaje.id,
        "nombre": mensaje.nombre,
        "email": mensaje.email,
        "asunto": mensaje.asunto,
        "fecha": mensaje.fecha.isoformat()
    }

# Funciones administrativas

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Autenticar un usuario por email y contraseña."""
    usuario = Usuario.query.filter_by(email=email, activo=True).first()
    
    if not usuario or not usuario.check_password(password):
        return None
        
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "rol": usuario.rol
    }

def get_all_bookings() -> List[Dict[str, Any]]:
    """Obtener todas las reservaciones."""
    reservaciones = Reservacion.query.order_by(Reservacion.fecha.desc(), Reservacion.hora).all()
    
    return [
        {
            "id": r.id,
            "cliente_nombre": Cliente.query.get(r.cliente_id).nombre,
            "servicio_nombre": Servicio.query.get(r.servicio_id).nombre,
            "ubicacion_nombre": Ubicacion.query.get(r.ubicacion_id).nombre,
            "fecha": r.fecha.strftime("%Y-%m-%d"),
            "hora": r.hora.strftime("%H:%M"),
            "estado": r.estado,
            "codigo_confirmacion": r.codigo_confirmacion
        }
        for r in reservaciones
    ]

def update_booking_status(booking_id: int, status: str) -> Optional[Dict[str, Any]]:
    """Actualizar el estado de una reservación."""
    reservacion = Reservacion.query.get(booking_id)
    if not reservacion:
        return None
        
    reservacion.estado = status
    db.session.commit()
    
    return get_booking(booking_id)

def create_service(service_data: Dict[str, Any]) -> Dict[str, Any]:
    """Crear un nuevo servicio."""
    servicio = Servicio(
        nombre=service_data["nombre"],
        descripcion=service_data["descripcion"],
        precio=service_data["precio"],
        duracion=service_data["duracion"],
        imagen=service_data.get("imagen", "default-service.svg"),
        categoria=service_data.get("categoria", "general")
    )
    
    db.session.add(servicio)
    db.session.commit()
    
    return {
        "id": servicio.id,
        "nombre": servicio.nombre,
        "descripcion": servicio.descripcion,
        "precio": servicio.precio,
        "duracion": servicio.duracion,
        "imagen": servicio.imagen,
        "categoria": servicio.categoria
    }

def update_service(service_id: int, service_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Actualizar un servicio existente."""
    servicio = Servicio.query.get(service_id)
    if not servicio:
        return None
        
    servicio.nombre = service_data.get("nombre", servicio.nombre)
    servicio.descripcion = service_data.get("descripcion", servicio.descripcion)
    servicio.precio = service_data.get("precio", servicio.precio)
    servicio.duracion = service_data.get("duracion", servicio.duracion)
    servicio.imagen = service_data.get("imagen", servicio.imagen)
    servicio.categoria = service_data.get("categoria", servicio.categoria)
    servicio.activo = service_data.get("activo", servicio.activo)
    
    db.session.commit()
    
    return {
        "id": servicio.id,
        "nombre": servicio.nombre,
        "descripcion": servicio.descripcion,
        "precio": servicio.precio,
        "duracion": servicio.duracion,
        "imagen": servicio.imagen,
        "categoria": servicio.categoria,
        "activo": servicio.activo
    }

def create_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Crear un nuevo evento."""
    evento = Evento(
        titulo=event_data["titulo"],
        descripcion=event_data["descripcion"],
        fecha=datetime.strptime(event_data["fecha"], "%Y-%m-%d").date(),
        ubicacion_id=event_data["ubicacion_id"]
    )
    
    # Opcional: hora de inicio y fin
    if "hora_inicio" in event_data:
        evento.hora_inicio = datetime.strptime(event_data["hora_inicio"], "%H:%M").time()
    if "hora_fin" in event_data:
        evento.hora_fin = datetime.strptime(event_data["hora_fin"], "%H:%M").time()
    
    db.session.add(evento)
    db.session.commit()
    
    ubicacion = Ubicacion.query.get(evento.ubicacion_id)
    
    return {
        "id": evento.id,
        "titulo": evento.titulo,
        "descripcion": evento.descripcion,
        "fecha": evento.fecha.strftime("%Y-%m-%d"),
        "hora_inicio": evento.hora_inicio.strftime("%H:%M") if evento.hora_inicio else None,
        "hora_fin": evento.hora_fin.strftime("%H:%M") if evento.hora_fin else None,
        "ubicacion_id": evento.ubicacion_id,
        "ubicacion_nombre": ubicacion.nombre
    }

def update_event(event_id: int, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Actualizar un evento existente."""
    evento = Evento.query.get(event_id)
    if not evento:
        return None
        
    evento.titulo = event_data.get("titulo", evento.titulo)
    evento.descripcion = event_data.get("descripcion", evento.descripcion)
    
    if "fecha" in event_data:
        evento.fecha = datetime.strptime(event_data["fecha"], "%Y-%m-%d").date()
    
    if "ubicacion_id" in event_data:
        evento.ubicacion_id = event_data["ubicacion_id"]
        
    if "hora_inicio" in event_data:
        evento.hora_inicio = datetime.strptime(event_data["hora_inicio"], "%H:%M").time() if event_data["hora_inicio"] else None
        
    if "hora_fin" in event_data:
        evento.hora_fin = datetime.strptime(event_data["hora_fin"], "%H:%M").time() if event_data["hora_fin"] else None
    
    db.session.commit()
    
    ubicacion = Ubicacion.query.get(evento.ubicacion_id)
    
    return {
        "id": evento.id,
        "titulo": evento.titulo,
        "descripcion": evento.descripcion,
        "fecha": evento.fecha.strftime("%Y-%m-%d"),
        "hora_inicio": evento.hora_inicio.strftime("%H:%M") if evento.hora_inicio else None,
        "hora_fin": evento.hora_fin.strftime("%H:%M") if evento.hora_fin else None,
        "ubicacion_id": evento.ubicacion_id,
        "ubicacion_nombre": ubicacion.nombre
    }

def delete_event(event_id: int) -> bool:
    """Eliminar un evento."""
    evento = Evento.query.get(event_id)
    if not evento:
        return False
        
    db.session.delete(evento)
    db.session.commit()
    return True

def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Crear un nuevo usuario (admin o terapista)."""
    # Verificar si el correo ya existe
    if Usuario.query.filter_by(email=user_data["email"]).first():
        raise ValueError("El correo electrónico ya está registrado")
        
    usuario = Usuario(
        nombre=user_data["nombre"],
        email=user_data["email"],
        telefono=user_data.get("telefono", ""),
        rol=user_data.get("rol", "terapista")
    )
    
    usuario.set_password(user_data["password"])
    
    db.session.add(usuario)
    db.session.commit()
    
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "rol": usuario.rol,
        "activo": usuario.activo
    }

def get_all_users() -> List[Dict[str, Any]]:
    """Obtener todos los usuarios."""
    usuarios = Usuario.query.all()
    
    return [
        {
            "id": u.id,
            "nombre": u.nombre,
            "email": u.email,
            "telefono": u.telefono,
            "rol": u.rol,
            "activo": u.activo,
            "fecha_creacion": u.fecha_creacion.strftime("%Y-%m-%d")
        }
        for u in usuarios
    ]

def update_user(user_id: int, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Actualizar un usuario existente."""
    usuario = Usuario.query.get(user_id)
    if not usuario:
        return None
        
    # Actualizar campos si se proporcionan
    if "nombre" in user_data:
        usuario.nombre = user_data["nombre"]
    if "email" in user_data:
        # Verificar que el nuevo email no esté en uso por otro usuario
        existing = Usuario.query.filter_by(email=user_data["email"]).first()
        if existing and existing.id != user_id:
            raise ValueError("El correo electrónico ya está en uso por otro usuario")
        usuario.email = user_data["email"]
    if "telefono" in user_data:
        usuario.telefono = user_data["telefono"]
    if "rol" in user_data:
        usuario.rol = user_data["rol"]
    if "activo" in user_data:
        usuario.activo = user_data["activo"]
    if "password" in user_data:
        usuario.set_password(user_data["password"])
    
    db.session.commit()
    
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "telefono": usuario.telefono,
        "rol": usuario.rol,
        "activo": usuario.activo
    }

def get_all_messages() -> List[Dict[str, Any]]:
    """Obtener todos los mensajes de contacto."""
    mensajes = Mensaje.query.order_by(Mensaje.fecha.desc()).all()
    
    return [
        {
            "id": m.id,
            "nombre": m.nombre,
            "email": m.email,
            "asunto": m.asunto,
            "mensaje": m.mensaje,
            "leido": m.leido,
            "fecha": m.fecha.strftime("%Y-%m-%d %H:%M")
        }
        for m in mensajes
    ]

def mark_message_as_read(message_id: int) -> Optional[Dict[str, Any]]:
    """Marcar un mensaje como leído."""
    mensaje = Mensaje.query.get(message_id)
    if not mensaje:
        return None
        
    mensaje.leido = True
    db.session.commit()
    
    return {
        "id": mensaje.id,
        "nombre": mensaje.nombre,
        "email": mensaje.email,
        "asunto": mensaje.asunto,
        "mensaje": mensaje.mensaje,
        "leido": mensaje.leido,
        "fecha": mensaje.fecha.strftime("%Y-%m-%d %H:%M")
    }

def create_location(location_data: Dict[str, Any]) -> Dict[str, Any]:
    """Crear una nueva ubicación."""
    ubicacion = Ubicacion(
        nombre=location_data["nombre"],
        direccion=location_data.get("direccion", ""),
        descripcion=location_data.get("descripcion", ""),
        imagen=location_data.get("imagen", "default-location.svg")
    )
    
    db.session.add(ubicacion)
    db.session.commit()
    
    return {
        "id": ubicacion.id,
        "nombre": ubicacion.nombre,
        "direccion": ubicacion.direccion,
        "descripcion": ubicacion.descripcion,
        "imagen": ubicacion.imagen
    }

def update_location(location_id: int, location_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Actualizar una ubicación existente."""
    ubicacion = Ubicacion.query.get(location_id)
    if not ubicacion:
        return None
        
    ubicacion.nombre = location_data.get("nombre", ubicacion.nombre)
    ubicacion.direccion = location_data.get("direccion", ubicacion.direccion)
    ubicacion.descripcion = location_data.get("descripcion", ubicacion.descripcion)
    ubicacion.imagen = location_data.get("imagen", ubicacion.imagen)
    ubicacion.activo = location_data.get("activo", ubicacion.activo)
    
    db.session.commit()
    
    return {
        "id": ubicacion.id,
        "nombre": ubicacion.nombre,
        "direccion": ubicacion.direccion,
        "descripcion": ubicacion.descripcion,
        "imagen": ubicacion.imagen,
        "activo": ubicacion.activo
    }