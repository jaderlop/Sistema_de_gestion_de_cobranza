from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    tipo_documento = Column(String)
    numero_documento = Column(Integer, unique=True)
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
    interes = Column(Float)  # corregido: antes era 'intere'
    comentario = Column(String)
    
    cliente = relationship("Cliente", back_populates='prestamos')
    cuotas_rel = relationship("Cuota", back_populates='prestamo')  # nombre coherente


class Cuota(Base):
    __tablename__ = 'cuotas'
    id = Column(Integer, primary_key=True)
    numero = Column(Integer)
    monto = Column(Float)
    fecha_vencimiento = Column(Date)
    pagado = Column(String, default="NO")
    comentario = Column(String)
    
    prestamo_id = Column(Integer, ForeignKey('prestamos.id'))
    prestamo = relationship("Prestamo", back_populates="cuotas_rel")
