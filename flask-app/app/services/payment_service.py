"""Payment service for multiple payment gateways."""
from flask import current_app, url_for, redirect, flash, render_template, session
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

# PayPal SDK - opcional
try:
    import paypalrestsdk
    PAYPAL_AVAILABLE = True
except ImportError:
    PAYPAL_AVAILABLE = False
    current_app.logger.warning("PayPal SDK no está instalado. La funcionalidad de PayPal no estará disponible.") if current_app else None


def get_coupon_from_session():
    """Get coupon info from session if available."""
    return session.get('applied_coupon', None)


def configure_paypal():
    """Configure PayPal SDK."""
    if not PAYPAL_AVAILABLE:
        raise ImportError("PayPal SDK no está instalado")

    config = Comercio.get_config()
    paypal_config = config.get_paypal_config()

    paypalrestsdk.configure({
        "mode": paypal_config['mode'],
        "client_id": paypal_config['client_id'],
        "client_secret": paypal_config['client_secret']
    })


def process_paypal_payment(order_data):
    """Process PayPal payment."""
    if not PAYPAL_AVAILABLE:
        flash('PayPal no está disponible en este momento. Use otro método de pago.', 'error')
        return redirect(url_for('checkout.index'))

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
    """
    Process PayU payment (Latin America payment gateway).

    PayU is a popular payment gateway in Latin America.
    Docs: https://developers.payulatam.com/latam/en/docs/integrations.html
    """
    config = Comercio.get_config()

    # Get PayU configuration from environment or database
    payu_merchant_id = current_app.config.get('PAYU_MERCHANT_ID', '')
    payu_api_key = current_app.config.get('PAYU_API_KEY', '')
    payu_account_id = current_app.config.get('PAYU_ACCOUNT_ID', '')
    payu_mode = current_app.config.get('PAYU_MODE', 'test')  # test or production

    if not all([payu_merchant_id, payu_api_key, payu_account_id]):
        flash('PayU no está configurado correctamente. Contacte al administrador.', 'error')
        return redirect(url_for('checkout.index'))

    cart_items = order_data['cart_items']
    subtotal = calculate_cart_total(cart_items)

    # Calculate totals
    tax = config.calculate_tax(subtotal)
    shipping = config.calculate_shipping(order_data['pais'])
    total = subtotal + tax + shipping

    # Create order with pending status
    order_id = f"PAYU-{order_data['user_id']}-{int(datetime.now().timestamp())}"
    cupon_info = get_coupon_from_session()

    success, message, orders = create_order_from_cart(
        order_data['user_id'],
        cart_items,
        order_data['direccion'],
        order_data['pais'],
        'payu',
        order_id,
        estado='pendiente',
        cupon_info=cupon_info
    )

    if not success:
        flash(f'Error al procesar la orden: {message}', 'error')
        return redirect(url_for('checkout.index'))

    # Clear coupon from session
    session.pop('applied_coupon', None)

    # Generate signature for PayU
    # Signature = md5(ApiKey~merchantId~referenceCode~amount~currency)
    reference_code = order_id
    amount = str(round(total, 2))
    currency = "USD"  # or get from config

    signature_string = f"{payu_api_key}~{payu_merchant_id}~{reference_code}~{amount}~{currency}"
    signature = hashlib.md5(signature_string.encode()).hexdigest()

    # PayU configuration
    payu_config = {
        'merchant_id': payu_merchant_id,
        'account_id': payu_account_id,
        'mode': payu_mode,
        'reference_code': reference_code,
        'description': f'Compra en Tienda Virtual - {reference_code}',
        'amount': amount,
        'tax': str(round(tax, 2)),
        'tax_return_base': str(round(subtotal, 2)),
        'currency': currency,
        'signature': signature,
        'buyer_email': order_data.get('email', ''),
        'response_url': url_for('checkout.payu_response', _external=True),
        'confirmation_url': url_for('checkout.payu_confirmation', _external=True)
    }

    # Return payment page with PayU form
    return render_template('checkout/payu.html',
                         order_id=order_id,
                         total=total,
                         payu_config=payu_config)


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
                # Decrement stock ONLY if payment is confirmed (procesando, entregado, enviado)
                # Do NOT decrement for 'pendiente' status (waiting for payment confirmation)
                should_decrement_stock = estado in ['procesando', 'entregado', 'enviado', 'completado']

                if should_decrement_stock:
                    stock_anterior = producto.stock
                    if not producto.decrementar_stock(item['cantidad']):
                        db.session.rollback()
                        return False, f"Error al decrementar stock del producto '{producto.titulo}'", None

                    # Registrar movimiento de stock para auditoría
                    try:
                        from app.models.stock_movement import StockMovement
                        movimiento = StockMovement.registrar_venta(
                            producto_id=producto.id,
                            orden_id=None,  # Se asignará después del commit
                            cantidad=item['cantidad'],
                            stock_anterior=stock_anterior,
                            stock_nuevo=producto.stock,
                            razon=f"Venta por {metodo}"
                        )
                        db.session.add(movimiento)
                    except ImportError:
                        pass  # Si el modelo no existe aún, continuar

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
                # NOTE: NO incrementar aquí, se hace en webhooks
                # if estado == 'procesando':
                #     producto.increment_sales()

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


