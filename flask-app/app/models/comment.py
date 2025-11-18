"""Comment/Review model."""
from datetime import datetime
from app.extensions import db


class Comentario(db.Model):
    """Comment/Review model."""

    __tablename__ = 'comentarios'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False, index=True)
    calificacion = db.Column(db.Float, default=0)  # Rating (e.g., 1-5)
    comentario = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Comentario {self.id} - Product {self.id_producto}>'

    def get_rating_stars(self):
        """Get rating as integer stars (1-5)."""
        return int(round(self.calificacion))
