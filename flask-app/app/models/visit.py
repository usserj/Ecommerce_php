"""Visit tracking models."""
from datetime import datetime
from app.extensions import db


class VisitaPais(db.Model):
    """Visit tracking by country model."""

    __tablename__ = 'visitaspaises'

    id = db.Column(db.Integer, primary_key=True)
    pais = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(10), nullable=False)
    cantidad = db.Column(db.Integer, default=0)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<VisitaPais {self.pais} - {self.cantidad}>'

    @staticmethod
    def increment_visit(pais, codigo):
        """Increment visit counter for a country."""
        visita = VisitaPais.query.filter_by(pais=pais, codigo=codigo).first()
        if visita:
            visita.cantidad += 1
            visita.fecha = datetime.utcnow()
        else:
            visita = VisitaPais(pais=pais, codigo=codigo, cantidad=1)
            db.session.add(visita)
        db.session.commit()
        return visita


class VisitaPersona(db.Model):
    """Visit tracking by IP model."""

    __tablename__ = 'visitaspersonas'

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50), nullable=False, unique=True, index=True)
    pais = db.Column(db.String(100), default='')
    visitas = db.Column(db.Integer, default=0)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<VisitaPersona {self.ip} - {self.visitas}>'

    @staticmethod
    def track_visit(ip, pais=''):
        """Track visit by IP address."""
        visita = VisitaPersona.query.filter_by(ip=ip).first()
        if visita:
            visita.visitas += 1
            visita.fecha = datetime.utcnow()
            if pais:
                visita.pais = pais
        else:
            visita = VisitaPersona(ip=ip, pais=pais, visitas=1)
            db.session.add(visita)
        db.session.commit()
        return visita

    @staticmethod
    def get_total_visits():
        """Get total number of visits."""
        from sqlalchemy import func
        result = db.session.query(func.sum(VisitaPersona.visitas)).scalar()
        return result or 0

    @staticmethod
    def get_unique_visitors():
        """Get number of unique visitors."""
        return VisitaPersona.query.count()
