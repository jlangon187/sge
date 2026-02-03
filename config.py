import os
import time # <--- IMPORTANTE: Necesitamos importar time

# --- NUEVO: FORZAR ZONA HORARIA DE MADRID ---
# Esto obliga al servidor de PythonAnywhere a usar la hora local de España
os.environ["TZ"] = "Europe/Madrid"
try:
    time.tzset()
except AttributeError:
    # time.tzset() solo funciona en Linux (PythonAnywhere).
    # El try/except evita que te de error si lo pruebas en Windows.
    pass

class Config:
    SECRET_KEY = "clave-super-secreta"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://javiliyors:rootroot@javiliyors.mysql.eu.pythonanywhere-services.com/javiliyors$sge"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True
    }

    # --- NUEVA CONFIGURACIÓN API REST (Flask-Smorest) ---
    API_TITLE = "API Control de Presencia"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    API_SPEC_OPTIONS = {
        "security": [{"bearerAuth": []}],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
        },
    }

    # --- NUEVA CONFIGURACIÓN JWT (Seguridad) ---
    JWT_SECRET_KEY = "clave-super-secreta-jwt-mas-larga-y-segura"

    @staticmethod
    def init_app(app):
        pass

config = {
    'default': Config
}