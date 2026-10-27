from fastapi import APIRouter, Response, status

from ..controllers import prestamos as prestamos_controller
from ..controllers import socios
from ..core.dependencies import PaginationDep, SessionDep
from ..schemas.prestamo import EstadoPrestamo, PrestamoRead
from ..schemas.socio import SocioCreate, SocioPatch, SocioRead

router = APIRouter(prefix="/socios", tags=["Socios"])


@router.get("", response_model=list[SocioRead])
def listar(
    db: SessionDep,
    paginacion: PaginationDep,
    activo: bool | None = None,
) -> list[SocioRead]:
    skip, limit = paginacion
    return socios.listar_socios(db, skip, limit, activo)


@router.get("/{socio_id}", response_model=SocioRead)
def obtener(socio_id: int, db: SessionDep) -> SocioRead:
    return socios.obtener_socio(db, socio_id)


@router.post("", response_model=SocioRead, status_code=status.HTTP_201_CREATED)
def crear(datos: SocioCreate, db: SessionDep) -> SocioRead:
    return socios.crear_socio(db, datos)


@router.patch("/{socio_id}", response_model=SocioRead)
def actualizar(
    socio_id: int, datos: SocioPatch, db: SessionDep
) -> SocioRead:
    return socios.actualizar_socio(db, socio_id, datos)


@router.delete("/{socio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(socio_id: int, db: SessionDep) -> Response:
    socios.eliminar_socio(db, socio_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{socio_id}/prestamos", response_model=list[PrestamoRead])
def listar_prestamos(
    socio_id: int,
    db: SessionDep,
    paginacion: PaginationDep,
    estado: EstadoPrestamo | None = None,
) -> list[PrestamoRead]:
    skip, limit = paginacion
    return socios.listar_prestamos_socio(db, socio_id, skip, limit, estado)
