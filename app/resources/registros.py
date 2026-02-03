from datetime import datetime
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Trabajador, Registro, db

blp = Blueprint("Registros API", "registros_api", description="Gestión de Fichajes")

@blp.route("/fichar/entrada")
class FicharEntrada(MethodView):
    @jwt_required()
    def post(self):
        """Registra una ENTRADA (Solo si no estás ya dentro)"""
        current_user_id = get_jwt_identity()
        ahora = datetime.now()
        fecha_hoy = ahora.date()

        # 1. Comprobar si ya tiene un fichaje abierto (sin cerrar)
        # Buscamos en CUALQUIER fecha, porque si se le olvidó cerrar ayer, sigue "dentro"
        registro_abierto = Registro.query.filter_by(
            id_trabajador=current_user_id,
            hora_salida=None
        ).first()

        if registro_abierto:
            # Si ya está dentro, devolvemos error 409 (Conflicto)
            abort(409, message="Error: Ya tienes un turno abierto. Debes fichar salida primero.")

        # 2. Crear el nuevo fichaje
        nuevo_registro = Registro(
            fecha=fecha_hoy,
            hora_entrada=ahora,
            id_trabajador=current_user_id
        )
        db.session.add(nuevo_registro)
        db.session.commit()

        return {
            "mensaje": "Entrada registrada correctamente",
            "tipo": "entrada",
            "hora": ahora.strftime("%H:%M")
        }

@blp.route("/fichar/salida")
class FicharSalida(MethodView):
    @jwt_required()
    def post(self):
        """Registra una SALIDA (Solo si tienes un turno abierto)"""
        current_user_id = get_jwt_identity()
        ahora = datetime.now()

        # 1. Buscar el fichaje que está abierto
        registro_abierto = Registro.query.filter_by(
            id_trabajador=current_user_id,
            hora_salida=None
        ).first()

        if not registro_abierto:
            # Si no hay nada abierto, no puedes salir. Error 409.
            abort(409, message="Error: No tienes ningún turno abierto. Debes fichar entrada primero.")

        # 2. Cerrar el fichaje
        registro_abierto.hora_salida = ahora
        db.session.commit()

        return {
            "mensaje": "Salida registrada correctamente",
            "tipo": "salida",
            "hora": ahora.strftime("%H:%M")
        }