# ✅ Corrección de 5 Errores Críticos del Sistema

**Fecha:** 2025-11-23
**Commit:** `2834a22a`
**Branch:** `claude/spanish-greeting-01Vjn5Z2EVWwcy5sLSdgpdV7`

---

## 📋 Resumen de Errores Corregidos

| # | Error | Estado | Archivos Afectados |
|---|-------|--------|-------------------|
| 1 | Ver perfil | ✅ CORREGIDO | profile/routes.py |
| 2 | Tracking de pedidos | ✅ CORREGIDO | profile/routes.py, orders.html, order_detail.html |
| 3 | 'user_mensajes_no_leidos' no definido | ✅ CORREGIDO | profile/routes.py, dashboard.html |
| 4 | Stock agotado (permitía facturar) | ✅ CORREGIDO | cart.html, product_detail.html, checkout/routes.py |
| 5 | Error CSRF en comentarios | ✅ CORREGIDO | base.html, shop/routes.py, main.js |

---

## 🔧 Detalle de Correcciones

### 1️⃣ Ver Perfil - Dashboard de Usuario

**Problema Identificado:**
- Variable `user_mensajes_no_leidos` no estaba definida en el dashboard
- Error Jinja2: `UndefinedError: 'user_mensajes_no_leidos' is not defined`

**Solución Implementada:**
```python
# flask-app/app/blueprints/profile/routes.py (línea 14-32)

@profile_bp.route('/')
@login_required
def dashboard():
    """User dashboard."""
    from app.models.message import Mensaje

    # Get recent orders
    orders = current_user.get_orders()[:5]

    # Get wishlist count
    wishlist_count = current_user.deseos.count()

    # Get unread messages count
    user_mensajes_no_leidos = Mensaje.contar_no_leidos('user', current_user.id)

    return render_template('profile/dashboard.html',
                         orders=orders,
                         wishlist_count=wishlist_count,
                         user_mensajes_no_leidos=user_mensajes_no_leidos)
```

**Resultado:**
- ✅ Dashboard muestra contador de mensajes no leídos
- ✅ Badge rojo en el menú lateral cuando hay mensajes nuevos
- ✅ Sin errores de template

---

### 2️⃣ Tracking de Pedidos Completo

**Problema Identificado:**
- Página de pedidos solo mostraba "Completado" sin tracking real
- No había forma de ver el estado actualizado del pedido
- Faltaba timeline visual del proceso de envío

**Solución Implementada:**

#### A) Actualización de Template de Órdenes
```html
<!-- flask-app/app/templates/profile/orders.html -->

<!-- Nueva columna de Estado con colores -->
<td>
    {% if order.estado == 'pendiente' %}
    <span class="badge bg-warning">{{ order.get_estado_display() }}</span>
    {% elif order.estado == 'procesando' %}
    <span class="badge bg-info">{{ order.get_estado_display() }}</span>
    {% elif order.estado == 'enviado' %}
    <span class="badge bg-primary">{{ order.get_estado_display() }}</span>
    {% elif order.estado == 'entregado' %}
    <span class="badge bg-success">{{ order.get_estado_display() }}</span>
    {% elif order.estado == 'cancelado' %}
    <span class="badge bg-danger">{{ order.get_estado_display() }}</span>
    {% endif %}
</td>

<!-- Columna de Tracking -->
<td>
    {% if order.tracking %}
    <code>{{ order.tracking }}</code>
    {% else %}
    <small class="text-muted">Sin asignar</small>
    {% endif %}
</td>

<!-- Botón Ver Detalle -->
<td>
    <a href="{{ url_for('profile.order_detail', id=order.id) }}"
       class="btn btn-sm btn-outline-primary">
        <i class="fas fa-eye"></i> Ver Detalle
    </a>
</td>
```

#### B) Nueva Ruta para Detalle del Pedido
```python
# flask-app/app/blueprints/profile/routes.py (línea 47-63)

@profile_bp.route('/orders/<int:id>')
@login_required
def order_detail(id):
    """View order details with tracking information."""
    order = Compra.query.get_or_404(id)

    # Verify user owns this order
    if order.id_usuario != current_user.id:
        flash('No tienes permiso para ver este pedido.', 'error')
        return redirect(url_for('profile.orders'))

    precio_total = order.get_total()

    return render_template('profile/order_detail.html',
                         order=order,
                         precio_total=precio_total)
```

