# 📋 PLAN DE MIGRACIÓN - Funcionalidades Pendientes

**Total de funcionalidades pendientes:** 45
**Prioridad:** Alta (23), Media (15), Baja (7)
**Estado actual:** 89% migrado (40/45 completadas)

---

## 🔴 FASE 1: ALTA PRIORIDAD (23 funcionalidades)

### 1. Sistema de Banners (7 funcionalidades) ✅ COMPLETADO
**Impacto:** Alto - Usado en frontend para promociones

**Tareas:**
- [x] Crear modelo Banner en SQLAlchemy
- [x] Migración SQL para tabla banner
- [x] Rutas admin CRUD (/admin/banners)
- [x] Templates admin (listar, crear, editar)
- [x] AJAX para tabla dinámica (DataTables)
- [x] Mostrar banners en frontend por categoría/subcategoría
- [x] Upload de imágenes de banner

**Archivos creados:**
- ✅ `app/models/setting.py` (Banner model)
- ✅ `app/blueprints/admin/routes.py` (rutas agregadas)
- ✅ `app/templates/admin/banners.html`
- ✅ `app/templates/admin/banner_form.html`

---

### 2. CRUD Administradores Completo (6 funcionalidades) ✅ COMPLETADO
**Impacto:** Alto - Gestión de equipo admin

**Tareas:**
- [x] Listar todos los administradores
- [x] Crear nuevo administrador desde admin
- [x] Editar perfil de administrador
- [x] Eliminar administrador
- [x] Activar/Desactivar administrador
- [x] Upload foto de perfil administrador

**Archivos creados:**
- ✅ `app/blueprints/admin/routes.py` (rutas de administradores)
- ✅ `app/templates/admin/administradores.html`
- ✅ `app/templates/admin/admin_form.html`

---

### 3. Personalización de Tienda (8 funcionalidades) ✅ COMPLETADO
**Impacto:** Alto - Branding y personalización

**Tareas:**
- [x] Cambiar logo de la tienda
- [x] Cambiar favicon
- [x] Personalizar colores (fondo, texto, navbar)
- [x] Configurar enlaces redes sociales
- [x] Facebook Pixel integration
- [x] Google Analytics integration
- [x] Scripts personalizados (header/footer)
- [x] Seleccionar plantilla/tema

**Archivos creados:**
- ✅ `app/models/setting.py` (métodos Plantilla)
- ✅ `app/blueprints/admin/routes.py` (ruta personalización)
- ✅ `app/templates/admin/personalizacion.html`

**Commit:** d210e8b

---

### 4. Upload Múltiples Imágenes Productos (1 funcionalidad) ✅ COMPLETADO
**Impacto:** Alto - Galería de imágenes para productos

**Tareas:**
- [x] Actualizar modelo Producto para multimedia JSON
- [x] UI para subir múltiples imágenes
- [x] Galería de imágenes en detalle de producto
- [x] Editar/eliminar imágenes adicionales

**Archivos creados/modificados:**
- ✅ `app/models/product.py` (métodos de galería)
- ✅ `app/blueprints/admin/routes.py` (product_gallery)
- ✅ `app/templates/admin/product_gallery.html`
- ✅ `app/templates/components/product_gallery.html`
- ✅ `app/templates/shop/product_detail.html` (integración galería)

**Commit:** 7f0ded5

---

### 5. UI para Aplicar Cupones en Checkout (1 funcionalidad) ✅ COMPLETO
**Impacto:** Alto - Backend completo, solo falta UI

**Estado:** ✅ YA IMPLEMENTADO en sesiones anteriores
- ✅ Campo de cupón en checkout
- ✅ Validación AJAX
- ✅ Aplicar descuento
- ✅ Mostrar descuento en resumen

---

## 🟡 FASE 2: MEDIA PRIORIDAD (15 funcionalidades)

### 6. Tablas Dinámicas AJAX con DataTables (6 módulos) ✅ COMPLETADO
**Impacto:** Medio - Mejora UX en admin

**Módulos:**
- [x] Productos ✅
- [x] Categorías ✅
- [x] Subcategorías ✅
- [x] Usuarios ✅
- [x] Ventas/Órdenes ✅
- [x] Banners ✅

**Tareas:**
- [x] Integrar DataTables en listados principales
- [x] Endpoints AJAX para paginación server-side
- [x] Búsqueda y filtros en tiempo real
- [x] Ordenamiento por columnas
- [x] Statistics cards en cada módulo
- [x] Event delegation para acciones

**Commits:** 9ef21c5, 505955e, 66151de, d32d02f

**Beneficios:** Rendimiento optimizado para grandes volúmenes de datos, UX mejorada, búsqueda instantánea

---

### 7. Reportes Avanzados (4 funcionalidades) ✅ COMPLETADO
**Impacto:** Medio - Analytics y reportes

**Tareas:**
- [x] Reportes de ventas por rango de fechas
- [x] Filtros avanzados (producto, usuario, método pago)
- [x] Gráficos de ventas (Chart.js)
- [x] Exportar reportes a Excel (openpyxl)

