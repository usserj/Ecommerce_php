"""
Rutas API para funcionalidades de IA.
"""

from flask import request, jsonify, session
from flask_login import current_user
from app.blueprints.ai import ai_bp
from app.services.ai_service import ai_service
from app.models.product import Producto
from app.models.analisis_review import AnalisisReview
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def get_or_create_session_id():
    """Obtiene o crea un session_id único para el chatbot."""
    if 'chatbot_session_id' not in session:
        session['chatbot_session_id'] = str(uuid.uuid4())
    return session['chatbot_session_id']


@ai_bp.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint para chatbot de ventas.

    Request JSON:
    {
        "message": "¿Tienen envío gratis?",
        "context": {
            "productos": [...],
            "carrito": {...}
        }
    }

    Response JSON:
    {
        "success": true,
        "response": "Sí, ofrecemos envío gratis...",
        "timestamp": "2025-01-01T12:00:00"
    }
    """
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Mensaje requerido'
            }), 400

        user_message = data['message'].strip()

        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Mensaje vacío'
            }), 400

        # Obtener session_id
        session_id = get_or_create_session_id()

        # Obtener usuario_id si está logueado
        usuario_id = current_user.id if current_user.is_authenticated else None

        # Obtener contexto
        context = data.get('context', {})

        # Llamar al servicio de IA
        result = ai_service.chatbot_response(
            session_id=session_id,
            user_message=user_message,
            context=context,
            usuario_id=usuario_id
        )

        if result['success']:
            return jsonify({
                'success': True,
                'response': result['response'],
                'timestamp': datetime.now().isoformat()
            })
        else:
            logger.error(f"Error en chatbot: {result['error']}")
            return jsonify({
                'success': True,  # Retornar success=True con mensaje de fallback
                'response': result['response'],  # Mensaje de fallback
                'timestamp': datetime.now().isoformat()
            })

    except Exception as e:
        logger.exception(f"Error en endpoint /chat: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500


@ai_bp.route('/recomendaciones/<int:producto_id>', methods=['GET'])
def recomendaciones(producto_id):
    """
    Endpoint para obtener recomendaciones de productos.

    Response JSON:
    {
        "success": true,
        "recomendaciones": [
            {
                "producto_id": 123,
                "nombre": "Producto X",
                "precio": 29.99,
                "imagen": "/static/uploads/...",
                "ruta": "producto-x",
                "razon": "Se complementa perfecto...",
                "tipo": "complementario"
            }
        ]
    }
    """
    try:
        # Verificar que el producto existe
        producto = Producto.query.get(producto_id)
        if not producto:
            return jsonify({
                'success': False,
                'recomendaciones': [],
                'error': 'Producto no encontrado'
            }), 404

        # Obtener usuario_id si está logueado
        usuario_id = current_user.id if current_user.is_authenticated else None

        # Llamar al servicio de IA
        result = ai_service.obtener_recomendaciones(
            producto_id=producto_id,
            usuario_id=usuario_id
        )

        if result['success']:
            return jsonify({
                'success': True,
                'recomendaciones': result['recomendaciones']
            })
        else:
            # Fallback: productos aleatorios de la misma categoría
            from app.extensions import db
            fallback_productos = Producto.query.filter(
                Producto.activo == True,
                Producto.id != producto_id,
                Producto.id_categoria == producto.id_categoria
            ).order_by(db.func.random()).limit(4).all()

            recomendaciones = []
            for p in fallback_productos:
                recomendaciones.append({
                    'producto_id': p.id,
                    'nombre': p.titulo,
                    'precio': float(p.get_precio_final()),
                    'imagen': p.imagen or '/static/images/no-image.jpg',
                    'ruta': p.ruta,
                    'razon': 'De la misma categoría',
                    'tipo': 'similar'
                })

            return jsonify({
                'success': True,
                'recomendaciones': recomendaciones
            })

    except Exception as e:
        logger.exception(f"Error en endpoint /recomendaciones: {e}")
        return jsonify({
            'success': False,
            'recomendaciones': [],
            'error': 'Error interno del servidor'
        }), 500


@ai_bp.route('/generar-descripcion', methods=['POST'])
def generar_descripcion():
    """
    Endpoint para generar descripción de producto con IA.

    Request JSON:
    {
        "nombre": "Laptop HP",
        "categoria": "Electrónica",
        "precio": 899.99,
        "caracteristicas": "Intel i5...",
        "publico": "Estudiantes",
        "keywords": "laptop ecuador"
    }

    Response JSON:
    {
        "success": true,
        "data": {
            "descripcion_corta": "...",
            "descripcion_larga": "...",
            "beneficios": [...],
            "call_to_action": "..."
        }
    }
    """
    try:
        data = request.get_json()

        # Validar datos requeridos
        required_fields = ['nombre', 'categoria', 'precio', 'caracteristicas']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400

        # Llamar al servicio de IA
        result = ai_service.generar_descripcion_producto(
            nombre=data['nombre'],
            categoria=data['categoria'],
            precio=float(data['precio']),
            caracteristicas=data['caracteristicas'],
            publico=data.get('publico', ''),
            keywords=data.get('keywords', '')
        )

        if result['success']:
            return jsonify({
                'success': True,
                'data': result['data']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Precio inválido: {str(e)}'
        }), 400

    except Exception as e:
        logger.exception(f"Error en endpoint /generar-descripcion: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500


@ai_bp.route('/analizar-reviews', methods=['POST'])
def analizar_reviews_endpoint():
    """
    Endpoint para generar análisis de reviews.

    Request JSON:
    {
        "producto_id": 123  // Opcional, null para análisis general
    }

    Response JSON:
    {
        "success": true,
        "message": "Análisis generado exitosamente"
    }
    """
    try:
        data = request.get_json() or {}
        producto_id = data.get('producto_id')

        # Convertir a None si es null/vacío
        if producto_id == '' or producto_id == 'null':
            producto_id = None
        elif producto_id is not None:
            producto_id = int(producto_id)

        # Llamar al servicio de IA
        success = ai_service.analizar_reviews(producto_id=producto_id)

        if success:
            return jsonify({
                'success': True,
                'message': 'Análisis generado exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No hay suficientes comentarios para analizar'
            }), 400

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'ID de producto inválido: {str(e)}'
        }), 400

    except Exception as e:
        logger.exception(f"Error en endpoint /analizar-reviews: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500


@ai_bp.route('/analisis-reviews/<int:producto_id>', methods=['GET'])
def obtener_analisis_reviews(producto_id):
    """
    Endpoint para obtener análisis existente de reviews.

    Response JSON:
    {
        "success": true,
        "analisis": {...}
    }
    """
    try:
        analisis = AnalisisReview.query.filter_by(producto_id=producto_id).first()

        if not analisis:
            return jsonify({
                'success': False,
                'error': 'No hay análisis disponible'
            }), 404

        return jsonify({
            'success': True,
            'analisis': {
                'sentimiento': {
                    'positivo': analisis.sentimiento_positivo,
                    'neutral': analisis.sentimiento_neutral,
                    'negativo': analisis.sentimiento_negativo
                },
                'aspectos_positivos': analisis.get_aspectos_positivos(),
                'aspectos_negativos': analisis.get_aspectos_negativos(),
                'calidad_score': float(analisis.calidad_score),
                'recomendacion': analisis.recomendacion,
                'total_reviews': analisis.total_reviews,
                'fecha_analisis': analisis.fecha_analisis.isoformat()
            }
        })

    except Exception as e:
        logger.exception(f"Error en endpoint /analisis-reviews: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500


@ai_bp.route('/busqueda-inteligente', methods=['POST'])
def busqueda_inteligente_endpoint():
    """
    Endpoint para búsqueda inteligente (usado internamente por /buscar).

    Request JSON:
    {
        "query": "laptop para estudiante"
    }

    Response JSON:
    {
        "success": true,
        "intencion_usuario": "Busca laptops...",
        "productos_ids": [123, 456],
        "sugerencias_busqueda": [...]
    }
    """
    try:
        data = request.get_json()

        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Query requerido'
            }), 400

        query = data['query'].strip()

        if not query:
            return jsonify({
                'success': False,
                'error': 'Query vacío'
            }), 400

        # Llamar al servicio de IA
        result = ai_service.busqueda_inteligente(query)

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Error en endpoint /busqueda-inteligente: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500
