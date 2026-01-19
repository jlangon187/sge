import os
from app import create_app, db
from app.models import Empresa, Trabajador, Rol, Horario, Dia, Franjas # Asegúrate de importar todos los modelos
from flask_migrate import Migrate

app = create_app('default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    # Añade todos los modelos aquí para poder probar en la consola si quieres
    return dict(db=db, Empresa=Empresa, Trabajador=Trabajador, Rol=Rol, Horario=Horario, Dia=Dia, Franjas=Franjas)

if __name__ == '__main__':
    app.run()