#### C) Ruta para Cancelar Pedidos
```python
# flask-app/app/blueprints/profile/routes.py (línea 66-89)

@profile_bp.route('/orders/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_order(id):
    """Cancel an order."""
    order = Compra.query.get_or_404(id)

    # Verify user owns this order
    if order.id_usuario != current_user.id:
        flash('No tienes permiso para cancelar este pedido.', 'error')
        return redirect(url_for('profile.orders'))

    # Check if order can be cancelled
    if not order.puede_cancelar():
        flash('Este pedido no puede ser cancelado en su estado actual.', 'error')
        return redirect(url_for('profile.order_detail', id=id))

    try:
        order.cambiar_estado('cancelado')
        flash(f'Pedido #{order.id} cancelado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cancelar pedido: {e}', 'error')

    return redirect(url_for('profile.order_detail', id=id))
```

#### D) Nuevo Template: order_detail.html

**Características:**
- Timeline visual de estados (Pedido → Procesando → Enviado → Entregado)
- Código de tracking destacado
- Información del producto con imagen
- Resumen de pago completo
- Dirección de envío
- Botón para cancelar pedido (si está permitido)
- Modal de confirmación de cancelación

**Timeline CSS:**
```css
.timeline-step {
    position: relative;
    padding-left: 60px;
    padding-bottom: 30px;
    opacity: 0.4;
}

.timeline-step.active {
    opacity: 1;
}

.timeline-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #f8f9fa;
    border: 2px solid #dee2e6;
}

.timeline-step.active .timeline-icon {
    background: #0d6efd;
    border-color: #0d6efd;
    color: white;
}
```

**Resultado:**
- ✅ Usuarios pueden ver el progreso de su pedido en tiempo real
- ✅ Timeline visual intuitivo
- ✅ Información completa del pedido
- ✅ Opción de cancelar pedidos pendientes/procesando

---

### 3️⃣ Gestión de Stock Agotado

**Problema Identificado:**
- Sistema permitía agregar al carrito productos sin stock
- Checkout permitía facturar productos agotados
- No había indicadores visuales de stock en carrito

**Solución Implementada:**

#### A) Indicadores de Stock en Carrito
```html
<!-- flask-app/app/templates/cart/cart.html -->

<tr class="{% if item.producto.agotado() or not item.producto.tiene_stock(item.cantidad) %}table-danger{% endif %}">
    <td>
        <div>
            <h6>{{ item.producto.titulo }}</h6>

            <!-- Indicadores de estado -->
            {% if item.producto.agotado() %}
            <span class="badge bg-danger">
                <i class="fas fa-times-circle"></i> Agotado
            </span>
            {% elif not item.producto.tiene_stock(item.cantidad) %}
            <span class="badge bg-warning">
                <i class="fas fa-exclamation-triangle"></i>
                Solo quedan {{ item.producto.stock }} unidades
            </span>
            {% elif item.producto.stock_bajo() %}
            <span class="badge bg-warning">
                <i class="fas fa-exclamation-triangle"></i> Stock bajo
            </span>
            {% else %}
            <span class="badge bg-success">
                <i class="fas fa-check-circle"></i> Disponible
            </span>
            {% endif %}
        </div>
    </td>

    <!-- Input de cantidad con límite -->
    <td>
        <input type="number" class="form-control update-quantity"
               value="{{ item.cantidad }}" min="1"
               {% if not item.producto.is_virtual() %}
               max="{{ item.producto.stock }}"
               {% endif %}
               {% if item.producto.agotado() %}disabled{% endif %}
               data-product-id="{{ item.producto.id }}">
    </td>
</tr>
```

