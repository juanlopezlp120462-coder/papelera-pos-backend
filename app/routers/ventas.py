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


@router.get("/", response_model=List[schemas.VentaOut])
def listar_ventas(db: Session = Depends(get_db)):

    return (
        db.query(models.Venta)
        .filter(models.Venta.estado == "ACTIVA")
        .order_by(models.Venta.id.desc())
        .all()
    )


@router.get("/{venta_id}/detalle")
def detalle_venta(
    venta_id: int,
    db: Session = Depends(get_db)
):

    items = (
        db.query(models.DetalleVenta)
        .filter(
            models.DetalleVenta.venta_id == venta_id
        )
        .all()
    )

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
def sincronizar_venta(
    data: dict,
    db: Session = Depends(get_db)
):

    venta_uuid = data.get("uuid")

    if not venta_uuid:
        raise HTTPException(
            400,
            "Falta uuid de la venta"
        )


    items = data.get("items", [])

    if not items:
        raise HTTPException(
            400,
            "La venta no tiene items"
        )


    total = data.get("total", 0)


    existente = (
        db.query(models.Venta)
        .filter(
            models.Venta.uuid == venta_uuid
        )
        .first()
    )


    # =====================================
    # SI EXISTE ACTUALIZAMOS
    # =====================================

    if existente:

        existente.fecha = (
            data.get("fecha")
            or existente.fecha
        )

        existente.total = total

        existente.forma_pago = (
            data.get("forma_pago")
        )

        existente.cliente_id = (
            data.get("cliente_id")
        )

        existente.descuento = (
            data.get("descuento",0)
        )

        existente.usuario = (
            data.get(
                "usuario",
                "Administrador"
            )
        )

        existente.pago_efectivo = (
            data.get(
                "pago_efectivo",
                0
            )
        )

        existente.pago_transferencia = (
            data.get(
                "pago_transferencia",
                0
            )
        )

        existente.pago_tarjeta = (
            data.get(
                "pago_tarjeta",
                0
            )
        )

        existente.pago_cuenta = (
            data.get(
                "pago_cuenta",
                0
            )
        )


        # borrar detalles anteriores

        db.query(models.DetalleVenta)\
            .filter(
                models.DetalleVenta.venta_id == existente.id
            )\
            .delete()


        for item in items:

            cantidad = item.get("cantidad", 0)
            precio = item.get("precio", 0)

            subtotal = item.get(
                "subtotal",
                cantidad * precio
            )

            db.add(
                models.DetalleVenta(
                    venta_id=venta.id,
                    producto=item.get("producto"),
                    cantidad=cantidad,
                    precio=precio,
                    subtotal=subtotal,
                    codigo=item.get("codigo")
                )
            )


        db.commit()


        return {
            "ok": True,
            "actualizada": True,
            "id": existente.id
        }



    # =====================================
    # SI NO EXISTE CREAMOS
    # =====================================


    venta = models.Venta(

        uuid=venta_uuid,

        fecha=data.get(
            "fecha"
        )
        or datetime.datetime.now()
        .strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        total=total,

        forma_pago=data.get(
            "forma_pago"
        ),

        cliente_id=data.get(
            "cliente_id"
        ),

        descuento=data.get(
            "descuento",
            0
        ),

        usuario=data.get(
            "usuario",
            "Administrador"
        ),

        pago_efectivo=data.get(
            "pago_efectivo",
            0
        ),

        pago_transferencia=data.get(
            "pago_transferencia",
            0
        ),

        pago_tarjeta=data.get(
            "pago_tarjeta",
            0
        ),

        pago_cuenta=data.get(
            "pago_cuenta",
            0
        )
    )


    db.add(venta)

    db.flush()


    for item in items:

        db.add(
            models.DetalleVenta(
                venta_id=venta.id,
                producto=item.get("producto"),
                cantidad=item.get(
                    "cantidad",
                    0
                ),
                precio=item.get(
                    "precio",
                    0
                ),
                subtotal=item.get(
                    "subtotal",
                    0
                ),
                codigo=item.get("codigo")
            )
        )


    db.commit()


    return {
        "ok": True,
        "creada": True,
        "id": venta.id
    }



@router.post("/", response_model=schemas.VentaOut)
def crear_venta(
    data: schemas.VentaCreate,
    db: Session = Depends(get_db)
):

    if not data.items:
        raise HTTPException(
            400,
            "La venta no tiene items"
        )


    total = (
        sum(
            i.cantidad * i.precio
            for i in data.items
        )
        -
        data.descuento
    )


    venta = models.Venta(

        uuid=str(uuid.uuid4()),

        fecha=datetime.datetime.now()
        .strftime("%Y-%m-%d %H:%M:%S"),

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

        subtotal = (
            item.cantidad *
            item.precio
        )


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


    db.commit()

    db.refresh(venta)

    return venta



@router.post("/{venta_id}/anular")
def anular_venta(
    venta_id: int,
    db: Session = Depends(get_db)
):

    venta = (
        db.query(models.Venta)
        .get(venta_id)
    )

    if not venta:
        raise HTTPException(
            404,
            "Venta no encontrada"
        )


    venta.estado = "ANULADA"

    db.commit()


    return {
        "ok": True
    }