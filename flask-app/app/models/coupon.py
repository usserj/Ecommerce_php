"""Coupon/Discount model."""
from datetime import datetime
from app.extensions import db


class Cupon(db.Model):
    """Coupon model for discounts."""

    __tablename__ = 'cupones'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    tipo = db.Column(db.String(20), nullable=False)  # 'porcentaje' or 'fijo'
    valor = db.Column(db.Float, nullable=False)  # Percentage (0-100) or fixed amount
    descripcion = db.Column(db.Text)
    usos_maximos = db.Column(db.Integer, default=0)  # 0 = unlimited
    usos_actuales = db.Column(db.Integer, default=0)
    monto_minimo = db.Column(db.Float, default=0)  # Minimum purchase amount
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin = db.Column(db.DateTime)
    estado = db.Column(db.Integer, default=1)  # 1=active, 0=inactive
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Cupon {self.codigo}>'

    def is_valid(self, monto_compra=0):
        """Check if coupon is valid for use."""
        now = datetime.utcnow()

        # Check if active
        if self.estado != 1:
            return False, "El cupón está desactivado."

        # Check start date
        if self.fecha_inicio and self.fecha_inicio > now:
            return False, "El cupón aún no está disponible."

        # Check expiration
        if self.fecha_fin and self.fecha_fin < now:
            return False, "El cupón ha expirado."

        # Check usage limit
        if self.usos_maximos > 0 and self.usos_actuales >= self.usos_maximos:
            return False, "El cupón ha alcanzado el límite de usos."

        # Check minimum purchase amount
        if self.monto_minimo > 0 and monto_compra < self.monto_minimo:
            return False, f"El monto mínimo de compra es ${self.monto_minimo:.2f}"

        return True, "Cupón válido"

    def calculate_discount(self, monto):
        """Calculate discount amount based on coupon type."""
        if self.tipo == 'porcentaje':
            # Percentage discount
            descuento = (monto * self.valor) / 100
        elif self.tipo == 'fijo':
            # Fixed amount discount
            descuento = self.valor
        else:
            descuento = 0

        # Discount cannot exceed purchase amount
        return min(descuento, monto)

    def increment_usage(self):
        """Increment the usage counter."""
        self.usos_actuales += 1
        db.session.commit()
