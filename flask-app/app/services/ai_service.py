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
import re
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app
from sqlalchemy import func
from app.extensions import db
from app.models.product import Producto
from app.models.comment import Comentario
from app.models.categoria import Categoria
from app.models.order import Compra
from app.models.user import User

logger = logging.getLogger(__name__)

class DeepSeekService:
    """Servicio base para interactuar con DeepSeek API"""

    def __init__(self):
        self.cache = {}  # Cache en memoria simple
        self._config_loaded = False
        self.api_key = None
        self.api_url = None
        self.model = None
        self.cache_ttl = None

    def _load_config(self):
        """Carga la configuración de Flask de manera lazy"""
        if self._config_loaded:
            return

        try:
            from flask import current_app
            self.api_key = current_app.config.get('DEEPSEEK_API_KEY', 'sk-5967b2b9feb7438dadd1059f600094c9')
            self.api_url = current_app.config.get('DEEPSEEK_API_URL', 'https://api.deepseek.com/chat/completions')  # Sin /v1
            self.model = current_app.config.get('DEEPSEEK_MODEL', 'deepseek-chat')
            self.cache_ttl = current_app.config.get('DEEPSEEK_CACHE_TTL', 3600)
            self._config_loaded = True
            logger.info(f"✅ Configuración de IA cargada: API={self.api_url}, Model={self.model}")
        except RuntimeError:
            # Fallback si no hay contexto de Flask
            logger.warning("⚠️ No hay contexto de Flask, usando configuración por defecto")
            self.api_key = "sk-5967b2b9feb7438dadd1059f600094c9"
            self.api_url = "https://api.deepseek.com/chat/completions"  # Sin /v1
            self.model = "deepseek-chat"
            self.cache_ttl = 3600
            self._config_loaded = True

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
        # Cargar configuración (lazy loading)
        self._load_config()

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

    # ==========================================
    # FUNCIONALIDAD 1: CHATBOT AVANZADO
    # ==========================================

    def chatbot_response(self, session_id: str, user_message: str,
                        context: dict = None, usuario_id: int = None) -> dict:
        """
        Chatbot AVANZADO con detección de intención y function calling

        Capacidades:
        1. Detecta la intención del usuario (buscar, rastrear, reclamo, etc.)
        2. Ejecuta funciones específicas según la intención
        3. Enriquece el contexto con datos del usuario
        4. Genera respuesta inteligente con DeepSeek

        Args:
            session_id: ID único de sesión
            user_message: Mensaje del usuario
            context: Contexto adicional (productos, carrito, etc.)
            usuario_id: ID del usuario si está logueado

        Returns:
            dict: {'success': bool, 'response': str, 'error': str, 'intencion': str}
        """
        try:
            from app.models.setting import Plantilla
            from app.models.chatbot import ConversacionChatbot
            from app.services.chatbot_tools import ejecutar_funcion

            logger.info(f"🤖 Procesando mensaje: '{user_message[:50]}...'")

            # 1. DETECCIÓN DE INTENCIÓN
            intencion = self._detectar_intencion(user_message)
            logger.info(f"🎯 Intención detectada: {intencion}")

            # 2. ENRIQUECIMIENTO DE CONTEXTO
            contexto_enriquecido = self._enriquecer_contexto(
                usuario_id=usuario_id,
                context=context or {},
                user_message=user_message
            )

            # 3. BÚSQUEDA INTELIGENTE DE PRODUCTOS (SIEMPRE)
            # Buscar productos mencionados en CUALQUIER mensaje para que la IA razone
            productos_encontrados = []
            palabras_clave = self._extraer_palabras_clave(user_message)
            if palabras_clave:
                logger.info(f"🔍 Búsqueda inteligente: '{palabras_clave}'")
                productos_encontrados = ejecutar_funcion('buscar_productos', {
                    'query': palabras_clave,
                    'limit': 8
                })

            # 4. EJECUCIÓN DE FUNCIONES ESPECÍFICAS (si aplica)
            resultado_funcion = None
            funcion_ejecutada = None

            if intencion == 'BUSCAR_PRODUCTO' and not productos_encontrados:
                # Si no encontró nada en búsqueda inteligente, intentar búsqueda específica
                query = self._extraer_query_busqueda(user_message)
                if query:
                    logger.info(f"🔍 Búsqueda específica: '{query}'")
                    productos_encontrados = ejecutar_funcion('buscar_productos', {
                        'query': query,
                        'limit': 8
                    })

            if intencion == 'RASTREAR_PEDIDO':
                if usuario_id:
                    logger.info(f"📦 Rastreando pedido para usuario {usuario_id}")
                    resultado_funcion = ejecutar_funcion('rastrear_pedido', {
                        'usuario_id': usuario_id
                    })
                    funcion_ejecutada = 'rastrear_pedido'
                else:
                    resultado_funcion = {'error': 'Necesitas iniciar sesión para rastrear tu pedido'}

            elif intencion == 'CONSULTA_ENVIO':
                ciudad = self._extraer_ciudad(user_message)
                if ciudad:
                    logger.info(f"🚚 Calculando envío a: {ciudad}")
                    resultado_funcion = ejecutar_funcion('calcular_envio', {
                        'ciudad': ciudad
                    })
                    funcion_ejecutada = 'calcular_envio'

            elif intencion == 'APLICAR_CUPON':
                codigo = self._extraer_codigo_cupon(user_message)
                if codigo:
                    total_carrito = contexto_enriquecido.get('carrito', {}).get('total_valor', 0)
                    logger.info(f"🎟️ Validando cupón: {codigo}")
                    resultado_funcion = ejecutar_funcion('validar_cupon', {
                        'codigo_cupon': codigo,
                        'total_compra': total_carrito or 100,
                        'usuario_id': usuario_id
                    })
                    funcion_ejecutada = 'validar_cupon'

            elif intencion == 'RECOMENDACION':
                logger.info(f"💡 Generando recomendaciones personalizadas")
                resultado_funcion = ejecutar_funcion('obtener_recomendaciones', {
                    'usuario_id': usuario_id,
                    'limite': 3
                })
                funcion_ejecutada = 'obtener_recomendaciones'

            elif intencion == 'CONSULTA_PAGO':
                total_carrito = contexto_enriquecido.get('carrito', {}).get('total_valor', 0)
                logger.info(f"💳 Consultando métodos de pago")
                resultado_funcion = ejecutar_funcion('metodos_pago', {
                    'total': total_carrito or 100
                })
                funcion_ejecutada = 'metodos_pago'

            # 5. CONSTRUCCIÓN DEL SYSTEM PROMPT AVANZADO
            system_prompt = self._construir_system_prompt_avanzado(
                contexto_enriquecido=contexto_enriquecido,
                resultado_funcion=resultado_funcion,
                productos_encontrados=productos_encontrados,
                intencion=intencion
            )

            # 6. OBTENER HISTORIAL
            historial = []
            try:
                historial = ConversacionChatbot.get_conversacion(session_id, limit=6)
                historial = list(reversed(historial))
            except Exception as e:
                logger.warning(f"No se pudo obtener historial: {e}")

            # 7. PREPARAR MENSAJES PARA DEEPSEEK
            messages = [{"role": "system", "content": system_prompt}]

            for conv in historial[-6:]:
                messages.append({
                    "role": conv.rol,
                    "content": conv.mensaje
                })

            messages.append({
                "role": "user",
                "content": user_message
            })

            # 8. LLAMAR A DEEPSEEK API
            logger.info(f"🧠 Llamando a DeepSeek con intención: {intencion}")
            result = self.call_api(
                messages=messages,
                temperature=0.7,
                max_tokens=800,
                use_cache=False
            )

            if result['success']:
                # 8. GUARDAR CONVERSACIÓN
                try:
                    conv_user = ConversacionChatbot(
                        session_id=session_id,
                        usuario_id=usuario_id,
                        rol='user',
                        mensaje=user_message
                    )
                    conv_user.set_contexto({
                        **(context if context else {}),
                        'intencion': intencion,
                        'funcion_ejecutada': funcion_ejecutada
                    })
                    db.session.add(conv_user)

                    conv_assistant = ConversacionChatbot(
                        session_id=session_id,
                        usuario_id=usuario_id,
                        rol='assistant',
                        mensaje=result['response']
                    )
                    db.session.add(conv_assistant)
                    db.session.commit()
                except Exception as e:
                    logger.warning(f"No se pudo guardar conversación: {e}")
                    db.session.rollback()

                logger.info(f"✅ Respuesta generada exitosamente")
                return {
                    'success': True,
                    'response': result['response'],
                    'error': None,
                    'intencion': intencion,
                    'funcion_ejecutada': funcion_ejecutada
                }
            else:
                logger.error(f"Error en chatbot: {result['error']}")
                return {
                    'success': False,
                    'response': "Lo siento, estoy teniendo problemas técnicos. ¿Puedes intentar de nuevo?",
                    'error': result['error']
                }

        except Exception as e:
            logger.exception(f"💥 Error crítico en chatbot_response: {e}")
            return {
                'success': False,
                'response': "Lo siento, ocurrió un error inesperado. Por favor intenta de nuevo.",
                'error': str(e)
            }

    def _detectar_intencion(self, mensaje: str) -> str:
        """Detecta la intención del usuario basándose en palabras clave"""
        mensaje_lower = mensaje.lower()

        patrones = {
            'RASTREAR_PEDIDO': ['pedido', 'orden', 'envío', 'tracking', 'dónde está', 'cuándo llega'],
            'RECLAMO': ['reclamo', 'devolver', 'defectuoso', 'problema', 'no llegó', 'malo', 'queja'],
            'CONSULTA_ENVIO': ['cuesta envío', 'envío a', 'cuánto cuesta enviar', 'demora'],
            'APLICAR_CUPON': ['cupón', 'código', 'descuento', 'promoción', 'promo'],
            'CONSULTA_PAGO': ['pago', 'pagar', 'tarjeta', 'efectivo', 'paypal', 'transferencia'],
            'RECOMENDACION': ['recomienda', 'sugiere', 'qué comprar', 'ayuda a elegir'],
            'COMPARACION': ['comparar', 'diferencia', 'mejor', 'vs', 'versus'],
            'BUSCAR_PRODUCTO': ['busco', 'quiero', 'necesito', 'tienen', 'venden', 'hay', 'precio de', 'cuesta', 'cuánto', 'stock', 'disponible', 'unidades', 'descripción'],
        }

        for intencion, keywords in patrones.items():
            if any(keyword in mensaje_lower for keyword in keywords):
                return intencion

        return 'CONVERSACION_GENERAL'

    def _enriquecer_contexto(self, usuario_id: int, context: dict, user_message: str) -> dict:
        """Enriquece el contexto con información del usuario"""
        contexto = {
            **context,
            'usuario': None,
            'carrito': context.get('carrito', {}),
            'productos_disponibles': []
        }

        if usuario_id:
            try:
                user = User.query.get(usuario_id)
                if user:
                    compras = Compra.query.filter_by(id_usuario=usuario_id).count()
                    gasto_total = db.session.query(func.sum(Compra.precio_total)).filter_by(
                        id_usuario=usuario_id
                    ).scalar() or 0

                    contexto['usuario'] = {
                        'id': user.id,
                        'nombre': user.nombre,
                        'email': user.email,
                        'compras_totales': compras,
                        'gasto_total': float(gasto_total),
                        'es_cliente_frecuente': compras >= 3
                    }
            except Exception as e:
                logger.warning(f"Error al cargar usuario: {e}")

        try:
            productos_db = Producto.query.filter(
                Producto.stock > 0
            ).order_by(Producto.ventas.desc()).limit(15).all()

            for p in productos_db:
                contexto['productos_disponibles'].append({
                    'id': p.id,
                    'nombre': p.titulo,
                    'precio': float(p.get_price()),
                    'categoria': p.categoria.categoria if p.categoria else 'Sin categoría',
                    'stock': p.stock,
                    'rating': p.get_average_rating()
                })
        except Exception as e:
            logger.warning(f"Error al cargar productos: {e}")

        return contexto

    def _construir_system_prompt_avanzado(self, contexto_enriquecido: dict,
                                          resultado_funcion: dict, productos_encontrados: list,
                                          intencion: str) -> str:
        """Construye system prompt avanzado con RAZONAMIENTO sobre datos reales"""
        prompt = """Eres SOFIA, un asistente de IA AVANZADO para ecommerce en Ecuador 🇪🇨

🎯 CAPACIDADES:
✅ VENDER - Recomendar productos y cerrar ventas
✅ SOPORTAR - Rastrear pedidos, gestionar reclamos
✅ AYUDAR - Calcular envíos, validar cupones, métodos de pago
✅ ANALIZAR - Dar insights de productos y reviews
✅ RAZONAR - Usar inteligencia para interpretar preguntas y conectar con datos reales

😊 PERSONALIDAD:
- Amable, profesional, proactiva
- Español ecuatoriano neutral
- 1-2 emojis por mensaje
- Máximo 4-5 oraciones
- Siempre termina con pregunta o CTA

⚠️ REGLA DE ORO - DATOS REALES:
- SIEMPRE usa los datos de la base de datos proporcionados
- NUNCA inventes precios, stock, o productos que no existen
- 🚨 CRÍTICO: NUNCA digas "no tenemos X" sin haber verificado los datos
- 🚨 Si la búsqueda no encuentra nada, PREGUNTA al usuario por más detalles ("¿Puedes ser más específico? ¿Qué marca o características buscas?")
- Si el usuario pregunta con sinónimos (ej: "portátil" por "laptop", "tv" por "televisor"), RAZONA y encuentra el producto correcto
- Si pregunta "algo para trabajar", RAZONA qué productos son apropiados (laptops, escritorios)
- Si pregunta "tengo $X, qué me alcanza?", RAZONA y filtra por presupuesto
- Los precios y stock cambian en tiempo real, usa SOLO los datos actuales
- Supera las expectativas con información precisa, razonada e inteligente
- 🚨 MUY IMPORTANTE: Si NO ves productos en la lista pero el usuario insiste que existen, RECONÓCELO y pide disculpas

📋 INFO TIENDA:
- Envíos 24-48h a todo Ecuador
- Envío GRATIS sobre $50
- Métodos: Tarjeta, PayPal, Transferencia, Contra entrega
- Garantía 30 días
"""

        if contexto_enriquecido.get('usuario'):
            usuario = contexto_enriquecido['usuario']
            prompt += f"\n👤 CLIENTE: {usuario['nombre']}"
            if usuario['es_cliente_frecuente']:
                prompt += " ⭐ (VIP)"
            prompt += f" | Compras: {usuario['compras_totales']}\n"

        if contexto_enriquecido.get('carrito', {}).get('total_items', 0) > 0:
            carrito = contexto_enriquecido['carrito']
            prompt += f"\n🛒 CARRITO: {carrito['total_items']} items\n"

        # PRODUCTOS ENCONTRADOS (búsqueda inteligente)
        if productos_encontrados and len(productos_encontrados) > 0:
            prompt += f"\n🔍 PRODUCTOS ENCONTRADOS ({len(productos_encontrados)} resultados relevantes):\n"
            prompt += "```json\n"
            prompt += json.dumps(productos_encontrados, indent=2, ensure_ascii=False)
            prompt += "\n```\n"
            prompt += "⚠️ ESTOS SON LOS PRODUCTOS REALES DE LA BD. USA ESTOS DATOS PARA RESPONDER.\n"
            prompt += "💡 RAZONA: Si el usuario pregunta de forma indirecta, conecta su pregunta con estos productos.\n"
        else:
            # NO se encontraron productos en la búsqueda
            prompt += "\n⚠️ ATENCIÓN: La búsqueda automática NO encontró productos con las palabras clave extraídas.\n"
            prompt += "🚨 IMPORTANTE: Esto NO significa que no existan. Puede ser un problema de sinónimos o búsqueda.\n"
            prompt += "📌 RESPUESTA CORRECTA: Pide al usuario más detalles (marca, características, categoría específica).\n"
            prompt += "❌ PROHIBIDO: Decir 'no tenemos X' o 'no está disponible' sin verificar el catálogo general.\n"

        if contexto_enriquecido.get('productos_disponibles'):
            productos = contexto_enriquecido['productos_disponibles']
            prompt += f"\n📦 CATÁLOGO GENERAL ({len(productos)} productos más populares):\n"
            for p in productos[:6]:
                prompt += f"- {p['nombre']}: ${p['precio']} | Stock: {p['stock']} | {p['categoria']}\n"

        if resultado_funcion:
            prompt += f"\n🔧 DATOS ADICIONALES:\n```json\n{json.dumps(resultado_funcion, indent=2, ensure_ascii=False)}\n```\n"

        # Instrucciones según intención
        if productos_encontrados and len(productos_encontrados) > 0:
            prompt += "\n🎯 INSTRUCCIONES PARA RESPONDER:\n"
            prompt += "- Analiza los productos encontrados y RAZONA cuál es el mejor para el usuario\n"
            prompt += "- Si pregunta precio, usa el precio EXACTO de la BD\n"
            prompt += "- Si pregunta stock, usa el stock EXACTO de la BD\n"
            prompt += "- Si pregunta descripción, usa la descripción REAL del producto\n"
            prompt += "- Si hay múltiples opciones, compara y sugiere la mejor\n"
            prompt += "- Si no hay stock, dilo claramente y sugiere alternativas\n"
            prompt += "- RAZONA sobre las especificaciones y características para dar la mejor recomendación\n"

        if intencion == 'BUSCAR_PRODUCTO':
            prompt += "\n🎯 El usuario está buscando productos. Razona y recomienda el mejor.\n"
        elif intencion == 'RASTREAR_PEDIDO':
            prompt += "\n🎯 Informa el estado claramente. Si en camino, da fecha. Si problema, ofrece solución.\n"
        elif intencion == 'CONSULTA_ENVIO':
            prompt += "\n🎯 Explica costo y tiempo. Menciona envío gratis >$50.\n"
        elif intencion == 'APLICAR_CUPON':
            prompt += "\n🎯 Si válido, celebra. Si no, explica por qué y sugiere alternativas.\n"

        prompt += """
FORMATO DE RESPUESTA:
- Usa **negritas** para nombres de productos o información importante
- Usa listas con guion (-) para múltiples items
- Mantén párrafos cortos y claros
- Usa emojis con moderación (1-2 por mensaje)
- Separa secciones con saltos de línea para mejor lectura

EJEMPLO BUENO:
"¡Perfecto! Te recomiendo la **Laptop HP i5 8GB** por $899.

Características principales:
- Ideal para trabajo y estudio
- 8GB RAM y 256GB SSD
- Batería de 8 horas
- Incluye garantía de 30 días

El envío a Quito es de $3.50 (gratis si superas $50). ¿Te gustaría agregarla al carrito?"

PROHIBIDO:
- Inventar productos que no están en el catálogo
- Dar precios incorrectos
- Usar secciones TODO EN MAYÚSCULAS con etiquetas
- Respuestas genéricas sin productos específicos
"""

        return prompt

    def _extraer_query_busqueda(self, mensaje: str) -> str:
        """Extrae término de búsqueda"""
        palabras_ignorar = ['busco', 'quiero', 'necesito', 'tienen', 'venden', 'hay']
        mensaje_lower = mensaje.lower()
        for palabra in palabras_ignorar:
            mensaje_lower = mensaje_lower.replace(palabra, '')
        query = mensaje_lower.strip()
        return query if len(query) > 2 else mensaje

    def _extraer_ciudad(self, mensaje: str) -> str:
        """Extrae ciudad del mensaje"""
        ciudades = ['quito', 'guayaquil', 'cuenca', 'ambato', 'manta', 'portoviejo',
                    'machala', 'loja', 'esmeraldas', 'ibarra', 'riobamba']
        mensaje_lower = mensaje.lower()
        for ciudad in ciudades:
            if ciudad in mensaje_lower:
                return ciudad.capitalize()
        return 'Quito'

    def _extraer_codigo_cupon(self, mensaje: str) -> Optional[str]:
        """Extrae código de cupón"""
        patron = r'\b[A-Z0-9]{4,12}\b'
        matches = re.findall(patron, mensaje.upper())
        return matches[0] if matches else None

    def _extraer_palabras_clave(self, mensaje: str) -> str:
        """
        Extrae palabras clave del mensaje para búsqueda inteligente
        Filtra palabras comunes y extrae términos relevantes
        """
        # Palabras a ignorar (stopwords en español)
        stopwords = {
            'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
            'de', 'del', 'al', 'a', 'en', 'con', 'por', 'para',
            'que', 'es', 'son', 'está', 'están', 'hay', 'tiene', 'tienen',
            'me', 'te', 'se', 'le', 'lo', 'mi', 'tu', 'su',
            'y', 'o', 'pero', 'si', 'no', 'ni',
            'busco', 'quiero', 'necesito', 'venden', 'cuánto', 'cuesta',
            'precio', 'cuál', 'qué', 'cómo', 'dónde', 'cuándo',
            'puede', 'puedo', 'podría', 'podrías', 'algo', 'algún', 'alguna',
            'este', 'esta', 'ese', 'esa', 'aquel', 'aquella',
            'muy', 'más', 'menos', 'mucho', 'poco', 'bastante',
            'hola', 'gracias', 'por', 'favor'
        }

        # Convertir a minúsculas y dividir en palabras
        palabras = mensaje.lower().split()

        # Filtrar stopwords y palabras cortas
        palabras_clave = [
            p for p in palabras
            if len(p) > 2 and p not in stopwords and not p.isdigit()
        ]

        # Unir palabras clave
        query = ' '.join(palabras_clave)

        # Si la query está vacía o muy corta, retornar el mensaje original
        if not query or len(query) < 3:
            return mensaje

        logger.debug(f"Palabras clave extraídas: '{query}' de '{mensaje}'")
        return query

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
