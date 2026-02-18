import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

# Archivo donde se guardará el modelo entrenado
MODEL_PATH = os.path.join(os.path.dirname(__file__), "modelo_decision_tree.pkl")

def generar_datos_sinteticos(n_samples=1000):
    """
    Genera un dataset ficticio para entrenar el modelo por primera vez.
    """
    np.random.seed(42)
    
    # Métricas Base (Hardware)
    cpu = np.random.uniform(0, 100, n_samples)
    ram = np.random.uniform(0, 100, n_samples)
    disk = np.random.uniform(0, 100, n_samples)
    
    # Síntomas (Formulario Web) - Booleanos convertidos a 1/0
    is_slow = np.random.choice([0, 1], size=n_samples, p=[0.7, 0.3])
    random_restarts = np.random.choice([0, 1], size=n_samples, p=[0.8, 0.2])
    weird_noises = np.random.choice([0, 1], size=n_samples, p=[0.85, 0.15])
    overheating = np.random.choice([0, 1], size=n_samples, p=[0.75, 0.25])
    bsod_errors = np.random.choice([0, 1], size=n_samples, p=[0.9, 0.1])
    
    # Crear el DataFrame
    data = pd.DataFrame({
        "cpu": cpu,
        "ram": ram,
        "disk": disk,
        "is_slow": is_slow,
        "random_restarts": random_restarts,
        "weird_noises": weird_noises,
        "overheating": overheating,
        "bsod_errors": bsod_errors
    })
    
    # Lógica Sintética para etiquetar los diagnósticos (La columna 'Target')
    diagnosis = []
    for i in range(n_samples):
        # Reglas básicas para simular el fallo
        if data.loc[i, "disk"] > 95 or data.loc[i, "weird_noises"] == 1:
            diagnosis.append("Falla inminente de Disco Duro")
        elif data.loc[i, "cpu"] > 85 and data.loc[i, "overheating"] == 1:
            diagnosis.append("Sobrecalentamiento Crítico")
        elif data.loc[i, "ram"] > 90 and data.loc[i, "is_slow"] == 1:
            diagnosis.append("Saturación de Memoria RAM")
        elif data.loc[i, "bsod_errors"] == 1 and data.loc[i, "random_restarts"] == 1:
            diagnosis.append("Fallo Crítico de Sistema (Posible Hardware/OS)")
        else:
            diagnosis.append("Sistema Saludable")
            
    data["diagnosis"] = diagnosis
    return data

def train_and_save_model():
    print("Generando dataset sintético (1000 muestras)...")
    df = generar_datos_sinteticos(1000)
    
    # Separar Características (X) y Objetivo (y)
    X = df.drop("diagnosis", axis=1)
    y = df["diagnosis"]
    
    # Dividir en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Entrenar el Árbol de Decisión
    print("Entrenando Decision Tree Classifier...")
    clf = DecisionTreeClassifier(random_state=42, max_depth=5)
    clf.fit(X_train, y_train)
    
    # Evaluar Precisión
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Precisión del modelo sintético: {acc * 100:.2f}%")
    
    # Guardar el modelo en disco
    joblib.dump(clf, MODEL_PATH)
    print(f"Modelo guardado exitosamente en: {os.path.abspath(MODEL_PATH)}")

if __name__ == "__main__":
    train_and_save_model()
