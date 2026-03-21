import joblib
import os
import pandas as pd

# Definir la ruta relativa al modelo asumiendo que el script se corre desde la ruta adecuada
MODEL_PATH = os.path.join(os.path.dirname(__file__), "modelo_decision_tree.pkl")

# Variable global para mantener el modelo en memoria
_model_cache = None

def get_model():
    global _model_cache
    if _model_cache is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"El modelo no existe en {MODEL_PATH}. Corre train_model.py primero.")
        _model_cache = joblib.load(MODEL_PATH)
    return _model_cache

def predict_status(hardware_metrics: dict, symptoms_data: dict) -> str:
    """
    Toma diccionarios de métricas de Hardware y Síntomas, los formatea como
    espera el modelo y retorna el diagnóstico predicho.
    """
    try:
        model = get_model()
    except FileNotFoundError as e:
        return f"Error: {str(e)}"

    # Mapear los datos al mismo formato exacto que se usó en el entrenamiento (orden de columnas importa)
    # Columnas esperadas: [cpu, ram, disk, is_slow, random_restarts, weird_noises, overheating, bsod_errors]
    
    input_data = pd.DataFrame([{
        "cpu": hardware_metrics.get("cpu", 0.0) or 0.0,
        "ram": hardware_metrics.get("ram", 0.0) or 0.0,
        "disk": hardware_metrics.get("disk", 0.0) or 0.0,
        "disk_active": hardware_metrics.get("disk_active", 0.0) or 0.0,
        "gpu": hardware_metrics.get("gpu", 0.0) or 0.0,
        
        "is_slow": 1 if symptoms_data.get("is_slow") else 0,
        "random_restarts": 1 if symptoms_data.get("random_restarts") else 0,
        "weird_noises": 1 if symptoms_data.get("weird_noises") else 0,
        "overheating": 1 if symptoms_data.get("overheating") else 0,
        "bsod_errors": 1 if symptoms_data.get("bsod_errors") else 0,
        "screen_flicker": 1 if symptoms_data.get("screen_flicker") else 0,
        "apps_crashing": 1 if symptoms_data.get("apps_crashing") else 0,
        "battery_issue": 1 if symptoms_data.get("battery_issue") else 0,
        "burnt_smell": 1 if symptoms_data.get("burnt_smell") else 0,
        "visual_artifacts": 1 if symptoms_data.get("visual_artifacts") else 0,
        "system_freezes": 1 if symptoms_data.get("system_freezes") else 0,
        "usb_disconnects": 1 if symptoms_data.get("usb_disconnects") else 0,
        "network_drops": 1 if symptoms_data.get("network_drops") else 0,
        "slow_boot": 1 if symptoms_data.get("slow_boot") else 0,
        "file_corruption": 1 if symptoms_data.get("file_corruption") else 0,
    }])

    # Predecir usando el modelo cargado
    prediction = model.predict(input_data)
    
    # Retornar el primer (y único) elemento de la predicción
    return prediction[0]
