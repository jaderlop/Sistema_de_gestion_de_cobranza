### Archivo encargado de leer la URL de conexion
### y creacion de el motor y fabrica de sesiones

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ✅ Esta función es la que necesitas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
