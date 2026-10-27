from fastapi import APIRouter, Response, status

from ..controllers import categorias
from ..core.dependencies import PaginationDep, SessionDep
from ..schemas.categoria import CategoriaCreate, CategoriaPatch, CategoriaRead

router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.get("", response_model=list[CategoriaRead])
def listar(db: SessionDep, paginacion: PaginationDep) -> list[CategoriaRead]:
    skip, limit = paginacion
    return categorias.listar_categorias(db, skip, limit)


@router.post("", response_model=CategoriaRead, status_code=status.HTTP_201_CREATED)
def crear(datos: CategoriaCreate, db: SessionDep) -> CategoriaRead:
    return categorias.crear_categoria(db, datos)


@router.patch("/{categoria_id}", response_model=CategoriaRead)
def actualizar(
    categoria_id: int, datos: CategoriaPatch, db: SessionDep
) -> CategoriaRead:
    return categorias.actualizar_categoria(db, categoria_id, datos)


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(categoria_id: int, db: SessionDep) -> Response:
    categorias.eliminar_categoria(db, categoria_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
