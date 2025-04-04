from app import app
from models_sql import db, Servicio, Ubicacion, Evento, Usuario
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def crear_datos_iniciales():
    """Crear datos iniciales en la base de datos."""
    try:
        with app.app_context():
            # Verificar si ya hay datos
            if Servicio.query.count() > 0:
                print("La base de datos ya contiene datos. No se inicializarán datos de ejemplo.")
                return

            print("Inicializando base de datos con datos de ejemplo...")

            # Crear ubicaciones
            ubicaciones = [
                Ubicacion(
                    nombre="San Juan - Condado",
                    direccion="Calle Ashford, Condado, San Juan, PR",
                    descripcion="Ubicación principal en la zona turística de Condado",
                    imagen="condado.svg"
                ),
                Ubicacion(
                    nombre="Isla Verde",
                    direccion="Ave. Isla Verde, Carolina, PR",
                    descripcion="A pasos de las hermosas playas de Isla Verde",
                    imagen="isla-verde.svg"
                ),
                Ubicacion(
                    nombre="Viejo San Juan",
                    direccion="Calle San Francisco, Viejo San Juan, PR",
                    descripcion="En el corazón histórico de la ciudad",
                    imagen="viejo-san-juan.svg"
                ),
                Ubicacion(
                    nombre="Rincón",
                    direccion="Carr. 413, Rincón, PR",
                    descripcion="Frente al mar en la capital del surf",
                    imagen="rincon.svg"
                )
            ]
            
            db.session.add_all(ubicaciones)
            db.session.commit()
            print(f"Creadas {len(ubicaciones)} ubicaciones")

            # Crear servicios
            servicios = [
                Servicio(
                    nombre="Masaje terapéutico y relajante",
                    descripcion="Relaja tensiones musculares y reduce el estrés, mejorando la circulación sanguínea.",
                    precio=65.00,
                    duracion=60,
                    imagen="massage-therapy.svg",
                    categoria="masajes"
                ),
                Servicio(
                    nombre="Masaje profundo (Deep Tissue)",
                    descripcion="Técnica enfocada en capas profundas del músculo para aliviar tensiones crónicas.",
                    precio=85.00,
                    duracion=60,
                    imagen="deep-tissue.svg",
                    categoria="masajes"
                ),
                Servicio(
                    nombre="Masaje deportivo",
                    descripcion="Enfocado en prevenir lesiones y mejorar el rendimiento físico de los deportistas.",
                    precio=75.00,
                    duracion=60,
                    imagen="sports-massage.svg",
                    categoria="masajes"
                ),
                Servicio(
                    nombre="Ventosaterapia (Cupping)",
                    descripcion="Técnica milenaria que utiliza ventosas para mejorar la circulación y aliviar el dolor.",
                    precio=55.00,
                    duracion=45,
                    imagen="cupping.svg",
                    categoria="terapias"
                ),
                Servicio(
                    nombre="Reflexología",
                    descripcion="Masaje en puntos específicos de pies y manos que conectan con órganos del cuerpo.",
                    precio=50.00,
                    duracion=45,
                    imagen="reflexology.svg",
                    categoria="terapias"
                ),
                Servicio(
                    nombre="Tratamientos faciales",
                    descripcion="Limpieza profunda e hidratación que rejuvenece y revitaliza la piel del rostro.",
                    precio=70.00,
                    duracion=60,
                    imagen="facial-treatment.svg",
                    categoria="faciales"
                ),
                Servicio(
                    nombre="Aromaterapia",
                    descripcion="Terapia que utiliza aceites esenciales para mejorar el bienestar físico y emocional.",
                    precio=60.00,
                    duracion=60,
                    imagen="aromatherapy.svg",
                    categoria="terapias"
                )
            ]
            
            db.session.add_all(servicios)
            db.session.commit()
            print(f"Creados {len(servicios)} servicios")

            # Crear eventos futuros para los próximos 3 meses
            hoy = datetime.now().date()
            eventos = []
            
            titulos_eventos = [
                "Festival de Bienestar", 
                "Día de Crucero - Carnival", 
                "Feria de Salud", 
                "Día Especial de Spa",
                "Promoción de Verano", 
                "Workshop de Autocuidado", 
                "Masajes a Mitad de Precio"
            ]
            
            descripciones = [
                "Evento especial con descuentos en todos nuestros servicios",
                "Servicios para turistas de crucero con paquetes especiales",
                "Participación en la feria anual de salud y bienestar",
                "Promociones especiales en todos nuestros servicios premium",
                "Disfruta de descuentos en tratamientos faciales y corporales",
                "Aprende técnicas de autocuidado y relajación con nuestros especialistas",
                "Aprovecha esta promoción por tiempo limitado en todos nuestros masajes"
            ]
            
            # Crear 10 eventos en fechas futuras aleatorias
            for i in range(10):
                # Fecha aleatoria entre hoy y 3 meses adelante
                dias_adicionales = random.randint(7, 90)
                fecha_evento = hoy + timedelta(days=dias_adicionales)
                
                # Seleccionar título y descripción aleatorio
                titulo_idx = random.randint(0, len(titulos_eventos) - 1)
                desc_idx = random.randint(0, len(descripciones) - 1)
                
                # Seleccionar ubicación aleatoria
                ubicacion_id = random.randint(1, len(ubicaciones))
                
                evento = Evento(
                    titulo=titulos_eventos[titulo_idx],
                    descripcion=descripciones[desc_idx],
                    fecha=fecha_evento,
                    ubicacion_id=ubicacion_id
                )
                eventos.append(evento)
            
            db.session.add_all(eventos)
            db.session.commit()
            print(f"Creados {len(eventos)} eventos")

            # Crear usuario administrador
            admin = Usuario(
                nombre="Administrador",
                email="admin@spaenruedas.com",
                telefono="123-456-7890",
                rol="admin",
                fecha_creacion=datetime.now()
            )
            admin.password_hash = generate_password_hash("admin123")
            
            db.session.add(admin)
            db.session.commit()
            print("Creado usuario administrador: admin@spaenruedas.com (contraseña: admin123)")

            print("Inicialización de la base de datos completada con éxito!")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")

if __name__ == "__main__":
    crear_datos_iniciales()
