# 📋 PLAN DE MIGRACIÓN - Funcionalidades Pendientes

**Total de funcionalidades pendientes:** 45
**Prioridad:** Alta (23), Media (15), Baja (7)
**Estado actual:** 82.5% migrado

---

## 🔴 FASE 1: ALTA PRIORIDAD (23 funcionalidades)

### 1. Sistema de Banners (7 funcionalidades) ⏳ EN PROGRESO
**Impacto:** Alto - Usado en frontend para promociones

**Tareas:**
- [ ] Crear modelo Banner en SQLAlchemy
- [ ] Migración SQL para tabla banner
- [ ] Rutas admin CRUD (/admin/banners)
- [ ] Templates admin (listar, crear, editar)
- [ ] AJAX para tabla dinámica (DataTables)
- [ ] Mostrar banners en frontend por categoría/subcategoría
- [ ] Upload de imágenes de banner

**Archivos a crear:**
- `app/models/banner.py`
- `app/blueprints/admin/routes.py` (agregar rutas)
- `app/templates/admin/banners.html`
- `app/templates/admin/banner_form.html`
- `app/templates/components/banner_display.html`

**Tiempo estimado:** 2-3 horas

---

### 2. CRUD Administradores Completo (6 funcionalidades) ⏳ PENDIENTE
**Impacto:** Alto - Gestión de equipo admin

**Estado actual:** Modelo existe, falta UI completa

**Tareas:**
- [ ] Listar todos los administradores
- [ ] Crear nuevo administrador desde admin
- [ ] Editar perfil de administrador
- [ ] Eliminar administrador
- [ ] Activar/Desactivar administrador
- [ ] Upload foto de perfil administrador

**Archivos a modificar:**
- `app/blueprints/admin/routes.py`
- Crear `app/templates/admin/administradores.html`
- Crear `app/templates/admin/admin_form.html`

**Tiempo estimado:** 1-2 horas

---

### 3. Personalización de Tienda (8 funcionalidades) ⏳ PENDIENTE
**Impacto:** Alto - Branding y personalización

**Tareas:**
- [ ] Cambiar logo de la tienda
- [ ] Cambiar favicon
- [ ] Personalizar colores (fondo, texto, navbar)
- [ ] Configurar enlaces redes sociales
- [ ] Facebook Pixel integration
- [ ] Google Analytics integration
- [ ] Scripts personalizados (header/footer)
- [ ] Seleccionar plantilla/tema

**Archivos a crear/modificar:**
- `app/models/comercio.py` (agregar campos)
- `app/blueprints/admin/routes.py` (configuración)
- `app/templates/admin/configuracion.html`
- `app/templates/admin/personalizacion.html`

**Tiempo estimado:** 3-4 horas

---

### 4. Upload Múltiples Imágenes Productos (1 funcionalidad) ⏳ PENDIENTE
**Impacto:** Alto - PHP soporta 3 imágenes, Flask solo 1

**Estado actual:** Solo soporta portada

**Tareas:**
- [ ] Actualizar modelo Producto para multimedia JSON
- [ ] UI para subir múltiples imágenes
- [ ] Galería de imágenes en detalle de producto
- [ ] Editar/eliminar imágenes adicionales

**Archivos a modificar:**
- `app/models/product.py` (multimedia JSON ya existe)
- `app/blueprints/admin/routes.py` (upload múltiple)
- `app/templates/admin/product_form.html`
- `app/templates/shop/product_detail.html` (galería)

**Tiempo estimado:** 1-2 horas

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

### 6. Tablas Dinámicas AJAX con DataTables (7 módulos) ⏳ PENDIENTE
**Impacto:** Medio - Mejora UX en admin

**Módulos:**
- [ ] Productos (app/templates/admin/products.html)
- [ ] Categorías
- [ ] Subcategorías
- [ ] Usuarios
- [ ] Ventas/Órdenes
- [ ] Banners
- [ ] Visitas

**Tareas:**
- [ ] Integrar DataTables en todos los listados
- [ ] Endpoints AJAX para paginación server-side
- [ ] Búsqueda y filtros en tiempo real
- [ ] Ordenamiento por columnas

**Tiempo estimado:** 2-3 horas

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
| Fase 1 (Alta) | 23 | 1 | 22 | 4% |
| Fase 2 (Media) | 15 | 0 | 15 | 0% |
| Fase 3 (Baja) | 7 | 0 | 7 | 0% |
| **TOTAL** | **45** | **1** | **44** | **2%** |

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

1. ✅ **UI Cupones** (ya completo)
2. ⏳ **Sistema de Banners** (en progreso)
3. ⏳ CRUD Administradores
4. ⏳ Upload múltiples imágenes productos
5. ⏳ Personalización de tienda
6. ⏳ Tablas dinámicas AJAX
7. ⏳ Reportes avanzados
8. ⏳ Gestión usuarios admin
9. ⏳ Resto de funcionalidades

---

## 📝 NOTAS

- Este plan se actualizará conforme se completen tareas
- Cada funcionalidad mayor tendrá su propio commit
- Se harán pruebas después de cada módulo completado
- La prioridad puede ajustarse según necesidades del negocio

---

**Última actualización:** 2025-01-19
**Actualizado por:** Sistema de migración automática