# ===========================
# Payment Webhooks/IPN Handlers
# ===========================

def validate_paypal_ipn(ipn_data):
    """
    Validate PayPal IPN (Instant Payment Notification).

    Args:
        ipn_data: Dictionary with IPN data from PayPal

    Returns:
        bool: True if IPN is valid
    """
    # Add cmd=_notify-validate to the data
    validate_data = ipn_data.copy()
    validate_data['cmd'] = '_notify-validate'

    # Get PayPal IPN validation URL
    config = Comercio.get_config()
    paypal_config = config.get_paypal_config()
    ipn_url = "https://ipnpb.paypal.com/cgi-bin/webscr" if paypal_config['mode'] == 'live' else "https://ipnpb.sandbox.paypal.com/cgi-bin/webscr"

    try:
        # Send back to PayPal for validation
        response = requests.post(ipn_url, data=validate_data, timeout=10)
        return response.text == 'VERIFIED'
    except Exception as e:
        current_app.logger.error(f"PayPal IPN validation error: {e}")
        return False


def process_paypal_ipn(ipn_data):
    """
    Process PayPal IPN notification.

    Args:
        ipn_data: Dictionary with IPN data

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Validate IPN first
        if not validate_paypal_ipn(ipn_data):
            return False, "IPN validation failed"

        payment_status = ipn_data.get('payment_status', '')
        txn_id = ipn_data.get('txn_id', '')
        receiver_email = ipn_data.get('receiver_email', '')
        mc_gross = float(ipn_data.get('mc_gross', 0))
        mc_currency = ipn_data.get('mc_currency', '')
        custom = ipn_data.get('custom', '')  # Our order ID

        # Verify receiver email matches our PayPal account
        config = Comercio.get_config()
        paypal_config = config.get_paypal_config()
        # Note: In production, verify receiver_email matches our PayPal account email

        # Find orders with this payment_id
        orders = Compra.query.filter_by(detalle=f'%{custom}%').all()

        if not orders:
            current_app.logger.warning(f"No orders found for PayPal IPN: {custom}")
            return False, f"No orders found for reference: {custom}"

        # Update order status based on payment status
        if payment_status == 'Completed':
            for order in orders:
                if order.estado != 'procesando':
                    # Decrement stock when payment is confirmed
                    producto = Producto.query.with_for_update().get(order.id_producto)
                    if producto and not producto.is_virtual():
                        if producto.tiene_stock(order.cantidad):
                            stock_anterior = producto.stock
                            producto.decrementar_stock(order.cantidad)
                            producto.increment_sales()

                            # Registrar movimiento de stock
                            try:
                                from app.models.stock_movement import StockMovement
                                movimiento = StockMovement.registrar_venta(
                                    producto_id=producto.id,
                                    orden_id=order.id,
                                    cantidad=order.cantidad,
                                    stock_anterior=stock_anterior,
                                    stock_nuevo=producto.stock,
                                    razon=f'Pago confirmado por webhook'
                                )
                                db.session.add(movimiento)
                            except ImportError:
                                pass
                        else:
                            # Stock is not available, cancel order
                            order.estado = 'cancelado'
                            detalle = json.loads(order.detalle) if order.detalle else {}
                            detalle['cancel_reason'] = f'Stock insuficiente al confirmar pago. Solo quedan {producto.stock} unidades.'
                            order.detalle = json.dumps(detalle)
                            continue

                    order.estado = 'procesando'
                    # Update detalle with transaction ID
                    detalle = json.loads(order.detalle) if order.detalle else {}
                    detalle['txn_id'] = txn_id
                    detalle['payment_status'] = payment_status
                    order.detalle = json.dumps(detalle)

                    # Increment notifications
                    Notificacion.increment_new_sales()

            db.session.commit()
            return True, f"Payment completed for {len(orders)} orders"

        elif payment_status in ['Pending', 'Processing']:
            # Keep as pending
            return True, "Payment pending"

        elif payment_status in ['Denied', 'Expired', 'Failed', 'Voided']:
            for order in orders:
                order.estado = 'cancelado'
            db.session.commit()
            return True, f"Payment {payment_status.lower()} - orders cancelled"

        elif payment_status == 'Refunded':
            for order in orders:
                order.estado = 'reembolsado'
            db.session.commit()
            return True, "Payment refunded"

        else:
            current_app.logger.warning(f"Unknown PayPal payment status: {payment_status}")
            return False, f"Unknown payment status: {payment_status}"

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"PayPal IPN processing error: {e}")
        return False, str(e)


def validate_payu_signature(data, signature, api_key):
    """
    Validate PayU confirmation signature.

    Signature format: md5(ApiKey~merchantId~referenceCode~value~currency~transactionState)
    """
    merchant_id = data.get('merchant_id', '')
    reference_code = data.get('reference_sale', '')
    value = data.get('value', '')
    currency = data.get('currency', '')
    state_pol = data.get('state_pol', '')  # Transaction state

    # Build signature string
    signature_string = f"{api_key}~{merchant_id}~{reference_code}~{value}~{currency}~{state_pol}"
    expected_signature = hashlib.md5(signature_string.encode()).hexdigest()

    return signature == expected_signature


def process_payu_confirmation(data):
    """
    Process PayU confirmation (webhook).

    Args:
        data: Dictionary with confirmation data

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Get API key from config
        api_key = current_app.config.get('PAYU_API_KEY', '')
        signature = data.get('sign', '')

        # Validate signature
        if not validate_payu_signature(data, signature, api_key):
            return False, "Invalid signature"

        reference_code = data.get('reference_sale', '')
        state_pol = data.get('state_pol', '')  # 4=approved, 6=declined, 5=expired, 7=pending
        transaction_id = data.get('transaction_id', '')
        value = data.get('value', '')

        # Find orders
        orders = Compra.query.filter(Compra.detalle.like(f'%{reference_code}%')).all()

        if not orders:
            current_app.logger.warning(f"No orders found for PayU confirmation: {reference_code}")
            return False, f"No orders found for reference: {reference_code}"

        # Update order status
        if state_pol == '4':  # Approved
            for order in orders:
                if order.estado != 'procesando':
                    # Decrement stock when payment is confirmed
                    producto = Producto.query.with_for_update().get(order.id_producto)
                    if producto and not producto.is_virtual():
                        if producto.tiene_stock(order.cantidad):
                            stock_anterior = producto.stock
                            producto.decrementar_stock(order.cantidad)
                            producto.increment_sales()

                            # Registrar movimiento de stock
                            try:
                                from app.models.stock_movement import StockMovement
                                movimiento = StockMovement.registrar_venta(
                                    producto_id=producto.id,
                                    orden_id=order.id,
                                    cantidad=order.cantidad,
                                    stock_anterior=stock_anterior,
                                    stock_nuevo=producto.stock,
                                    razon=f'Pago confirmado por webhook'
                                )
                                db.session.add(movimiento)
                            except ImportError:
                                pass
                        else:
                            # Stock is not available, cancel order
                            order.estado = 'cancelado'
                            detalle = json.loads(order.detalle) if order.detalle else {}
                            detalle['cancel_reason'] = f'Stock insuficiente al confirmar pago. Solo quedan {producto.stock} unidades.'
                            order.detalle = json.dumps(detalle)
                            continue

                    order.estado = 'procesando'
                    detalle = json.loads(order.detalle) if order.detalle else {}
                    detalle['transaction_id'] = transaction_id
                    detalle['payu_state'] = state_pol
                    order.detalle = json.dumps(detalle)

                    # Increment notifications
                    Notificacion.increment_new_sales()

            db.session.commit()
            return True, f"Payment approved for {len(orders)} orders"

        elif state_pol == '7':  # Pending
            return True, "Payment pending"

        elif state_pol in ['6', '5']:  # Declined or Expired
            for order in orders:
                order.estado = 'cancelado'
            db.session.commit()
            return True, f"Payment declined/expired - orders cancelled"

        else:
            current_app.logger.warning(f"Unknown PayU state: {state_pol}")
            return False, f"Unknown payment state: {state_pol}"

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"PayU confirmation error: {e}")
        return False, str(e)


