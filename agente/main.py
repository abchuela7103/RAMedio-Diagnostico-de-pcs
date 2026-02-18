from collector import collect_metrics
from sender import send_metrics
import time
import json
from datetime import datetime, UTC 
import socket

# Identificador del equipo
device_id = socket.gethostname()

# #Archivo donde guardaremos los datos recolectados del agente, esto para poder entrenar el modelo mas adelante
LOG_FILE = "metrics_log.jsonl"

while True:
    data = collect_metrics()

    payload = {
        "device_id": device_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "metrics": data
    }

    print(json.dumps(payload, indent=4))    #Convertimos a string y damos una identacion al texto

   # Guardar en archivo (modo append)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")
    
    # Enviar al servidor
    send_metrics(payload)

    time.sleep(5)




