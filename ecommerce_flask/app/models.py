"""
Modelos SQLAlchemy - Ecommerce Flask
Migrados desde PHP/MySQL a Python/Flask

16 Modelos correspondientes a las 16 tablas del proyecto PHP:
1. Usuario
2. Administrador
3. Producto
4. Categoria
5. Subcategoria
6. Compra
7. Deseo
8. Banner
9. Slide
10. Cabecera
11. Comercio
12. Notificacion
13. Visita
14. Comentario
15. Oferta (integrada en Producto/Categoria/Subcategoria)
16. Multimedia (integrada en Producto como JSON)
"""
from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from passlib.hash import bcrypt
import json


# Mixin para timestamps
class TimestampMixin:
    """Agrega campos de timestamp a los modelos"""
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


# ============================================================================
# MODELO 1: Usuario (tabla usuarios)
# ============================================================================
class Usuario(UserMixin, TimestampMixin, db.Model):
    """
    Modelo de Usuario (clientes de la tienda)
    Migrado desde: backend/modelos/usuarios.modelo.php
    """
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255))  # NULL para usuarios de redes sociales
    modo = db.Column(db.String(20), default='directo')  # directo, google, facebook
    foto = db.Column(db.String(255))
    verificacion = db.Column(db.Integer, default=1)  # 0=verificado, 1=pendiente
    email_encriptado = db.Column(db.String(255))  # Token de verificación
    direccion = db.Column(db.Text)
    telefono = db.Column(db.String(20))
    pais = db.Column(db.String(50))

    # Relaciones
    compras = db.relationship('Compra', backref='usuario', lazy='dynamic', cascade='all, delete-orphan')
    deseos = db.relationship('Deseo', backref='usuario', lazy='dynamic', cascade='all, delete-orphan')
    comentarios = db.relationship('Comentario', backref='usuario', lazy='dynamic')

    def set_password(self, password):
        """Encripta y guarda la contraseña (equivalente a crypt() en PHP)"""
        self.password = bcrypt.hash(password)

    def check_password(self, password):
        """Verifica la contraseña"""
        if not self.password:
            return False
        return bcrypt.verify(password, self.password)

    @property
    def is_verified(self):
        """Retorna True si el email está verificado"""
        return self.verificacion == 0

    def to_dict(self):
        """Serializa el usuario a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'foto': self.foto,
            'modo': self.modo,
            'verificado': self.is_verified,
            'fecha': self.fecha.isoformat()
        }

    def __repr__(self):
        return f'<Usuario {self.email}>'


# ============================================================================
# MODELO 2: Administrador (tabla administradores)
# ============================================================================
class Administrador(UserMixin, TimestampMixin, db.Model):
    """
    Modelo de Administrador (usuarios del panel backend)
    Migrado desde: backend/modelos/administradores.modelo.php
    """
    __tablename__ = 'administradores'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    usuario = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    foto = db.Column(db.String(255))
    perfil = db.Column(db.String(50), default='vendedor')  # admin, vendedor, etc
    estado = db.Column(db.Integer, default=1)  # 1=activo, 0=inactivo

    def set_password(self, password):
        """Encripta y guarda la contraseña"""
        self.password = bcrypt.hash(password)

    def check_password(self, password):
        """Verifica la contraseña"""
        return bcrypt.verify(password, self.password)

    @property
    def is_active(self):
        """Retorna True si el administrador está activo"""
        return self.estado == 1

    def __repr__(self):
        return f'<Administrador {self.usuario}>'


# ============================================================================
# MODELO 3: Categoria (tabla categorias)
# ============================================================================
class Categoria(TimestampMixin, db.Model):
    """
    Modelo de Categoría
    Migrado desde: backend/modelos/categorias.modelo.php
    """
    __tablename__ = 'categorias'

    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(100), unique=True, nullable=False)
    ruta = db.Column(db.String(255), unique=True, nullable=False, index=True)
    estado = db.Column(db.Integer, default=1)  # 1=activo, 0=inactivo

    # Ofertas a nivel de categoría
    oferta = db.Column(db.Integer, default=0)  # 0=no, 1=sí
    precio_oferta = db.Column(db.Numeric(10, 2), default=0)
    descuento_oferta = db.Column(db.Integer, default=0)
    img_oferta = db.Column(db.String(255))
    fin_oferta = db.Column(db.Date)

    # Relaciones
    subcategorias = db.relationship('Subcategoria', backref='categoria', lazy='dynamic')
    productos = db.relationship('Producto', backref='categoria', lazy='dynamic')
    cabecera = db.relationship('Cabecera', backref='categoria', uselist=False)  # One-to-one

    @property
    def is_active(self):
        """Retorna True si la categoría está activa"""
        return self.estado == 1

    def __repr__(self):
        return f'<Categoria {self.categoria}>'


# ============================================================================
# MODELO 4: Subcategoria (tabla subcategorias)
# ============================================================================
class Subcategoria(TimestampMixin, db.Model):
    """
    Modelo de Subcategoría
    Migrado desde: backend/modelos/subcategorias.modelo.php
    """
    __tablename__ = 'subcategorias'

    id = db.Column(db.Integer, primary_key=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    subcategoria = db.Column(db.String(100), nullable=False)
    ruta = db.Column(db.String(255), unique=True, nullable=False, index=True)
    estado = db.Column(db.Integer, default=1)

    # Ofertas a nivel de subcategoría
    oferta = db.Column(db.Integer, default=0)
    precio_oferta = db.Column(db.Numeric(10, 2), default=0)
    descuento_oferta = db.Column(db.Integer, default=0)
    img_oferta = db.Column(db.String(255))
    fin_oferta = db.Column(db.Date)

    # Relaciones
    productos = db.relationship('Producto', backref='subcategoria', lazy='dynamic')
    cabecera = db.relationship('Cabecera', backref='subcategoria', uselist=False)

    @property
    def is_active(self):
        return self.estado == 1

    def __repr__(self):
        return f'<Subcategoria {self.subcategoria}>'


# ============================================================================
# MODELO 5: Producto (tabla productos)
# ============================================================================
class Producto(TimestampMixin, db.Model):
    """
    Modelo de Producto
    Migrado desde: backend/modelos/productos.modelo.php
    """
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    id_subcategoria = db.Column(db.Integer, db.ForeignKey('subcategorias.id'), nullable=False)

    tipo = db.Column(db.String(20), nullable=False)  # fisico, virtual
    ruta = db.Column(db.String(255), unique=True, nullable=False, index=True)
    estado = db.Column(db.Integer, default=1)

    # Información básica
    titulo = db.Column(db.String(200), nullable=False)
    titular = db.Column(db.String(255))  # Subtítulo
    descripcion = db.Column(db.Text)
    palabras_claves = db.Column(db.Text)  # Keywords SEO

    # Multimedia y detalles (JSON)
    multimedia = db.Column(db.JSON)  # [{"foto": "path"}, ...] o "youtube_id"
    detalles = db.Column(db.JSON)  # {"Talla": [...], "Color": [...]} o {"Clases": 10, ...}

    # Precio y ventas
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    precio_comparacion = db.Column(db.Numeric(10, 2))  # Precio original (para mostrar descuento)
    ventas = db.Column(db.Integer, default=0)
    vistas = db.Column(db.Integer, default=0)

    # Imágenes
    portada = db.Column(db.String(255))  # Imagen principal 400x450
    portada_horizontal = db.Column(db.String(255))  # Imagen horizontal

    # Oferta del producto
    oferta = db.Column(db.Integer, default=0)
    precio_oferta = db.Column(db.Numeric(10, 2), default=0)
    descuento_oferta = db.Column(db.Integer, default=0)
    img_oferta = db.Column(db.String(255))  # 640x430
    fin_oferta = db.Column(db.Date)

    # Entrega (solo productos físicos)
    peso = db.Column(db.Numeric(10, 2))  # kg
    entrega = db.Column(db.Integer)  # días hábiles, 0=inmediata

    # Relaciones
    cabecera = db.relationship('Cabecera', backref='producto', uselist=False)
    comentarios = db.relationship('Comentario', backref='producto', lazy='dynamic')
    deseos = db.relationship('Deseo', backref='producto', lazy='dynamic')

    @property
    def precio_final(self):
        """Calcula el precio final considerando ofertas"""
        # Prioridad: oferta del producto > oferta de subcategoría > oferta de categoría
        if self.oferta and self.precio_oferta > 0:
            return self.precio_oferta
        elif self.subcategoria.oferta and self.subcategoria.precio_oferta > 0:
            return self.subcategoria.precio_oferta
        elif self.categoria.oferta and self.categoria.precio_oferta > 0:
            return self.categoria.precio_oferta
        else:
            return self.precio

    @property
    def descuento_porcentaje(self):
        """Calcula el porcentaje de descuento"""
        if self.precio_final < self.precio:
            return int(((self.precio - self.precio_final) / self.precio) * 100)
        return 0

    @property
    def is_active(self):
        return self.estado == 1

    def get_multimedia(self):
        """Retorna la multimedia parseada"""
        if isinstance(self.multimedia, str):
            try:
                return json.loads(self.multimedia)
            except:
                return []
        return self.multimedia or []

    def get_detalles(self):
        """Retorna los detalles parseados"""
        if isinstance(self.detalles, str):
            try:
                return json.loads(self.detalles)
            except:
                return {}
        return self.detalles or {}

    def to_dict(self):
        """Serializa el producto a diccionario"""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'precio': float(self.precio),
            'precio_final': float(self.precio_final),
            'descuento': self.descuento_porcentaje,
            'portada': self.portada,
            'ruta': self.ruta,
            'tipo': self.tipo,
            'ventas': self.ventas,
            'categoria': self.categoria.categoria,
            'subcategoria': self.subcategoria.subcategoria
        }

    def __repr__(self):
        return f'<Producto {self.titulo}>'


# ============================================================================
# MODELO 6: Cabecera (tabla cabeceras - SEO)
# ============================================================================
class Cabecera(db.Model):
    """
    Modelo de Cabecera (metadatos SEO para productos/categorías/subcategorías)
    Migrado desde: backend/modelos/cabeceras.modelo.php
    """
    __tablename__ = 'cabeceras'

    id = db.Column(db.Integer, primary_key=True)
    ruta = db.Column(db.String(255), unique=True, nullable=False, index=True)

    # Puede ser producto, categoría o subcategoría
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=True)
    id_subcategoria = db.Column(db.Integer, db.ForeignKey('subcategorias.id'), nullable=True)

    # SEO
    titulo = db.Column(db.String(200))
    descripcion = db.Column(db.Text)
    palabras_claves = db.Column(db.Text)
    portada = db.Column(db.String(255))  # 1280x720

    def __repr__(self):
        return f'<Cabecera {self.ruta}>'


# ============================================================================
# MODELO 7: Compra (tabla compras)
# ============================================================================
class Compra(TimestampMixin, db.Model):
    """
    Modelo de Compra/Venta
    Migrado desde: backend/modelos/ventas.modelo.php
    """
    __tablename__ = 'compras'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)

    # Detalles de la compra
    detalle = db.Column(db.Text)  # Descripción del producto al momento de la compra
    cantidad = db.Column(db.Integer, default=1)
    pago = db.Column(db.Numeric(10, 2), nullable=False)

    # Método de pago
    metodo = db.Column(db.String(50), nullable=False)  # paypal, payu, gratis
    email = db.Column(db.String(100))  # Email del comprador (puede diferir del usuario)

    # Envío
    envio = db.Column(db.Integer, default=0)  # 0=despachando, 1=enviando, 2=entregado
    direccion = db.Column(db.Text)
    pais = db.Column(db.String(50))

    # Relación con producto
    producto = db.relationship('Producto', backref='compras')

    @property
    def estado_envio_texto(self):
        """Retorna el estado del envío en texto"""
        estados = {
            0: 'Despachando',
            1: 'Enviado',
            2: 'Entregado'
        }
        return estados.get(self.envio, 'Desconocido')

    def __repr__(self):
        return f'<Compra #{self.id} - Usuario {self.id_usuario}>'


# ============================================================================
# MODELO 8: Deseo (tabla deseos - wishlist)
# ============================================================================
class Deseo(TimestampMixin, db.Model):
    """
    Modelo de Lista de Deseos
    Migrado desde: backend/modelos/usuarios.modelo.php (métodos de deseos)
    """
    __tablename__ = 'deseos'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)

    # Índice único para evitar duplicados
    __table_args__ = (
        db.UniqueConstraint('id_usuario', 'id_producto', name='unique_usuario_producto'),
    )

    def __repr__(self):
        return f'<Deseo Usuario:{self.id_usuario} Producto:{self.id_producto}>'


# ============================================================================
# MODELO 9: Comentario (tabla comentarios - reviews)
# ============================================================================
class Comentario(TimestampMixin, db.Model):
    """
    Modelo de Comentario/Review
    Migrado desde: backend/modelos/usuarios.modelo.php
    """
    __tablename__ = 'comentarios'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)

    comentario = db.Column(db.Text, nullable=False)
    calificacion = db.Column(db.Integer)  # 1-5 estrellas
    respuesta = db.Column(db.Text)  # Respuesta del admin

    def __repr__(self):
        return f'<Comentario #{self.id} - Producto {self.id_producto}>'


# ============================================================================
# MODELO 10: Banner (tabla banner)
# ============================================================================
class Banner(TimestampMixin, db.Model):
    """
    Modelo de Banner
    Migrado desde: backend/modelos/banner.modelo.php
    """
    __tablename__ = 'banner'

    id = db.Column(db.Integer, primary_key=True)
    ruta = db.Column(db.String(255), nullable=False, index=True)
    img = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(50))  # categorias, subcategorias, productos
    estado = db.Column(db.Integer, default=1)

    @property
    def is_active(self):
        return self.estado == 1

    def __repr__(self):
        return f'<Banner {self.ruta}>'


# ============================================================================
# MODELO 11: Slide (tabla slide - carousel)
# ============================================================================
class Slide(db.Model):
    """
    Modelo de Slide (carousel principal)
    Migrado desde: backend/modelos/slide.modelo.php
    """
    __tablename__ = 'slide'

    id = db.Column(db.Integer, primary_key=True)
    img_fondo = db.Column(db.String(255), nullable=False)
    img_producto = db.Column(db.String(255))

    # Tipo y estilos
    tipo_slide = db.Column(db.String(50))  # sin_img, con_img
    estilo_img_producto = db.Column(db.String(100))  # CSS classes
    estilo_texto_slide = db.Column(db.String(100))  # text-left, text-right, etc

    # Textos
    titulo_1 = db.Column(db.String(200))
    titulo_2 = db.Column(db.String(200))
    titulo_3 = db.Column(db.String(200))
    boton = db.Column(db.String(100))  # Texto del botón
    url = db.Column(db.String(255))  # URL del botón

    # Orden
    orden = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Slide #{self.id} - Orden {self.orden}>'


# ============================================================================
# MODELO 12: Comercio (tabla comercio - configuración general)
# ============================================================================
class Comercio(db.Model):
    """
    Modelo de Comercio (configuración general de la tienda)
    Migrado desde: backend/modelos/comercio.modelo.php
    Solo hay un registro (singleton)
    """
    __tablename__ = 'comercio'

    id = db.Column(db.Integer, primary_key=True)

    # Branding
    logo = db.Column(db.String(255))
    icono = db.Column(db.String(255))

    # Colores
    barra_superior = db.Column(db.String(7))  # hex color
    texto_superior = db.Column(db.String(7))
    color_fondo = db.Column(db.String(7))
    color_texto = db.Column(db.String(7))

    # Redes sociales (JSON)
    redes_sociales = db.Column(db.JSON)  # {"facebook": "url", "twitter": "url", ...}

    # Scripts de terceros
    api_facebook = db.Column(db.Text)
    pixel_facebook = db.Column(db.Text)
    google_analytics = db.Column(db.Text)

    # Configuración de envíos e impuestos
    impuesto = db.Column(db.Numeric(10, 2), default=0)  # %
    envio_nacional = db.Column(db.Numeric(10, 2), default=0)
    envio_internacional = db.Column(db.Numeric(10, 2), default=0)
    tasa_minima_nal = db.Column(db.Numeric(10, 2), default=0)  # Envío gratis si supera este monto
    tasa_minima_int = db.Column(db.Numeric(10, 2), default=0)
    seleccionar_pais = db.Column(db.String(50))  # País base

    # PayPal
    modo_paypal = db.Column(db.String(20), default='sandbox')  # sandbox, live
    cliente_id_paypal = db.Column(db.String(255))
    llave_secreta_paypal = db.Column(db.String(255))

    # PayU
    modo_payu = db.Column(db.String(20), default='sandbox')
    merchant_id_payu = db.Column(db.String(100))
    account_id_payu = db.Column(db.String(100))
    api_key_payu = db.Column(db.String(255))

    def get_redes_sociales(self):
        """Retorna las redes sociales parseadas"""
        if isinstance(self.redes_sociales, str):
            try:
                return json.loads(self.redes_sociales)
            except:
                return {}
        return self.redes_sociales or {}

    def __repr__(self):
        return '<Comercio Config>'


# ============================================================================
# MODELO 13: Notificacion (tabla notificaciones)
# ============================================================================
class Notificacion(db.Model):
    """
    Modelo de Notificaciones (contadores del panel admin)
    Migrado desde: backend/modelos/notificaciones.modelo.php
    Solo hay un registro (singleton)
    """
    __tablename__ = 'notificaciones'

    id = db.Column(db.Integer, primary_key=True)
    nuevos_usuarios = db.Column(db.Integer, default=0)
    nuevas_ventas = db.Column(db.Integer, default=0)
    nuevas_visitas = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Notificaciones: {self.nuevas_ventas} ventas, {self.nuevos_usuarios} usuarios>'


# ============================================================================
# MODELO 14: Visita (tabla visitas - analytics)
# ============================================================================
class Visita(TimestampMixin, db.Model):
    """
    Modelo de Visita (tracking de visitantes)
    Migrado desde: backend/modelos/visitas.modelo.php
    """
    __tablename__ = 'visitas'

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50), nullable=False, index=True)
    pais = db.Column(db.String(50))
    visitas = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f'<Visita {self.ip} - {self.pais}>'
