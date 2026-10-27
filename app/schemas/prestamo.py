from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EstadoPrestamo(str, Enum):
    activo = "activo"
    vencido = "vencido"
    devuelto = "devuelto"


class PrestamoCreate(BaseModel):
    libro_id: int
    socio_id: int
    fecha_prestamo: date = Field(default_factory=date.today)
    dias: int = Field(default=14, ge=1, le=30)

    @field_validator("fecha_prestamo")
    @classmethod
    def fecha_no_futura(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("La fecha de préstamo no puede ser futura")
        return value


class LibroPrestamoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str


class SocioPrestamoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str


class PrestamoRead(BaseModel):
    id: int
    libro_id: int
    socio_id: int
    fecha_prestamo: date
    fecha_limite: date
    fecha_devolucion: date | None
    multa: Decimal
    estado: EstadoPrestamo
    libro: LibroPrestamoRead
    socio: SocioPrestamoRead
