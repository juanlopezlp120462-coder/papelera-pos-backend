from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.get("/", response_model=List[schemas.ClienteOut])
def listar_clientes(db: Session = Depends(get_db)):
    return db.query(models.Cliente).order_by(models.Cliente.nombre).all()


@router.post("/", response_model=schemas.ClienteOut)
def crear_cliente(data: schemas.ClienteCreate, db: Session = Depends(get_db)):
    c = models.Cliente(**data.dict())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.put("/{cliente_id}", response_model=schemas.ClienteOut)
def editar_cliente(cliente_id: int, data: schemas.ClienteCreate, db: Session = Depends(get_db)):
    c = db.query(models.Cliente).get(cliente_id)
    if not c:
        raise HTTPException(404, "Cliente no encontrado")
    for k, v in data.dict().items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{cliente_id}")
def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    c = db.query(models.Cliente).get(cliente_id)
    if not c:
        raise HTTPException(404, "Cliente no encontrado")
    db.delete(c)
    db.commit()
    return {"ok": True}
