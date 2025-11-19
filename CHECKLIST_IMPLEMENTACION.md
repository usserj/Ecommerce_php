# CHECKLIST - IMPLEMENTACIÓN DE INCONSISTENCIAS

---

## PRIORIDAD 1: CRÍTICA - SISTEMA DE MENSAJERÍA (Estimado: 5-6 horas)

### Backend (Ya existe, verificar):
- [x] Modelo Mensaje completo con campos bidireccionales
- [x] Rutas admin para mensajes (9 rutas)
- [x] Métodos helper: marcar_como_leido(), contar_no_leidos()
- [x] Método estático: enviar_mensaje()

### Frontend - Rutas a implementar:
- [ ] GET  /perfil/mensajes → Listar mensajes recibidos
- [ ] GET  /perfil/mensajes/<id> → Ver detalle + cadena conversación
- [ ] GET  /perfil/mensajes/nuevo → Formulario enviar nuevo
- [ ] POST /perfil/mensajes/nuevo → Guardar nuevo mensaje
- [ ] POST /perfil/mensajes/<id>/responder → Responder a mensaje
- [ ] POST /perfil/mensajes/<id>/eliminar → Eliminar mensaje

### Frontend - Templates a crear:
- [ ] /templates/profile/mensajes.html (listado con badge "Nuevo")
- [ ] /templates/profile/mensaje_detalle.html (conversación anidada)
- [ ] /templates/profile/mensaje_form.html (formulario nuevo)

### Frontend - Cambios en templates existentes:
- [ ] /templates/base.html: Agregar enlace en dropdown perfil
- [ ] /templates/profile/dashboard.html: Agregar contador no leídos (opcional)

### Testing:
- [ ] Usuario puede enviar mensaje a admin
- [ ] Admin ve mensaje en /admin/mensajes
- [ ] Admin puede responder
- [ ] Usuario ve respuesta en /perfil/mensajes/<id>
- [ ] Conversación anidada se muestra correctamente
- [ ] Mensaje se marca como leído al verlo
- [ ] Usuario no puede ver mensajes de otros usuarios

---

## PRIORIDAD 2: MEDIA - COMENTARIOS + RESPUESTAS ADMIN (Estimado: 1-2 horas)

### Backend (verificar que existe):
- [x] Campo respuesta_admin en modelo Comentario
- [x] Ruta admin para responder: /admin/comments/respond/<id>
- [x] Métodos en modelo: es_aprobado(), get_estado_display()

### Frontend - Templates a modificar:
- [ ] /templates/shop/product_detail.html (línea 210-244):
  - [ ] Mostrar respuesta_admin si existe
  - [ ] Mostrar estado de moderación (badge)
  - [ ] Filtrar para mostrar solo aprobados

### Testing:
- [ ] Admin responde comentario → Se guarda respuesta_admin
- [ ] Usuario ve respuesta en product_detail
- [ ] Usuario ve estado (pendiente/rechazado/aprobado)
- [ ] Respuesta solo se muestra si está aprobado

---

## PRIORIDAD 3: BAJA - NOTIFICACIONES (Estimado: 8-10 horas, OPCIONAL)

### Análisis de lo que existe:
- [x] Modelo Notificacion es básico (solo contadores admin)
- [ ] NO hay tabla de notificaciones de usuario
- [ ] NO hay rutas de usuario para notificaciones
- [ ] NO hay templates

### Si se implementa:
- [ ] Crear modelo Notificacion mejorado (user notifications)
- [ ] Crear rutas usuario: /perfil/notificaciones
- [ ] Crear templates para notificaciones
- [ ] Agregar triggers para generar notificaciones en eventos
- [ ] Sistema de notificaciones en tiempo real (WebSockets) - OPCIONAL

---

## VERIFICACIONES FINALES

