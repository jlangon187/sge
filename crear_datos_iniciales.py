from app import app
from extensions import db
from models import Rol, Dia, Empresa, Horario, Trabajador

def cargar_datos():
    with app.app_context():

        # 1. Crear Roles (Incluyendo Superadministrador)
        roles = ['Administrador', 'Trabajador', 'RRHH', 'Superadministrador']
        for nombre in roles:
            rol_existente = Rol.query.filter_by(nombre_rol=nombre).first()
            if not rol_existente:
                nuevo_rol = Rol(nombre_rol=nombre)
                db.session.add(nuevo_rol)
                print(f"Rol creado: {nombre}")

        # 2. Crear Días de la semana
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        for nombre in dias:
            dia_existente = Dia.query.filter_by(nombre=nombre).first()
            if not dia_existente:
                nuevo_dia = Dia(nombre=nombre)
                db.session.add(nuevo_dia)
                print(f"Día creado: {nombre}")

        # Guardamos roles y días para poder usarlos abajo
        db.session.commit()

        # 3. Crear Empresa por defecto
        empresa = Empresa.query.first()
        if not empresa:
            empresa = Empresa(nombrecomercial="Empresa SGE", cif="A12345678")
            db.session.add(empresa)
            print("Empresa creada")

        # 4. Crear un Horario por defecto
        horario = Horario.query.first()
        if not horario:
            horario = Horario(nombre_horario="Horario General", descripcion="L-V 8:00-15:00")
            db.session.add(horario)
            print("Horario base creado")

        db.session.commit()

        empresa_obj = Empresa.query.first()
        horario_obj = Horario.query.first()

        # 5. Crear Usuario Administrador
        admin = Trabajador.query.filter_by(email="admin@sge.com").first()
        if not admin:
            rol_admin = Rol.query.filter_by(nombre_rol='Administrador').first()

            nuevo_admin = Trabajador(
                nif="00000000T",
                nombre="Super",
                apellidos="Administrador",
                passw="1234",
                email="admin@sge.com",
                telef="600000000",
                idEmpresa=empresa_obj.id_empresa,
                idRol=rol_admin.id_rol,
                idHorario=horario_obj.id_horario
            )
            db.session.add(nuevo_admin)
            print("Usuario Administrador creado")

        # 6. Crear Usuario SUPERADMINISTRADOR
        super_admin = Trabajador.query.filter_by(email="super@sge.com").first()
        if not super_admin:
            rol_super = Rol.query.filter_by(nombre_rol='Superadministrador').first()

            nuevo_super = Trabajador(
                nif="99999999S",
                nombre="Jefe",
                apellidos="Supremo",
                passw="root",
                email="super@sge.com",
                telef="600000000",
                idEmpresa=empresa_obj.id_empresa,
                idRol=rol_super.id_rol,
                idHorario=horario_obj.id_horario
            )
            db.session.add(nuevo_super)
            print("Usuario Superadministrador creado")

        # Confirmar todos los cambios
        db.session.commit()
        print("¡Datos iniciales cargados correctamente!")

if __name__ == '__main__':
    cargar_datos()