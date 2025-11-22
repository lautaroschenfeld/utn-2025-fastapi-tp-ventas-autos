from datetime import datetime
from typing import List, Optional

from sqlmodel import Session, select

from models import (
    Auto,
    AutoCreate,
    AutoUpdate,
    Venta,
    VentaCreate,
    VentaUpdate,
)


class AutoRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, auto: AutoCreate) -> Auto:
        db_auto = Auto(**auto.model_dump(by_alias=False))
        self.session.add(db_auto)
        self.session.commit()
        self.session.refresh(db_auto)
        return db_auto

    def get_by_id(self, auto_id: int) -> Optional[Auto]:
        return self.session.get(Auto, auto_id)

    def get_all(
        self,
        skip: int = 0,
        limit: int = 10,
        marca: Optional[str] = None,
        modelo: Optional[str] = None,
    ) -> List[Auto]:
        statement = select(Auto)

        if marca:
            statement = statement.where(Auto.marca.ilike(f"%{marca}%"))
        if modelo:
            statement = statement.where(Auto.modelo.ilike(f"%{modelo}%"))

        results = self.session.exec(
            statement.order_by(Auto.id).offset(skip).limit(limit)
        )
        return results.all()

    def update(self, auto_id: int, auto_update: AutoUpdate) -> Optional[Auto]:
        db_auto = self.get_by_id(auto_id)
        if not db_auto:
            return None

        update_data = auto_update.model_dump(exclude_unset=True, by_alias=False)
        for field, value in update_data.items():
            setattr(db_auto, field, value)

        self.session.add(db_auto)
        self.session.commit()
        self.session.refresh(db_auto)
        return db_auto

    def delete(self, auto_id: int) -> bool:
        db_auto = self.get_by_id(auto_id)
        if not db_auto:
            return False
        self.session.delete(db_auto)
        self.session.commit()
        return True

    def get_by_chasis(self, numero_chasis: str) -> Optional[Auto]:
        statement = select(Auto).where(Auto.numero_chasis == numero_chasis.upper())
        return self.session.exec(statement).one_or_none()


class VentaRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, venta: VentaCreate) -> Venta:
        db_venta = Venta(**venta.model_dump(by_alias=False))
        self.session.add(db_venta)
        self.session.commit()
        self.session.refresh(db_venta)
        return db_venta

    def get_by_id(self, venta_id: int) -> Optional[Venta]:
        return self.session.get(Venta, venta_id)

    def get_all(
        self,
        skip: int = 0,
        limit: int = 10,
        nombre_comprador: Optional[str] = None,
        auto_id: Optional[int] = None,
        precio_min: Optional[float] = None,
        precio_max: Optional[float] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
    ) -> List[Venta]:
        statement = select(Venta)

        if nombre_comprador:
            statement = statement.where(
                Venta.nombre_comprador.ilike(f"%{nombre_comprador}%")
            )
        if auto_id:
            statement = statement.where(Venta.auto_id == auto_id)
        if precio_min is not None:
            statement = statement.where(Venta.precio >= precio_min)
        if precio_max is not None:
            statement = statement.where(Venta.precio <= precio_max)
        if fecha_desde:
            statement = statement.where(Venta.fecha_venta >= fecha_desde)
        if fecha_hasta:
            statement = statement.where(Venta.fecha_venta <= fecha_hasta)

        results = self.session.exec(
            statement.order_by(Venta.fecha_venta.desc(), Venta.id).offset(skip).limit(
                limit
            )
        )
        return results.all()

    def update(self, venta_id: int, venta_update: VentaUpdate) -> Optional[Venta]:
        db_venta = self.get_by_id(venta_id)
        if not db_venta:
            return None

        update_data = venta_update.model_dump(exclude_unset=True, by_alias=False)
        for field, value in update_data.items():
            setattr(db_venta, field, value)

        self.session.add(db_venta)
        self.session.commit()
        self.session.refresh(db_venta)
        return db_venta

    def delete(self, venta_id: int) -> bool:
        db_venta = self.get_by_id(venta_id)
        if not db_venta:
            return False
        self.session.delete(db_venta)
        self.session.commit()
        return True

    def get_by_auto_id(self, auto_id: int) -> List[Venta]:
        statement = select(Venta).where(Venta.auto_id == auto_id)
        return self.session.exec(statement.order_by(Venta.fecha_venta.desc())).all()

    def get_by_comprador(self, nombre: str) -> List[Venta]:
        statement = select(Venta).where(Venta.nombre_comprador.ilike(f"%{nombre}%"))
        return self.session.exec(statement.order_by(Venta.fecha_venta.desc())).all()
