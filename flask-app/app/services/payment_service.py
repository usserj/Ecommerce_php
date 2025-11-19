"""Payment service for multiple payment gateways."""
from flask import current_app, url_for, redirect, flash, render_template, session
import paypalrestsdk
import requests
import hashlib
import hmac
import base64
import json
from datetime import datetime
from app.models.comercio import Comercio
from app.models.product import Producto
from app.models.order import Compra
from app.models.notification import Notificacion
from app.extensions import db


def get_coupon_from_session():
    """Get coupon info from session if available."""
    return session.get('applied_coupon', None)


def configure_paypal():
    """Configure PayPal SDK."""
    config = Comercio.get_config()
    paypal_config = config.get_paypal_config()

    paypalrestsdk.configure({
        "mode": paypal_config['mode'],
        "client_id": paypal_config['client_id'],
        "client_secret": paypal_config['client_secret']
    })


def process_paypal_payment(order_data):
    """Process PayPal payment."""
    configure_paypal()

    cart_items = order_data['cart_items']
    items = []
    subtotal = 0

    # Build items list
    for item in cart_items:
        producto = Producto.query.get(item['id'])
        if producto:
            precio = producto.get_price()
            cantidad = item['cantidad']
            item_total = precio * cantidad
            subtotal += item_total

            items.append({
                "name": producto.titulo,
                "sku": str(producto.id),
                "price": str(precio),
                "currency": "USD",
                "quantity": cantidad
            })

    # Calculate totals
    config = Comercio.get_config()
    tax = config.calculate_tax(subtotal)
    shipping = config.calculate_shipping(order_data['pais'])
    total = subtotal + tax + shipping

    # Create payment
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": url_for('checkout.paypal_execute', _external=True),
            "cancel_url": url_for('checkout.cancel', _external=True)
        },
        "transactions": [{
            "item_list": {
                "items": items
            },
            "amount": {
                "total": str(round(total, 2)),
                "currency": "USD",
                "details": {
                    "subtotal": str(round(subtotal, 2)),
                    "tax": str(round(tax, 2)),
                    "shipping": str(round(shipping, 2))
                }
            },
            "description": "Compra en Tienda Virtual"
        }]
    })

    if payment.create():
        # Get approval URL
        for link in payment.links:
            if link.rel == "approval_url":
                return redirect(link.href)
    else:
        flash('Error al procesar el pago con PayPal.', 'error')
        return redirect(url_for('checkout.index'))


def process_payu_payment(order_data):
    """Process PayU payment."""
    # TODO: Implement PayU payment processing
    flash('PayU no está implementado aún. Use PayPal.', 'warning')
    return redirect(url_for('checkout.index'))


def create_order_from_cart(user_id, cart_items, direccion, pais, metodo, payment_id, estado='pendiente', cupon_info=None):
    """Create order records from cart.

    Args:
        user_id: User ID
        cart_items: List of cart items
        direccion: Shipping address
        pais: Country
        metodo: Payment method
        payment_id: Payment transaction ID
        estado: Order status
        cupon_info: Dictionary with coupon info {'id': int, 'codigo': str, 'descuento': float}

    Returns:
        tuple: (success: bool, message: str, orders: list or None)
    """
    from app.models.user import User
    from app.models.coupon import Cupon
    user = User.query.get(user_id)

    if not user:
        return False, "Usuario no encontrado", None

    created_orders = []
    cupon_aplicado = None

    try:
        # Validate and lock coupon if provided
        if cupon_info and cupon_info.get('id'):
            cupon_aplicado = Cupon.query.with_for_update().get(cupon_info['id'])
            if not cupon_aplicado:
                db.session.rollback()
                return False, "El cupón seleccionado ya no está disponible", None

            # Re-validate coupon
            subtotal = sum(Producto.query.get(item['id']).get_price() * item['cantidad']
                          for item in cart_items if Producto.query.get(item['id']))
            is_valid, message = cupon_aplicado.is_valid(subtotal)
            if not is_valid:
                db.session.rollback()
                return False, f"El cupón ya no es válido: {message}", None

        # First pass: Validate all stock availability with database locking
        for item in cart_items:
            # Use SELECT FOR UPDATE to prevent race conditions
            producto = Producto.query.with_for_update().get(item['id'])

            if not producto:
                db.session.rollback()
                return False, f"Producto con ID {item['id']} no encontrado", None

            if producto.estado != 1:
                db.session.rollback()
                return False, f"El producto '{producto.titulo}' no está disponible", None

            # Validate stock availability
            if not producto.tiene_stock(item['cantidad']):
                db.session.rollback()
                stock_msg = "sin stock" if producto.agotado() else f"solo quedan {producto.stock} unidades"
                return False, f"El producto '{producto.titulo}' no tiene stock suficiente ({stock_msg})", None

        # Calculate total and apply discount
        subtotal_orders = 0
        for item in cart_items:
            producto = Producto.query.get(item['id'])
            if producto:
                subtotal_orders += producto.get_price() * item['cantidad']

        descuento_total = 0
        if cupon_aplicado:
            descuento_total = cupon_aplicado.calculate_discount(subtotal_orders)

        # Second pass: Create orders and decrement stock
        for item in cart_items:
            producto = Producto.query.with_for_update().get(item['id'])

            if producto:
                # Decrement stock immediately (reserve inventory)
                if not producto.decrementar_stock(item['cantidad']):
                    db.session.rollback()
                    return False, f"Error al decrementar stock del producto '{producto.titulo}'", None

                # Calculate item price and proportional discount
                item_total = float(producto.get_price() * item['cantidad'])
                item_discount = 0
                if descuento_total > 0 and subtotal_orders > 0:
                    # Apply discount proportionally to this item
                    item_discount = (item_total / subtotal_orders) * descuento_total

                final_price = max(0, item_total - item_discount)

                # Prepare detalle with payment_id and coupon info
                detalle_data = {
                    'payment_id': payment_id,
                }
                if cupon_aplicado:
                    detalle_data['cupon'] = {
                        'codigo': cupon_aplicado.codigo,
                        'descuento': round(item_discount, 2)
                    }

                # Create order record
                compra = Compra(
                    id_usuario=user_id,
                    id_producto=producto.id,
                    envio=0,  # TODO: Calculate shipping
                    metodo=metodo,
                    email=user.email,
                    direccion=direccion,
                    pais=pais,
                    cantidad=item['cantidad'],
                    detalle=json.dumps(detalle_data),
                    pago=round(final_price, 2),
                    estado=estado
                )
                db.session.add(compra)
                created_orders.append(compra)

                # Update product sales counter only if paid
                if estado == 'procesando':
                    producto.increment_sales()

        # Increment coupon usage if applied and payment is processing
        if cupon_aplicado and estado == 'procesando':
            cupon_aplicado.increment_usage()

        # Update notifications
        if estado == 'procesando':
            Notificacion.increment_new_sales()

        db.session.commit()
        return True, "Órdenes creadas exitosamente", created_orders

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating orders: {e}")
        return False, f"Error al crear las órdenes: {str(e)}", None


