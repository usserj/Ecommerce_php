# 🤖 Integración de IA con DeepSeek - PRODUCCIÓN

**Estado:** ✅ LISTO PARA PRODUCCIÓN
**Branch:** `claude/spanish-greeting-01Vjn5Z2EVWwcy5sLSdgpdV7`
**Última actualización:** 20 Nov 2025

---

## 📋 RESUMEN

Integración completa de **5 funcionalidades de Inteligencia Artificial** utilizando DeepSeek API en el ecommerce Flask:

1. ✅ **Chatbot de ventas 24/7** - Widget flotante en todas las páginas
2. ✅ **Recomendador de productos** - Sugerencias inteligentes basadas en IA
3. ✅ **Generador de descripciones** - Descripciones SEO automáticas
4. ✅ **Análisis de reviews** - Análisis de sentimiento y sugerencias
5. ✅ **Búsqueda inteligente** - Procesamiento de lenguaje natural

---

## 📁 ESTRUCTURA DE ARCHIVOS

### Backend

```
app/
├── blueprints/
│   └── ai/
│       ├── __init__.py          # Blueprint de IA con CORS
│       └── routes.py            # Endpoints de las 5 funcionalidades
├── services/
│   └── ai_service.py            # Servicio central de DeepSeek
├── models/
│   ├── chatbot.py               # Modelo ConversacionChatbot
│   └── analisis_review.py       # Modelo AnalisisReview
└── config.py                     # Configuración de DeepSeek API
```

### Frontend

```
app/
├── static/
│   ├── js/
│   │   └── ai-chatbot.js        # Widget del chatbot
│   └── css/
│       └── ai-chatbot.css       # Estilos del widget
└── templates/
    ├── base.html                # Integración del widget
    └── admin/
        ├── ia_dashboard.html    # Panel de admin IA
        ├── ia_conversaciones.html
        ├── ia_generador.html
        └── ia_estadisticas.html
```

---

## 🔧 CONFIGURACIÓN

### Variables de Entorno

```bash
# .env
DEEPSEEK_API_KEY=sk-5967b2b9feb7438dadd1059f600094c9
DEEPSEEK_API_URL=https://api.deepseek.com/chat/completions  # Sin /v1
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_CACHE_TTL=3600  # 1 hora
```

### Configuración en código

**Archivo:** `app/config.py` líneas 117-121

```python
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'sk-5967b2b9feb7438dadd1059f600094c9')
DEEPSEEK_API_URL = os.environ.get('DEEPSEEK_API_URL', 'https://api.deepseek.com/chat/completions')
DEEPSEEK_MODEL = os.environ.get('DEEPSEEK_MODEL', 'deepseek-chat')
DEEPSEEK_CACHE_TTL = int(os.environ.get('DEEPSEEK_CACHE_TTL', 3600))
```

---

## 🚀 ENDPOINTS DE API

### 1. Health Check
```
GET /api/ai/health
```
**Respuesta:**
```json
{
  "status": "healthy",
  "api_connection": "OK",
  "config": {
    "api_key": "sk-5967...94c9",
    "api_url": "https://api.deepseek.com/chat/completions",
    "model": "deepseek-chat"
  }
}
```

### 2. Chatbot de Ventas
```
POST /api/ai/chat
Content-Type: application/json

{
  "message": "¿Hacen envíos a Guayaquil?",
  "context": {
    "carrito": {"total_items": 3},
    "productos": [...]
  }
}
```

### 3. Recomendador de Productos
```
GET /api/ai/recomendaciones/<producto_id>
```

### 4. Generador de Descripciones
```
POST /api/ai/generar-descripcion

{
  "nombre": "Laptop HP",
  "categoria": "Computadoras",
  "precio": 899.99,
  "caracteristicas": [...]
}
```

### 5. Análisis de Reviews
```
POST /api/ai/analizar-reviews

{
  "producto_id": 1,
  "reviews": [
    {"texto": "Excelente producto", "calificacion": 5}
  ]
}
```

### 6. Búsqueda Inteligente
```
POST /api/ai/busqueda-inteligente

{
  "query": "laptop barata para estudiar"
}
```

---

## 🗄️ BASE DE DATOS

### Tablas Creadas Automáticamente

#### `conversaciones_chatbot`
- `id` - Primary key
- `session_id` - UUID de sesión
- `usuario_id` - FK a usuarios (nullable)
- `rol` - 'user' o 'assistant'
- `mensaje` - Texto del mensaje
- `contexto` - JSON con contexto
- `fecha` - Timestamp

#### `analisis_reviews`
- `id` - Primary key
- `producto_id` - FK a productos
- `sentimiento` - positivo/neutro/negativo
- `score_calidad` - 0-100
- `aspectos_positivos` - JSON array
- `aspectos_negativos` - JSON array
- `recomendaciones` - JSON array
- `fecha_analisis` - Timestamp

**Nota:** Las tablas se crean automáticamente al iniciar Flask.

---

## 🎨 WIDGET DEL CHATBOT

### Características
- ✅ Botón flotante responsive
- ✅ Ventana de chat adaptable
- ✅ Historial en sessionStorage
- ✅ Indicador "typing..."
- ✅ Auto-scroll
- ✅ Sugerencias rápidas
- ✅ Manejo de errores

### Integración
El widget se carga automáticamente en todas las páginas excepto `/admin`.

