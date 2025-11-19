"""Flask application factory."""
import os
from flask import Flask, render_template
from app.config import config
from app.extensions import init_extensions


def create_app(config_name=None):
    """Create and configure the Flask application.

    Args:
        config_name: Configuration name (development, testing, production)

    Returns:
        Flask application instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Register CLI commands
    register_cli_commands(app)

    # Register context processors
    register_context_processors(app)

    return app


def register_blueprints(app):
    """Register Flask blueprints."""
    from app.blueprints.main import main_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.shop import shop_bp
    from app.blueprints.cart import cart_bp
    from app.blueprints.checkout import checkout_bp
    from app.blueprints.profile import profile_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.health import health_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(shop_bp, url_prefix='/tienda')
    app.register_blueprint(cart_bp, url_prefix='/carrito')
    app.register_blueprint(checkout_bp, url_prefix='/checkout')
    app.register_blueprint(profile_bp, url_prefix='/perfil')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(health_bp)


def register_error_handlers(app):
    """Register error handlers."""

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from app.extensions import db
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403


def register_cli_commands(app):
    """Register CLI commands."""

    @app.cli.command()
    def init_db():
        """Initialize the database."""
        from app.extensions import db
        db.create_all()
        print('Database initialized successfully.')

    @app.cli.command()
    def seed_db():
        """Seed the database with initial data."""
        from scripts.seed_data import seed_all
        seed_all()
        print('Database seeded successfully.')

    @app.cli.command()
    def migrate_data():
        """Migrate data from PHP MySQL database."""
        from scripts.migrate_data import migrate_all_data
        migrate_all_data()
        print('Data migration completed successfully.')


def register_context_processors(app):
    """Register context processors."""
    from flask_login import current_user
    from app.models.categoria import Categoria
    from app.models.setting import Plantilla

    @app.context_processor
    def inject_global_data():
        """Inject global data into all templates."""
        categorias = Categoria.query.filter_by(estado=1).all() if Categoria.query.first() else []
        plantilla = Plantilla.query.first()

        cart_count = 0
        if current_user.is_authenticated:
            from flask import session
            cart_count = len(session.get('cart', []))

        return {
            'categorias': categorias,
            'plantilla': plantilla,
            'cart_count': cart_count
        }

    @app.context_processor
    def inject_admin_data():
        """Inject admin-specific data into all templates."""
        from flask import session
        from app.models.message import Mensaje

        # Get unread messages count for admin
        mensajes_no_leidos = 0
        if 'admin_id' in session:
            try:
                mensajes_no_leidos = Mensaje.contar_no_leidos('admin', session['admin_id'])
            except:
                mensajes_no_leidos = 0

        return {
            'admin_mensajes_no_leidos': mensajes_no_leidos
        }
