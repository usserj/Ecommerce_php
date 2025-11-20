# 🔧 Instrucciones para Actualizar el Chatbot a Versión Avanzada

## 📋 Resumen

Ya he creado TODO el sistema de chatbot avanzado:
- ✅ 12 funciones/herramientas listas (`chatbot_tools.py`)
- ✅ Documentación completa del sistema
- ✅ Sistema de function calling implementado

**FALTA**: Modificar `ai_service.py` para usar las herramientas con detección de intención automática.

---

## 🎯 Cambio Requerido

**Archivo**: `flask-app/app/services/ai_service.py`
**Método**: `chatbot_response()` (líneas 224-427)
**Acción**: REEMPLAZAR completamente por versión avanzada

---

## 🚀 Opción 1: Cambio Manual (RECOMENDADO)

### Paso 1: Abrir el archivo

```bash
cd /home/user/Ecommerce_php/flask-app/app/services
nano ai_service.py
```

### Paso 2: Ir a la línea 224

Busca el método:
```python
def chatbot_response(self, session_id: str, user_message: str,
                    context: dict = None, usuario_id: int = None) -> dict:
```

### Paso 3: Eliminar todo el método

Desde la línea 224 hasta la 427 (antes de `def obtener_recomendaciones`)

### Paso 4: Pegar el nuevo método

(Ver código completo en la sección de abajo)

---

## 💻 Código Completo del Nuevo Método

