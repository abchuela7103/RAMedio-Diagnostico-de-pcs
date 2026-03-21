import requests

SERVER_URL = "http://127.0.0.1:8000/metrics"

def send_metrics(payload):
    try:
        response = requests.post(SERVER_URL, json=payload)
        print("Servidor respondio:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("Error enviando datos:", e)
