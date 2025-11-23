"""Stock movement audit model."""
from datetime import datetime
from app.extensions import db


class StockMovement(db.Model):
    """Auditoría de movimientos de inventario."""

    __tablename__ = 'stock_movements'

    # Tipos de movimiento
    TIPO_VENTA = 'venta'
    TIPO_CANCELACION = 'cancelacion'
    TIPO_AJUSTE = 'ajuste'
    TIPO_DEVOLUCION = 'devolucion'

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False, index=True)
    orden_id = db.Column(db.Integer, db.ForeignKey('compras.id'), index=True)
    tipo = db.Column(db.String(20), nullable=False, index=True)
    cantidad = db.Column(db.Integer, nullable=False)
    stock_anterior = db.Column(db.Integer, nullable=False)
    stock_nuevo = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    razon = db.Column(db.Text)

    def __repr__(self):
        return f'<StockMovement {self.tipo} - Producto {self.producto_id} - {self.cantidad} unidades>'

    @staticmethod
    def registrar_venta(producto_id, orden_id, cantidad, stock_anterior, stock_nuevo, razon=None):
        """Registrar venta de producto."""
        movimiento = StockMovement(
            producto_id=producto_id,
            orden_id=orden_id,
            tipo=StockMovement.TIPO_VENTA,
            cantidad=-cantidad,  # Negativo porque se resta
            stock_anterior=stock_anterior,
            stock_nuevo=stock_nuevo,
            razon=razon or 'Venta confirmada'
        )
        return movimiento

    @staticmethod
    def registrar_cancelacion(producto_id, orden_id, cantidad, stock_anterior, stock_nuevo, razon=None):
        """Registrar cancelación de orden y restauración de stock."""
        movimiento = StockMovement(
            producto_id=producto_id,
            orden_id=orden_id,
            tipo=StockMovement.TIPO_CANCELACION,
            cantidad=cantidad,  # Positivo porque se suma
            stock_anterior=stock_anterior,
            stock_nuevo=stock_nuevo,
            razon=razon or 'Orden cancelada - Stock restaurado'
        )
        return movimiento

    @staticmethod
    def registrar_ajuste(producto_id, cantidad, stock_anterior, stock_nuevo, razon, usuario_id=None):
        """Registrar ajuste manual de stock."""
        movimiento = StockMovement(
            producto_id=producto_id,
            orden_id=None,
            tipo=StockMovement.TIPO_AJUSTE,
            cantidad=cantidad,
            stock_anterior=stock_anterior,
            stock_nuevo=stock_nuevo,
            razon=razon,
            usuario_id=usuario_id
        )
        return movimiento

    @staticmethod
    def registrar_devolucion(producto_id, orden_id, cantidad, stock_anterior, stock_nuevo, razon=None):
        """Registrar devolución de producto."""
        movimiento = StockMovement(
            producto_id=producto_id,
            orden_id=orden_id,
            tipo=StockMovement.TIPO_DEVOLUCION,
            cantidad=cantidad,  # Positivo porque se suma
            stock_anterior=stock_anterior,
            stock_nuevo=stock_nuevo,
            razon=razon or 'Producto devuelto'
        )
        return movimiento

    def get_tipo_display(self):
        """Get human-readable tipo."""
        tipos_display = {
            self.TIPO_VENTA: 'Venta',
            self.TIPO_CANCELACION: 'Cancelación',
            self.TIPO_AJUSTE: 'Ajuste Manual',
            self.TIPO_DEVOLUCION: 'Devolución'
        }
        return tipos_display.get(self.tipo, self.tipo)

    @classmethod
    def get_movimientos_producto(cls, producto_id, limit=50):
        """Obtener últimos movimientos de un producto."""
        return cls.query.filter_by(
            producto_id=producto_id
        ).order_by(
            cls.fecha.desc()
        ).limit(limit).all()

    @classmethod
    def get_movimientos_orden(cls, orden_id):
        """Obtener movimientos relacionados a una orden."""
        return cls.query.filter_by(orden_id=orden_id).all()
