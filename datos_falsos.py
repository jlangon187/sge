import random
from datetime import datetime, timedelta, time
from app import create_app, db
from app.models import Trabajador, Registro, Incidencia, Empresa

# Inicializamos la app
app = create_app('default')

def generar_datos():
    with app.app_context():
        print("--- GENERADOR DE DATOS DE PRUEBA ---")

        # 1. Buscar una empresa válida
        empresa = Empresa.query.first()
        if not empresa:
            print("❌ Error: No hay ninguna empresa creada. Crea una primero desde el panel.")
            return

        print(f"🏢 Empresa encontrada: {empresa.nombrecomercial}")

        # 2. Buscar empleados de esa empresa
        empleados = Trabajador.query.filter_by(idEmpresa=empresa.id_empresa).all()
        if not empleados:
            print("❌ Error: Esta empresa no tiene empleados. Crea alguno primero.")
            return

        print(f"👥 Se han encontrado {len(empleados)} empleados.")

        # 3. Generar Fichajes (Últimos 7 días)
        registros_creados = 0
        fecha_hoy = datetime.now().date()

        # Recorremos los últimos 7 días
        for i in range(7):
            fecha_iteracion = fecha_hoy - timedelta(days=i)

            # Saltamos fines de semana (Sábado=5, Domingo=6) para hacerlo realista
            if fecha_iteracion.weekday() >= 5:
                continue

            print(f"   📅 Generando datos para: {fecha_iteracion}...")

            for empleado in empleados:
                # 90% de probabilidad de que el empleado haya ido a trabajar ese día
                if random.random() > 0.1:

                    # Hora de entrada aleatoria (entre 07:50 y 09:30)
                    hora_entrada = datetime.combine(fecha_iteracion, time(random.randint(7, 9), random.randint(0, 59)))

                    # Hora de salida aleatoria (entre 16:00 y 19:00)
                    hora_salida = datetime.combine(fecha_iteracion, time(random.randint(16, 19), random.randint(0, 59)))

                    # CASO ESPECIAL: Si es HOY, quizás alguno aún no ha salido (fichaje abierto)
                    if i == 0 and random.random() > 0.7:
                        hora_salida = None # Aún trabajando

                    nuevo_registro = Registro(
                        fecha=fecha_iteracion,
                        hora_entrada=hora_entrada,
                        hora_salida=hora_salida,
                        id_trabajador=empleado.id_trabajador
                    )
                    db.session.add(nuevo_registro)
                    registros_creados += 1

        # 4. Generar Incidencias Aleatorias
        incidencias_creadas = 0
        tipos_incidencias = [
            "Olvidé fichar a la salida",
            "Llegué tarde por tráfico",
            "Cita médica a primera hora",
            "No funcionaba la App",
            "Trabajo remoto hoy"
        ]

        for _ in range(5): # Crear 5 incidencias al azar
            empleado_random = random.choice(empleados)
            fecha_random = datetime.now() - timedelta(days=random.randint(0, 10))

            nueva_incidencia = Incidencia(
                fecha_hora=fecha_random,
                descripcion=random.choice(tipos_incidencias),
                id_trabajador=empleado_random.id_trabajador
            )
            db.session.add(nueva_incidencia)
            incidencias_creadas += 1

        # Guardar todo
        db.session.commit()

        print("\n✅ ¡PROCESO FINALIZADO!")
        print(f"   - Registros de presencia creados: {registros_creados}")
        print(f"   - Incidencias creadas: {incidencias_creadas}")

if __name__ == '__main__':
    generar_datos()