"""Flask extensions initialization."""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect

# Optional imports - graceful degradation
try:
    from flask_mail import Mail
    mail = Mail()
    HAS_MAIL = True
except ImportError:
    mail = None
    HAS_MAIL = False

try:
    from flask_caching import Cache
    cache = Cache()
    HAS_CACHE = True
except ImportError:
    cache = None
    HAS_CACHE = False

try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    HAS_LIMITER = True
except ImportError:
    limiter = None
    HAS_LIMITER = False

try:
    from authlib.integrations.flask_client import OAuth
    oauth = OAuth()
    HAS_OAUTH = True
except ImportError:
    oauth = None
    HAS_OAUTH = False

# Initialize core extensions (always required)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()


def init_extensions(app):
    """Initialize Flask extensions."""
    # Core extensions (always initialized)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    # Optional extensions
    if HAS_MAIL and mail:
        mail.init_app(app)

    if HAS_CACHE and cache:
        cache.init_app(app)

    if HAS_LIMITER and limiter:
        limiter.init_app(app)

    if HAS_OAUTH and oauth:
        oauth.init_app(app)

    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'

    # User loader callback
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # OAuth Providers (only if OAuth is available)
    if HAS_OAUTH and oauth and app.config.get('GOOGLE_CLIENT_ID'):
        oauth.register(
            name='google',
            client_id=app.config['GOOGLE_CLIENT_ID'],
            client_secret=app.config['GOOGLE_CLIENT_SECRET'],
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'}
        )

        if app.config.get('FACEBOOK_CLIENT_ID'):
            oauth.register(
                name='facebook',
                client_id=app.config['FACEBOOK_CLIENT_ID'],
                client_secret=app.config['FACEBOOK_CLIENT_SECRET'],
                access_token_url='https://graph.facebook.com/oauth/access_token',
                access_token_params=None,
                authorize_url='https://www.facebook.com/dialog/oauth',
                authorize_params=None,
                api_base_url='https://graph.facebook.com/',
                client_kwargs={'scope': 'email'}
            )
