import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import json
import os

# ---------------------------------------------------------------------------
# ETIQUETAS — deben coincidir exactamente con las claves del dict `soluciones`
# en server/api.py y con las clases esperadas del modelo guardado.
# ---------------------------------------------------------------------------
LABELS = {
    "healthy":          "Sistema Saludable",
    "thermal":          "Degradación Térmica Severa (Sobrecalentamiento)",
    "gpu_failure":      "Falla Crítica de GPU (Artefactos de Video)",
    "hdd_failure":      "Falla Inminente de Disco (Corrupción/SMART)",
    "ram_failure":      "Saturación o Defecto en RAM (BSODs frecuentes)",
    "psu_mobo":         "Fallo Eléctrico (Fuente de Poder / Placa Base)",
    "network":          "Problema del Adaptador de Red (Wi-Fi/Ethernet)",
    "cpu_bottleneck":   "Cuello de Botella Máximo en Procesador (CPU)",
    "malware":          "Comportamiento Anómalo (Infección de Malware Pts. Alta)",
}

def generate_data(num_samples: int = 25000) -> pd.DataFrame:
    """
    Genera datos sintéticos mejorados:
    - Clases más balanceadas (~11% c/u).
    - Casos ambiguos con síntomas mezclados.
    - Ruido controlado en síntomas para evitar reglas perfectas y overfitting.
    """
    rng = np.random.default_rng(42)
    data = []

    symptom_keys = [
        "is_slow", "random_restarts", "weird_noises", "overheating", "bsod_errors",
        "screen_flicker", "apps_crashing", "battery_issue", "burnt_smell",
        "visual_artifacts", "system_freezes", "usb_disconnects", "network_drops",
        "slow_boot", "file_corruption",
    ]

    # Probabilidades balanceadas: 20% saludable, ~10% cada falla (8 fallas)
    scenarios = list(LABELS.keys())
    probs     = [0.20, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10]

    for _ in range(num_samples):
        # ── Hardware base (sistema en reposo) ───────────────────────────────
        row = {
            "cpu":         float(np.clip(rng.normal(30, 18), 0, 100)),
            "ram":         float(np.clip(rng.normal(42, 22), 0, 100)),
            "disk":        float(np.clip(rng.normal(22, 12), 0, 100)),
            "disk_active": float(np.clip(rng.exponential(7),  0, 100)),
            "gpu":         float(np.clip(rng.lognormal(1.2, 1), 0, 100)),
        }
        # Síntomas base (ruido: 8% de chance de síntoma espurio en sistema sano)
        for k in symptom_keys:
            row[k] = int(rng.random() < 0.08)

        scenario = rng.choice(scenarios, p=probs)

        # ── Escenarios específicos ────────────────────────────────────────────
        if scenario == "thermal":
            row["overheating"]     = int(rng.random() < 0.88)
            row["cpu"]             = float(np.clip(rng.normal(88, 10), 0, 100))
            row["gpu"]             = float(np.clip(rng.normal(82, 15), 0, 100))
            row["is_slow"]         = int(rng.random() < 0.88)
            row["random_restarts"] = int(rng.random() < 0.38)
            # Casos ambiguos: a veces el equipo se calienta sin que el usuario lo note
            if rng.random() < 0.15:
                row["overheating"] = 0  # Silencioso pero CPU alta

        elif scenario == "gpu_failure":
            row["visual_artifacts"] = int(rng.random() < 0.82)
            row["screen_flicker"]   = int(rng.random() < 0.68)
            row["apps_crashing"]    = int(rng.random() < 0.55)
            # GPU puede estar a 0 (muerta) o a tope
            row["gpu"] = float(np.clip(
                rng.choice([rng.normal(96, 4), rng.normal(2, 3)]), 0, 100
            ))
            # Caso ambiguo: artefactos sin GPU disparada (driver issue)
            if rng.random() < 0.20:
                row["gpu"] = float(np.clip(rng.normal(45, 15), 0, 100))

        elif scenario == "hdd_failure":
            row["file_corruption"] = int(rng.random() < 0.65)
            row["weird_noises"]    = int(rng.random() < 0.72)
            row["disk_active"]     = float(np.clip(rng.normal(93, 7), 0, 100))
            row["slow_boot"]       = int(rng.random() < 0.88)
            row["is_slow"]         = 1
            # Disco puede fallar sin ruidos (SSD)
            if rng.random() < 0.25:
                row["weird_noises"] = 0

        elif scenario == "ram_failure":
            row["system_freezes"] = int(rng.random() < 0.78)
            row["bsod_errors"]    = int(rng.random() < 0.62)
            row["apps_crashing"]  = int(rng.random() < 0.70)
            row["ram"]            = float(np.clip(rng.normal(94, 5), 0, 100))
            row["is_slow"]        = int(rng.random() < 0.72)
            # Caso ambiguo: RAM al límite pero sin BSODs aún
            if rng.random() < 0.20:
                row["bsod_errors"] = 0

        elif scenario == "psu_mobo":
            row["usb_disconnects"] = int(rng.random() < 0.88)
            row["random_restarts"] = int(rng.random() < 0.82)
            row["burnt_smell"]     = int(rng.random() < 0.30)   # No siempre hay olor
            row["screen_flicker"]  = int(rng.random() < 0.35)
            # Caso ambiguo: sólo USB sin reinicios (fuente débil)
            if rng.random() < 0.18:
                row["random_restarts"] = 0

        elif scenario == "network":
            row["network_drops"] = int(rng.random() < 0.93)
            row["is_slow"]       = int(rng.random() < 0.28)
            # Caso ambiguo: lentitud web sin network_drops detectados
            if rng.random() < 0.12:
                row["network_drops"] = 0
                row["is_slow"]       = 1

        elif scenario == "cpu_bottleneck":
            row["cpu"]          = float(np.clip(rng.normal(97, 3), 0, 100))
            row["is_slow"]      = 1
            row["apps_crashing"]= int(rng.random() < 0.32)
            row["slow_boot"]    = int(rng.random() < 0.55)
            # Caso ambiguo: CPU muy alta pero en ráfaga corta
            if rng.random() < 0.15:
                row["cpu"] = float(np.clip(rng.normal(72, 8), 0, 100))

        elif scenario == "malware":
            row["cpu"]          = float(np.clip(rng.normal(84, 12), 0, 100))
            row["disk_active"]  = float(np.clip(rng.normal(65, 22), 0, 100))
            row["network_drops"]= int(rng.random() < 0.42)
            row["is_slow"]      = 1
            row["system_freezes"] = int(rng.random() < 0.32)
            # Caso ambiguo: malware muy sigiloso con CPU moderada
            if rng.random() < 0.22:
                row["cpu"] = float(np.clip(rng.normal(55, 10), 0, 100))

        row["label"] = LABELS[scenario]
        data.append(row)

    return pd.DataFrame(data)


