# DETALLES TÉCNICOS - INCONSISTENCIAS BACKEND VS FRONTEND

---

## 1. SISTEMA DE MENSAJERÍA (CRÍTICO)

### 1.1 Análisis del Modelo Actual
```
Tabla: mensajes
- id (PK)
- remitente_tipo: 'admin' | 'user'
- remitente_id: int (FK a admin.id o usuario.id)
- destinatario_tipo: 'admin' | 'user'
- destinatario_id: int
- asunto: VARCHAR(255)
- contenido: TEXT
- leido: BOOLEAN (default False)
- fecha_leido: DATETIME (nullable)
- mensaje_padre_id: int (FK para respuestas anidadas)
- fecha: DATETIME (default now)
```

### 1.2 Rutas Admin Existentes (VERIFICADAS)

**Listado de mensajes recibidos:**
```
Línea 3136: @admin_bp.route('/mensajes')
- Querys por: destinatario_tipo='admin', destinatario_id=current_admin.id
- Paginación incluida
- Ordena por fecha DESC
```

**Listado de mensajes enviados:**
```
Línea 3157: @admin_bp.route('/mensajes/enviados')
- Query por: remitente_tipo='admin', remitente_id=current_admin.id
```

**Crear nuevo mensaje:**
```
Línea 3174: @admin_bp.route('/mensajes/nuevo', methods=['GET', 'POST'])
- GET: Renderiza formulario (admin/mensaje_form.html)
- POST: Crea Mensaje.enviar_mensaje()
```

**Ver detalle:**
```
Línea 3214: @admin_bp.route('/mensajes/<int:id>')
- GET: Renderiza admin/mensaje_detalle.html
- Marca como leído si no lo está
```

**Responder:**
```
Línea 3245: @admin_bp.route('/mensajes/<int:id>/responder', methods=['GET', 'POST'])
- POST: Crea nuevo Mensaje con mensaje_padre_id=id
```

### 1.3 LO QUE FALTA EN EL FRONTEND (5 rutas + 3 templates)

#### Rutas a crear en: app/blueprints/profile/routes.py

**1. Listar mensajes del usuario:**
```python
@profile_bp.route('/mensajes')
@login_required
def mensajes():
    """User received messages."""
    page = request.args.get('page', 1, type=int)
    from app.models.message import Mensaje
    
    mensajes = Mensaje.query.filter_by(
        destinatario_tipo='user',
        destinatario_id=current_user.id
    ).order_by(
        Mensaje.leido.asc(),  # No leídos primero
        Mensaje.fecha.desc()
    ).paginate(page=page, per_page=10, error_out=False)
    
    return render_template('profile/mensajes.html', mensajes=mensajes)
```

**2. Ver detalle de mensaje:**
```python
@profile_bp.route('/mensajes/<int:id>')
@login_required
def mensaje_detalle(id):
    """View message details."""
    from app.models.message import Mensaje
    
    mensaje = Mensaje.query.get_or_404(id)
    
    # Validar que pertenece al usuario
    if mensaje.destinatario_tipo != 'user' or mensaje.destinatario_id != current_user.id:
        abort(403)
    
    # Marcar como leído
    if not mensaje.leido:
        mensaje.marcar_como_leido()
    
    # Obtener cadena de conversación
    respuestas = []
    actual = mensaje
    while actual.mensaje_padre_id:
        actual = Mensaje.query.get(actual.mensaje_padre_id)
        respuestas.insert(0, actual)
    respuestas.append(mensaje)
    
    return render_template('profile/mensaje_detalle.html', 
                         mensaje=mensaje, 
                         respuestas=respuestas)
```

**3. Formulario enviar nuevo mensaje:**
```python
@profile_bp.route('/mensajes/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_mensaje():
    """Send new message to admin."""
    if request.method == 'POST':
        from app.models.message import Mensaje
        
        asunto = request.form.get('asunto')
        contenido = request.form.get('contenido')
        
        if not asunto or not contenido:
            flash('Asunto y contenido son requeridos.', 'error')
            return redirect(url_for('profile.nuevo_mensaje'))
        
        # Obtener primer admin (o permitir seleccionar)
        from app.models.admin import Administrador
        admin = Administrador.query.first()
        
        if not admin:
            flash('No hay administrador disponible.', 'error')
            return redirect(url_for('profile.nuevo_mensaje'))
        
        Mensaje.enviar_mensaje(
            remitente_tipo='user',
            remitente_id=current_user.id,
            destinatario_tipo='admin',
            destinatario_id=admin.id,
            asunto=asunto,
            contenido=contenido
        )
        
        flash('Mensaje enviado correctamente.', 'success')
        return redirect(url_for('profile.mensajes'))
    
    return render_template('profile/mensaje_form.html')
```

