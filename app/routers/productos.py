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
    p = models.Producto(**data.dict())
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
