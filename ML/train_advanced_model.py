import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
import joblib
import os

def generate_synthetic_data(num_samples=2500):
    data = []
    
    features = [
        "cpu", "ram", "disk", "disk_active", "gpu",
        "is_slow", "random_restarts", "weird_noises", "overheating", "bsod_errors",
        "screen_flicker", "apps_crashing", "battery_issue", "burnt_smell",
        "visual_artifacts", "system_freezes", "usb_disconnects", "network_drops", 
        "slow_boot", "file_corruption"
    ]
    
    for _ in range(num_samples):
        # Base healthy state
        row = {f: 0 for f in features}
        row["cpu"] = np.random.uniform(1, 40)
        row["ram"] = np.random.uniform(20, 60)
        row["disk"] = np.random.uniform(10, 80)
        row["disk_active"] = np.random.uniform(0, 5)
        row["gpu"] = np.random.uniform(0, 15)
        label = "Sistema Saludable"
        
        # Inject scenarios manually based on standard PC failure rates
        scenario = np.random.choice([
            "healthy", "thermal_throttling", "gpu_failure", "hdd_failure", 
            "ram_failure", "psu_mobo_failure", "network_failure", "cpu_bottleneck"
        ], p=[0.4, 0.1, 0.05, 0.1, 0.1, 0.05, 0.1, 0.1])
        
        if scenario == "thermal_throttling":
            row["overheating"] = 1
            row["cpu"] = np.random.uniform(85, 100)
            row["gpu"] = np.random.uniform(85, 100)
            row["is_slow"] = np.random.choice([1, 0])
            label = "Degradación Térmica Severa (Sobrecalentamiento)"
            
        elif scenario == "gpu_failure":
            row["visual_artifacts"] = 1
            row["screen_flicker"] = np.random.choice([1, 0])
            label = "Falla Crítica de GPU (Artefactos de Video)"
            
        elif scenario == "hdd_failure":
            row["file_corruption"] = 1
            row["weird_noises"] = np.random.choice([1, 0])
            row["disk_active"] = 100.0
            row["is_slow"] = 1
            label = "Falla Inminente de Disco (Corrupción/SMART)"
            
        elif scenario == "ram_failure":
            row["system_freezes"] = 1
            row["bsod_errors"] = np.random.choice([1, 0], p=[0.7, 0.3])
            row["apps_crashing"] = 1
            row["ram"] = np.random.uniform(90, 100)
            label = "Defecto en Memoria RAM (Pantallazos Azules)"
            
        elif scenario == "psu_mobo_failure":
            row["usb_disconnects"] = 1
            row["random_restarts"] = 1
            row["burnt_smell"] = np.random.choice([1, 0], p=[0.1, 0.9])
            label = "Fallo Eléctrico (Fuente de Poder / Placa Base)"
            
        elif scenario == "network_failure":
            row["network_drops"] = 1
            label = "Problema del Controlador de Red (Wi-Fi/Ethernet)"
            
        elif scenario == "cpu_bottleneck":
            row["cpu"] = 100.0
            row["is_slow"] = 1
            row["slow_boot"] = np.random.choice([1, 0])
            label = "Cuello de Botella Máximo en CPU"
            
        row["label"] = label
        data.append(row)
        
    return pd.DataFrame(data)

if __name__ == "__main__":
    print("Iniciando Generación de Datos Sintéticos para Múltiples Escenarios...")
    df = generate_synthetic_data()
    
    X = df.drop("label", axis=1)
    y = df["label"]
    
    print("Simulando entorno de entrenamiento con Árboles de Decisión...")
    model = DecisionTreeClassifier(max_depth=12, random_state=42)
    model.fit(X, y)
    
    model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ML", "modelo_decision_tree.pkl")
    joblib.dump(model, model_path)
    
    print(f"ÉXITO: Modelo guardado en: {model_path}")
    print("La Inteligencia Artificial ahora predice 8 diagnósticos especializados a partir de 20 variables de salud.")
