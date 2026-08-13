from pydantic import BaseModel
from typing import Optional, List


class ProductoBase(BaseModel):
    codigo_barras: Optional[str] = None
    nombre: str
    categoria: Optional[str] = None
    precio_compra: float = 0
    precio_venta: float = 0
    stock: int = 0
    stock_minimo: int = 5


class ProductoCreate(ProductoBase):
    pass


class ProductoSync(BaseModel):
    uuid: str
    codigo_barras: Optional[str] = None
    nombre: str
    categoria: Optional[str] = None
    precio_compra: float = 0
    precio_venta: float = 0
    stock: int = 0
    stock_minimo: int = 5


class ProductoOut(ProductoBase):
    id: int
    uuid: str | None = None

    class Config:
        from_attributes = True


class ClienteBase(BaseModel):
    nombre: str
    documento: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    email: Optional[str] = None
    saldo: float = 0


class ClienteCreate(ClienteBase):
    pass


class ClienteOut(ClienteBase):
    id: int

    class Config:
        from_attributes = True


class ItemVenta(BaseModel):
    producto_id: Optional[int] = None
    producto: str
    cantidad: int
    precio: float
    codigo: Optional[str] = None


class VentaCreate(BaseModel):
    items: List[ItemVenta]
    forma_pago: Optional[str] = "EFECTIVO"
    cliente_id: Optional[int] = None
    descuento: float = 0
    usuario: Optional[str] = "Administrador"
    pago_efectivo: float = 0
    pago_transferencia: float = 0
    pago_tarjeta: float = 0
    pago_cuenta: float = 0


class VentaOut(BaseModel):
    id: int
    uuid: str | None
    fecha: str
    total: float
    forma_pago: Optional[str]
    cliente_id: Optional[int]
    estado: str
    descuento: float
    usuario: str
    pago_efectivo: float = 0
    pago_transferencia: float = 0
    pago_tarjeta: float = 0
    pago_cuenta: float = 0

    class Config:
        from_attributes = True


class MovimientoCajaCreate(BaseModel):
    uuid: Optional[str] = None
    fecha: Optional[str] = None
    tipo: str
    importe: float
    concepto: Optional[str] = None
    usuario: Optional[str] = "Administrador"


class MovimientoCajaOut(MovimientoCajaCreate):
    id: int

    class Config:
        from_attributes = True


class ArqueoCreate(BaseModel):
    uuid: Optional[str] = None
    fecha: str
    apertura: float = 0
    esperado: float = 0
    real: float = 0
    diferencia: float = 0
    usuario: Optional[str] = "Administrador"
    observaciones: Optional[str] = None
    ventas_total: float = 0
    ventas_efectivo: float = 0
    ventas_transferencia: float = 0
    ventas_tarjeta: float = 0
    ventas_cuenta: float = 0
    cantidad_ventas: int = 0


class PedidoCreate(BaseModel):
    entrega: Optional[str] = None
    cliente_id: Optional[int] = None
    observaciones: Optional[str] = None
    items: List[ItemVenta] = []


class ConfiguracionOut(BaseModel):
    clave: str
    valor: Optional[str]

    class Config:
        from_attributes = True