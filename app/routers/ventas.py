import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/ventas", tags=["ventas"])


@router.get("/", response_model=List[schemas.VentaOut])
def listar_ventas(db: Session = Depends(get_db)):
    return (
        db.query(models.Venta)
        .filter(models.Venta.estado == "ACTIVA")
        .order_by(models.Venta.id.desc())
        .all()
    )


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


@router.post("/", response_model=schemas.VentaOut)
def crear_venta(data: schemas.VentaCreate, db: Session = Depends(get_db)):
    if not data.items:
        raise HTTPException(400, "La venta no tiene items")

    total = sum(i.cantidad * i.precio for i in data.items) - data.descuento

    venta = models.Venta(
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
    db.flush()  # para obtener venta.id antes del commit

    for item in data.items:
        subtotal = item.cantidad * item.precio
        db.add(
            models.DetalleVenta(
                venta_id=venta.id,
                producto=item.producto,
                cantidad=item.cantidad,
                precio=item.precio,
                subtotal=subtotal,
                codigo=item.codigo,
            )
        )
        # descontar stock si el item está vinculado a un producto
        if item.producto_id:
            prod = db.query(models.Producto).get(item.producto_id)
            if prod:
                prod.stock = max(0, prod.stock - item.cantidad)

    db.commit()
    db.refresh(venta)
    return venta


@router.post("/{venta_id}/anular")
def anular_venta(venta_id: int, db: Session = Depends(get_db)):
    venta = db.query(models.Venta).get(venta_id)
    if not venta:
        raise HTTPException(404, "Venta no encontrada")
    venta.estado = "ANULADA"
    db.commit()
    return {"ok": True}