### Flujos de usuario:
- [ ] Usuario puede comunicarse completamente con admin (enviar y recibir)
- [ ] Usuario ve respuestas de admin a sus comentarios
- [ ] Usuario puede aplicar cupones (YA FUNCIONA)
- [ ] Usuario puede manejar lista de deseos (YA FUNCIONA)

### Seguridad:
- [ ] Usuario solo ve sus propios mensajes
- [ ] Usuario no puede editar/eliminar mensajes de otros
- [ ] Admin solo ve mensajes dirigidos a él
- [ ] CSRF tokens en todos los formularios POST

### Rendimiento:
- [ ] Paginación en listados de mensajes
- [ ] Índices en queries: (destinatario_tipo, destinatario_id)
- [ ] Cache de contactos frecuentes (opcional)

### UX/UI:
- [ ] Indicadores visuales de mensajes no leídos
- [ ] Navegación consistente con resto del sitio
- [ ] Timestamps legibles
- [ ] Botones de acción claramente visibles

---

## ORDEN RECOMENDADO DE IMPLEMENTACIÓN

### Fase 1: Rutas (1-2 horas)
1. Implementar 5 rutas en profile/routes.py
2. Testing básico de funcionalidad CRUD

### Fase 2: Templates (2-3 horas)
1. Crear mensajes.html
2. Crear mensaje_detalle.html
3. Crear mensaje_form.html
4. Agregar links en base.html

### Fase 3: Mejoras UI (1 hora)
1. Badges de "Nuevo"
2. Estados de lectura visual
3. Integración en dashboard

### Fase 4: Comentarios (1-2 horas)
1. Modificar product_detail.html
2. Agregar estilos para respuestas admin
3. Testing

### Fase 5: Notificaciones (OPCIONAL, 8-10 horas)
1. Si se decide implementar: crear modelo mejorado
2. Rutas y templates
3. Integración con eventos del sistema

---

## COMANDOS DE TEST

```bash
# Test unitario para mensajes
pytest app/tests/test_messages.py

# Test de rutas
pytest app/tests/test_profile_routes.py::test_user_messages

# Test de seguridad
pytest app/tests/test_security.py::test_user_cannot_see_other_messages

# Test de UI
selenium tests/test_messaging_ui.py
```

---

## DOCUMENTACIÓN A ACTUALIZAR

- [ ] README.md: Documentar nuevo sistema de mensajería
- [ ] ENDPOINTS.md: Agregar rutas de usuario
- [ ] USER_GUIDE.md: Cómo usar mensajería y comentarios
- [ ] ADMIN_GUIDE.md: Actualizar guía admin con nuevas funciones

---

## COMMITS RECOMENDADOS

1. "feat: Add user messaging system - routes and models"
2. "feat: Add user messaging templates (mensajes, detalle, form)"
3. "fix: Show admin replies in product comments"
4. "style: Add visual indicators for message status"
5. "docs: Update documentation for messaging system"

---

## BUGS CONOCIDOS A VERIFICAR

- [ ] En admin/messages: ¿Se paginan correctamente?
- [ ] En admin/comments: ¿Se guardan las respuestas correctamente?
- [ ] Timestamps: ¿Usan UTC o timezone local?
- [ ] Validaciones: ¿Se sanitizan inputs para XSS?

---

## NOTAS IMPORTANTES

### Sobre la tabla mensajes:
- Actualmente soporta bidireccionalidad con tipos (admin/user)
- mensaje_padre_id permite conversaciones anidadas
- NO hay archivos adjuntos (si se necesita, hay que agregar)
- NO hay sistema de notificaciones en tiempo real

### Sobre comentarios:
- Ya soportan moderación (pendiente/aprobado/rechazado)
- Validación de compra ya implementada
- La UI solo necesita actualizarse para mostrar respuestas

### Cupones:
- Sistema completamente funcional
- Integración con checkout correcta
- NO necesita cambios

### Wishlist:
- Sistema completamente funcional
- CRUD funciona correctamente
- NO necesita cambios

