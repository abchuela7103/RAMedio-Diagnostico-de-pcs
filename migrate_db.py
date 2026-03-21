import os
import sys

# Agregar la ruta del proyecto para poder importar server.database
sys.path.append(os.path.join(os.path.dirname(__file__), "server"))

from database import engine
from sqlalchemy import text

def run_migrations():
    print("Conectando a la base de datos (Supabase/Local)...")
    with engine.connect() as conn:
        print("\n--- Actualizando tabla 'metrics' ---")
        try:
            conn.execute(text("ALTER TABLE metrics ADD COLUMN disk_active FLOAT;"))
            print("✔️ Columna 'disk_active' agregada con éxito.")
        except Exception as e:
            print("⚠️ 'disk_active' ya existe o hubo un error.")

        try:
            conn.execute(text("ALTER TABLE metrics ADD COLUMN gpu FLOAT;"))
            print("✔️ Columna 'gpu' agregada con éxito.")
        except Exception as e:
            print("⚠️ 'gpu' ya existe o hubo un error.")
            
        print("\n--- Actualizando tabla 'symptoms' ---")
        symptoms_cols = [
            "screen_flicker", "apps_crashing", "battery_issue", "burnt_smell",
            "visual_artifacts", "system_freezes", "usb_disconnects", "network_drops",
            "slow_boot", "file_corruption"
        ]
        
        for col in symptoms_cols:
            try:
                conn.execute(text(f"ALTER TABLE symptoms ADD COLUMN {col} BOOLEAN DEFAULT FALSE;"))
                print(f"✔️ Columna '{col}' agregada con éxito.")
            except Exception as e:
                print(f"⚠️ '{col}' ya existe o hubo un error.")
        
        # Confirmar los cambios si se usa Postgres
        try:
            conn.commit()
        except:
            pass

    print("\n✅ ¡Migración de Supabase completada! Tu base de datos ahora soporta todas las nuevas variables.")

if __name__ == "__main__":
    run_migrations()
