from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Modelo de datos esperado
class Metrics(BaseModel):
    device_id: str
    timestamp: str
    metrics: dict

@app.post("/metrics")
def receive_metrics(data: Metrics):
    print("Datos recibidos:")
    print(data)
    return {"status": "ok"}
