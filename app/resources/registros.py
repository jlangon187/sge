from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Registro, Trabajador, Franjas, db
from app.schemas import FichajeSchema, RegistroSchema
from datetime import datetime, timedelta
import pytz  # <--- IMPORTANTE: Necesitamos esto para la hora de España
from sqlalchemy import func

# Definimos la zona horaria de España
MADRID_TZ = pytz.timezone('Europe/Madrid')

def calcular_distancia(lat1, lon1, lat2, lon2):
    from math import radians, cos, sin, asin, sqrt
    # Radio de la tierra en km (aprox)
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    distancia_km = R * c
    return distancia_km * 1000 # Devolver en metros

blp = Blueprint("Registros API", "registros_api", description="Fichajes de entrada y salida")

@blp.route("/fichar/entrada")
class FicharEntrada(MethodView):
    @jwt_required()
    @blp.arguments(FichajeSchema)
    def post(self, fichaje_data):
        """Fichar ENTRADA """
        current_user_id = get_jwt_identity()
        trabajador = Trabajador.query.get_or_404(current_user_id)

        ahora_madrid = datetime.now(MADRID_TZ)
        ahora_naive = ahora_madrid.replace(tzinfo=None)
        fecha_hoy = ahora_naive.date()

        empresa = trabajador.empresa
        if empresa and empresa.latitud is not None and empresa.longitud is not None:
            distancia = calcular_distancia(
                fichaje_data["latitud"], fichaje_data["longitud"],
                empresa.latitud, empresa.longitud
            )
            radio_max = empresa.radio if empresa.radio else 100
            if distancia > radio_max:
                abort(403, message=f"Estás fuera del radio permitido ({int(distancia)}m).")

        if trabajador.idHorario:
            dia_semana_id = ahora_naive.weekday() + 1

            franja_hoy = Franjas.query.filter_by(
                id_horario=trabajador.idHorario,
                id_dia=dia_semana_id
            ).first()

            if not franja_hoy:
                abort(403, message="Hoy no tienes turno asignado (No existe franja para hoy).")

            hora_entrada_teorica = datetime.combine(fecha_hoy, franja_hoy.hora_entrada)
            hora_salida_teorica = datetime.combine(fecha_hoy, franja_hoy.hora_salida)

            margen_inicio = hora_entrada_teorica - timedelta(minutes=30)

            print(f"DEBUG: Ahora: {ahora_naive} | Inicio Teórico: {hora_entrada_teorica} | Margen: {margen_inicio}")

            if ahora_naive < margen_inicio:
                 abort(403, message=f"Demasiado pronto. Tu turno empieza a las {franja_hoy.hora_entrada}.")

            if ahora_naive > hora_salida_teorica:
                 abort(403, message="Tu turno de hoy ya ha terminado.")


        if Registro.query.filter_by(id_trabajador=current_user_id, hora_salida=None).first():
            abort(409, message="Ya tienes un turno abierto.")

        nuevo_registro = Registro(
            fecha=fecha_hoy,
            hora_entrada=ahora_naive,
            id_trabajador=current_user_id,
            horas_extra=0.0,
            latitud=fichaje_data.get("latitud"),
            longitud=fichaje_data.get("longitud")
        )
        db.session.add(nuevo_registro)
        db.session.commit()

        return {
            "mensaje": "Entrada registrada correctamente",
            "hora": ahora_naive.strftime("%H:%M")
        }


@blp.route("/fichar/salida")
class FicharSalida(MethodView):
    @jwt_required()
    def post(self):
        """Fichar SALIDA """
        current_user_id = get_jwt_identity()
        trabajador = Trabajador.query.get_or_404(current_user_id)

        ahora_madrid = datetime.now(MADRID_TZ)
        ahora_naive = ahora_madrid.replace(tzinfo=None)

        registro = Registro.query.filter_by(id_trabajador=current_user_id, hora_salida=None).first()
        if not registro:
            abort(409, message="No tienes ningún turno abierto.")

        horas_extra_calculadas = 0.0

        if trabajador.idHorario:
            dia_semana_id = ahora_naive.weekday() + 1
            franja_hoy = Franjas.query.filter_by(
                id_horario=trabajador.idHorario,
                id_dia=dia_semana_id
            ).first()

            if franja_hoy:
                salida_teorica = datetime.combine(ahora_naive.date(), franja_hoy.hora_salida)

                print(f"DEBUG: Salida Real: {ahora_naive} | Teórica: {salida_teorica}")

                if ahora_naive > salida_teorica:
                    diferencia = ahora_naive - salida_teorica
                    # Convertir a horas decimales
                    horas_extra_calculadas = round(diferencia.total_seconds() / 3600, 2)

        registro.hora_salida = ahora_naive
        registro.horas_extra = horas_extra_calculadas

        db.session.commit()

        msg = "Salida registrada."
        if horas_extra_calculadas > 0:
            msg += f" Has realizado {horas_extra_calculadas} horas extra."

        return {
            "mensaje": msg,
            "hora": ahora_naive.strftime("%H:%M"),
            "horas_extra": horas_extra_calculadas
        }

@blp.route("/fichajes")
class FichajesList(MethodView):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        registros = Registro.query.filter_by(id_trabajador=user_id).order_by(Registro.hora_entrada.desc()).all()

        resultado = []
        for reg in registros:
            resultado.append({
                "id_registro": reg.id_registro,
                "fecha": reg.fecha.isoformat(),
                "hora_entrada": reg.hora_entrada.isoformat(),
                "hora_salida": reg.hora_salida.isoformat() if reg.hora_salida else None,
                "horas_extra": reg.horas_extra
            })
        return resultado

@blp.route("/admin/registros/<int:id_trabajador>")
class HistorialAdmin(MethodView):
    @jwt_required()
    @blp.response(200, RegistroSchema(many=True))
    def get(self, id_trabajador):
        """Ver historial de un empleado específico"""
        current_user_id = get_jwt_identity()
        admin = Trabajador.query.get(current_user_id)
        empleado = Trabajador.query.get_or_404(id_trabajador)

        if admin.rol.nombre_rol != 'Superadministrador':
            if not admin.idEmpresa:
                abort(403, message="Acceso denegado. No tienes empresa asignada.")
            if empleado.idEmpresa != admin.idEmpresa:
                abort(403, message="Este empleado no pertenece a tu empresa.")

        return Registro.query.filter_by(id_trabajador=id_trabajador)\
            .order_by(Registro.fecha.desc(), Registro.hora_entrada.desc()).all()