# 🤖 Sistema de Chatbot Avanzado con IA

## 📋 Arquitectura del Sistema

### Flujo de Procesamiento

```
Usuario → Mensaje
    ↓
1. DETECCIÓN DE INTENCIÓN
    - ¿Busca productos?
    - ¿Rastrea pedido?
    - ¿Tiene reclamo?
    - ¿Pregunta sobre envío/pago?
    - ¿Necesita soporte?
    ↓
2. ENRIQUECIMIENTO DE CONTEXTO
    - Historial del usuario
    - Productos vistos
    - Carrito actual
    - Compras previas
    ↓
3. EJECUCIÓN DE FUNCIONES
    - buscar_productos()
    - rastrear_pedido()
    - calcular_envio()
    - validar_cupon()
    - detectar_fraude()
    - etc...
    ↓
4. GENERACIÓN DE RESPUESTA (DeepSeek API)
    - System prompt inteligente
    - Resultados de funciones
    - Contexto enriquecido
    - Historial de conversación
    ↓
5. POST-PROCESAMIENTO
    - Guardar conversación
    - Analytics
    - Seguimiento de métricas
    ↓
Usuario ← Respuesta Inteligente
```

---

## 🎯 Capacidades del Chatbot

### 1. VENDER - Recomendaciones y Guía de Compra

**Funciones disponibles:**
- `buscar_productos(query, categoria, precio_max, precio_min)`
- `obtener_recomendaciones_personalizadas(usuario_id, producto_actual)`
- `comparar_productos(producto_ids)`

**Escenarios cubiertos:**
- ✅ "¿Tienen laptops HP?" → Busca y muestra productos específicos
- ✅ "Quiero algo para gaming" → Recomienda productos relevantes
- ✅ "Compara estos 3 productos" → Comparación detallada
- ✅ "¿Qué me recomiendas?" → Recomendaciones personalizadas basadas en historial

---

### 2. SOPORTAR - Preguntas, Reclamos, Tracking

**Funciones disponibles:**
- `rastrear_pedido(order_id, usuario_id, email)`
- `obtener_historial_compras(usuario_id)`
- `procesar_reclamo(usuario_id, order_id, motivo, descripcion)`

**Escenarios cubiertos:**
- ✅ "¿Dónde está mi pedido?" → Rastrea automáticamente
- ✅ "Mi pedido #123 no llegó" → Consulta estado y da solución
- ✅ "Quiero devolver un producto" → Registra reclamo y explica proceso
- ✅ "El producto llegó defectuoso" → Genera ticket de reclamo

---

### 3. COBRAR - Ayuda en Checkout

**Funciones disponibles:**
- `calcular_costo_envio(ciudad, provincia, peso_kg)`
- `validar_aplicar_cupon(codigo_cupon, total_compra)`
- `obtener_metodos_pago_disponibles(total)`
- `validar_datos_compra(nombre, email, telefono, direccion)`

**Escenarios cubiertos:**
- ✅ "¿Cuánto cuesta el envío a Quito?" → Calcula en tiempo real
- ✅ "Tengo un cupón DESC20" → Valida y aplica
- ✅ "¿Aceptan contra entrega?" → Muestra métodos disponibles
- ✅ "¿Puedo pagar con tarjeta?" → Explica opciones de pago locales

---

### 4. RETENER - Automatización y Campañas

**Funciones disponibles:**
- Análisis de comportamiento del usuario
- Detección de abandono de carrito
- Sugerencias proactivas

**Escenarios cubiertos:**
- ✅ Detecta carrito abandonado → "Vi que dejaste algo en el carrito, ¿te ayudo a finalizar?"
- ✅ Usuario inactivo → Ofrece descuentos personalizados
- ✅ Compra reciente → Follow-up y productos complementarios

---

### 5. ANALIZAR - Insights y BI

**Funciones disponibles:**
- `obtener_estadisticas_producto(producto_id)`
- Analytics de conversaciones
- Forecast de demanda

**Escenarios cubiertos:**
- ✅ "¿Qué opinan de este producto?" → Muestra análisis de reviews
- ✅ "¿Es buena calidad?" → Ratings, sentimiento, aspectos positivos/negativos
- ✅ Detección de productos problemáticos → Alerta a admin

---

### 6. OPTIMIZAR - Automatización Interna

**Funciones disponibles:**
- Detección de productos sin stock
- Identificación de preguntas frecuentes
- Sugerencias de mejora de catálogo

**Escenarios cubiertos:**
- ✅ Usuario pregunta por producto sin stock → Notifica a admin, sugiere alternativas
- ✅ Preguntas repetitivas → Genera FAQ automático
- ✅ Detecta confusión en descripciones → Alerta para mejorar

---

### 7. PROTEGER - Fraude y Validación

**Funciones disponibles:**
- `detectar_comportamiento_sospechoso(usuario_id, email, total_compra)`
- `validar_datos_compra(nombre, email, telefono, direccion)`