```python
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
            dict: {'success': bool, 'response': str, 'error': str, 'function_used': str}
        """
        try:
            from app.models.setting import Plantilla
            from app.models.chatbot import ConversacionChatbot
            from app.models.user import User
            from app.services.chatbot_tools import ejecutar_funcion
            import re

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
                # Extraer query de búsqueda
                query = self._extraer_query_busqueda(user_message)
                if query:
                    logger.info(f"🔍 Buscando productos: '{query}'")
                    resultado_funcion = ejecutar_funcion('buscar_productos', {
                        'query': query,
                        'limit': 5
                    })
                    funcion_ejecutada = 'buscar_productos'

            elif intencion == 'RASTREAR_PEDIDO':
                # Rastrear pedido del usuario
                if usuario_id:
                    logger.info(f"📦 Rastreando pedido para usuario {usuario_id}")
                    resultado_funcion = ejecutar_funcion('rastrear_pedido', {
                        'usuario_id': usuario_id
                    })
                    funcion_ejecutada = 'rastrear_pedido'
                else:
                    resultado_funcion = {'error': 'Necesitas iniciar sesión para rastrear tu pedido'}

            elif intencion == 'CONSULTA_ENVIO':
                # Extraer ciudad
                ciudad = self._extraer_ciudad(user_message)
                if ciudad:
                    logger.info(f"🚚 Calculando envío a: {ciudad}")
                    resultado_funcion = ejecutar_funcion('calcular_envio', {
                        'ciudad': ciudad
                    })
                    funcion_ejecutada = 'calcular_envio'

            elif intencion == 'APLICAR_CUPON':
                # Extraer código de cupón
                codigo = self._extraer_codigo_cupon(user_message)
                if codigo:
                    total_carrito = contexto_enriquecido.get('carrito', {}).get('total_valor', 0)
                    logger.info(f"🎟️ Validando cupón: {codigo}")
                    resultado_funcion = ejecutar_funcion('validar_cupon', {
                        'codigo_cupon': codigo,
                        'total_compra': total_carrito,
                        'usuario_id': usuario_id
                    })
                    funcion_ejecutada = 'validar_cupon'

            elif intencion == 'RECOMENDACION':
                # Obtener recomendaciones personalizadas
                logger.info(f"💡 Generando recomendaciones personalizadas")
                resultado_funcion = ejecutar_funcion('obtener_recomendaciones', {
                    'usuario_id': usuario_id,
                    'limite': 3
                })
                funcion_ejecutada = 'obtener_recomendaciones'

            elif intencion == 'CONSULTA_PAGO':
                # Métodos de pago disponibles
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

            # Agregar historial (últimos 6 mensajes)
            for conv in historial[-6:]:
                messages.append({
                    "role": conv.rol,
                    "content": conv.mensaje
                })

            # Agregar mensaje actual
            messages.append({
                "role": "user",
                "content": user_message
            })

            # 7. LLAMAR A DEEPSEEK API
            logger.info(f"🧠 Llamando a DeepSeek API con intención: {intencion}")
            result = self.call_api(
                messages=messages,
                temperature=0.7,
                max_tokens=800,  # Aumentado para respuestas más completas
                use_cache=False
            )

            if result['success']:
                # 8. GUARDAR CONVERSACIÓN EN BD
                try:
                    conv_user = ConversacionChatbot(
                        session_id=session_id,
                        usuario_id=usuario_id,
                        rol='user',
                        mensaje=user_message
                    )
                    conv_user.set_contexto({
                        **context,
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

    # ==========================================
    # MÉTODOS AUXILIARES PARA CHATBOT AVANZADO
    # ==========================================

    def _detectar_intencion(self, mensaje: str) -> str:
        """
        Detecta la intención del usuario basándose en palabras clave

        Returns:
            str: Intención detectada (BUSCAR_PRODUCTO, RASTREAR_PEDIDO, etc.)
        """
        mensaje_lower = mensaje.lower()

        # Patrones de intención
        patrones = {
            'RASTREAR_PEDIDO': ['pedido', 'orden', 'envío', 'tracking', 'dónde está', 'cuándo llega', 'delivery'],
            'RECLAMO': ['reclamo', 'devolver', 'devolución', 'defectuoso', 'problema', 'no llegó', 'malo', 'queja'],
            'CONSULTA_ENVIO': ['cuesta envío', 'envío a', 'cuánto cuesta enviar', 'shipping', 'demora'],
            'APLICAR_CUPON': ['cupón', 'código', 'descuento', 'promoción', 'promo', 'cupon'],
            'CONSULTA_PAGO': ['pago', 'pagar', 'tarjeta', 'efectivo', 'paypal', 'transferencia', 'métodos de pago'],
            'RECOMENDACION': ['recomienda', 'sugiere', 'qué comprar', 'ayuda a elegir', 'qué me conviene'],
            'COMPARACION': ['comparar', 'diferencia', 'mejor', 'vs', 'versus'],
            'BUSCAR_PRODUCTO': ['busco', 'quiero', 'necesito', 'tienen', 'venden', 'hay', 'producto', 'comprar'],
        }

        # Buscar coincidencias
        for intencion, keywords in patrones.items():
            if any(keyword in mensaje_lower for keyword in keywords):
                return intencion

        # Si no detecta intención específica, asumir conversación general
        return 'CONVERSACION_GENERAL'

    def _enriquecer_contexto(self, usuario_id: int, context: dict, user_message: str) -> dict:
        """
        Enriquece el contexto con información del usuario y sistema

        Returns:
            dict: Contexto enriquecido con datos del usuario, carrito, productos, etc.
        """
        contexto = {
            **context,
            'usuario': None,
            'carrito': context.get('carrito', {}),
            'productos_disponibles': []
        }

        # Agregar información del usuario si está logueado
        if usuario_id:
            try:
                from app.models.user import User
                user = User.query.get(usuario_id)
                if user:
                    # Obtener historial de compras
                    compras = Compra.query.filter_by(id_usuario=usuario_id).count()
                    gasto_total = db.session.query(func.sum(Compra.precio_total)).filter_by(id_usuario=usuario_id).scalar() or 0

                    contexto['usuario'] = {
                        'id': user.id,
                        'nombre': user.nombre,
                        'email': user.email,
                        'compras_totales': compras,
                        'gasto_total': float(gasto_total),
                        'es_cliente_frecuente': compras >= 3
                    }
            except Exception as e:
                logger.warning(f"Error al cargar info de usuario: {e}")

        # Cargar productos disponibles (top 15)
        try:
            productos_db = Producto.query.filter(Producto.stock > 0).order_by(
                Producto.ventas.desc()
            ).limit(15).all()

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
        """
        Construye un system prompt avanzado con toda la información disponible

        Returns:
            str: System prompt completo para DeepSeek
        """
        # Base del prompt
        prompt = """Eres SOFIA, un asistente de IA AVANZADO para una tienda de ecommerce en Ecuador.

🎯 TU MISIÓN:
No eres un chatbot básico. Eres un asistente inteligente que puede:
✅ VENDER - Recomendar productos personalizados y cerrar ventas
✅ SOPORTAR - Resolver problemas, rastrear pedidos, gestionar reclamos
✅ AYUDAR - Calcular envíos, validar cupones, explicar métodos de pago
✅ PROTEGER - Validar datos, detectar fraudes
✅ ANALIZAR - Dar insights basados en reviews y estadísticas

🧠 CAPACIDADES ESPECIALES:
- Acceso a base de datos de productos en tiempo real
- Puedes rastrear pedidos automáticamente
- Calculas costos de envío al instante
- Validas y aplicas cupones
- Tienes memoria de conversaciones pasadas
- Conoces el historial de compras del usuario

😊 PERSONALIDAD:
- Amable, profesional, proactiva
- Español ecuatoriano neutral
- Orientada a ayudar Y vender
- Usa 1-2 emojis relevantes por mensaje
- Respuestas concisas pero completas (máximo 4-5 oraciones)
- Siempre terminas con pregunta o llamado a acción

📋 INFORMACIÓN DE LA TIENDA:
- Ecommerce en Ecuador 🇪🇨
- Envíos a todo el país en 24-48 horas
- Envío GRATIS en compras sobre $50
- Métodos de pago: Tarjeta, PayPal, Transferencia, Contra entrega
- Garantía de 30 días en todos los productos
- Atención 24/7 vía chat
"""

        # Agregar información del usuario si existe
        if contexto_enriquecido.get('usuario'):
            usuario = contexto_enriquecido['usuario']
            prompt += f"\n\n👤 CLIENTE ACTUAL:\n"
            prompt += f"- Nombre: {usuario['nombre']}\n"
            prompt += f"- Compras previas: {usuario['compras_totales']}\n"
            if usuario['es_cliente_frecuente']:
                prompt += f"- ⭐ Cliente frecuente (trato especial)\n"
            prompt += f"- Gasto total histórico: ${usuario['gasto_total']:.2f}\n"

        # Agregar información del carrito
        if contexto_enriquecido.get('carrito', {}).get('total_items', 0) > 0:
            carrito = contexto_enriquecido['carrito']
            prompt += f"\n\n🛒 CARRITO ACTUAL:\n"
            prompt += f"- {carrito['total_items']} producto(s)\n"
            if 'total_valor' in carrito:
                prompt += f"- Valor total: ${carrito['total_valor']:.2f}\n"

        # Agregar catálogo de productos
        if contexto_enriquecido.get('productos_disponibles'):
            productos = contexto_enriquecido['productos_disponibles']
            prompt += f"\n\n📦 CATÁLOGO (Top {len(productos)} productos):\n"
            for p in productos[:10]:
                prompt += f"- {p['nombre']}: ${p['precio']} ({p['categoria']}) - Stock: {p['stock']}\n"
            prompt += "\n⚠️ USA SOLO estos productos reales. NO inventes.\n"

        # Agregar resultado de función si se ejecutó
        if resultado_funcion:
            prompt += f"\n\n🔧 RESULTADO DE ACCIÓN EJECUTADA:\n"
            prompt += f"```json\n{json.dumps(resultado_funcion, indent=2, ensure_ascii=False)}\n```\n"
            prompt += "\n📌 USA esta información para responder de forma específica y útil.\n"

        # Instrucciones específicas según intención
        if intencion == 'BUSCAR_PRODUCTO':
            prompt += "\n\n🎯 INSTRUCCIÓN: El usuario busca un producto. Muestra los resultados con precios, stock y características. Sugiere el mejor según sus necesidades.\n"
        elif intencion == 'RASTREAR_PEDIDO':
            prompt += "\n\n🎯 INSTRUCCIÓN: Informa el estado del pedido de forma clara. Si está en camino, da fecha estimada. Si hay problema, ofrece solución.\n"
        elif intencion == 'CONSULTA_ENVIO':
            prompt += "\n\n🎯 INSTRUCCIÓN: Explica el costo y tiempo de envío. Menciona envío gratis sobre $50. Ofrece agregar al carrito.\n"
        elif intencion == 'APLICAR_CUPON':
            prompt += "\n\n🎯 INSTRUCCIÓN: Si el cupón es válido, celebra el ahorro. Si no, explica por qué y sugiere alternativas.\n"

        # Reglas finales
        prompt += """

❌ PROHIBIDO:
- Inventar productos que no están en el catálogo
- Dar precios incorrectos
- Prometer lo que no podemos cumplir
- Respuestas genéricas tipo "tenemos varios productos"
- Ser repetitivo o aburrido

✅ SIEMPRE:
- Menciona productos ESPECÍFICOS con nombre y precio
- Termina con pregunta o call-to-action
- Sé útil, no solo amable
- Si no sabes algo, admítelo y ofrece alternativa
"""

        return prompt

    def _extraer_query_busqueda(self, mensaje: str) -> str:
        """Extrae el término de búsqueda del mensaje"""
        import re

        # Remover palabras comunes
        palabras_ignorar = ['busco', 'quiero', 'necesito', 'tienen', 'venden', 'hay', 'dame', 'muestra', 'ver']

        mensaje_lower = mensaje.lower()
        for palabra in palabras_ignorar:
            mensaje_lower = mensaje_lower.replace(palabra, '')

        # Limpiar y retornar
        query = mensaje_lower.strip()
        return query if len(query) > 2 else mensaje

    def _extraer_ciudad(self, mensaje: str) -> str:
        """Extrae el nombre de la ciudad del mensaje"""
        import re

        # Ciudades principales de Ecuador
        ciudades = [
            'quito', 'guayaquil', 'cuenca', 'ambato', 'manta',
            'portoviejo', 'machala', 'loja', 'esmeraldas', 'ibarra',
            'riobamba', 'santo domingo', 'durán', 'quevedo'
        ]

        mensaje_lower = mensaje.lower()
        for ciudad in ciudades:
            if ciudad in mensaje_lower:
                return ciudad.capitalize()

        return 'Quito'  # Default

    def _extraer_codigo_cupon(self, mensaje: str) -> Optional[str]:
        """Extrae el código de cupón del mensaje"""
        import re

        # Buscar patrones de código (ej: DESC10, PROMO2024, etc.)
        patron = r'\b[A-Z0-9]{4,12}\b'
        matches = re.findall(patron, mensaje.upper())

        if matches:
            return matches[0]

        return None
```

