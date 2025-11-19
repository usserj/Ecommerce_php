"""Notification model."""
from app.extensions import db


class Notificacion(db.Model):
    """Notification counters model for admin dashboard."""

    __tablename__ = 'notificaciones'

    id = db.Column(db.Integer, primary_key=True)
    nuevosUsuarios = db.Column(db.Integer, default=0)
    nuevasVentas = db.Column(db.Integer, default=0)
    nuevasVisitas = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Notificacion {self.id}>'

    @staticmethod
    def get_counters():
        """Get notification counters (singleton)."""
        counters = Notificacion.query.first()
        if not counters:
            counters = Notificacion()
            db.session.add(counters)
            db.session.commit()
        return counters

    @staticmethod
    def increment_new_users():
        """Increment new users counter."""
        counters = Notificacion.get_counters()
        counters.nuevosUsuarios += 1
        db.session.commit()

    @staticmethod
    def increment_new_sales():
        """Increment new sales counter."""
        counters = Notificacion.get_counters()
        counters.nuevasVentas += 1
        db.session.commit()

    @staticmethod
    def increment_new_visits():
        """Increment new visits counter."""
        counters = Notificacion.get_counters()
        counters.nuevasVisitas += 1
        db.session.commit()

    @staticmethod
    def reset_counters():
        """Reset all counters to zero."""
        counters = Notificacion.get_counters()
        counters.nuevosUsuarios = 0
        counters.nuevasVentas = 0
        counters.nuevasVisitas = 0
        db.session.commit()
