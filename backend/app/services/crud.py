from app.models.modelos import Cliente, Prestamo, Cuota
from app.database.conexion import SessionLocal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import Cliente
from app.database import SessionLocal
from dateutil.relativedelta import relativedelta

# ——————————————————————————————
# 1. Sesión
# ——————————————————————————————
def get_db() -> Session:
    """Devuelve una sesión nueva; recuerda cerrarla cuando termines."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ——————————————————————————————
# 2. CREATE
# ——————————————————————————————
def crear_cliente(db: Session, nombre: str, dni: str) -> Cliente:
    cliente = Cliente(nombre=nombre, dni=dni)
    db.add(cliente)
    db.commit()
    db.refresh(cliente)   # trae el objeto con su ID y datos actualizados
    return cliente


# ——————————————————————————————
# 3. LISTAR CLIENTE
# ——————————————————————————————
def obtener_cliente(db: Session, id: int = None, dni: str = None, nombre: str = None) -> Cliente:
    query = db.query(Cliente)
    if id:
        return query.filter(Cliente.id == id).first()
    if dni:
        return query.filter(Cliente.dni == dni).first()
    if nombre:
        return query.filter(Cliente.nombre.ilike(f"%{nombre}%")).first()
    return None

# ——————————————————————————————
# 4. UPDATE
# ——————————————————————————————
def actualizar_cliente(db: Session, cliente_id: int, nombre: str = None, dni: str = None, comentario: str = None) -> Cliente:
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente:
        if nombre:
            cliente.nombre = nombre
        if dni:
            cliente.dni = dni
        if comentario:
            cliente.comentario = comentario
        db.commit()
        db.refresh(cliente)
    return cliente


# ——————————————————————————————
# 5. DELETE_CLIENTE
# ——————————————————————————————
def eliminar_cliente(db: Session, cliente_id: int) -> bool:
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente:
        cliente.estado = "INACTIVO"
        for prestamo in cliente.prestamos:
            for cuota in prestamo.cuotas_rel:
                if cuota.pagado == "NO":
                    cuota.pagado = "INACTIVO"
        db.commit()
        return True
    return False


# ——————————————————————————————
# 6. CREAR_PRESTAMO
# ——————————————————————————————
def crear_prestamo(
    db: Session,
    cliente_id: int,
    monto: float,
    cuotas: int,
    interes: float = 0.0,
    frecuencia: str = 'mensual'
) -> Prestamo:
    monto_total = round(monto * (1 + interes), 2)
    fecha_inicio = datetime.today().date()
    fecha_fin = fecha_inicio + relativedelta(months=+cuotas)

    prestamo = Prestamo(
        cliente_id=cliente_id,
        monto_original=monto,
        monto_final=monto_total,
        cuotas=cuotas,
        intere=interes,
        frecuencia=frecuencia,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )
    db.add(prestamo)
    db.commit()
    db.refresh(prestamo)

    # Llamada a función externa
    generar_cuotas(
        db=db,
        prestamo_id=prestamo.id,
        monto=monto_total,
        cuotas=cuotas,
        fecha_inicio=fecha_inicio,
        frecuencia=frecuencia
    )

    return prestamo

# ——————————————————————————————
# 7. GENARA CUOTAS
# ——————————————————————————————
def generar_cuotas(
    db: Session,
    prestamo_id: int,
    monto: float,
    cuotas: int,
    fecha_inicio: date,
    frecuencia: str = "mensual"
) -> list[Cuota]:
    monto_por_cuota = round(monto / cuotas, 2)
    lista = []

    for i in range(1, cuotas + 1):
        if frecuencia == "mensual":
            venc = fecha_inicio + relativedelta(months=+i)
        elif frecuencia == "quincenal":
            venc = fecha_inicio + timedelta(days=15 * i)
        elif frecuencia == "semanal":
            venc = fecha_inicio + timedelta(weeks=i)
        else:
            venc = fecha_inicio + relativedelta(months=+i)  # default

        cuota = Cuota(
            numero=i,
            monto=monto_por_cuota,
            fecha_vencimiento=venc,
            pagado="NO",
            prestamo_id=prestamo_id
        )
        db.add(cuota)
        lista.append(cuota)

    db.commit()
    return lista

# ——————————————————————————————
# 8. LISTAR CUOTAS
# ——————————————————————————————
def listar_cuotas(db: Session) -> list[Cuota]:
    return db.query(Cuota).all()

# ——————————————————————————————
# 9. OBTENER CUOTAS
# ——————————————————————————————
def obtener_cuota_por_id(db: Session, cuota_id: int) -> Cuota:
    return db.query(Cuota).filter(Cuota.id == cuota_id).first()

# ——————————————————————————————
# 10. MARCAR CUOTA COMO PAGADA
# ——————————————————————————————
def marcar_cuota_pagada(db: Session, cuota_id: int) -> Cuota:
    cuota = db.query(Cuota).filter(Cuota.id == cuota_id).first()
    if cuota:
        cuota.pagado = "SI"
        db.commit()
        db.refresh(cuota)
    return cuota

# ——————————————————————————————
# 11. COTIZAR_PRESTAMO
# ——————————————————————————————
def cotizar_prestamo(monto, cuotas, interes=0.0, frecuencia='Mensual'):
    monto_total = monto * (1 + interes)
    monto_cuota = monto_total / cuotas
    return {
        'monto_total': round(monto_total, 2),
        'monto_cuota': round(monto_cuota, 2),
        'cuotas': cuotas,
        'frecuencia': frecuencia
    }