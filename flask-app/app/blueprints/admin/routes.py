"""Admin panel routes."""
from flask import render_template, redirect, url_for, flash, request, session, jsonify, send_file
from flask_login import login_required, current_user, login_user, logout_user
from app.blueprints.admin import admin_bp
from app.models.admin import Administrador
from app.models.user import User
from app.models.product import Producto
from app.models.order import Compra
from app.models.notification import Notificacion
from app.models.visit import VisitaPais, VisitaPersona
from app.models.categoria import Categoria, Subcategoria
from app.models.setting import Slide, Banner
from app.models.comercio import Comercio
from app.extensions import db, bcrypt
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
import os
import json
import io
from PIL import Image


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

    # Chart data - Sales by day (last 7 days)
    from datetime import timedelta
    from sqlalchemy import func, cast, Date
    today = datetime.now().date()
    week_ago = today - timedelta(days=6)
    
    sales_by_day = db.session.query(
        cast(Compra.fecha, Date).label('date'),
        func.count(Compra.id).label('count'),
        func.sum(Compra.pago).label('total')
    ).filter(Compra.fecha >= week_ago).group_by(cast(Compra.fecha, Date)).all()
    
    # Chart data - Visits by country (top 5)
    top_countries = VisitaPais.query.order_by(VisitaPais.cantidad.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_products=total_products,
                         total_orders=total_orders,
                         total_visits=total_visits,
                         notifications=notifications,
                         recent_orders=recent_orders,
                         top_products=top_products,
                         sales_by_day=sales_by_day,
                         top_countries=top_countries)


@admin_bp.route('/users')
@admin_required
def users():
    """Manage users."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    query = User.query

    if search:
        query = query.filter(User.nombre.contains(search) | User.email.contains(search))

    users = query.order_by(User.fecha.desc()).paginate(page=page, per_page=25, error_out=False)

    return render_template('admin/users.html', users=users)



@admin_bp.route('/users/toggle/<int:id>', methods=['POST'])
@admin_required
def toggle_user(id):
    """Toggle user verification status."""
    try:
        user = User.query.get_or_404(id)
        user.verificacion = 0 if user.verificacion == 1 else 1
        db.session.commit()
        return jsonify({'success': True, 'verificacion': user.verificacion})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/users/<int:id>/orders')
@admin_required
def user_orders(id):
    """View user's order history."""
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    orders = Compra.query.filter_by(id_usuario=id).order_by(Compra.fecha.desc()).paginate(
        page=page, per_page=25, error_out=False
    )

    return render_template('admin/user_orders.html', user=user, orders=orders)
