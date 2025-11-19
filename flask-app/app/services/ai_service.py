"""
Servicio centralizado para funcionalidades de IA con DeepSeek.

Este módulo maneja:
- Comunicación con API DeepSeek
- Cache de respuestas
- Manejo robusto de errores
- Logging de todas las interacciones
"""

import requests
import json
import hashlib
import logging
from datetime import datetime, timedelta
from app.extensions import db

logger = logging.getLogger(__name__)


class DeepSeekService:
    """Servicio base para interactuar con DeepSeek API."""

    def __init__(self):
        # API key configurada directamente en el backend
        self.api_key = "sk-5967b2b9feb7438dadd1059f600094c9"
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"
        self.cache = {}  # Cache en memoria simple
        self.cache_ttl = 3600  # 1 hora por defecto

    def _get_cache_key(self, prompt: str, context: dict = None) -> str:
        """Genera key única para cache basada en prompt y contexto."""
        data = f"{prompt}_{json.dumps(context or {}, sort_keys=True)}"
        return hashlib.md5(data.encode()).hexdigest()

    def _check_cache(self, cache_key: str):
        """Verifica si hay respuesta en cache válida."""
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
        """Guarda respuesta en cache."""
        if ttl is None:
            ttl = self.cache_ttl
        self.cache[cache_key] = (data, datetime.now())
        logger.info(f"Cache SET para {cache_key[:8]}... (TTL: {ttl}s)")

    def _limpiar_cache_antiguo(self):
        """Limpia entradas de cache expiradas."""
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
        Llamada base a DeepSeek API.

        Args:
            messages: Lista de mensajes [{"role": "user/system", "content": "..."}]
            temperature: Creatividad (0-1). Menor = más determinista
            max_tokens: Límite de tokens de respuesta
            use_cache: Usar sistema de cache
            cache_ttl: TTL personalizado para cache (segundos)

        Returns:
            dict: {
                'success': bool,
                'response': str,
                'error': str (si success=False),
                'tokens_used': int
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
        Genera respuesta del chatbot de ventas.

        Args:
            session_id: ID único de sesión
            user_message: Mensaje del usuario
            context: Contexto adicional (productos en página, carrito, etc.)
            usuario_id: ID del usuario si está logueado

        Returns:
            dict: {'success': bool, 'response': str, 'error': str}
        """
        try:
            from app.models.plantilla import Plantilla
            from app.models.chatbot import ConversacionChatbot

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
                    productos_contexto += f"- {p.get('nombre', 'N/A')}: ${p.get('precio', 0)}\n"

            # Construir contexto de carrito
            carrito_contexto = ""
            if carrito and isinstance(carrito, dict):
                total_items = sum(item.get('cantidad', 0) for item in carrito.values() if isinstance(item, dict))
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

            # Agregar historial (últimos 10 mensajes)
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
                    'response': "Lo siento, estoy teniendo problemas técnicos. Por favor intenta de nuevo en un momento. 😅",
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
        Genera recomendaciones de productos usando IA.

        Args:
            producto_id: ID del producto actual
            usuario_id: ID del usuario (opcional)

        Returns:
            dict: {
                'success': bool,
                'recomendaciones': [...]
            }
        """
        try:
            from app.models.product import Producto
            from app.models.order import Order

            # Obtener producto actual
            producto = Producto.query.get(producto_id)
            if not producto:
                return {'success': False, 'recomendaciones': [], 'error': 'Producto no encontrado'}

            # Obtener catálogo de productos activos (excluir el actual)
            catalogo = Producto.query.filter(
                Producto.activo == True,
                Producto.id != producto_id
            ).limit(50).all()

            if not catalogo:
                return {'success': False, 'recomendaciones': [], 'error': 'No hay productos disponibles'}

            # Obtener historial del usuario si está logueado
            historial = []
            if usuario_id:
                compras = Order.query.filter_by(
                    id_usuario=usuario_id
                ).order_by(Order.fecha.desc()).limit(10).all()

                historial = [c.producto.titulo for c in compras if c.producto]

            # Preparar prompt para IA
            prompt = f"""PRODUCTO ACTUAL:
ID: {producto.id}
Nombre: {producto.titulo}
Precio: ${producto.get_precio_final()}
Categoría: {producto.categoria.categoria if producto.categoria else 'Sin categoría'}
Descripción: {producto.descripcion[:200] if producto.descripcion else 'Sin descripción'}...

CATÁLOGO DISPONIBLE (ID | Nombre | Precio | Categoría):
"""

            for p in catalogo:
                cat_nombre = p.categoria.categoria if p.categoria else 'Sin categoría'
                prompt += f"{p.id} | {p.titulo} | ${p.get_precio_final()} | {cat_nombre}\n"

            if historial:
                prompt += f"\n\nHISTORIAL DEL USUARIO:\nHa comprado: {', '.join(historial[:5])}\n"

            prompt += """
TAREA:
Analiza el producto actual y recomienda los 3-4 mejores productos para maximizar la conversión.

CRITERIOS:
1. Productos complementarios (cross-sell): que se usen juntos
2. Productos similares (upsell): misma categoría, mejor calidad o precio
3. Productos frecuentemente comprados juntos
4. Considera el presupuesto: ±30% del precio actual
5. NO recomiendes el mismo producto actual

RESPONDE EN JSON VÁLIDO (sin texto adicional ni markdown):
{
  "recomendaciones": [
    {
      "producto_id": 123,
      "razon": "Se complementa perfecto para usar junto con este producto",
      "tipo": "complementario"
    }
  ]
}

IMPORTANTE: Responde SOLO el JSON, sin explicaciones ni markdown.
"""

            # Llamar a DeepSeek
            result = self.call_api(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=500,
                use_cache=True,
                cache_ttl=3600  # Cache de 1 hora
            )

            if not result['success']:
                # Fallback: productos aleatorios de la misma categoría
                logger.warning(f"IA falló para recomendaciones, usando fallback")
                fallback_productos = Producto.query.filter(
                    Producto.activo == True,
                    Producto.id != producto_id,
                    Producto.id_categoria == producto.id_categoria
                ).limit(4).all()

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

                return {'success': True, 'recomendaciones': recomendaciones}

            # Parsear respuesta JSON
            try:
                # Limpiar respuesta de markdown si existe
                response_text = result['response'].strip()
                if response_text.startswith('```'):
                    # Remover markdown
                    lines = response_text.split('\n')
                    response_text = '\n'.join([l for l in lines if not l.startswith('```')])

                data = json.loads(response_text)
                recomendaciones_ia = data.get('recomendaciones', [])

                # Enriquecer con datos reales de productos
                recomendaciones = []
                for rec in recomendaciones_ia[:4]:  # Máximo 4
                    prod_id = rec.get('producto_id')
                    p = Producto.query.get(prod_id)

                    if p and p.activo:
                        recomendaciones.append({
                            'producto_id': p.id,
                            'nombre': p.titulo,
                            'precio': float(p.get_precio_final()),
                            'imagen': p.imagen or '/static/images/no-image.jpg',
                            'ruta': p.ruta,
                            'razon': rec.get('razon', 'Recomendado para ti'),
                            'tipo': rec.get('tipo', 'similar')
                        })

                return {'success': True, 'recomendaciones': recomendaciones}

            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON de recomendaciones: {e}")
                logger.error(f"Respuesta IA: {result['response']}")
                # Usar fallback
                return {'success': False, 'recomendaciones': [], 'error': 'Error parsing response'}

        except Exception as e:
            logger.exception(f"Error en obtener_recomendaciones: {e}")
            return {'success': False, 'recomendaciones': [], 'error': str(e)}

    # ==========================================
    # FUNCIONALIDAD 3: GENERADOR DE DESCRIPCIONES
    # ==========================================

    def generar_descripcion_producto(self, nombre: str, categoria: str,
                                    precio: float, caracteristicas: str,
                                    publico: str = '', keywords: str = '') -> dict:
        """
        Genera descripciones profesionales de productos.

        Args:
            nombre: Nombre del producto
            categoria: Categoría del producto
            precio: Precio del producto
            caracteristicas: Características técnicas
            publico: Público objetivo (opcional)
            keywords: Palabras clave SEO (opcional)

        Returns:
            dict: {'success': bool, 'data': {...}}
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

2. DESCRIPCIÓN LARGA (150-200 palabras):
   - SEO optimizada para Ecuador
   - Incluye palabras clave naturalmente
   - Enfocada en BENEFICIOS, no solo características
   - Menciona: calidad, garantía, envío rápido Ecuador
   - Genera urgencia/confianza

3. CINCO BENEFICIOS CLAVE:
   - Formato: "Título del beneficio: breve explicación"
   - Enfocados en el valor para el cliente

4. CALL TO ACTION:
   - Frase persuasiva de cierre
   - Genera urgencia sin ser agresivo

ESTILO:
- Profesional pero accesible
- Español ecuatoriano neutral
- Tono positivo y persuasivo
- Evita exageraciones

RESPONDE EN JSON VÁLIDO (sin markdown ni explicaciones):
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

IMPORTANTE: Responde SOLO el JSON.
"""

            # Llamar a DeepSeek
            result = self.call_api(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=800,
                use_cache=False
            )

            if not result['success']:
                return {
                    'success': False,
                    'data': None,
                    'error': result['error']
                }

            # Parsear JSON
            try:
                response_text = result['response'].strip()
                if response_text.startswith('```'):
                    lines = response_text.split('\n')
                    response_text = '\n'.join([l for l in lines if not l.startswith('```')])

                data = json.loads(response_text)

                return {
                    'success': True,
                    'data': data,
                    'error': None
                }

            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON de descripción: {e}")
                logger.error(f"Respuesta IA: {result['response']}")
                return {
                    'success': False,
                    'data': None,
                    'error': 'Error al parsear respuesta de IA'
                }

        except Exception as e:
            logger.exception(f"Error en generar_descripcion_producto: {e}")
            return {
                'success': False,
                'data': None,
                'error': str(e)
            }

    # ==========================================
    # FUNCIONALIDAD 4: ANÁLISIS DE REVIEWS
    # ==========================================

    def analizar_reviews(self, producto_id: int = None) -> bool:
        """
        Analiza reviews y genera insights con IA.

        Args:
            producto_id: ID del producto (None = análisis general)

        Returns:
            bool: True si se generó exitosamente
        """
        try:
            from app.models.comment import Comentario
            from app.models.product import Producto
            from app.models.analisis_review import AnalisisReview

            # Obtener comentarios aprobados
            query = Comentario.query.filter_by(estado=Comentario.ESTADO_APROBADO)

            if producto_id:
                query = query.filter_by(id_producto=producto_id)
                producto = Producto.query.get(producto_id)
                contexto = f"Producto: {producto.titulo}" if producto else ""
            else:
                contexto = "Análisis general de todos los productos de la tienda"

            comentarios = query.order_by(Comentario.fecha.desc()).limit(100).all()

            if not comentarios:
                logger.info(f"No hay comentarios para analizar (producto_id={producto_id})")
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
{reviews_text}

TAREA:
Realiza un análisis profesional de sentimientos y extrae insights accionables.

GENERA:

1. SENTIMIENTO GENERAL (porcentajes que sumen 100):
   - % Positivo, Neutral, Negativo

2. TOP 3 ASPECTOS POSITIVOS más elogiados

3. TOP 3 ASPECTOS NEGATIVOS o áreas de mejora

4. CALIDAD SCORE (1-10):
   - 1-3: Muy baja | 4-5: Baja | 6-7: Aceptable | 8-9: Buena | 10: Excelente

5. RECOMENDACIÓN PARA EL VENDEDOR (máximo 2-3 oraciones)

RESPONDE EN JSON VÁLIDO (sin markdown):
{{
  "sentimiento": {{
    "positivo": 65,
    "neutral": 25,
    "negativo": 10
  }},
  "aspectos_positivos": ["Aspecto 1", "Aspecto 2", "Aspecto 3"],
  "aspectos_negativos": ["Aspecto 1", "Aspecto 2", "Aspecto 3"],
  "calidad_score": 8.5,
  "recomendacion_vendedor": "Recomendación aquí."
}}

IMPORTANTE: Responde SOLO el JSON.
"""

            # Llamar a DeepSeek
            result = self.call_api(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=600,
                use_cache=True,
                cache_ttl=86400  # Cache de 24 horas
            )

            if not result['success']:
                logger.error(f"Error en análisis de reviews: {result['error']}")
                return False

            # Parsear JSON
            try:
                response_text = result['response'].strip()
                if response_text.startswith('```'):
                    lines = response_text.split('\n')
                    response_text = '\n'.join([l for l in lines if not l.startswith('```')])

                data = json.loads(response_text)

                # Crear o actualizar análisis en BD
                analisis = AnalisisReview.query.filter_by(producto_id=producto_id).first()

                if not analisis:
                    analisis = AnalisisReview(producto_id=producto_id)

                analisis.sentimiento_positivo = data['sentimiento']['positivo']
                analisis.sentimiento_neutral = data['sentimiento']['neutral']
                analisis.sentimiento_negativo = data['sentimiento']['negativo']
                analisis.set_aspectos_positivos(data['aspectos_positivos'])
                analisis.set_aspectos_negativos(data['aspectos_negativos'])
                analisis.calidad_score = data['calidad_score']
                analisis.recomendacion = data['recomendacion_vendedor']
                analisis.total_reviews = len(comentarios)
                analisis.fecha_analisis = datetime.utcnow()

                db.session.add(analisis)
                db.session.commit()

                logger.info(f"Análisis de reviews guardado exitosamente (producto_id={producto_id})")
                return True

            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON de análisis: {e}")
                logger.error(f"Respuesta IA: {result['response']}")
                return False

        except Exception as e:
            logger.exception(f"Error en analizar_reviews: {e}")
            return False

    # ==========================================
    # FUNCIONALIDAD 5: BÚSQUEDA INTELIGENTE
    # ==========================================

    def busqueda_inteligente(self, query_usuario: str) -> dict:
        """
        Procesa búsqueda con IA para entender intención.

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
            from app.models.product import Producto

            # Obtener catálogo de productos activos
            productos = Producto.query.filter_by(activo=True).limit(100).all()

            if not productos:
                return {
                    'success': False,
                    'intencion_usuario': '',
                    'productos_ids': [],
                    'sugerencias_busqueda': []
                }

            # Preparar lista para el prompt
            catalogo_text = ""
            for p in productos:
                cat = p.categoria.categoria if p.categoria else 'Sin categoría'
                precio = p.get_precio_final()
                desc = p.descripcion[:100] if p.descripcion else 'Sin descripción'
                catalogo_text += f"{p.id} | {p.titulo} | {cat} | {desc} | ${precio}\n"

            prompt = f"""Analiza la búsqueda de un usuario de ecommerce ecuatoriano y encuentra los productos más relevantes.

BÚSQUEDA DEL USUARIO:
"{query_usuario}"

CATÁLOGO DISPONIBLE (ID | Nombre | Categoría | Descripción | Precio):
{catalogo_text}

TAREA:

1. INTERPRETA LA INTENCIÓN REAL:
   - ¿Qué busca realmente el usuario?
   - Ejemplos:
     * "algo para correr barato" = zapatillas deportivas económicas
     * "regalo mamá" = productos populares para mujeres/madres
     * "laptop estudiante" = laptops gama media

2. IDENTIFICA PRODUCTOS RELEVANTES (máximo 8, ordenados por relevancia)

3. SUGERENCIAS ALTERNATIVAS (2-3 búsquedas relacionadas)

RESPONDE EN JSON VÁLIDO (sin markdown):
{{
  "intencion_usuario": "Descripción breve",
  "productos_ids": [123, 456, 789],
  "sugerencias_busqueda": ["búsqueda 1", "búsqueda 2"]
}}

IMPORTANTE: Si no encuentras productos relevantes, retorna lista vacía en productos_ids. Responde SOLO el JSON.
"""

            # Llamar a DeepSeek
            result = self.call_api(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=400,
                use_cache=True,
                cache_ttl=1800  # Cache de 30 minutos
            )

            if not result['success']:
                return {
                    'success': False,
                    'intencion_usuario': '',
                    'productos_ids': [],
                    'sugerencias_busqueda': [],
                    'error': result['error']
                }

            # Parsear JSON
            try:
                response_text = result['response'].strip()
                if response_text.startswith('```'):
                    lines = response_text.split('\n')
                    response_text = '\n'.join([l for l in lines if not l.startswith('```')])

                data = json.loads(response_text)

                return {
                    'success': True,
                    'intencion_usuario': data.get('intencion_usuario', ''),
                    'productos_ids': data.get('productos_ids', []),
                    'sugerencias_busqueda': data.get('sugerencias_busqueda', [])
                }

            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON de búsqueda: {e}")
                logger.error(f"Respuesta IA: {result['response']}")
                return {
                    'success': False,
                    'intencion_usuario': '',
                    'productos_ids': [],
                    'sugerencias_busqueda': [],
                    'error': 'Error parsing response'
                }

        except Exception as e:
            logger.exception(f"Error en busqueda_inteligente: {e}")
            return {
                'success': False,
                'intencion_usuario': '',
                'productos_ids': [],
                'sugerencias_busqueda': [],
                'error': str(e)
            }


# Instancia global del servicio
ai_service = DeepSeekService()