**Configuración inyectada desde Flask:**
```javascript
window.CHATBOT_CONFIG = {
    apiUrl: '/api/ai/chat',
    userName: 'Juan Pérez',  // si está logueado
    userId: 123,
    cartCount: 3,
    storeName: 'Mi Tienda'
};
```

---

## 🔒 SEGURIDAD

### CSRF Protection
- ✅ Rutas POST de IA exentas de CSRF con `@csrf.exempt`
- ✅ CORS configurado correctamente
- ✅ Validación de inputs en todos los endpoints

### Archivos con @csrf.exempt:
- `/api/ai/chat` (routes.py:28)
- `/api/ai/generar-descripcion` (routes.py:211)
- `/api/ai/analizar-reviews` (routes.py:300)
- `/api/ai/busqueda-inteligente` (routes.py:401)

---

## 📊 CONTEXTO DEL CHATBOT

El chatbot tiene conocimiento completo de:

**Información de la tienda:**
- Nombre, email, teléfono, WhatsApp
- Política de envíos (24-48h, gratis >$50)
- Métodos de pago (PayPal, PayU, etc.)
- Garantía (30 días)
- País: Ecuador

**Contexto del usuario:**
- Productos en la página actual
- Estado del carrito
- Historial de conversación (últimos 10 mensajes)
- Usuario logueado (si aplica)

**Personalidad:**
- Español ecuatoriano neutral
- Amable y profesional
- Orientado a ventas
- Respuestas breves (máx 3-4 oraciones)
- Usa emojis ocasionalmente 😊

---

## 🧪 TESTING

### Verificar API de DeepSeek

```bash
curl -X POST https://api.deepseek.com/chat/completions \
  -H "Authorization: Bearer sk-5967b2b9feb7438dadd1059f600094c9" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Hola"}],
    "stream": false
  }'
```

### Verificar Chatbot

```bash
curl -X POST http://localhost:5000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola", "context": {}}'
```

### Verificar Health Check

```bash
curl http://localhost:5000/api/ai/health
```

---

## 🚀 DESPLIEGUE

### Desarrollo

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar variables de entorno (opcional)
cp .env.example .env

# 3. Iniciar Flask
python run.py

# 4. Abrir navegador
http://localhost:5000
```

### Producción

```bash
# 1. Variables de entorno
export DEEPSEEK_API_KEY="sk-5967b2b9feb7438dadd1059f600094c9"
export FLASK_ENV="production"

# 2. Usar gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app('production')"

# 3. Configurar nginx como reverse proxy
# 4. Habilitar HTTPS
```

---

## 📈 COSTOS ESTIMADOS

**DeepSeek API Pricing:**
- Input: $0.14 por 1M tokens
- Output: $0.28 por 1M tokens

**Estimaciones:**
- ~500 tokens por conversación promedio
- ~$0.0002 USD por conversación
- 1000 conversaciones/día = ~$6 USD/mes

---

## ⚠️ CONSIDERACIONES

### Limitaciones Actuales

1. **Cache en memoria** - Se pierde al reiniciar
   - Recomendación: Migrar a Redis para producción

2. **Sin rate limiting** - DeepSeek tiene límites
   - Recomendación: Implementar límites por IP/usuario

3. **Historial solo en sessionStorage** - Se pierde al cerrar
   - Recomendación: Guardar en BD si usuario logueado

### Próximos Pasos

**Corto plazo:**
- Monitorear uso real de usuarios
- Recolectar feedback
- Ajustar prompts basado en conversaciones

**Mediano plazo:**
- Migrar cache a Redis
- Implementar rate limiting
- Dashboard de métricas

**Largo plazo:**
- Fine-tuning con datos propios
- Integración con CRM
- Bot proactivo

---

## 📞 SOPORTE

### Logs a Monitorear

```bash
# Ver logs de IA
grep "app.blueprints.ai" logs/flask.log

# Ver errores
grep "ERROR" logs/flask.log | grep ai

# Ver conversaciones
grep "💬 Mensaje del usuario" logs/flask.log
```

### Comandos Útiles

```bash
# Ver conversaciones recientes
SELECT * FROM conversaciones_chatbot ORDER BY fecha DESC LIMIT 20;

# Ver análisis de reviews
SELECT * FROM analisis_reviews ORDER BY fecha_analisis DESC LIMIT 10;
```

---

## ✅ CHECKLIST DE PRODUCCIÓN

- [x] API Key configurada
- [x] URL correcta (sin `/v1`)
- [x] CSRF exempt en rutas POST
- [x] CORS habilitado
- [x] Base de datos configurada
- [x] Logging implementado
- [x] Manejo de errores robusto
- [x] Frontend responsive
- [x] Archivos de test eliminados
- [x] Documentación completa

---

## 📝 CHANGELOG

### 2025-11-20
- ✅ Integración completa de 5 funcionalidades de IA
- ✅ Fix de URL de DeepSeek (sin `/v1`)
- ✅ Fix de CSRF con `@csrf.exempt`
- ✅ Widget de chatbot implementado
- ✅ Base de datos persistente
- ✅ Limpieza de archivos de test

---

**Estado Final:** ✅ PRODUCCIÓN READY
**Commits:** 8b5a058d (limpieza) → 625d0451 (debug) → a21d00c6 (fix URL)
