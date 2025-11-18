"""
Rutas de la Tienda (Frontend)
Migrado desde: frontend/controladores/*.controlador.php

Total: 7 controladores migrados
"""
from flask import render_template, redirect, url_for, request, session
from app.shop import bp
from app.models import Producto, Categoria, Subcategoria, Usuario
from app import db

# ============================================================================
# INICIO
# ============================================================================

@bp.route('/')
@bp.route('/inicio')
def index():
    """Página principal de la tienda"""
    # TODO: Productos destacados, ofertas, slides
    return render_template('shop/index.html')


# ============================================================================
# PRODUCTOS
# ============================================================================

@bp.route('/productos')
def productos():
    """Lista de productos"""
    # TODO: Filtros, paginación
    return render_template('shop/productos.html')


@bp.route('/producto/<ruta>')
def producto_detalle(ruta):
    """Detalle de un producto"""
    # TODO: Incrementar vistas, reviews
    producto = Producto.query.filter_by(ruta=ruta).first_or_404()
    return render_template('shop/producto.html', producto=producto)


# ============================================================================
# CARRITO
# ============================================================================

@bp.route('/carrito-de-compras')
def carrito():
    """Carrito de compras"""
    return render_template('shop/carrito.html')


# TODO: Más rutas de finalizar-compra, perfil, etc.
# Se expandirá con TODO el código migrado
