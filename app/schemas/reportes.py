from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class LibroMasPrestadoRead(BaseModel):
    libro: str
    autor: str
    total_prestamos: int


class CategoriaReporteRead(BaseModel):
    nombre: str
    total_libros: int


class PrestamoVencidoRead(BaseModel):
    prestamo_id: int
    titulo: str
    socio: str
    email: str
    fecha_limite: date
    dias_retraso: int


class SocioMultasRead(BaseModel):
    socio: str
    total_multas: Decimal
    prestamos_con_multa: int


class AutorReporteRead(BaseModel):
    autor: str
    total_libros: int
    total_ejemplares: int
    total_prestamos: int


class ResumenRead(BaseModel):
    total_libros: int
    total_ejemplares: int
    prestados: int
    socios_activos: int
    vencidos: int
    multas: Decimal
