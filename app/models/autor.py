from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


class Autor(Base):
    __tablename__ = "autores"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    nacionalidad: Mapped[str | None] = mapped_column(String(60))
    anio_nacimiento: Mapped[int | None] = mapped_column(Integer)
    libros: Mapped[list["Libro"]] = relationship(back_populates="autor")
