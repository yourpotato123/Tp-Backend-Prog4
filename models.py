from typing import Optional, List
from datetime import datetime
import re
from sqlmodel import SQLModel, Field, Relationship
from pydantic import validator, Field as PydanticField




CURRENT_YEAR = datetime.utcnow().year

# ---------- Auto models ----------
class AutoBase(SQLModel):
    marca: str
    modelo: str
    año: int
    numero_chasis: str

    @validator("año")
    def año_valido(cls, v):
        if not (1900 <= v <= CURRENT_YEAR):
            raise ValueError(f"Año debe estar entre 1900 y {CURRENT_YEAR}")
        return v

    @validator("numero_chasis")
    def chasis_alfanumerico(cls, v):
        if not re.fullmatch(r"[A-Za-z0-9\-]+", v):
            raise ValueError("numero_chasis debe ser alfanumérico")
        return v


class Auto(AutoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    numero_chasis: str = Field(index=True, unique=True)
    
    ventas: List["Venta"] = Relationship(back_populates="auto")


class AutoCreate(AutoBase):
    pass


class AutoUpdate(SQLModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    año: Optional[int] = None
    numero_chasis: Optional[str] = None

    @validator("año")
    def año_valido(cls, v):
        if v is None:
            return v
        if not (1900 <= v <= CURRENT_YEAR):
            raise ValueError(f"Año debe estar entre 1900 y {CURRENT_YEAR}")
        return v

    @validator("numero_chasis")
    def chasis_alfanumerico(cls, v):
        if v is None:
            return v
        if not re.fullmatch(r"[A-Za-z0-9\-]+", v):
            raise ValueError("numero_chasis debe ser alfanumérico")
        return v


class AutoResponse(AutoBase):
    id: int


class AutoResponseWithVentas(AutoResponse):
    ventas: List["VentaResponse"] = PydanticField(default_factory=list)


# ---------- Venta models ----------
class VentaBase(SQLModel):
    nombre_comprador: str
    precio: float
    fecha_venta: datetime

    @validator("precio")
    def precio_positivo(cls, v):
        if v <= 0:
            raise ValueError("precio debe ser mayor a 0")
        return v

    @validator("nombre_comprador")
    def nombre_no_vacio(cls, v):
        if not v or not v.strip():
            raise ValueError("nombre_comprador no puede estar vacío")
        return v.strip()

    @validator("fecha_venta")
    def fecha_no_futura(cls, v):
        if v > datetime.utcnow():
            raise ValueError("fecha_venta no puede ser futura")
        return v


class Venta(VentaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    auto_id: int = Field(foreign_key="auto.id")

    auto: Optional[Auto] = Relationship(back_populates="ventas")


class VentaCreate(VentaBase):
    auto_id: int


class VentaUpdate(SQLModel):
    nombre_comprador: Optional[str] = None
    precio: Optional[float] = None
    fecha_venta: Optional[datetime] = None
    auto_id: Optional[int] = None

    @validator("precio")
    def precio_positivo(cls, v):
        if v is not None and v <= 0:
            raise ValueError("precio debe ser mayor a 0")
        return v

    @validator("nombre_comprador")
    def nombre_no_vacio(cls, v):
        if v is not None and not v.strip():
            raise ValueError("nombre_comprador no puede estar vacío")
        return v

    @validator("fecha_venta")
    def fecha_no_futura(cls, v):
        if v is not None and v > datetime.utcnow():
            raise ValueError("fecha_venta no puede ser futura")
        return v


class VentaResponse(VentaBase):
    id: int
    auto_id: int


class VentaResponseWithAuto(VentaResponse):
    auto: Optional[AutoResponse] = None


# forward refs
Auto.update_forward_refs()
Venta.update_forward_refs()
AutoResponseWithVentas.update_forward_refs()
VentaResponseWithAuto.update_forward_refs()


