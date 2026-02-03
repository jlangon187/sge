from app import create_app, db
from app.models import TokenBlocklist # Importamos para que SQLAlchemy la reconozca

app = create_app('default')

with app.app_context():
    print("Creando tabla de tokens revocados...")
    db.create_all() # Esto crea solo las tablas que falten
    print("✅ Tabla 'token_blocklist' creada con éxito.")