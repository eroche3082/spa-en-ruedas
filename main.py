from app import app
from models_sql import db
from init_db import crear_datos_iniciales
from routes_new import *  # Importar todas las rutas

# Inicializar datos de ejemplo
crear_datos_iniciales()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
