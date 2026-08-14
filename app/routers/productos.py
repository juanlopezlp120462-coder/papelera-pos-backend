from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/productos", tags=["productos"])


@router.get("/", response_model=List[schemas.ProductoOut])
def listar_productos(db: Session = Depends(get_db)):
    return db.query(models.Producto).order_by(models.Producto.nombre).all()


@router.get("/{producto_id}", response_model=schemas.ProductoOut)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Producto).get(producto_id)
    if not p:
        raise HTTPException(404, "Producto no encontrado")
    return p


@router.post("/", response_model=schemas.ProductoOut)
def crear_producto(data: schemas.ProductoCreate, db: Session = Depends(get_db)):
    p = models.Producto(uuid=str(uuid4()), **data.dict())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.put("/{producto_id}", response_model=schemas.ProductoOut)
def editar_producto(producto_id: int, data: schemas.ProductoCreate, db: Session = Depends(get_db)):
    p = db.query(models.Producto).get(producto_id)
    if not p:
        raise HTTPException(404, "Producto no encontrado")
    for k, v in data.dict().items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{producto_id}")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Producto).get(producto_id)
    if not p:
        raise HTTPException(404, "Producto no encontrado")
    db.delete(p)
    db.commit()
    return {"ok": True}

# ==========================================================
# ELIMINAR PRODUCTO POR UUID
# USADO POR LA SINCRONIZACION
# ==========================================================

@router.delete("/sync/{producto_uuid}")
def eliminar_producto_sync(
    producto_uuid: str,
    db: Session = Depends(get_db)
):

    producto = (
        db.query(models.Producto)
        .filter(
            models.Producto.uuid == producto_uuid
        )
        .first()
    )

    if not producto:

        return {
            "eliminado": False,
            "ya_no_existe": True
        }

    db.delete(producto)
    db.commit()

    return {
        "eliminado": True,
        "uuid": producto_uuid
    }

@router.post("/sync")
def sincronizar_producto(
    data: schemas.ProductoSync,
    db: Session = Depends(get_db)
):

    producto = (
        db.query(models.Producto)
        .filter(
            models.Producto.uuid == data.uuid
        )
        .first()
    )


    if producto:

        producto.codigo_barras = data.codigo_barras
        producto.nombre = data.nombre
        producto.categoria = data.categoria
        producto.precio_compra = data.precio_compra
        producto.precio_venta = data.precio_venta
        producto.stock = data.stock
        producto.stock_minimo = data.stock_minimo

        db.commit()
        db.refresh(producto)

        return {
            "actualizada": True,
            "id": producto.id
        }


    nuevo = models.Producto(
        uuid=data.uuid,
        codigo_barras=data.codigo_barras,
        nombre=data.nombre,
        categoria=data.categoria,
        precio_compra=data.precio_compra,
        precio_venta=data.precio_venta,
        stock=data.stock,
        stock_minimo=data.stock_minimo
    )


    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)


    return {
        "creada": True,
        "id": nuevo.id
    }