**4. Responder mensaje:**
```python
@profile_bp.route('/mensajes/<int:id>/responder', methods=['POST'])
@login_required
def responder_mensaje(id):
    """Reply to a message."""
    from app.models.message import Mensaje
    
    mensaje_padre = Mensaje.query.get_or_404(id)
    
    # Validar que pertenece al usuario
    if mensaje_padre.destinatario_tipo != 'user' or \
       mensaje_padre.destinatario_id != current_user.id:
        abort(403)
    
    contenido = request.form.get('contenido')
    if not contenido:
        flash('El contenido de la respuesta es requerido.', 'error')
        return redirect(url_for('profile.mensaje_detalle', id=id))
    
    # El remitente original es ahora destinatario
    Mensaje.enviar_mensaje(
        remitente_tipo='user',
        remitente_id=current_user.id,
        destinatario_tipo=mensaje_padre.remitente_tipo,
        destinatario_id=mensaje_padre.remitente_id,
        asunto=f"Re: {mensaje_padre.asunto}",
        contenido=contenido,
        mensaje_padre_id=id
    )
    
    flash('Respuesta enviada.', 'success')
    return redirect(url_for('profile.mensaje_detalle', id=id))
```

**5. Eliminar mensaje:**
```python
@profile_bp.route('/mensajes/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_mensaje(id):
    """Delete message."""
    from app.models.message import Mensaje
    
    mensaje = Mensaje.query.get_or_404(id)
    
    # Validar propiedad
    if mensaje.destinatario_tipo != 'user' or \
       mensaje.destinatario_id != current_user.id:
        abort(403)
    
    db.session.delete(mensaje)
    db.session.commit()
    
    flash('Mensaje eliminado.', 'info')
    return redirect(url_for('profile.mensajes'))
```

#### Templates a crear:

**1. /templates/profile/mensajes.html**
```html
{% extends "base.html" %}
{% block title %}Mis Mensajes - Perfil{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-3">
        <!-- Sidebar igual que dashboard.html -->
    </div>
    <div class="col-md-9">
        <h3>Mis Mensajes</h3>
        
        <a href="{{ url_for('profile.nuevo_mensaje') }}" class="btn btn-primary mb-3">
            <i class="fas fa-envelope"></i> Nuevo Mensaje
        </a>
        
        {% if mensajes.items %}
        <div class="list-group">
            {% for mensaje in mensajes.items %}
            <a href="{{ url_for('profile.mensaje_detalle', id=mensaje.id) }}" 
               class="list-group-item list-group-item-action {% if not mensaje.leido %}active{% endif %}">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="mb-1">{{ mensaje.asunto }}</h6>
                        <p class="mb-1 text-muted text-truncate">{{ mensaje.contenido[:100] }}...</p>
                        <small class="text-muted">
                            De: {{ mensaje.get_remitente_nombre() }}
                        </small>
                    </div>
                    <div class="text-end">
                        {% if not mensaje.leido %}
                        <span class="badge bg-primary">Nuevo</span>
                        {% endif %}
                        <small class="text-muted d-block">
                            {{ mensaje.fecha.strftime('%d/%m/%Y %H:%M') }}
                        </small>
                    </div>
                </div>
            </a>
            {% endfor %}
        </div>
        
        <!-- Paginación -->
        {% if mensajes.pages > 1 %}
        <nav class="mt-4">
            <ul class="pagination">
                <!-- Implementar paginación -->
            </ul>
        </nav>
        {% endif %}
        {% else %}
        <div class="alert alert-info">
            No tienes mensajes. <a href="{{ url_for('profile.nuevo_mensaje') }}">Enviar uno nuevo</a>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}
```

