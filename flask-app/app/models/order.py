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

    # TEMPORARY: Commented out until migration is run
    # Uncomment these after running: python run_migration.py
    # precio_total = db.Column(db.Numeric(10, 2))  # Total price including shipping
    # estado = db.Column(db.String(20), default=ESTADO_PENDIENTE, index=True)
    # tracking = db.Column(db.String(100))
    # fecha_estado = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Compra {self.id} - User {self.id_usuario}>'

    # Fallback properties for columns that may not exist in DB yet
    @property
    def estado(self):
        """Get order status with fallback."""
        # Try to get from database column if it exists
        try:
            return self.__dict__.get('estado', self.ESTADO_ENTREGADO)
        except:
            # If column doesn't exist, assume delivered for old orders
            return self.ESTADO_ENTREGADO

    @estado.setter
    def estado(self, value):
        """Set order status."""
        self.__dict__['estado'] = value

    @property
    def tracking(self):
        """Get tracking number with fallback."""
        return self.__dict__.get('tracking', None)

    @tracking.setter
    def tracking(self, value):
        """Set tracking number."""
        self.__dict__['tracking'] = value

    @property
    def fecha_estado(self):
        """Get status update date with fallback."""
        return self.__dict__.get('fecha_estado', self.fecha)

    @fecha_estado.setter
    def fecha_estado(self, value):
        """Set status update date."""
        self.__dict__['fecha_estado'] = value

    def get_total(self):
        """Get total amount paid including shipping."""
        try:
            # Try precio_total first if it exists
            if hasattr(self, 'precio_total') and self.precio_total:
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
        return estados_display.get(self.estado, 'Completado')
