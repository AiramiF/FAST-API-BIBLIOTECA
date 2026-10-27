from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.exceptions import Conflicto, NoEncontrado
from ..models.categoria import Categoria
from ..schemas.categoria import CategoriaCreate, CategoriaPatch


def listar_categorias(db: Session, skip: int, limit: int) -> list[Categoria]:
    statement = select(Categoria).order_by(Categoria.id).offset(skip).limit(limit)
    return list(db.scalars(statement))


def obtener_categoria(db: Session, categoria_id: int) -> Categoria:
    categoria = db.get(Categoria, categoria_id)
    if categoria is None:
        raise NoEncontrado("Categoría no encontrada")
    return categoria


def crear_categoria(db: Session, datos: CategoriaCreate) -> Categoria:
    if db.scalar(
        select(Categoria.id).where(Categoria.nombre == datos.nombre)
    ) is not None:
        raise Conflicto("La categoría ya existe")
    categoria = Categoria(**datos.model_dump())
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


def actualizar_categoria(
    db: Session, categoria_id: int, datos: CategoriaPatch
) -> Categoria:
    categoria = obtener_categoria(db, categoria_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "nombre" in cambios and db.scalar(
        select(Categoria.id).where(
            Categoria.nombre == cambios["nombre"], Categoria.id != categoria_id
        )
    ) is not None:
        raise Conflicto("La categoría ya existe")
    for campo, valor in cambios.items():
        setattr(categoria, campo, valor)
    db.commit()
    db.refresh(categoria)
    return categoria


def eliminar_categoria(db: Session, categoria_id: int) -> None:
    categoria = obtener_categoria(db, categoria_id)
    categoria.libros.clear()
    db.delete(categoria)
    db.commit()
