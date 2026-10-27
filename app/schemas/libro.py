from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class LibroBase(BaseModel):
    titulo: str = Field(min_length=1, max_length=150)
    isbn: str = Field(pattern=r"^\d{13}$")
    anio_publicacion: int = Field(ge=1450)
    ejemplares: int = Field(ge=1, le=50)
    autor_id: int

    @field_validator("titulo")
    @classmethod
    def format_titulo(cls, value: str) -> str:
        value = value.strip().title()
        if not value:
            raise ValueError("El título no puede estar vacío")
        return value

    @field_validator("anio_publicacion")
    @classmethod
    def valid_anio(cls, value: int) -> int:
        if value > date.today().year:
            raise ValueError("El año de publicación no puede ser futuro")
        return value


class LibroCreate(LibroBase):
    categoria_ids: list[int] = Field(min_length=1, max_length=5)

    @field_validator("categoria_ids")
    @classmethod
    def unique_categorias(cls, value: list[int]) -> list[int]:
        if len(set(value)) != len(value):
            raise ValueError("No se permiten categorías repetidas")
        return value


class LibroPatch(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=150)
    isbn: str | None = Field(default=None, pattern=r"^\d{13}$")
    anio_publicacion: int | None = Field(default=None, ge=1450)
    ejemplares: int | None = Field(default=None, ge=1, le=50)
    autor_id: int | None = None
    categoria_ids: list[int] | None = Field(default=None, min_length=1, max_length=5)

    @field_validator("titulo")
    @classmethod
    def format_titulo(cls, value: str | None) -> str | None:
        return value.strip().title() if value is not None else None

    @field_validator("anio_publicacion")
    @classmethod
    def valid_anio(cls, value: int | None) -> int | None:
        if value is not None and value > date.today().year:
            raise ValueError("El año de publicación no puede ser futuro")
        return value

    @field_validator("categoria_ids")
    @classmethod
    def unique_categorias(cls, value: list[int] | None) -> list[int] | None:
        if value is not None and len(set(value)) != len(value):
            raise ValueError("No se permiten categorías repetidas")
        return value

    @model_validator(mode="after")
    def require_non_null_fields(self) -> "LibroPatch":
        for campo in ("titulo", "isbn", "anio_publicacion", "ejemplares", "autor_id"):
            if campo in self.model_fields_set and getattr(self, campo) is None:
                raise ValueError(f"{campo} no puede ser null")
        if "categoria_ids" in self.model_fields_set and self.categoria_ids is None:
            raise ValueError("categoria_ids no puede ser null")
        if self.titulo is not None and not self.titulo.strip():
            raise ValueError("El título no puede estar vacío")
        return self


class AutorLibroRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class CategoriaLibroRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class LibroRead(BaseModel):
    id: int
    titulo: str
    isbn: str
    anio_publicacion: int
    ejemplares: int
    disponibles: int
    autor: AutorLibroRead
    categorias: list[CategoriaLibroRead]


class OrdenLibro(str, Enum):
    titulo = "titulo"
    anio = "anio"
    anio_desc = "-anio"
