"""
Blueprint API - Endpoints REST para AJAX
Equivalente a los 22 archivos .ajax.php

Rutas:
- /api/productos/*
- /api/carrito/*
- /api/usuarios/*
- etc.
"""
from flask import Blueprint

bp = Blueprint('api', __name__)

# Disable CSRF for API endpoints (se valida por otros medios)
# csrf.exempt(bp)

from app.api import (
    productos,
    categorias,
    usuarios,
    carrito,
    admin_endpoints
)
