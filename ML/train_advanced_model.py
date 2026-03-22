import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
import joblib
import os

def generate_chaotic_synthetic_data(num_samples=15000):
    data = []
    
    features = [
        "cpu", "ram", "disk", "disk_active", "gpu",
        "is_slow", "random_restarts", "weird_noises", "overheating", "bsod_errors",
        "screen_flicker", "apps_crashing", "battery_issue", "burnt_smell",
        "visual_artifacts", "system_freezes", "usb_disconnects", "network_drops", 
        "slow_boot", "file_corruption"
    ]
    
    for _ in range(num_samples):
        # Base state (caótico, mucha varianza normal)
        row = {f: np.random.choice([0, 1], p=[0.9, 0.1]) for f in features[5:]} # Síntomas esporádicos en sistemas sanos
        row["cpu"] = np.random.normal(30, 15)
        row["ram"] = np.random.normal(40, 20)
        row["disk"] = np.random.normal(20, 10)
        row["disk_active"] = np.random.exponential(5)
        row["gpu"] = np.random.lognormal(1, 1)
        
        label = "Sistema Saludable"
        
        scenario = np.random.choice([
            "healthy", "thermal_throttling", "gpu_failure", "hdd_failure", 
            "ram_failure", "psu_mobo_failure", "network_failure", "cpu_bottleneck",
            "malware_infection"
        ], p=[0.3, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05, 0.1, 0.05])
        
        if scenario == "thermal_throttling":
            row["overheating"] = np.random.choice([1, 0], p=[0.85, 0.15]) # A veces falla sin reportarse caliente
            row["cpu"] = np.random.normal(90, 10)
            row["gpu"] = np.random.normal(80, 20)
            row["is_slow"] = np.random.choice([1, 0], p=[0.9, 0.1])
            row["random_restarts"] = np.random.choice([1, 0], p=[0.4, 0.6])
            label = "Degradación Térmica Severa (Sobrecalentamiento)"
            
        elif scenario == "gpu_failure":
            row["visual_artifacts"] = np.random.choice([1, 0], p=[0.8, 0.2])
            row["screen_flicker"] = np.random.choice([1, 0], p=[0.7, 0.3])
            row["gpu"] = np.random.choice([np.random.normal(95, 5), np.random.normal(0, 5)]) # Picosa o muerta
            row["apps_crashing"] = np.random.choice([1, 0], p=[0.6, 0.4])
            label = "Falla Crítica de GPU (Artefactos de Video)"
            
        elif scenario == "hdd_failure":
            row["file_corruption"] = np.random.choice([1, 0], p=[0.6, 0.4])
            row["weird_noises"] = np.random.choice([1, 0], p=[0.75, 0.25])
            row["disk_active"] = np.random.normal(95, 5) # Disco permanentemente escrito
            row["slow_boot"] = np.random.choice([1, 0], p=[0.9, 0.1])
            row["is_slow"] = 1
            label = "Falla Inminente de Disco"
            
        elif scenario == "ram_failure":
            row["system_freezes"] = np.random.choice([1, 0], p=[0.8, 0.2])
            row["bsod_errors"] = np.random.choice([1, 0], p=[0.6, 0.4])
            row["apps_crashing"] = np.random.choice([1, 0], p=[0.7, 0.3])
            row["ram"] = np.random.normal(95, 5) # Out of memory constante
            row["is_slow"] = np.random.choice([1, 0], p=[0.7, 0.3])
            label = "Saturación o Defecto en RAM"
            
        elif scenario == "psu_mobo_failure":
            row["usb_disconnects"] = np.random.choice([1, 0], p=[0.9, 0.1])
            row["random_restarts"] = np.random.choice([1, 0], p=[0.8, 0.2])
            row["burnt_smell"] = np.random.choice([1, 0], p=[0.2, 0.8])
            row["screen_flicker"] = np.random.choice([1, 0], p=[0.3, 0.7])
            label = "Fallo Eléctrico (Fuente de Poder / Placa Base)"
            
        elif scenario == "network_failure":
            row["network_drops"] = np.random.choice([1, 0], p=[0.95, 0.05])
            row["is_slow"] = np.random.choice([1, 0], p=[0.3, 0.7])
            label = "Problema del Adaptador de Red"
            
        elif scenario == "cpu_bottleneck":
            row["cpu"] = np.random.normal(98, 2)
            row["is_slow"] = 1
            row["apps_crashing"] = np.random.choice([1, 0], p=[0.3, 0.7])
            row["slow_boot"] = np.random.choice([1, 0], p=[0.6, 0.4])
            label = "Cuello de Botella Máximo en Procesador"
            
        elif scenario == "malware_infection":
            row["cpu"] = np.random.normal(85, 10)
            row["network_drops"] = np.random.choice([1, 0], p=[0.4, 0.6])
            row["disk_active"] = np.random.normal(60, 20)
            row["is_slow"] = 1
            row["system_freezes"] = np.random.choice([1, 0], p=[0.3, 0.7])
            label = "Comportamiento Anómalo (Infección de Malware)"
            
        # Limitar para evitar valores ilógicos fuera de 0-100 en hardware
        row["cpu"] = np.clip(row["cpu"], 0, 100)
        row["ram"] = np.clip(row["ram"], 0, 100)
        row["disk"] = np.clip(row["disk"], 0, 100)
        row["disk_active"] = np.clip(row["disk_active"], 0, 100)
        row["gpu"] = np.clip(row["gpu"], 0, 100)

        row["label"] = label
        data.append(row)
        
    return pd.DataFrame(data)

if __name__ == "__main__":
    print("Iniciando Generación de Datos Sintéticos...")
    df = generate_chaotic_synthetic_data(15000)
    
    X = df.drop("label", axis=1)
    y = df["label"]
    
    print("Entrenando Árbol de Decisión...")
    # Al aumentar la profundidad máxima y bajar el min_samples, forzamos un árbol ENORME.
    model = DecisionTreeClassifier(max_depth=20, min_samples_leaf=4, min_samples_split=10, random_state=42)
    model.fit(X, y)
    
    # Evaluar complejidad y precisión lograda
    train_acc = model.score(X, y)
    print(f"Precisión del Modelo: {train_acc * 100:.2f}%")
    print(f"Profundidad real alcanzada: {model.tree_.max_depth} niveles lógicos")
    print(f"Total de nodos creados: {model.tree_.node_count}")
    
    # Usar __file__ para ubicar dinámicamente el proyecto 
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelo_decision_tree.pkl")
    joblib.dump(model, model_path)
    
    print(f"ÉXITO: Modelo Guardado en {model_path}")
