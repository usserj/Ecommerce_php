"""Application entry point."""
import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

# Create Flask app
app = create_app(os.environ.get('FLASK_ENV', 'development'))

# Auto-initialize database on first run
if __name__ == '__main__':
    from app.utils.db_init import auto_init_database
    auto_init_database(app)

    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )
