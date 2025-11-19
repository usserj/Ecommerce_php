"""Settings models (Plantilla, Slide, Banner, Cabecera)."""
from datetime import datetime
from flask import url_for
from app.extensions import db


class Plantilla(db.Model):
    """Template/Theme settings model."""

    __tablename__ = 'plantilla'

    id = db.Column(db.Integer, primary_key=True)
    barraSuperior = db.Column(db.String(50), default='')
    textoSuperior = db.Column(db.Text, default='')
    colorFondo = db.Column(db.String(20), default='#ffffff')
    colorTexto = db.Column(db.String(20), default='#000000')
    logo = db.Column(db.String(255), default='')
    icono = db.Column(db.String(255), default='')
    redesSociales = db.Column(db.JSON)  # Social media links
    apiFacebook = db.Column(db.Text, default='')
    pixelFacebook = db.Column(db.Text, default='')
    googleAnalytics = db.Column(db.Text, default='')
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Plantilla {self.id}>'

    @staticmethod
    def get_settings():
        """Get template settings (singleton)."""
        settings = Plantilla.query.first()
        if not settings:
            settings = Plantilla()
            db.session.add(settings)
            db.session.commit()
        return settings


class Slide(db.Model):
    """Carousel slide model."""

    __tablename__ = 'slide'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    imgFondo = db.Column(db.String(255), nullable=False)
    tipoSlide = db.Column(db.String(50), default='')
    imgProducto = db.Column(db.String(255), default='')
    estiloImgProducto = db.Column(db.Text, default='')
    estiloTextoSlide = db.Column(db.Text, default='')
    titulo1 = db.Column(db.String(255), default='')
    titulo2 = db.Column(db.String(255), default='')
    titulo3 = db.Column(db.String(255), default='')
    boton = db.Column(db.String(100), default='')
    url = db.Column(db.String(255), default='')
    orden = db.Column(db.Integer, default=0)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Slide {self.nombre}>'


class Banner(db.Model):
    """Banner model for category/subcategory promotional images."""

    __tablename__ = 'banner'

    id = db.Column(db.Integer, primary_key=True)
    ruta = db.Column(db.String(255), nullable=False)  # Route (category/subcategory path or 'general')
    tipo = db.Column(db.String(50), nullable=False)  # Type: 'categorias', 'subcategorias', 'general'
    img = db.Column(db.String(255), nullable=False)  # Image filename
    estado = db.Column(db.Integer, default=1)  # 1=active, 0=inactive
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Banner {self.tipo}:{self.ruta}>'

    def is_active(self):
        """Check if banner is active."""
        return self.estado == 1

    def activate(self):
        """Activate banner."""
        self.estado = 1
        db.session.commit()

    def deactivate(self):
        """Deactivate banner."""
        self.estado = 0
        db.session.commit()

    def get_image_url(self):
        """Get full URL for banner image."""
        if self.img.startswith('http'):
            return self.img
        return url_for('static', filename=f'uploads/banners/{self.img}')

    def to_dict(self):
        """Convert banner to dictionary for JSON responses."""
        return {
            'id': self.id,
            'ruta': self.ruta,
            'tipo': self.tipo,
            'img': self.img,
            'img_url': self.get_image_url(),
            'estado': self.estado,
            'activo': self.is_active(),
            'fecha': self.fecha.isoformat() if self.fecha else None
        }

    @staticmethod
    def get_active_banners(tipo=None, ruta=None):
        """Get active banners filtered by type and/or route.

        Args:
            tipo: 'categorias', 'subcategorias', 'general' or None for all
            ruta: Specific route path or None for all

        Returns:
            List of active Banner objects
        """
        query = Banner.query.filter_by(estado=1)

        if tipo:
            query = query.filter_by(tipo=tipo)

        if ruta:
            query = query.filter_by(ruta=ruta)

        return query.order_by(Banner.fecha.desc()).all()

    @staticmethod
    def get_banners_for_category(categoria_ruta):
        """Get active banners for a specific category.

        Args:
            categoria_ruta: Category route path (e.g., 'electronics')

        Returns:
            List of active banners for the category
        """
        return Banner.get_active_banners(tipo='categorias', ruta=categoria_ruta)

    @staticmethod
    def get_banners_for_subcategory(subcategoria_ruta):
        """Get active banners for a specific subcategory.

        Args:
            subcategoria_ruta: Subcategory route path (e.g., 'laptops')

        Returns:
            List of active banners for the subcategory
        """
        return Banner.get_active_banners(tipo='subcategorias', ruta=subcategoria_ruta)

    @staticmethod
    def get_general_banners():
        """Get active general banners (shown everywhere).

        Returns:
            List of active general banners
        """
        return Banner.get_active_banners(tipo='general', ruta='general')


class Cabecera(db.Model):
    """Header/SEO metadata model."""

    __tablename__ = 'cabeceras'

    id = db.Column(db.Integer, primary_key=True)
    ruta = db.Column(db.String(255), unique=True, nullable=False, index=True)
    titulo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, default='')
    palabrasClaves = db.Column(db.Text, default='')
    portada = db.Column(db.String(255), default='')
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Cabecera {self.ruta}>'

    @staticmethod
    def get_or_create(ruta, titulo, descripcion='', palabras_claves='', portada=''):
        """Get or create header metadata for a route."""
        cabecera = Cabecera.query.filter_by(ruta=ruta).first()
        if not cabecera:
            cabecera = Cabecera(
                ruta=ruta,
                titulo=titulo,
                descripcion=descripcion,
                palabrasClaves=palabras_claves,
                portada=portada
            )
            db.session.add(cabecera)
            db.session.commit()
        return cabecera
