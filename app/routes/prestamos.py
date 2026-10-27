from fastapi import APIRouter, status

from ..controllers import prestamos
from ..core.dependencies import PaginationDep, SessionDep
from ..schemas.prestamo import EstadoPrestamo, PrestamoCreate, PrestamoRead

router = APIRouter(prefix="/prestamos", tags=["Préstamos"])


@router.get("", response_model=list[PrestamoRead])
def listar(
    db: SessionDep,
    paginacion: PaginationDep,
    estado: EstadoPrestamo | None = None,
    socio_id: int | None = None,
    libro_id: int | None = None,
) -> list[PrestamoRead]:
    skip, limit = paginacion
    return prestamos.listar_prestamos(
        db, skip, limit, estado, socio_id, libro_id
    )


@router.get("/{prestamo_id}", response_model=PrestamoRead)
def obtener(prestamo_id: int, db: SessionDep) -> PrestamoRead:
    return prestamos.obtener_prestamo(db, prestamo_id)


@router.post("", response_model=PrestamoRead, status_code=status.HTTP_201_CREATED)
def crear(datos: PrestamoCreate, db: SessionDep) -> PrestamoRead:
    return prestamos.crear_prestamo(db, datos)


@router.post("/{prestamo_id}/devolucion", response_model=PrestamoRead)
def devolver(prestamo_id: int, db: SessionDep) -> PrestamoRead:
    return prestamos.devolver_prestamo(db, prestamo_id)
