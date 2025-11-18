"""Admin panel routes."""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.blueprints.admin import admin_bp
from app.models.admin import Administrador
from app.models.user import User
from app.models.product import Producto
from app.models.order import Compra
from app.models.notification import Notificacion
from app.models.visit import VisitaPais, VisitaPersona
from app.extensions import db
from functools import wraps


def admin_required(f):
    """Decorator to require admin access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated and is an admin
        if not current_user.is_authenticated:
            flash('Debe iniciar sesión.', 'error')
            return redirect(url_for('auth.login'))

        # Try to get admin user
        admin = Administrador.query.filter_by(email=current_user.email).first()
        if not admin or not admin.is_active_user():
            flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
            return redirect(url_for('main.index'))

        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard."""
    # Get statistics
    total_users = User.query.count()
    total_products = Producto.query.filter_by(estado=1).count()
    total_orders = Compra.query.count()
    total_visits = VisitaPersona.get_total_visits()

    # Get notifications
    notifications = Notificacion.get_counters()

    # Recent orders
    recent_orders = Compra.query.order_by(Compra.fecha.desc()).limit(10).all()

    # Top products
    top_products = Producto.query.filter_by(estado=1).order_by(Producto.ventas.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_products=total_products,
                         total_orders=total_orders,
                         total_visits=total_visits,
                         notifications=notifications,
                         recent_orders=recent_orders,
                         top_products=top_products)


@admin_bp.route('/users')
@admin_required
def users():
    """Manage users."""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=25, error_out=False)

    return render_template('admin/users.html', users=users)


@admin_bp.route('/products')
@admin_required
def products():
    """Manage products."""
    page = request.args.get('page', 1, type=int)
    products = Producto.query.paginate(page=page, per_page=25, error_out=False)

    return render_template('admin/products.html', products=products)


@admin_bp.route('/orders')
@admin_required
def orders():
    """Manage orders."""
    page = request.args.get('page', 1, type=int)
    orders = Compra.query.order_by(Compra.fecha.desc()).paginate(
        page=page, per_page=25, error_out=False
    )

    return render_template('admin/orders.html', orders=orders)


@admin_bp.route('/analytics')
@admin_required
def analytics():
    """Analytics and reports."""
    # Get visit statistics
    visits_by_country = VisitaPais.query.order_by(VisitaPais.cantidad.desc()).limit(10).all()
    total_visits = VisitaPersona.get_total_visits()
    unique_visitors = VisitaPersona.get_unique_visitors()

    return render_template('admin/analytics.html',
                         visits_by_country=visits_by_country,
                         total_visits=total_visits,
                         unique_visitors=unique_visitors)
