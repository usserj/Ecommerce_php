"""
Configuración del proyecto Flask Ecommerce
Migrado desde PHP a Python/Flask
"""
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """Configuración base"""

    # Secret Key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-CHANGE-IN-PRODUCTION-2024'

    # Database Configuration
    # MySQL connection string: mysql+pymysql://user:password@localhost/dbname
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:@localhost/ecommerce_flask'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set to True for SQL debugging

    # Upload Configuration
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Image Sizes (from PHP project)
    IMAGE_SIZES = {
        'portada': (1280, 720),      # Header/banner images
        'principal': (400, 450),     # Main product images
        'oferta': (640, 430),        # Offer images
        'multimedia': (1000, 1000),  # Gallery images
    }

    # Email Configuration (PHPMailer → Flask-Mail)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'cursos@tutorialesatualcance.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or \
        ('Tienda Virtual', 'cursos@tutorialesatualcance.com')

    # Timezone (from PHP: America/Bogota)
    TIMEZONE = 'America/Bogota'

    # PayPal Configuration (from PHP PayPal SDK)
    PAYPAL_MODE = os.environ.get('PAYPAL_MODE') or 'sandbox'  # sandbox or live
    PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
    PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET')
    PAYPAL_RETURN_URL = os.environ.get('PAYPAL_RETURN_URL') or 'http://localhost:5000/pago/exito'
    PAYPAL_CANCEL_URL = os.environ.get('PAYPAL_CANCEL_URL') or 'http://localhost:5000/carrito-de-compras'

    # PayU Configuration (from PHP PayU)
    PAYU_MODE = os.environ.get('PAYU_MODE') or 'sandbox'  # sandbox or production
    PAYU_MERCHANT_ID = os.environ.get('PAYU_MERCHANT_ID')
    PAYU_ACCOUNT_ID = os.environ.get('PAYU_ACCOUNT_ID')
    PAYU_API_KEY = os.environ.get('PAYU_API_KEY')
    PAYU_TEST_URL = 'https://sandbox.checkout.payulatam.com/ppp-web-gateway-payu'
    PAYU_PRODUCTION_URL = 'https://checkout.payulatam.com/ppp-web-gateway-payu'

    # Currency Conversion API (from PHP project)
    CURRENCY_API_KEY = os.environ.get('CURRENCY_API_KEY') or 'a01ebaf9a1c69eb4ff79'
    CURRENCY_API_URL = 'https://free.currconv.com/api/v7/convert'

    # Google OAuth Configuration
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = 'https://accounts.google.com/.well-known/openid-configuration'

    # Facebook SDK Configuration
    FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
    FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')

    # Session Configuration
    SESSION_COOKIE_NAME = 'ecommerce_session'
    SESSION_COOKIE_SECURE = False  # Set True in production with HTTPS
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

    # Pagination
    ITEMS_PER_PAGE = 20

    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or SECRET_KEY


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Show SQL queries
    TEMPLATES_AUTO_RELOAD = True


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Override database with production credentials
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Force HTTPS
    PREFERRED_URL_SCHEME = 'https'


class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory database for tests


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
