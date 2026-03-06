from fastapi import FastAPI
from pydantic import BaseModel
from database import insert_metrics
from database import insert_questionnaire

app = FastAPI()

# Modelo para los valores de métricas
class MetricValues(BaseModel):
    cpu: float
    ram: float
    disk: float

# Modelo del mensaje completo que manda el agente
class Metrics(BaseModel):
    device_id: str
    timestamp: str
    metrics: MetricValues

# Para las respuestas deñ cuestionario 
class Questionnaire(BaseModel):
    device_id: str
    answers: dict


@app.post("/metrics")
def receive_metrics(data: Metrics):

    #solo para saber si se esta corriendo el agente y ver data en consola
    print("Datos recibidos:")
    print(data)

    # guardar métricas en PostgreSQL
    insert_metrics(
        data.device_id,
        data.metrics.cpu,
        data.metrics.ram,
        data.metrics.disk
    )
    return {"status": "saved"}

@app.post("/questionnaire")
def receive_questionnaire(data: Questionnaire):

    #para verificar que recibimos el cuestionario  e imprimir data en consola 
    print("Cuestionario recibido:")
    print(data)

    insert_questionnaire(
        data.device_id,
        data.answers
    )
    return {"status": "questionnaire saved"}

