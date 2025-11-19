# 🤖 Instalación de Funcionalidades de IA con DeepSeek

Este documento contiene las instrucciones para instalar y configurar las 5 funcionalidades de IA integradas en el sistema de e-commerce.

---

## 📋 Funcionalidades Implementadas

1. **✅ Chatbot de Ventas 24/7** - Widget flotante en todas las páginas de tienda
2. **✅ Recomendador de Productos** - Sugerencias inteligentes en página de producto
3. **✅ Generador de Descripciones** - IA para crear descripciones profesionales
4. **✅ Análisis de Reviews** - Sentimientos y insights de comentarios
5. **✅ Búsqueda Inteligente** - Entiende lenguaje natural

---

## 🚀 Instalación

### Paso 1: Crear las Tablas de Base de Datos

Ejecutar el script de migración para crear las tablas necesarias:

```bash
cd /home/user/Ecommerce_php/flask-app
python create_ai_tables.py
```

Este script creará dos nuevas tablas:
- `conversaciones_chatbot` - Para almacenar historial del chatbot
- `analisis_reviews` - Para guardar análisis de sentimientos

**Nota:** Asegúrate de que MySQL esté corriendo antes de ejecutar el script.

### Paso 2: Verificar la Instalación

Verifica que los archivos se hayan creado correctamente:

```bash
# Verificar modelos
ls -l app/models/chatbot.py
ls -l app/models/analisis_review.py

# Verificar servicio
ls -l app/services/ai_service.py

# Verificar blueprint
ls -l app/blueprints/ai/

# Verificar frontend
ls -l app/static/js/ai-chatbot.js
ls -l app/static/css/ai-chatbot.css
```

### Paso 3: Reiniciar el Servidor Flask

```bash
python run.py
```

---

## 🧪 Probar las Funcionalidades

### 1. Chatbot de Ventas

1. Abre cualquier página de la tienda (NO admin): http://localhost:5000
2. Verifica que aparezca el botón flotante "¿Dudas?" en la esquina inferior derecha
3. Haz clic para abrir el chat
4. Envía un mensaje de prueba: "¿Tienen envío gratis?"
5. El chatbot debe responder en 2-5 segundos

**Si no aparece:**
- Abre la consola del navegador (F12) y busca errores
- Verifica que NO estés en una ruta `/admin/*`
- Verifica que los archivos JS y CSS se carguen correctamente

### 2. Recomendaciones de Productos

**Nota:** Esta funcionalidad requiere modificar los templates de productos manualmente.
Ver sección "Configuración Adicional" más abajo.

### 3. Generador de Descripciones

**Nota:** Esta funcionalidad requiere agregar UI en el panel admin.
Ver sección "Configuración Adicional" más abajo.

### 4. Análisis de Reviews

**Nota:** Esta funcionalidad requiere crear nuevas páginas en el admin.
Ver sección "Configuración Adicional" más abajo.

### 5. Búsqueda Inteligente

Esta funcionalidad puede integrarse modificando el endpoint `/buscar` existente.

---

## ⚙️ Configuración API DeepSeek

La API key de DeepSeek está **configurada directamente en el backend** en el archivo:

```
app/services/ai_service.py
```

**API Key configurada:**
```python
self.api_key = "sk-5967b2b9feb7438dadd1059f600094c9"
```

### Límites y Costos

- DeepSeek cobra por tokens consumidos
- El sistema implementa cache para reducir llamadas
- Se registra el uso de tokens en los logs

### Monitoreo de Uso

Ver logs de la aplicación para monitorear tokens consumidos:

```bash
tail -f logs/app.log | grep "Tokens usados"
```

---

## 🛠️ Configuración Adicional

### Agregar Recomendaciones en Página de Producto

Editar: `app/templates/shop/product_detail.html`

Agregar después de la descripción del producto:

```html
<!-- Recomendaciones de IA -->
<section class="mt-5">
    <h4><i class="fas fa-lightbulb text-warning"></i> Te podría interesar</h4>
    <div id="loading-recomendaciones" class="text-center my-4">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Cargando...</span>
        </div>
        <p>Buscando productos perfectos para ti...</p>
    </div>
    <div id="productos-recomendados" class="row"></div>
</section>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const productoId = {{ producto.id }};
    const container = document.getElementById('productos-recomendados');
    const loading = document.getElementById('loading-recomendaciones');

    // Llamar a API de recomendaciones
    fetch(`/api/ai/recomendaciones/${productoId}`)
        .then(response => response.json())
        .then(data => {
            loading.style.display = 'none';

            if (data.success && data.recomendaciones.length > 0) {
                let html = '';

                data.recomendaciones.forEach(producto => {
                    html += `
                        <div class="col-md-3 mb-3">
                            <div class="card h-100 hover-shadow">
                                <img src="${producto.imagen}" class="card-img-top" alt="${producto.nombre}">
                                <div class="card-body">
                                    <h6 class="card-title">${producto.nombre}</h6>
                                    <p class="text-primary fw-bold">$${producto.precio.toFixed(2)}</p>
                                    <small class="text-muted">${producto.razon}</small>
                                    <a href="/producto/${producto.ruta}" class="btn btn-sm btn-primary w-100 mt-2">
                                        Ver Producto
                                    </a>
                                </div>
                                <div class="card-footer">
                                    <small class="badge bg-secondary">
                                        ${producto.tipo === 'complementario' ? '📦 Complementario' :
                                          producto.tipo === 'similar' ? '⭐ Similar' : '🔥 Popular'}
                                    </small>
                                </div>
                            </div>
                        </div>
                    `;
                });

                container.innerHTML = html;
            } else {
                container.innerHTML = '<p class="text-muted">No hay recomendaciones disponibles.</p>';
            }
        })
        .catch(error => {
            console.error('Error al cargar recomendaciones:', error);
            loading.style.display = 'none';
            container.innerHTML = '<p class="text-danger">Error al cargar recomendaciones.</p>';
        });
});
</script>
```

