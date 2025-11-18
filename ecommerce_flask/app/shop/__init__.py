"""
Blueprint Shop - Tienda para Clientes
Equivalente al frontend PHP

Rutas:
- /
- /productos
- /carrito-de-compras
- /finalizar-compra
- /perfil
- etc.
"""
from flask import Blueprint

bp = Blueprint('shop', __name__)

from app.shop import routes
