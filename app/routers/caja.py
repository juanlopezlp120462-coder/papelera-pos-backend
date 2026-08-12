import datetime
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/caja", tags=["caja"])

# =========================
# MOVIMIENTOS
# =========================

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


@router.post("/movimientos/sync")
def sincronizar_movimientos(movimientos: List[schemas.MovimientoCajaCreate], db: Session = Depends(get_db)):
    for data in movimientos:
        datos_dict = data.dict()
        if "fecha" not in datos_dict or not datos_dict["fecha"]:
            datos_dict["fecha"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        m = models.MovimientoCaja(**datos_dict)
        db.add(m)
        
    db.commit()
    return {"status": "success", "sincronizados": len(movimientos)}

# =========================
# ARQUEOS
# =========================

@router.get("/arqueos")
def listar_arqueos(db: Session = Depends(get_db)):
    """
    Permite que cualquier PC descargue la lista de arqueos para mostrarlos en el historial.
    """
    return db.query(models.Arqueo).order_by(models.Arqueo.id.desc()).all()


@router.post("/arqueos")
def crear_arqueo(data: schemas.ArqueoCreate, db: Session = Depends(get_db)):
    """
    Recibe un cierre de caja individual desde una PC y lo guarda en la nube.
    """
    datos_dict = data.dict()
    
    if "uuid" not in datos_dict or not datos_dict["uuid"]:
        datos_dict["uuid"] = str(uuid.uuid4())
        
    # Evitar duplicados si se reintenta el envío
    existente = db.query(models.Arqueo).filter(models.Arqueo.uuid == datos_dict["uuid"]).first()
    if existente:
        return existente

    nuevo_arqueo = models.Arqueo(**datos_dict)
    db.add(nuevo_arqueo)
    db.commit()
    db.refresh(nuevo_arqueo)
    return nuevo_arqueo


@router.post("/arqueos/sync")
def sincronizar_arqueos(arqueos: List[schemas.ArqueoCreate], db: Session = Depends(get_db)):
    """
    Recibe un lote de arqueos desde el punto de venta local e inserta los faltantes.
    """
    count = 0
    for data in arqueos:
        datos_dict = data.dict()
        
        if "uuid" not in datos_dict or not datos_dict["uuid"]:
            datos_dict["uuid"] = str(uuid.uuid4())
            
        existente = db.query(models.Arqueo).filter(models.Arqueo.uuid == datos_dict["uuid"]).first()
        if not existente:
            nuevo_arqueo = models.Arqueo(**datos_dict)
            db.add(nuevo_arqueo)
            count += 1
            
    db.commit()
    return {"status": "success", "arqueos_sincronizados": count}

# =========================
# RESUMEN
# =========================

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