from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    dni = Column(String)
    prestamos = relationship("Prestamo", back_populates="cliente")

class Prestamo(Base):
    __tablename__ = 'prestamos'
    id = Column(Integer, primary_key=True)
    monto = Column(Float)
    cuotas = Column(Integer)
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    cliente = relationship("Cliente", back_populates="prestamos")
    cuotas_rel = relationship("Cuota", back_populates="prestamo")

class Cuota(Base):
    __tablename__ = 'cuotas'
    id = Column(Integer, primary_key=True)
    numero = Column(Integer)
    monto = Column(Float)
    fecha_vencimiento = Column(Date)
    pagado = Column(String, default="NO")
    prestamo_id = Column(Integer, ForeignKey('prestamos.id'))
    prestamo = relationship("Prestamo", back_populates="cuotas_rel")
