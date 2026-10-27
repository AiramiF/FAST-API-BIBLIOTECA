from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CategoriaBase(BaseModel):
    nombre: str = Field(min_length=3, max_length=50)
    descripcion: str | None = Field(default=None, max_length=200)

    @field_validator("nombre")
    @classmethod
    def normalize_nombre(cls, value: str) -> str:
        value = value.strip().lower()
        if not 3 <= len(value) <= 50:
            raise ValueError("El nombre debe tener entre 3 y 50 caracteres")
        return value

    @field_validator("descripcion")
    @classmethod
    def trim_descripcion(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaPatch(BaseModel):
    nombre: str | None = Field(default=None, min_length=3, max_length=50)
    descripcion: str | None = Field(default=None, max_length=200)

    @field_validator("nombre")
    @classmethod
    def normalize_nombre(cls, value: str | None) -> str | None:
        return value.strip().lower() if value is not None else None

    @field_validator("descripcion")
    @classmethod
    def trim_descripcion(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @model_validator(mode="after")
    def valid_patch_fields(self) -> "CategoriaPatch":
        if "nombre" in self.model_fields_set and self.nombre is None:
            raise ValueError("nombre no puede ser null")
        if self.nombre is not None and not 3 <= len(self.nombre) <= 50:
            raise ValueError("El nombre debe tener entre 3 y 50 caracteres")
        return self


class CategoriaRead(CategoriaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
