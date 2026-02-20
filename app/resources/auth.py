from flask import url_for, render_template_string, request
from flask_mail import Message
from app.extensions import mail
from datetime import timedelta
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from app.models import Trabajador, TokenBlocklist, db, Empresa
from app.schemas import UserLoginSchema, PerfilSchema, ResetRequestSchema, ResetPasswordSchema, EmpresaListaSchema

blp = Blueprint("Auth API", "auth_api", description="Autenticación y Tokens JWT")

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    def post(self, user_data):
        """Inicia sesión y devuelve Token, Nombre Completo y Rol"""
        usuario = Trabajador.query.filter_by(email=user_data["email"]).first()

        if usuario and usuario.check_password(user_data["password"]):
            access_token = create_access_token(identity=str(usuario.id_trabajador))

            nombre_rol = "Trabajador" # Por defecto
            if usuario.rol:
                nombre_rol = usuario.rol.nombre_rol

            return {
                "access_token": access_token,
                "nombre": f"{usuario.nombre} {usuario.apellidos}",
                "rol": nombre_rol
            }

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

@blp.route("/admin/empresas")
class ListaEmpresasAdmin(MethodView):
    @jwt_required()
    @blp.response(200, EmpresaListaSchema(many=True))
    def get(self):
        """(SUPERADMIN) Listar todas las empresas para el selector"""
        current_user_id = get_jwt_identity()
        admin = Trabajador.query.get(current_user_id)
        if admin.rol.nombre_rol != 'Superadministrador':
            abort(403, message="Acceso denegado. Solo Superadmin.")
        return Empresa.query.all()

@blp.route("/admin/empleados")
class ListaEmpleadosAdmin(MethodView):
    @jwt_required()
    @blp.response(200, PerfilSchema(many=True))
    def get(self):
        """Listar mis empleados / Listar empleados por empresa"""
        current_user_id = get_jwt_identity()
        admin = Trabajador.query.get(current_user_id)

        empresa_id = request.args.get("empresa_id")

        if admin.rol.nombre_rol == 'Superadministrador':
            if not empresa_id:
                abort(400, message="Debes indicar empresa_id.")
            return Trabajador.query.filter_by(idEmpresa=empresa_id).all()
        else:
            if not admin.idEmpresa:
                 abort(403, message="No eres administrador de empresa.")
            return Trabajador.query.filter_by(idEmpresa=admin.idEmpresa).all()