# ===========================
# Paymentez/Datafast (Ecuador)
# ===========================

def process_paymentez_payment(order_data):
    """Process Paymentez payment (Ecuador)."""
    config = Comercio.get_config()
    paymentez_config = config.get_paymentez_config()

    if not paymentez_config.get('app_code') or not paymentez_config.get('app_key'):
        flash('Paymentez no está configurado. Contacte al administrador.', 'error')
        return redirect(url_for('checkout.index'))

    cart_items = order_data['cart_items']
    subtotal = calculate_cart_total(cart_items)

    # Calculate totals
    tax = config.calculate_tax(subtotal)
    shipping = config.calculate_shipping(order_data['pais'])
    total = subtotal + tax + shipping

    # Create order with pending status
    order_id = f"ORDER-{order_data['user_id']}-{int(datetime.now().timestamp())}"
    cupon_info = get_coupon_from_session()

    success, message, orders = create_order_from_cart(
        order_data['user_id'],
        cart_items,
        order_data['direccion'],
        order_data['pais'],
        'paymentez',
        order_id,
        estado='pendiente',
        cupon_info=cupon_info
    )

    if not success:
        flash(f'Error al procesar la orden: {message}', 'error')
        return redirect(url_for('checkout.index'))

    # Clear coupon from session after creating order
    session.pop('applied_coupon', None)

    # Return payment page with Paymentez checkout
    return render_template('checkout/paymentez.html',
                         order_id=order_id,
                         total=total,
                         paymentez_config=paymentez_config)


def process_datafast_payment(order_data):
    """Process Datafast payment (Ecuador)."""
    config = Comercio.get_config()
    datafast_config = config.get_datafast_config()

    if not datafast_config.get('mid') or not datafast_config.get('tid'):
        flash('Datafast no está configurado. Contacte al administrador.', 'error')
        return redirect(url_for('checkout.index'))

    cart_items = order_data['cart_items']
    subtotal = calculate_cart_total(cart_items)

    # Calculate totals
    tax = config.calculate_tax(subtotal)
    shipping = config.calculate_shipping(order_data['pais'])
    total = subtotal + tax + shipping

    # Create order with pending status
    order_id = f"ORDER-{order_data['user_id']}-{int(datetime.now().timestamp())}"
    cupon_info = get_coupon_from_session()

    success, message, orders = create_order_from_cart(
        order_data['user_id'],
        cart_items,
        order_data['direccion'],
        order_data['pais'],
        'datafast',
        order_id,
        estado='pendiente',
        cupon_info=cupon_info
    )

    if not success:
        flash(f'Error al procesar la orden: {message}', 'error')
        return redirect(url_for('checkout.index'))

    # Clear coupon from session
    session.pop('applied_coupon', None)

    # Return payment page with Datafast form
    return render_template('checkout/datafast.html',
                         order_id=order_id,
                         total=total,
                         datafast_config=datafast_config)


