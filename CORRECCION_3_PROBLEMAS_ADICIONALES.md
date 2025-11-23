# Corrección de 3 Problemas Adicionales del Sistema

**Fecha:** 2025-11-23
**Branch:** claude/spanish-greeting-01Vjn5Z2EVWwcy5sLSdgpdV7

## Resumen

Se identificaron y corrigieron 3 problemas reportados por el usuario:

1. ✅ Stock no muestra cantidad disponible en tarjetas de productos
2. ✅ Lista de deseos no funciona en frontend
3. ✅ Error CSRF en formulario de reseñas

---

## 1. Visualización de Stock en Tarjetas de Productos

### Problema
Las tarjetas de productos solo mostraban "Disponible" sin indicar la cantidad de unidades en stock.

### Ubicación
- **Archivo:** `flask-app/app/templates/components/product_card.html`
- **Línea:** 56

### Cambio Realizado
```html
<!-- ANTES -->
<span class="badge bg-success w-100">
    <i class="fas fa-check-circle"></i> Disponible
</span>

<!-- DESPUÉS -->
<span class="badge bg-success w-100">
    <i class="fas fa-check-circle"></i> En Stock ({{ producto.stock }} disponibles)
</span>
```

### Resultado
Ahora las tarjetas de productos muestran claramente cuántas unidades están disponibles.

### Nota sobre Decremento de Stock
El decremento automático de stock **YA ESTABA IMPLEMENTADO** correctamente:
- **Ubicación:** `flask-app/app/services/payment_service.py:276`
- **Función:** `create_order_from_cart()`
- **Código:**
```python
# Decrement stock immediately (reserve inventory)
if not producto.decrementar_stock(item['cantidad']):
    db.session.rollback()
    return False, f"Error al decrementar stock del producto '{producto.titulo}'", None
```

El sistema valida y decrementa el stock automáticamente al crear cada orden.

---

## 2. Lista de Deseos (Wishlist) - Funcionalidad Frontend

### Problema
Los botones de "Agregar a Lista de Deseos" no respondían a los clics porque no tenían event listeners asignados.

### Análisis
- El backend ya tenía el endpoint `/profile/wishlist/toggle` funcionando
- La función JavaScript `toggleWishlist()` existía pero no se inicializaba
- Los botones con clase `.add-to-wishlist` no tenían eventos vinculados

### Cambios Realizados

#### 2.1. Nueva función de inicialización
**Archivo:** `flask-app/app/static/js/main.js`
**Línea:** 275-286

```javascript
/**
 * Add to wishlist buttons (product listing and detail pages)
 */
function initAddToWishlistButtons() {
    const addToWishlistButtons = document.querySelectorAll('.add-to-wishlist');
    addToWishlistButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.productId;
            toggleWishlist(productId, this);
        });
    });
}
```

#### 2.2. Llamada en DOMContentLoaded
**Archivo:** `flask-app/app/static/js/main.js`
**Línea:** 687

```javascript
// Initialize add to wishlist buttons
initAddToWishlistButtons();
```

### Resultado
Los botones de lista de deseos ahora funcionan correctamente en:
- ✅ Listado de productos (tarjetas)
- ✅ Página de detalle de producto
- ✅ Productos relacionados

---

## 3. Error CSRF en Formulario de Reseñas

### Problema
El formulario de reseñas generaba error "Solicitud incorrecta - Falta el token CSRF" al intentar enviar un comentario.

### Causa Raíz
El formulario de comentarios no incluía:
1. El token CSRF requerido por Flask-WTF
2. El atributo `id="commentForm"` que busca el JavaScript
3. El atributo `data-product-id` para AJAX

### Cambios Realizados
**Archivo:** `flask-app/app/templates/shop/product_detail.html`
**Línea:** 225-226

```html
<!-- ANTES -->
<form method="POST" action="{{ url_for('shop.add_comment', ruta=producto.ruta) }}">

<!-- DESPUÉS -->
<form id="commentForm" method="POST"
      action="{{ url_for('shop.add_comment', ruta=producto.ruta) }}"
      data-product-id="{{ producto.id }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

### Funcionamiento
El formulario ahora funciona de dos formas:
1. **Con JavaScript habilitado:** Envío AJAX al endpoint `/shop/product/{id}/comment`
2. **Sin JavaScript:** POST tradicional a `/producto/{ruta}/comentar`

Ambos endpoints validan el token CSRF automáticamente.

### Backend Endpoints
- **AJAX:** `@shop_bp.route('/product/<int:id>/comment', methods=['POST'])` (línea 153)
- **Tradicional:** `@shop_bp.route('/producto/<ruta>/comentar', methods=['POST'])` (línea 219)

Ambos están protegidos con CSRF por Flask-WTF.

---

## Archivos Modificados

### Templates
1. `flask-app/app/templates/components/product_card.html`
   - Línea 56: Agregado contador de stock

2. `flask-app/app/templates/shop/product_detail.html`
   - Línea 225-226: Agregado id, data-product-id y token CSRF al formulario

### JavaScript
3. `flask-app/app/static/js/main.js`
   - Líneas 275-286: Nueva función `initAddToWishlistButtons()`
   - Línea 687: Llamada a inicialización en DOMContentLoaded

---

## Validación y Pruebas

### Stock
- ✅ Tarjetas de producto muestran cantidad exacta
- ✅ Stock se decrementa automáticamente en compras
- ✅ Validación de stock antes de checkout
- ✅ Productos agotados no permiten compra

### Lista de Deseos
- ✅ Botón funciona en tarjetas de productos
- ✅ Botón funciona en página de detalle
- ✅ Icono cambia de vacío (far) a lleno (fas)
- ✅ Mensaje de confirmación se muestra
- ✅ Redirección a login si no autenticado

### Reseñas/Comentarios
- ✅ Token CSRF incluido en formulario
- ✅ Envío AJAX funciona correctamente
- ✅ Fallback a POST tradicional disponible
- ✅ Validación de compra previa
- ✅ Prevención de comentarios duplicados

---

## Notas Técnicas

### Seguridad
- Todos los endpoints POST están protegidos con CSRF
- Validación de autenticación en lista de deseos
- Validación de compra previa en comentarios

### Performance
- Stock se reserva con `SELECT FOR UPDATE` (lock pesimista)
- Prevención de condiciones de carrera en compras
- Decrementode stock atómico en transacción

### UX/UI
- Feedback visual claro en todas las acciones
- Mensajes informativos al usuario
- Estados disabled en productos agotados
- Badges de colores según disponibilidad

---

## Conclusión

Los 3 problemas han sido solucionados satisfactoriamente:

1. **Stock:** Ahora se muestra claramente la cantidad disponible
2. **Wishlist:** Funcionalidad completamente operativa
3. **CSRF:** Token incluido, sin errores al enviar reseñas

El sistema está listo para producción en estos aspectos.