**2. /templates/profile/mensaje_detalle.html**
```html
{% extends "base.html" %}
{% block title %}{{ mensaje.asunto }} - Mensajes{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-3">
        <!-- Sidebar -->
    </div>
    <div class="col-md-9">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h3>{{ mensaje.asunto }}</h3>
            <a href="{{ url_for('profile.mensajes') }}" class="btn btn-secondary btn-sm">
                <i class="fas fa-arrow-left"></i> Volver
            </a>
        </div>
        
        <!-- Conversación -->
        <div class="card">
            <div class="card-body">
                {% for msg in respuestas %}
                <div class="mb-4 pb-3 {% if not loop.last %}border-bottom{% endif %}">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div>
                            <h6 class="mb-0">{{ msg.get_remitente_nombre() }}</h6>
                            <small class="text-muted">{{ msg.fecha.strftime('%d/%m/%Y %H:%M') }}</small>
                        </div>
                        {% if msg.id == mensaje.id %}
                        <form method="POST" action="{{ url_for('profile.eliminar_mensaje', id=msg.id) }}" 
                              style="display: inline;">
                            <button type="submit" class="btn btn-sm btn-danger" 
                                    onclick="return confirm('¿Eliminar este mensaje?')">
                                <i class="fas fa-trash"></i>
                            </button>
                        </form>
                        {% endif %}
                    </div>
                    <div class="bg-light p-3 rounded">
                        {{ msg.contenido|linebreaks }}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- Formulario responder -->
        <div class="card mt-4">
            <div class="card-header">
                <h6 class="mb-0">Responder</h6>
            </div>
            <div class="card-body">
                <form method="POST" action="{{ url_for('profile.responder_mensaje', id=mensaje.id) }}">
                    {{ csrf_token() }}
                    <div class="mb-3">
                        <textarea class="form-control" name="contenido" rows="4" 
                                  placeholder="Escribe tu respuesta..." required></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-paper-plane"></i> Enviar Respuesta
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

**3. /templates/profile/mensaje_form.html**
```html
{% extends "base.html" %}
{% block title %}Nuevo Mensaje - Perfil{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-3">
        <!-- Sidebar -->
    </div>
    <div class="col-md-9">
        <h3>Nuevo Mensaje</h3>
        
        <div class="card">
            <div class="card-body">
                <form method="POST">
                    {{ csrf_token() }}
                    <div class="mb-3">
                        <label class="form-label">Asunto *</label>
                        <input type="text" class="form-control" name="asunto" required 
                               placeholder="Asunto del mensaje">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Mensaje *</label>
                        <textarea class="form-control" name="contenido" rows="6" required 
                                  placeholder="Escribe tu mensaje aquí..."></textarea>
                    </div>
                    <div class="d-flex gap-2">
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-paper-plane"></i> Enviar
                        </button>
                        <a href="{{ url_for('profile.mensajes') }}" class="btn btn-secondary">
                            Cancelar
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### 1.4 Cambios en base.html (agregar enlace en menú usuario)
```html
<!-- Agregar en el dropdown de perfil -->
<a class="dropdown-item" href="{{ url_for('profile.mensajes') }}">
    <i class="fas fa-envelope"></i> Mis Mensajes
    {% set unread = Mensaje.contar_no_leidos('user', current_user.id) %}
    {% if unread > 0 %}
    <span class="badge bg-danger">{{ unread }}</span>
    {% endif %}
</a>
```

---

## 2. SISTEMA DE COMENTARIOS (MEDIA PRIORIDAD)

### 2.1 Problema Identificado
En `product_detail.html` línea 210-244, se muestran comentarios pero:
- No se muestra `respuesta_admin`
- No se muestra estado de moderación (pendiente/aprobado/rechazado)

### 2.2 Cambios en product_detail.html
```html
<!-- LÍNEA 210-244: Reemplazar bloque comentarios con: -->

{% for comentario in comentarios %}
<div class="card mb-3 {% if not comentario.es_aprobado() %}border-warning{% endif %}">
    <div class="card-body">
        <!-- Info del comentario original -->
        <div class="d-flex justify-content-between align-items-start">
            <div>
                <h6 class="mb-1">
                    {{ comentario.usuario.nombre }}
                    {% if not comentario.es_aprobado() %}
                    <span class="badge bg-warning">{{ comentario.get_estado_display() }}</span>
                    {% endif %}
                </h6>
                <div class="mb-2">
                    {% for i in range(comentario.get_rating_stars()) %}
                    <i class="fas fa-star text-warning"></i>
                    {% endfor %}
                    {% for i in range(5 - comentario.get_rating_stars()) %}
                    <i class="far fa-star text-warning"></i>
                    {% endfor %}
                </div>
            </div>
            {% if current_user.is_authenticated and current_user.id == comentario.id_usuario %}
            <div class="btn-group btn-group-sm" role="group">
                <button type="button" class="btn btn-outline-primary edit-comment"
                        data-id="{{ comentario.id }}"
                        data-comentario="{{ comentario.comentario }}"
                        data-calificacion="{{ comentario.calificacion }}">
                    <i class="fas fa-edit"></i>
                </button>
                <button type="button" class="btn btn-outline-danger delete-comment"
                        data-id="{{ comentario.id }}">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            {% endif %}
        </div>
        
        <p class="mb-1">{{ comentario.comentario }}</p>
        <small class="text-muted">{{ comentario.fecha.strftime('%d/%m/%Y %H:%M') }}</small>
        
        <!-- NUEVA SECCIÓN: Respuesta del admin -->
        {% if comentario.respuesta_admin and comentario.es_aprobado() %}
        <div class="mt-3 p-3 bg-light border-start border-success rounded">
            <p class="mb-1"><strong><i class="fas fa-reply text-success"></i> Respuesta del Administrador:</strong></p>
            <p class="mb-0 text-muted">{{ comentario.respuesta_admin|linebreaks }}</p>
        </div>
        {% endif %}
    </div>
</div>
{% endfor %}
```

---

## 3. MATRIZ DE ARCHIVOS AFECTADOS

| Archivo | Tipo | Acción | Prioridad |
|---------|------|--------|-----------|
| app/blueprints/profile/routes.py | Python | Agregar 5 rutas | CRÍTICA |
| templates/profile/mensajes.html | HTML | Crear | CRÍTICA |
| templates/profile/mensaje_detalle.html | HTML | Crear | CRÍTICA |
| templates/profile/mensaje_form.html | HTML | Crear | CRÍTICA |
| templates/shop/product_detail.html | HTML | Modificar | MEDIA |
| templates/base.html | HTML | Agregar enlace | CRÍTICA |
| templates/profile/dashboard.html | HTML | Agregar contador (opcional) | BAJA |

---

## 4. VALIDACIONES Y SEGURIDAD

### Mensajería:
- Verificar que usuario solo accede a sus propios mensajes
- Verificar que no puede responder a mensajes que no le pertenecen
- CSRF token en formularios POST
- Validar que admin exista antes de enviar

### Comentarios:
- Usuario solo puede editar/eliminar propios comentarios (YA IMPLEMENTADO)
- Solo usuarios autenticados pueden comentar (YA IMPLEMENTADO)
- Solo usuarios que compraron pueden comentar (YA IMPLEMENTADO)

---

## 5. FLUJOS DE NEGOCIO

### Flujo de Mensajería Usuario:
1. Usuario: Accede a /perfil/mensajes
2. Usuario: Ve lista de mensajes recibidos (con indicador de leído)
3. Usuario: Hace clic en un mensaje → /perfil/mensajes/<id>
4. Sistema: Marca como leído
5. Usuario: Lee mensaje y responde
6. Usuario: Hace clic "Responder" → POST a /perfil/mensajes/<id>/responder
7. Sistema: Crea Mensaje con mensaje_padre_id
8. Usuario: Vuelve a ver conversación completa

### Flujo Admin respondiendo:
1. Admin: Ve /admin/mensajes (mensajes recibidos de usuarios)
2. Admin: Hace clic → /admin/mensajes/<id>
3. Admin: Lee mensaje del usuario
4. Admin: Responde → POST a /admin/mensajes/<id>/responder
5. Sistema: Crea Mensaje con remitente_tipo='admin', mensaje_padre_id=<original>
6. Usuario: Ve respuesta en su panel /perfil/mensajes