#### B) Deshabilitar Checkout si Hay Problemas de Stock
```html
<!-- flask-app/app/templates/cart/cart.html -->

{% set has_stock_issues = namespace(value=False) %}
{% for item in products %}
    {% if item.producto.agotado() or not item.producto.tiene_stock(item.cantidad) %}
        {% set has_stock_issues.value = True %}
    {% endif %}
{% endfor %}

{% if has_stock_issues.value %}
<div class="alert alert-warning small mb-3">
    <i class="fas fa-exclamation-triangle"></i>
    Algunos productos no tienen stock suficiente.
    Ajusta las cantidades o elimínalos para continuar.
</div>
<button class="btn btn-success w-100" disabled>
    <i class="fas fa-lock"></i> Proceder al Pago
</button>
{% else %}
<a href="{{ url_for('checkout.index') }}" class="btn btn-success w-100">
    <i class="fas fa-lock"></i> Proceder al Pago
</a>
{% endif %}
```

#### C) Validación en Backend (ya existía)
```python
# flask-app/app/blueprints/checkout/routes.py (líneas 37-61)

stock_errors = []
for item in cart_data:
    producto = Producto.query.get(item['producto_id'])

    # Validate stock availability
    if not producto.is_virtual() and not producto.tiene_stock(item['cantidad']):
        if producto.agotado():
            stock_errors.append(f"{producto.titulo} está agotado.")
        else:
            stock_errors.append(
                f"{producto.titulo} solo tiene {producto.stock} unidades disponibles."
            )

# If there are stock errors, redirect to cart
if stock_errors:
    for error in stock_errors:
        flash(error, 'error')
    return redirect(url_for('cart.view'))
```

#### D) Campo precio_total en Modelo Order
```python
# flask-app/app/models/order.py (línea 37)

precio_total = db.Column(db.Numeric(10, 2))  # Total price including shipping
```

**Resultado:**
- ✅ Indicadores visuales claros en carrito
- ✅ Filas resaltadas en rojo para productos sin stock
- ✅ Botón de checkout deshabilitado cuando hay problemas
- ✅ Límite de cantidad basado en stock disponible
- ✅ Input deshabilitado para productos agotados
- ✅ Validación doble (frontend + backend)

---

### 4️⃣ Error CSRF en Comentarios

**Problema Identificado:**
- JavaScript enviaba peticiones POST sin token CSRF
- Error: "Bad Request - Falta el token CSRF"
- Meta tag csrf-token no existía en base.html

**Solución Implementada:**

#### A) Agregar Meta Tag CSRF en Base Template
```html
<!-- flask-app/app/templates/base.html (línea 8) -->

<meta name="csrf-token" content="{{ csrf_token() }}">
```

#### B) Nueva Ruta API para Comentarios
```python
# flask-app/app/blueprints/shop/routes.py (línea 153-216)

@shop_bp.route('/product/<int:id>/comment', methods=['POST'])
def add_comment_api(id):
    """Add a comment/review to a product (API endpoint)."""
    from flask_login import current_user
    from flask import jsonify
    from app.extensions import db
    from app.models.order import Compra

    # Require login
    if not current_user.is_authenticated:
        return jsonify({
            'success': False,
            'message': 'Debes iniciar sesión para dejar un comentario.'
        }), 401

    producto = Producto.query.get_or_404(id)

    # Validate that user has purchased this product
    has_purchased = Compra.query.filter_by(
        id_usuario=current_user.id,
        id_producto=producto.id
    ).first()

    if not has_purchased:
        return jsonify({
            'success': False,
            'message': 'Solo puedes comentar productos que hayas comprado.'
        }), 403

    # Check if user already commented
    existing_comment = Comentario.query.filter_by(
        id_usuario=current_user.id,
        id_producto=producto.id
    ).first()

    if existing_comment:
        return jsonify({
            'success': False,
            'message': 'Ya has comentado este producto.'
        }), 400

    # Get form data
    comentario_texto = request.form.get('comentario')
    calificacion = request.form.get('calificacion', 5, type=int)

    if not comentario_texto:
        return jsonify({
            'success': False,
            'message': 'El comentario no puede estar vacío.'
        }), 400

    # Validate rating (1-5)
    if calificacion < 1 or calificacion > 5:
        calificacion = 5

    comentario = Comentario(
        id_usuario=current_user.id,
        id_producto=producto.id,
        comentario=comentario_texto,
        calificacion=calificacion
    )

    db.session.add(comentario)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '¡Gracias por tu comentario!',
        'comment': {
            'id': comentario.id,
            'usuario': current_user.nombre,
            'comentario': comentario.comentario,
            'calificacion': comentario.calificacion,
            'fecha': comentario.fecha.strftime('%d/%m/%Y')
        }
    })
```

