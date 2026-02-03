from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from app.models import Trabajador
from app.schemas import UserLoginSchema
from app.blocklist import BLOCKLIST

# Definimos el Blueprint de la API
blp = Blueprint("Auth API", "auth_api", description="Autenticación y Tokens JWT")

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    def post(self, user_data):
        """Inicia sesión y devuelve un Token de Acceso"""

        usuario = Trabajador.query.filter_by(email=user_data["email"]).first()

        if usuario and usuario.check_password(user_data["password"]):
            # Generar Token (guardamos el ID del trabajador como identidad)
            access_token = create_access_token(identity=str(usuario.id_trabajador))
            return {"access_token": access_token}

        abort(401, message="Credenciales inválidas (Email o contraseña incorrectos).")

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required() # <--- Requiere que envíes un token válido
    def post(self):
        """Cierra sesión revocando el token actual"""

        # 1. Obtenemos el identificador único del token (jti)
        jti = get_jwt()["jti"]

        # 2. Lo añadimos a la lista negra
        BLOCKLIST.add(jti)

        return {"message": "Sesión cerrada correctamente. Token revocado."}