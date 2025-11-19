"""Checkout routes."""
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from app.blueprints.checkout import checkout_bp
from app.models.product import Producto
from app.models.order import Compra
from app.models.notification import Notificacion
from app.models.coupon import Cupon
from app.extensions import db
from app.services.payment_service import (
    process_paypal_payment,
    process_payu_payment,
    process_paymentez_payment,
    process_datafast_payment,
    process_deuna_payment,
    process_bank_transfer_payment,
    process_transfer_voucher_payment
)
import os
from werkzeug.utils import secure_filename
from datetime import datetime


@checkout_bp.route('/')
@login_required
def index():
    """Checkout page."""
    cart_items = session.get('cart', [])

    if not cart_items:
        flash('Su carrito está vacío.', 'warning')
        return redirect(url_for('shop.index'))

    # Get products and calculate totals
    products = []
    subtotal = 0
    stock_errors = []

    for item in cart_items:
        producto = Producto.query.get(item['id'])
        if producto:
            # Validate stock availability
            if not producto.is_virtual() and not producto.tiene_stock(item['cantidad']):
                if producto.agotado():
                    stock_errors.append(f"{producto.titulo} está agotado.")
                else:
                    stock_errors.append(f"{producto.titulo} solo tiene {producto.stock} unidades disponibles (solicitadas: {item['cantidad']}).")
                continue

            precio = producto.get_price()
            item_total = precio * item['cantidad']
            products.append({
                'producto': producto,
                'cantidad': item['cantidad'],
                'precio': precio,
                'total': item_total
            })
            subtotal += item_total

    # If there are stock errors, redirect to cart
    if stock_errors:
        for error in stock_errors:
            flash(error, 'error')
        return redirect(url_for('cart.index'))

    # Calculate tax and shipping
    from app.models.comercio import Comercio
    config = Comercio.get_config()
    tax = config.calculate_tax(subtotal)
    shipping = config.envioNacional
    total = subtotal + tax + shipping

    return render_template('checkout/checkout.html',
                         products=products,
                         subtotal=subtotal,
                         tax=tax,
                         shipping=shipping,
                         total=total,
                         paypal_client_id=config.clienteIdPaypal)


@checkout_bp.route('/process', methods=['POST'])
@login_required
def process():
    """Process checkout."""
    metodo_pago = request.form.get('metodo_pago')
    direccion = request.form.get('direccion')
    pais = request.form.get('pais', 'Ecuador')
    telefono = request.form.get('telefono', '')
    cedula = request.form.get('cedula', '')

    if not direccion or not metodo_pago:
        flash('Complete todos los campos requeridos.', 'error')
        return redirect(url_for('checkout.index'))

    cart_items = session.get('cart', [])

    if not cart_items:
        flash('Su carrito está vacío.', 'warning')
        return redirect(url_for('shop.index'))

    # Validate stock before processing payment
    stock_errors = []
    for item in cart_items:
        producto = Producto.query.get(item['id'])
        if producto:
            if not producto.is_virtual() and not producto.tiene_stock(item['cantidad']):
                if producto.agotado():
                    stock_errors.append(f"{producto.titulo} está agotado.")
                else:
                    stock_errors.append(f"{producto.titulo} solo tiene {producto.stock} unidades disponibles.")

    if stock_errors:
        for error in stock_errors:
            flash(error, 'error')
        return redirect(url_for('cart.index'))

    # Save checkout data in session for PayPal callback
    session['checkout_direccion'] = direccion
    session['checkout_pais'] = pais

    # Prepare order data
    order_data = {
        'user_id': current_user.id,
        'cart_items': cart_items,
        'direccion': direccion,
        'pais': pais,
        'telefono': telefono,
        'cedula': cedula,
        'metodo': metodo_pago
    }

    # Process payment based on method
    payment_methods = {
        'paypal': process_paypal_payment,
        'payu': process_payu_payment,
        'paymentez': process_paymentez_payment,
        'datafast': process_datafast_payment,
        'deuna': process_deuna_payment,
        'transferencia': process_bank_transfer_payment,
        'transferencia_comprobante': process_transfer_voucher_payment
    }

    payment_handler = payment_methods.get(metodo_pago)
    if payment_handler:
        return payment_handler(order_data)
    else:
        flash('Método de pago no válido.', 'error')
        return redirect(url_for('checkout.index'))


@checkout_bp.route('/validate-coupon', methods=['POST'])
@login_required
def validate_coupon():
    """Validate coupon code and return discount."""
    try:
        data = request.get_json()
        codigo = data.get('codigo', '').strip().upper()
        monto = float(data.get('monto', 0))

        if not codigo:
            return jsonify({
                'success': False,
                'message': 'Código de cupón requerido'
            }), 400

        # Find coupon
        cupon = Cupon.query.filter_by(codigo=codigo).first()

        if not cupon:
            return jsonify({
                'success': False,
                'message': 'Cupón no válido o no existe'
            })

        # Validate coupon
        is_valid, message = cupon.is_valid(monto)

        if not is_valid:
            return jsonify({
                'success': False,
                'message': message
            })

        # Calculate discount
        descuento = cupon.calculate_discount(monto)

        # Save coupon in session for later use
        session['applied_coupon'] = {
            'codigo': codigo,
            'id': cupon.id,
            'descuento': descuento
        }
        session.modified = True

        return jsonify({
            'success': True,
            'message': f'¡Cupón aplicado! {message}',
            'descuento': round(descuento, 2),
            'tipo': cupon.tipo,
            'valor': cupon.valor
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al validar cupón: {str(e)}'
        }), 500


