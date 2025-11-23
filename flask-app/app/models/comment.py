"""Comment/Review model."""
from datetime import datetime
from app.extensions import db


class Comentario(db.Model):
    """Comment/Review model."""

    __tablename__ = 'comentarios'

    # Estados de moderación
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_APROBADO = 'aprobado'
    ESTADO_RECHAZADO = 'rechazado'

    ESTADOS_VALIDOS = [ESTADO_PENDIENTE, ESTADO_APROBADO, ESTADO_RECHAZADO]

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False, index=True)
    calificacion = db.Column(db.Float, default=0)  # Rating (e.g., 1-5)
    comentario = db.Column(db.Text, nullable=False)
    estado = db.Column(db.String(20), default=ESTADO_APROBADO, index=True)  # Estado de moderación
    respuesta_admin = db.Column(db.Text, nullable=True)  # Admin response
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_moderacion = db.Column(db.DateTime, nullable=True)  # Moderation date
    helpful_votes = db.Column(db.Integer, default=0)  # Number of helpful votes
    images = db.Column(db.Text, nullable=True)  # JSON list of image URLs

    def __repr__(self):
        return f'<Comentario {self.id} - Product {self.id_producto}>'

    def get_rating_stars(self):
        """Get rating as integer stars (1-5)."""
        return int(round(self.calificacion))

    def aprobar(self):
        """Approve comment."""
        self.estado = self.ESTADO_APROBADO
        self.fecha_moderacion = datetime.utcnow()
        db.session.commit()

    def rechazar(self):
        """Reject comment."""
        self.estado = self.ESTADO_RECHAZADO
        self.fecha_moderacion = datetime.utcnow()
        db.session.commit()

    def es_aprobado(self):
        """Check if comment is approved."""
        return self.estado == self.ESTADO_APROBADO

    def es_pendiente(self):
        """Check if comment is pending."""
        return self.estado == self.ESTADO_PENDIENTE

    def es_rechazado(self):
        """Check if comment is rejected."""
        return self.estado == self.ESTADO_RECHAZADO

    def get_estado_badge(self):
        """Get Bootstrap badge class for status."""
        badges = {
            self.ESTADO_APROBADO: 'success',
            self.ESTADO_PENDIENTE: 'warning',
            self.ESTADO_RECHAZADO: 'danger'
        }
        return badges.get(self.estado, 'secondary')

    def get_estado_display(self):
        """Get human-readable status."""
        estados = {
            self.ESTADO_APROBADO: 'Aprobado',
            self.ESTADO_PENDIENTE: 'Pendiente',
            self.ESTADO_RECHAZADO: 'Rechazado'
        }
        return estados.get(self.estado, self.estado)

    def increment_helpful_votes(self):
        """Increment helpful votes counter."""
        self.helpful_votes = (self.helpful_votes or 0) + 1
        db.session.commit()

    def get_images_list(self):
        """Get list of image URLs from JSON."""
        if not self.images:
            return []
        try:
            import json
            return json.loads(self.images)
        except:
            return []

    def add_image(self, image_url):
        """Add image URL to review."""
        import json
        images = self.get_images_list()
        images.append(image_url)
        self.images = json.dumps(images)
        db.session.commit()
