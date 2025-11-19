"""Modelo para conversaciones del chatbot de IA."""
from datetime import datetime, timedelta
from app.extensions import db
import json


class ConversacionChatbot(db.Model):
    """Modelo para almacenar conversaciones del chatbot."""

    __tablename__ = 'conversaciones_chatbot'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True, index=True)
    rol = db.Column(db.String(10), nullable=False)  # 'user' o 'assistant'
    mensaje = db.Column(db.Text, nullable=False)
    contexto = db.Column(db.Text, nullable=True)  # JSON string
    fecha = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relación con usuario (opcional)
    usuario = db.relationship('User', backref='conversaciones_chatbot', lazy=True)

    def __repr__(self):
        return f'<ConversacionChatbot {self.session_id} - {self.rol}>'

    def get_contexto(self):
        """Retorna contexto parseado como dict."""
        if self.contexto:
            try:
                return json.loads(self.contexto)
            except:
                return {}
        return {}

    def set_contexto(self, data):
        """Guarda contexto como JSON string."""
        if data:
            self.contexto = json.dumps(data, ensure_ascii=False)
        else:
            self.contexto = None

    @staticmethod
    def get_conversacion(session_id, limit=20):
        """
        Obtiene últimos mensajes de una sesión.

        Args:
            session_id: ID de sesión
            limit: Número máximo de mensajes

        Returns:
            Lista de mensajes ordenados por fecha descendente
        """
        return ConversacionChatbot.query.filter_by(
            session_id=session_id
        ).order_by(
            ConversacionChatbot.fecha.desc()
        ).limit(limit).all()

    @staticmethod
    def limpiar_antiguas(dias=30):
        """
        Elimina conversaciones mayores a X días.

        Args:
            dias: Número de días para mantener conversaciones

        Returns:
            Número de conversaciones eliminadas
        """
        fecha_limite = datetime.utcnow() - timedelta(days=dias)
        count = ConversacionChatbot.query.filter(
            ConversacionChatbot.fecha < fecha_limite
        ).delete()
        db.session.commit()
        return count

    @staticmethod
    def get_estadisticas():
        """
        Obtiene estadísticas generales de las conversaciones.

        Returns:
            dict con estadísticas
        """
        total = ConversacionChatbot.query.count()
        total_usuarios = ConversacionChatbot.query.filter(
            ConversacionChatbot.usuario_id.isnot(None)
        ).distinct(ConversacionChatbot.usuario_id).count()
        total_sesiones = ConversacionChatbot.query.distinct(
            ConversacionChatbot.session_id
        ).count()

        return {
            'total_mensajes': total,
            'total_usuarios': total_usuarios,
            'total_sesiones': total_sesiones
        }
