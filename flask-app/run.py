"""Application entry point."""
import os
import shutil
import logging
from dotenv import load_dotenv
from app import create_app

# Configure logging - Show warnings and errors, hide verbose SQL
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s: %(message)s'
)
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)

# Create .env from .env.example if it doesn't exist
if not os.path.exists('.env') and os.path.exists('.env.example'):
    print("📝 Creando archivo .env desde .env.example...")
    shutil.copy('.env.example', '.env')
    print("✅ Archivo .env creado. Puedes editarlo con tus credenciales.\n")

# Load environment variables
load_dotenv()

# Create Flask app
app = create_app(os.environ.get('FLASK_ENV', 'development'))

# Auto-initialize database on first run
if __name__ == '__main__':
    from app.utils.db_init import auto_init_database
    auto_init_database(app)

    # Apply pending migrations
    try:
        from apply_migration import apply_migration
        apply_migration()
    except Exception as e:
        print(f"⚠️  Migration note: {e}")

    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )
