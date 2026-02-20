from app import create_app, db
from sqlalchemy import text

app = create_app('default')

with app.app_context():
    with db.engine.connect() as conn:
        # Añadir columna fcm_token a trabajadores
        try:
            conn.execute(text("ALTER TABLE trabajadores ADD COLUMN fcm_token VARCHAR(255)"))
            print("Columna fcm_token añadida.")
        except:
            print("La columna fcm_token ya existía.")

        # Añadir columna horas_extra a registros
        try:
            conn.execute(text("ALTER TABLE registros ADD COLUMN horas_extra FLOAT DEFAULT 0.0"))
            print("Columna horas_extra añadida.")
        except:
             print("La columna horas_extra ya existía.")

        # Añadir columna titulo a incidencias
        try:
            conn.execute(text("ALTER TABLE incidencias ADD COLUMN titulo VARCHAR(100) DEFAULT 'Incidencia'"))
            print("Columna titulo añadida.")
        except:
             print("La columna titulo ya existía.")

        try:
            conn.execute(text("ALTER TABLE registros ADD COLUMN latitud FLOAT"))
            conn.execute(text("ALTER TABLE registros ADD COLUMN longitud FLOAT"))
            print("Columnas de mapa añadidas.")
        except:
            print("Las columnas de mapa ya existían.")

        conn.commit()