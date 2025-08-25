from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.conexion import get_db
from app.services.crud import crear_cliente, obtener_cliente, actualizar_cliente, probar_conexion
from pydantic import BaseModel
from datetime import date

router = APIRouter(prefix="/clientes", tags=["Clientes"])

class ClienteConPrestamoInput(BaseModel):
    nombre: str
    tipo_documento: str
    numero_documento: str
    fecha_nacimiento: date
    
@router.post("/", summary="Crear cliente con préstamo")
def crear_cliente_endopint(cliente: ClienteConPrestamoInput, db: Session = Depends(get_db)):
    return crear_cliente(
        db, cliente.nombre, cliente.tipo_documento, cliente.numero_documento, cliente.fecha_nacimiento
    )

@router.get("/{cliente_id}", summary="Obtener cliente por ID")
def get_cliente_endopint(cliente_id: int, db: Session = Depends(get_db)):
    return obtener_cliente(db, cliente_id)

@router.get("/test-db")
def test_db(db:Session = Depends(get_db)):
    return {"ok": probar_conexion(db)}