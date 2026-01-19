from app import create_app, db
from app.models import Trabajador

app = create_app('default')

with app.app_context():
    # Buscamos al admin
    admin = Trabajador.query.filter_by(email="admin@admin.com").first()

    if admin:
        print("\n--- INFORME DE USUARIO ---")
        print(f"Email: {admin.email}")
        print(f"Contraseña guardada (Hash): {admin.passw}")
        print(f"Longitud del hash: {len(admin.passw)}")

        # Intentamos verificar
        check = admin.check_password("admin")
        print(f"Resultado de check_password('admin'): {check}")
        print("--------------------------\n")

        if not check:
            print("⚠ ERROR: La contraseña no coincide. Posibles causas:")
            if len(admin.passw) < 60:
                print("1. La contraseña parece texto plano (no es un hash). Revisa models.py.")
            elif not admin.passw.startswith("pbkdf2:sha256"):
                print("2. El formato del hash no es pbkdf2:sha256.")
    else:
        print("Error: No se encontró el usuario admin@admin.com")