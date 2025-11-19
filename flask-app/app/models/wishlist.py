"""Wishlist model."""
from datetime import datetime
from app.extensions import db


class Deseo(db.Model):
    """Wishlist model."""

    __tablename__ = 'deseos'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False, index=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    # Add unique constraint to prevent duplicates
    __table_args__ = (
        db.UniqueConstraint('id_usuario', 'id_producto', name='unique_wishlist_item'),
    )

    def __repr__(self):
        return f'<Deseo User:{self.id_usuario} Product:{self.id_producto}>'
