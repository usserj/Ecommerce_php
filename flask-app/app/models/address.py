"""User address model for saved shipping addresses."""
from datetime import datetime
from app.extensions import db


class Address(db.Model):
    """User saved shipping address."""

    __tablename__ = 'addresses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    nombre = db.Column(db.String(100), nullable=False)  # Address name (e.g., "Casa", "Oficina")
    nombre_completo = db.Column(db.String(200), nullable=False)  # Full recipient name
    direccion = db.Column(db.Text, nullable=False)  # Street address
    ciudad = db.Column(db.String(100), nullable=False)
    provincia = db.Column(db.String(100), nullable=False)
    codigo_postal = db.Column(db.String(20))
    pais = db.Column(db.String(100), default='Ecuador')
    telefono = db.Column(db.String(20))
    is_default = db.Column(db.Boolean, default=False)  # Default shipping address
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Address {self.nombre} - User {self.user_id}>'

    def set_as_default(self):
        """Set this address as default and unset others."""
        # Unset all other defaults for this user
        Address.query.filter_by(user_id=self.user_id).update({'is_default': False})
        self.is_default = True
        db.session.commit()

    def get_full_address(self):
        """Get formatted full address."""
        parts = [
            self.direccion,
            self.ciudad,
            self.provincia,
            self.codigo_postal if self.codigo_postal else None,
            self.pais
        ]
        return ', '.join(filter(None, parts))

    @classmethod
    def get_user_addresses(cls, user_id):
        """Get all addresses for a user."""
        return cls.query.filter_by(user_id=user_id).order_by(
            cls.is_default.desc(),
            cls.fecha_creacion.desc()
        ).all()

    @classmethod
    def get_default_address(cls, user_id):
        """Get user's default address."""
        return cls.query.filter_by(user_id=user_id, is_default=True).first()
