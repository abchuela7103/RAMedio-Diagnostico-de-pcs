import joblib
import json
import os
import pandas as pd
import numpy as np
from sklearn.tree import _tree

# ── Rutas ────────────────────────────────────────────────────────────────────
_BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH   = os.path.join(_BASE_DIR, "modelo_decision_tree.pkl")
METRICS_PATH = os.path.join(_BASE_DIR, "model_metrics.json")

# ── Caché en memoria ──────────────────────────────────────────────────────────
_model_cache = None


def get_model():
    global _model_cache
    if _model_cache is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"El modelo no existe en {MODEL_PATH}. "
                "Ejecuta ML/train_advanced_model.py primero."
            )
        _model_cache = joblib.load(MODEL_PATH)
    return _model_cache


def _build_input(hardware_metrics: dict, symptoms_data: dict) -> pd.DataFrame:
    """Construye el DataFrame de entrada con el orden exacto de columnas del modelo."""
    model = get_model()
    row = {
        "cpu":          hardware_metrics.get("cpu",         0.0) or 0.0,
        "ram":          hardware_metrics.get("ram",         0.0) or 0.0,
        "disk":         hardware_metrics.get("disk",        0.0) or 0.0,
        "disk_active":  hardware_metrics.get("disk_active", 0.0) or 0.0,
        "gpu":          hardware_metrics.get("gpu",         0.0) or 0.0,

        "is_slow":         1 if symptoms_data.get("is_slow")         else 0,
        "random_restarts": 1 if symptoms_data.get("random_restarts") else 0,
        "weird_noises":    1 if symptoms_data.get("weird_noises")    else 0,
        "overheating":     1 if symptoms_data.get("overheating")     else 0,
        "bsod_errors":     1 if symptoms_data.get("bsod_errors")     else 0,
        "screen_flicker":  1 if symptoms_data.get("screen_flicker")  else 0,
        "apps_crashing":   1 if symptoms_data.get("apps_crashing")   else 0,
        "battery_issue":   1 if symptoms_data.get("battery_issue")   else 0,
        "burnt_smell":     1 if symptoms_data.get("burnt_smell")     else 0,
        "visual_artifacts":1 if symptoms_data.get("visual_artifacts")else 0,
        "system_freezes":  1 if symptoms_data.get("system_freezes")  else 0,
        "usb_disconnects": 1 if symptoms_data.get("usb_disconnects") else 0,
        "network_drops":   1 if symptoms_data.get("network_drops")   else 0,
        "slow_boot":       1 if symptoms_data.get("slow_boot")       else 0,
        "file_corruption": 1 if symptoms_data.get("file_corruption") else 0,
    }
    df = pd.DataFrame([row])
    # Respetar el orden de features con el que se entrenó el modelo
    return df[model.feature_names_in_]


def predict_status(hardware_metrics: dict, symptoms_data: dict) -> str:
    """Retorna únicamente la etiqueta del diagnóstico predicho."""
    try:
        model = get_model()
    except FileNotFoundError as e:
        return f"Error: {e}"
    return model.predict(_build_input(hardware_metrics, symptoms_data))[0]


def predict_status_with_proba(hardware_metrics: dict, symptoms_data: dict) -> dict:
    """Retorna predicción, probabilidades por clase y camino del árbol de decisión."""
    try:
        model = get_model()
    except FileNotFoundError as e:
        return {"prediction": f"Error: {e}", "probabilities": {}, "decision_path": []}

    X = _build_input(hardware_metrics, symptoms_data)

    prediction    = model.predict(X)[0]
    probas        = model.predict_proba(X)[0]
    node_indicator = model.decision_path(X)
    decision_path = [int(idx) for idx in node_indicator.indices]

    prob_dict = {
        cls: round(prob * 100, 2)
        for cls, prob in zip(model.classes_, probas)
        if prob > 0
    }

    return {
        "prediction":    prediction,
        "probabilities": prob_dict,
        "decision_path": decision_path,
    }


def get_tree_structure() -> dict:
    """
    Convierte el árbol de decisión a un formato JSON jerárquico compatible con ECharts.
    Los nombres de features se muestran en español.
    """
    model = get_model()
    tree_ = model.tree_

    # Orden idéntico al de model.feature_names_in_
    feature_names_es = {
        "is_slow":          "Lentitud General",
        "random_restarts":  "Reinicios Aleatorios",
        "weird_noises":     "Ruidos Extraños",
        "overheating":      "Sobrecalentamiento",
        "bsod_errors":      "Pantallazos Azules",
        "screen_flicker":   "Parpadeo de Pantalla",
        "apps_crashing":    "Apps se Cierran",
        "battery_issue":    "Falla de Batería",
        "burnt_smell":      "Olor a Quemado",
        "visual_artifacts": "Artefactos Visuales",
        "system_freezes":   "Congelamientos",
        "usb_disconnects":  "USB Inestable",
        "network_drops":    "Caídas de Red",
        "slow_boot":        "Arranque Lento",
        "file_corruption":  "Corrupción de Archivos",
        "cpu":              "CPU (%)",
        "ram":              "RAM (%)",
        "disk":             "Uso de Disco (%)",
        "disk_active":      "Disco Activo (%)",
        "gpu":              "GPU (%)",
    }

    feature_list = list(model.feature_names_in_)
    class_names  = model.classes_

    def recurse(node: int) -> dict:
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            feat_key  = feature_list[tree_.feature[node]]
            feat_name = feature_names_es.get(feat_key, feat_key)
            threshold = tree_.threshold[node]
            return {
                "name":     f"{feat_name} ≤ {threshold:.1f}",
                "node_id":  int(node),
                "children": [
                    recurse(tree_.children_left[node]),
                    recurse(tree_.children_right[node]),
                ],
            }
        else:
            value    = tree_.value[node][0]
            class_id = int(np.argmax(value))
            return {
                "name":    f"→ {class_names[class_id]}",
                "value":   int(value[class_id]),
                "node_id": int(node),
            }

    return recurse(0)


def get_model_accuracy() -> float | None:
    """
    Retorna la precisión REAL del modelo medida en datos de prueba (no vistos durante
    el entrenamiento). Lee el valor del archivo model_metrics.json generado al entrenar.
    Devuelve None si el archivo no existe todavía.
    """
    if not os.path.exists(METRICS_PATH):
        return None
    try:
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            metrics = json.load(f)
        return metrics.get("accuracy_test")
    except Exception:
        return None
