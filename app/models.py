from sqlalchemy import Column, Integer, String, Float, Text
from .database import Base


class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    codigo_barras = Column(String, nullable=True, index=True)
    nombre = Column(String, nullable=False)
    categoria = Column(String, nullable=True)
    precio_compra = Column(Float, default=0)
    precio_venta = Column(Float, default=0)
    stock = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=5)


class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    documento = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    direccion = Column(String, nullable=True)
    email = Column(String, nullable=True)
    saldo = Column(Float, default=0)


class Venta(Base):
    __tablename__ = "ventas"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(String, nullable=False)
    total = Column(Float, nullable=False)
    forma_pago = Column(String, nullable=True)
    cliente_id = Column(Integer, nullable=True)
    estado = Column(String, default="ACTIVA")
    descuento = Column(Float, default=0)
    usuario = Column(String, default="Administrador")
    pago_efectivo = Column(Float, default=0)
    pago_transferencia = Column(Float, default=0)
    pago_tarjeta = Column(Float, default=0)
    pago_cuenta = Column(Float, default=0)


class DetalleVenta(Base):
    __tablename__ = "detalle_ventas"
    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer, nullable=True, index=True)
    producto = Column(String, nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    codigo = Column(String, nullable=True)


class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(String, nullable=False)
    entrega = Column(String, nullable=True)
    cliente_id = Column(Integer, nullable=True)
    estado = Column(String, default="PENDIENTE")
    observaciones = Column(Text, nullable=True)
    total = Column(Float, default=0)


class DetallePedido(Base):
    __tablename__ = "detalle_pedidos"
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, nullable=True, index=True)
    producto = Column(String, nullable=True)
    cantidad = Column(Integer, nullable=True)
    precio = Column(Float, nullable=True)
    subtotal = Column(Float, nullable=True)
    codigo = Column(String, nullable=True)


class MovimientoCaja(Base):
    __tablename__ = "movimientos_caja"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    importe = Column(Float, nullable=False)
    concepto = Column(String, nullable=True)
    usuario = Column(String, default="Administrador")


class Arqueo(Base):
    __tablename__ = "arqueos"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(String, nullable=False)
    apertura = Column(Float, nullable=True)
    esperado = Column(Float, nullable=True)
    real = Column(Float, nullable=True)
    diferencia = Column(Float, nullable=True)
    usuario = Column(String, nullable=True)
    observaciones = Column(Text, nullable=True)
    ventas_total = Column(Float, default=0)
    ventas_efectivo = Column(Float, default=0)
    ventas_transferencia = Column(Float, default=0)
    ventas_tarjeta = Column(Float, default=0)
    ventas_cuenta = Column(Float, default=0)
    cantidad_ventas = Column(Integer, default=0)


class Configuracion(Base):
    __tablename__ = "configuracion"
    clave = Column(String, primary_key=True)
    valor = Column(String, nullable=True)
