from sqlalchemy.orm import Session
from app.models.modelos import Cliente, Prestamo, Cuota, EstadoCuota
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from datetime import date
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

# ——————————————————————————————
# 1. VERIFICAR CONEXION
# ——————————————————————————————

def probar_conexion(db: Session):
    return db.execute("SELECT 1").scalar()

# ——————————————————————————————
# 2. CREATE
# ——————————————————————————————
def crear_cliente(db: Session, nombre: str, tipo_documento: str, numero_documento: int, fecha_nacimiento: date) -> Cliente:
    try:
        cliente = Cliente(
            nombre=nombre, 
            tipo_documento=tipo_documento, 
            numero_documento=numero_documento, 
            fecha_nacimiento=fecha_nacimiento)
        db.add(cliente)
        db.commit()
        db.refresh(cliente)   # trae el objeto con su ID y datos actualizados
        return cliente
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El numero de docuemnto ya esta registrado")

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
# 6. CREAR PRESTAMO Y 
# ——————————————————————————————

def crear_prestamo( db: Session, 
                   cliente_id: int, 
                   monto_original: float, 
                   interes: float,
                   cuotas: int,
                   frecuencia: str,
                   fecha_inicio: date, 
                   fecha_fin: date,  
                   estado: str ="ACTIVO") -> Prestamo:
    # 1) validaciones básicas
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise ValueError("Cliente no encontrado")

    if cuotas <= 0:
        raise ValueError("cuotas debe ser > 0")
    
    if interes <0:
        raise ValueError("El interes no puede ser negativo")
    
    # calculo del monto con interes
    monto_total = monto_original * (1 + interes/100)

    # 2) crear objeto Prestamo (estado inicial)
    prestamo = Prestamo(
        cliente_id=cliente_id,
        monto_original=monto_original,
        monto_final=monto_total,
        interes=interes,
        cuotas=cuotas,
        fecha_inicio=fecha_inicio,
        frecuencia=frecuencia,
        fecha_fin=fecha_fin,
        estado=estado
    )
    db.add(prestamo)
    db.flush()  # asigna prestamo.id antes del commit

    # 3) calcular monto de cuota (ejemplo simple: cuotas iguales sin interés compuesto)
    # Si quieres amortización real, ver la nota abajo.
    cuota_base = round(monto_total / cuotas, 2)

    # 4) generar cuotas
    fecha = fecha_inicio
    for n in range(1, cuotas + 1):
        cuota = Cuota(
            prestamo_id=prestamo.id,
            numero_cuota=n,
            monto=cuota_base,
            fecha_vencimiento=fecha,
            estado="impago"
        )
        db.add(cuota)
        # avanzar fecha según frecuencia
        if frecuencia == "mensual":
            fecha = fecha + relativedelta(months=1)
        elif frecuencia == "semanal":
            fecha = fecha + relativedelta(days=7)
        else:
            fecha = fecha + relativedelta(months=1)

    # 5) commit y refrescar
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(prestamo)
    return prestamo
# ——————————————————————————————# ——————————————————————————————# ——————————————————————————————
# ——————————————————————————————# ——————————————————————————————# ——————————————————————————————# ——————————————————————————————
# Limpiar y definir funciones utiles de las que no# ——————————————————————————————# ——————————————————————————————# ——————————————————————————————

## pagar cuotas
def pagar_cuota(db: Session, dni: str, numero_cuota: int, fecha_abono: date):
    cliente = db.query(Cliente).filter(Cliente.numero_documento == dni).first()
    if not cliente:
        return {"error": "Cliente no encontrado"}
    
    db.refresh(cliente)

    # Buscar las cuotas del cliente en orden
    todas_cuotas = []
    for prestamo in cliente.prestamos:
        todas_cuotas.extend(prestamo.cuotas_rel)
    
    todas_cuotas.sort(key=lambda x: (x.prestamo_id, x.numero_cuota))

    # Verificar que la cuota existe
    cuota = next((c for c in todas_cuotas if c.numero_cuota == numero_cuota), None)
    if not cuota:
        return {"error": "Cuota no encontrada"}

    # Validar que no se pueda pagar una cuota adelantada
    cuotas_pendientes = [c for c in todas_cuotas if c.estado != "pagado"]
    if not cuotas_pendientes:
        return {"error": "El cliente ya no tiene cuotas pendientes"}

    siguiente_cuota = cuotas_pendientes[0]
    if cuota.id != siguiente_cuota.id:
        return {"error": f"Debe pagar primero la cuota {siguiente_cuota.numero_cuota}"}

    # Marcar como pagada
    cuota.estado = "pagado"
    cuota.fecha_abono = fecha_abono
    db.commit()
    db.refresh(cuota)

    return {"mensaje": f"Cuota {cuota.numero_cuota} pagada correctamente"}







# ——————————————————————————————# ——————————————————————————————# ——————————————————————————————# ——————————————————————————————
# ——————————————————————————————# ——————————————————————————————# ——————————————————————————————# ——————————————————————————————
# ——————————————————————————————# ——————————————————————————————# ——————————————————————————————# ——————————————————————————————
# 8. LISTAR CUOTAS
# ——————————————————————————————
def listar_cuotas(db: Session) -> list[Cuota]:
    return db.query(Cuota).all()



## lista do de cuotas por DNI
def listar_cuotas_por_dni(db: Session, dni: str):
    cliente = db.query(Cliente).filter(Cliente.numero_documento == dni).first()
    if not cliente:
        return None

    cuotas = []
    for prestamo in cliente.prestamos:
        for cuota in prestamo.cuotas_rel:
            cuotas.append({
                "prestamo_id": prestamo.id,
                "cuota_numero": cuota.numero_cuota,
                "monto": cuota.monto,
                "fecha_vencimiento": cuota.fecha_vencimiento,
                "estado": cuota.estado
            })

    # Ordenar por préstamo y número de cuota
    cuotas.sort(key=lambda x: (x["prestamo_id"], x["cuota_numero"]))
    return cuotas



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