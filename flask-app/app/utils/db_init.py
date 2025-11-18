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


def auto_init_database(app):
    """
    Automatically initialize database on first run.

    Args:
        app: Flask application instance
    """
    database_url = app.config.get('SQLALCHEMY_DATABASE_URI')

    if database_url and 'mysql' in database_url:
        print("\n" + "="*60)
        print("DATABASE INITIALIZATION")
        print("="*60)

        # Ensure database exists
        if ensure_database_exists(database_url):
            # Initialize tables
            initialize_tables(app)

        print("="*60 + "\n")
