from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


class SocioCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=150)
    telefono: str | None = Field(default=None, min_length=7, max_length=15)

    @field_validator("nombre")
    @classmethod
    def format_nombre(cls, value: str) -> str:
        value = value.strip().title()
        if not value:
            raise ValueError("El nombre no puede estar vacío")
        return value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("telefono")
    @classmethod
    def valid_telefono(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()
            if not 7 <= len(value) <= 15 or any(
                character not in "0123456789 +" for character in value
            ):
                raise ValueError("El teléfono debe tener 7-15 dígitos, espacios o +")
        return value


class SocioPatch(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=150)
    telefono: str | None = Field(default=None, min_length=7, max_length=15)
    activo: bool | None = None

    @field_validator("nombre")
    @classmethod
    def format_nombre(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip().title()
            if not value:
                raise ValueError("El nombre no puede estar vacío")
        return value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("telefono")
    @classmethod
    def valid_telefono(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()
            if not 7 <= len(value) <= 15 or any(
                character not in "0123456789 +" for character in value
            ):
                raise ValueError("El teléfono debe tener 7-15 dígitos, espacios o +")
        return value

    @model_validator(mode="after")
    def require_nombre(self) -> "SocioPatch":
        if "nombre" in self.model_fields_set and self.nombre is None:
            raise ValueError("nombre no puede ser null")
        if "email" in self.model_fields_set and self.email is None:
            raise ValueError("email no puede ser null")
        if "activo" in self.model_fields_set and self.activo is None:
            raise ValueError("activo no puede ser null")
        return self


class SocioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: EmailStr
    telefono: str | None
    activo: bool
    fecha_alta: datetime
