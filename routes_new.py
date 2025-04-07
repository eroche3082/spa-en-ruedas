from flask import render_template, request, redirect, url_for, jsonify, flash, session
from app import app
from models_sql import db, Servicio, Ubicacion, Evento, Reservacion, Cliente, Pago, Mensaje
from utils_new import format_currency, format_date, format_time, generate_booking_confirmation_email, send_email
from services_sql import (
    get_all_services, get_service_by_id, get_all_events, get_all_locations,
    create_booking, get_booking, get_booking_by_confirmation,
    process_payment, create_contact_message, get_available_slots
)
import stripe
import os

# Configurar Stripe
stripe_key = os.environ.get('STRIPE_SECRET_KEY', '')
if stripe_key:
    stripe.api_key = stripe_key

# Rutas públicas
@app.route('/')
def index():
    """Render página principal."""
    servicios = get_all_services()[:3]  # Primeros 3 servicios destacados
    eventos = get_all_events()[:3]      # Próximos 3 eventos
    return render_template('index.html', servicios=servicios, eventos=eventos)

@app.route('/servicios')
def servicios():
    """Render página de servicios."""
    todos_servicios = get_all_services()
    return render_template('servicios.html', servicios=todos_servicios)

@app.route('/servicios/<int:service_id>')
def detalle_servicio(service_id):
    """Render detalle de un servicio específico."""
    servicio = get_service_by_id(service_id)
    if not servicio:
        flash('Servicio no encontrado', 'error')
        return redirect(url_for('servicios'))
    
    # Obtener servicios relacionados (misma categoría)
    categoria = servicio.get('categoria', 'general')
    servicios_relacionados = [
        s for s in get_all_services() 
        if s.get('categoria') == categoria and s.get('id') != service_id
    ][:3]  # Limitar a 3 relacionados
    
    return render_template(
        'detalle_servicio.html', 
        servicio=servicio, 
        servicios_relacionados=servicios_relacionados
    )

@app.route('/reservar', methods=['GET', 'POST'])
def reservar():
    """Render página de reservación o procesar formulario."""
    if request.method == 'POST':
        # Procesar formulario de reservación
        servicio_id = request.form.get('servicio_id')
        ubicacion_id = request.form.get('ubicacion_id')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        
        if not servicio_id or not ubicacion_id or not fecha or not hora:
            flash('Por favor complete todos los campos obligatorios', 'error')
            servicios = get_all_services()
            ubicaciones = get_all_locations()
            return render_template('reservar.html', servicios=servicios, ubicaciones=ubicaciones)
        
        # Crear datos de reservación
        booking_data = {
            'nombre': request.form.get('nombre'),
            'email': request.form.get('email'),
            'telefono': request.form.get('telefono'),
            'servicio_id': servicio_id,
            'ubicacion_id': ubicacion_id,
            'fecha': fecha,
            'hora': hora,
            'comentarios': request.form.get('comentarios', '')
        }
        
        # Crear reservación
        reserva = create_booking(booking_data)
        
        # Guardar ID de reserva en sesión para el paso de pago
        session['reserva_id'] = reserva['id']
        
        # Redireccionar a la página de pago
        return redirect(url_for('pago'))
    
    # GET - mostrar formulario de reservación
    servicios = get_all_services()
    ubicaciones = get_all_locations()
    
    # Verificar si se preseleccionó un servicio desde la URL
    servicio_id = request.args.get('service')
    servicio_seleccionado = None
    if servicio_id:
        servicio_seleccionado = get_service_by_id(int(servicio_id))
    
    return render_template(
        'reservar.html', 
        servicios=servicios, 
        ubicaciones=ubicaciones,
        servicio_seleccionado=servicio_seleccionado
    )