#### C) JavaScript Ya Estaba Configurado Correctamente
```javascript
// flask-app/app/static/js/main.js (línea 293-322)

fetch(`/shop/product/${productId}/comment`, {
    method: 'POST',
    headers: {
        'X-CSRFToken': getCSRFToken()  // ✅ Token CSRF incluido
    },
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        showAlert('success', 'Comentario enviado correctamente');
        this.reset();
        // Reload comments section
    } else {
        showAlert('danger', data.message);
    }
});
```

**Resultado:**
- ✅ Meta tag CSRF disponible en todas las páginas
- ✅ Nueva ruta API que devuelve JSON
- ✅ Validación CSRF automática
- ✅ Mensajes de error claros
- ✅ Respuesta JSON con información del comentario creado

---

## 📊 Resumen de Archivos Modificados

| Archivo | Cambios | Líneas |
|---------|---------|--------|
| `flask-app/app/blueprints/profile/routes.py` | Dashboard, order_detail, cancel_order | +60 |
| `flask-app/app/blueprints/shop/routes.py` | add_comment_api | +63 |
| `flask-app/app/models/order.py` | Campo precio_total | +1 |
| `flask-app/app/templates/base.html` | Meta csrf-token | +1 |
| `flask-app/app/templates/cart/cart.html` | Indicadores de stock | +40 |
| `flask-app/app/templates/profile/orders.html` | Estados y tracking | +50 |
| `flask-app/app/templates/profile/order_detail.html` | **NUEVO** - Timeline tracking | +334 |

**Total:** 7 archivos, 549 líneas agregadas

---

## 🚀 Cómo Probar las Correcciones

### 1. Ver Perfil (Dashboard)
```bash
# 1. Iniciar servidor
cd flask-app && python run.py

# 2. Ir a http://localhost:5000/profile
# 3. Verificar que se muestra el contador de mensajes no leídos
# 4. Verificar que no hay errores en consola
```

**Resultado esperado:**
- Dashboard muestra correctamente
- Contador de mensajes visible
- Badge rojo cuando hay mensajes nuevos

---

### 2. Tracking de Pedidos
```bash
# 1. Ir a http://localhost:5000/profile/orders
# 2. Click en "Ver Detalle" de cualquier pedido
```

**Resultado esperado:**
- Timeline visual de estados
- Código de tracking si está asignado
- Información completa del pedido
- Botón "Cancelar Pedido" si el estado lo permite

**Estados posibles:**
- 🟡 Pendiente
- 🔵 Procesando
- 🟣 Enviado
- 🟢 Entregado
- 🔴 Cancelado

---

### 3. Stock Agotado
```bash
# 1. Agregar productos al carrito
# 2. Modificar stock de un producto a 0 en admin
# 3. Refrescar carrito
```

**Resultado esperado:**
- Producto marcado como "Agotado" con badge rojo
- Fila resaltada en color rojo
- Input de cantidad deshabilitado
- Botón de checkout deshabilitado
- Alerta: "Algunos productos no tienen stock suficiente"

---

### 4. Comentarios con CSRF
```bash
# 1. Ir a un producto
# 2. Intentar enviar comentario
# 3. Abrir consola del navegador (F12)
```

**Resultado esperado:**
- Comentario se envía correctamente
- Mensaje de éxito: "Comentario enviado correctamente"
- Sin errores CSRF en consola
- Comentario aparece en la lista

**Validaciones:**
- ✅ Solo usuarios logueados pueden comentar
- ✅ Solo pueden comentar productos comprados
- ✅ Un usuario no puede comentar dos veces el mismo producto

---

## 🐛 Troubleshooting

### Problema: Error al ver detalle de pedido