**Archivos creados/modificados:**
- ✅ `app/blueprints/admin/routes.py` (rutas reports, reports_data, export_reports)
- ✅ `app/templates/admin/reports.html` (interfaz completa con Chart.js)

**Funcionalidades:**
- Filtros avanzados: fecha, producto, usuario, método de pago
- Gráfico de línea: Ventas e ingresos por fecha (dual axis)
- Gráfico de barras horizontal: Top 10 productos por ingresos
- Gráfico de dona: Distribución por método de pago
- Tarjetas de estadísticas: Total ventas, ingresos totales, ticket promedio
- Exportación a Excel con estilos (openpyxl)
- Actualización en tiempo real con AJAX
- Chart.js 4.4.0 para visualizaciones interactivas

**Tiempo real:** 2.5 horas

---

### 8. Gestión Usuarios desde Admin (2 funcionalidades) ✅ COMPLETADO
**Tareas:**
- [x] Editar usuario desde admin
- [x] Eliminar usuario desde admin

**Archivos creados/modificados:**
- ✅ `app/blueprints/admin/routes.py` (edit_user, delete_user)
- ✅ `app/templates/admin/user_form.html` (formulario de edición)
- ✅ `app/templates/admin/users.html` (botón editar agregado)

**Funcionalidades:**
- Formulario completo de edición de usuarios
- Cambio de nombre, email, foto de perfil
- Cambio opcional de contraseña
- Validación de email único
- Estadísticas del usuario en formulario
- Eliminación con validación (no permite eliminar si tiene compras)
- Modal de confirmación para eliminación

**Tiempo real:** 45 minutos

---

### 9. Filtros Avanzados de Órdenes (1 funcionalidad) ✅ COMPLETADO
**Tareas:**
- [x] Filtrar por fecha (rango desde-hasta)
- [x] Filtrar por estado
- [x] Filtrar por método de pago
- [x] Filtrar por usuario (nombre o email)

**Archivos modificados:**
- ✅ `app/blueprints/admin/routes.py` (lógica de filtros en orders_ajax)
- ✅ `app/templates/admin/orders.html` (UI de filtros avanzados)

**Funcionalidades:**
- Filtro por rango de fechas con auto-aplicación
- Filtro por nombre o email de cliente con búsqueda en tiempo real
- Filtros combinables (todos los filtros funcionan juntos)
- Botones "Aplicar Filtros" y "Limpiar Filtros"
- Enter key habilitado en búsqueda de cliente
- Interfaz mejorada con labels descriptivos

**Tiempo real:** 45 minutos

---

### 10. Drag & Drop para Reordenar Slides (1 funcionalidad) ✅ COMPLETADO
**Tareas:**
- [x] UI drag & drop con SortableJS
- [x] Endpoint para actualizar orden
- [x] Guardar orden en DB
- [x] Visual feedback al arrastrar
- [x] Auto-actualización de badges de orden

**Archivos modificados:**
- ✅ `app/blueprints/admin/routes.py` (reorder_slides endpoint)
- ✅ `app/templates/admin/slides.html` (SortableJS integration)

**Funcionalidades:**
- Drag & drop con SortableJS 1.15.0
- Handle específico para arrastre (icono grip)
- Actualización automática del orden en BD vía AJAX
- Visual feedback durante el arrastre (ghost, chosen, drag states)
- Actualización instantánea de badges de orden
- Manejo de errores con reload automático
- Tooltip informativo sobre funcionalidad
- Cursor visual (grab/grabbing)

**Tiempo real:** 30 minutos

---

## 🟢 FASE 3: BAJA PRIORIDAD (7 funcionalidades)

### 11. Sistema de Mensajería Interna (3 funcionalidades) ✅ COMPLETADO
**Tareas:**
- [x] Modelo Mensaje
- [x] Bandeja de entrada
- [x] Enviar/responder mensajes

**Archivos creados/modificados:**
- ✅ `app/models/message.py` (modelo Mensaje completo)
- ✅ `app/models/__init__.py` (agregado Mensaje)
- ✅ `app/utils/db_init.py` (create_mensajes_table migration)
- ✅ `app/blueprints/admin/routes.py` (7 rutas de mensajería)
- ✅ `app/templates/admin/mensajes.html` (bandeja de entrada/enviados)
- ✅ `app/templates/admin/mensaje_form.html` (componer/responder)
- ✅ `app/templates/admin/mensaje_detalle.html` (vista detalle con thread)
- ✅ `app/templates/admin/base_admin.html` (link en navegación con contador)

**Funcionalidades:**
- Modelo Mensaje con soporte para admin-usuario, usuario-admin
- Bandeja de entrada con mensajes recibidos (pestañas recibidos/enviados)
- Mensajes enviados por administrador
- Componer nuevo mensaje a cualquier usuario
- Ver detalles de mensaje con conversación completa (threading)
- Responder mensajes (mantiene conversación)
- Respuesta rápida desde vista de detalle
- Marcar como leído automáticamente
- Eliminar mensajes (con confirmación)
- Contador de mensajes no leídos en navegación
- Estados visuales (leído/no leído, fecha de lectura)
- Validación de permisos (solo destinatario/remitente puede ver)
- Cascade delete para respuestas
- Interfaz con Bootstrap 5 y Font Awesome

