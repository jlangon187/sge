import os
import time

# Esto obliga al servidor de PythonAnywhere a usar la hora local de España
os.environ["TZ"] = "Europe/Madrid"
try:
    time.tzset()
except AttributeError:
    pass

class Config:
    SECRET_KEY = "clave-super-secreta"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://javiliyors:rootroot@javiliyors.mysql.eu.pythonanywhere-services.com/javiliyors$sge"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True
    }

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

    JWT_SECRET_KEY = "clave-super-secreta-jwt-mas-larga-y-segura"

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'jlangon187@iesfuengirola1.es'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'xpzf pooz alhx mfnz'
    MAIL_DEFAULT_SENDER = ('Control Presencia', MAIL_USERNAME)

    @staticmethod
    def init_app(app):
        pass

config = {
    'default': Config
}