**Escenarios cubiertos:**
- ✅ Usuario nuevo con compra alta → Marca para verificación
- ✅ Múltiples pagos rechazados → Alerta de fraude
- ✅ Datos inconsistentes → Solicita validación adicional
- ✅ Dirección sospechosa → Requiere confirmación

---

## 🧠 Detección de Intención

El sistema clasifica automáticamente la intención del usuario en:

### Intenciones Principales:

1. **BUSCAR_PRODUCTO**
   - Palabras clave: "busco", "quiero", "necesito", "tienen", "venden"
   - Acción: Ejecuta `buscar_productos()`

2. **RASTREAR_PEDIDO**
   - Palabras clave: "pedido", "orden", "envío", "tracking", "dónde está"
   - Acción: Ejecuta `rastrear_pedido()`

3. **RECLAMO**
   - Palabras clave: "reclamo", "devolver", "defectuoso", "problema", "no llegó"
   - Acción: Ejecuta `procesar_reclamo()`

4. **CONSULTA_ENVIO**
   - Palabras clave: "envío", "shipping", "cuánto cuesta enviar", "cuánto demora"
   - Acción: Ejecuta `calcular_costo_envio()`

5. **CONSULTA_PAGO**
   - Palabras clave: "pago", "tarjeta", "efectivo", "paypal", "transferencia"
   - Acción: Ejecuta `obtener_metodos_pago_disponibles()`

6. **APLICAR_CUPON**
   - Palabras clave: "cupón", "descuento", "código", "promoción"
   - Acción: Ejecuta `validar_aplicar_cupon()`

7. **RECOMENDACION**
   - Palabras clave: "recomienda", "sugiere", "qué comprar", "ayuda a elegir"
   - Acción: Ejecuta `obtener_recomendaciones_personalizadas()`

8. **COMPARACION**
   - Palabras clave: "comparar", "diferencia", "cuál es mejor", "vs"
   - Acción: Ejecuta `comparar_productos()`

9. **INFO_PRODUCTO**
   - Palabras clave: "opiniones", "reviews", "calidad", "garantía", "especificaciones"
   - Acción: Ejecuta `obtener_estadisticas_producto()`

10. **CONVERSACION_GENERAL**
    - Saludos, agradecimientos, despedidas
    - Acción: Respuesta directa sin funciones

---

## 💾 Contexto Enriquecido

El chatbot tiene acceso a:

### Datos del Usuario:
```python
{
    'usuario_id': 123,
    'nombre': 'Juan Pérez',
    'email': 'juan@example.com',
    'fecha_registro': '2024-01-15',
    'compras_totales': 5,
    'gasto_total': 450.00,
    'ultima_compra': '2024-11-10',
    'productos_vistos_recientemente': [1, 5, 8]
}
```

### Carrito Actual:
```python
{
    'total_items': 3,
    'total_valor': 125.50,
    'productos': [
        {'id': 1, 'nombre': 'Laptop HP', 'cantidad': 1, 'precio': 899.00},
        {'id': 5, 'nombre': 'Mouse', 'cantidad': 2, 'precio': 25.00}
    ]
}
```

### Historial de Conversación:
```python
[
    {'rol': 'user', 'mensaje': '¿Tienen laptops?', 'timestamp': '2024-11-20 10:30'},
    {'rol': 'assistant', 'mensaje': 'Sí, tenemos...', 'timestamp': '2024-11-20 10:30'},
]
```

### Productos Disponibles:
```python
[
    {'id': 1, 'nombre': 'Laptop HP i7', 'precio': 1200, 'categoria': 'Tecnología', 'stock': 10},
    {'id': 2, 'nombre': 'Mouse Logitech', 'precio': 25, 'categoria': 'Accesorios', 'stock': 50},
    # ...
]
```

---

## 🔄 Flujo de Function Calling

### Ejemplo: Búsqueda de Producto

```
Usuario: "¿Tienen laptops HP?"
    ↓
[DETECCIÓN] Intención: BUSCAR_PRODUCTO
    ↓
[EXTRACCIÓN] Parámetros:
    - query: "laptop HP"
    - categoria: null
    - precio_max: null
    ↓
[EJECUCIÓN] buscar_productos(query="laptop HP")
    ↓
[RESULTADO]
{
    'productos': [
        {'id': 1, 'nombre': 'Laptop HP i7 16GB', 'precio': 1200, 'stock': 10},
        {'id': 2, 'nombre': 'Laptop HP i5 8GB', 'precio': 899, 'stock': 5}
    ]
}
    ↓
[ENRIQUECIMIENTO] System prompt + resultados
    ↓
[DEEPSEEK API] Genera respuesta natural
    ↓
[RESPUESTA]
"¡Claro! Tenemos 2 laptops HP disponibles:

1. **Laptop HP i7 16GB** por $1,200 - Excelente para trabajo pesado y gaming 💻
2. **Laptop HP i5 8GB** por $899 - Perfecta para uso diario y oficina 👍

Ambas tienen stock disponible. ¿Te interesa alguna en particular o necesitas más detalles?"
```

---

## 📊 Analytics y Métricas

El sistema registra automáticamente:

