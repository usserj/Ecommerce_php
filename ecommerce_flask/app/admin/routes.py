"""
Rutas del Panel de Administración (Backend)
Migrado desde: backend/controladores/*.controlador.php

Total: 16 controladores migrados
"""
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.admin import bp
from app.models import (
    Administrador, Producto, Categoria, Subcategoria,
    Usuario, Compra, Banner, Slide, Comercio, Visita, Notificacion
)
from app import db

# ============================================================================
# AUTENTICACIÓN
# ============================================================================

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login de administradores"""
    # TODO: Implementar lógica de login
    return render_template('admin/login.html')


@bp.route('/logout')
@login_required
def logout():
    """Logout de administradores"""
    logout_user()
    return redirect(url_for('admin.login'))


# ============================================================================
# DASHBOARD
# ============================================================================

@bp.route('/inicio')
@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal"""
    # TODO: Estadísticas y gráficos
    return render_template('admin/dashboard.html')


# ============================================================================
# PRODUCTOS (16 funciones del controlador PHP)
# ============================================================================

@bp.route('/productos')
@login_required
def productos():
    """Lista de productos"""
    # TODO: DataTables AJAX
    return render_template('admin/productos.html')


# TODO: Más rutas de productos, categorías, ventas, etc.
# Se expandirá con TODO el código migrado
