from flask_sqlalchemy import SQLAlchemy
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_bootstrap import Bootstrap

# Inicializamos las extensiones
db = SQLAlchemy()
api = Api()
jwt = JWTManager()
bootstrap = Bootstrap()