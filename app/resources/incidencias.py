from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Incidencia, db
from app.schemas import IncidenciaSchema
from datetime import datetime

blp = Blueprint("Incidencias API", "incidencias_api", description="Gestión de incidencias desde App")

@blp.route("/incidencias")
class IncidenciasResource(MethodView):

    @jwt_required()
    @blp.arguments(IncidenciaSchema)
    def post(self, incidencia_data):
        """Crear una nueva incidencia (Desde APP)"""
        current_user = get_jwt_identity()

        nueva_incidencia = Incidencia(
            titulo=incidencia_data["titulo"],
            descripcion=incidencia_data["descripcion"],
            id_trabajador=current_user,
            fecha_hora=datetime.utcnow()
        )

        try:
            db.session.add(nueva_incidencia)
            db.session.commit()
            return {"message": "Incidencia registrada correctamente"}, 201
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"Error al guardar incidencia: {str(e)}")

    @jwt_required()
    @blp.response(200, IncidenciaSchema(many=True))
    def get(self):
        """Listar mis incidencias"""
        current_user = get_jwt_identity()
        return Incidencia.query.filter_by(id_trabajador=current_user).order_by(Incidencia.fecha_hora.desc()).all()