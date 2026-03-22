import sys
import os
sys.path.insert(0, os.path.abspath('server'))
from database import engine
from sqlalchemy import text

def add_column_if_not_exists(table, column_name, column_type):
    with engine.begin() as conn:
        try:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column_name} {column_type}"))
            print(f"Columna {column_name} agregada a la tabla {table}.")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower() or "sqlite3.operationalerror: near" in str(e).lower():
                print(f"Columna {column_name} ya existe en {table} (o hubo un error leve: {e}).")
            else:
                print(f"Error agregando {column_name} a {table}: {e}")

if __name__ == "__main__":
    print("Iniciando migración de base de datos...")
    
    # Nuevas metricas
    add_column_if_not_exists("metrics", "disk_active", "FLOAT")
    add_column_if_not_exists("metrics", "gpu", "FLOAT")
    add_column_if_not_exists("metrics", "battery_percent", "FLOAT")
    add_column_if_not_exists("metrics", "battery_plugged", "BOOLEAN")

    # Nuevos sintomas
    nuevos_sintomas = [
        "screen_flicker", "apps_crashing", "battery_issue", "burnt_smell",
        "visual_artifacts", "system_freezes", "usb_disconnects", "network_drops",
        "slow_boot", "file_corruption"
    ]
    for sintoma in nuevos_sintomas:
        add_column_if_not_exists("symptoms", sintoma, "BOOLEAN DEFAULT FALSE")
        
    print("Migración completada.")
