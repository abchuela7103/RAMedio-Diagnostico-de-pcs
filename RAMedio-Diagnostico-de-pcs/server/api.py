from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import socket
from sqlalchemy.orm import Session
from datetime import datetime
import json

from database import engine, get_db, Base
from models import MetricRecord, SymptomRecord

# Inicializar Base de datos y crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configurar CORS para permitir que el frontend web llame a la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción se debe limitar a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------
# MODELOS PYDANTIC 
# -----------------
class Metrics(BaseModel):
    device_id: str
    timestamp: str
    metrics: dict

class SymptomsData(BaseModel):
    is_slow: bool
    random_restarts: bool
    weird_noises: bool
    overheating: bool
    bsod_errors: bool

class SymptomPayload(BaseModel):
    device_id: str
    timestamp: str
    symptoms: SymptomsData

# -----------------
# ENDPOINTS 
# -----------------

@app.post("/metrics")
def receive_metrics(data: Metrics, db: Session = Depends(get_db)):
    # Parse the inner metrics dictionary
    m = data.metrics
    bat = m.get("battery") or {}
    
    # Create the SQLAlchemy Record
    db_record = MetricRecord(
        device_id=data.device_id,
        # Parse ISO datetime
        timestamp=datetime.fromisoformat(data.timestamp.replace("Z", "+00:00")),
        cpu=m.get("cpu"),
        ram=m.get("ram"),
        disk=m.get("disk"),
        battery_percent=bat.get("percent") if bat else None,
        battery_plugged=bat.get("power_plugged") if bat else None
    )
    db.add(db_record)
    db.commit()
    return {"status": "ok", "message": "Metrics saved to DB"}

@app.post("/api/symptoms")
def receive_symptoms(data: SymptomPayload, db: Session = Depends(get_db)):
    s = data.symptoms
    db_record = SymptomRecord(
        device_id=data.device_id,
        timestamp=datetime.fromisoformat(data.timestamp.replace("Z", "+00:00")),
        is_slow=s.is_slow,
        random_restarts=s.random_restarts,
        weird_noises=s.weird_noises,
        overheating=s.overheating,
        bsod_errors=s.bsod_errors
    )
    db.add(db_record)
    db.commit()
    return {"status": "ok", "message": "Symptoms saved to DB"}

@app.get("/api/diagnostico/{device_id}")
def run_diagnostics(device_id: str, db: Session = Depends(get_db)):
    # 1. Obtener la última métrica de hardware
    latest_metric = db.query(MetricRecord).filter(MetricRecord.device_id == device_id).order_by(MetricRecord.timestamp.desc()).first()
    
    # 2. Obtener el último reporte de síntomas web
    latest_symptoms = db.query(SymptomRecord).filter(SymptomRecord.device_id == device_id).order_by(SymptomRecord.timestamp.desc()).first()
    
    if not latest_metric:
        return {"error": "No hay datos de hardware para este equipo. Corre el agente (main.py) primero."}
        
    if not latest_symptoms:
        return {"error": "No hay datos web para este equipo. Llena el formulario primero."}

    # 3. Formatear para el modelo
    hardware_data = {
        "cpu": latest_metric.cpu,
        "ram": latest_metric.ram,
        "disk": latest_metric.disk
    }
    
    symptoms_data = {
        "is_slow": latest_symptoms.is_slow,
        "random_restarts": latest_symptoms.random_restarts,
        "weird_noises": latest_symptoms.weird_noises,
        "overheating": latest_symptoms.overheating,
        "bsod_errors": latest_symptoms.bsod_errors
    }
    
    # 4. Importar dinámicamente y predecir
    import sys
    import os
    # Agregar carpeta raíz al path para poder importar desde ML
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ML.classifier import predict_status
    
    diagnosis = predict_status(hardware_data, symptoms_data)
    
    return {
        "device_id": device_id,
        "hardware_timestamp": latest_metric.timestamp,
        "symptoms_timestamp": latest_symptoms.timestamp,
        "diagnostico_ml": diagnosis
    }

@app.get("/api/device-id")
def get_device_id():
    """Retorna el nombre del host (Device ID) para autocompletar el formulario"""
    return {"device_id": socket.gethostname()}

