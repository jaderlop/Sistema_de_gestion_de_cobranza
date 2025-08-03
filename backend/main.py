from fastapi import FastAPI
from app.models.modelos import Base
from app.database.conexion import engine
from app.routers import clientes, prestamos, cuotas

# Crea las tablas
Base.metadata.create_all(bind=engine)

# Instancia FastAPI
app = FastAPI(
    title="Sistema de Gestión de Préstamos",
    description="API para gestionar clientes, préstamos y cuotas",
    version="1.0.0"
)

# Incluye los routers
app.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
app.include_router(prestamos.router, prefix="/prestamos", tags=["Préstamos"])
app.include_router(cuotas.router, prefix="/cuotas", tags=["Cuotas"])
