"""Shopping cart routes."""
from flask import render_template, request, jsonify, session, redirect, url_for
from app.blueprints.cart import cart_bp
from app.models.product import Producto


@cart_bp.route('/')
def index():
    """Cart page."""
    cart_items = session.get('cart', [])

    # Get product details
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

    # Calculate tax and shipping (basic example)
    from app.models.comercio import Comercio
    config = Comercio.get_config()
    tax = config.calculate_tax(subtotal)
    shipping = config.envioNacional if subtotal > 0 else 0
    total = subtotal + tax + shipping

    return render_template('cart/cart.html',
                         products=products,
                         subtotal=subtotal,
                         tax=tax,
                         shipping=shipping,
                         total=total)


@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    """Add product to cart (AJAX)."""
    data = request.get_json()
    producto_id = data.get('producto_id')
    cantidad = data.get('cantidad', 1)

    if not producto_id:
        return jsonify({'success': False, 'message': 'Producto inválido'}), 400

    # Verify product exists
    producto = Producto.query.get(producto_id)
    if not producto or producto.estado != 1:
        return jsonify({'success': False, 'message': 'Producto no disponible'}), 404

    # Get or create cart
    cart = session.get('cart', [])

    # Check if product already in cart
    found = False
    for item in cart:
        if item['id'] == producto_id:
            item['cantidad'] += cantidad
            found = True
            break

    if not found:
        cart.append({
            'id': producto_id,
            'cantidad': cantidad
        })

    session['cart'] = cart
    session.modified = True

    return jsonify({
        'success': True,
        'cart_count': len(cart),
        'message': 'Producto añadido al carrito'
    })


@cart_bp.route('/update', methods=['POST'])
def update_cart():
    """Update cart item quantity."""
    data = request.get_json()
    producto_id = data.get('producto_id')
    cantidad = data.get('cantidad', 1)

    cart = session.get('cart', [])

    for item in cart:
        if item['id'] == producto_id:
            if cantidad <= 0:
                cart.remove(item)
            else:
                item['cantidad'] = cantidad
            break

    session['cart'] = cart
    session.modified = True

    return jsonify({'success': True})


@cart_bp.route('/remove/<int:producto_id>', methods=['POST'])
def remove_from_cart(producto_id):
    """Remove product from cart."""
    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != producto_id]

    session['cart'] = cart
    session.modified = True

    return jsonify({'success': True})


@cart_bp.route('/clear', methods=['POST'])
def clear_cart():
    """Clear all cart."""
    session['cart'] = []
    session.modified = True

    return jsonify({'success': True})