**Tiempo real:** 2 horas

---

### 12. UI para Cabeceras SEO (2 funcionalidades) ✅ COMPLETADO
**Nota:** Modelo ya existe

**Tareas:**
- [x] UI admin para editar meta tags (crear, editar, listar)
- [x] Eliminar cabeceras

**Archivos creados/modificados:**
- ✅ `app/blueprints/admin/routes.py` (rutas seo_headers, create_seo_header, edit_seo_header, delete_seo_header)
- ✅ `app/templates/admin/seo_headers.html` (listado con tabla)
- ✅ `app/templates/admin/seo_header_form.html` (formulario crear/editar)

**Funcionalidades:**
- CRUD completo para cabeceras SEO
- Campos: ruta, título, descripción, palabras clave, portada Open Graph
- Contador de caracteres en tiempo real (título 60, descripción 160)
- Vista previa estilo Google Search Result
- Validación de rutas únicas
- Upload de imagen Open Graph (1200x630px)
- Guía SEO integrada en el formulario
- Alertas informativas sobre mejores prácticas SEO

**Tiempo real:** 1 hora

---

### 13. PayU Completion (1 funcionalidad) ⏳ PENDIENTE
**Tareas:**
- [ ] Completar integración PayU
- [ ] Webhooks/IPN handlers

**Tiempo estimado:** 2-3 horas

---

### 14. Webhooks para Pagos (1 funcionalidad) ⏳ PENDIENTE
**Tareas:**
- [ ] IPN handlers para PayPal
- [ ] Webhooks para otros gateways

**Tiempo estimado:** 2 horas

---

## 📊 PROGRESO DE MIGRACIÓN

| Fase | Funcionalidades | Completadas | Pendientes | % Completo |
|------|----------------|-------------|------------|------------|
| Fase 1 (Alta) | 23 | 23 | 0 | 100% ✅ |
| Fase 2 (Media) | 15 | 15 | 0 | 100% ✅ |
| Fase 3 (Baja) | 7 | 5 | 2 | 71% 🚀 |
| **TOTAL** | **45** | **43** | **2** | **96%** ⬆️ |

---

## ⏱️ TIEMPO ESTIMADO TOTAL

| Fase | Tiempo Estimado |
|------|-----------------|
| Fase 1 | 9-13 horas |
| Fase 2 | 7-10 horas |
| Fase 3 | 7-9 horas |
| **TOTAL** | **23-32 horas** |

---

## 🎯 ORDEN DE IMPLEMENTACIÓN RECOMENDADO

### ✅ COMPLETADO - FASE 1 (Alta Prioridad)
1. ✅ **UI Cupones**
2. ✅ **Sistema de Banners**
3. ✅ **CRUD Administradores**
4. ✅ **Upload múltiples imágenes productos**
5. ✅ **Personalización de tienda**

### ✅ COMPLETADO - FASE 2 (Media Prioridad)
6. ✅ **Tablas dinámicas AJAX** (COMPLETADO)
7. ✅ **Reportes avanzados** (COMPLETADO)
8. ✅ **Gestión usuarios admin** (COMPLETADO)
9. ✅ **Filtros avanzados de órdenes** (COMPLETADO)
10. ✅ **Drag & drop reordenar slides** (COMPLETADO)

### ✅ COMPLETADO - FASE 3 (Baja Prioridad)
11. ✅ **Sistema de mensajería interna** (COMPLETADO)
12. ✅ **UI para cabeceras SEO** (COMPLETADO)

### 🚀 PENDIENTE - FASE 3 (Baja Prioridad)
13. ⏳ PayU completion
14. ⏳ Webhooks para pagos

---

## 📝 NOTAS

- Este plan se actualizará conforme se completen tareas
- Cada funcionalidad mayor tendrá su propio commit
- Se harán pruebas después de cada módulo completado
- La prioridad puede ajustarse según necesidades del negocio

---

**Última actualización:** 2025-01-19
**Actualizado por:** Sistema de migración automática
**Progreso actual:** 96% completado (43/45 funcionalidades) 🎉
**Últimas funcionalidades completadas:**
- ✅ **FASE 1 Y FASE 2 COMPLETADAS AL 100%** 🎉
- ✅ **FASE 3 AL 71%** - Solo quedan 2 funcionalidades pendientes
- **Sistema de mensajería interna** (bandeja de entrada, enviar, responder, threading)
- **UI para Cabeceras SEO** (CRUD completo, vista previa Google, contador de caracteres)
- **Reportes avanzados con Chart.js** (gráficos de ventas, top productos, métodos de pago)
- **Exportación a Excel** con openpyxl y estilos profesionales
- Gestión completa de usuarios desde admin (editar/eliminar)
- Filtros avanzados de órdenes (fecha, usuario, método pago, estado)
- Drag & drop para reordenar slides (SortableJS)
