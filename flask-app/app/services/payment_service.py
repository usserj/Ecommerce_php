"""Payment service for PayPal and PayU."""
from flask import current_app, url_for, redirect, flash
import paypalrestsdk
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


def create_order_from_cart(user_id, cart_items, direccion, pais, metodo, payment_id):
    """Create order records from cart."""
    for item in cart_items:
        producto = Producto.query.get(item['id'])
        if producto:
            compra = Compra(
                id_usuario=user_id,
                id_producto=producto.id,
                envio=0,  # TODO: Calculate shipping
                metodo=metodo,
                email=Producto.query.get(user_id).email,
                direccion=direccion,
                pais=pais,
                cantidad=item['cantidad'],
                detalle=payment_id,
                pago=str(producto.get_price() * item['cantidad'])
            )
            db.session.add(compra)

            # Update product sales
            producto.increment_sales()

    # Update notifications
    Notificacion.increment_new_sales()

    db.session.commit()
