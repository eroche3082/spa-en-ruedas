import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from flask_mail import Message
from app import mail

def format_currency(amount: float) -> str:
    """Format amount as currency."""
    return f"${amount:.2f}"

def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime object."""
    return datetime.strptime(date_str, "%Y-%m-%d")

def format_date(dt: datetime) -> str:
    """Format datetime object to readable date string."""
    return dt.strftime("%B %d, %Y")

def format_time(time_str: str) -> str:
    """Format time string to 12-hour format."""
    dt = datetime.strptime(time_str, "%H:%M")
    return dt.strftime("%I:%M %p")

def is_valid_email(email: str) -> bool:
    """Validate email format."""
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def send_email(to: str, subject: str, template: str, **kwargs) -> bool:
    """Send email using Flask-Mail."""
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
        print(f"Error sending email: {e}")
        return False

def generate_booking_confirmation_email(booking: Dict[str, Any], payment: Dict[str, Any]) -> str:
    """Generate HTML email for booking confirmation."""
    service_name = booking.get('service_name', 'Servicio de Spa')
    booking_date = booking.get('date', 'Fecha pendiente')
    booking_time = booking.get('time', 'Hora pendiente')
    location = booking.get('location_name', 'Ubicación pendiente')
    
    html = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #8e44ad; color: white; padding: 10px; text-align: center; }}
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
                    <p>Estimado/a {booking.get('name', 'Cliente')},</p>
                    <p>Gracias por reservar con Spa en Ruedas. A continuación encontrará los detalles de su reserva:</p>
                    <ul>
                        <li><strong>Servicio:</strong> {service_name}</li>
                        <li><strong>Fecha:</strong> {booking_date}</li>
                        <li><strong>Hora:</strong> {booking_time}</li>
                        <li><strong>Ubicación:</strong> {location}</li>
                        <li><strong>Código de Confirmación:</strong> {payment.get('confirmation_code', 'Pendiente')}</li>
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

def calculate_total_price(service_price: float, extras: List[Dict[str, Any]] = None) -> float:
    """Calculate total price based on service and extras."""
    total = service_price
    if extras:
        for extra in extras:
            total += extra.get('price', 0)
    return total
