from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db

router = APIRouter(prefix="/historial", tags=["historial"])


@router.get("/")
def obtener_historial(db: Session = Depends(get_db)):
    ventas = (
        db.query(models.Venta)
        .order_by(models.Venta.id.desc())
        .all()
    )

    return ventas