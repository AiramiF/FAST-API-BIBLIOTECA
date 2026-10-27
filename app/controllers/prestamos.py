from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..core.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from ..models.libro import Libro
from ..models.prestamo import Prestamo
from ..models.socio import Socio
from ..schemas.prestamo import (
    EstadoPrestamo,
    PrestamoCreate,
    PrestamoRead,
)


def expresion_estado(estado: EstadoPrestamo):
    hoy = date.today()
    if estado == EstadoPrestamo.devuelto:
        return Prestamo.fecha_devolucion.is_not(None)
    if estado == EstadoPrestamo.vencido:
        return (
            Prestamo.fecha_devolucion.is_(None)
            & (Prestamo.fecha_limite < hoy)
        )
    return (
        Prestamo.fecha_devolucion.is_(None)
        & (Prestamo.fecha_limite >= hoy)
    )


def _estado(prestamo: Prestamo) -> EstadoPrestamo:
    if prestamo.fecha_devolucion is not None:
        return EstadoPrestamo.devuelto
    if prestamo.fecha_limite < date.today():
        return EstadoPrestamo.vencido
    return EstadoPrestamo.activo


def _respuesta(prestamo: Prestamo) -> PrestamoRead:
    return PrestamoRead(
        id=prestamo.id,
        libro_id=prestamo.libro_id,
        socio_id=prestamo.socio_id,
        fecha_prestamo=prestamo.fecha_prestamo,
        fecha_limite=prestamo.fecha_limite,
        fecha_devolucion=prestamo.fecha_devolucion,
        multa=prestamo.multa,
        estado=_estado(prestamo),
        libro=prestamo.libro,
        socio=prestamo.socio,
    )


def listar_prestamos(
    db: Session,
    skip: int,
    limit: int,
    estado: EstadoPrestamo | None,
    socio_id: int | None,
    libro_id: int | None,
) -> list[PrestamoRead]:
    statement = select(Prestamo).options(
        selectinload(Prestamo.libro), selectinload(Prestamo.socio)
    )
    if estado is not None:
        statement = statement.where(expresion_estado(estado))
    if socio_id is not None:
        statement = statement.where(Prestamo.socio_id == socio_id)
    if libro_id is not None:
        statement = statement.where(Prestamo.libro_id == libro_id)
    prestamos = db.scalars(
        statement.order_by(Prestamo.id).offset(skip).limit(limit)
    ).all()
    return [_respuesta(prestamo) for prestamo in prestamos]


def obtener_prestamo(db: Session, prestamo_id: int) -> PrestamoRead:
    prestamo = db.scalar(
        select(Prestamo)
        .options(selectinload(Prestamo.libro), selectinload(Prestamo.socio))
        .where(Prestamo.id == prestamo_id)
    )
    if prestamo is None:
        raise NoEncontrado("Préstamo no encontrado")
    return _respuesta(prestamo)


def crear_prestamo(db: Session, datos: PrestamoCreate) -> PrestamoRead:
    socio = db.get(Socio, datos.socio_id)
    if socio is None:
        raise NoEncontrado("Socio no encontrado")
    libro = db.get(Libro, datos.libro_id)
    if libro is None:
        raise NoEncontrado("Libro no encontrado")
    if not socio.activo:
        raise ReglaNegocio("El socio no está activo")
    vencidos = db.scalar(
        select(func.count(Prestamo.id)).where(
            Prestamo.socio_id == socio.id,
            expresion_estado(EstadoPrestamo.vencido),
        )
    )
    if vencidos:
        raise ReglaNegocio("El socio tiene préstamos vencidos")
    sin_devolver = db.scalar(
        select(func.count(Prestamo.id)).where(
            Prestamo.socio_id == socio.id,
            Prestamo.fecha_devolucion.is_(None),
        )
    )
    if sin_devolver >= 3:
        raise ReglaNegocio("Máximo de 3 préstamos")
    repetido = db.scalar(
        select(Prestamo.id).where(
            Prestamo.socio_id == socio.id,
            Prestamo.libro_id == libro.id,
            Prestamo.fecha_devolucion.is_(None),
        )
    )
    if repetido is not None:
        raise Conflicto("El socio ya tiene este libro sin devolver")
    prestados = db.scalar(
        select(func.count(Prestamo.id)).where(
            Prestamo.libro_id == libro.id,
            Prestamo.fecha_devolucion.is_(None),
        )
    )
    if libro.ejemplares - (prestados or 0) <= 0:
        raise ReglaNegocio("No hay ejemplares disponibles")
    prestamo = Prestamo(
        libro_id=libro.id,
        socio_id=socio.id,
        fecha_prestamo=datos.fecha_prestamo,
        fecha_limite=datos.fecha_prestamo + timedelta(days=datos.dias),
    )
    db.add(prestamo)
    db.commit()
    db.refresh(prestamo)
    return _respuesta(prestamo)


def devolver_prestamo(db: Session, prestamo_id: int) -> PrestamoRead:
    prestamo = db.scalar(
        select(Prestamo)
        .options(selectinload(Prestamo.libro), selectinload(Prestamo.socio))
        .where(Prestamo.id == prestamo_id)
    )
    if prestamo is None:
        raise NoEncontrado("Préstamo no encontrado")
    if prestamo.fecha_devolucion is not None:
        raise Conflicto("El préstamo ya fue devuelto")
    hoy = date.today()
    if hoy < prestamo.fecha_prestamo:
        raise ReglaNegocio("La fecha de devolución no puede ser anterior al préstamo")
    retraso = (hoy - prestamo.fecha_limite).days
    if retraso > 0:
        prestamo.multa = Decimal(retraso) * Decimal("0.50")
    prestamo.fecha_devolucion = hoy
    db.commit()
    return _respuesta(prestamo)