---

## 🔄 Opción 2: Script Automático

Voy a crear un script que hace el cambio automáticamente.

**PRÓXIMO MENSAJE**: Te daré el script completo para aplicar el cambio.

---

## ✅ Verificación Post-Cambio

Después de aplicar el cambio:

1. **Test de sintaxis:**
   ```bash
   python -c "from app.services import ai_service; print('✅ OK')"
   ```

2. **Test de import de chatbot_tools:**
   ```bash
   python -c "from app.services.chatbot_tools import ejecutar_funcion; print('✅ OK')"
   ```

3. **Test del chatbot:**
   ```bash
   python3 test_chatbot_deepseek.py
   ```

4. **Iniciar servidor:**
   ```bash
   cd flask-app && python run.py
   ```

5. **Probar en navegador:**
   - Abrir http://localhost:5000
   - Abrir consola (F12)
   - Click en chatbot
   - Click en 🗑️ (limpiar historial)
   - Probar: "¿Tienen laptops HP?"
   - Probar: "¿Cuánto cuesta envío a Quito?"
   - Probar: "¿Dónde está mi pedido?"

---

## 📊 Resultado Esperado

**ANTES (Chatbot Básico):**
```
Usuario: "¿Tienen laptops?"
Bot: "Sí, tenemos varios productos disponibles. ¿Te interesa alguno?"
```

**DESPUÉS (Chatbot Avanzado):**
```
Usuario: "¿Tienen laptops HP?"
Bot: "¡Claro! Encontré 2 laptops HP disponibles para ti:

1. **Laptop HP i7 16GB** - $1,200 💻
   • Ideal para trabajo pesado y gaming
   • Stock: 10 unidades disponibles
   • Rating: 4.8⭐ (24 reviews)

2. **Laptop HP i5 8GB** - $899 💻
   • Perfecta para uso diario y oficina
   • Stock: 5 unidades
   • Rating: 4.5⭐ (18 reviews)

¿Cuál te interesa más o necesitas ayuda para decidir? 😊"
```

---

## 🎯 Próximos Pasos

1. ✅ Aplicar el cambio al ai_service.py
2. ⏳ Testing completo
3. ⏳ Commit y push
4. ⏳ Documentación final

**Estado actual**: Listo para aplicar cambio
**Fecha**: 2025-11-20
