from app import create_app, db
from app.models import Rol, Trabajador, Dia, Horario, Franjas
from datetime import time

# Inicializamos la app con el contexto
app = create_app('default')

with app.app_context():
    # 1. Borrar todo para empezar de cero y evitar conflictos
    db.drop_all()
    db.create_all()
    print("Base de datos reiniciada.")

    # -----------------------------------------------------------
    # 2. CREAR DÍAS DE LA SEMANA
    # -----------------------------------------------------------
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    objs_dias = []

    for nombre_dia in dias_semana:
        dia = Dia(nombre=nombre_dia)
        objs_dias.append(dia)
        db.session.add(dia)

    db.session.commit()
    print("Días de la semana creados.")

    # -----------------------------------------------------------
    # 3. CREAR ROLES
    # -----------------------------------------------------------
    rol_super = Rol(nombre_rol="Superadministrador")
    rol_admin = Rol(nombre_rol="Administrador")
    rol_trabajador = Rol(nombre_rol="Trabajador")

    db.session.add_all([rol_super, rol_admin, rol_trabajador])
    db.session.commit()
    print("Roles creados.")

    # -----------------------------------------------------------
    # 4. CREAR HORARIO GENERAL
    # -----------------------------------------------------------
    horario_general = Horario(
        nombre_horario="Horario General (Oficina)",
        descripcion="Horario estándar de lunes a viernes de 09:00 a 17:00"
    )
    db.session.add(horario_general)
    db.session.commit()

    for i in range(5):
        franja = Franjas(
            id_horario=horario_general.id_horario,
            id_dia=objs_dias[i].id,
            hora_entrada=time(9, 0),
            hora_salida=time(17, 0)
        )
        db.session.add(franja)

    db.session.commit()
    print("Horario General creado con sus franjas.")

    # -----------------------------------------------------------
    # 5. CREAR SUPERADMIN
    # -----------------------------------------------------------
    admin = Trabajador(
        nif="00000000T",
        nombre="Super",
        apellidos="Admin",
        email="admin@admin.com",
        telef="600000000",
        calle="Calle Base",
        localidad="Madrid",
        provincia="Madrid",
        cp="28000",
        idRol=rol_super.id_rol,
        idHorario=horario_general.id_horario
    )
    # Establecemos contraseña segura
    admin.set_password("admin")

    db.session.add(admin)
    db.session.commit()

    print("\n---------------------------------------------------------")
    print("✔ INSTALACIÓN COMPLETADA CON ÉXITO")
    print("  - Usuario: admin@admin.com")
    print("  - Contraseña: admin")
    print("---------------------------------------------------------")