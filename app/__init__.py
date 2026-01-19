from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()

def create_app(config_name):

    app = Flask(__name__)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)

    # --- REGISTRO DE BLUEPRINTS (MÓDULOS) ---

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .main import main_bp
    app.register_blueprint(main_bp)

    from .empresas import empresas_bp
    app.register_blueprint(empresas_bp, url_prefix='/admin/empresas')

    from .empleados import empleados_bp
    app.register_blueprint(empleados_bp, url_prefix='/empleados')

    from .superadmins import superadmins_bp
    app.register_blueprint(superadmins_bp, url_prefix='/admin/superadmins')

    from .roles import roles_bp
    app.register_blueprint(roles_bp, url_prefix='/admin/roles')

    from .horarios import horarios_bp
    app.register_blueprint(horarios_bp, url_prefix='/horarios')

    return app