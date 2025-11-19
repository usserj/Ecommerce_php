"""Modelo para análisis de reviews con IA."""
from datetime import datetime, timedelta
from app.extensions import db
import json


class AnalisisReview(db.Model):
    """Modelo para almacenar análisis de sentimientos de reviews."""

    __tablename__ = 'analisis_reviews'

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=True, index=True)
    sentimiento_positivo = db.Column(db.Integer, default=0)
    sentimiento_neutral = db.Column(db.Integer, default=0)
    sentimiento_negativo = db.Column(db.Integer, default=0)
    aspectos_positivos = db.Column(db.Text, nullable=True)  # JSON string
    aspectos_negativos = db.Column(db.Text, nullable=True)  # JSON string
    calidad_score = db.Column(db.Numeric(3, 1))
    recomendacion = db.Column(db.Text)
    fecha_analisis = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    total_reviews = db.Column(db.Integer)

    def __repr__(self):
        producto_info = f"Producto {self.producto_id}" if self.producto_id else "General"
        return f'<AnalisisReview {producto_info}>'

    def get_aspectos_positivos(self):
        """Retorna aspectos positivos como lista."""
        if self.aspectos_positivos:
            try:
                return json.loads(self.aspectos_positivos)
            except:
                return []
        return []

    def set_aspectos_positivos(self, lista):
        """Guarda aspectos positivos como JSON."""
        self.aspectos_positivos = json.dumps(lista, ensure_ascii=False)

    def get_aspectos_negativos(self):
        """Retorna aspectos negativos como lista."""
        if self.aspectos_negativos:
            try:
                return json.loads(self.aspectos_negativos)
            except:
                return []
        return []

    def set_aspectos_negativos(self, lista):
        """Guarda aspectos negativos como JSON."""
        self.aspectos_negativos = json.dumps(lista, ensure_ascii=False)

    def get_sentimiento_dominante(self):
        """Retorna el sentimiento con mayor porcentaje."""
        sentimientos = {
            'positivo': self.sentimiento_positivo,
            'neutral': self.sentimiento_neutral,
            'negativo': self.sentimiento_negativo
        }
        return max(sentimientos, key=sentimientos.get)

    @staticmethod
    def necesita_actualizacion(producto_id=None):
        """Verifica si el análisis necesita actualizarse."""
        analisis = AnalisisReview.query.filter_by(producto_id=producto_id).first()

        if not analisis:
            return True

        # Actualizar si tiene más de 24 horas
        if datetime.utcnow() - analisis.fecha_analisis > timedelta(hours=24):
            return True

        # Actualizar si hay nuevos comentarios aprobados desde el último análisis
        from app.models.comment import Comentario
        nuevos_comentarios = Comentario.query.filter(
            Comentario.estado == Comentario.ESTADO_APROBADO,
            Comentario.fecha > analisis.fecha_analisis
        )

        if producto_id:
            nuevos_comentarios = nuevos_comentarios.filter_by(id_producto=producto_id)

        return nuevos_comentarios.count() > 0
