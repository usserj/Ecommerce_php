"""Payment service for multiple payment gateways."""
from flask import current_app, url_for, redirect, flash, render_template
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


def create_order_from_cart(user_id, cart_items, direccion, pais, metodo, payment_id, estado='pendiente'):
    """Create order records from cart."""
    from app.models.user import User
    user = User.query.get(user_id)

    for item in cart_items:
        producto = Producto.query.get(item['id'])
        if producto:
            compra = Compra(
                id_usuario=user_id,
                id_producto=producto.id,
                envio=0,  # TODO: Calculate shipping
                metodo=metodo,
                email=user.email,
                direccion=direccion,
                pais=pais,
                cantidad=item['cantidad'],
                detalle=payment_id,
                pago=float(producto.get_price() * item['cantidad']),
                estado=estado
            )
            db.session.add(compra)

            # Update product sales only if paid
            if estado == 'procesando':
                producto.increment_sales()

    # Update notifications
    if estado == 'procesando':
        Notificacion.increment_new_sales()

    db.session.commit()


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
    create_order_from_cart(
        order_data['user_id'],
        cart_items,
        order_data['direccion'],
        order_data['pais'],
        'paymentez',
        order_id,
        estado='pendiente'
    )

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
    create_order_from_cart(
        order_data['user_id'],
        cart_items,
        order_data['direccion'],
        order_data['pais'],
        'datafast',
        order_id,
        estado='pendiente'
    )

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
    create_order_from_cart(
        order_data['user_id'],
        cart_items,
        order_data['direccion'],
        order_data['pais'],
        'deuna',
        order_id,
        estado='pendiente'
    )

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
    create_order_from_cart(
        order_data['user_id'],
        cart_items,
        order_data['direccion'],
        order_data['pais'],
        'transferencia',
        order_id,
        estado='pendiente'
    )

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
    create_order_from_cart(
        order_data['user_id'],
        cart_items,
        order_data['direccion'],
        order_data['pais'],
        'transferencia_comprobante',
        order_id,
        estado='pendiente'
    )

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