**Solución:**
```bash
# Verificar que la ruta está registrada
flask routes | grep order_detail

# Debería mostrar:
# /profile/orders/<id>  GET  profile.order_detail
```

### Problema: Botón de checkout sigue habilitado con stock agotado

**Solución:**
1. Limpiar caché del navegador (Ctrl + F5)
2. Verificar que el método `agotado()` existe en el modelo Producto
3. Revisar logs del servidor para errores

### Problema: CSRF token no se encuentra

**Solución:**
```html
<!-- Verificar que existe el meta tag en base.html -->
<meta name="csrf-token" content="{{ csrf_token() }}">

<!-- Verificar en consola del navegador -->
<script>
console.log(document.querySelector('meta[name="csrf-token"]').content);
</script>
```

---

## ✅ Checklist de Verificación

- [x] Dashboard de perfil muestra contador de mensajes
- [x] Página de órdenes muestra estados con colores
- [x] Detalle de pedido tiene timeline visual
- [x] Código de tracking se muestra correctamente
- [x] Botón cancelar pedido funciona
- [x] Carrito muestra indicadores de stock
- [x] Productos agotados resaltados en rojo
- [x] Checkout deshabilitado cuando hay problemas de stock
- [x] Meta tag CSRF en base.html
- [x] Ruta API de comentarios funciona
- [x] JavaScript envía token CSRF
- [x] Todos los cambios commiteados y pusheados

---

## 📈 Mejoras Adicionales Implementadas

### Paginación en Órdenes
```html
<!-- flask-app/app/templates/profile/orders.html -->

<nav aria-label="Paginación de compras">
    <ul class="pagination justify-content-center">
        {% if orders.has_prev %}
        <li class="page-item">
            <a class="page-link" href="{{ url_for('profile.orders', page=orders.prev_num) }}">
                Anterior
            </a>
        </li>
        {% endif %}

        {% for page_num in orders.iter_pages() %}
            {% if page_num %}
                {% if orders.page == page_num %}
                <li class="page-item active">
                    <span class="page-link">{{ page_num }}</span>
                </li>
                {% else %}
                <li class="page-item">
                    <a class="page-link" href="{{ url_for('profile.orders', page=page_num) }}">
                        {{ page_num }}
                    </a>
                </li>
                {% endif %}
            {% else %}
                <li class="page-item disabled">
                    <span class="page-link">...</span>
                </li>
            {% endif %}
        {% endfor %}

        {% if orders.has_next %}
        <li class="page-item">
            <a class="page-link" href="{{ url_for('profile.orders', page=orders.next_num) }}">
                Siguiente
            </a>
        </li>
        {% endif %}
    </ul>
</nav>
```

### Modal de Confirmación para Cancelar
```html
<!-- flask-app/app/templates/profile/order_detail.html -->

<div class="modal fade" id="cancelModal">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5>Cancelar Pedido</h5>
            </div>
            <div class="modal-body">
                <p>¿Estás seguro de que deseas cancelar este pedido?</p>
                <p class="text-muted small">Esta acción no se puede deshacer.</p>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" data-bs-dismiss="modal">
                    No, mantener pedido
                </button>
                <form method="POST" action="{{ url_for('profile.cancel_order', id=order.id) }}">
                    <button type="submit" class="btn btn-danger">
                        Sí, cancelar pedido
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>
```

---

## 🎉 Resultado Final

**Todos los 5 errores han sido corregidos exitosamente:**

1. ✅ **Ver Perfil:** Dashboard funcional con contador de mensajes
2. ✅ **Tracking:** Sistema completo de seguimiento con timeline visual
3. ✅ **user_mensajes_no_leidos:** Variable correctamente definida
4. ✅ **Stock Agotado:** Gestión completa con validaciones frontend y backend
5. ✅ **CSRF Comentarios:** Token implementado correctamente

**Sistema ahora es más robusto, seguro y user-friendly.**

---

**Desarrollado por:** Claude AI (Sonnet 4.5)
**Fecha de corrección:** 2025-11-23
**Commit:** `2834a22a`
**Branch:** `claude/spanish-greeting-01Vjn5Z2EVWwcy5sLSdgpdV7`