@app.route('/slots_disponibles')
def slots_disponibles():
    """API para obtener slots de tiempo disponibles."""
    fecha = request.args.get('fecha')
    ubicacion = request.args.get('ubicacion')
    
    if not fecha or not ubicacion:
        return jsonify({'error': 'Parámetros incompletos'}), 400
    
    slots = get_available_slots(fecha, int(ubicacion))
    return jsonify({'slots': slots})

@app.route('/pago', methods=['GET', 'POST'])
def pago():
    """Render página de pago o procesar pago."""
    reserva_id = session.get('reserva_id')
    if not reserva_id:
        flash('No hay reserva activa. Por favor realice una reserva primero.', 'error')
        return redirect(url_for('reservar'))
    
    reserva = get_booking(reserva_id)
    if not reserva:
        flash('Reserva no encontrada. Por favor realice una nueva reserva.', 'error')
        return redirect(url_for('reservar'))
    
    if request.method == 'POST':
        # Si hay Stripe configurado, crear checkout
        if stripe_key:
            try:
                YOUR_DOMAIN = request.host_url.rstrip('/')
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[
                        {
                            'price_data': {
                                'currency': 'usd',
                                'product_data': {
                                    'name': reserva['servicio']['nombre'],
                                    'description': f"Reserva para {reserva['fecha']} a las {reserva['hora']}",
                                },
                                'unit_amount': int(reserva['servicio']['precio'] * 100),
                            },
                            'quantity': 1,
                        },
                    ],
                    mode='payment',
                    success_url=YOUR_DOMAIN + f'/pago_exitoso?session_id={{CHECKOUT_SESSION_ID}}',
                    cancel_url=YOUR_DOMAIN + '/pago_cancelado',
                    client_reference_id=str(reserva_id),
                )
                return redirect(checkout_session.url, code=303)
            except Exception as e:
                app.logger.error(f"Error Stripe: {e}")
                flash('Error procesando el pago con Stripe. Procesaremos manualmente.', 'warning')
        
        # Procesar pago sin Stripe (simulación)
        payment_data = {
            'reservacion_id': reserva_id,
            'monto': reserva['servicio']['precio'],
            'metodo': request.form.get('metodo_pago', 'tarjeta')
        }
        
        # Procesar pago (simulado)
        payment_result = process_payment(payment_data)
        
        if payment_result['status'] == 'success':
            # Enviar email de confirmación
            cliente_email = reserva['cliente']['email']
            email_html = generate_booking_confirmation_email(reserva, payment_result)
            send_email(cliente_email, 'Spa en Ruedas - Confirmación de Reserva', email_html)
            
            # Guardar resultado de pago en sesión
            session['payment_result'] = payment_result
            
            # Redireccionar a confirmación
            return redirect(url_for('confirmacion'))
        else:
            flash('Error procesando el pago. Por favor intente nuevamente.', 'error')
    
    # GET - mostrar formulario de pago
    return render_template('pago.html', reserva=reserva)

@app.route('/pago_exitoso')
def pago_exitoso():
    """Procesar pago exitoso de Stripe."""
    session_id = request.args.get('session_id')
    reserva_id = session.get('reserva_id')
    
    if not reserva_id:
        flash('No hay reserva activa.', 'error')
        return redirect(url_for('reservar'))
    
    if session_id and stripe_key:
        try:
            # Recuperar información de la sesión de Stripe
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            
            # Verificar que corresponde a la reserva actual
            if checkout_session.client_reference_id != str(reserva_id):
                flash('Error de referencia en la transacción.', 'error')
                return redirect(url_for('pago'))
            
            # Procesar pago como exitoso
            payment_data = {
                'reservacion_id': reserva_id,
                'monto': checkout_session.amount_total / 100,  # Convertir de centavos
                'metodo': 'tarjeta',
            }
            
            payment_result = process_payment(payment_data)
            session['payment_result'] = payment_result
            
            # Obtener la reserva y enviar email
            reserva = get_booking(reserva_id)
            cliente_email = reserva['cliente']['email']
            email_html = generate_booking_confirmation_email(reserva, payment_result)
            send_email(cliente_email, 'Spa en Ruedas - Confirmación de Reserva', email_html)
            
            return redirect(url_for('confirmacion'))
        except Exception as e:
            app.logger.error(f"Error procesando pago Stripe: {e}")
            flash('Error verificando el pago. Por favor contacte a soporte.', 'error')
            return redirect(url_for('pago'))
    
    # Si no hay session_id, es posible que el usuario haya llegado directamente a esta URL
    flash('Información de pago incompleta', 'error')
    return redirect(url_for('pago'))

