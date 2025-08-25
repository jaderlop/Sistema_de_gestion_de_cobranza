from pydantic import BaseModel
from typing import Optional
from datetime import date
import enum

# --------------------
# CLIENTE
# --------------------
class ClienteBase(BaseModel):
    nombre: str
    documento: str
    tipo_documento: Optional[str] = "DNI"

class ClienteOut(BaseModel):
    id: int

    class Config:
        from_attributes = True

# --------------------
# PRESTAMO
# --------------------
# Schema de entrada: lo que el usuario envía
class PrestamoCreate(BaseModel):
    cliente_id: int
    monto_original: float
    interes: Optional[float] = 0.0
    frecuencia: Optional[str] = "Mensual"
    cuotas: int
    fecha_inicio: date
    fecha_fin: date

# Schema de salida: lo que devolvemos
class PrestamoOut(BaseModel):
    id: int
    cliente_id: int
    monto_original: float
    cuotas: int
    interes: float
    frecuencia: str
    monto_final: float
    fecha_inicio: date
    fecha_fin: date

    class Config:
        from_attributes = True

class PagarCuota(BaseModel):
    dni: str
    numero_cuota: int
    fecha_abono: date


# ---------------------------------
# Base
# ---------------------------------
class CuotaBase(BaseModel):
    numero_cuota: int
    monto: float
    fecha_vencimiento: date
    estado: str   # podría usarse EstadoCuota si quieres tipado estricto
    comentario: Optional[str] = None


# ---------------------------------
# Para creación (input al crear)
# ---------------------------------
class CuotaCreate(CuotaBase):
    prestamo_id: int   # porque necesitas ligarla a un préstamo


# ---------------------------------
# Para actualización (input al editar)
# ---------------------------------
class CuotaUpdate(BaseModel):
    monto: Optional[float] = None
    fecha_vencimiento: Optional[date] = None
    estado: Optional[str] = None
    comentario: Optional[str] = None
    pagado: Optional[str] = None


# ---------------------------------
# Para salida (output al devolver en endpoints)
# ---------------------------------
class CuotaOut(CuotaBase):
    id: int
    prestamo_id: int
    pagado: str

    class Config:
        orm_mode = True
