"""
Rutas API para funcionalidades de IA
"""

from flask import request, jsonify, session
from flask_login import current_user
from app.blueprints.ai import ai_bp
from app.services.ai_service import ai_service
from app.models.product import Producto
from app.models.comment import Comentario
from app.models.analisis_review import AnalisisReview
from app.extensions import db, csrf
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def get_or_create_session_id():
    """Obtiene o crea un session_id único para el chatbot"""
    if 'chatbot_session_id' not in session:
        session['chatbot_session_id'] = str(uuid.uuid4())
    return session['chatbot_session_id']


@ai_bp.route('/chat', methods=['POST'])
@csrf.exempt
def chat():
    """
    Endpoint para chatbot de ventas

    Request JSON:
    {
        "message": "¿Tienen envío gratis?",
        "context": {
            "productos": [...],  # Opcional
            "carrito": {...}      # Opcional
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
        # Log de la petición recibida
        logger.info(f"📥 Petición al chatbot desde {request.remote_addr}")
        logger.debug(f"Headers: {dict(request.headers)}")
        logger.debug(f"Content-Type: {request.content_type}")

        # Intentar obtener JSON con manejo de errores
        try:
            data = request.get_json(force=True)
            logger.debug(f"JSON recibido: {data}")
        except Exception as json_error:
            logger.error(f"❌ Error al parsear JSON: {json_error}")
            logger.error(f"Raw data: {request.data}")
            return jsonify({
                'success': False,
                'error': f'JSON inválido: {str(json_error)}',
                'debug': {
                    'content_type': request.content_type,
                    'raw_data': str(request.data[:200])  # Primeros 200 caracteres
                }
            }), 400

        if not data:
            logger.warning("⚠️ Petición sin datos")
            return jsonify({
                'success': False,
                'error': 'No se recibieron datos'
            }), 400

        if 'message' not in data:
            logger.warning(f"⚠️ Petición sin campo 'message': {data}")
            return jsonify({
                'success': False,
                'error': 'Campo "message" requerido',
                'received': list(data.keys())
            }), 400

        user_message = str(data['message']).strip()

        if not user_message:
            logger.warning("⚠️ Mensaje vacío")
            return jsonify({
                'success': False,
                'error': 'Mensaje vacío'
            }), 400

        logger.info(f"💬 Mensaje del usuario: {user_message[:50]}...")

        # Obtener session_id
        session_id = get_or_create_session_id()
        logger.debug(f"Session ID: {session_id}")

        # Obtener usuario_id si está logueado
        usuario_id = current_user.id if current_user.is_authenticated else None
        if usuario_id:
            logger.debug(f"Usuario autenticado: {usuario_id}")

        # Obtener contexto
        context = data.get('context', {})
        logger.debug(f"Contexto: {context}")

        # Llamar al servicio de IA
        logger.info("🤖 Llamando al servicio de IA...")
        result = ai_service.chatbot_response(
            session_id=session_id,
            user_message=user_message,
            context=context,
            usuario_id=usuario_id
        )

        if result['success']:
            logger.info(f"✅ Respuesta generada exitosamente: {result['response'][:50]}...")
            return jsonify({
                'success': True,
                'response': result['response'],
                'timestamp': datetime.now().isoformat()
            })
        else:
            logger.error(f"❌ Error en chatbot: {result.get('error')}")
            # Retornar success=True con mensaje de fallback
            return jsonify({
                'success': True,
                'response': result.get('response', 'Lo siento, estoy teniendo problemas técnicos.'),
                'timestamp': datetime.now().isoformat(),
                'debug_error': result.get('error')
            })

    except Exception as e:
        logger.exception(f"💥 Error crítico en endpoint /chat: {e}")
        import traceback
        return jsonify({
            'success': False,
            'error': f'Error del servidor: {str(e)}',
            'response': 'Lo siento, ocurrió un error inesperado. Por favor intenta de nuevo.',
            'timestamp': datetime.now().isoformat(),
            'traceback': traceback.format_exc() if logger.level <= 10 else None  # Solo en DEBUG
        }), 500


@ai_bp.route('/recomendaciones/<int:producto_id>', methods=['GET'])
def recomendaciones(producto_id):
    """
    Endpoint para obtener recomendaciones de productos

    Response JSON:
    {
        "success": true,
        "recomendaciones": [
            {
                "producto_id": 123,
                "nombre": "...",
                "precio": 99.99,
                "imagen": "...",
                "ruta": "...",
                "razon": "Se complementa perfecto",
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
                'error': 'Producto no encontrado',
                'recomendaciones': []
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
            logger.error(f"Error en recomendaciones: {result.get('error')}")
            return jsonify({
                'success': False,
                'error': result.get('error', 'Error al obtener recomendaciones'),
                'recomendaciones': []
            })

    except Exception as e:
        logger.exception(f"Error en endpoint /recomendaciones: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'recomendaciones': []
        }), 500


@ai_bp.route('/generar-descripcion', methods=['POST'])
@csrf.exempt
def generar_descripcion():
    """
    Endpoint para generar descripción de producto con IA

    Request JSON:
    {
        "nombre": "Laptop HP",
        "categoria": "Electrónica",
        "precio": 899.99,
        "caracteristicas": "Intel i5...",
        "publico": "Estudiantes",  # Opcional
        "keywords": "laptop ecuador"  # Opcional
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

        # Validar campos requeridos
        required_fields = ['nombre', 'categoria', 'precio', 'caracteristicas']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400

        # Obtener datos
        nombre = data['nombre'].strip()
        categoria = data['categoria'].strip()
        precio = float(data['precio'])
        caracteristicas = data['caracteristicas'].strip()
        publico = data.get('publico', '').strip()
        keywords = data.get('keywords', '').strip()

        # Validaciones
        if precio <= 0:
            return jsonify({
                'success': False,
                'error': 'Precio debe ser mayor a 0'
            }), 400

        # Llamar al servicio de IA
        result = ai_service.generar_descripcion_producto(
            nombre=nombre,
            categoria=categoria,
            precio=precio,
            caracteristicas=caracteristicas,
            publico=publico,
            keywords=keywords
        )

        if result['success']:
            return jsonify({
                'success': True,
                'data': result['data']
            })
        else:
            logger.error(f"Error al generar descripción: {result.get('error')}")
            return jsonify({
                'success': False,
                'error': result.get('error', 'Error al generar descripción')
            }), 500

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Precio inválido'
        }), 400
    except Exception as e:
        logger.exception(f"Error en endpoint /generar-descripcion: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500


@ai_bp.route('/analizar-reviews', methods=['POST'])
@csrf.exempt
def analizar_reviews_endpoint():
    """
    Endpoint para análisis de reviews de un producto

    Request JSON:
    {
        "producto_id": 123  # Opcional, null = análisis general
    }

    Response JSON:
    {
        "success": true,
        "mensaje": "Análisis generado exitosamente"
    }
    """
    try:
        data = request.get_json() or {}
        producto_id = data.get('producto_id', None)

        # Si se especifica producto_id, verificar que existe
        if producto_id:
            producto = Producto.query.get(producto_id)
            if not producto:
                return jsonify({
                    'success': False,
                    'error': 'Producto no encontrado'
                }), 404

        # Llamar al servicio de IA
        success = ai_service.analizar_reviews(producto_id=producto_id)

        if success:
            return jsonify({
                'success': True,
                'mensaje': 'Análisis generado exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No hay suficientes comentarios para analizar'
            }), 400

    except Exception as e:
        logger.exception(f"Error en endpoint /analizar-reviews: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500


@ai_bp.route('/analizar-reviews/<int:producto_id>', methods=['GET'])
def obtener_analisis_reviews(producto_id):
    """
    Endpoint para obtener análisis existente de un producto

    Response JSON:
    {
        "success": true,
        "analisis": {...}
    }
    """
    try:
        # Obtener análisis existente
        analisis = AnalisisReview.get_analisis_reciente(producto_id=producto_id)

        if not analisis:
            return jsonify({
                'success': False,
                'error': 'No hay análisis disponible para este producto'
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
                'calidad_descripcion': analisis.get_calidad_descripcion(),
                'recomendacion': analisis.recomendacion,
                'total_reviews': analisis.total_reviews,
                'fecha_analisis': analisis.fecha_analisis.isoformat(),
                'sentimiento_dominante': analisis.get_sentimiento_dominante(),
                'color_sentimiento': analisis.get_color_sentimiento()
            }
        })

    except Exception as e:
        logger.exception(f"Error en endpoint /analizar-reviews/{producto_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500


@ai_bp.route('/busqueda-inteligente', methods=['POST'])
@csrf.exempt
def busqueda_inteligente_endpoint():
    """
    Endpoint para búsqueda inteligente (usado internamente por /buscar)

    Request JSON:
    {
        "query": "quiero algo para correr barato"
    }

    Response JSON:
    {
        "success": true,
        "intencion": "Busca zapatillas deportivas económicas",
        "productos_ids": [1, 2, 3],
        "sugerencias": ["zapatillas running", "tenis deportivos"]
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
        result = ai_service.busqueda_inteligente(query_usuario=query)

        if result['success']:
            return jsonify({
                'success': True,
                'intencion': result.get('intencion_usuario', ''),
                'productos_ids': result.get('productos_ids', []),
                'sugerencias': result.get('sugerencias_busqueda', [])
            })
        else:
            logger.error(f"Error en búsqueda inteligente: {result.get('error')}")
            return jsonify({
                'success': False,
                'error': result.get('error', 'Error al procesar búsqueda')
            }), 500

    except Exception as e:
        logger.exception(f"Error en endpoint /busqueda-inteligente: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500


@ai_bp.route('/health', methods=['GET'])
def health():
    """
    Endpoint de salud para verificar que el servicio de IA está funcionando

    Verifica:
    - Configuración de DeepSeek
    - Conexión con la API
    - Estado de las tablas de BD
    """
    # Cargar configuración
    ai_service._load_config()

    # Construir respuesta
    response = {
        'status': 'healthy',
        'service': 'AI Service with DeepSeek',
        'timestamp': datetime.now().isoformat(),
        'config': {
            'api_key': ai_service.api_key[:15] + '...' + ai_service.api_key[-4:] if ai_service.api_key else 'NO CONFIGURADA',
            'api_url': ai_service.api_url or 'NO CONFIGURADA',
            'model': ai_service.model or 'NO CONFIGURADO',
            'cache_ttl': ai_service.cache_ttl or 0
        },
        'database': {
            'conversaciones_chatbot': False,
            'analisis_reviews': False
        }
    }

    # Verificar tablas de BD
    try:
        from app.models.chatbot import ConversacionChatbot
        response['database']['conversaciones_chatbot'] = True
    except:
        pass

    try:
        from app.models.analisis_review import AnalisisReview
        response['database']['analisis_reviews'] = True
    except:
        pass

    # Probar conexión con API (llamada simple)
    try:
        test_result = ai_service.call_api(
            messages=[
                {"role": "system", "content": "You are a test assistant."},
                {"role": "user", "content": "Say 'ok' if you receive this."}
            ],
            max_tokens=10,
            temperature=0,
            use_cache=False
        )

        if test_result['success']:
            response['api_connection'] = 'OK'
            response['message'] = 'API de DeepSeek funcionando correctamente'
        else:
            response['status'] = 'degraded'
            response['api_connection'] = 'ERROR'
            response['message'] = f'Error en API: {test_result.get("error", "Desconocido")}'
    except Exception as e:
        response['status'] = 'unhealthy'
        response['api_connection'] = 'ERROR'
        response['message'] = f'Error al conectar con DeepSeek: {str(e)}'

    return jsonify(response)
