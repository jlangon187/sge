import math
from datetime import datetime
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Trabajador, Registro, db
from app.schemas import RegistroSchema, FichajeSchema

blp = Blueprint("Registros API", "registros_api", description="Gestión de Fichajes")

# --- FÓRMULA DE HAVERSINE (Matemáticas para distancia GPS) ---
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371000  # Radio de la Tierra en metros
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
# -------------------------------------------------------------

@blp.route("/fichajes")
class HistorialRegistros(MethodView):
    @jwt_required()
    @blp.response(200, RegistroSchema(many=True))
    def get(self):
        """Obtiene el historial de fichajes del usuario"""
        current_user_id = get_jwt_identity()
        return Registro.query.filter_by(id_trabajador=current_user_id)\
            .order_by(Registro.fecha.desc(), Registro.hora_entrada.desc()).all()

@blp.route("/fichar/entrada")
class FicharEntrada(MethodView):
    @jwt_required()
    @blp.arguments(FichajeSchema)
    def post(self, fichaje_data):
        """Fichar ENTRADA (Valida distancia con el radio de la BD)"""
        current_user_id = get_jwt_identity()
        trabajador = Trabajador.query.get_or_404(current_user_id)

        # 1. VALIDACIÓN GEOLOCALIZACIÓN
        empresa = trabajador.empresa

        # Solo validamos si la empresa tiene coordenadas configuradas
        if empresa and empresa.latitud is not None and empresa.longitud is not None:
            distancia = calcular_distancia(
                fichaje_data["latitud"],
                fichaje_data["longitud"],
                empresa.latitud,
                empresa.longitud
            )

            radio_max = empresa.radio if empresa.radio else 100

            if distancia > radio_max:
                abort(403, message=f"Estás fuera del radio permitido. Distancia: {int(distancia)}m (Máx permitido: {radio_max}m).")

        # 2. PROCESO DE FICHAJE
        ahora = datetime.now()
        fecha_hoy = ahora.date()

        if Registro.query.filter_by(id_trabajador=current_user_id, hora_salida=None).first():
            abort(409, message="Ya tienes un turno abierto. Debes fichar salida primero.")

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
        """Fichar SALIDA"""
        current_user_id = get_jwt_identity()
        ahora = datetime.now()

        registro = Registro.query.filter_by(id_trabajador=current_user_id, hora_salida=None).first()

        if not registro:
            abort(409, message="No tienes ningún turno abierto.")

        registro.hora_salida = ahora
        db.session.commit()

        return {
            "mensaje": "Salida registrada correctamente",
            "tipo": "salida",
            "hora": ahora.strftime("%H:%M")
        }