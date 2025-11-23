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
    precio_total = db.Column(db.Numeric(10, 2))  # Total price including shipping
    estado = db.Column(db.String(20), default=ESTADO_PENDIENTE, index=True)  # Estado del pedido
    tracking = db.Column(db.String(100))  # Número de tracking/seguimiento
    fecha = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    fecha_estado = db.Column(db.DateTime, default=datetime.utcnow)  # Última actualización de estado

    def __repr__(self):
        return f'<Compra {self.id} - User {self.id_usuario}>'

    def get_total(self):
        """Get total amount paid."""
        try:
            return float(self.pago)
        except (ValueError, TypeError):
            return 0.0

    def get_shipping_info(self):
        """Get shipping information."""
        return {
            'direccion': self.direccion,
            'pais': self.pais,
            'envio': self.envio
        }

    def cambiar_estado(self, nuevo_estado):
        """Cambiar el estado del pedido."""
        if nuevo_estado not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido: {nuevo_estado}")

        self.estado = nuevo_estado
        self.fecha_estado = datetime.utcnow()
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
        return estados_display.get(self.estado, self.estado)
