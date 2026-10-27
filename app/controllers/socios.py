from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.exceptions import Conflicto, NoEncontrado
from ..models.prestamo import Prestamo
from ..models.socio import Socio
from ..schemas.prestamo import EstadoPrestamo, PrestamoRead
from ..schemas.socio import SocioCreate, SocioPatch
from .prestamos import _respuesta, expresion_estado


def listar_socios(
    db: Session, skip: int, limit: int, activo: bool | None = None
) -> list[Socio]:
    statement = select(Socio).order_by(Socio.id).offset(skip).limit(limit)
    if activo is not None:
        statement = statement.where(Socio.activo.is_(activo))
    return list(db.scalars(statement))


def obtener_socio(db: Session, socio_id: int) -> Socio:
    socio = db.get(Socio, socio_id)
    if socio is None:
        raise NoEncontrado("Socio no encontrado")
    return socio


def crear_socio(db: Session, datos: SocioCreate) -> Socio:
    if db.scalar(select(Socio.id).where(Socio.email == datos.email)) is not None:
        raise Conflicto("El email ya existe")
    socio = Socio(**datos.model_dump())
    db.add(socio)
    db.commit()
    db.refresh(socio)
    return socio


def actualizar_socio(db: Session, socio_id: int, datos: SocioPatch) -> Socio:
    socio = obtener_socio(db, socio_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "email" in cambios and db.scalar(
        select(Socio.id).where(
            Socio.email == datos.email, Socio.id != socio_id
        )
    ) is not None:
        raise Conflicto("El email ya existe")
    for campo, valor in cambios.items():
        setattr(socio, campo, valor)
    db.commit()
    db.refresh(socio)
    return socio


def eliminar_socio(db: Session, socio_id: int) -> None:
    socio = obtener_socio(db, socio_id)
    prestamos = db.scalars(
        select(Prestamo).where(Prestamo.socio_id == socio_id)
    ).all()
    if any(prestamo.fecha_devolucion is None for prestamo in prestamos):
        raise Conflicto("No se puede eliminar un socio con préstamos sin devolver")
    if prestamos:
        socio.activo = False
    else:
        db.delete(socio)
    db.commit()


def listar_prestamos_socio(
    db: Session,
    socio_id: int,
    skip: int,
    limit: int,
    estado: EstadoPrestamo | None,
) -> list[PrestamoRead]:
    obtener_socio(db, socio_id)
    statement = select(Prestamo).where(Prestamo.socio_id == socio_id)
    if estado is not None:
        statement = statement.where(expresion_estado(estado))
    prestamos = db.scalars(
        statement.order_by(Prestamo.id).offset(skip).limit(limit)
    ).all()
    return [_respuesta(prestamo) for prestamo in prestamos]
