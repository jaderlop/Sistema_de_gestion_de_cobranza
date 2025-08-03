from pydantic import BaseModel
from typing import Optional
from datetime import date

class ClienteBase(BaseModel):
    nombre: str
    documento: str
    tipo_documento: Optional[str] = "DNI"

class ClienteOut(ClienteBase):
    id: int

    class Config:
        orm_mode = True

class PrestamoBase(BaseModel):
    cliente_id: int
    monto: float
    cuotas: int
    interes: Optional[float] = 0.0
    frecuencia: Optional[str] = "Mensual"

class PrestamoOut(PrestamoBase):
    id: int
    monto_final: float
    fecha_inicio: date
    fecha_fin: date

    class Config:
        orm_mode = True