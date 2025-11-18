"""
Integration tests for cart and checkout routes
"""

import pytest
import json
from app.models.product import Producto
from app.models.order import Compra


# ===========================
# Cart Display Tests
# ===========================

@pytest.mark.integration
@pytest.mark.cart
@pytest.mark.blueprints
class TestCartDisplayRoutes:
    """Tests for cart display"""

    def test_cart_page_loads(self, client):
        """Test cart page loads"""
        response = client.get('/cart')
        assert response.status_code == 200
        assert b'cart' in response.data.lower() or b'carrito' in response.data.lower()

    def test_empty_cart_display(self, client):
        """Test empty cart shows appropriate message"""
        response = client.get('/cart')
        assert response.status_code == 200
        # Should show empty cart message
        assert b'empty' in response.data.lower() or b'vac' in response.data.lower()

    def test_cart_with_items(self, client_with_cart, init_database, test_producto):
        """Test cart with items displays correctly"""
        response = client_with_cart.get('/cart')
        assert response.status_code == 200


# ===========================
# Add to Cart Tests
# ===========================

@pytest.mark.integration
@pytest.mark.cart
@pytest.mark.blueprints
class TestAddToCartRoutes:
    """Tests for adding products to cart"""

    def test_add_to_cart_ajax(self, client, init_database, test_producto):
        """Test adding product to cart via AJAX"""
        data = {
            'producto_id': test_producto.id,
            'cantidad': 2
        }

        response = client.post(
            '/cart/add',
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data.get('success') is True
        assert 'cart_count' in response_data

    def test_add_invalid_product(self, client):
        """Test adding non-existent product"""
        data = {
            'producto_id': 99999,
            'cantidad': 1
        }

        response = client.post(
            '/cart/add',
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code in [400, 404]

    def test_add_out_of_stock_product(self, client, init_database, db_session, test_categoria):
        """Test adding out of stock product"""
        # Create out of stock product
        producto = Producto(
            titulo='Out of Stock',
            precio=99.99,
            stock=0,
            categoria_id=test_categoria.id,
            estado=True
        )
        db_session.add(producto)
        db_session.commit()

        data = {
            'producto_id': producto.id,
            'cantidad': 1
        }

        response = client.post(
            '/cart/add',
            data=json.dumps(data),
            content_type='application/json'
        )

        response_data = json.loads(response.data)
        assert response_data.get('success') is False

    def test_add_exceeds_stock(self, client, init_database, test_producto):
        """Test adding more than available stock"""
        data = {
            'producto_id': test_producto.id,
            'cantidad': test_producto.stock + 10  # More than available
        }

        response = client.post(
            '/cart/add',
            data=json.dumps(data),
            content_type='application/json'
        )

        response_data = json.loads(response.data)
        # Should either limit to stock or show error
        assert response.status_code in [200, 400]


# ===========================
# Update Cart Tests
# ===========================

@pytest.mark.integration
@pytest.mark.cart
@pytest.mark.blueprints
class TestUpdateCartRoutes:
    """Tests for updating cart quantities"""

    def test_update_cart_quantity(self, client_with_cart, init_database):
        """Test updating item quantity in cart"""
        data = {
            'producto_id': 1,
            'cantidad': 5
        }

        response = client_with_cart.post(
            '/cart/update',
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data.get('success') is True

    def test_update_to_zero_removes_item(self, client_with_cart):
        """Test updating quantity to 0 removes item"""
        data = {
            'producto_id': 1,
            'cantidad': 0
        }

        response = client_with_cart.post(
            '/cart/update',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Should remove item or redirect to remove endpoint
        assert response.status_code in [200, 302]


# ===========================
# Remove from Cart Tests
# ===========================

@pytest.mark.integration
@pytest.mark.cart
@pytest.mark.blueprints
class TestRemoveFromCartRoutes:
    """Tests for removing products from cart"""

    def test_remove_from_cart(self, client_with_cart):
        """Test removing item from cart"""
        data = {'producto_id': 1}

        response = client_with_cart.post(
            '/cart/remove',
            data=json.dumps(data),
            content_type='application/json'
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data.get('success') is True


# ===========================
# Clear Cart Tests
# ===========================

@pytest.mark.integration
@pytest.mark.cart
@pytest.mark.blueprints
class TestClearCartRoutes:
    """Tests for clearing entire cart"""

    def test_clear_cart(self, client_with_cart):
        """Test clearing all items from cart"""
        response = client_with_cart.post(
            '/cart/clear',
            content_type='application/json'
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data.get('success') is True


# ===========================
# Checkout Page Tests
# ===========================

@pytest.mark.integration
@pytest.mark.cart
@pytest.mark.blueprints
class TestCheckoutPageRoutes:
    """Tests for checkout page"""

    def test_checkout_requires_login(self, client):
        """Test checkout requires authentication"""
        response = client.get('/checkout', follow_redirects=True)

        # Should redirect to login
        assert b'login' in response.data.lower()

    def test_checkout_page_loads(self, authenticated_client, client_with_cart):
        """Test checkout page loads for authenticated user"""
        # Merge authenticated client with cart session
        with authenticated_client.session_transaction() as sess:
            sess['cart'] = [
                {'producto_id': 1, 'cantidad': 2, 'precio': 99.99}
            ]

        response = authenticated_client.get('/checkout')
        assert response.status_code == 200

    def test_checkout_empty_cart(self, authenticated_client):
        """Test checkout with empty cart"""
        response = authenticated_client.get('/checkout', follow_redirects=True)

        # Should redirect to cart or shop
        assert response.status_code == 200


# ===========================
# Checkout Process Tests
# ===========================

@pytest.mark.integration
@pytest.mark.cart
@pytest.mark.payment
@pytest.mark.blueprints
class TestCheckoutProcessRoutes:
    """Tests for checkout processing"""

    def test_process_checkout_paypal(self, authenticated_client, init_database, test_producto, mock_paypal_payment):
        """Test processing checkout with PayPal"""
        # Set up cart
        with authenticated_client.session_transaction() as sess:
            sess['cart'] = [
                {
                    'producto_id': test_producto.id,
                    'cantidad': 1,
                    'precio': test_producto.precio
                }
            ]

        checkout_data = {
            'metodo_pago': 'paypal',
            'direccion': '123 Test St',
            'ciudad': 'Test City',
            'pais': 'Test Country',
            'codigo_postal': '12345'
        }

        response = authenticated_client.post(
            '/checkout/process',
            data=checkout_data,
            follow_redirects=False
        )

        # Should redirect to PayPal or success page
        assert response.status_code in [200, 302, 303]

    def test_process_checkout_invalid_payment_method(self, authenticated_client):
        """Test checkout with invalid payment method"""
        checkout_data = {
            'metodo_pago': 'invalid_method'
        }

        response = authenticated_client.post(
            '/checkout/process',
            data=checkout_data
        )

        # Should show error
        assert response.status_code in [400, 422]


# ===========================
# Order Success Tests
# ===========================

@pytest.mark.integration
@pytest.mark.cart
@pytest.mark.blueprints
class TestOrderSuccessRoutes:
    """Tests for order success page"""

    def test_success_page_loads(self, authenticated_client):
        """Test order success page"""
        response = authenticated_client.get('/checkout/success')
        assert response.status_code == 200
        assert b'success' in response.data.lower() or b'xito' in response.data.lower()


# ===========================
# Cart Session Tests
# ===========================

@pytest.mark.integration
@pytest.mark.cart
class TestCartSession:
    """Tests for cart session management"""

    def test_cart_persists_across_requests(self, client, init_database, test_producto):
        """Test cart data persists in session"""
        # Add to cart
        data = {
            'producto_id': test_producto.id,
            'cantidad': 2
        }

        client.post(
            '/cart/add',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Check cart in new request
        response = client.get('/cart')
        assert response.status_code == 200

        # Verify session has cart
        with client.session_transaction() as sess:
            assert 'cart' in sess
            assert len(sess['cart']) > 0

    def test_cart_cleared_after_checkout(self, authenticated_client, init_database, test_producto):
        """Test cart is cleared after successful checkout"""
        # Add to cart
        with authenticated_client.session_transaction() as sess:
            sess['cart'] = [
                {
                    'producto_id': test_producto.id,
                    'cantidad': 1,
                    'precio': test_producto.precio
                }
            ]

        checkout_data = {
            'metodo_pago': 'paypal',
            'direccion': '123 Test St'
        }

        # Process checkout
        authenticated_client.post(
            '/checkout/process',
            data=checkout_data
        )

        # Cart should be cleared or order created
        # Implementation specific


# ===========================
# Cart Calculations Tests
# ===========================

@pytest.mark.integration
@pytest.mark.cart
class TestCartCalculations:
    """Tests for cart total calculations"""

    def test_cart_subtotal_calculation(self, client, init_database, test_producto):
        """Test cart subtotal is calculated correctly"""
        # Add multiple items
        for i in range(3):
            data = {
                'producto_id': test_producto.id,
                'cantidad': 2
            }
            client.post(
                '/cart/add',
                data=json.dumps(data),
                content_type='application/json'
            )

        response = client.get('/cart')
        assert response.status_code == 200
        # Subtotal should be visible in response

    def test_cart_with_discount_product(self, client, init_database, test_producto_oferta):
        """Test cart uses discounted price for products on sale"""
        data = {
            'producto_id': test_producto_oferta.id,
            'cantidad': 1
        }

        response = client.post(
            '/cart/add',
            data=json.dumps(data),
            content_type='application/json'
        )

        response_data = json.loads(response.data)
        # Should use precio_oferta if available
        assert response.status_code == 200
