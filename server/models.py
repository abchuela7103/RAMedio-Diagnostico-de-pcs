from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime)

class UserDevice(Base):
    __tablename__ = "user_devices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(String, index=True)

class MetricRecord(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Métricas Base
    cpu = Column(Float, nullable=True)
    ram = Column(Float, nullable=True)
    disk = Column(Float, nullable=True)
    disk_active = Column(Float, nullable=True)
    gpu = Column(Float, nullable=True)
    
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
    screen_flicker = Column(Boolean, default=False)
    apps_crashing = Column(Boolean, default=False)
    battery_issue = Column(Boolean, default=False)
    burnt_smell = Column(Boolean, default=False)
    visual_artifacts = Column(Boolean, default=False)
    system_freezes = Column(Boolean, default=False)
    usb_disconnects = Column(Boolean, default=False)
    network_drops = Column(Boolean, default=False)
    slow_boot = Column(Boolean, default=False)
    file_corruption = Column(Boolean, default=False)
