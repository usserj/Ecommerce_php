"""Order/Purchase model."""
from datetime import datetime
from app.extensions import db


class Compra(db.Model):
    """Purchase/Order model."""

    __tablename__ = 'compras'

    # Estados posibles de una compra
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_PROCESANDO = 'procesando'
    ESTADO_ENVIADO = 'enviado'
    ESTADO_ENTREGADO = 'entregado'
    ESTADO_CANCELADO = 'cancelado'

    ESTADOS_VALIDOS = [
        ESTADO_PENDIENTE,
        ESTADO_PROCESANDO,
        ESTADO_ENVIADO,
        ESTADO_ENTREGADO,
        ESTADO_CANCELADO
    ]

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False, index=True)
    envio = db.Column(db.Integer, default=0)  # Shipping method/cost
    metodo = db.Column(db.String(50), nullable=False)  # paypal, payu, etc.
    email = db.Column(db.String(120), nullable=False)
    direccion = db.Column(db.Text, nullable=False)
    pais = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, default=1)
    detalle = db.Column(db.Text)  # Additional details (JSON or text)
    pago = db.Column(db.String(255), nullable=False)  # Payment amount/details
    fecha = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Columnas de tracking y estado
    precio_total = db.Column(db.Numeric(10, 2))  # Total price including shipping
    estado = db.Column(db.String(20), default=ESTADO_PENDIENTE, index=True)
    tracking = db.Column(db.String(100))
    fecha_estado = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Compra {self.id} - User {self.id_usuario}>'

    # Transiciones de estado válidas
    TRANSICIONES_VALIDAS = {
        ESTADO_PENDIENTE: [ESTADO_PROCESANDO, ESTADO_CANCELADO],
        ESTADO_PROCESANDO: [ESTADO_ENVIADO, ESTADO_CANCELADO],
        ESTADO_ENVIADO: [ESTADO_ENTREGADO],
        ESTADO_ENTREGADO: [],  # Estado final
        ESTADO_CANCELADO: []   # Estado final
    }

    def get_total(self):
        """Get total amount paid including shipping."""
        try:
            if self.precio_total:
                return float(self.precio_total)
            # Fallback: calculate from pago + envio
            total = float(self.pago) + float(self.envio or 0)
            return total
        except (ValueError, TypeError):
            return 0.0

    def get_shipping_info(self):
        """Get shipping information."""
        return {
            'direccion': self.direccion,
            'pais': self.pais,
            'envio': self.envio
        }

    def cambiar_estado(self, nuevo_estado, razon=None):
        """Cambiar el estado del pedido con validación de transiciones."""
        if nuevo_estado not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido: {nuevo_estado}")

        # Validar transición de estado
        transiciones_permitidas = self.TRANSICIONES_VALIDAS.get(self.estado, [])
        if nuevo_estado not in transiciones_permitidas:
            raise ValueError(
                f"Transición de estado inválida: {self.estado} → {nuevo_estado}. "
                f"Transiciones permitidas desde {self.estado}: {', '.join(transiciones_permitidas) if transiciones_permitidas else 'ninguna'}"
            )

        estado_anterior = self.estado
        self.estado = nuevo_estado
        self.fecha_estado = datetime.utcnow()

        # Si se cancela una orden, restaurar el stock
        if nuevo_estado == self.ESTADO_CANCELADO and estado_anterior != self.ESTADO_CANCELADO:
            self.restaurar_stock(razon or f"Orden cancelada desde estado {estado_anterior}")

        db.session.commit()

    def restaurar_stock(self, razon="Orden cancelada"):
        """Restaurar stock cuando se cancela una orden."""
        from app.models.product import Producto

        producto = Producto.query.get(self.id_producto)
        if not producto or producto.is_virtual():
            return  # No restaurar stock de productos virtuales

        stock_anterior = producto.stock
        producto.stock += self.cantidad
        stock_nuevo = producto.stock

        # Registrar movimiento de stock
        try:
            from app.models.stock_movement import StockMovement
            movimiento = StockMovement.registrar_cancelacion(
                producto_id=self.id_producto,
                orden_id=self.id,
                cantidad=self.cantidad,
                stock_anterior=stock_anterior,
                stock_nuevo=stock_nuevo,
                razon=razon
            )
            db.session.add(movimiento)
        except ImportError:
            # Si el modelo StockMovement no existe aún, solo actualizar stock
            pass

        db.session.commit()

    def es_pendiente(self):
        """Check if order is pending."""
        return self.estado == self.ESTADO_PENDIENTE

    def es_procesando(self):
        """Check if order is being processed."""
        return self.estado == self.ESTADO_PROCESANDO

    def es_enviado(self):
        """Check if order has been shipped."""
        return self.estado == self.ESTADO_ENVIADO

    def es_entregado(self):
        """Check if order has been delivered."""
        return self.estado == self.ESTADO_ENTREGADO

    def es_cancelado(self):
        """Check if order is cancelled."""
        return self.estado == self.ESTADO_CANCELADO

    def puede_cancelar(self):
        """Check if order can be cancelled."""
        return self.estado in [self.ESTADO_PENDIENTE, self.ESTADO_PROCESANDO]

    def get_estado_display(self):
        """Get human-readable estado."""
        estados_display = {
            self.ESTADO_PENDIENTE: 'Pendiente',
            self.ESTADO_PROCESANDO: 'Procesando',
            self.ESTADO_ENVIADO: 'Enviado',
            self.ESTADO_ENTREGADO: 'Entregado',
            self.ESTADO_CANCELADO: 'Cancelado'
        }
        return estados_display.get(self.estado, 'Completado')
