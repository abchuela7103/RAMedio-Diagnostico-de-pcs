import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Cargar variables del entorno si existen
load_dotenv()

# Intentar obtener credenciales de Postgres desde el .env
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "")

if DB_USER and DB_PASSWORD and DB_HOST and DB_NAME:
    # Si tenemos credenciales, usamos PostgreSQL
    SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    # Fallback automático a SQLite local para desarrollo rápido
    print("⚠️  Advertencia: No se encontraron credenciales de Postgres completas en .env")
    print("🛠️  Usando base de datos SQLite local (ramedio.db) como fallback.")
    SQLALCHEMY_DATABASE_URL = "sqlite:///./ramedio.db"
    # El argumento 'check_same_thread' solo es necesario para SQLite
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependencia para inyectar la sesión en las rutas de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
