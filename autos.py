from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from database import get_session
from models import AutoCreate, AutoResponse, AutoResponseWithVentas, AutoUpdate
from repository import AutoRepository, VentaRepository

router = APIRouter(prefix="/autos", tags=["Autos"])


def get_auto_repository(session: Session = Depends(get_session)) -> AutoRepository:
    return AutoRepository(session)


def get_venta_repository(session: Session = Depends(get_session)) -> VentaRepository:
    return VentaRepository(session)


@router.post(
    "",
    response_model=AutoResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_auto(
    auto: AutoCreate,
    repo: AutoRepository = Depends(get_auto_repository),
):
    existing = repo.get_by_chasis(auto.numero_chasis)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un auto con ese número de chasis",
        )
    return repo.create(auto)


@router.get("", response_model=list[AutoResponse])
def list_autos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    marca: str | None = Query(None, description="Búsqueda parcial por marca"),
    modelo: str | None = Query(None, description="Búsqueda parcial por modelo"),
    repo: AutoRepository = Depends(get_auto_repository),
):
    return repo.get_all(skip=skip, limit=limit, marca=marca, modelo=modelo)


@router.get("/{auto_id}", response_model=AutoResponse)
def get_auto(
    auto_id: int,
    repo: AutoRepository = Depends(get_auto_repository),
):
    auto = repo.get_by_id(auto_id)
    if not auto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auto no encontrado")
    return auto


@router.get("/chasis/{numero_chasis}", response_model=AutoResponse)
def get_auto_by_chasis(
    numero_chasis: str,
    repo: AutoRepository = Depends(get_auto_repository),
):
    auto = repo.get_by_chasis(numero_chasis)
    if not auto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auto no encontrado")
    return auto


@router.put("/{auto_id}", response_model=AutoResponse)
def update_auto(
    auto_id: int,
    auto_data: AutoUpdate,
    repo: AutoRepository = Depends(get_auto_repository),
):
    existing = repo.get_by_id(auto_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auto no encontrado")

    # Validar unicidad de número de chasis si viene en la actualización
    if auto_data.numero_chasis:
        other = repo.get_by_chasis(auto_data.numero_chasis)
        if other and other.id != auto_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un auto con ese número de chasis",
            )

    updated = repo.update(auto_id, auto_data)
    return updated


@router.delete("/{auto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_auto(
    auto_id: int,
    repo: AutoRepository = Depends(get_auto_repository),
):
    deleted = repo.delete(auto_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auto no encontrado")
    return None


@router.get("/{auto_id}/with-ventas", response_model=AutoResponseWithVentas)
def get_auto_with_sales(
    auto_id: int,
    auto_repo: AutoRepository = Depends(get_auto_repository),
    venta_repo: VentaRepository = Depends(get_venta_repository),
):
    auto = auto_repo.get_by_id(auto_id)
    if not auto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auto no encontrado")

    ventas = venta_repo.get_by_auto_id(auto_id)
    auto.ventas = ventas
    return auto