---

## 📊 Estructura de Archivos Creados

```
flask-app/
├── app/
│   ├── blueprints/
│   │   └── ai/                          # ⭐ NUEVO Blueprint de IA
│   │       ├── __init__.py
│   │       └── routes.py                # API endpoints
│   │
│   ├── models/
│   │   ├── chatbot.py                   # ⭐ NUEVO Modelo chatbot
│   │   └── analisis_review.py           # ⭐ NUEVO Modelo análisis
│   │
│   ├── services/
│   │   └── ai_service.py                # ⭐ NUEVO Servicio IA completo
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── ai-chatbot.css           # ⭐ NUEVO Estilos chatbot
│   │   └── js/
│   │       └── ai-chatbot.js            # ⭐ NUEVO Lógica chatbot
│   │
│   └── templates/
│       └── base.html                    # MODIFICADO (chatbot integrado)
│
├── create_ai_tables.py                  # ⭐ NUEVO Script migración
└── INSTALACION_IA.md                    # ⭐ NUEVO Este archivo
```

---

## 🐛 Troubleshooting

### Problema: Chatbot no aparece

**Soluciones:**
1. Verifica que NO estés en una ruta `/admin/*`
2. Abre consola del navegador (F12) y busca errores
3. Verifica que los archivos JS/CSS se carguen:
   - http://localhost:5000/static/js/ai-chatbot.js
   - http://localhost:5000/static/css/ai-chatbot.css
4. Verifica que `window.CHATBOT_CONFIG` esté definido en la consola

### Problema: Error "API Error 401"

**Causa:** API key inválida o expirada

**Solución:**
1. Verificar API key en `app/services/ai_service.py`
2. Contactar con DeepSeek para renovar key si es necesario

### Problema: Chatbot responde muy lento

**Causas posibles:**
- API de DeepSeek lenta (2-5 segundos es normal)
- Conexión a internet lenta
- Límite de rate de la API alcanzado

**Solución:**
- Esperar unos segundos
- Revisar logs para ver tiempos de respuesta

### Problema: Error "Table doesn't exist"

**Causa:** Tablas de IA no creadas en la base de datos

**Solución:**
```bash
python create_ai_tables.py
```

### Problema: Recomendaciones no cargan

**Soluciones:**
1. Verifica que hay productos activos en la base de datos
2. Abre consola del navegador y verifica el error
3. Verifica que el endpoint `/api/ai/recomendaciones/123` responde correctamente

---

## 📈 Monitoreo y Logs

### Ver conversaciones del chatbot

```sql
SELECT * FROM conversaciones_chatbot
ORDER BY fecha DESC
LIMIT 50;
```

### Ver análisis de reviews

```sql
SELECT * FROM analisis_reviews
ORDER BY fecha_analisis DESC;
```

### Ver logs de la aplicación

```bash
tail -f logs/app.log | grep "DeepSeek"
```

---

## 🔐 Seguridad

### API Key

- **NUNCA** commitear la API key en repositorios públicos
- La key actual está en el backend, no en variables de entorno
- Para producción, considerar mover a variable de entorno

### Datos de Usuarios

- Las conversaciones del chatbot se almacenan en BD
- Implementar política de retención de datos
- El script de limpieza automática se ejecuta con:

```python
from app.models.chatbot import ConversacionChatbot
ConversacionChatbot.limpiar_antiguas(dias=30)
```

---

## 📞 Soporte

Si tienes problemas con la instalación:

1. Verifica que todos los archivos existan
2. Revisa los logs de la aplicación
3. Verifica la consola del navegador para errores frontend
4. Asegúrate de que MySQL esté corriendo

---

## ✅ Checklist de Instalación Completa

- [x] Modelos de IA creados (`chatbot.py`, `analisis_review.py`)
- [x] Servicio de IA implementado (`ai_service.py`)
- [x] Blueprint de IA registrado
- [x] Frontend del chatbot (JS + CSS)
- [x] Templates modificados (`base.html`)
- [ ] Tablas de BD creadas (ejecutar `create_ai_tables.py`)
- [ ] Servidor Flask reiniciado
- [ ] Chatbot probado y funcionando
- [ ] API DeepSeek respondiendo correctamente

---

**¡Todo listo para usar IA en tu e-commerce! 🎉**
