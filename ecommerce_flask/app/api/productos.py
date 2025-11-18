"""
API Endpoints para Productos
Migrado desde: backend/ajax/productos.ajax.php

Endpoints:
- POST /api/productos/activar - Activar/desactivar producto
- POST /api/productos/validar - Validar título único
- POST /api/productos/multimedia - Subir imagen
- POST /api/productos/crear - Crear producto
- POST /api/productos/editar - Editar producto
- GET /api/productos/<id> - Obtener producto
"""
from flask import jsonify, request
from app.api import bp
from app.models import Producto
from app import db

@bp.route('/productos/activar', methods=['POST'])
def activar_producto():
    """Activar/desactivar un producto (AJAX)"""
    # TODO: Implementar
    return jsonify({'status': 'ok'})

# TODO: Más endpoints
# Se expandirá con TODO el código de los 22 archivos AJAX
