from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from app.models import Trabajador, TokenBlocklist, db
from app.schemas import UserLoginSchema, PerfilSchema

blp = Blueprint("Auth API", "auth_api", description="Autenticación y Tokens JWT")

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    def post(self, user_data):
        """Inicia sesión y devuelve un Token de Acceso"""
        usuario = Trabajador.query.filter_by(email=user_data["email"]).first()

        if usuario and usuario.check_password(user_data["password"]):
            access_token = create_access_token(identity=str(usuario.id_trabajador))
            return {"access_token": access_token}

        abort(401, message="Credenciales inválidas.")

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        """Cierra sesión revocando el token actual (Persistente en BD)"""
        jti = get_jwt()["jti"]

        # --- NUEVO: GUARDAR EN BASE DE DATOS ---
        token_bloqueado = TokenBlocklist(jti=jti)
        db.session.add(token_bloqueado)
        db.session.commit()
        # ---------------------------------------

        return {"message": "Sesión cerrada correctamente. Token revocado."}

@blp.route("/perfil")
class UserProfile(MethodView):
    @jwt_required()
    @blp.response(200, PerfilSchema)
    def get(self):
        """Devuelve los datos del usuario conectado"""
        current_user_id = get_jwt_identity()
        usuario = Trabajador.query.get_or_404(current_user_id)
        return usuario