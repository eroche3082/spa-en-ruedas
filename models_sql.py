import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Inicializar SQLAlchemy
db = SQLAlchemy()

class Usuario(db.Model):
    """Modelo para administradores y terapistas."""
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    password_hash = db.Column(db.String(256))
    rol = db.Column(db.String(20), default='terapista')  # 'admin' o 'terapista'
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Servicio(db.Model):
    """Modelo para servicios de spa."""
    __tablename__ = 'servicios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    duracion = db.Column(db.Integer, nullable=False)  # Duración en minutos
    imagen = db.Column(db.String(255))
    categoria = db.Column(db.String(50))
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    reservaciones = db.relationship('Reservacion', backref='servicio', lazy=True)
    
    def __repr__(self):
        return f'<Servicio {self.nombre}>'

class Ubicacion(db.Model):
    """Modelo para ubicaciones donde se ofrece el servicio."""
    __tablename__ = 'ubicaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(255))
    descripcion = db.Column(db.Text)
    imagen = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    eventos = db.relationship('Evento', backref='ubicacion', lazy=True)
    reservaciones = db.relationship('Reservacion', backref='ubicacion', lazy=True)
    
    def __repr__(self):
        return f'<Ubicacion {self.nombre}>'

class Evento(db.Model):
    """Modelo para eventos especiales."""
    __tablename__ = 'eventos'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time)
    hora_fin = db.Column(db.Time)
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'), nullable=False)
    
    def __repr__(self):
        return f'<Evento {self.titulo}>'

class Cliente(db.Model):
    """Modelo para clientes."""
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    reservaciones = db.relationship('Reservacion', backref='cliente', lazy=True)
    
    def __repr__(self):
        return f'<Cliente {self.nombre}>'

class Reservacion(db.Model):
    """Modelo para reservaciones."""
    __tablename__ = 'reservaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'), nullable=False)
    terapista_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, confirmada, cancelada, completada
    comentarios = db.Column(db.Text)
    codigo_confirmacion = db.Column(db.String(20), unique=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    pagos = db.relationship('Pago', backref='reservacion', lazy=True)
    
    def __repr__(self):
        return f'<Reservacion #{self.id}>'

class Pago(db.Model):
    """Modelo para pagos."""
    __tablename__ = 'pagos'
    
    id = db.Column(db.Integer, primary_key=True)
    reservacion_id = db.Column(db.Integer, db.ForeignKey('reservaciones.id'), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    metodo = db.Column(db.String(50), nullable=False)  # tarjeta, paypal, efectivo
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, completado, rechazado, reembolsado
    referencia = db.Column(db.String(100))  # ID de transacción externa o referencia
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Pago #{self.id}>'

class Mensaje(db.Model):
    """Modelo para mensajes de contacto."""
    __tablename__ = 'mensajes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    asunto = db.Column(db.String(200))
    mensaje = db.Column(db.Text, nullable=False)
    leido = db.Column(db.Boolean, default=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Mensaje #{self.id}>'