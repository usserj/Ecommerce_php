"""Modelo para análisis de reviews con IA."""
from datetime import datetime, timedelta
from app.extensions import db
import json


class AnalisisReview(db.Model):
    """Modelo para almacenar análisis de reviews de productos."""

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

    # Relación con producto (opcional, NULL = análisis general)
    producto = db.relationship('Producto', backref='analisis_reviews', lazy=True)

    def __repr__(self):
        if self.producto_id:
            return f'<AnalisisReview Producto:{self.producto_id}>'
        return '<AnalisisReview General>'

    def get_aspectos_positivos(self):
        """Retorna aspectos positivos parseados como lista."""
        if self.aspectos_positivos:
            try:
                return json.loads(self.aspectos_positivos)
            except:
                return []
        return []

    def set_aspectos_positivos(self, lista):
        """Guarda aspectos positivos como JSON string."""
        if lista:
            self.aspectos_positivos = json.dumps(lista, ensure_ascii=False)
        else:
            self.aspectos_positivos = None

    def get_aspectos_negativos(self):
        """Retorna aspectos negativos parseados como lista."""
        if self.aspectos_negativos:
            try:
                return json.loads(self.aspectos_negativos)
            except:
                return []
        return []

    def set_aspectos_negativos(self, lista):
        """Guarda aspectos negativos como JSON string."""
        if lista:
            self.aspectos_negativos = json.dumps(lista, ensure_ascii=False)
        else:
            self.aspectos_negativos = None

    def get_sentimiento_dominante(self):
        """
        Retorna el sentimiento con mayor porcentaje.

        Returns:
            str: 'positivo', 'neutral' o 'negativo'
        """
        sentimientos = {
            'positivo': self.sentimiento_positivo or 0,
            'neutral': self.sentimiento_neutral or 0,
            'negativo': self.sentimiento_negativo or 0
        }
        return max(sentimientos, key=sentimientos.get)

    def get_color_sentimiento(self):
        """
        Retorna el color Bootstrap según el sentimiento dominante.

        Returns:
            str: 'success', 'warning' o 'danger'
        """
        dominante = self.get_sentimiento_dominante()
        if dominante == 'positivo':
            return 'success'
        elif dominante == 'neutral':
            return 'warning'
        else:
            return 'danger'

    def get_calidad_descripcion(self):
        """
        Retorna descripción textual del score de calidad.

        Returns:
            str: Descripción de calidad
        """
        score = float(self.calidad_score or 0)
        if score >= 9:
            return 'Excelente'
        elif score >= 7:
            return 'Buena'
        elif score >= 5:
            return 'Aceptable'
        elif score >= 3:
            return 'Baja'
        else:
            return 'Muy Baja'

    @staticmethod
    def necesita_actualizacion(producto_id=None):
        """
        Verifica si el análisis necesita actualizarse.

        Args:
            producto_id: ID del producto (None = análisis general)

        Returns:
            bool: True si necesita actualización
        """
        analisis = AnalisisReview.query.filter_by(producto_id=producto_id).first()

        if not analisis:
            return True

        # Actualizar si tiene más de 24 horas
        if datetime.utcnow() - analisis.fecha_analisis > timedelta(hours=24):
            return True

        # Actualizar si hay nuevos comentarios aprobados desde el último análisis
        from app.models.comment import Comentario
        nuevos_comentarios = Comentario.query.filter(
            Comentario.estado == 1,  # estado=1 = aprobado
            Comentario.fecha > analisis.fecha_analisis
        )

        if producto_id:
            nuevos_comentarios = nuevos_comentarios.filter_by(id_producto=producto_id)

        return nuevos_comentarios.count() > 0

    @staticmethod
    def get_analisis_reciente(producto_id=None):
        """
        Obtiene el análisis más reciente de un producto o general.

        Args:
            producto_id: ID del producto (None = análisis general)

        Returns:
            AnalisisReview o None
        """
        return AnalisisReview.query.filter_by(
            producto_id=producto_id
        ).order_by(
            AnalisisReview.fecha_analisis.desc()
        ).first()

    @staticmethod
    def get_estadisticas_generales():
        """
        Obtiene estadísticas generales de todos los análisis.

        Returns:
            dict con estadísticas
        """
        total = AnalisisReview.query.count()
        analisis_recientes = AnalisisReview.query.filter(
            AnalisisReview.fecha_analisis > datetime.utcnow() - timedelta(days=7)
        ).count()

        # Promedio de calidad general
        from sqlalchemy import func
        avg_calidad = db.session.query(
            func.avg(AnalisisReview.calidad_score)
        ).scalar()

        return {
            'total_analisis': total,
            'analisis_recientes_7dias': analisis_recientes,
            'promedio_calidad': float(avg_calidad) if avg_calidad else 0
        }