@checkout_bp.route('/paypal/execute')
@login_required
def paypal_execute():
    """Execute PayPal payment after user approval."""
    import paypalrestsdk
    from app.services.payment_service import configure_paypal, create_order_from_cart

    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')

    if not payment_id or not payer_id:
        flash('Información de pago incompleta.', 'error')
        return redirect(url_for('cart.index'))

    try:
        # Configure PayPal and execute payment
        configure_paypal()
        payment = paypalrestsdk.Payment.find(payment_id)

        if payment.execute({"payer_id": payer_id}):
            # Get cart and create order
            cart_items = session.get('cart', [])

            if cart_items:
                # Get user's address (we should save this during checkout, for now use default)
                direccion = session.get('checkout_direccion', 'Pendiente')
                pais = session.get('checkout_pais', 'Ecuador')

                # Get coupon from session
                cupon_info = session.get('applied_coupon', None)

                # Create order with completed status
                success, message, orders = create_order_from_cart(
                    current_user.id,
                    cart_items,
                    direccion,
                    pais,
                    'paypal',
                    payment_id,
                    estado='procesando',
                    cupon_info=cupon_info
                )

                if not success:
                    flash(f'Pago completado pero error al crear orden: {message}', 'warning')
                    return redirect(url_for('account.orders'))

                # Clear cart and session data
                session['cart'] = []
                session.pop('checkout_direccion', None)
                session.pop('checkout_pais', None)
                session.pop('applied_coupon', None)
                session.modified = True

                flash('¡Pago completado exitosamente!', 'success')
                return redirect(url_for('checkout.success'))
            else:
                flash('Carrito vacío.', 'warning')
                return redirect(url_for('shop.index'))
        else:
            flash(f'Error al procesar el pago: {payment.error}', 'error')
            return redirect(url_for('cart.index'))

    except Exception as e:
        flash(f'Error al procesar el pago con PayPal: {str(e)}', 'error')
        return redirect(url_for('cart.index'))


@checkout_bp.route('/success')
@login_required
def success():
    """Payment success page."""
    # Clear cart
    session['cart'] = []
    session.modified = True

    flash('¡Compra realizada exitosamente!', 'success')
    return render_template('checkout/success.html')


@checkout_bp.route('/cancel')
@login_required
def cancel():
    """Payment cancelled page."""
    flash('Pago cancelado.', 'warning')
    return redirect(url_for('cart.index'))


@checkout_bp.route('/upload_voucher', methods=['POST'])
@login_required
def upload_voucher():
    """Handle voucher upload for bank transfer."""
    order_id = request.form.get('order_id')
    referencia = request.form.get('referencia', '')

    if 'comprobante' not in request.files:
        flash('No se seleccionó ningún archivo.', 'error')
        return redirect(url_for('checkout.index'))

    file = request.files['comprobante']

    if file.filename == '':
        flash('No se seleccionó ningún archivo.', 'error')
        return redirect(url_for('checkout.index'))

    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'pdf', 'txt'}
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

    if file_ext not in allowed_extensions:
        flash('Tipo de archivo no permitido. Use PNG, JPG, PDF o TXT.', 'error')
        return redirect(url_for('checkout.index'))

    # Create uploads directory if it doesn't exist
    upload_folder = os.path.join('app', 'static', 'uploads', 'vouchers')
    os.makedirs(upload_folder, exist_ok=True)

    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = secure_filename(f"{current_user.id}_{timestamp}_{file.filename}")
    filepath = os.path.join(upload_folder, filename)

    try:
        # Save file
        file.save(filepath)

        # Create order with pending status
        cart_items = session.get('cart', [])

        if cart_items:
            from app.services.payment_service import create_order_from_cart
            from app.models.comercio import Comercio

            # Calculate total
            subtotal = 0
            for item in cart_items:
                producto = Producto.query.get(item['id'])
                if producto:
                    subtotal += producto.get_price() * item['cantidad']

            config = Comercio.get_config()
            tax = config.calculate_tax(subtotal)
            shipping = config.envioNacional
            total = subtotal + tax + shipping

            # Get user address from form or use default
            direccion = request.form.get('direccion', 'Pendiente')
            pais = request.form.get('pais', 'Ecuador')

            # Get coupon from session
            cupon_info = session.get('applied_coupon', None)

            # Create order
            success, message, orders = create_order_from_cart(
                current_user.id,
                cart_items,
                direccion,
                pais,
                'transferencia_comprobante',
                order_id or f"ORD-{current_user.id}-{int(datetime.now().timestamp())}",
                estado='pendiente',
                cupon_info=cupon_info
            )

            if not success:
                flash(f'Error al crear la orden: {message}', 'error')
                return redirect(url_for('checkout.index'))

            # TODO: Could add a Message/Log model to track voucher uploads
            # For now, the voucher is saved and the order is created with pending status

            # Clear cart and coupon
            session['cart'] = []
            session.pop('applied_coupon', None)
            session.modified = True

            flash('Comprobante subido exitosamente. Su pedido será procesado en 24-48 horas.', 'success')
            return redirect(url_for('checkout.success'))
        else:
            flash('Carrito vacío.', 'error')
            return redirect(url_for('shop.index'))

    except Exception as e:
        flash(f'Error al subir el comprobante: {str(e)}', 'error')
        return redirect(url_for('checkout.index'))
