from flask import Flask
from config import config
from .extensions import db, api, jwt, bootstrap
from .blocklist import BLOCKLIST
from flask_migrate import Migrate

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # --- INICIALIZAR EXTENSIONES ---
    db.init_app(app)
    bootstrap.init_app(app)
    jwt.init_app(app)
    api.init_app(app)

    Migrate(app, db)

    # --- CALLBACKS DE JWT (Lista Negra) ---
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            {"description": "El token ha sido revocado.", "error": "token_revoked"},
            401,
        )

    from .main import main_bp
    app.register_blueprint(main_bp)

    from .auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .empleados import empleados_bp
    app.register_blueprint(empleados_bp, url_prefix='/admin/empleados')

    from .empresas import empresas_bp
    app.register_blueprint(empresas_bp, url_prefix='/admin/empresas')

    from .horarios import horarios_bp
    app.register_blueprint(horarios_bp, url_prefix='/admin/horarios')

    from .roles import roles_bp
    app.register_blueprint(roles_bp, url_prefix='/admin/roles')

    from .superadmins import superadmins_bp
    app.register_blueprint(superadmins_bp, url_prefix='/admin/superadmins')

    # API de Auth y Fichajes
    from app.resources.auth import blp as AuthApiBlueprint
    api.register_blueprint(AuthApiBlueprint)

    from app.resources.registros import blp as RegistrosApiBlueprint
    api.register_blueprint(RegistrosApiBlueprint)

    return app