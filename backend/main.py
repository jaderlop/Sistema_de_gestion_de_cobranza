from fastapi import FastAPI
from app.models.modelos import Base
from app.database.conexion import engine
from app.routes import cuotas_routes, prestamos_routes, clientes_routes
from app.models.modelos import Cliente, Prestamo, Cuota

app = FastAPI()

# Crear las tablas en la BD
# Base.metadata.drop_all(bind=engine) ## --> Eliminacion de las tablas
Base.metadata.create_all(bind=engine)

# Registrar las rutas
app.include_router(clientes_routes.router)
app.include_router(prestamos_routes.router)
app.include_router(cuotas_routes.router)

