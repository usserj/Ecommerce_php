"""Admin panel routes."""
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user, login_user, logout_user
from app.blueprints.admin import admin_bp
from app.models.admin import Administrador
from app.models.user import User
from app.models.product import Producto
from app.models.order import Compra
from app.models.notification import Notificacion
from app.models.visit import VisitaPais, VisitaPersona
from app.extensions import db, bcrypt
from functools import wraps


def admin_required(f):
    """Decorator to require admin access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if admin is logged in
        if 'admin_id' not in session:
            flash('Debe iniciar sesión como administrador.', 'error')
            return redirect(url_for('admin.login'))

        # Verify admin still exists and is active
        admin = Administrador.query.get(session['admin_id'])
        if not admin or not admin.is_active_user():
            session.pop('admin_id', None)
            flash('Sesión de administrador inválida.', 'error')
            return redirect(url_for('admin.login'))

        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    # If already logged in as admin, redirect to dashboard
    if 'admin_id' in session:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Por favor complete todos los campos.', 'error')
            return render_template('admin/login.html')

        # Find admin user
        admin = Administrador.query.filter_by(email=email).first()

        if admin and admin.check_password(password):
            if admin.is_active_user():
                # Store admin ID in session
                session['admin_id'] = admin.id
                session['admin_email'] = admin.email
                session['admin_nombre'] = admin.nombre
                session['admin_perfil'] = admin.perfil

                flash(f'Bienvenido {admin.nombre}!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Su cuenta de administrador está inactiva.', 'error')
        else:
            flash('Email o contraseña incorrectos.', 'error')

    return render_template('admin/login.html')


@admin_bp.route('/logout')
def logout():
    """Admin logout."""
    session.pop('admin_id', None)
    session.pop('admin_email', None)
    session.pop('admin_nombre', None)
    session.pop('admin_perfil', None)
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('admin.login'))


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


@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    """Store settings and payment gateways configuration."""
    from app.models.comercio import Comercio
    import json

    config = Comercio.get_config()

    if request.method == 'POST':
        try:
            # Store settings
            config.impuesto = float(request.form.get('impuesto', 0))
            config.envioNacional = float(request.form.get('envioNacional', 0))
            config.envioInternacional = float(request.form.get('envioInternacional', 0))
            config.pais = request.form.get('pais', 'Ecuador')

            # PayPal settings
            config.modoPaypal = request.form.get('modoPaypal', 'sandbox')
            config.clienteIdPaypal = request.form.get('clienteIdPaypal', '')
            config.llaveSecretaPaypal = request.form.get('llaveSecretaPaypal', '')

            # Paymentez settings
            config.modoPaymentez = request.form.get('modoPaymentez', 'test')
            config.appCodePaymentez = request.form.get('appCodePaymentez', '')
            config.appKeyPaymentez = request.form.get('appKeyPaymentez', '')

            # Datafast settings
            config.modoDatafast = request.form.get('modoDatafast', 'test')
            config.midDatafast = request.form.get('midDatafast', '')
            config.tidDatafast = request.form.get('tidDatafast', '')

            # De Una settings
            config.modoDeUna = request.form.get('modoDeUna', 'test')
            config.apiKeyDeUna = request.form.get('apiKeyDeUna', '')

            # Bank accounts (save as JSON)
            bank_accounts = {}
            for bank in ['banco_pichincha', 'banco_guayaquil', 'banco_pacifico']:
                bank_accounts[bank] = {
                    'nombre': request.form.get(f'{bank}_nombre', ''),
                    'cuenta': request.form.get(f'{bank}_cuenta', ''),
                    'tipo': request.form.get(f'{bank}_tipo', 'Ahorros'),
                    'cedula': request.form.get(f'{bank}_cedula', '')
                }
            config.cuentasBancarias = json.dumps(bank_accounts)

            db.session.commit()
            flash('Configuración guardada exitosamente!', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar configuración: {e}', 'error')

        return redirect(url_for('admin.settings'))

    # Get bank accounts
    bank_accounts = config.get_bank_accounts()
    if not bank_accounts:
        bank_accounts = {
            'banco_pichincha': {'nombre': '', 'cuenta': '', 'tipo': 'Ahorros', 'cedula': ''},
            'banco_guayaquil': {'nombre': '', 'cuenta': '', 'tipo': 'Ahorros', 'cedula': ''},
            'banco_pacifico': {'nombre': '', 'cuenta': '', 'tipo': 'Ahorros', 'cedula': ''}
        }

    return render_template('admin/settings.html',
                         config=config,
                         bank_accounts=bank_accounts)