@admin_bp.route('/products')
@admin_required
def products():
    """Manage products."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    categoria_id = request.args.get('categoria', type=int)

    query = Producto.query

    if search:
        query = query.filter(Producto.titulo.contains(search) | Producto.descripcion.contains(search))

    if categoria_id:
        query = query.filter_by(id_categoria=categoria_id)

    products = query.order_by(Producto.fecha.desc()).paginate(page=page, per_page=25, error_out=False)
    categorias = Categoria.query.all()

    return render_template('admin/products.html', products=products, categorias=categorias)


@admin_bp.route('/products/create', methods=['GET', 'POST'])
@admin_required
def create_product():
    """Create new product."""
    if request.method == 'POST':
        try:
            # Get form data
            titulo = request.form.get('titulo')
            ruta = request.form.get('ruta')
            id_categoria = request.form.get('id_categoria', type=int)
            id_subcategoria = request.form.get('id_subcategoria', type=int) or None
            tipo = request.form.get('tipo', 'fisico')
            precio = float(request.form.get('precio', 0))
            stock = int(request.form.get('stock', 0)) if tipo == 'fisico' else 0
            descripcion = request.form.get('descripcion', '')
            titular = request.form.get('titular', '')

            # Handle image upload
            portada = ''
            if 'portada' in request.files:
                file = request.files['portada']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    upload_folder = os.path.join('app/static/uploads/productos')
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)

                    filepath = os.path.join(upload_folder, filename)

                    # Resize image to 1280x720
                    img = Image.open(file)
                    img = img.resize((1280, 720), Image.Resampling.LANCZOS)
                    img.save(filepath)

                    portada = f'uploads/productos/{filename}'

            # Create product
            producto = Producto(
                titulo=titulo,
                ruta=ruta,
                id_categoria=id_categoria,
                id_subcategoria=id_subcategoria,
                tipo=tipo,
                precio=precio,
                stock=stock,
                descripcion=descripcion,
                titular=titular,
                portada=portada,
                estado=1
            )

            db.session.add(producto)
            db.session.commit()

            flash('Producto creado exitosamente!', 'success')
            return redirect(url_for('admin.products'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear producto: {e}', 'error')

    categorias = Categoria.query.all()
    subcategorias = Subcategoria.query.all()
    return render_template('admin/product_create.html', categorias=categorias, subcategorias=subcategorias)


@admin_bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_product(id):
    """Edit product."""
    producto = Producto.query.get_or_404(id)

    if request.method == 'POST':
        try:
            producto.titulo = request.form.get('titulo')
            producto.ruta = request.form.get('ruta')
            producto.id_categoria = request.form.get('id_categoria', type=int)
            producto.id_subcategoria = request.form.get('id_subcategoria', type=int) or None
            producto.tipo = request.form.get('tipo', 'fisico')
            producto.precio = float(request.form.get('precio', 0))
            producto.stock = int(request.form.get('stock', 0)) if producto.tipo == 'fisico' else 0
            producto.stock_minimo = int(request.form.get('stock_minimo', 5))
            producto.descripcion = request.form.get('descripcion', '')
            producto.titular = request.form.get('titular', '')

            # Handle offer
            producto.oferta = 1 if request.form.get('oferta') == '1' else 0
            if producto.oferta:
                producto.precioOferta = float(request.form.get('precioOferta', 0))
                producto.descuentoOferta = int(request.form.get('descuentoOferta', 0))
                fin_oferta = request.form.get('finOferta')
                if fin_oferta:
                    producto.finOferta = datetime.strptime(fin_oferta, '%Y-%m-%d')

            # Handle image upload
            if 'portada' in request.files:
                file = request.files['portada']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    upload_folder = os.path.join('app/static/uploads/productos')
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)

                    filepath = os.path.join(upload_folder, filename)

                    # Resize image to 1280x720
                    img = Image.open(file)
                    img = img.resize((1280, 720), Image.Resampling.LANCZOS)
                    img.save(filepath)

                    producto.portada = f'uploads/productos/{filename}'

            db.session.commit()
            flash('Producto actualizado exitosamente!', 'success')
            return redirect(url_for('admin.products'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar producto: {e}', 'error')

    categorias = Categoria.query.all()
    subcategorias = Subcategoria.query.all()
    return render_template('admin/product_edit.html',
                         producto=producto,
                         categorias=categorias,
                         subcategorias=subcategorias)


@admin_bp.route('/products/delete/<int:id>', methods=['POST'])
@admin_required
def delete_product(id):
    """Delete product."""
    try:
        producto = Producto.query.get_or_404(id)
        db.session.delete(producto)
        db.session.commit()
        flash('Producto eliminado exitosamente!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar producto: {e}', 'error')

    return redirect(url_for('admin.products'))


@admin_bp.route('/products/toggle/<int:id>', methods=['POST'])
@admin_required
def toggle_product(id):
    """Toggle product status."""
    try:
        producto = Producto.query.get_or_404(id)
        producto.estado = 0 if producto.estado == 1 else 1
        db.session.commit()
        return jsonify({'success': True, 'estado': producto.estado})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/orders')
@admin_required
def orders():
    """Manage orders."""
    page = request.args.get('page', 1, type=int)
    orders = Compra.query.order_by(Compra.fecha.desc()).paginate(
        page=page, per_page=25, error_out=False
    )

    return render_template('admin/orders.html', orders=orders)


@admin_bp.route('/orders/update-status/<int:id>', methods=['POST'])
@admin_required
def update_order_status(id):
    """Update order status."""
    try:
        order = Compra.query.get_or_404(id)
        estado = request.form.get('estado')
        tracking = request.form.get('tracking', '')
        
        if estado:
            order.estado = estado
            if tracking:
                order.tracking = tracking
            order.fecha_estado = datetime.now()
            db.session.commit()
            
            flash('Estado de orden actualizado correctamente!', 'success')
        else:
            flash('Debe seleccionar un estado.', 'error')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar estado: {e}', 'error')
    
    return redirect(url_for('admin.orders'))



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


@admin_bp.route('/export/users')
@admin_required
def export_users():
    """Export users to Excel."""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Usuarios"
        
        # Headers
        headers = ['ID', 'Nombre', 'Email', 'Modo', 'Verificado', 'Fecha Registro']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="667EEA", end_color="667EEA", fill_type="solid")
        
        # Data
        users = User.query.all()
        for row, user in enumerate(users, 2):
            ws.cell(row=row, column=1, value=user.id)
            ws.cell(row=row, column=2, value=user.nombre)
            ws.cell(row=row, column=3, value=user.email)
            ws.cell(row=row, column=4, value=user.modo)
            ws.cell(row=row, column=5, value='Sí' if user.verificacion == 0 else 'No')
            ws.cell(row=row, column=6, value=user.fecha.strftime('%d/%m/%Y'))
        
        # Save to BytesIO
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        as_attachment=True, download_name=f'usuarios_{datetime.now().strftime("%Y%m%d")}.xlsx')
    except Exception as e:
        flash(f'Error al exportar: {e}', 'error')
        return redirect(url_for('admin.users'))


@admin_bp.route('/export/products')
@admin_required
def export_products():
    """Export products to Excel."""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Productos"
        
        # Headers
        headers = ['ID', 'Título', 'Categoría', 'Precio', 'Stock', 'Ventas', 'Estado']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="667EEA", end_color="667EEA", fill_type="solid")
        
        # Data
        products = Producto.query.all()
        for row, p in enumerate(products, 2):
            ws.cell(row=row, column=1, value=p.id)
            ws.cell(row=row, column=2, value=p.titulo)
            ws.cell(row=row, column=3, value=p.categoria.categoria if p.categoria else 'N/A')
            ws.cell(row=row, column=4, value=float(p.precio))
            ws.cell(row=row, column=5, value=p.stock)
            ws.cell(row=row, column=6, value=p.ventas)
            ws.cell(row=row, column=7, value='Activo' if p.estado == 1 else 'Inactivo')
        
        # Save to BytesIO
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        as_attachment=True, download_name=f'productos_{datetime.now().strftime("%Y%m%d")}.xlsx')
    except Exception as e:
        flash(f'Error al exportar: {e}', 'error')
        return redirect(url_for('admin.products'))


@admin_bp.route('/export/orders')
@admin_required
def export_orders():
    """Export orders to Excel."""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Pedidos"
        
        # Headers
        headers = ['ID', 'Cliente', 'Producto', 'Cantidad', 'Total', 'Método', 'Estado', 'Fecha']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="667EEA", end_color="667EEA", fill_type="solid")
        
        # Data
        orders = Compra.query.all()
        for row, o in enumerate(orders, 2):
            ws.cell(row=row, column=1, value=o.id)
            ws.cell(row=row, column=2, value=o.usuario.nombre if o.usuario else 'N/A')
            ws.cell(row=row, column=3, value=o.producto.titulo if o.producto else 'N/A')
            ws.cell(row=row, column=4, value=o.cantidad)
            ws.cell(row=row, column=5, value=float(o.pago))
            ws.cell(row=row, column=6, value=o.metodo)
            ws.cell(row=row, column=7, value=o.estado)
            ws.cell(row=row, column=8, value=o.fecha.strftime('%d/%m/%Y %H:%M'))
        
        # Save to BytesIO
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        as_attachment=True, download_name=f'pedidos_{datetime.now().strftime("%Y%m%d")}.xlsx')
    except Exception as e:
        flash(f'Error al exportar: {e}', 'error')
        return redirect(url_for('admin.orders'))
