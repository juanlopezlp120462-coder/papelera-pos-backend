import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/ventas",
    tags=["ventas"]
)

@router.get("/caja/estado")
def estado_caja(db: Session = Depends(get_db)):
    pendientes = db.query(models.Venta).filter(models.Venta.estado == "ACTIVA").count()
    return {"caja_abierta": pendientes > 0}

@router.get("/", response_model=List[schemas.VentaOut])
def listar_ventas(db: Session = Depends(get_db)):
    return db.query(models.Venta).filter(models.Venta.estado == "ACTIVA").order_by(models.Venta.id.desc()).all()

@router.get("/{venta_id}/detalle")
def detalle_venta(venta_id: int, db: Session = Depends(get_db)):
    items = db.query(models.DetalleVenta).filter(models.DetalleVenta.venta_id == venta_id).all()
    return [
        {
            "producto": d.producto,
            "cantidad": d.cantidad,
            "precio": d.precio,
            "subtotal": d.subtotal,
            "codigo": d.codigo,
        }
        for d in items
    ]

# ============================================
# SINCRONIZACION OFFLINE POR UUID
# ============================================

@router.post("/sync")
def sincronizar_venta(data: dict, db: Session = Depends(get_db)):
    venta_uuid = data.get("uuid")
    items = data.get("items", [])

    if not venta_uuid:
        raise HTTPException(400, "Falta uuid de la venta")
    if not items:
        raise HTTPException(400, "La venta no tiene items")

    # Conversión segura de tipos
    try:
        total = float(data.get("total", 0))
        pago_efectivo = float(data.get("pago_efectivo", 0))
        pago_transferencia = float(data.get("pago_transferencia", 0))
        pago_tarjeta = float(data.get("pago_tarjeta", 0))
        pago_cuenta = float(data.get("pago_cuenta", 0))
        descuento = float(data.get("descuento", 0))
    except ValueError:
        raise HTTPException(400, "Datos numéricos inválidos")

    existente = db.query(models.Venta).filter(models.Venta.uuid == venta_uuid).first()

    # --- LÓGICA DE ACTUALIZACIÓN ---
    if existente:
        existente.fecha = data.get("fecha") or existente.fecha
        existente.total = total
        existente.forma_pago = data.get("forma_pago")
        existente.cliente_id = data.get("cliente_id")
        existente.descuento = descuento
        existente.usuario = data.get("usuario", "Administrador")
        existente.pago_efectivo = pago_efectivo
        existente.pago_transferencia = pago_transferencia
        existente.pago_tarjeta = pago_tarjeta
        existente.pago_cuenta = pago_cuenta

        # Borrar detalles previos para reinsertar
        db.query(models.DetalleVenta).filter(models.DetalleVenta.venta_id == existente.id).delete()
    
    # --- LÓGICA DE CREACIÓN ---
    else:
        existente = models.Venta(
            uuid=venta_uuid,
            estado="ACTIVA",
            fecha=data.get("fecha") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total=total,
            forma_pago=data.get("forma_pago"),
            cliente_id=data.get("cliente_id"),
            descuento=descuento,
            usuario=data.get("usuario", "Administrador"),
            pago_efectivo=pago_efectivo,
            pago_transferencia=pago_transferencia,
            pago_tarjeta=pago_tarjeta,
            pago_cuenta=pago_cuenta
        )
        db.add(existente)
        db.flush() # Obtener el ID antes del commit

    # Insertar detalles y actualizar stock
    for item in items:
        cantidad = float(item.get("cantidad", 0))
        precio = float(item.get("precio", 0))
        subtotal = float(item.get("subtotal", cantidad * precio))
        codigo = item.get("codigo")

        db.add(models.DetalleVenta(
            venta_id=existente.id,
            producto=item.get("producto"),
            cantidad=cantidad,
            precio=precio,
            subtotal=subtotal,
            codigo=codigo
        ))

        # Actualizar stock si existe el producto
        prod = db.query(models.Producto).filter(models.Producto.codigo_barras == codigo).first()
        if prod:
            prod.stock -= cantidad

    db.commit()
    return {"ok": True, "id": existente.id}

@router.post("/", response_model=schemas.VentaOut)
def crear_venta(data: schemas.VentaCreate, db: Session = Depends(get_db)):
    if not data.items:
        raise HTTPException(400, "La venta no tiene items")

    total = sum(i.cantidad * i.precio for i in data.items) - data.descuento

    venta = models.Venta(
        uuid=str(uuid.uuid4()),
        estado="ACTIVA",
        fecha=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total=total,
        forma_pago=data.forma_pago,
        cliente_id=data.cliente_id,
        descuento=data.descuento,
        usuario=data.usuario,
        pago_efectivo=data.pago_efectivo,
        pago_transferencia=data.pago_transferencia,
        pago_tarjeta=data.pago_tarjeta,
        pago_cuenta=data.pago_cuenta,
    )

    db.add(venta)
    db.flush()

    for item in data.items:
        db.add(models.DetalleVenta(
            venta_id=venta.id,
            producto=item.producto,
            cantidad=item.cantidad,
            precio=item.precio,
            subtotal=item.cantidad * item.precio,
            codigo=item.codigo,
        ))
        
        # Descontar stock
        prod = db.query(models.Producto).filter(models.Producto.codigo == item.codigo).first()
        if prod:
            prod.stock -= item.cantidad

    db.commit()
    db.refresh(venta)
    return venta

@router.post("/{venta_id}/anular")
def anular_venta(venta_id: int, db: Session = Depends(get_db)):
    venta = db.query(models.Venta).get(venta_id)
    if not venta:
        raise HTTPException(404, "Venta no encontrada")
    
    # Devolver stock al anular
    items = db.query(models.DetalleVenta).filter(models.DetalleVenta.venta_id == venta_id).all()
    for item in items:
        prod = db.query(models.Producto).filter(models.Producto.codigo == item.codigo).first()
        if prod:
            prod.stock += item.cantidad

    venta.estado = "ANULADA"
    db.commit()
    return {"ok": True}