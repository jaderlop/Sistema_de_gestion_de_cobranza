from app.models.modelos import Base
from app.database.conexion import engine

Base.metadata.create_all(bind=engine)

from app.services.crud import crear_cliente_con_prestamo
crear_cliente_con_prestamo("Juan Pérez", "12345678", 1000, 5)
