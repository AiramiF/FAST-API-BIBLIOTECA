from fastapi import APIRouter, Query

from ..controllers import reportes
from ..core.dependencies import SessionDep
from ..schemas.reportes import (
    AutorReporteRead,
    CategoriaReporteRead,
    LibroMasPrestadoRead,
    PrestamoVencidoRead,
    ResumenRead,
    SocioMultasRead,
)

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/libros-mas-prestados", response_model=list[LibroMasPrestadoRead])
def libros_mas_prestados(
    db: SessionDep, limite: int = Query(default=5, ge=1, le=100)
) -> list[LibroMasPrestadoRead]:
    return reportes.libros_mas_prestados(db, limite)


@router.get("/categorias", response_model=list[CategoriaReporteRead])
def categorias(db: SessionDep) -> list[CategoriaReporteRead]:
    return reportes.categorias(db)


@router.get("/prestamos-vencidos", response_model=list[PrestamoVencidoRead])
def prestamos_vencidos(db: SessionDep) -> list[PrestamoVencidoRead]:
    return reportes.prestamos_vencidos(db)


@router.get("/socios-con-multas", response_model=list[SocioMultasRead])
def socios_con_multas(db: SessionDep) -> list[SocioMultasRead]:
    return reportes.socios_con_multas(db)


@router.get("/autores", response_model=list[AutorReporteRead])
def autores(db: SessionDep) -> list[AutorReporteRead]:
    return reportes.autores(db)


@router.get("/resumen", response_model=ResumenRead)
def resumen(db: SessionDep) -> ResumenRead:
    return reportes.resumen(db)
