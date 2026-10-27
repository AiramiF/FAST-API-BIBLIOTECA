from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..core.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from ..models.autor import Autor
from ..models.categoria import Categoria
from ..models.libro import Libro
from ..models.prestamo import Prestamo
from ..schemas.libro import LibroCreate, LibroPatch, LibroRead


def _disponibles(db: Session, libro: Libro) -> int:
    prestados = db.scalar(
        select(func.count(Prestamo.id)).where(
            Prestamo.libro_id == libro.id,
            Prestamo.fecha_devolucion.is_(None),
        )
    )
    return libro.ejemplares - (prestados or 0)


def _respuesta(db: Session, libro: Libro) -> LibroRead:
    return LibroRead(
        id=libro.id,
        titulo=libro.titulo,
        isbn=libro.isbn,
        anio_publicacion=libro.anio_publicacion,
        ejemplares=libro.ejemplares,
        disponibles=_disponibles(db, libro),
        autor=libro.autor,
        categorias=libro.categorias,
    )


def _obtener(db: Session, libro_id: int) -> Libro:
    libro = db.scalar(
        select(Libro)
        .options(selectinload(Libro.autor), selectinload(Libro.categorias))
        .where(Libro.id == libro_id)
    )
    if libro is None:
        raise NoEncontrado("Libro no encontrado")
    return libro


def listar_libros(
    db: Session,
    skip: int,
    limit: int,
    buscar: str | None = None,
    autor: str | None = None,
    categoria_id: int | None = None,
    desde: int | None = None,
    hasta: int | None = None,
    orden: str = "titulo",
) -> list[LibroRead]:
    statement = select(Libro).options(
        selectinload(Libro.autor), selectinload(Libro.categorias)
    )
    if buscar:
        statement = statement.where(Libro.titulo.ilike(f"%{buscar}%"))
    if autor:
        statement = statement.join(Libro.autor).where(
            Autor.nombre.ilike(f"%{autor}%")
        )
    if categoria_id is not None:
        statement = statement.join(Libro.categorias).where(
            Categoria.id == categoria_id
        )
    if desde is not None:
        statement = statement.where(Libro.anio_publicacion >= desde)
    if hasta is not None:
        statement = statement.where(Libro.anio_publicacion <= hasta)
    if orden == "anio":
        statement = statement.order_by(Libro.anio_publicacion, Libro.id)
    elif orden == "-anio":
        statement = statement.order_by(Libro.anio_publicacion.desc(), Libro.id)
    else:
        statement = statement.order_by(Libro.titulo, Libro.id)
    libros = db.scalars(statement.distinct().offset(skip).limit(limit)).all()
    return [_respuesta(db, libro) for libro in libros]


def obtener_libro(db: Session, libro_id: int) -> LibroRead:
    return _respuesta(db, _obtener(db, libro_id))


def listar_libros_autor(
    db: Session, autor_id: int, skip: int, limit: int
) -> list[LibroRead]:
    if db.get(Autor, autor_id) is None:
        raise NoEncontrado("Autor no encontrado")
    statement = (
        select(Libro)
        .options(selectinload(Libro.autor), selectinload(Libro.categorias))
        .where(Libro.autor_id == autor_id)
        .order_by(Libro.id)
        .offset(skip)
        .limit(limit)
    )
    return [_respuesta(db, libro) for libro in db.scalars(statement).all()]


def crear_libro(db: Session, datos: LibroCreate) -> LibroRead:
    if db.get(Autor, datos.autor_id) is None:
        raise NoEncontrado("Autor no encontrado")
    categorias = list(
        db.scalars(
            select(Categoria).where(Categoria.id.in_(datos.categoria_ids))
        ).all()
    )
    if len(categorias) != len(datos.categoria_ids):
        raise NoEncontrado("Categoría no encontrada")
    if db.scalar(select(Libro.id).where(Libro.isbn == datos.isbn)) is not None:
        raise Conflicto("El ISBN ya existe")
    campos = datos.model_dump(exclude={"categoria_ids"})
    libro = Libro(**campos, categorias=categorias)
    db.add(libro)
    db.commit()
    return _respuesta(db, _obtener(db, libro.id))


def actualizar_libro(db: Session, libro_id: int, datos: LibroPatch) -> LibroRead:
    libro = _obtener(db, libro_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "autor_id" in cambios and db.get(Autor, cambios["autor_id"]) is None:
        raise NoEncontrado("Autor no encontrado")
    if "isbn" in cambios and db.scalar(
        select(Libro.id).where(Libro.isbn == cambios["isbn"], Libro.id != libro_id)
    ) is not None:
        raise Conflicto("El ISBN ya existe")
    categorias = None
    if "categoria_ids" in cambios:
        categoria_ids = cambios.pop("categoria_ids")
        categorias = list(
            db.scalars(select(Categoria).where(Categoria.id.in_(categoria_ids))).all()
        )
        if len(categorias) != len(categoria_ids):
            raise NoEncontrado("Categoría no encontrada")
    ejemplares = cambios.get("ejemplares", libro.ejemplares)
    prestamos_activos = db.scalar(
        select(func.count(Prestamo.id)).where(
            Prestamo.libro_id == libro_id,
            Prestamo.fecha_devolucion.is_(None),
        )
    )
    if ejemplares < (prestamos_activos or 0):
        raise ReglaNegocio("Los ejemplares no pueden ser menores que los préstamos activos")
    for campo, valor in cambios.items():
        setattr(libro, campo, valor)
    if categorias is not None:
        libro.categorias = categorias
    db.commit()
    return _respuesta(db, _obtener(db, libro_id))


def eliminar_libro(db: Session, libro_id: int) -> None:
    libro = _obtener(db, libro_id)
    activos = db.scalar(
        select(func.count(Prestamo.id)).where(
            Prestamo.libro_id == libro_id,
            Prestamo.fecha_devolucion.is_(None),
        )
    )
    if activos:
        raise Conflicto("No se puede eliminar un libro con préstamos sin devolver")
    db.delete(libro)
    db.commit()
