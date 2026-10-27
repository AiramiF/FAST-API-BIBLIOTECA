from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from ..models.autor import Autor
from ..models.categoria import Categoria, libro_categoria
from ..models.libro import Libro
from ..models.prestamo import Prestamo
from ..models.socio import Socio
from ..schemas.reportes import (
    AutorReporteRead,
    CategoriaReporteRead,
    LibroMasPrestadoRead,
    PrestamoVencidoRead,
    ResumenRead,
    SocioMultasRead,
)


def libros_mas_prestados(db: Session, limite: int) -> list[LibroMasPrestadoRead]:
    statement = (
        select(
            Libro.titulo.label("libro"),
            Autor.nombre.label("autor"),
            func.count(Prestamo.id).label("total_prestamos"),
        )
        .join(Libro.autor)
        .join(Libro.prestamos)
        .group_by(Libro.id, Libro.titulo, Autor.id, Autor.nombre)
        .order_by(func.count(Prestamo.id).desc(), Libro.id)
        .limit(limite)
    )
    return [
        LibroMasPrestadoRead.model_validate(row)
        for row in db.execute(statement).mappings()
    ]


def categorias(db: Session) -> list[CategoriaReporteRead]:
    statement = (
        select(
            Categoria.nombre.label("nombre"),
            func.count(libro_categoria.c.libro_id).label("total_libros"),
        )
        .outerjoin(libro_categoria, Categoria.id == libro_categoria.c.categoria_id)
        .group_by(Categoria.id, Categoria.nombre)
        .order_by(Categoria.nombre)
    )
    return [
        CategoriaReporteRead.model_validate(row)
        for row in db.execute(statement).mappings()
    ]


def prestamos_vencidos(db: Session) -> list[PrestamoVencidoRead]:
    statement = (
        select(
            Prestamo.id.label("prestamo_id"),
            Libro.titulo.label("titulo"),
            Socio.nombre.label("socio"),
            Socio.email.label("email"),
            Prestamo.fecha_limite.label("fecha_limite"),
            (func.current_date() - Prestamo.fecha_limite).label("dias_retraso"),
        )
        .join(Prestamo.libro)
        .join(Prestamo.socio)
        .where(
            Prestamo.fecha_devolucion.is_(None),
            Prestamo.fecha_limite < func.current_date(),
        )
        .order_by(Prestamo.fecha_limite, Prestamo.id)
    )
    return [
        PrestamoVencidoRead.model_validate(row)
        for row in db.execute(statement).mappings()
    ]


def socios_con_multas(db: Session) -> list[SocioMultasRead]:
    statement = (
        select(
            Socio.nombre.label("socio"),
            func.sum(Prestamo.multa).label("total_multas"),
            func.count(Prestamo.id)
            .filter(Prestamo.multa > 0)
            .label("prestamos_con_multa"),
        )
        .join(Socio.prestamos)
        .group_by(Socio.id, Socio.nombre)
        .having(func.sum(Prestamo.multa) > 0)
        .order_by(Socio.nombre)
    )
    return [
        SocioMultasRead.model_validate(row)
        for row in db.execute(statement).mappings()
    ]


def autores(db: Session) -> list[AutorReporteRead]:
    prestamos_por_libro = (
        select(
            Prestamo.libro_id.label("libro_id"),
            func.count(Prestamo.id).label("total_prestamos"),
        )
        .group_by(Prestamo.libro_id)
        .subquery()
    )
    statement = (
        select(
            Autor.nombre.label("autor"),
            func.count(distinct(Libro.id)).label("total_libros"),
            func.coalesce(func.sum(Libro.ejemplares), 0).label("total_ejemplares"),
            func.coalesce(func.sum(prestamos_por_libro.c.total_prestamos), 0).label(
                "total_prestamos"
            ),
        )
        .outerjoin(Autor.libros)
        .outerjoin(prestamos_por_libro, prestamos_por_libro.c.libro_id == Libro.id)
        .group_by(Autor.id, Autor.nombre)
        .order_by(Autor.nombre)
    )
    return [
        AutorReporteRead.model_validate(row)
        for row in db.execute(statement).mappings()
    ]


def resumen(db: Session) -> ResumenRead:
    prestados = select(func.count(Prestamo.id)).where(
        Prestamo.fecha_devolucion.is_(None)
    )
    vencidos = select(func.count(Prestamo.id)).where(
        Prestamo.fecha_devolucion.is_(None),
        Prestamo.fecha_limite < func.current_date(),
    )
    statement = select(
        select(func.count(Libro.id)).scalar_subquery().label("total_libros"),
        select(func.coalesce(func.sum(Libro.ejemplares), 0))
        .scalar_subquery()
        .label("total_ejemplares"),
        prestados.scalar_subquery().label("prestados"),
        select(func.count(Socio.id))
        .where(Socio.activo.is_(True))
        .scalar_subquery()
        .label("socios_activos"),
        vencidos.scalar_subquery().label("vencidos"),
        select(func.coalesce(func.sum(Prestamo.multa), 0))
        .scalar_subquery()
        .label("multas"),
    )
    return ResumenRead.model_validate(db.execute(statement).mappings().one())