### Métricas de Conversación:
- Número de mensajes por sesión
- Tiempo de conversación
- Productos mencionados
- Funciones ejecutadas
- Intenciones detectadas

### Métricas de Conversión:
- Conversaciones que llevan a compra
- Productos agregados al carrito desde chat
- Cupones aplicados desde chat
- Tasa de abandono post-chat

### Insights de Negocio:
- Productos más consultados
- Preguntas frecuentes
- Puntos de fricción (reclamos, confusiones)
- Oportunidades de mejora

---

## 🛡️ Seguridad y Validación

### Validaciones Automáticas:

1. **Validación de Entrada:**
   - Sanitización de mensajes
   - Detección de spam
   - Rate limiting

2. **Validación de Datos:**
   - Emails válidos
   - Teléfonos ecuatorianos
   - Direcciones completas

3. **Detección de Fraude:**
   - Comportamiento sospechoso
   - Múltiples cuentas
   - Patrones anormales

4. **Protección de Datos:**
   - No almacena datos sensibles (tarjetas, contraseñas)
   - GDPR compliant
   - Logs auditables

---

## 🚀 Ventajas del Sistema

### vs Chatbot Básico:

| Característica | Básico | Avanzado |
|----------------|--------|----------|
| Respuestas genéricas | ❌ | ✅ Específicas con datos reales |
| Acciones | ❌ | ✅ 12+ funciones ejecutables |
| Tracking de pedidos | ❌ | ✅ Automático |
| Aplicar cupones | ❌ | ✅ Validación en tiempo real |
| Calcular envíos | ❌ | ✅ Tarifas actualizadas |
| Detectar fraude | ❌ | ✅ Scoring de riesgo |
| Recomendaciones personalizadas | ❌ | ✅ Basadas en historial |
| Análisis de sentimiento | ❌ | ✅ Reviews y ratings |
| Soporte de reclamos | ❌ | ✅ Registro y seguimiento |
| Analytics | ❌ | ✅ Métricas completas |

---

## 📝 Ejemplo Completo de Interacción

### Escenario: Usuario busca producto, pregunta por envío y aplica cupón

```
Usuario: "Hola, busco una laptop para trabajar"

Bot: "¡Hola! 👋 Te puedo recomendar:

1. **Laptop HP i7 16GB** - $1,200
   • Ideal para trabajo pesado, multitarea y edición
   • En stock: 10 unidades

2. **Laptop HP i5 8GB** - $899
   • Perfecta para uso diario, oficina y navegación
   • En stock: 5 unidades

¿Cuál te interesa más?"

Usuario: "La HP i5. ¿Cuánto cuesta el envío a Quito?"

[FUNCIÓN EJECUTADA: calcular_costo_envio(ciudad="Quito")]

Bot: "La Laptop HP i5 por $899 es excelente elección! 👍

📦 **Envío a Quito:**
• Costo: $3.50
• Tiempo: 1-2 días hábiles
• ¡Envío GRATIS en compras sobre $50! ✅

Tu total sería: $902.50

¿Tienes algún cupón de descuento? 🎁"

Usuario: "Sí, tengo el código DESC10"

[FUNCIÓN EJECUTADA: validar_aplicar_cupon(codigo="DESC10", total=902.50)]

Bot: "¡Perfecto! ✨

✅ Cupón **DESC10** aplicado
💰 Descuento: -$90.25 (10%)
📦 Envío: $3.50

**Total con descuento: $812.25**
**¡Ahorras $90.25!** 🎉

¿Listo para finalizar la compra? Puedes pagar con:
• Tarjeta (Visa, Mastercard) 💳
• PayPal
• Transferencia bancaria
• Contra entrega"

Usuario: "Perfecto, voy a pagar"

Bot: "¡Excelente! 😊 Te dirijo al checkout para completar tu compra.

Recuerda:
✅ Laptop HP i5 8GB - $899
✅ Cupón DESC10 aplicado
✅ Envío express a Quito
📅 Llegaría en 1-2 días

¡Gracias por tu compra! Si necesitas algo más, estoy aquí. 🛒"
```

---

## 🔧 Configuración y Uso

### 1. Activar el Sistema:

El sistema está activo automáticamente. No requiere configuración adicional.

### 2. Probar Funcionalidades:

```bash
# Ejecutar script de prueba
python3 test_chatbot_deepseek.py
```

### 3. Monitorear Logs:

```bash
# Ver logs del chatbot
tail -f flask-app/logs/chatbot.log
```

### 4. Analytics:

Los analytics se registran automáticamente en:
- Tabla `conversaciones_chatbot` - Historial completo
- Logs del servidor - Métricas en tiempo real

---

## 📞 Soporte

Si necesitas ajustar el comportamiento del chatbot:

1. **System Prompt**: Edita en `ai_service.py` línea 306+
2. **Funciones**: Agrega nuevas en `chatbot_tools.py`
3. **Detección de Intención**: Modifica en `ai_service.py` método `_detectar_intencion()`

---

**Sistema desarrollado con Claude AI (Sonnet 4.5)**
**Fecha: 2025-11-20**
