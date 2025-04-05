import os
import logging
from flask import Flask, render_template
from flask_cors import CORS
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from models_sql import db

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

# Crear la aplicación Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "spa-en-ruedas-secret-key")

# Configurar la base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Habilitar CORS
CORS(app)

# Configurar CSRF Protection
csrf = CSRFProtect(app)

# Inicializar extensiones
db.init_app(app)

# Configurar correo electrónico
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'test@example.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'password')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'test@example.com')
mail = Mail(app)

# Crear tablas si no existen
with app.app_context():
    db.create_all()
    app.logger.info("Tablas de base de datos creadas")

# Registrar manejadores de errores
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, message="Página no encontrada"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, message="Error interno del servidor"), 500
