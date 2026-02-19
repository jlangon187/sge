from flask import url_for, render_template_string
from flask_mail import Message
from app.extensions import mail
from datetime import timedelta
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from app.models import Trabajador, TokenBlocklist, db
from app.schemas import UserLoginSchema, PerfilSchema, ResetRequestSchema, ResetPasswordSchema

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

        token_bloqueado = TokenBlocklist(jti=jti)
        db.session.add(token_bloqueado)
        db.session.commit()

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

@blp.route("/reset-password-request")
class ResetPasswordRequest(MethodView):
    @blp.arguments(ResetRequestSchema)
    def post(self, user_data):
        """Solicitar cambio de contraseña (envía email)"""
        email = user_data.get("email")
        usuario = Trabajador.query.filter_by(email=email).first()

        if not usuario:
            # Por seguridad, no decimos si el email existe o no
            return {"message": "Si el correo existe, se ha enviado un enlace."}, 200

        # Generamos un token temporal (15 min)
        # Usamos create_access_token pero con un tiempo corto
        reset_token = create_access_token(identity=str(usuario.id_trabajador), expires_delta=timedelta(minutes=15))

        # Crear el link
        link = f"https://javiliyors.eu.pythonanywhere.com/auth/reset-password/{reset_token}"

        msg = Message("Recuperar Contraseña - Control Presencia",
                      recipients=[usuario.email])
        msg.body = f"Hola {usuario.nombre},\n\nPara cambiar tu contraseña, usa este token en la App o haz clic aquí:\n{link}\n\nEste enlace caduca en 15 minutos."

        try:
            mail.send(msg)
            return {"message": "Correo enviado correctamente."}, 200
        except Exception as e:
            return {"message": "Error al enviar correo.", "error": str(e)}, 500

@blp.route("/reset-password")
class ResetPassword(MethodView):
    @jwt_required()
    @blp.arguments(ResetPasswordSchema)
    def post(self, user_data):
        """Cambiar contraseña usando el token del email"""
        nueva_password = user_data.get("password")
        usuario_id = get_jwt_identity()

        usuario = Trabajador.query.get(usuario_id)
        if not usuario:
            abort(404, message="Usuario no encontrado.")

        usuario.set_password(nueva_password)
        db.session.commit()

        return {"message": "Contraseña actualizada correctamente."}, 200