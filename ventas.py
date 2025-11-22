from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from database import get_session
from models import VentaCreate, VentaResponse, VentaResponseWithAuto, VentaUpdate
from repository import AutoRepository, VentaRepository

router = APIRouter(prefix="/ventas", tags=["Ventas"])


def get_venta_repository(session: Session = Depends(get_session)) -> VentaRepository:
    return VentaRepository(session)


def get_auto_repository(session: Session = Depends(get_session)) -> AutoRepository:
    return AutoRepository(session)


@router.post(
    "",
    response_model=VentaResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_venta(
    venta: VentaCreate,
    venta_repo: VentaRepository = Depends(get_venta_repository),
    auto_repo: AutoRepository = Depends(get_auto_repository),
):
    auto = auto_repo.get_by_id(venta.auto_id)
    if not auto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El auto especificado no existe",
        )
    return venta_repo.create(venta)


@router.get("", response_model=list[VentaResponse])
def list_ventas(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    nombre_comprador: str | None = Query(None, description="Búsqueda parcial por comprador"),
    auto_id: int | None = Query(None, gt=0, description="Filtrar por auto"),
    precio_min: float | None = Query(None, ge=0),
    precio_max: float | None = Query(None, ge=0),
    fecha_desde: datetime | None = Query(None, description="Fecha desde (ISO 8601)"),
    fecha_hasta: datetime | None = Query(None, description="Fecha hasta (ISO 8601)"),
    repo: VentaRepository = Depends(get_venta_repository),
):
    if precio_min is not None and precio_max is not None and precio_min > precio_max:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="precio_min no puede ser mayor que precio_max",
        )
    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="fecha_desde no puede ser mayor que fecha_hasta",
        )

    return repo.get_all(
        skip=skip,
        limit=limit,
        nombre_comprador=nombre_comprador,
        auto_id=auto_id,
        precio_min=precio_min,
        precio_max=precio_max,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )


@router.get("/{venta_id}", response_model=VentaResponse)
def get_venta(
    venta_id: int,
    repo: VentaRepository = Depends(get_venta_repository),
):
    venta = repo.get_by_id(venta_id)
    if not venta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")
    return venta


@router.put("/{venta_id}", response_model=VentaResponse)
def update_venta(
    venta_id: int,
    venta_data: VentaUpdate,
    venta_repo: VentaRepository = Depends(get_venta_repository),
    auto_repo: AutoRepository = Depends(get_auto_repository),
):
    venta = venta_repo.get_by_id(venta_id)
    if not venta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")

    if venta_data.auto_id:
        auto = auto_repo.get_by_id(venta_data.auto_id)
        if not auto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El auto especificado no existe",
            )

    updated = venta_repo.update(venta_id, venta_data)
    return updated


@router.delete("/{venta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_venta(
    venta_id: int,
    repo: VentaRepository = Depends(get_venta_repository),
):
    deleted = repo.delete(venta_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")
    return None


@router.get("/auto/{auto_id}", response_model=list[VentaResponse])
def get_ventas_by_auto(
    auto_id: int,
    venta_repo: VentaRepository = Depends(get_venta_repository),
    auto_repo: AutoRepository = Depends(get_auto_repository),
):
    auto = auto_repo.get_by_id(auto_id)
    if not auto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auto no encontrado")
    return venta_repo.get_by_auto_id(auto_id)


@router.get("/comprador/{nombre}", response_model=list[VentaResponse])
def get_ventas_by_comprador(
    nombre: str,
    repo: VentaRepository = Depends(get_venta_repository),
):
    return repo.get_by_comprador(nombre)


@router.get("/{venta_id}/with-auto", response_model=VentaResponseWithAuto)
def get_venta_with_auto(
    venta_id: int,
    venta_repo: VentaRepository = Depends(get_venta_repository),
    auto_repo: AutoRepository = Depends(get_auto_repository),
):
    venta = venta_repo.get_by_id(venta_id)
    if not venta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")

    auto = auto_repo.get_by_id(venta.auto_id)
    venta.auto = auto
    return venta