# ===========================
# De Una (Ecuador - Pago móvil)
# ===========================

def process_deuna_payment(order_data):
    """Process De Una payment (Ecuador)."""
    config = Comercio.get_config()
    deuna_config = config.get_deuna_config()

    if not deuna_config.get('api_key'):
        flash('De Una no está configurado. Contacte al administrador.', 'error')
        return redirect(url_for('checkout.index'))

    cart_items = order_data['cart_items']
    subtotal = calculate_cart_total(cart_items)

    # Calculate totals
    tax = config.calculate_tax(subtotal)
    shipping = config.calculate_shipping(order_data['pais'])
    total = subtotal + tax + shipping

    # Create order with pending status
    order_id = f"ORDER-{order_data['user_id']}-{int(datetime.now().timestamp())}"
    cupon_info = get_coupon_from_session()

    success, message, orders = create_order_from_cart(
        order_data['user_id'],
        cart_items,
        order_data['direccion'],
        order_data['pais'],
        'deuna',
        order_id,
        estado='pendiente',
        cupon_info=cupon_info
    )

    if not success:
        flash(f'Error al procesar la orden: {message}', 'error')
        return redirect(url_for('checkout.index'))

    # Clear coupon from session
    session.pop('applied_coupon', None)

    # Return payment page with De Una instructions
    return render_template('checkout/deuna.html',
                         order_id=order_id,
                         total=total,
                         deuna_config=deuna_config)


# ===========================
# Transferencia Bancaria
# ===========================

def process_bank_transfer_payment(order_data):
    """Process bank transfer payment."""
    config = Comercio.get_config()
    bank_accounts = config.get_bank_accounts()

    # If no bank accounts from DB, use config defaults
    if not bank_accounts:
        bank_accounts = current_app.config.get('BANK_ACCOUNTS', {})

    if not bank_accounts:
        flash('No hay cuentas bancarias configuradas. Contacte al administrador.', 'error')
        return redirect(url_for('checkout.index'))

    cart_items = order_data['cart_items']
    subtotal = calculate_cart_total(cart_items)

    # Calculate totals
    tax = config.calculate_tax(subtotal)
    shipping = config.calculate_shipping(order_data['pais'])
    total = subtotal + tax + shipping

    # Create order with pending status
    order_id = f"ORDER-{order_data['user_id']}-{int(datetime.now().timestamp())}"
    cupon_info = get_coupon_from_session()

    success, message, orders = create_order_from_cart(
        order_data['user_id'],
        cart_items,
        order_data['direccion'],
        order_data['pais'],
        'transferencia',
        order_id,
        estado='pendiente',
        cupon_info=cupon_info
    )

    if not success:
        flash(f'Error al procesar la orden: {message}', 'error')
        return redirect(url_for('checkout.index'))

    # Clear coupon from session
    session.pop('applied_coupon', None)

    # Return page with bank account details
    return render_template('checkout/bank_transfer.html',
                         order_id=order_id,
                         total=total,
                         bank_accounts=bank_accounts)


# ===========================
# Transferencia con Comprobante
# ===========================

def process_transfer_voucher_payment(order_data):
    """Process transfer with voucher upload."""
    config = Comercio.get_config()
    bank_accounts = config.get_bank_accounts()

    # If no bank accounts from DB, use config defaults
    if not bank_accounts:
        bank_accounts = current_app.config.get('BANK_ACCOUNTS', {})

    if not bank_accounts:
        flash('No hay cuentas bancarias configuradas. Contacte al administrador.', 'error')
        return redirect(url_for('checkout.index'))

    cart_items = order_data['cart_items']
    subtotal = calculate_cart_total(cart_items)

    # Calculate totals
    tax = config.calculate_tax(subtotal)
    shipping = config.calculate_shipping(order_data['pais'])
    total = subtotal + tax + shipping

    # Create order with pending status
    order_id = f"ORDER-{order_data['user_id']}-{int(datetime.now().timestamp())}"
    cupon_info = get_coupon_from_session()

    success, message, orders = create_order_from_cart(
        order_data['user_id'],
        cart_items,
        order_data['direccion'],
        order_data['pais'],
        'transferencia_comprobante',
        order_id,
        estado='pendiente',
        cupon_info=cupon_info
    )

    if not success:
        flash(f'Error al procesar la orden: {message}', 'error')
        return redirect(url_for('checkout.index'))

    # Clear coupon from session
    session.pop('applied_coupon', None)

    # Return page with voucher upload form
    return render_template('checkout/transfer_voucher.html',
                         order_id=order_id,
                         total=total,
                         bank_accounts=bank_accounts)


# ===========================
# Utility Functions
# ===========================

def calculate_cart_total(cart_items):
    """Calculate cart subtotal."""
    subtotal = 0
    for item in cart_items:
        producto = Producto.query.get(item['id'])
        if producto:
            subtotal += producto.get_price() * item['cantidad']
    return subtotal
