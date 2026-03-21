import requests

SERVER_URL = "https://ramedio-diagnostico-de-pcs.onrender.com/metrics"

def send_metrics(payload):
    try:
        response = requests.post(SERVER_URL, json=payload)
        print("Servidor respondio:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("Error enviando datos:", e)
