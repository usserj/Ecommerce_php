"""Database initialization utilities."""
import os
import pymysql
from sqlalchemy import create_engine, text
from urllib.parse import urlparse


def ensure_database_exists(database_url):
    """
    Ensure the database exists, create it if it doesn't.

    Args:
        database_url: SQLAlchemy database URL

    Returns:
        bool: True if database exists or was created successfully
    """
    try:
        # Parse the database URL
        parsed = urlparse(database_url)

        # Extract connection details
        username = parsed.username or 'root'
        password = parsed.password or ''
        host = parsed.hostname or 'localhost'
        port = parsed.port or 3306
        database = parsed.path.lstrip('/')

        # Connect without specifying database
        connection = pymysql.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            charset='utf8mb4'
        )

        try:
            with connection.cursor() as cursor:
                # Check if database exists
                cursor.execute(
                    "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s",
                    (database,)
                )
                result = cursor.fetchone()

                if not result:
                    # Create database
                    print(f"Creating database '{database}'...")
                    cursor.execute(
                        f"CREATE DATABASE `{database}` "
                        f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                    )
                    connection.commit()
                    print(f"Database '{database}' created successfully!")
                else:
                    print(f"Database '{database}' already exists.")

            return True

        finally:
            connection.close()

    except Exception as e:
        print(f"Error ensuring database exists: {e}")
        return False


def initialize_tables(app):
    """
    Initialize database tables using migrations or create_all.

    Args:
        app: Flask application instance
    """
    from app.extensions import db

    try:
        # Check if migrations directory exists
        migrations_dir = os.path.join(app.root_path, '..', 'migrations')

        if os.path.exists(migrations_dir):
            print("Migrations directory found. Run 'flask db upgrade' to create tables.")
        else:
            print("Creating database tables...")
            with app.app_context():
                db.create_all()
            print("Database tables created successfully!")

    except Exception as e:
        print(f"Error initializing tables: {e}")


def check_and_seed_data(app):
    """
    Check if database is empty and seed with demo data if needed.

    Args:
        app: Flask application instance
    """
    from app.extensions import db
    from app.models import User, Administrador, Producto, Categoria

    try:
        with app.app_context():
            # Check if there are any categories (good indicator of seeded data)
            categoria_count = Categoria.query.count()
            producto_count = Producto.query.count()
            admin_count = Administrador.query.count()

            if categoria_count == 0 or producto_count == 0 or admin_count == 0:
                print("\n" + "🌱 Base de datos vacía detectada. Poblando con datos demo...")
                print("="*60)

                # Import and run setup
                from setup_demo import EcommerceDemoSetup

                setup = EcommerceDemoSetup()

                # Clear any existing data
                setup.clear_data()

                # Create all demo data
                setup.create_admin_users()
                setup.create_regular_users()
                productos = setup.create_categories_and_products()
                setup.create_store_settings()

                # Get users for creating additional data
                usuarios = User.query.all()

                # Create sample data
                setup.create_sample_orders(usuarios, productos)
                setup.create_reviews(usuarios, productos)
                setup.create_wishlists(usuarios, productos)

                print("\n" + "✅ DATOS DEMO CREADOS EXITOSAMENTE")
                print("="*60)
                print("\n📋 CREDENCIALES DE ACCESO:\n")
                print("🔐 ADMIN:")
                print("   Email:    admin@ecommerce.ec")
                print("   Password: admin123")
                print("   URL:      http://localhost:5000/admin/login")
                print("\n👤 CLIENTES (password: demo123):")
                print("   - carlos.mendoza@email.com")
                print("   - maria.gonzalez@email.com")
                print("   - luis.torres@email.com")
                print("   URL:      http://localhost:5000/login")
                print("\n" + "="*60 + "\n")
            else:
                print(f"✅ Base de datos ya contiene datos ({categoria_count} categorías, {producto_count} productos)")

    except Exception as e:
        print(f"⚠️  Error verificando/creando datos demo: {e}")
        print("    Puedes ejecutar manualmente: python setup_demo.py")


def migrate_payment_gateway_columns(database_url):
    """
    Add payment gateway columns to comercio table if they don't exist.

    Args:
        database_url: SQLAlchemy database URL

    Returns:
        bool: True if migration successful
    """
    try:
        # Parse the database URL
        parsed = urlparse(database_url)

        # Extract connection details
        username = parsed.username or 'root'
        password = parsed.password or ''
        host = parsed.hostname or 'localhost'
        port = parsed.port or 3306
        database = parsed.path.lstrip('/')

        # Connect to database
        connection = pymysql.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database,
            charset='utf8mb4'
        )

        try:
            with connection.cursor() as cursor:
                # List of columns to add: (name, definition)
                columns = [
                    ("modoPaymentez", "VARCHAR(20) DEFAULT 'test'"),
                    ("appCodePaymentez", "TEXT"),
                    ("appKeyPaymentez", "TEXT"),
                    ("modoDatafast", "VARCHAR(20) DEFAULT 'test'"),
                    ("midDatafast", "VARCHAR(100)"),
                    ("tidDatafast", "VARCHAR(100)"),
                    ("modoDeUna", "VARCHAR(20) DEFAULT 'test'"),
                    ("apiKeyDeUna", "TEXT"),
                    ("cuentasBancarias", "TEXT"),
                ]

                columns_added = 0

                for column_name, column_def in columns:
                    try:
                        # Check if column exists
                        cursor.execute(f"SHOW COLUMNS FROM comercio LIKE '{column_name}'")
                        result = cursor.fetchone()

                        if not result:
                            # Add column
                            sql = f"ALTER TABLE comercio ADD COLUMN {column_name} {column_def}"
                            cursor.execute(sql)
                            connection.commit()
                            columns_added += 1

                    except pymysql.err.OperationalError:
                        # Column might already exist or other error
                        connection.rollback()
                        pass

                if columns_added > 0:
                    print(f"✅ Agregadas {columns_added} columnas de pasarelas de pago")

            return True

        finally:
            connection.close()

    except Exception as e:
        print(f"⚠️  Error migrando columnas de pasarelas: {e}")
        return False


def auto_init_database(app):
    """
    Automatically initialize database on first run.

    Args:
        app: Flask application instance
    """
    database_url = app.config.get('SQLALCHEMY_DATABASE_URI')

    if database_url and 'mysql' in database_url:
        print("\n" + "="*60)
        print("🚀 INICIALIZACIÓN AUTOMÁTICA DE BASE DE DATOS")
        print("="*60)

        # Ensure database exists
        if ensure_database_exists(database_url):
            # Initialize tables
            initialize_tables(app)

            # Migrate payment gateway columns
            migrate_payment_gateway_columns(database_url)

            # Check and seed data if empty
            check_and_seed_data(app)

        print("="*60 + "\n")
