"""Internal messaging model."""
from datetime import datetime
from app.extensions import db


class Mensaje(db.Model):
    """Internal messaging system for admin-user communication."""

    __tablename__ = 'mensajes'

    id = db.Column(db.Integer, primary_key=True)

    # Sender and recipient (can be admin or user)
    remitente_tipo = db.Column(db.String(20), nullable=False)  # 'admin' or 'user'
    remitente_id = db.Column(db.Integer, nullable=False)
    destinatario_tipo = db.Column(db.String(20), nullable=False)  # 'admin' or 'user'
    destinatario_id = db.Column(db.Integer, nullable=False)

    # Message content
    asunto = db.Column(db.String(255), nullable=False)
    contenido = db.Column(db.Text, nullable=False)

    # Status
    leido = db.Column(db.Boolean, default=False)
    fecha_leido = db.Column(db.DateTime, nullable=True)

    # Reply reference
    mensaje_padre_id = db.Column(db.Integer, db.ForeignKey('mensajes.id'), nullable=True)

    # Timestamps
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    respuestas = db.relationship(
        'Mensaje',
        backref=db.backref('mensaje_padre', remote_side=[id]),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Mensaje {self.id}: {self.asunto[:30]}>'

    def marcar_como_leido(self):
        """Mark message as read."""
        if not self.leido:
            self.leido = True
            self.fecha_leido = datetime.utcnow()
            db.session.commit()

    def get_remitente_nombre(self):
        """Get sender name."""
        if self.remitente_tipo == 'admin':
            from app.models.admin import Administrador
            admin = Administrador.query.get(self.remitente_id)
            return admin.nombre if admin else 'Admin (eliminado)'
        else:
            from app.models.user import User
            user = User.query.get(self.remitente_id)
            return user.nombre if user else 'Usuario (eliminado)'

    def get_destinatario_nombre(self):
        """Get recipient name."""
        if self.destinatario_tipo == 'admin':
            from app.models.admin import Administrador
            admin = Administrador.query.get(self.destinatario_id)
            return admin.nombre if admin else 'Admin (eliminado)'
        else:
            from app.models.user import User
            user = User.query.get(self.destinatario_id)
            return user.nombre if user else 'Usuario (eliminado)'

    def get_remitente_email(self):
        """Get sender email."""
        if self.remitente_tipo == 'admin':
            from app.models.admin import Administrador
            admin = Administrador.query.get(self.remitente_id)
            return admin.email if admin else ''
        else:
            from app.models.user import User
            user = User.query.get(self.remitente_id)
            return user.email if user else ''

    @staticmethod
    def contar_no_leidos(destinatario_tipo, destinatario_id):
        """Count unread messages for a recipient."""
        return Mensaje.query.filter_by(
            destinatario_tipo=destinatario_tipo,
            destinatario_id=destinatario_id,
            leido=False
        ).count()

    @staticmethod
    def enviar_mensaje(remitente_tipo, remitente_id, destinatario_tipo, destinatario_id, asunto, contenido, mensaje_padre_id=None):
        """Send a new message."""
        mensaje = Mensaje(
            remitente_tipo=remitente_tipo,
            remitente_id=remitente_id,
            destinatario_tipo=destinatario_tipo,
            destinatario_id=destinatario_id,
            asunto=asunto,
            contenido=contenido,
            mensaje_padre_id=mensaje_padre_id
        )
        db.session.add(mensaje)
        db.session.commit()
        return mensaje
