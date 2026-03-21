from collector import collect_metrics
from sender import send_metrics
import time
import json
from datetime import datetime, UTC 
import socket
import webbrowser

# Identificador del equipo
device_id = socket.gethostname()

# ¡Magia UX! Abrir el navegador automáticamente al usuario
url_formulario = f"https://ramedio.onrender.com/?device_id={device_id}"
print(f"\n🌐 Abriendo formulario de diagnóstico de forma automática en tu navegador:")
print(f"👉 {url_formulario}\n")
webbrowser.open(url_formulario)

# Archivo donde guardaremos los datos recolectados del agente
LOG_FILE = "metrics_log.jsonl"

while True:
    print("\n[+] Iniciando recoleccion de métricas del equipo...")
    metrics_history = {"cpu": [], "ram": [], "disk": [], "disk_active": [], "gpu": [], "battery_pct": [], "battery_plug": []}
    
    for i in range(10):
        data = collect_metrics()
        
        metrics_history["cpu"].append(data.get("cpu", 0.0) or 0.0)
        metrics_history["ram"].append(data.get("ram", 0.0) or 0.0)
        metrics_history["disk"].append(data.get("disk", 0.0) or 0.0)
        metrics_history["disk_active"].append(data.get("disk_active", 0.0) or 0.0)
        metrics_history["gpu"].append(data.get("gpu", 0.0) or 0.0)
        
        bat = data.get("battery")
        if bat:
            metrics_history["battery_pct"].append(bat.get("percent", 0.0) or 0.0)
            metrics_history["battery_plug"].append(bat.get("power_plugged", False))
            
        print(f"Métrica [{i+1}/10] recolectada...")
        
        # collect_metrics tiene ~0.5s de delay por la lectura de disco. 
        # Dormimos 1.5s = ~2s por iteración * 10 = ~20s en total
        time.sleep(1.5)

    # Calcular el promedio de las listas dividiendo su sumatoria entre 10
    avg_data = {
        "cpu": round(sum(metrics_history["cpu"]) / 10, 2),
        "ram": round(sum(metrics_history["ram"]) / 10, 2),
        "disk": round(sum(metrics_history["disk"]) / 10, 2),
        "disk_active": round(sum(metrics_history["disk_active"]) / 10, 2),
        "gpu": round(sum(metrics_history["gpu"]) / 10, 2),
        "battery": None
    }
    
    if metrics_history["battery_pct"]:
        avg_data["battery"] = {
            "percent": round(sum(metrics_history["battery_pct"]) / len(metrics_history["battery_pct"]), 2),
            "power_plugged": metrics_history["battery_plug"][-1] # El último estado capturado
        }

    payload = {
        "device_id": device_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "metrics": avg_data
    }

    print("\n--- Métricas recolectadas ---")
    print(json.dumps(payload, indent=4))

    # Guardar en archivo (modo append)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")
    
    # Enviar al servidor
    send_metrics(payload)



