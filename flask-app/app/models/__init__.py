"""Database models."""
from app.models.user import User
from app.models.admin import Administrador
from app.models.product import Producto
from app.models.categoria import Categoria, Subcategoria
from app.models.order import Compra
from app.models.comment import Comentario
from app.models.wishlist import Deseo
from app.models.comercio import Comercio
from app.models.setting import Plantilla, Slide, Banner, Cabecera
from app.models.notification import Notificacion
from app.models.visit import VisitaPais, VisitaPersona

__all__ = [
    'User',
    'Administrador',
    'Producto',
    'Categoria',
    'Subcategoria',
    'Compra',
    'Comentario',
    'Deseo',
    'Comercio',
    'Plantilla',
    'Slide',
    'Banner',
    'Cabecera',
    'Notificacion',
    'VisitaPais',
    'VisitaPersona'
]
