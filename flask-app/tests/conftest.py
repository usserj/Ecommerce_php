"""
Pytest configuration and fixtures
"""

import os
import sys
import pytest
from datetime import datetime
from pathlib import Path

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app, db
from app.models.user import Usuario
from app.models.admin import Administrador
from app.models.product import Producto
from app.models.categoria import Categoria, Subcategoria
from app.models.order import Compra
from app.models.comment import Comentario
from app.models.wishlist import Deseo
from app.models.comercio import Comercio
from app.models.setting import Plantilla


# ===========================
# Application Fixtures
# ===========================

@pytest.fixture(scope='session')
def app():
    """Create application instance for testing"""
    # Set testing config
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['SECRET_KEY'] = 'test-secret-key'
    os.environ['WTF_CSRF_ENABLED'] = 'False'

    app = create_app('testing')

    # Additional test config
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['LOGIN_DISABLED'] = False

    yield app


@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create CLI test runner"""
    return app.test_cli_runner()


# ===========================
# Database Fixtures
# ===========================

@pytest.fixture(scope='function')
def db_session(app):
    """Create database session for testing"""
    with app.app_context():
        # Create all tables
        db.create_all()

        yield db.session

        # Cleanup
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def init_database(db_session):
    """Initialize database with test data"""
    # Create test categoria
    categoria = Categoria(
        nombre='Electrónica',
        descripcion='Productos electrónicos',
        estado=True
    )
    db_session.add(categoria)
    db_session.commit()

    # Create test subcategoria
    subcategoria = Subcategoria(
        nombre='Smartphones',
        descripcion='Teléfonos inteligentes',
        categoria_id=categoria.id,
        estado=True
    )
    db_session.add(subcategoria)
    db_session.commit()

    # Create test comercio settings
    comercio = Comercio(
        nombre='Tienda Test',
        email='test@tienda.com',
        telefono='123456789',
        moneda='USD',
        impuesto=10.0,
        costo_envio=5.0
    )
    db_session.add(comercio)

    # Create test plantilla
    plantilla = Plantilla(
        titulo='Tienda Test',
        color_primario='#007bff',
        color_secundario='#6c757d'
    )
    db_session.add(plantilla)

    db_session.commit()

    yield db_session


# ===========================
# User Fixtures
# ===========================

@pytest.fixture(scope='function')
def test_user(db_session):
    """Create test user"""
    user = Usuario(
        nombre='Test User',
        email='test@example.com',
        verificado=True,
        activo=True
    )
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope='function')
def test_admin(db_session):
    """Create test admin"""
    admin = Administrador(
        nombre='Test Admin',
        email='admin@example.com',
        rol='admin',
        activo=True
    )
    admin.set_password('admin123')
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture(scope='function')
def authenticated_client(client, test_user):
    """Create authenticated test client"""
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
        session['_fresh'] = True
    return client


@pytest.fixture(scope='function')
def admin_client(client, test_admin):
    """Create authenticated admin client"""
    with client.session_transaction() as session:
        session['admin_id'] = test_admin.id
        session['_fresh'] = True
    return client


# ===========================
# Product Fixtures
# ===========================

@pytest.fixture(scope='function')
def test_categoria(db_session):
    """Create test categoria"""
    categoria = Categoria(
        nombre='Test Category',
        descripcion='Test category description',
        estado=True
    )
    db_session.add(categoria)
    db_session.commit()
    return categoria


@pytest.fixture(scope='function')
def test_producto(db_session, test_categoria):
    """Create test producto"""
    producto = Producto(
        titulo='Test Product',
        descripcion='Test product description',
        precio=99.99,
        stock=10,
        categoria_id=test_categoria.id,
        estado=True,
        destacado=True
    )
    db_session.add(producto)
    db_session.commit()
    return producto


@pytest.fixture(scope='function')
def test_producto_oferta(db_session, test_categoria):
    """Create test producto with offer"""
    producto = Producto(
        titulo='Product On Sale',
        descripcion='Product with discount',
        precio=100.0,
        precio_oferta=75.0,
        stock=5,
        categoria_id=test_categoria.id,
        estado=True
    )
    db_session.add(producto)
    db_session.commit()
    return producto


# ===========================
# Order Fixtures
# ===========================

@pytest.fixture(scope='function')
def test_compra(db_session, test_user, test_producto):
    """Create test compra"""
    compra = Compra(
        usuario_id=test_user.id,
        producto_id=test_producto.id,
        cantidad=2,
        precio_unitario=test_producto.precio,
        total=test_producto.precio * 2,
        metodo_pago='paypal',
        estado='completado'
    )
    db_session.add(compra)
    db_session.commit()
    return compra


# ===========================
# Comment Fixtures
# ===========================

@pytest.fixture(scope='function')
def test_comentario(db_session, test_user, test_producto):
    """Create test comentario"""
    comentario = Comentario(
        usuario_id=test_user.id,
        producto_id=test_producto.id,
        comentario='Great product!',
        calificacion=5,
        estado=True
    )
    db_session.add(comentario)
    db_session.commit()
    return comentario


# ===========================
# Wishlist Fixtures
# ===========================

@pytest.fixture(scope='function')
def test_deseo(db_session, test_user, test_producto):
    """Create test wishlist item"""
    deseo = Deseo(
        usuario_id=test_user.id,
        producto_id=test_producto.id
    )
    db_session.add(deseo)
    db_session.commit()
    return deseo


# ===========================
# Utility Fixtures
# ===========================

@pytest.fixture(scope='function')
def sample_cart_data():
    """Sample cart data for testing"""
    return {
        'items': [
            {
                'producto_id': 1,
                'cantidad': 2,
                'precio': 99.99
            },
            {
                'producto_id': 2,
                'cantidad': 1,
                'precio': 49.99
            }
        ],
        'subtotal': 249.97,
        'tax': 24.99,
        'shipping': 5.00,
        'total': 279.96
    }


@pytest.fixture(scope='function')
def sample_user_data():
    """Sample user registration data"""
    return {
        'nombre': 'John Doe',
        'email': 'john@example.com',
        'password': 'SecurePass123!',
        'password_confirm': 'SecurePass123!'
    }


@pytest.fixture(scope='function')
def sample_product_data():
    """Sample product data"""
    return {
        'titulo': 'New Product',
        'descripcion': 'Product description',
        'precio': 199.99,
        'precio_oferta': 149.99,
        'stock': 20,
        'categoria_id': 1,
        'estado': True,
        'destacado': False
    }


# ===========================
# Mock Fixtures
# ===========================

@pytest.fixture
def mock_paypal_payment(mocker):
    """Mock PayPal payment"""
    mock_payment = mocker.Mock()
    mock_payment.create.return_value = True
    mock_payment.id = 'PAYPAL-PAYMENT-ID'
    mock_payment.links = [
        {'rel': 'approval_url', 'href': 'https://paypal.com/approval'}
    ]
    return mock_payment


@pytest.fixture
def mock_email_send(mocker):
    """Mock email sending"""
    return mocker.patch('app.services.email_service.send_email')


@pytest.fixture
def mock_oauth_google(mocker):
    """Mock Google OAuth"""
    mock = mocker.patch('app.extensions.oauth.google.authorize_access_token')
    mock.return_value = {
        'userinfo': {
            'email': 'user@gmail.com',
            'name': 'Google User',
            'picture': 'https://example.com/photo.jpg',
            'sub': 'google-user-id-123'
        }
    }
    return mock


@pytest.fixture
def mock_oauth_facebook(mocker):
    """Mock Facebook OAuth"""
    mock = mocker.patch('app.extensions.oauth.facebook.authorize_access_token')
    mock.return_value = {
        'userinfo': {
            'email': 'user@facebook.com',
            'name': 'Facebook User',
            'picture': {'data': {'url': 'https://example.com/photo.jpg'}},
            'id': 'facebook-user-id-123'
        }
    }
    return mock


# ===========================
# Session Fixtures
# ===========================

@pytest.fixture
def client_with_cart(client):
    """Client with cart session"""
    with client.session_transaction() as session:
        session['cart'] = [
            {'producto_id': 1, 'cantidad': 2, 'precio': 99.99},
            {'producto_id': 2, 'cantidad': 1, 'precio': 49.99}
        ]
    return client


# ===========================
# File Fixtures
# ===========================

@pytest.fixture
def temp_upload_dir(tmp_path):
    """Create temporary upload directory"""
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    return upload_dir


@pytest.fixture
def sample_image_file():
    """Create sample image file for upload testing"""
    from io import BytesIO
    data = BytesIO(b"fake image data")
    data.name = 'test_image.jpg'
    return data


# ===========================
# Cleanup
# ===========================

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup after each test"""
    yield
    # Any cleanup code here
