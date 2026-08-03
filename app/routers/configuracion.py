from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/configuracion", tags=["configuracion"])

DEFAULTS = {
    "nombre_negocio": "COTILLON",
    "direccion": "",
    "telefono": "",
    "email": "",
    "cuit": "",
    "pie_ticket": "¡Gracias por su compra!",
    "moneda": "$",
}


@router.get("/", response_model=List[schemas.ConfiguracionOut])
def listar_configuracion(db: Session = Depends(get_db)):
    existentes = {c.clave: c for c in db.query(models.Configuracion).all()}
    for k, v in DEFAULTS.items():
        if k not in existentes:
            nuevo = models.Configuracion(clave=k, valor=v)
            db.add(nuevo)
            existentes[k] = nuevo
    db.commit()
    return list(existentes.values())


@router.put("/{clave}")
def set_configuracion(clave: str, valor: str, db: Session = Depends(get_db)):
    c = db.query(models.Configuracion).get(clave)
    if c:
        c.valor = valor
    else:
        c = models.Configuracion(clave=clave, valor=valor)
        db.add(c)
    db.commit()
    return {"ok": True}