if __name__ == "__main__":
    print("=" * 60)
    print("  RAMedio -- Entrenamiento del Modelo de Diagnostico IA")
    print("=" * 60)

    print(f"\n[1/4] Generando {25000:,} muestras de datos sinteticos...")
    df = generate_data(25000)
    print(f"      Distribucion de clases:")
    for label, count in df["label"].value_counts().items():
        pct = count / len(df) * 100
        print(f"      - {label[:55]:<55} {count:>5} ({pct:.1f}%)")

    feature_cols = [c for c in df.columns if c != "label"]
    X = df[feature_cols]
    y = df["label"]

    print("\n[2/4] Dividiendo dataset (80% entrenamiento / 20% prueba)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"      Train: {len(X_train):,} muestras | Test: {len(X_test):,} muestras")

    print("\n[3/4] Entrenando Arbol de Decision...")
    model = DecisionTreeClassifier(
        max_depth=18,
        min_samples_leaf=6,
        min_samples_split=12,
        random_state=42
    )
    model.fit(X_train, y_train)

    train_acc = accuracy_score(y_train, model.predict(X_train))
    test_acc  = accuracy_score(y_test,  model.predict(X_test))

    print(f"\n      [OK] Precision en entrenamiento : {train_acc * 100:.2f}%")
    print(f"      [OK] Precision en prueba (real) : {test_acc  * 100:.2f}%")
    print(f"      [OK] Profundidad del arbol       : {model.tree_.max_depth}")
    print(f"      [OK] Total de nodos              : {model.tree_.node_count}")

    print("\n      Reporte por clase (datos de prueba):")
    report = classification_report(y_test, model.predict(X_test), zero_division=0)
    for line in report.split("\n"):
        print(f"      {line}")

    print("\n[4/4] Guardando modelo y metricas...")
    base_dir   = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "modelo_decision_tree.pkl")
    metrics_path = os.path.join(base_dir, "model_metrics.json")

    joblib.dump(model, model_path)
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump({
            "accuracy_train": round(train_acc * 100, 2),
            "accuracy_test":  round(test_acc  * 100, 2),
            "n_samples_train": len(X_train),
            "n_samples_test":  len(X_test),
            "tree_depth":      model.tree_.max_depth,
            "n_nodes":         model.tree_.node_count,
        }, f, indent=2, ensure_ascii=False)

    print(f"      [OK] Modelo guardado en   : {model_path}")
    print(f"      [OK] Metricas guardadas en: {metrics_path}")
    print("\n" + "=" * 60)
    print(f"  Listo. Precision real en datos no vistos: {test_acc * 100:.2f}%")
    print("=" * 60)
