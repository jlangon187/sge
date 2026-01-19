class Config:
    SECRET_KEY = "clave-super-secreta" # (La que tengas puesta)
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://javiliyors:rootroot@javiliyors.mysql.eu.pythonanywhere-services.com/javiliyors$sge"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True
    }

    @staticmethod
    def init_app(app):
        pass

config = {
    'default': Config
}