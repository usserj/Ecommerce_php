"""
Blueprint Admin - Panel de Administración
Equivalente al backend PHP

Rutas:
- /backend/login
- /backend/dashboard
- /backend/productos
- /backend/categorias
- /backend/ventas
- etc.
"""
from flask import Blueprint

bp = Blueprint('admin', __name__)

from app.admin import routes
