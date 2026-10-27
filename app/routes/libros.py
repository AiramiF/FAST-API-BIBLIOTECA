from fastapi import APIRouter, Query, Response, status

from ..controllers import libros
from ..core.dependencies import PaginationDep, SessionDep
from ..schemas.libro import LibroCreate, LibroPatch, LibroRead, OrdenLibro

router = APIRouter(prefix="/libros", tags=["Libros"])


@router.get("", response_model=list[LibroRead])
def listar(
    db: SessionDep,
    paginacion: PaginationDep,
    buscar: str | None = None,
    autor: str | None = None,
    categoria_id: int | None = Query(default=None, ge=1),
    desde: int | None = Query(default=None, ge=1450),
    hasta: int | None = Query(default=None, ge=1450),
    orden: OrdenLibro = OrdenLibro.titulo,
) -> list[LibroRead]:
    skip, limit = paginacion
    return libros.listar_libros(
        db, skip, limit, buscar, autor, categoria_id, desde, hasta, orden.value
    )


@router.get("/{libro_id}", response_model=LibroRead)
def obtener(libro_id: int, db: SessionDep) -> LibroRead:
    return libros.obtener_libro(db, libro_id)


@router.post("", response_model=LibroRead, status_code=status.HTTP_201_CREATED)
def crear(datos: LibroCreate, db: SessionDep) -> LibroRead:
    return libros.crear_libro(db, datos)


@router.patch("/{libro_id}", response_model=LibroRead)
def actualizar(
    libro_id: int, datos: LibroPatch, db: SessionDep
) -> LibroRead:
    return libros.actualizar_libro(db, libro_id, datos)


@router.delete("/{libro_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(libro_id: int, db: SessionDep) -> Response:
    libros.eliminar_libro(db, libro_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
