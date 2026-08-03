import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/caja", tags=["caja"])


@router.get("/movimientos", response_model=List[schemas.MovimientoCajaOut])
def listar_movimientos(db: Session = Depends(get_db)):
    return db.query(models.MovimientoCaja).order_by(models.MovimientoCaja.id.desc()).all()


@router.post("/movimientos", response_model=schemas.MovimientoCajaOut)
def crear_movimiento(data: schemas.MovimientoCajaCreate, db: Session = Depends(get_db)):
    m = models.MovimientoCaja(
        fecha=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **data.dict(),
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@router.get("/resumen")
def resumen_caja(db: Session = Depends(get_db)):
    hoy = datetime.datetime.now().strftime("%Y-%m-%d")
    ventas_hoy = (
        db.query(models.Venta)
        .filter(models.Venta.fecha.like(f"{hoy}%"), models.Venta.estado == "ACTIVA")
        .all()
    )
    total_ventas = sum(v.total for v in ventas_hoy)
    movimientos_hoy = db.query(models.MovimientoCaja).filter(models.MovimientoCaja.fecha.like(f"{hoy}%")).all()
    ingresos = sum(m.importe for m in movimientos_hoy if m.tipo == "INGRESO")
    egresos = sum(m.importe for m in movimientos_hoy if m.tipo == "EGRESO")
    return {
        "fecha": hoy,
        "total_ventas": total_ventas,
        "cantidad_ventas": len(ventas_hoy),
        "ingresos_manuales": ingresos,
        "egresos_manuales": egresos,
    }
