from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from database import Base
from datetime import datetime

class MetricRecord(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Métricas Base
    cpu = Column(Float, nullable=True)
    ram = Column(Float, nullable=True)
    disk = Column(Float, nullable=True)
    
    # Mejoras
    battery_percent = Column(Float, nullable=True)
    battery_plugged = Column(Boolean, nullable=True)

class SymptomRecord(Base):
    __tablename__ = "symptoms"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Formulario de Usuario (ML Features)
    is_slow = Column(Boolean, default=False)
    random_restarts = Column(Boolean, default=False)
    weird_noises = Column(Boolean, default=False)
    overheating = Column(Boolean, default=False)
    bsod_errors = Column(Boolean, default=False)
