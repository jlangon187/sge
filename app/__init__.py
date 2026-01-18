from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import config

# 1. Inicializamos las extensiones fuera de la función (globales)
# Se crean vacías para que luego puedan ser usadas por cualquier módulo
bootstrap = Bootstrap()
db = SQLAlchemy()

def create_app(config_name):
    # 2. Creamos la aplicación Flask
    app = Flask(__name__)

    # 3. Cargamos la configuración (desde config.py)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 4. Iniciamos las extensiones con la aplicación creada
    bootstrap.init_app(app)
    db.init_app(app)

    # --- REGISTRO DE BLUEPRINTS (MÓDULOS) ---

    # Módulo de Autenticación (Login/Logout)
    # Lo importamos aquí dentro para evitar dependencias circulares
    from .auth import auth_bp
    app.register_blueprint(auth_bp)
    # Nota: No pongo url_prefix para que las rutas sean /login y /logout directas

    # Módulo Principal (Dashboard/Inicio)
    # Este será el siguiente que crearemos. Lo dejo aquí ya puesto.
    from .main import main_bp
    app.register_blueprint(main_bp)

    # --- FUTUROS MÓDULOS (Descomenta a medida que los crees) ---

    # from .empresas import empresas_bp
    # app.register_blueprint(empresas_bp, url_prefix='/admin/empresas')

    # from .empleados import empleados_bp
    # app.register_blueprint(empleados_bp, url_prefix='/empleados')

    # from .superadmins import superadmins_bp
    # app.register_blueprint(superadmins_bp, url_prefix='/admin/superadmins')

    return app