from flask import render_template, request, redirect, url_for, jsonify, flash, session
import json
from app import app
from models import storage
from services import (
    get_all_services, get_service_by_id, get_all_events, get_all_locations,
    create_booking, process_payment, send_confirmation_email, create_contact_message,
    get_available_slots, get_booking
)
from utils import (
    format_currency, format_date, generate_booking_confirmation_email,
    calculate_total_price, send_email
)

@app.route('/')
def index():
    """Render the homepage."""
    services = get_all_services()[:3]  # Get first 3 services for showcase
    events = get_all_events()[:3]      # Get first 3 upcoming events
    return render_template('index.html', services=services, events=events)

@app.route('/services')
def services():
    """Render the services page."""
    all_services = get_all_services()
    return render_template('services.html', services=all_services)

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    """Render the booking page or process booking form."""
    if request.method == 'POST':
        # Process booking form submission
        booking_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'service_id': request.form.get('service'),
            'service_name': get_service_by_id(request.form.get('service')).get('name'),
            'location_id': request.form.get('location'),
            'location_name': next((loc['name'] for loc in get_all_locations() if loc['id'] == request.form.get('location')), None),
            'date': request.form.get('date'),
            'time': request.form.get('time'),
            'comments': request.form.get('comments', ''),
            'status': 'pending'
        }
        
        # Create booking
        booking = create_booking(booking_data)
        
        # Store booking ID in session for the payment step
        session['booking_id'] = booking['id']
        
        # Redirect to payment page
        return redirect(url_for('payment'))
    
    # GET request - show booking form
    services = get_all_services()
    locations = get_all_locations()
    
    return render_template('booking.html', services=services, locations=locations)

@app.route('/get_available_slots', methods=['GET'])
def available_slots():
    """API endpoint to get available time slots."""
    date = request.args.get('date')
    location_id = request.args.get('location_id')
    
    if not date or not location_id:
        return jsonify({'error': 'Missing parameters'}), 400
    
    slots = get_available_slots(date, location_id)
    return jsonify({'slots': slots})

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    """Render the payment page or process payment."""
    booking_id = session.get('booking_id')
    if not booking_id:
        flash('No booking found. Please start the booking process again.', 'error')
        return redirect(url_for('booking'))
    
    booking = get_booking(booking_id)
    if not booking:
        flash('Booking not found. Please try again.', 'error')
        return redirect(url_for('booking'))
    
    service = get_service_by_id(booking['service_id'])
    
    if request.method == 'POST':
        # Process payment form submission
        payment_data = {
            'booking_id': booking_id,
            'amount': service['price'],
            'card_number': request.form.get('card_number'),
            'card_holder': request.form.get('card_holder'),
            'expiry_date': request.form.get('expiry_date'),
            'cvv': request.form.get('cvv')
        }
        
        # Process payment (mock)
        payment_result = process_payment(payment_data)
        
        if payment_result['status'] == 'success':
            # Update booking status
            booking['status'] = 'confirmed'
            
            # Send confirmation email (mock)
            email_html = generate_booking_confirmation_email(booking, payment_result)
            send_email(booking['email'], 'Spa en Ruedas - Confirmación de Reserva', email_html)
            
            # Store payment result in session
            session['payment_result'] = payment_result
            
            # Redirect to confirmation page
            return redirect(url_for('confirmation'))
        else:
            flash('Payment failed. Please try again.', 'error')
    
    # GET request - show payment form
    return render_template('payment.html', booking=booking, service=service)

@app.route('/confirmation')
def confirmation():
    """Render the booking confirmation page."""
    booking_id = session.get('booking_id')
    payment_result = session.get('payment_result')
    
    if not booking_id or not payment_result:
        flash('No booking information found. Please start the booking process again.', 'error')
        return redirect(url_for('booking'))
    
    booking = get_booking(booking_id)
    if not booking:
        flash('Booking not found. Please try again.', 'error')
        return redirect(url_for('booking'))
    
    service = get_service_by_id(booking['service_id'])
    
    # Clear session data
    session.pop('booking_id', None)
    session.pop('payment_result', None)
    
    return render_template('confirmation.html', booking=booking, service=service, payment=payment_result)

@app.route('/calendar')
def calendar():
    """Render the calendar page."""
    events = get_all_events()
    locations = get_all_locations()
    return render_template('calendar.html', events=events, locations=locations)

@app.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Render the contact page or process contact form."""
    if request.method == 'POST':
        # Process contact form submission
        message_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'subject': request.form.get('subject'),
            'message': request.form.get('message')
        }
        
        # Create message
        message = create_contact_message(message_data)
        
        # Send notification email (mock)
        flash('Thank you for your message. We will get back to you soon!', 'success')
        return redirect(url_for('contact'))
    
    # GET request - show contact form
    return render_template('contact.html')
