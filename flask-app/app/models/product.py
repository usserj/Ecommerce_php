"""Product model."""
from datetime import datetime
from app.extensions import db


class Producto(db.Model):
    """Product model."""

    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False, index=True)
    id_subcategoria = db.Column(db.Integer, db.ForeignKey('subcategorias.id'), index=True)
    tipo = db.Column(db.String(20), default='fisico')  # fisico, virtual
    ruta = db.Column(db.String(255), unique=True, nullable=False, index=True)
    estado = db.Column(db.Integer, default=1)  # 1=active, 0=inactive
    titulo = db.Column(db.String(255), nullable=False)
    titular = db.Column(db.Text)
    descripcion = db.Column(db.Text)
    multimedia = db.Column(db.JSON)  # List of image URLs
    detalles = db.Column(db.JSON)  # Product specifications
    precio = db.Column(db.Float, nullable=False)
    portada = db.Column(db.String(255))
    vistas = db.Column(db.Integer, default=0)
    ventas = db.Column(db.Integer, default=0)
    vistasGratis = db.Column(db.Integer, default=0)
    ventasGratis = db.Column(db.Integer, default=0)
    ofertadoPorCategoria = db.Column(db.Integer, default=0)
    ofertadoPorSubCategoria = db.Column(db.Integer, default=0)
    oferta = db.Column(db.Integer, default=0)  # 1=on offer, 0=not on offer
    precioOferta = db.Column(db.Float, default=0)
    descuentoOferta = db.Column(db.Integer, default=0)
    imgOferta = db.Column(db.String(255))
    finOferta = db.Column(db.DateTime)
    peso = db.Column(db.Float, default=0)
    entrega = db.Column(db.Float, default=0)
    stock = db.Column(db.Integer, default=0)  # Stock disponible
    stock_minimo = db.Column(db.Integer, default=5)  # Alerta de stock bajo
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    # Use back_populates to avoid backref conflicts
    categoria = db.relationship('Categoria', foreign_keys=[id_categoria])
    subcategoria = db.relationship('Subcategoria', foreign_keys=[id_subcategoria])
    comentarios = db.relationship('Comentario', backref='producto', lazy='dynamic', cascade='all, delete-orphan')
    compras = db.relationship('Compra', backref='producto', lazy='dynamic')
    deseos = db.relationship('Deseo', backref='producto', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Producto {self.titulo}>'

    def get_price(self):
        """Get current price (offer price if available and valid)."""
        if self.oferta == 1 and self.precioOferta > 0:
            if not self.finOferta or self.finOferta > datetime.utcnow():
                return self.precioOferta
        return self.precio

    def get_final_price(self):
        """Get final price (alias for get_price for template compatibility)."""
        return self.get_price()

    def get_discount_percentage(self):
        """Get discount percentage."""
        if self.oferta == 1 and self.descuentoOferta > 0:
            return self.descuentoOferta
        return 0

    @property
    def descuento(self):
        """Alias para descuentoOferta para compatibilidad."""
        return self.descuentoOferta if self.descuentoOferta else 0

    def is_on_offer(self):
        """Check if product is currently on offer."""
        if self.oferta == 1:
            if not self.finOferta or self.finOferta > datetime.utcnow():
                return True
        return False

    def increment_views(self):
        """Increment product views."""
        self.vistas += 1
        db.session.commit()

    def increment_sales(self):
        """Increment product sales."""
        self.ventas += 1
        db.session.commit()

    def get_average_rating(self):
        """Get average rating from comments."""
        from sqlalchemy import func
        from app.models.comment import Comentario
        result = db.session.query(func.avg(Comentario.calificacion)).filter_by(id_producto=self.id).scalar()
        return round(result, 1) if result else 0

    def get_comments_count(self):
        """Get number of comments."""
        return self.comentarios.count()

    def get_multimedia_list(self):
        """Get list of multimedia URLs."""
        if isinstance(self.multimedia, list):
            return self.multimedia
        return []

    def is_physical(self):
        """Check if product is physical."""
        return self.tipo == 'fisico'

    def is_virtual(self):
        """Check if product is virtual."""
        return self.tipo == 'virtual'

    def tiene_stock(self, cantidad=1):
        """Check if product has enough stock."""
        if self.is_virtual():
            return True  # Productos virtuales siempre disponibles
        return self.stock >= cantidad

    def decrementar_stock(self, cantidad):
        """Decrement stock after purchase."""
        if self.is_virtual():
            return True  # Productos virtuales no decrementan stock

        if self.tiene_stock(cantidad):
            self.stock -= cantidad
            db.session.commit()
            return True
        return False

    def incrementar_stock(self, cantidad):
        """Increment stock (for returns or inventory adjustment)."""
        if not self.is_virtual():
            self.stock += cantidad
            db.session.commit()

    def stock_bajo(self):
        """Check if stock is below minimum threshold."""
        if self.is_virtual():
            return False
        return self.stock <= self.stock_minimo

    def agotado(self):
        """Check if product is out of stock."""
        if self.is_virtual():
            return False
        return self.stock == 0
