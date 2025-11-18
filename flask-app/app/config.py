"""Flask configuration."""
import os
from datetime import timedelta


class Config:
    """Base configuration."""

    # Flask Core
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:@localhost/Ecommerce_Ec'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # PayPal Configuration
    PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'sandbox')  # sandbox or live
    PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
    PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET')

    # PayU Configuration
    PAYU_MODE = os.environ.get('PAYU_MODE', 'test')
    PAYU_MERCHANT_ID = os.environ.get('PAYU_MERCHANT_ID')
    PAYU_ACCOUNT_ID = os.environ.get('PAYU_ACCOUNT_ID')
    PAYU_API_KEY = os.environ.get('PAYU_API_KEY')

    # OAuth Configuration
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    FACEBOOK_CLIENT_ID = os.environ.get('FACEBOOK_CLIENT_ID')
    FACEBOOK_CLIENT_SECRET = os.environ.get('FACEBOOK_CLIENT_SECRET')

    # reCAPTCHA
    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')

    # Upload Configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'app/static/uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=int(os.environ.get('PERMANENT_SESSION_LIFETIME', 604800))  # 7 days
    )
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'true').lower() in ['true', 'on', '1']
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS

    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # Cache Configuration
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = 300

    # Celery Configuration
    CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    # Currency API
    CURRENCY_API_KEY = os.environ.get('CURRENCY_API_KEY')

    # Pagination
    ITEMS_PER_PAGE = 12
    ADMIN_ITEMS_PER_PAGE = 25

    # Admin Configuration
    FLASK_ADMIN_SWATCH = 'cerulean'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'

    # Security headers
    TALISMAN_FORCE_HTTPS = True
    TALISMAN_CONTENT_SECURITY_POLICY = {
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", 'cdn.jsdelivr.net', 'code.jquery.com'],
        'style-src': ["'self'", "'unsafe-inline'", 'cdn.jsdelivr.net'],
        'img-src': ["'self'", 'data:', 'https:'],
    }


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
