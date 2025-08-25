from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.conexion import get_db
from app.services.crud import crear_prestamo
from pydantic import BaseModel
from datetime import date
from app.schemas import PrestamoCreate, PrestamoOut

router = APIRouter(prefix="/prestamo", tags=["Prestamo"])

@router.post("/", summary="Crear prestamo y generar cuotas", response_model=PrestamoOut)
def crear_prestamo_endpoint(payload: PrestamoCreate, db: Session = Depends(get_db)):
    try:
        prestamo = crear_prestamo(
            db=db,
            cliente_id=payload.cliente_id,
            monto_original=payload.monto_original,
            cuotas=payload.cuotas,
            interes=payload.interes,
            fecha_inicio=payload.fecha_inicio,
            frecuencia=payload.frecuencia,
            fecha_fin=payload.fecha_fin
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return prestamo

