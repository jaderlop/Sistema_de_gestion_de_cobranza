
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.conexion import get_db
from app.services.crud import listar_cuotas_por_dni, pagar_cuota
from pydantic import BaseModel
from datetime import date

router = APIRouter(prefix="/cuotas", tags=["Cuotas"])

# 1. Endpoint para listar cuotas de un cliente por DNI
@router.get("/cuotas/{dni}")
def listar_cuotas_endpoint(dni: str, db: Session = Depends(get_db)):
    cuotas = listar_cuotas_por_dni(db, dni)
    if cuotas is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"dni": dni, "cuotas": cuotas}





# 2. Endpoint para pagar una cuota
@router.post("/cuotas/pagar")
def pagar_cuotas_endpoint(dni: str, numero_cuota: int, fecha_abono: date, db: Session = Depends(get_db)):
    resultado = pagar_cuota(db, dni, numero_cuota, fecha_abono)
    if "error" in resultado:
        raise HTTPException(status_code=400, detail=resultado["error"])
    return resultado