@app.route('/pago_cancelado')
def pago_cancelado():
    """Manejar cancelación de pago de Stripe."""
    flash('Pago cancelado. Puede intentar nuevamente o contactar con nosotros.', 'warning')
    return redirect(url_for('pago'))

@app.route('/confirmacion')
def confirmacion():
    """Render página de confirmación de reserva."""
    reserva_id = session.get('reserva_id')
    payment_result = session.get('payment_result')
    
    if not reserva_id or not payment_result:
        flash('No hay información de reserva. Por favor realice una nueva reserva.', 'error')
        return redirect(url_for('reservar'))
    
    reserva = get_booking(reserva_id)
    if not reserva:
        flash('Reserva no encontrada. Por favor realice una nueva reserva.', 'error')
        return redirect(url_for('reservar'))
    
    # Limpiar datos de sesión
    session.pop('reserva_id', None)
    session.pop('payment_result', None)
    
    return render_template('confirmacion.html', reserva=reserva, pago=payment_result)

@app.route('/verificar_reserva', methods=['GET', 'POST'])
def verificar_reserva():
    """Página para verificar estado de una reserva."""
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        email = request.form.get('email')
        
        if not codigo or not email:
            flash('Por favor ingrese el código de reserva y email', 'error')
            return render_template('verificar_reserva.html')
        
        # Buscar reserva por código
        reserva = get_booking_by_confirmation(codigo)
        
        if not reserva or reserva['cliente']['email'] != email:
            flash('No se encontró la reserva con esos datos', 'error')
            return render_template('verificar_reserva.html')
        
        return render_template('detalle_reserva.html', reserva=reserva)
    
    # GET - mostrar formulario de verificación
    return render_template('verificar_reserva.html')

@app.route('/calendario')
def calendario():
    """Render página de calendario de eventos."""
    eventos = get_all_events()
    ubicaciones = get_all_locations()
    return render_template('calendar.html', events=eventos, locations=ubicaciones)

@app.route('/nosotros')
def nosotros():
    """Render página de acerca de nosotros."""
    return render_template('nosotros.html')

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    """Render página de contacto o procesar formulario."""
    if request.method == 'POST':
        # Procesar formulario de contacto
        mensaje_data = {
            'nombre': request.form.get('nombre'),
            'email': request.form.get('email'),
            'asunto': request.form.get('asunto'),
            'mensaje': request.form.get('mensaje')
        }
        
        # Verificar campos requeridos
        if not mensaje_data['nombre'] or not mensaje_data['email'] or not mensaje_data['mensaje']:
            flash('Por favor complete todos los campos obligatorios', 'error')
            return render_template('contacto.html')
        
        # Crear mensaje
        create_contact_message(mensaje_data)
        
        flash('¡Gracias por su mensaje! Nos pondremos en contacto pronto.', 'success')
        return redirect(url_for('contacto'))
    
    # GET - mostrar formulario de contacto
    return render_template('contacto.html')

@app.route('/api/servicio/<int:service_id>')
def api_servicio(service_id):
    """API para obtener detalles de un servicio."""
    servicio = get_service_by_id(service_id)
    if not servicio:
        return jsonify({'error': 'Servicio no encontrado'}), 404
    
    return jsonify({'servicio': servicio})

# Importar rutas de administración
from admin_routes import *