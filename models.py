import json
import uuid
from datetime import datetime
import os
from typing import List, Dict, Any, Optional

# In-memory storage for the MVP
class Storage:
    def __init__(self):
        self.services = []
        self.bookings = []
        self.events = []
        self.locations = []
        self.users = []
        self.messages = []
        self._load_initial_data()
    
    def _load_initial_data(self):
        """Load initial data for services, locations, and events."""
        # Services data
        self.services = [
            {
                "id": "1",
                "name": "Masaje terapéutico y relajante",
                "description": "Relaja tensiones musculares y reduce el estrés, mejorando la circulación sanguínea.",
                "price": 65.00,
                "duration": 60,
                "image": "massage-therapy.svg",
                "benefits": ["Reduce el estrés", "Mejora la circulación", "Relaja la musculatura"]
            },
            {
                "id": "2",
                "name": "Masaje profundo (Deep Tissue)",
                "description": "Técnica enfocada en capas profundas del músculo para aliviar tensiones crónicas.",
                "price": 85.00,
                "duration": 60,
                "image": "deep-tissue.svg",
                "benefits": ["Alivia dolor crónico", "Recuperación muscular", "Mejora la postura"]
            },
            {
                "id": "3",
                "name": "Masaje deportivo",
                "description": "Enfocado en prevenir lesiones y mejorar el rendimiento físico de los deportistas.",
                "price": 75.00,
                "duration": 60,
                "image": "sports-massage.svg",
                "benefits": ["Previene lesiones", "Mejora rendimiento", "Acelera recuperación"]
            },
            {
                "id": "4",
                "name": "Ventosaterapia (Cupping)",
                "description": "Técnica milenaria que utiliza ventosas para mejorar la circulación y aliviar el dolor.",
                "price": 55.00,
                "duration": 45,
                "image": "cupping.svg",
                "benefits": ["Desintoxica", "Alivia dolor muscular", "Mejora flujo sanguíneo"]
            },
            {
                "id": "5",
                "name": "Reflexología",
                "description": "Masaje en puntos específicos de pies y manos que conectan con órganos del cuerpo.",
                "price": 50.00,
                "duration": 45,
                "image": "reflexology.svg",
                "benefits": ["Equilibra energía", "Mejora sistema nervioso", "Reduce estrés"]
            },
            {
                "id": "6",
                "name": "Tratamientos faciales",
                "description": "Limpieza profunda e hidratación que rejuvenece y revitaliza la piel del rostro.",
                "price": 70.00,
                "duration": 60,
                "image": "facial-treatment.svg",
                "benefits": ["Rejuvenece", "Limpia poros", "Hidrata profundamente"]
            },
            {
                "id": "7",
                "name": "Aromaterapia",
                "description": "Terapia que utiliza aceites esenciales para mejorar el bienestar físico y emocional.",
                "price": 60.00,
                "duration": 60,
                "image": "aromatherapy.svg",
                "benefits": ["Relaja mente", "Equilibra emociones", "Reduce ansiedad"]
            }
        ]
        
        # Locations data
        self.locations = [
            {
                "id": "1",
                "name": "San Juan - Condado",
                "address": "Calle Ashford, Condado, San Juan, PR",
                "image": "condado.svg",
                "description": "Ubicación principal en la zona turística de Condado"
            },
            {
                "id": "2",
                "name": "Isla Verde",
                "address": "Ave. Isla Verde, Carolina, PR",
                "image": "isla-verde.svg",
                "description": "A pasos de las hermosas playas de Isla Verde"
            },
            {
                "id": "3",
                "name": "Viejo San Juan",
                "address": "Calle San Francisco, Viejo San Juan, PR",
                "image": "viejo-san-juan.svg",
                "description": "En el corazón histórico de la ciudad"
            },
            {
                "id": "4",
                "name": "Rincón",
                "address": "Carr. 413, Rincón, PR",
                "image": "rincon.svg",
                "description": "Frente al mar en la capital del surf"
            }
        ]
        
        # Events data
        self.events = [
            {
                "id": "1",
                "title": "Festival de Bienestar",
                "date": "2023-12-15",
                "location_id": "1",
                "description": "Evento especial con descuentos en todos nuestros servicios"
            },
            {
                "id": "2",
                "title": "Día de Crucero - Carnival",
                "date": "2023-11-20",
                "location_id": "3",
                "description": "Servicios para turistas de crucero con paquetes especiales"
            },
            {
                "id": "3",
                "title": "Feria de Salud Rincón",
                "date": "2023-12-05",
                "location_id": "4",
                "description": "Participación en la feria anual de salud y bienestar"
            }
        ]
    
    def add_booking(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new booking to the storage."""
        booking_id = str(uuid.uuid4())
        booking = {
            "id": booking_id,
            "created_at": datetime.now().isoformat(),
            **booking_data
        }
        self.bookings.append(booking)
        return booking
    
    def get_booking(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """Get a booking by ID."""
        for booking in self.bookings:
            if booking["id"] == booking_id:
                return booking
        return None
    
    def get_services(self) -> List[Dict[str, Any]]:
        """Get all services."""
        return self.services
    
    def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Get a service by ID."""
        for service in self.services:
            if service["id"] == service_id:
                return service
        return None
    
    def get_events(self) -> List[Dict[str, Any]]:
        """Get all events."""
        return self.events
    
    def get_locations(self) -> List[Dict[str, Any]]:
        """Get all locations."""
        return self.locations
    
    def add_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new contact message to the storage."""
        message_id = str(uuid.uuid4())
        message = {
            "id": message_id,
            "created_at": datetime.now().isoformat(),
            **message_data
        }
        self.messages.append(message)
        return message

# Initialize storage
storage = Storage()
