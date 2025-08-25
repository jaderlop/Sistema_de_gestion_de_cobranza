from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    tipo_documento = Column(String)
    numero_documento = Column(String, unique=True, nullable=False)
    fecha_nacimiento = Column(Date)
    estado = Column(String, default="ACTIVO")  # ACTIVO o INACTIVO
    comentario = Column(String)
    prestamos = relationship("Prestamo", back_populates="cliente")
    

class Prestamo(Base):
    __tablename__= 'prestamos'
    id = Column(Integer, primary_key=True)
    monto_original = Column(Float)
    monto_final = Column(Float)
    cuotas = Column(Integer)
    frecuencia = Column(String)  # "Mensual", "Semanal", etc.
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    interes = Column(Float)  # corregido: antes era 'interes'
    comentario = Column(String)
    estado = Column(String(20), default="pendiente")
    
    cliente = relationship("Cliente", back_populates='prestamos')
    cuotas_rel = relationship("Cuota", back_populates='prestamo')  # nombre coherente

class EstadoCuota(str, enum.Enum):
    pagado = "pagado"
    impago = "impago"
    mora = "mora"

class Cuota(Base):
    __tablename__ = 'cuotas'
    id = Column(Integer, primary_key=True)
    numero_cuota = Column(Integer)
    monto = Column(Float)
    fecha_vencimiento = Column(Date)
    pagado = Column(String, default="NO")
    fecha_abono = Column(Date)
    estado = Column(Enum(EstadoCuota), default=EstadoCuota.impago)
    comentario = Column(String)
    
    prestamo_id = Column(Integer, ForeignKey('prestamos.id'))
    prestamo = relationship("Prestamo", back_populates="cuotas_rel")
