from app import create_app, db
from app.models import Rol, Trabajador

app = create_app('default')

with app.app_context():
    db.drop_all()
    db.create_all()

    # 2. Crear Roles
    rol_super = Rol(nombre_rol="Superadministrador")
    rol_admin = Rol(nombre_rol="Administrador")
    rol_trabajador = Rol(nombre_rol="Trabajador")

    db.session.add_all([rol_super, rol_admin, rol_trabajador])
    db.session.commit()

    print("Roles creados.")

    admin = Trabajador(
        nif="00000000T",
        nombre="Super",
        apellidos="Admin",
        email="admin@admin.com",
        idRol=rol_super.id_rol,
        telef="600000000",
        calle="Calle Base",
        localidad="Madrid",
        provincia="Madrid",
        cp="28000"
    )
    admin.set_password("admin")

    db.session.add(admin)
    db.session.commit()

    print("Superadmin creado: admin@admin.com / admin")