import os
import re
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from flask import render_template
from app import mail
from flask_mail import Message

def format_currency(amount: float) -> str:
    """Formatear cantidad como moneda."""
    return f"${amount:.2f}"

def parse_date(date_str: str) -> datetime:
    """Convertir string de fecha a objeto datetime."""
    return datetime.strptime(date_str, "%Y-%m-%d")

def format_date(dt: datetime) -> str:
    """Formatear objeto datetime a string legible."""
    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    dia_semana = dias[dt.weekday()]
    dia = dt.day
    mes = meses[dt.month]
    anio = dt.year
    
    return f"{dia_semana}, {dia} de {mes} de {anio}"

def format_time(time_str: str) -> str:
    """Formatear string de hora a formato de 12 horas."""
    dt = datetime.strptime(time_str, "%H:%M")
    return dt.strftime("%I:%M %p").lower().replace("am", "a.m.").replace("pm", "p.m.")

def is_valid_email(email: str) -> bool:
    """Validar formato de email."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def generate_booking_confirmation_email(booking: Dict[str, Any], payment: Dict[str, Any]) -> str:
    """Generar email HTML para confirmación de reserva."""
    service_name = booking.get('servicio', {}).get('nombre', 'Servicio de Spa')
    booking_date = booking.get('fecha', 'Fecha pendiente')
    booking_time = booking.get('hora', 'Hora pendiente')
    location = booking.get('ubicacion', {}).get('nombre', 'Ubicación pendiente')
    
    try:
        fecha_obj = datetime.strptime(booking_date, "%Y-%m-%d")
        booking_date = format_date(fecha_obj)
    except:
        pass
    
    try:
        hora_obj = datetime.strptime(booking_time, "%H:%M")
        booking_time = format_time(booking_time)
    except:
        pass
    
    html = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #9c6644; color: white; padding: 10px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ text-align: center; padding: 10px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>¡Confirmación de Reserva!</h1>
                </div>
                <div class="content">
                    <p>Estimado/a {booking.get('cliente', {}).get('nombre', 'Cliente')},</p>
                    <p>Gracias por reservar con Spa en Ruedas. A continuación encontrará los detalles de su reserva:</p>
                    <ul>
                        <li><strong>Servicio:</strong> {service_name}</li>
                        <li><strong>Fecha:</strong> {booking_date}</li>
                        <li><strong>Hora:</strong> {booking_time}</li>
                        <li><strong>Ubicación:</strong> {location}</li>
                        <li><strong>Código de Confirmación:</strong> {payment.get('confirmation_code', booking.get('codigo_confirmacion', 'Pendiente'))}</li>
                    </ul>
                    <p>Si necesita hacer algún cambio o tiene alguna pregunta, no dude en contactarnos.</p>
                    <p>¡Esperamos verle pronto!</p>
                </div>
                <div class="footer">
                    <p>Spa en Ruedas - Puerto Rico</p>
                    <p>Este es un correo electrónico automático, por favor no responda.</p>
                </div>
            </div>
        </body>
    </html>
    """
    return html

def send_email(to: str, subject: str, template: str, **kwargs) -> bool:
    """Enviar correo usando Flask-Mail."""
    try:
        msg = Message(
            subject=subject,
            recipients=[to],
            html=template,
            sender=os.environ.get('MAIL_DEFAULT_SENDER', 'test@example.com')
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False

def calculate_total_price(service_price: float, extras: List[Dict[str, Any]] = None) -> float:
    """Calcular precio total basado en servicio y extras."""
    total = service_price
    
    # Agregar servicios extra si se proporcionan
    if extras:
        for extra in extras:
            total += extra.get('precio', 0)
    
    return total

def generate_admin_dashboard_stats() -> Dict[str, Any]:
    """Generar estadísticas para el panel de administración."""
    # Importamos aquí para evitar circular imports
    from models_sql import db, Reservacion, Cliente, Pago, Mensaje
    
    # Fecha de hoy
    hoy = datetime.now().date()
    
    # Reservaciones
    total_reservaciones = Reservacion.query.count()
    reservaciones_pendientes = Reservacion.query.filter_by(estado="pendiente").count()
    reservaciones_confirmadas = Reservacion.query.filter_by(estado="confirmada").count()
    
    # Reservaciones de los últimos 7 días
    fecha_inicio = hoy - timedelta(days=7)
    reservaciones_recientes = Reservacion.query.filter(Reservacion.fecha_creacion >= fecha_inicio).count()
    
    # Reservaciones para hoy
    reservaciones_hoy = Reservacion.query.filter_by(fecha=hoy).count()
    
    # Clientes
    total_clientes = Cliente.query.count()
    
    # Pagos e ingresos
    total_pagos = Pago.query.filter_by(estado="completado").count()
    ingresos_totales = db.session.query(db.func.sum(Pago.monto)).filter_by(estado="completado").scalar() or 0
    
    # Mensajes
    mensajes_no_leidos = Mensaje.query.filter_by(leido=False).count()
    
    return {
        "total_reservaciones": total_reservaciones,
        "reservaciones_pendientes": reservaciones_pendientes,
        "reservaciones_confirmadas": reservaciones_confirmadas,
        "reservaciones_recientes": reservaciones_recientes,
        "reservaciones_hoy": reservaciones_hoy,
        "total_clientes": total_clientes,
        "total_pagos": total_pagos,
        "ingresos_totales": ingresos_totales,
        "mensajes_no_leidos": mensajes_no_leidos
    }