from flask import render_template, request, redirect, url_for, jsonify, flash, session, abort
from functools import wraps
from app import app
from models_sql import Usuario, Servicio, Ubicacion, Evento, Reservacion, Pago, Mensaje, db
from utils_new import format_date, format_time, generate_admin_dashboard_stats
from services_sql import (
    authenticate_user, get_all_bookings, update_booking_status,
    create_service, update_service, get_all_services,
    create_event, update_event, delete_event, get_all_events,
    create_user, update_user, get_all_users,
    create_location, update_location, get_all_locations,
    get_all_messages, mark_message_as_read
)

# Decorador para rutas protegidas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_user' not in session:
            flash('Por favor inicie sesión para acceder a esta página', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para verificar rol de administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_user' not in session:
            flash('Por favor inicie sesión para acceder a esta página', 'warning')
            return redirect(url_for('admin_login'))
        
        if session['admin_user'].get('rol') != 'admin':
            flash('No tiene permiso para acceder a esta página', 'danger')
            return redirect(url_for('admin_dashboard'))
            
        return f(*args, **kwargs)
    return decorated_function

# Rutas de administración

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Página de inicio de sesión para administradores."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = authenticate_user(email, password)
        
        if user:
            session['admin_user'] = user
            flash(f'Bienvenido/a, {user["nombre"]}', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Credenciales incorrectas. Intente nuevamente.', 'danger')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """Cerrar sesión."""
    session.pop('admin_user', None)
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    """Panel de control principal."""
    # Obtener estadísticas para el dashboard
    stats = generate_admin_dashboard_stats()
    
    # Obtener reservaciones recientes
    recent_bookings = Reservacion.query.order_by(Reservacion.fecha_creacion.desc()).limit(5).all()
    bookings_data = []
    
    for booking in recent_bookings:
        cliente = booking.cliente
        servicio = booking.servicio
        ubicacion = booking.ubicacion
        
        bookings_data.append({
            "id": booking.id,
            "cliente_nombre": cliente.nombre,
            "servicio_nombre": servicio.nombre,
            "ubicacion_nombre": ubicacion.nombre,
            "fecha": booking.fecha,
            "hora": booking.hora,
            "estado": booking.estado
        })
    
    # Obtener mensajes recientes
    recent_messages = Mensaje.query.order_by(Mensaje.fecha.desc()).limit(5).all()
    messages_data = []
    
    for msg in recent_messages:
        messages_data.append({
            "id": msg.id,
            "nombre": msg.nombre,
            "email": msg.email,
            "asunto": msg.asunto,
            "fecha": msg.fecha,
            "leido": msg.leido
        })
    
    # Proximos eventos
    upcoming_events = Evento.query.filter(Evento.fecha >= db.func.current_date()).order_by(Evento.fecha).limit(3).all()
    events_data = []
    
    for event in upcoming_events:
        events_data.append({
            "id": event.id,
            "titulo": event.titulo,
            "fecha": event.fecha,
            "ubicacion_nombre": event.ubicacion.nombre
        })
    
    return render_template(
        'admin/dashboard.html',
        stats=stats,
        bookings=bookings_data,
        messages=messages_data,
        events=events_data
    )

# Rutas para gestión de reservaciones

@app.route('/admin/reservaciones')
@login_required
def admin_bookings():
    """Gestión de reservaciones."""
    filtro = request.args.get('filtro', 'todas')
    
    # Consulta base
    query = Reservacion.query.join(Cliente).join(Servicio).join(Ubicacion)
    
    # Aplicar filtro
    if filtro == 'pendientes':
        query = query.filter(Reservacion.estado == 'pendiente')
    elif filtro == 'confirmadas':
        query = query.filter(Reservacion.estado == 'confirmada')
    elif filtro == 'canceladas':
        query = query.filter(Reservacion.estado == 'cancelada')
    elif filtro == 'completadas':
        query = query.filter(Reservacion.estado == 'completada')
    elif filtro == 'hoy':
        query = query.filter(Reservacion.fecha == db.func.current_date())
    
    # Ordenar por fecha y hora
    reservaciones = query.order_by(Reservacion.fecha.desc(), Reservacion.hora).all()
    
    bookings_data = []
    for reserva in reservaciones:
        bookings_data.append({
            "id": reserva.id,
            "cliente": {
                "id": reserva.cliente.id,
                "nombre": reserva.cliente.nombre,
                "email": reserva.cliente.email,
                "telefono": reserva.cliente.telefono
            },
            "servicio": {
                "id": reserva.servicio.id,
                "nombre": reserva.servicio.nombre,
                "precio": reserva.servicio.precio
            },
            "ubicacion": {
                "id": reserva.ubicacion.id,
                "nombre": reserva.ubicacion.nombre
            },
            "fecha": reserva.fecha,
            "hora": reserva.hora,
            "estado": reserva.estado,
            "codigo_confirmacion": reserva.codigo_confirmacion,
            "fecha_creacion": reserva.fecha_creacion
        })
    
    return render_template('admin/bookings.html', reservaciones=bookings_data, filtro_actual=filtro)

@app.route('/admin/reservaciones/<int:booking_id>')
@login_required
def admin_booking_detail(booking_id):
    """Ver detalles de una reservación."""
    reserva = Reservacion.query.get_or_404(booking_id)
    
    # Obtener pagos asociados
    pagos = Pago.query.filter_by(reservacion_id=booking_id).all()
    pagos_data = []
    
    for pago in pagos:
        pagos_data.append({
            "id": pago.id,
            "monto": pago.monto,
            "metodo": pago.metodo,
            "estado": pago.estado,
            "referencia": pago.referencia,
            "fecha": pago.fecha
        })
    
    booking_data = {
        "id": reserva.id,
        "cliente": {
            "id": reserva.cliente.id,
            "nombre": reserva.cliente.nombre,
            "email": reserva.cliente.email,
            "telefono": reserva.cliente.telefono
        },
        "servicio": {
            "id": reserva.servicio.id,
            "nombre": reserva.servicio.nombre,
            "precio": reserva.servicio.precio,
            "duracion": reserva.servicio.duracion
        },
        "ubicacion": {
            "id": reserva.ubicacion.id,
            "nombre": reserva.ubicacion.nombre,
            "direccion": reserva.ubicacion.direccion
        },
        "fecha": reserva.fecha,
        "hora": reserva.hora,
        "estado": reserva.estado,
        "comentarios": reserva.comentarios,
        "codigo_confirmacion": reserva.codigo_confirmacion,
        "fecha_creacion": reserva.fecha_creacion,
        "pagos": pagos_data
    }
    
    return render_template('admin/booking_detail.html', reserva=booking_data)

@app.route('/admin/reservaciones/<int:booking_id>/actualizar', methods=['POST'])
@login_required
def admin_update_booking_status(booking_id):
    """Actualizar estado de una reservación."""
    estado = request.form.get('estado')
    
    if not estado or estado not in ['pendiente', 'confirmada', 'cancelada', 'completada']:
        flash('Estado no válido', 'danger')
        return redirect(url_for('admin_booking_detail', booking_id=booking_id))
    
    reserva = Reservacion.query.get_or_404(booking_id)
    reserva.estado = estado
    db.session.commit()
    
    flash('Estado de la reservación actualizado correctamente', 'success')
    return redirect(url_for('admin_booking_detail', booking_id=booking_id))

# Rutas para gestión de servicios

@app.route('/admin/servicios')
@login_required
def admin_services():
    """Gestión de servicios."""
    servicios = Servicio.query.all()
    return render_template('admin/services.html', servicios=servicios)

@app.route('/admin/servicios/nuevo', methods=['GET', 'POST'])
@login_required
def admin_new_service():
    """Crear nuevo servicio."""
    if request.method == 'POST':
        servicio_data = {
            "nombre": request.form.get('nombre'),
            "descripcion": request.form.get('descripcion'),
            "precio": float(request.form.get('precio')),
            "duracion": int(request.form.get('duracion')),
            "categoria": request.form.get('categoria', 'general'),
            "imagen": request.form.get('imagen', 'default-service.svg')
        }
        
        create_service(servicio_data)
        flash('Servicio creado correctamente', 'success')
        return redirect(url_for('admin_services'))
    
    return render_template('admin/service_form.html')

@app.route('/admin/servicios/<int:service_id>/editar', methods=['GET', 'POST'])
@login_required
def admin_edit_service(service_id):
    """Editar servicio existente."""
    servicio = Servicio.query.get_or_404(service_id)
    
    if request.method == 'POST':
        servicio_data = {
            "nombre": request.form.get('nombre'),
            "descripcion": request.form.get('descripcion'),
            "precio": float(request.form.get('precio')),
            "duracion": int(request.form.get('duracion')),
            "categoria": request.form.get('categoria'),
            "imagen": request.form.get('imagen'),
            "activo": 'activo' in request.form
        }
        
        update_service(service_id, servicio_data)
        flash('Servicio actualizado correctamente', 'success')
        return redirect(url_for('admin_services'))
    
    return render_template('admin/service_form.html', servicio=servicio)

# Rutas para gestión de eventos

@app.route('/admin/eventos')
@login_required
def admin_events():
    """Gestión de eventos."""
    eventos = Evento.query.order_by(Evento.fecha).all()
    
    events_data = []
    for evento in eventos:
        events_data.append({
            "id": evento.id,
            "titulo": evento.titulo,
            "descripcion": evento.descripcion,
            "fecha": evento.fecha,
            "hora_inicio": evento.hora_inicio,
            "hora_fin": evento.hora_fin,
            "ubicacion": {
                "id": evento.ubicacion.id,
                "nombre": evento.ubicacion.nombre
            }
        })
    
    return render_template('admin/events.html', eventos=events_data)

@app.route('/admin/eventos/nuevo', methods=['GET', 'POST'])
@login_required
def admin_new_event():
    """Crear nuevo evento."""
    if request.method == 'POST':
        evento_data = {
            "titulo": request.form.get('titulo'),
            "descripcion": request.form.get('descripcion'),
            "fecha": request.form.get('fecha'),
            "ubicacion_id": request.form.get('ubicacion_id')
        }
        
        # Campos opcionales
        if request.form.get('hora_inicio'):
            evento_data["hora_inicio"] = request.form.get('hora_inicio')
        if request.form.get('hora_fin'):
            evento_data["hora_fin"] = request.form.get('hora_fin')
        
        create_event(evento_data)
        flash('Evento creado correctamente', 'success')
        return redirect(url_for('admin_events'))
    
    ubicaciones = Ubicacion.query.filter_by(activo=True).all()
    return render_template('admin/event_form.html', ubicaciones=ubicaciones)

@app.route('/admin/eventos/<int:event_id>/editar', methods=['GET', 'POST'])
@login_required
def admin_edit_event(event_id):
    """Editar evento existente."""
    evento = Evento.query.get_or_404(event_id)
    
    if request.method == 'POST':
        evento_data = {
            "titulo": request.form.get('titulo'),
            "descripcion": request.form.get('descripcion'),
            "fecha": request.form.get('fecha'),
            "ubicacion_id": request.form.get('ubicacion_id')
        }
        
        # Campos opcionales
        if request.form.get('hora_inicio'):
            evento_data["hora_inicio"] = request.form.get('hora_inicio')
        else:
            evento_data["hora_inicio"] = None
            
        if request.form.get('hora_fin'):
            evento_data["hora_fin"] = request.form.get('hora_fin')
        else:
            evento_data["hora_fin"] = None
        
        update_event(event_id, evento_data)
        flash('Evento actualizado correctamente', 'success')
        return redirect(url_for('admin_events'))
    
    ubicaciones = Ubicacion.query.filter_by(activo=True).all()
    return render_template('admin/event_form.html', evento=evento, ubicaciones=ubicaciones)

@app.route('/admin/eventos/<int:event_id>/eliminar', methods=['POST'])
@login_required
def admin_delete_event(event_id):
    """Eliminar evento."""
    if delete_event(event_id):
        flash('Evento eliminado correctamente', 'success')
    else:
        flash('No se pudo eliminar el evento', 'danger')
    
    return redirect(url_for('admin_events'))

# Rutas para gestión de ubicaciones

@app.route('/admin/ubicaciones')
@login_required
def admin_locations():
    """Gestión de ubicaciones."""
    ubicaciones = Ubicacion.query.all()
    return render_template('admin/locations.html', ubicaciones=ubicaciones)

@app.route('/admin/ubicaciones/nueva', methods=['GET', 'POST'])
@login_required
def admin_new_location():
    """Crear nueva ubicación."""
    if request.method == 'POST':
        ubicacion_data = {
            "nombre": request.form.get('nombre'),
            "direccion": request.form.get('direccion'),
            "descripcion": request.form.get('descripcion'),
            "imagen": request.form.get('imagen', 'default-location.svg')
        }
        
        create_location(ubicacion_data)
        flash('Ubicación creada correctamente', 'success')
        return redirect(url_for('admin_locations'))
    
    return render_template('admin/location_form.html')

@app.route('/admin/ubicaciones/<int:location_id>/editar', methods=['GET', 'POST'])
@login_required
def admin_edit_location(location_id):
    """Editar ubicación existente."""
    ubicacion = Ubicacion.query.get_or_404(location_id)
    
    if request.method == 'POST':
        ubicacion_data = {
            "nombre": request.form.get('nombre'),
            "direccion": request.form.get('direccion'),
            "descripcion": request.form.get('descripcion'),
            "imagen": request.form.get('imagen'),
            "activo": 'activo' in request.form
        }
        
        update_location(location_id, ubicacion_data)
        flash('Ubicación actualizada correctamente', 'success')
        return redirect(url_for('admin_locations'))
    
    return render_template('admin/location_form.html', ubicacion=ubicacion)

# Rutas para gestión de usuarios

@app.route('/admin/usuarios')
@admin_required
def admin_users():
    """Gestión de usuarios."""
    usuarios = get_all_users()
    return render_template('admin/users.html', usuarios=usuarios)

@app.route('/admin/usuarios/nuevo', methods=['GET', 'POST'])
@admin_required
def admin_new_user():
    """Crear nuevo usuario."""
    if request.method == 'POST':
        try:
            usuario_data = {
                "nombre": request.form.get('nombre'),
                "email": request.form.get('email'),
                "telefono": request.form.get('telefono'),
                "password": request.form.get('password'),
                "rol": request.form.get('rol', 'terapista')
            }
            
            create_user(usuario_data)
            flash('Usuario creado correctamente', 'success')
            return redirect(url_for('admin_users'))
        except ValueError as e:
            flash(str(e), 'danger')
    
    return render_template('admin/user_form.html')

@app.route('/admin/usuarios/<int:user_id>/editar', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    """Editar usuario existente."""
    usuario = Usuario.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            usuario_data = {
                "nombre": request.form.get('nombre'),
                "email": request.form.get('email'),
                "telefono": request.form.get('telefono'),
                "rol": request.form.get('rol'),
                "activo": 'activo' in request.form
            }
            
            # Solo actualizar la contraseña si se proporcionó una nueva
            if request.form.get('password'):
                usuario_data["password"] = request.form.get('password')
            
            update_user(user_id, usuario_data)
            flash('Usuario actualizado correctamente', 'success')
            return redirect(url_for('admin_users'))
        except ValueError as e:
            flash(str(e), 'danger')
    
    return render_template('admin/user_form.html', usuario=usuario)

# Rutas para gestión de mensajes

@app.route('/admin/mensajes')
@login_required
def admin_messages():
    """Gestión de mensajes de contacto."""
    mensajes = get_all_messages()
    return render_template('admin/messages.html', mensajes=mensajes)

@app.route('/admin/mensajes/<int:message_id>')
@login_required
def admin_message_detail(message_id):
    """Ver detalle de un mensaje."""
    mensaje = Mensaje.query.get_or_404(message_id)
    
    # Marcar como leído si no lo está
    if not mensaje.leido:
        mark_message_as_read(message_id)
    
    mensaje_data = {
        "id": mensaje.id,
        "nombre": mensaje.nombre,
        "email": mensaje.email,
        "asunto": mensaje.asunto,
        "mensaje": mensaje.mensaje,
        "fecha": mensaje.fecha,
        "leido": mensaje.leido
    }
    
    return render_template('admin/message_detail.html', mensaje=mensaje_data)

@app.route('/admin/mensajes/<int:message_id>/leido', methods=['POST'])
@login_required
def admin_mark_message_read(message_id):
    """Marcar mensaje como leído."""
    mark_message_as_read(message_id)
    return redirect(url_for('admin_messages'))

# API para el panel de administración

@app.route('/api/admin/stats')
@login_required
def api_admin_stats():
    """API para obtener estadísticas del panel de administración."""
    stats = generate_admin_dashboard_stats()
    return jsonify(stats)

@app.route('/api/admin/bookings/next')
@login_required
def api_admin_next_bookings():
    """API para obtener próximas reservaciones."""
    hoy = datetime.now().date()
    proximas = Reservacion.query.filter(
        Reservacion.fecha >= hoy,
        Reservacion.estado == 'confirmada'
    ).order_by(Reservacion.fecha, Reservacion.hora).limit(5).all()
    
    result = []
    for r in proximas:
        result.append({
            "id": r.id,
            "cliente": r.cliente.nombre,
            "servicio": r.servicio.nombre,
            "fecha": r.fecha.strftime('%Y-%m-%d'),
            "hora": r.hora.strftime('%H:%M'),
            "ubicacion": r.ubicacion.nombre
        })
    
    return jsonify(result)