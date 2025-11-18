"""Category and Subcategory models."""
from datetime import datetime
from app.extensions import db


class Categoria(db.Model):
    """Category model."""

    __tablename__ = 'categorias'

    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(100), nullable=False)
    ruta = db.Column(db.String(255), unique=True, nullable=False, index=True)
    estado = db.Column(db.Integer, default=1)  # 1=active, 0=inactive
    oferta = db.Column(db.Integer, default=0)
    precioOferta = db.Column(db.Float, default=0)
    descuentoOferta = db.Column(db.Integer, default=0)
    imgOferta = db.Column(db.String(255))
    finOferta = db.Column(db.DateTime)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    subcategorias = db.relationship('Subcategoria', backref='categoria', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Categoria {self.categoria}>'

    def get_products_count(self):
        """Get number of products in this category."""
        from app.models.product import Producto
        return Producto.query.filter_by(id_categoria=self.id, estado=1).count()

    def is_on_offer(self):
        """Check if category is on offer."""
        if self.oferta == 1:
            if not self.finOferta or self.finOferta > datetime.utcnow():
                return True
        return False


class Subcategoria(db.Model):
    """Subcategory model."""

    __tablename__ = 'subcategorias'

    id = db.Column(db.Integer, primary_key=True)
    subcategoria = db.Column(db.String(100), nullable=False)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False, index=True)
    ruta = db.Column(db.String(255), unique=True, nullable=False, index=True)
    estado = db.Column(db.Integer, default=1)
    ofertadoPorCategoria = db.Column(db.Integer, default=0)
    oferta = db.Column(db.Integer, default=0)
    precioOferta = db.Column(db.Float, default=0)
    descuentoOferta = db.Column(db.Integer, default=0)
    imgOferta = db.Column(db.String(255))
    finOferta = db.Column(db.DateTime)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Subcategoria {self.subcategoria}>'

    def get_products_count(self):
        """Get number of products in this subcategory."""
        from app.models.product import Producto
        return Producto.query.filter_by(id_subcategoria=self.id, estado=1).count()

    def is_on_offer(self):
        """Check if subcategory is on offer."""
        if self.oferta == 1:
            if not self.finOferta or self.finOferta > datetime.utcnow():
                return True
        return False
