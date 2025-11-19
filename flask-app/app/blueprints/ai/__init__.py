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

from . import routes
