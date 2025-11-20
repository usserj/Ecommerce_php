"""
Blueprint para funcionalidades de IA

Endpoints REST para:
- Chatbot de ventas
- Recomendaciones de productos
- Generación de descripciones
- Análisis de reviews
- Búsqueda inteligente
"""

from flask import Blueprint

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

# IMPORTANTE: Deshabilitar CSRF para este blueprint (es una API REST)
# El decorador se aplicará después de registrar el blueprint
ai_bp._is_api = True

# Configurar CORS para el blueprint
@ai_bp.after_request
def after_request(response):
    """Agregar headers CORS a todas las respuestas del blueprint AI"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-CSRFToken')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

from . import routes
