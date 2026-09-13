import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://"
        f"{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración del pool de conexiones: SQLAlchemy crea el engine
    # (y por tanto la conexión/pool) una única vez al iniciar la app y
    # lo reutiliza en todas las peticiones, en lugar de abrir una
    # conexión nueva con pymysql.connect() en cada request.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,   # valida la conexión antes de usarla
        "pool_recycle": 280,     # recicla conexiones antes de que MySQL las cierre
        "pool_size": 5,          # conexiones mantenidas en el pool
        "max_overflow": 10,      # conexiones extra permitidas bajo demanda
    }
