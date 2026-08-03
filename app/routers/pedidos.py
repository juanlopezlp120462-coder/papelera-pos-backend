import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/pedidos", tags=["pedidos"])


@router.get("/")
def listar_pedidos(db: Session = Depends(get_db)):
    pedidos = db.query(models.Pedido).order_by(models.Pedido.id.desc()).all()
    return [
        {
            "id": p.id,
            "fecha": p.fecha,
            "entrega": p.entrega,
            "cliente_id": p.cliente_id,
            "estado": p.estado,
            "observaciones": p.observaciones,
            "total": p.total,
        }
        for p in pedidos
    ]


@router.post("/")
def crear_pedido(data: schemas.PedidoCreate, db: Session = Depends(get_db)):
    total = sum(i.cantidad * i.precio for i in data.items)
    pedido = models.Pedido(
        fecha=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        entrega=data.entrega,
        cliente_id=data.cliente_id,
        observaciones=data.observaciones,
        total=total,
    )
    db.add(pedido)
    db.flush()
    for item in data.items:
        db.add(
            models.DetallePedido(
                pedido_id=pedido.id,
                producto=item.producto,
                cantidad=item.cantidad,
                precio=item.precio,
                subtotal=item.cantidad * item.precio,
                codigo=item.codigo,
            )
        )
    db.commit()
    return {"id": pedido.id, "total": pedido.total}


@router.put("/{pedido_id}/estado")
def cambiar_estado(pedido_id: int, estado: str, db: Session = Depends(get_db)):
    pedido = db.query(models.Pedido).get(pedido_id)
    if not pedido:
        raise HTTPException(404, "Pedido no encontrado")
    pedido.estado = estado
    db.commit()
    return {"ok": True}
