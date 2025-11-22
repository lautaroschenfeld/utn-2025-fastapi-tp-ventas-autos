from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from autos import router as autos_router
from database import create_db_and_tables
from ventas import router as ventas_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="API Venta de Autos",
    version="1.0.0",
    description="Gestión de inventario y ventas de autos con FastAPI y SQLModel.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(autos_router)
app.include_router(ventas_router)


@app.get("/health", tags=["Health"])
def healthcheck():
    return {"status": "ok"}
