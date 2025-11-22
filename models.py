from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import ConfigDict, field_validator
from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

def alias_anio(field_name: str) -> str:
    """Usa 'año' como alias de serialización/entrada para el campo anio."""
    return "año" if field_name == "anio" else field_name


class AutoBase(SQLModel):
    marca: str = Field(min_length=1, max_length=100, description="Marca del vehículo")
    modelo: str = Field(min_length=1, max_length=100, description="Modelo del vehículo")
    anio: int = Field(
        alias="año",
        description="Año de fabricación",
    )
    numero_chasis: str = Field(
        min_length=6,
        max_length=50,
        description="Número de chasis alfanumérico",
    )

    model_config = ConfigDict(populate_by_name=True, alias_generator=alias_anio)

    @field_validator("anio")
    @classmethod
    def validate_anio(cls, value: int) -> int:
        current_year = datetime.utcnow().year
        if value < 1900 or value > current_year:
            raise ValueError("El año debe estar entre 1900 y el año actual")
        return value

    @field_validator("numero_chasis")
    @classmethod
    def validate_chasis(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("El número de chasis no puede estar vacío")
        if not cleaned.isalnum():
            raise ValueError("El número de chasis debe ser alfanumérico")
        return cleaned.upper()


class Auto(AutoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    numero_chasis: str = Field(
        min_length=6,
        max_length=50,
        index=True,
        sa_column_kwargs={"unique": True},
    )
    ventas: list["Venta"] = Relationship(
        back_populates="auto",
        sa_relationship=relationship("Venta", back_populates="auto"),
    )


class AutoCreate(AutoBase):
    pass


class AutoUpdate(SQLModel):
    marca: Optional[str] = Field(default=None, min_length=1, max_length=100)
    modelo: Optional[str] = Field(default=None, min_length=1, max_length=100)
    anio: Optional[int] = Field(
        default=None,
        alias="año",
    )
    numero_chasis: Optional[str] = Field(default=None, min_length=6, max_length=50)

    model_config = ConfigDict(populate_by_name=True, alias_generator=alias_anio)

    @field_validator("anio")
    @classmethod
    def validate_anio_optional(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        return AutoBase.validate_anio(value)

    @field_validator("numero_chasis")
    @classmethod
    def validate_chasis_optional(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return AutoBase.validate_chasis(value)


class VentaBase(SQLModel):
    nombre_comprador: str = Field(
        min_length=1,
        max_length=200,
        description="Nombre completo del comprador",
    )
    precio: float = Field(gt=0, description="Precio de venta")
    auto_id: int = Field(foreign_key="auto.id", description="ID del auto vendido")
    fecha_venta: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha y hora de la venta",
    )

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("nombre_comprador")
    @classmethod
    def validate_nombre(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("El nombre del comprador no puede estar vacío")
        return cleaned

    @field_validator("fecha_venta")
    @classmethod
    def validate_fecha(cls, value: datetime) -> datetime:
        if value > datetime.utcnow():
            raise ValueError("La fecha de venta no puede estar en el futuro")
        return value

    @field_validator("auto_id")
    @classmethod
    def validate_auto_id(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("El ID del auto debe ser un entero positivo")
        return value


class Venta(VentaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    auto: Optional["Auto"] = Relationship(
        back_populates="ventas",
        sa_relationship=relationship("Auto", back_populates="ventas"),
    )


class VentaCreate(VentaBase):
    pass


class VentaUpdate(SQLModel):
    nombre_comprador: Optional[str] = Field(default=None, min_length=1, max_length=200)
    precio: Optional[float] = Field(default=None, gt=0)
    auto_id: Optional[int] = Field(default=None, description="ID del auto vendido")
    fecha_venta: Optional[datetime] = Field(default=None)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("nombre_comprador")
    @classmethod
    def validate_nombre_optional(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return VentaBase.validate_nombre(value)

    @field_validator("fecha_venta")
    @classmethod
    def validate_fecha_optional(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return value
        return VentaBase.validate_fecha(value)

    @field_validator("auto_id")
    @classmethod
    def validate_auto_id_optional(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        return VentaBase.validate_auto_id(value)


class AutoResponse(AutoBase):
    id: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class VentaResponse(VentaBase):
    id: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AutoResponseWithVentas(AutoResponse):
    ventas: List[VentaResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class VentaResponseWithAuto(VentaResponse):
    auto: Optional[AutoResponse] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
