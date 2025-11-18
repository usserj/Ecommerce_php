"""Checkout routes."""
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.blueprints.checkout import checkout_bp
from app.models.product import Producto
from app.models.order import Compra
from app.models.notification import Notificacion
from app.extensions import db
from app.services.payment_service import process_paypal_payment, process_payu_payment


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

    for item in cart_items:
        producto = Producto.query.get(item['id'])
        if producto:
            precio = producto.get_price()
            item_total = precio * item['cantidad']
            products.append({
                'producto': producto,
                'cantidad': item['cantidad'],
                'precio': precio,
                'total': item_total
            })
            subtotal += item_total

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
    metodo_pago = request.form.get('metodo_pago')  # paypal, payu
    direccion = request.form.get('direccion')
    pais = request.form.get('pais', 'Colombia')

    if not direccion or not metodo_pago:
        flash('Complete todos los campos requeridos.', 'error')
        return redirect(url_for('checkout.index'))

    cart_items = session.get('cart', [])

    if not cart_items:
        flash('Su carrito está vacío.', 'warning')
        return redirect(url_for('shop.index'))

    # Prepare order data
    order_data = {
        'user_id': current_user.id,
        'cart_items': cart_items,
        'direccion': direccion,
        'pais': pais,
        'metodo': metodo_pago
    }

    # Process payment based on method
    if metodo_pago == 'paypal':
        return process_paypal_payment(order_data)
    elif metodo_pago == 'payu':
        return process_payu_payment(order_data)
    else:
        flash('Método de pago no válido.', 'error')
        return redirect(url_for('checkout.index'))


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
