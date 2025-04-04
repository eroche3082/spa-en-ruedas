import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from models import storage

def get_all_services():
    """Get all spa services."""
    return storage.get_services()

def get_service_by_id(service_id: str):
    """Get a service by ID."""
    return storage.get_service(service_id)

def get_all_events():
    """Get all upcoming events."""
    return storage.get_events()

def get_all_locations():
    """Get all spa locations."""
    return storage.get_locations()

def create_booking(booking_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new booking."""
    return storage.add_booking(booking_data)

def get_booking(booking_id: str) -> Optional[Dict[str, Any]]:
    """Get a booking by ID."""
    return storage.get_booking(booking_id)

def process_payment(payment_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a payment (mock implementation)."""
    payment_id = str(uuid.uuid4())
    transaction_result = {
        "payment_id": payment_id,
        "status": "success",
        "amount": payment_data.get("amount"),
        "timestamp": datetime.now().isoformat(),
        "confirmation_code": f"SPR-{payment_id[:8].upper()}"
    }
    return transaction_result

def send_confirmation_email(booking_data: Dict[str, Any], payment_data: Dict[str, Any]) -> bool:
    """Send confirmation email (mock implementation)."""
    # In a real implementation, this would use Flask-Mail to send an actual email
    print(f"Sending confirmation email for booking {booking_data['id']} to {booking_data['email']}")
    return True

def create_contact_message(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new contact message."""
    return storage.add_message(message_data)

def get_available_slots(date_str: str, location_id: str) -> List[str]:
    """Get available time slots for a specific date and location."""
    # This would normally check against existing bookings
    # For the MVP, we'll return a fixed set of time slots
    time_slots = ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00"]
    
    # In a real implementation, we would filter out already booked slots
    # For now, we'll just return all slots
    return time_slots
