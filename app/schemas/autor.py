from datetime import date

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class AutorBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    nacionalidad: str | None = Field(default=None, max_length=60)
    anio_nacimiento: int | None = Field(default=None, ge=1000)

    @field_validator("nombre")
    @classmethod
    def format_nombre(cls, value: str) -> str:
        value = value.strip().title()
        if not 2 <= len(value) <= 100:
            raise ValueError("El nombre debe tener entre 2 y 100 caracteres")
        return value

    @field_validator("nacionalidad")
    @classmethod
    def trim_nacionalidad(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @field_validator("anio_nacimiento")
    @classmethod
    def valid_anio(cls, value: int | None) -> int | None:
        if value is not None and value > date.today().year:
            raise ValueError("El año de nacimiento no puede ser futuro")
        return value

class AutorCreate(AutorBase):
    pass


class AutorPatch(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    nacionalidad: str | None = Field(default=None, max_length=60)
    anio_nacimiento: int | None = Field(default=None, ge=1000)

    @field_validator("nombre")
    @classmethod
    def format_nombre(cls, value: str | None) -> str | None:
        return value.strip().title() if value is not None else None

    @field_validator("nacionalidad")
    @classmethod
    def trim_nacionalidad(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @field_validator("anio_nacimiento")
    @classmethod
    def valid_anio(cls, value: int | None) -> int | None:
        if value is not None and value > date.today().year:
            raise ValueError("El año de nacimiento no puede ser futuro")
        return value

    @model_validator(mode="after")
    def valid_patch_name(self) -> "AutorPatch":
        if "nombre" in self.model_fields_set and self.nombre is None:
            raise ValueError("nombre no puede ser null")
        if self.nombre is not None and not 2 <= len(self.nombre) <= 100:
            raise ValueError("El nombre debe tener entre 2 y 100 caracteres")
        return self


class AutorRead(AutorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