def process_paymentez_webhook(data):
    """
    Process Paymentez webhook notification.

    Args:
        data: Dictionary with webhook data

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Validate webhook signature if provided
        # Paymentez uses HMAC-SHA256 for signature validation

        status = data.get('transaction', {}).get('status', '')
        order_id = data.get('transaction', {}).get('dev_reference', '')
        transaction_id = data.get('transaction', {}).get('id', '')

        # Find orders
        orders = Compra.query.filter(Compra.detalle.like(f'%{order_id}%')).all()

        if not orders:
            return False, f"No orders found for reference: {order_id}"

        # Update status
        if status == 'success':
            for order in orders:
                if order.estado != 'procesando':
                    # Decrement stock when payment is confirmed
                    producto = Producto.query.with_for_update().get(order.id_producto)
                    if producto and not producto.is_virtual():
                        if producto.tiene_stock(order.cantidad):
                            stock_anterior = producto.stock
                            producto.decrementar_stock(order.cantidad)
                            producto.increment_sales()

                            # Registrar movimiento de stock
                            try:
                                from app.models.stock_movement import StockMovement
                                movimiento = StockMovement.registrar_venta(
                                    producto_id=producto.id,
                                    orden_id=order.id,
                                    cantidad=order.cantidad,
                                    stock_anterior=stock_anterior,
                                    stock_nuevo=producto.stock,
                                    razon=f'Pago confirmado por webhook'
                                )
                                db.session.add(movimiento)
                            except ImportError:
                                pass
                        else:
                            # Stock is not available, cancel order
                            order.estado = 'cancelado'
                            detalle = json.loads(order.detalle) if order.detalle else {}
                            detalle['cancel_reason'] = f'Stock insuficiente al confirmar pago. Solo quedan {producto.stock} unidades.'
                            order.detalle = json.dumps(detalle)
                            continue

                    order.estado = 'procesando'
                    detalle = json.loads(order.detalle) if order.detalle else {}
                    detalle['transaction_id'] = transaction_id
                    detalle['paymentez_status'] = status
                    order.detalle = json.dumps(detalle)

                    # Increment notifications
                    Notificacion.increment_new_sales()

            db.session.commit()
            return True, "Payment successful"

        elif status == 'pending':
            return True, "Payment pending"

        elif status in ['failure', 'cancelled']:
            for order in orders:
                order.estado = 'cancelado'
            db.session.commit()
            return True, "Payment failed - orders cancelled"

        else:
            return False, f"Unknown status: {status}"

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Paymentez webhook error: {e}")
        return False, str(e)


def process_datafast_callback(data):
    """
    Process Datafast callback/response.

    Args:
        data: Dictionary with callback data

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Datafast specific fields
        response_code = data.get('cd_response', '')
        order_id = data.get('nb_order', '')
        transaction_id = data.get('cd_transaction', '')

        # Find orders
        orders = Compra.query.filter(Compra.detalle.like(f'%{order_id}%')).all()

        if not orders:
            return False, f"No orders found for reference: {order_id}"

        # Response code 00 = Approved
        if response_code == '00':
            for order in orders:
                if order.estado != 'procesando':
                    # Decrement stock when payment is confirmed
                    producto = Producto.query.with_for_update().get(order.id_producto)
                    if producto and not producto.is_virtual():
                        if producto.tiene_stock(order.cantidad):
                            stock_anterior = producto.stock
                            producto.decrementar_stock(order.cantidad)
                            producto.increment_sales()

                            # Registrar movimiento de stock
                            try:
                                from app.models.stock_movement import StockMovement
                                movimiento = StockMovement.registrar_venta(
                                    producto_id=producto.id,
                                    orden_id=order.id,
                                    cantidad=order.cantidad,
                                    stock_anterior=stock_anterior,
                                    stock_nuevo=producto.stock,
                                    razon=f'Pago confirmado por webhook'
                                )
                                db.session.add(movimiento)
                            except ImportError:
                                pass
                        else:
                            # Stock is not available, cancel order
                            order.estado = 'cancelado'
                            detalle = json.loads(order.detalle) if order.detalle else {}
                            detalle['cancel_reason'] = f'Stock insuficiente al confirmar pago. Solo quedan {producto.stock} unidades.'
                            order.detalle = json.dumps(detalle)
                            continue

                    order.estado = 'procesando'
                    detalle = json.loads(order.detalle) if order.detalle else {}
                    detalle['transaction_id'] = transaction_id
                    detalle['datafast_response'] = response_code
                    order.detalle = json.dumps(detalle)

                    # Increment notifications
                    Notificacion.increment_new_sales()

            db.session.commit()
            return True, "Payment approved"

        else:
            # Any other response code is declined/failed
            for order in orders:
                order.estado = 'cancelado'
            db.session.commit()
            return True, f"Payment declined (code: {response_code})"

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Datafast callback error: {e}")
        return False, str(e)
