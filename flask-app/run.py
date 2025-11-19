"""Application entry point."""
import os
import socket
import logging
from dotenv import load_dotenv
from app import create_app

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)

# Load environment variables
load_dotenv()

# Create Flask app
app = create_app(os.environ.get('FLASK_ENV', 'development'))


def get_local_ip():
    """Get local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == '__main__':
    # Get port and IP
    port = int(os.environ.get('PORT', 5000))
    local_ip = get_local_ip()

    # Print access URLs
    print("\n" + "="*60)
    print("🚀 SERVIDOR FLASK INICIANDO")
    print("="*60)
    print(f"\n🌐 Accede al servidor en:\n")
    print(f"   Local:    http://localhost:{port}")
    print(f"   Red:      http://{local_ip}:{port}")
    print(f"\n📊 Panel Admin:")
    print(f"   Admin:    http://{local_ip}:{port}/admin/login")
    print(f"\n🔥 Hot-reload: ACTIVADO")
    print("="*60 + "\n")

    # Run app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        use_reloader=True,
        use_debugger=True
    )
