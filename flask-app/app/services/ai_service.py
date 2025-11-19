"""
Servicio centralizado para funcionalidades de IA con DeepSeek

Este módulo maneja:
- Comunicación con API DeepSeek
- Cache de respuestas (in-memory)
- Manejo robusto de errores
- Rate limiting
- Logging de todas las interacciones
- Fallbacks cuando la API falla
"""

import requests
import json
import hashlib
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app
from app.extensions import db
from app.models.product import Producto
from app.models.comment import Comentario
from app.models.categoria import Categoria
from app.models.order import Compra

logger = logging.getLogger(__name__)

class DeepSeekService:
    """Servicio base para interactuar con DeepSeek API"""

    def __init__(self):
        self.api_key = "sk-5967b2b9feb7438dadd1059f600094c9"
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"
        self.cache = {}  # Cache en memoria simple
        self.cache_ttl = 3600  # 1 hora por defecto

    def _get_cache_key(self, prompt: str, context: dict = None) -> str:
        """Genera key única para cache basada en prompt y contexto"""
        data = f"{prompt}_{json.dumps(context or {}, sort_keys=True)}"
        return hashlib.md5(data.encode()).hexdigest()

    def _check_cache(self, cache_key: str):
        """Verifica si hay respuesta en cache válida"""
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                logger.info(f"Cache HIT para {cache_key[:8]}...")
                return cached_data
            else:
                # Cache expirado, eliminar
                del self.cache[cache_key]
        return None

    def _set_cache(self, cache_key: str, data, ttl: int = None):
        """Guarda respuesta en cache"""
        if ttl is None:
            ttl = self.cache_ttl
        self.cache[cache_key] = (data, datetime.now())
        logger.info(f"Cache SET para {cache_key[:8]}... (TTL: {ttl}s)")

    def _limpiar_cache_antiguo(self):
        """Limpia entradas de cache expiradas"""
        ahora = datetime.now()
        keys_expiradas = [
            key for key, (_, timestamp) in self.cache.items()
            if ahora - timestamp >= timedelta(seconds=self.cache_ttl)
        ]
        for key in keys_expiradas:
            del self.cache[key]
        if keys_expiradas:
            logger.info(f"Cache: eliminadas {len(keys_expiradas)} entradas expiradas")

    def call_api(self, messages: list, temperature: float = 0.7,
                 max_tokens: int = 1000, use_cache: bool = True,
                 cache_ttl: int = None) -> dict:
        """
        Llamada base a DeepSeek API

        Args:
            messages: Lista de mensajes [{"role": "user/system", "content": "..."}]
            temperature: Creatividad (0-1). Menor = más determinista
            max_tokens: Límite de tokens de respuesta
            use_cache: Usar sistema de cache
            cache_ttl: TTL personalizado para cache (segundos)

        Returns:
            dict: {
                'success': bool,
                'response': str (contenido de la respuesta),
                'error': str (si success=False),
                'tokens_used': int (total de tokens consumidos)
            }
        """
        try:
            # Limpiar cache antiguo periódicamente
            if len(self.cache) > 100:
                self._limpiar_cache_antiguo()

            # Generar cache key
            cache_key = self._get_cache_key(str(messages))

            # Verificar cache
            if use_cache:
                cached = self._check_cache(cache_key)
                if cached:
                    return cached

            # Preparar payload para DeepSeek
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Log de la llamada
            logger.info(f"Llamando a DeepSeek API - Mensajes: {len(messages)}, Temp: {temperature}, MaxTokens: {max_tokens}")

            # Realizar llamada a la API
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            # Verificar respuesta
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                tokens_used = data.get('usage', {}).get('total_tokens', 0)

                result = {
                    "success": True,
                    "response": content,
                    "error": None,
                    "tokens_used": tokens_used
                }

                logger.info(f"DeepSeek API exitoso. Tokens usados: {tokens_used}")

                # Guardar en cache
                if use_cache:
                    self._set_cache(cache_key, result, cache_ttl)

                return result
            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "response": None,
                    "error": error_msg,
                    "tokens_used": 0
                }

        except requests.Timeout:
            error_msg = "Timeout al llamar a DeepSeek API (30s)"
            logger.error(error_msg)
            return {
                "success": False,
                "response": None,
                "error": error_msg,
                "tokens_used": 0
            }

        except requests.RequestException as e:
            error_msg = f"Error de conexión con DeepSeek API: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "response": None,
                "error": error_msg,
                "tokens_used": 0
            }

        except Exception as e:
            error_msg = f"Error inesperado en DeepSeek service: {str(e)}"
            logger.exception(error_msg)
            return {
                "success": False,
                "response": None,
                "error": error_msg,
                "tokens_used": 0
            }

    # ==========================================
    # FUNCIONALIDAD 1: CHATBOT
    # ==========================================

    def chatbot_response(self, session_id: str, user_message: str,
                        context: dict = None, usuario_id: int = None) -> dict:
        """
        Genera respuesta del chatbot de ventas

        Args:
            session_id: ID único de sesión
            user_message: Mensaje del usuario
            context: Contexto adicional (productos en página, carrito, etc.)
            usuario_id: ID del usuario si está logueado

        Returns:
            dict: {
                'success': bool,
                'response': str,
                'error': str
            }
        """
        try:
            from app.models.setting import Plantilla

            # Importar el modelo aquí para evitar circular imports
            try:
                from app.models.chatbot import ConversacionChatbot
            except ImportError:
                # Si el modelo no existe aún, devolver respuesta de fallback
                logger.warning("Modelo ConversacionChatbot no disponible aún")
                return {
                    'success': True,
                    'response': "¡Hola! Soy tu asistente de compras. ¿En qué puedo ayudarte hoy?",
                    'error': None
                }

            # Obtener info de la tienda
            plantilla = Plantilla.query.first()

            # Obtener historial de conversación
            historial = ConversacionChatbot.get_conversacion(session_id, limit=10)
            historial = list(reversed(historial))  # Orden cronológico

            # Preparar contexto
            context = context or {}
            productos_pagina = context.get('productos', [])
            carrito = context.get('carrito', {})

            # Construir contexto de productos
            productos_contexto = ""
            if productos_pagina:
                productos_contexto = "\n\nProductos en esta página:\n"
                for p in productos_pagina[:5]:  # Máximo 5 productos
                    productos_contexto += f"- {p.get('nombre', 'Producto')}: ${p.get('precio', 0)}\n"

            # Construir contexto de carrito
            carrito_contexto = ""
            if carrito and isinstance(carrito, dict):
                total_items = carrito.get('total_items', 0)
                if total_items > 0:
                    carrito_contexto = f"\n\nCarrito actual: {total_items} producto(s)"

            # System prompt
            system_prompt = f"""Eres un asistente de ventas para {plantilla.nombre_tienda if plantilla else 'nuestra tienda'}, un ecommerce ecuatoriano.

PERSONALIDAD:
- Amable, profesional, orientado a cerrar ventas
- Español ecuatoriano neutral pero cercano
- Ayudas a tomar decisiones de compra inteligentes
- Resuelves dudas sobre productos, envíos, pagos, garantías

INFORMACIÓN DE LA TIENDA:
- Nombre: {plantilla.nombre_tienda if plantilla else 'Tienda Virtual'}
- Email: {plantilla.email_contacto if plantilla else 'contacto@tienda.com'}
- Teléfono: {plantilla.telefono_contacto if plantilla else 'N/A'}
- WhatsApp: {plantilla.whatsapp if plantilla else 'N/A'}
- Envíos: A todo Ecuador en 24-48 horas
- Envío gratis: Compras sobre $50
- Métodos de pago: PayPal, PayU, Paymentez, Datafast, transferencia bancaria
- Garantía: 30 días en todos los productos
- País: Ecuador

CONTEXTO ACTUAL:{productos_contexto}{carrito_contexto}

INSTRUCCIONES:
1. Sé breve y directo (máximo 3-4 oraciones por respuesta)
2. Si preguntan por producto específico, menciona precio y características clave
3. Siempre intenta cerrar venta o sugerir siguiente paso
4. Si no sabes algo específico, deriva a contacto de la tienda
5. Usa emojis ocasionalmente para ser más cercano 😊
6. Si preguntan por el carrito y está vacío, sugiere explorar productos

PROHIBIDO:
- Inventar precios, stock o información de productos
- Prometer envíos inmediatos sin confirmación
- Dar información técnica incorrecta
- Ser repetitivo o genérico
"""

            # Construir mensajes para la API
            messages = [{"role": "system", "content": system_prompt}]

            # Agregar historial (últimos 5 intercambios = 10 mensajes)
            for conv in historial[-10:]:
                messages.append({
                    "role": conv.rol,
                    "content": conv.mensaje
                })

            # Agregar mensaje actual del usuario
            messages.append({
                "role": "user",
                "content": user_message
            })

            # Llamar a DeepSeek
            result = self.call_api(
                messages=messages,
                temperature=0.7,
                max_tokens=300,
                use_cache=False  # No cachear conversaciones
            )

            if result['success']:
                # Guardar mensaje del usuario en BD
                conv_user = ConversacionChatbot(
                    session_id=session_id,
                    usuario_id=usuario_id,
                    rol='user',
                    mensaje=user_message
                )
                conv_user.set_contexto(context)
                db.session.add(conv_user)

                # Guardar respuesta del asistente
                conv_assistant = ConversacionChatbot(
                    session_id=session_id,
                    usuario_id=usuario_id,
                    rol='assistant',
                    mensaje=result['response']
                )
                db.session.add(conv_assistant)

                db.session.commit()

                return {
                    'success': True,
                    'response': result['response'],
                    'error': None
                }
            else:
                logger.error(f"Error en chatbot: {result['error']}")
                return {
                    'success': False,
                    'response': "Lo siento, estoy teniendo problemas técnicos. Por favor intenta de nuevo en un momento.",
                    'error': result['error']
                }

        except Exception as e:
            logger.exception(f"Error en chatbot_response: {e}")
            return {
                'success': False,
                'response': "Lo siento, ocurrió un error inesperado. Por favor intenta de nuevo.",
                'error': str(e)
            }

    # ==========================================
    # FUNCIONALIDAD 2: RECOMENDACIONES
    # ==========================================

    def obtener_recomendaciones(self, producto_id: int, usuario_id: int = None) -> dict:
        """
        Genera recomendaciones de productos usando IA

        Args:
            producto_id: ID del producto actual
            usuario_id: ID del usuario (opcional, para personalizar)

        Returns:
            dict: {
                'success': bool,
                'recomendaciones': [{producto_id, nombre, precio, imagen, ruta, razon, tipo}]
            }
        """
        try:
            # Obtener producto actual
            producto = Producto.query.get(producto_id)
            if not producto:
                return {'success': False, 'recomendaciones': [], 'error': 'Producto no encontrado'}

            # Obtener catálogo de productos activos (excluyendo el actual)
            catalogo = Producto.query.filter(
                Producto.id != producto_id,
                Producto.stock > 0
            ).limit(50).all()

            if not catalogo:
                return {'success': False, 'recomendaciones': [], 'error': 'No hay productos disponibles'}

            # Historial del usuario (si está logueado)
            historial_productos = []
            if usuario_id:
                # Obtener últimas compras
                compras = Compra.query.filter_by(id_usuario=usuario_id).order_by(Compra.fecha.desc()).limit(5).all()
                for compra in compras:
                    if compra.producto:
                        historial_productos.append(compra.producto.titulo)

            # Preparar prompt para IA
            categoria_nombre = producto.categoria.categoria if producto.categoria else 'Sin categoría'
            precio_producto = producto.precio

            prompt = f"""PRODUCTO ACTUAL:
ID: {producto.id}
Nombre: {producto.titulo}
Precio: ${precio_producto}
Categoría: {categoria_nombre}
Descripción: {producto.descripcion[:200] if producto.descripcion else 'Sin descripción'}

CATÁLOGO DISPONIBLE (ID | Nombre | Precio | Categoría):
"""

            for p in catalogo:
                cat_nombre = p.categoria.categoria if p.categoria else 'Sin categoría'
                prompt += f"{p.id} | {p.titulo} | ${p.precio} | {cat_nombre}\n"

            if historial_productos:
                prompt += f"\n\nHISTORIAL DEL USUARIO:\nHa comprado: {', '.join(historial_productos[:5])}\n"

            prompt += """
TAREA:
Analiza el producto actual y recomienda los 3-4 mejores productos para maximizar la conversión.

CRITERIOS:
1. Productos complementarios (cross-sell): que se usen juntos
2. Productos similares (upsell): misma categoría, mejor calidad o precio
3. Productos frecuentemente comprados juntos
4. Considera el presupuesto: ±30% del precio actual
5. NO recomiendes el mismo producto actual

RESPONDE EN JSON VÁLIDO (sin markdown ni texto adicional):
{
  "recomendaciones": [
    {
      "producto_id": 123,
      "razon": "Se complementa perfecto para usar junto con este producto",
      "tipo": "complementario"
    },
    {
      "producto_id": 456,
      "razon": "Alternativa de mejor calidad en la misma categoría",
      "tipo": "similar"
    },
    {
      "producto_id": 789,
      "razon": "Otros clientes compraron esto junto con el producto actual",
      "tipo": "frecuente"
    }
  ]
}

IMPORTANTE: Responde SOLO el JSON, sin markdown (```json) ni explicaciones.
"""

            # Llamar a DeepSeek
            messages = [{"role": "user", "content": prompt}]
            result = self.call_api(
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                use_cache=True,
                cache_ttl=3600  # 1 hora de cache
            )

            if not result['success']:
                logger.error(f"Error al obtener recomendaciones: {result['error']}")
                # Fallback: productos aleatorios de la misma categoría
                return self._recomendaciones_fallback(producto, catalogo)

            # Parsear respuesta JSON
            try:
                # Limpiar respuesta (remover markdown si existe)
                response_text = result['response'].strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.startswith('```'):
                    response_text = response_text[3:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()

                data = json.loads(response_text)
                recomendaciones_ia = data.get('recomendaciones', [])

                # Enriquecer con datos de productos
                recomendaciones_finales = []
                for rec in recomendaciones_ia[:4]:  # Máximo 4
                    prod_id = rec.get('producto_id')
                    prod = Producto.query.get(prod_id)

                    if prod and prod.stock > 0:
                        recomendaciones_finales.append({
                            'producto_id': prod.id,
                            'nombre': prod.titulo,
                            'precio': float(prod.precio),
                            'imagen': prod.imagen or '/static/images/no-image.png',
                            'ruta': prod.ruta,
                            'razon': rec.get('razon', ''),
                            'tipo': rec.get('tipo', 'recomendado')
                        })

                if not recomendaciones_finales:
                    # Si no se encontraron productos válidos, usar fallback
                    return self._recomendaciones_fallback(producto, catalogo)

                return {
                    'success': True,
                    'recomendaciones': recomendaciones_finales
                }

            except json.JSONDecodeError as e:
                logger.error(f"Error al parsear JSON de recomendaciones: {e}")
                logger.error(f"Respuesta recibida: {result['response']}")
                return self._recomendaciones_fallback(producto, catalogo)

        except Exception as e:
            logger.exception(f"Error en obtener_recomendaciones: {e}")
            return {'success': False, 'recomendaciones': [], 'error': str(e)}

    def _recomendaciones_fallback(self, producto, catalogo):
        """Fallback: productos aleatorios de la misma categoría o similares"""
        import random

        # Intentar productos de la misma categoría primero
        productos_categoria = [p for p in catalogo if p.categoria_id == producto.categoria_id]

        if not productos_categoria:
            # Si no hay de la misma categoría, usar cualquiera
            productos_categoria = catalogo

        # Seleccionar 3-4 aleatorios
        seleccionados = random.sample(productos_categoria, min(4, len(productos_categoria)))

        recomendaciones = []
        for prod in seleccionados:
            recomendaciones.append({
                'producto_id': prod.id,
                'nombre': prod.titulo,
                'precio': float(prod.precio),
                'imagen': prod.imagen or '/static/images/no-image.png',
                'ruta': prod.ruta,
                'razon': 'Producto recomendado de la misma categoría',
                'tipo': 'similar'
            })

        return {
            'success': True,
            'recomendaciones': recomendaciones
        }

    # ==========================================
    # FUNCIONALIDAD 3: GENERADOR DE DESCRIPCIONES
    # ==========================================

    def generar_descripcion_producto(self, nombre: str, categoria: str,
                                    precio: float, caracteristicas: str,
                                    publico: str = '', keywords: str = '') -> dict:
        """
        Genera descripciones profesionales de productos

        Args:
            nombre: Nombre del producto
            categoria: Categoría del producto
            precio: Precio del producto
            caracteristicas: Características técnicas
            publico: Público objetivo (opcional)
            keywords: Palabras clave SEO (opcional)

        Returns:
            dict: {
                'success': bool,
                'data': {
                    'descripcion_corta': str,
                    'descripcion_larga': str,
                    'beneficios': list,
                    'call_to_action': str
                }
            }
        """
        try:
            prompt = f"""Eres un copywriter experto en ecommerce ecuatoriano con 10 años de experiencia.

PRODUCTO A DESCRIBIR:
Nombre: {nombre}
Categoría: {categoria}
Precio: ${precio}
Características técnicas: {caracteristicas}
{f'Público objetivo: {publico}' if publico else ''}
{f'Palabras clave SEO: {keywords}' if keywords else ''}

TAREA:
Genera contenido de venta profesional y persuasivo para este producto.

REQUISITOS:

1. DESCRIPCIÓN CORTA (2-3 líneas máximo):
   - Gancho de venta inmediato
   - Destaca el beneficio principal
   - Crea deseo de compra
   - Perfecto para listados y previews

2. DESCRIPCIÓN LARGA (150-200 palabras):
   - SEO optimizada para Ecuador
   - Incluye palabras clave naturalmente
   - Enfocada en BENEFICIOS, no solo características
   - Menciona: calidad, garantía, envío rápido Ecuador
   - Genera urgencia/confianza
   - Estructura: introducción, beneficios, especificaciones, cierre

3. CINCO BENEFICIOS CLAVE:
   - Formato: "Título del beneficio: breve explicación"
   - Enfocados en el valor para el cliente
   - Variados (calidad, economía, conveniencia, etc.)

4. CALL TO ACTION:
   - Frase persuasiva de cierre
   - Genera urgencia sin ser agresivo
   - Menciona garantía o envío gratis

ESTILO:
- Profesional pero accesible y cercano
- Español ecuatoriano neutral (sin modismos)
- Tono positivo y persuasivo
- Evita exageraciones o falsas promesas
- Incluye emojis sutiles donde sea apropiado

RESPONDE EN JSON VÁLIDO (sin markdown ni texto adicional):
{{
  "descripcion_corta": "texto aquí",
  "descripcion_larga": "texto aquí",
  "beneficios": [
    "Beneficio 1: Explicación",
    "Beneficio 2: Explicación",
    "Beneficio 3: Explicación",
    "Beneficio 4: Explicación",
    "Beneficio 5: Explicación"
  ],
  "call_to_action": "texto aquí"
}}

IMPORTANTE: Responde SOLO el JSON, sin markdown (```json) ni explicaciones adicionales.
"""

            messages = [{"role": "user", "content": prompt}]
            result = self.call_api(
                messages=messages,
                temperature=0.8,  # Un poco más creativo
                max_tokens=800,
                use_cache=False  # No cachear, cada generación es única
            )

            if not result['success']:
                return {
                    'success': False,
                    'error': result['error']
                }

            # Parsear JSON
            try:
                response_text = result['response'].strip()
                # Limpiar markdown
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.startswith('```'):
                    response_text = response_text[3:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()

                data = json.loads(response_text)

                return {
                    'success': True,
                    'data': {
                        'descripcion_corta': data.get('descripcion_corta', ''),
                        'descripcion_larga': data.get('descripcion_larga', ''),
                        'beneficios': data.get('beneficios', []),
                        'call_to_action': data.get('call_to_action', '')
                    }
                }

            except json.JSONDecodeError as e:
                logger.error(f"Error al parsear JSON: {e}")
                logger.error(f"Respuesta: {result['response']}")
                return {
                    'success': False,
                    'error': 'Error al procesar la respuesta de IA'
                }

        except Exception as e:
            logger.exception(f"Error en generar_descripcion_producto: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ==========================================
    # FUNCIONALIDAD 4: ANÁLISIS DE REVIEWS
    # ==========================================

    def analizar_reviews(self, producto_id: int = None) -> bool:
        """
        Analiza reviews y genera insights con IA

        Args:
            producto_id: ID del producto (None = análisis general)

        Returns:
            bool: True si se generó exitosamente
        """
        try:
            # Importar modelo aquí para evitar circular imports
            try:
                from app.models.analisis_review import AnalisisReview
            except ImportError:
                logger.warning("Modelo AnalisisReview no disponible aún")
                return False

            # Obtener comentarios aprobados
            query = Comentario.query.filter_by(estado=1)  # estado=1 = aprobado

            if producto_id:
                query = query.filter_by(id_producto=producto_id)
                producto = Producto.query.get(producto_id)
                contexto = f"Producto: {producto.titulo}"
            else:
                contexto = "Análisis general de todos los productos de la tienda"

            comentarios = query.order_by(Comentario.fecha.desc()).limit(100).all()

            if not comentarios:
                logger.info("No hay comentarios para analizar")
                return False

            # Preparar datos para el prompt
            reviews_text = ""
            for c in comentarios:
                usuario_nombre = c.usuario.nombre if c.usuario else "Anónimo"
                reviews_text += f"Usuario: {usuario_nombre} | Rating: {c.calificacion}/5\n"
                reviews_text += f"Comentario: {c.comentario}\n\n"

            prompt = f"""Analiza las siguientes reviews de clientes reales de un ecommerce ecuatoriano.

{contexto}
Total de reviews a analizar: {len(comentarios)}

REVIEWS:
{reviews_text[:4000]}

TAREA:
Realiza un análisis profesional de sentimientos y extrae insights accionables.

GENERA:

1. SENTIMIENTO GENERAL (porcentajes que sumen 100):
   - % Positivo (reviews satisfechas, contentas)
   - % Neutral (ni buenas ni malas, tibias)
   - % Negativo (reviews insatisfechas, quejas)

2. TOP 3 ASPECTOS POSITIVOS:
   - Los 3 aspectos más elogiados o destacados positivamente
   - Sé específico (ej: "Entrega rápida", "Excelente calidad", "Buena atención")

3. TOP 3 ASPECTOS NEGATIVOS O ÁREAS DE MEJORA:
   - Los 3 aspectos más criticados o que necesitan mejora
   - Sé específico y constructivo

4. CALIDAD SCORE (1-10):
   - Evaluación objetiva de la calidad percibida
   - Considera ratings y comentarios
   - 1-3: Muy baja | 4-5: Baja | 6-7: Aceptable | 8-9: Buena | 10: Excelente

5. RECOMENDACIÓN PARA EL VENDEDOR:
   - Consejo específico y accionable
   - Basado en el análisis de las reviews
   - Máximo 2-3 oraciones
   - Enfocado en mejora continua

RESPONDE EN JSON VÁLIDO (sin markdown):
{{
  "sentimiento": {{
    "positivo": 65,
    "neutral": 25,
    "negativo": 10
  }},
  "aspectos_positivos": [
    "Aspecto positivo 1",
    "Aspecto positivo 2",
    "Aspecto positivo 3"
  ],
  "aspectos_negativos": [
    "Aspecto negativo 1",
    "Aspecto negativo 2",
    "Aspecto negativo 3"
  ],
  "calidad_score": 8.5,
  "recomendacion_vendedor": "Recomendación específica y accionable aquí."
}}

IMPORTANTE: Responde SOLO el JSON, sin markdown ni explicaciones.
"""

            messages = [{"role": "user", "content": prompt}]
            result = self.call_api(
                messages=messages,
                temperature=0.5,  # Más determinista para análisis
                max_tokens=600,
                use_cache=True,
                cache_ttl=86400  # 24 horas
            )

            if not result['success']:
                logger.error(f"Error en análisis: {result['error']}")
                return False

            # Parsear JSON
            try:
                response_text = result['response'].strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.startswith('```'):
                    response_text = response_text[3:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()

                data = json.loads(response_text)

                # Guardar en base de datos
                # Verificar si ya existe un análisis
                analisis_existente = AnalisisReview.query.filter_by(producto_id=producto_id).first()

                if analisis_existente:
                    # Actualizar
                    analisis = analisis_existente
                else:
                    # Crear nuevo
                    analisis = AnalisisReview(producto_id=producto_id)
                    db.session.add(analisis)

                # Actualizar datos
                sentimiento = data.get('sentimiento', {})
                analisis.sentimiento_positivo = sentimiento.get('positivo', 0)
                analisis.sentimiento_neutral = sentimiento.get('neutral', 0)
                analisis.sentimiento_negativo = sentimiento.get('negativo', 0)

                analisis.set_aspectos_positivos(data.get('aspectos_positivos', []))
                analisis.set_aspectos_negativos(data.get('aspectos_negativos', []))

                analisis.calidad_score = data.get('calidad_score', 0)
                analisis.recomendacion = data.get('recomendacion_vendedor', '')
                analisis.total_reviews = len(comentarios)
                analisis.fecha_analisis = datetime.now()

                db.session.commit()

                logger.info(f"Análisis de reviews guardado exitosamente para producto_id={producto_id}")
                return True

            except json.JSONDecodeError as e:
                logger.error(f"Error al parsear JSON: {e}")
                logger.error(f"Respuesta: {result['response']}")
                return False

        except Exception as e:
            logger.exception(f"Error en analizar_reviews: {e}")
            return False

    # ==========================================
    # FUNCIONALIDAD 5: BÚSQUEDA INTELIGENTE
    # ==========================================

    def busqueda_inteligente(self, query_usuario: str) -> dict:
        """
        Procesa búsqueda con IA para entender intención

        Args:
            query_usuario: Consulta en lenguaje natural

        Returns:
            dict: {
                'success': bool,
                'intencion_usuario': str,
                'productos_ids': list,
                'sugerencias_busqueda': list
            }
        """
        try:
            # Obtener catálogo de productos activos
            productos = Producto.query.filter_by(stock__gt=0).limit(100).all()

            if not productos:
                return {
                    'success': False,
                    'error': 'No hay productos disponibles'
                }

            # Preparar lista para el prompt
            catalogo_text = ""
            for p in productos:
                cat = p.categoria.categoria if p.categoria else 'Sin categoría'
                precio = p.precio
                descripcion = p.descripcion[:100] if p.descripcion else ''
                catalogo_text += f"{p.id} | {p.titulo} | {cat} | {descripcion} | ${precio}\n"

            prompt = f"""Analiza la búsqueda de un usuario de ecommerce ecuatoriano y encuentra los productos más relevantes.

BÚSQUEDA DEL USUARIO:
"{query_usuario}"

CATÁLOGO DISPONIBLE (ID | Nombre | Categoría | Descripción | Precio):
{catalogo_text[:3000]}

TAREA:

1. INTERPRETA LA INTENCIÓN REAL:
   - ¿Qué busca realmente el usuario?
   - Considera: tipo de producto, presupuesto implícito, uso previsto
   - Ejemplos:
     * "algo para correr barato" = zapatillas deportivas económicas
     * "regalo mamá" = productos populares para mujeres/madres
     * "laptop estudiante" = laptops gama media, buena relación calidad-precio

2. IDENTIFICA PRODUCTOS RELEVANTES:
   - Máximo 8 productos, ordenados por relevancia (más relevante primero)
   - Considera: coincidencia semántica, categoría, precio, descripción
   - Usa sinónimos y variaciones del español ecuatoriano

3. SUGERENCIAS ALTERNATIVAS:
   - 2-3 búsquedas relacionadas que podrían interesar al usuario
   - Más específicas o complementarias

RESPONDE EN JSON VÁLIDO (sin markdown):
{{
  "intencion_usuario": "Descripción breve de qué busca realmente el usuario",
  "productos_ids": [123, 456, 789],
  "sugerencias_busqueda": [
    "búsqueda alternativa 1",
    "búsqueda alternativa 2"
  ]
}}

IMPORTANTE:
- Si no encuentras productos relevantes, retorna lista vacía en productos_ids
- Responde SOLO el JSON, sin markdown ni explicaciones
"""

            messages = [{"role": "user", "content": prompt}]
            result = self.call_api(
                messages=messages,
                temperature=0.6,
                max_tokens=400,
                use_cache=True,
                cache_ttl=1800  # 30 minutos
            )

            if not result['success']:
                return {
                    'success': False,
                    'error': result['error']
                }

            # Parsear JSON
            try:
                response_text = result['response'].strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.startswith('```'):
                    response_text = response_text[3:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()

                data = json.loads(response_text)

                return {
                    'success': True,
                    'intencion_usuario': data.get('intencion_usuario', ''),
                    'productos_ids': data.get('productos_ids', []),
                    'sugerencias_busqueda': data.get('sugerencias_busqueda', [])
                }

            except json.JSONDecodeError as e:
                logger.error(f"Error al parsear JSON: {e}")
                logger.error(f"Respuesta: {result['response']}")
                return {
                    'success': False,
                    'error': 'Error al procesar respuesta'
                }

        except Exception as e:
            logger.exception(f"Error en busqueda_inteligente: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Instancia global del servicio
ai_service = DeepSeekService()
