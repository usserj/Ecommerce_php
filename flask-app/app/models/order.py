"""Order/Purchase model."""
from datetime import datetime
from app.extensions import db


class Compra(db.Model):
    """Purchase/Order model."""

    __tablename__ = 'compras'

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
