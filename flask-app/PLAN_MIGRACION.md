# 📋 PLAN DE MIGRACIÓN - Funcionalidades Pendientes

**Total de funcionalidades pendientes:** 45
**Prioridad:** Alta (23), Media (15), Baja (7)
**Estado actual:** 91% migrado (41/45 completadas)

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

### 7. Reportes Avanzados (4 funcionalidades) ⏳ PENDIENTE
**Impacto:** Medio - Analytics y reportes

**Tareas:**
- [ ] Reportes de ventas por rango de fechas
- [ ] Filtros avanzados (producto, usuario, método pago)
- [ ] Gráficos de ventas (Chart.js)
- [ ] Exportar reportes a Excel (openpyxl)

**Archivos a crear:**
- `app/blueprints/admin/routes.py` (reportes)
- `app/templates/admin/reportes.html`
- `app/services/report_service.py`

**Tiempo estimado:** 2-3 horas

---

### 8. Gestión Usuarios desde Admin (2 funcionalidades) ⏳ PENDIENTE
**Tareas:**
- [ ] Editar usuario desde admin
- [ ] Eliminar usuario desde admin

**Tiempo estimado:** 30 minutos

---

### 9. Filtros Avanzados de Órdenes (1 funcionalidad) ⏳ PENDIENTE
**Tareas:**
- [ ] Filtrar por fecha
- [ ] Filtrar por estado
- [ ] Filtrar por método de pago
- [ ] Filtrar por usuario

**Tiempo estimado:** 1 hora

---

### 10. Drag & Drop para Reordenar Slides (1 funcionalidad) ⏳ PENDIENTE
**Tareas:**
- [ ] UI drag & drop con SortableJS
- [ ] Endpoint para actualizar orden
- [ ] Guardar orden en DB

**Tiempo estimado:** 1 hora

---

## 🟢 FASE 3: BAJA PRIORIDAD (7 funcionalidades)

### 11. Sistema de Mensajería Interna (3 funcionalidades) ⏳ PENDIENTE
**Tareas:**
- [ ] Modelo Mensaje
- [ ] Bandeja de entrada
- [ ] Enviar/responder mensajes

**Tiempo estimado:** 2-3 horas

---

### 12. UI para Cabeceras SEO (2 funcionalidades) ⏳ PENDIENTE
**Nota:** Modelo ya existe

**Tareas:**
- [ ] UI admin para editar meta tags
- [ ] Eliminar cabeceras

**Tiempo estimado:** 1 hora

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
| Fase 2 (Media) | 15 | 9 | 6 | 60% 🚀 |
| Fase 3 (Baja) | 7 | 0 | 7 | 0% |
| **TOTAL** | **45** | **32** | **13** | **71%** ⬆️ |

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

### 🚀 SIGUIENTE - FASE 2 (Media Prioridad)
6. ⏳ **Tablas dinámicas AJAX** (EN PROGRESO)
7. ⏳ Reportes avanzados
8. ⏳ Gestión usuarios admin
9. ⏳ Filtros avanzados de órdenes
10. ⏳ Drag & drop reordenar slides

### 📋 PENDIENTE - FASE 3 (Baja Prioridad)
11. ⏳ Sistema de mensajería interna
12. ⏳ UI para cabeceras SEO
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
