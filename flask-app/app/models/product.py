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
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    categoria = db.relationship('Categoria', backref='productos')
    subcategoria = db.relationship('Subcategoria', backref='productos')
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

    def get_discount_percentage(self):
        """Get discount percentage."""
        if self.oferta == 1 and self.descuentoOferta > 0:
            return self.descuentoOferta
        return 0

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
        result = db.session.query(func.avg(self.comentarios.filter_by().calificacion)).scalar()
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
