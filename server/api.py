from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import socket
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
import hashlib
import os
import sys
import traceback

# Precargar el modelo de IA y agregarlo al PATH globalmente
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ML.classifier import predict_status_with_proba, get_tree_structure, get_model_accuracy

from database import engine, get_db, Base
from models import MetricRecord, SymptomRecord, User, UserSession, UserDevice

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
    screen_flicker: bool
    apps_crashing: bool
    battery_issue: bool
    burnt_smell: bool
    visual_artifacts: bool
    system_freezes: bool
    usb_disconnects: bool
    network_drops: bool
    slow_boot: bool
    file_corruption: bool

class SymptomPayload(BaseModel):
    device_id: str
    timestamp: str
    symptoms: SymptomsData

class AuthPayload(BaseModel):
    username: str
    password: str

class LinkPayload(BaseModel):
    device_id: str

# -----------------
# AUTH & DEPENDENCIES
# -----------------

def hash_password(password: str) -> str:
    # Simple hashing (in production use bcrypt or passlib)
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    
    token = authorization.replace("Bearer ", "")
    session = db.query(UserSession).filter(UserSession.token == token).first()
    
    if not session or session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Sesión expirada o inválida")
        
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
    return user

# -----------------
# ENDPOINTS 
# -----------------

@app.post("/api/register")
def register(data: AuthPayload, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
        
    new_user = User(
        username=data.username,
        password_hash=hash_password(data.password)
    )
    db.add(new_user)
    db.commit()
    return {"status": "ok", "message": "Usuario registrado exitosamente"}

@app.post("/api/login")
def login(data: AuthPayload, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or user.password_hash != hash_password(data.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
    # Crear token
    token = os.urandom(32).hex()
    session = UserSession(
        token=token,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.add(session)
    db.commit()
    return {"status": "ok", "token": token, "username": user.username}

@app.post("/api/devices/link")
def link_device(data: LinkPayload, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing_link = db.query(UserDevice).filter(UserDevice.device_id == data.device_id, UserDevice.user_id == current_user.id).first()
    if not existing_link:
        new_link = UserDevice(user_id=current_user.id, device_id=data.device_id)
        db.add(new_link)
        db.commit()
    return {"status": "ok", "message": "Dispositivo vinculado al usuario"}

@app.get("/api/user/devices")
def get_user_devices(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    devices = db.query(UserDevice).filter(UserDevice.user_id == current_user.id).all()
    return {"devices": [d.device_id for d in devices]}

@app.get("/api/user/scans")
def get_user_scans(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    devices = db.query(UserDevice).filter(UserDevice.user_id == current_user.id).all()
    device_ids = [d.device_id for d in devices]
    if not device_ids:
        return {"scans": []}
    
    scans = db.query(SymptomRecord).filter(SymptomRecord.device_id.in_(device_ids)).order_by(SymptomRecord.timestamp.desc()).all()
    
    result = []
    for s in scans:
        latest_metric = db.query(MetricRecord).filter(MetricRecord.device_id == s.device_id, MetricRecord.timestamp <= s.timestamp).order_by(MetricRecord.timestamp.desc()).first()
        if not latest_metric:
            latest_metric = db.query(MetricRecord).filter(MetricRecord.device_id == s.device_id).order_by(MetricRecord.timestamp.asc()).first()
            
        verdict = "Pendiente"
        if latest_metric:
            hardware_data = {
                "cpu": latest_metric.cpu,
                "ram": latest_metric.ram,
                "disk": latest_metric.disk,
                "disk_active": latest_metric.disk_active,
                "gpu": latest_metric.gpu
            }
            symptoms_data = {
                "is_slow": s.is_slow,
                "random_restarts": s.random_restarts,
                "weird_noises": s.weird_noises,
                "overheating": s.overheating,
                "bsod_errors": s.bsod_errors,
                "screen_flicker": s.screen_flicker,
                "apps_crashing": s.apps_crashing,
                "battery_issue": s.battery_issue,
                "burnt_smell": s.burnt_smell,
                "visual_artifacts": s.visual_artifacts,
                "system_freezes": s.system_freezes,
                "usb_disconnects": s.usb_disconnects,
                "network_drops": s.network_drops,
                "slow_boot": s.slow_boot,
                "file_corruption": s.file_corruption
            }
            try:
                diag = predict_status_with_proba(hardware_data, symptoms_data)
                verdict = diag["prediction"]
            except:
                pass
                
        result.append({
            "id": s.id,
            "device_id": s.device_id,
            "timestamp": s.timestamp.isoformat() + "Z",
            "verdict": verdict
        })
    return {"scans": result}

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
        disk_active=m.get("disk_active"),
        gpu=m.get("gpu"),
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
        bsod_errors=s.bsod_errors,
        screen_flicker=s.screen_flicker,
        apps_crashing=s.apps_crashing,
        battery_issue=s.battery_issue,
        burnt_smell=s.burnt_smell,
        visual_artifacts=s.visual_artifacts,
        system_freezes=s.system_freezes,
        usb_disconnects=s.usb_disconnects,
        network_drops=s.network_drops,
        slow_boot=s.slow_boot,
        file_corruption=s.file_corruption
    )
    db.add(db_record)
    db.commit()
    return {"status": "ok", "message": "Symptoms saved to DB"}

@app.get("/api/diagnostico/{device_id}")
def run_diagnostics(device_id: str, symptom_id: int = None, db: Session = Depends(get_db)):
    try:
        if symptom_id is not None:
            latest_symptoms = db.query(SymptomRecord).filter(SymptomRecord.id == symptom_id, SymptomRecord.device_id == device_id).first()
            if not latest_symptoms:
                return {"error": "El escaneo solicitado no fue encontrado."}
            
            latest_metric = db.query(MetricRecord).filter(MetricRecord.device_id == device_id, MetricRecord.timestamp <= latest_symptoms.timestamp).order_by(MetricRecord.timestamp.desc()).first()
            if not latest_metric:
                latest_metric = db.query(MetricRecord).filter(MetricRecord.device_id == device_id).order_by(MetricRecord.timestamp.asc()).first()
        else:
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
            "disk": latest_metric.disk,
            "disk_active": latest_metric.disk_active,
            "gpu": latest_metric.gpu
        }
        
        symptoms_data = {
            "is_slow": latest_symptoms.is_slow,
            "random_restarts": latest_symptoms.random_restarts,
            "weird_noises": latest_symptoms.weird_noises,
            "overheating": latest_symptoms.overheating,
            "bsod_errors": latest_symptoms.bsod_errors,
            "screen_flicker": latest_symptoms.screen_flicker,
            "apps_crashing": latest_symptoms.apps_crashing,
            "battery_issue": latest_symptoms.battery_issue,
            "burnt_smell": latest_symptoms.burnt_smell,
            "visual_artifacts": latest_symptoms.visual_artifacts,
            "system_freezes": latest_symptoms.system_freezes,
            "usb_disconnects": latest_symptoms.usb_disconnects,
            "network_drops": latest_symptoms.network_drops,
            "slow_boot": latest_symptoms.slow_boot,
            "file_corruption": latest_symptoms.file_corruption
        }
        
        # 4. Predecir (el modelo ya está cargado en caché globalmente)
        diagnosis_obj = predict_status_with_proba(hardware_data, symptoms_data)
        prediction_label = diagnosis_obj["prediction"]
        
        # Mapeo de soluciones sugeridas
        soluciones = {
            "Sistema Saludable": "No es necesario realizar ninguna acción preventiva. El equipo funciona óptimamente.",
            "Degradación Térmica Severa (Sobrecalentamiento)": "Solución: Limpiar ventiladores y disipadores, cambiar pasta térmica del procesador/GPU y verificar flujo de aire del gabinete.",
            "Falla Crítica de GPU (Artefactos de Video)": "Solución: Actualizar drivers de video. Si persiste, revisar temperaturas de la tarjeta gráfica o considerar un reemplazo por daño de hardware (VRAM).",
            "Falla Inminente de Disco (Corrupción/SMART)": "Solución URGENTE: Realizar respaldo (backup) inmediato de todos los archivos importantes. Reemplazar la unidad de almacenamiento por una nueva (preferiblemente SSD).",
            "Saturación o Defecto en RAM (BSODs frecuentes)": "Solución: Ejecutar 'Diagnóstico de memoria de Windows' (mdsched). Limpiar los pines de las memorias RAM con goma de borrar. Si falla, reemplazar el módulo de memoria defectuoso.",
            "Fallo Eléctrico (Fuente de Poder / Placa Base)": "Solución: Evitar forzar el encendido. Probar el equipo con otra fuente de poder (PSU) de mayor certificación. Revisar capacitores hinchados en la placa base.",
            "Problema del Adaptador de Red (Wi-Fi/Ethernet)": "Solución: Actualizar o reinstalar drivers de red. Reiniciar el módem/router. Si es físico, usar un adaptador Wi-Fi/Ethernet por USB temporalmente.",
            "Cuello de Botella Máximo en Procesador (CPU)": "Solución: Cerrar procesos en segundo plano innecesarios desde el Administrador de tareas. Escanear por malware minero. Considerar hacer un upgrade de CPU si el uso al 100% es constante.",
            "Comportamiento Anómalo (Infección de Malware Pts. Alta)": "Solución: Desconectar de internet inmediatamente. Realizar un análisis profundo con Windows Defender o un antivirus confiable como Malwarebytes."
        }
        
        return {
            "device_id": device_id,
            "hardware_timestamp": latest_metric.timestamp.isoformat() + "Z",
            "symptoms_timestamp": latest_symptoms.timestamp.isoformat() + "Z",
            "timestamp_hw": latest_metric.timestamp.isoformat() + "Z",
            "timestamp_sym": latest_symptoms.timestamp.isoformat() + "Z",
            "diagnostico_ml": prediction_label,
            "solucion": soluciones.get(prediction_label, "Se requiere revisión técnica detallada."),
            "regla_explicacion": soluciones.get(prediction_label, "Se requiere revisión técnica detallada."),
            "probabilidades": diagnosis_obj["probabilities"],
            "decision_path": diagnosis_obj["decision_path"],
            "hardware": hardware_data,
            "symptoms": symptoms_data
        }
    except Exception as e:
        import traceback
        err_str = traceback.format_exc()
        # Imprimir en consola y retornar en JSON
        print("\n=== CRITICAL ERROR IN DIAGNOSTICS ===")
        print(err_str)
        print("======================================\n")
        return {"error": f"INTERNAL SERVER ERROR:\n{str(e)}"}


@app.get("/api/device-id")
def get_device_id():
    """Retorna un error intencional. En la nube no podemos saber el hostname local del usuario."""
    from fastapi import HTTPException
    raise HTTPException(status_code=501, detail="Manual ID entry required in cloud mode.")

@app.get("/api/dashboard/history/{device_id}")
def get_device_history(device_id: str, db: Session = Depends(get_db)):
    """Obtiene el historial de métricas de hardware de un equipo."""
    records = db.query(MetricRecord).filter(MetricRecord.device_id == device_id).order_by(MetricRecord.timestamp.desc()).limit(20).all()
    records.reverse()
    return {
        "timestamps": [(r.timestamp.isoformat() + "Z") for r in records],
        "cpu": [r.cpu for r in records],
        "ram": [r.ram for r in records],
        "disk": [r.disk or 0 for r in records],
        "disk_active": [r.disk_active or 0 for r in records],
        "gpu": [r.gpu or 0 for r in records]
    }

@app.get("/api/ml/tree")
def get_ml_tree():
    """Obtiene la estructura del árbol de decisión y la precisión para ECharts."""
    return {
        "accuracy": get_model_accuracy(),
        "tree": get_tree_structure()
    }

@app.get("/api/metrics/status/{device_id}")
def check_metrics_status(device_id: str, db: Session = Depends(get_db)):
    """Medida de seguridad para evitar diagnósticos si las métricas no se han enviado por el agente."""
    from datetime import datetime
    latest = db.query(MetricRecord).filter(MetricRecord.device_id == device_id).order_by(MetricRecord.timestamp.desc()).first()
    
    if not latest:
        return {"has_metrics": False, "reason": "No hay métricas registradas en absoluto."}
        
    delta = datetime.utcnow() - latest.timestamp
    if delta.total_seconds() > 3600: # Expiran tras 1 hora max
        return {"has_metrics": False, "reason": "Las métricas están caducadas (más de 1 hora). Vuelve a iniciar el agente."}
        
    return {"has_metrics": True}

# -----------------
# SERVIR FRONTEND WEB
# -----------------
import os
from fastapi.staticfiles import StaticFiles

# Configurar para servir los archivos estáticos del dashboard web en la raíz del dominio
web_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web")
app.mount("/", StaticFiles(directory=web_path, html=True), name="static")
