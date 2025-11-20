#!/usr/bin/env python3
"""
Script para reemplazar el método chatbot_response con la versión avanzada
"""

# Leer el archivo
with open('/home/user/Ecommerce_php/flask-app/app/services/ai_service.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar la línea donde empieza chatbot_response (debería ser línea 224 aprox, índice 223)
start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if 'def chatbot_response(self, session_id: str, user_message: str,' in line and start_idx is None:
        # Retroceder para incluir el comentario
        start_idx = i - 4 if i >= 4 and '# FUNCIONALIDAD 1:' in lines[i-4] else i
    if start_idx is not None and end_idx is None and i > start_idx + 10:
        # Buscar el siguiente método o sección
        if (line.strip().startswith('def ') and 'chatbot_response' not in line) or \
           (line.strip().startswith('# =') and 'FUNCIONALIDAD 2' in line):
            end_idx = i
            break

if start_idx is None:
    print("❌ No se encontró el método chatbot_response")
    exit(1)

print(f"📍 Método encontrado en líneas {start_idx + 1} - {end_idx}")

# Nuevo código (sin escapes dobles)
new_code = '''    # ==========================================
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

            # 3. EJECUCIÓN DE FUNCIONES (si aplica)
            resultado_funcion = None
            funcion_ejecutada = None

            if intencion == 'BUSCAR_PRODUCTO':
                query = self._extraer_query_busqueda(user_message)
                if query:
                    logger.info(f"🔍 Buscando productos: '{query}'")
                    resultado_funcion = ejecutar_funcion('buscar_productos', {
                        'query': query,
                        'limit': 5
                    })
                    funcion_ejecutada = 'buscar_productos'

            elif intencion == 'RASTREAR_PEDIDO':
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

            # 4. CONSTRUCCIÓN DEL SYSTEM PROMPT AVANZADO
            system_prompt = self._construir_system_prompt_avanzado(
                contexto_enriquecido=contexto_enriquecido,
                resultado_funcion=resultado_funcion,
                intencion=intencion
            )

            # 5. OBTENER HISTORIAL
            historial = []
            try:
                historial = ConversacionChatbot.get_conversacion(session_id, limit=6)
                historial = list(reversed(historial))
            except Exception as e:
                logger.warning(f"No se pudo obtener historial: {e}")

            # 6. PREPARAR MENSAJES PARA DEEPSEEK
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

            # 7. LLAMAR A DEEPSEEK API
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
                        **context if context else {},
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
            'BUSCAR_PRODUCTO': ['busco', 'quiero', 'necesito', 'tienen', 'venden', 'hay'],
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
                                          resultado_funcion: dict, intencion: str) -> str:
        """Construye system prompt avanzado"""
        prompt = """Eres SOFIA, un asistente de IA AVANZADO para ecommerce en Ecuador 🇪🇨

🎯 CAPACIDADES:
✅ VENDER - Recomendar productos y cerrar ventas
✅ SOPORTAR - Rastrear pedidos, gestionar reclamos
✅ AYUDAR - Calcular envíos, validar cupones, métodos de pago
✅ ANALIZAR - Dar insights de productos y reviews

😊 PERSONALIDAD:
- Amable, profesional, proactiva
- Español ecuatoriano neutral
- 1-2 emojis por mensaje
- Máximo 4-5 oraciones
- Siempre termina con pregunta o CTA

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

        if contexto_enriquecido.get('productos_disponibles'):
            productos = contexto_enriquecido['productos_disponibles']
            prompt += f"\n📦 CATÁLOGO ({len(productos)} productos):\n"
            for p in productos[:8]:
                prompt += f"- {p['nombre']}: ${p['precio']} ({p['categoria']})\n"

        if resultado_funcion:
            prompt += f"\n🔧 RESULTADO:\n```json\n{json.dumps(resultado_funcion, indent=2, ensure_ascii=False)}\n```\n"
            prompt += "📌 USA esta info para responder específicamente.\n"

        if intencion == 'BUSCAR_PRODUCTO':
            prompt += "\n🎯 Muestra los productos con precio, stock y características. Sugiere el mejor.\n"
        elif intencion == 'RASTREAR_PEDIDO':
            prompt += "\n🎯 Informa el estado claramente. Si en camino, da fecha. Si problema, ofrece solución.\n"
        elif intencion == 'CONSULTA_ENVIO':
            prompt += "\n🎯 Explica costo y tiempo. Menciona envío gratis >$50.\n"
        elif intencion == 'APLICAR_CUPON':
            prompt += "\n🎯 Si válido, celebra. Si no, explica por qué y sugiere alternativas.\n"

        prompt += "\n❌ PROHIBIDO: Inventar productos, precios incorrectos, respuestas genéricas\n"
        prompt += "✅ SIEMPRE: Productos específicos con nombre/precio, pregunta final, ser útil\n"

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
        patron = r'\\b[A-Z0-9]{4,12}\\b'
        matches = re.findall(patron, mensaje.upper())
        return matches[0] if matches else None

'''

# Reemplazar
new_lines = lines[:start_idx] + [new_code] + lines[end_idx:]

# Guardar
with open('/home/user/Ecommerce_php/flask-app/app/services/ai_service.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"✅ Método chatbot_response reemplazado (líneas {start_idx + 1} - {end_idx})")
print("✅ Agregados 6 métodos auxiliares")
print("✅ Chatbot avanzado con detección de intención implementado")
