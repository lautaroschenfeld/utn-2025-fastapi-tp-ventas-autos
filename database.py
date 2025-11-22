import os

from dotenv import load_dotenv
from sqlalchemy.engine.url import make_url
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

# Cargar variables de entorno desde .env si existe
load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/autos_db",
)

# Habilitar logging SQL en desarrollo
ENGINE_ECHO = os.getenv("DB_ECHO", "true").lower() == "true"

url = make_url(DATABASE_URL)
engine_kwargs: dict = {"echo": ENGINE_ECHO}
connect_args: dict = {}

# Ajustes especiales para SQLite (útil en pruebas locales)
if url.drivername.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    engine_kwargs["connect_args"] = connect_args
    if not url.database or url.database == ":memory:":
        engine_kwargs["poolclass"] = StaticPool
else:
    if connect_args:
        engine_kwargs["connect_args"] = connect_args

engine = create_engine(DATABASE_URL, **engine_kwargs)


def create_db_and_tables() -> None:
    """Crea las tablas definidas en los modelos."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependencia de sesión con patrón generator."""
    with Session(engine) as session:
        yield session
