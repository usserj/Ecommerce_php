"""
Aplicación Flask Ecommerce
Migrado desde PHP a Python/Flask

Estructura:
- admin: Panel de administración (backend)
- shop: Tienda para clientes (frontend)
- api: Endpoints REST para AJAX
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from config import config
import os

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()


def create_app(config_name='default'):
    """
    Factory pattern para crear la aplicación Flask

    Args:
        config_name: 'development', 'production', 'testing', o 'default'

    Returns:
        Aplicación Flask configurada
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Inicializar extensiones con app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    # Configuración de Flask-Login
    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Por favor inicie sesión para acceder a esta página'
    login_manager.login_message_category = 'warning'
    login_manager.session_protection = 'strong'

    # User loader para Flask-Login
    from app.models import Administrador, Usuario

    @login_manager.user_loader
    def load_user(user_id):
        """Carga el usuario desde la sesión"""
        # Intentar cargar como administrador primero
        admin = Administrador.query.get(int(user_id))
        if admin:
            return admin
        # Si no, intentar cargar como usuario normal
        return Usuario.query.get(int(user_id))

    # Registrar blueprints

    # Admin Blueprint (Backend - Panel de administración)
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/backend')

    # Shop Blueprint (Frontend - Tienda para clientes)
    from app.shop import bp as shop_bp
    app.register_blueprint(shop_bp)

    # API Blueprint (Endpoints REST para AJAX)
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Manejadores de errores
    @app.errorhandler(404)
    def not_found_error(error):
        """Página 404 personalizada"""
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Página 500 personalizada"""
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Context processors (variables globales para templates)
    @app.context_processor
    def inject_globals():
        """Inyecta variables globales en todos los templates"""
        from app.models import Comercio, Categoria

        # Configuración del comercio (logo, redes sociales, etc)
        comercio = Comercio.query.first()

        # Categorías para el menú
        categorias = Categoria.query.filter_by(estado=True).all()

        return {
            'comercio': comercio,
            'categorias_menu': categorias
        }

    # Crear directorio de uploads si no existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Crear subdirectorios para imágenes
    for folder in ['cabeceras', 'productos', 'ofertas', 'multimedia', 'usuarios', 'banner', 'slide']:
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], folder), exist_ok=True)

    return app
