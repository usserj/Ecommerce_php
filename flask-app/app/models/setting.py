"""Settings models (Plantilla, Slide, Banner, Cabecera)."""
from datetime import datetime
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
    """Banner model for promotional banners by category/subcategory."""

    __tablename__ = 'banner'

    id = db.Column(db.Integer, primary_key=True)
    ruta = db.Column(db.String(255), nullable=False, index=True)  # Route (category/subcategory)
    tipo = db.Column(db.String(50), nullable=False)  # 'categoria', 'subcategoria', 'general'
    img = db.Column(db.String(255), nullable=False)  # Image path
    estado = db.Column(db.Integer, default=1)  # 1=active, 0=inactive
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Banner {self.id}: {self.tipo} - {self.ruta}>'

    @property
    def is_active(self):
        """Check if banner is active."""
        return self.estado == 1

    def toggle_status(self):
        """Toggle banner status."""
        self.estado = 1 if self.estado == 0 else 0
        db.session.commit()
        return self.estado

    @staticmethod
    def get_by_route(ruta):
        """Get active banner by route."""
        return Banner.query.filter_by(ruta=ruta, estado=1).first()

    @staticmethod
    def get_all_active():
        """Get all active banners."""
        return Banner.query.filter_by(estado=1).order_by(Banner.fecha.desc()).all()

    @staticmethod
    def get_all():
        """Get all banners."""
        return Banner.query.order_by(Banner.fecha.desc()).all()

    def to_dict(self):
        """Convert banner to dictionary."""
        return {
            'id': self.id,
            'ruta': self.ruta,
            'tipo': self.tipo,
            'img': self.img,
            'estado': self.estado,
            'is_active': self.is_active,
            'fecha': self.fecha.strftime('%Y-%m-%d %H:%M:%S') if self.fecha else None
        }


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
