# Documentación Técnica - Sistema E-commerce Flask

**Versión:** 2.0
**Fecha:** Noviembre 2025
**Framework:** Flask 3.0+
**Base de Datos:** MySQL 8.0+
**Python:** 3.8+

---

## 📋 Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Modelos de Base de Datos](#modelos-de-base-de-datos)
5. [Blueprints y Rutas](#blueprints-y-rutas)
6. [Sistemas Principales](#sistemas-principales)
7. [Configuración y Deployment](#configuración-y-deployment)
8. [Guía de Desarrollo](#guía-de-desarrollo)
9. [Testing](#testing)
10. [Mantenimiento](#mantenimiento)

---

## 📝 Descripción General

Sistema de comercio electrónico desarrollado en Flask que permite:
- Gestión completa de productos y categorías
- Carrito de compras con sesiones
- Procesamiento de pagos con múltiples pasarelas
- Sistema de usuarios con autenticación
- Panel de administración completo
- Sistema de mensajería bidireccional admin ↔ usuario
- Sistema de comentarios y reseñas con moderación
- Gestión de órdenes y pedidos
- Lista de deseos (wishlist)
- Sistema de cupones y descuentos

---

## 🏗️ Arquitectura del Sistema

### Patrón de Diseño
- **MVC (Model-View-Controller)** implementado a través de blueprints
- **Factory Pattern** para creación de la aplicación Flask
- **Repository Pattern** para acceso a datos (SQLAlchemy ORM)

### Componentes Principales

```
┌─────────────────────────────────────────────────────┐
│                    Cliente Web                       │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│              Flask Application                       │
│  ┌──────────────────────────────────────────────┐  │
│  │            Blueprints Layer                   │  │
│  │  • main  • shop  • cart  • checkout          │  │
│  │  • auth  • profile  • admin                  │  │
│  └──────────────────┬───────────────────────────┘  │
│                     │                                │
│  ┌──────────────────▼───────────────────────────┐  │
│  │         Services Layer                        │  │
│  │  • payment_service  • email_service          │  │
│  └──────────────────┬───────────────────────────┘  │
│                     │                                │
│  ┌──────────────────▼───────────────────────────┐  │
│  │          Models Layer (ORM)                   │  │
│  │  SQLAlchemy Models                           │  │
│  └──────────────────┬───────────────────────────┘  │
└────────────────────┬─┬───────────────────────────┘
                     │ │
            ┌────────▼─▼──────────┐
            │   MySQL Database    │
            └─────────────────────┘
```

### Stack Tecnológico

**Backend:**
- Flask 3.0+ (Framework web)
- SQLAlchemy 2.0+ (ORM)
- Flask-Login (Autenticación)
- Flask-WTF (Formularios y CSRF)
- PyMySQL (Driver MySQL)
- python-dotenv (Configuración)

**Frontend:**
- Bootstrap 5.3 (UI Framework)
- jQuery 3.7 (DOM manipulation)
- Font Awesome 6.4 (Iconos)
- Chart.js 4.4 (Gráficas en admin)
- DataTables (Tablas admin)
- SortableJS (Drag & drop)

**Pasarelas de Pago:**
- PayPal (IPN)
- PayU (América Latina)
- Paymentez (Ecuador)
- Datafast (Ecuador)

---

## 📁 Estructura del Proyecto

```
flask-app/
├── app/
│   ├── __init__.py              # Factory de aplicación Flask
│   ├── config.py                # Configuraciones del sistema
│   ├── extensions.py            # Extensiones Flask (SQLAlchemy, Login, etc)
│   │
│   ├── models/                  # Modelos SQLAlchemy
│   │   ├── user.py              # Usuario (clientes)
│   │   ├── admin.py             # Administradores
│   │   ├── product.py           # Productos
│   │   ├── category.py          # Categorías
│   │   ├── order.py             # Órdenes/Pedidos
│   │   ├── comment.py           # Comentarios/Reseñas
│   │   ├── message.py           # Mensajería interna
│   │   ├── wishlist.py          # Lista de deseos
│   │   ├── cupon.py             # Cupones de descuento
│   │   └── plantilla.py         # Configuración de plantilla
│   │
│   ├── blueprints/              # Blueprints (rutas agrupadas)
│   │   ├── main/                # Páginas principales (home, contacto)
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   │
│   │   ├── shop/                # Tienda (productos, búsqueda)
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   │
│   │   ├── cart/                # Carrito de compras
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   │
│   │   ├── checkout/            # Proceso de compra y webhooks
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   │
│   │   ├── auth/                # Autenticación (login, registro)
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   │
│   │   ├── profile/             # Perfil de usuario
│   │   │   ├── __init__.py
│   │   │   └── routes.py        # Incluye sistema de mensajería
│   │   │
│   │   └── admin/               # Panel administrativo
│   │       ├── __init__.py
│   │       └── routes.py        # ~3400+ líneas, todas las funciones admin
│   │
│   ├── services/                # Lógica de negocio
│   │   ├── payment_service.py   # Procesamiento pagos y webhooks
│   │   └── email_service.py     # Envío de emails
│   │
│   ├── templates/               # Templates Jinja2
│   │   ├── base.html            # Template base (navbar, footer)
│   │   ├── main/                # Templates páginas principales
│   │   ├── shop/                # Templates tienda
│   │   │   └── product_detail.html  # Incluye comentarios con respuestas admin
│   │   ├── cart/                # Templates carrito
│   │   ├── checkout/            # Templates checkout
│   │   ├── auth/                # Templates autenticación
│   │   ├── profile/             # Templates perfil usuario
│   │   │   ├── dashboard.html   # Dashboard con enlace mensajes
│   │   │   ├── mensajes.html    # Bandeja entrada/enviados
│   │   │   ├── mensaje_detalle.html  # Ver conversación
│   │   │   └── mensaje_form.html     # Componer/responder
│   │   └── admin/               # Templates panel admin
│   │       ├── base_admin.html  # Base admin con sidebar
│   │       ├── mensajes.html    # Mensajería admin
│   │       ├── mensaje_detalle.html
│   │       └── mensaje_form.html
│   │
│   └── static/                  # Archivos estáticos
│       ├── css/
│       ├── js/
│       ├── images/
│       └── uploads/             # Imágenes subidas (productos, usuarios)
│
├── migrations/                  # Migraciones de base de datos (Alembic)
├── .env                         # Variables de entorno (NO en git)
├── .env.example                 # Ejemplo de configuración
├── requirements.txt             # Dependencias Python
├── fix_database.py              # Script mantenimiento BD
└── run.py                       # Punto de entrada aplicación
```

---

## 🗄️ Modelos de Base de Datos

### 1. Usuario (users)

**Archivo:** `app/models/user.py`
**Tabla:** `usuarios`

```python
class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.Text)
    foto = db.Column(db.String(255))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    verificado = db.Column(db.Boolean, default=False)
    token_verificacion = db.Column(db.String(100))

    # Relaciones
    orders = db.relationship('Order', backref='usuario', lazy=True)
    comentarios = db.relationship('Comentario', backref='usuario', lazy=True)
    wishlist = db.relationship('Wishlist', backref='usuario', lazy=True)
```

**Métodos importantes:**
- `set_password(password)` - Hash de contraseña con Werkzeug
- `check_password(password)` - Verificar contraseña
- `get_id()` - Requerido por Flask-Login

---

### 2. Administrador (admin)

**Archivo:** `app/models/admin.py`
**Tabla:** `administradores`

```python
class Administrador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(50), default='admin')
    foto = db.Column(db.String(255))
    estado = db.Column(db.Integer, default=1)
    ultimo_acceso = db.Column(db.DateTime)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
```

**Roles disponibles:**
- `superadmin` - Acceso total
- `admin` - Gestión general
- `moderador` - Moderación de contenido

---

### 3. Producto (product)

**Archivo:** `app/models/product.py`
**Tabla:** `productos`

```python
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    precio_oferta = db.Column(db.Float)
    stock = db.Column(db.Integer, default=0)
    imagen = db.Column(db.String(255))
    imagenes_adicionales = db.Column(db.Text)  # JSON string
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id'), index=True)
    ruta = db.Column(db.String(255), unique=True, nullable=False, index=True)  # URL slug
    destacado = db.Column(db.Boolean, default=False)
    oferta = db.Column(db.Boolean, default=False)
    activo = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relaciones
    comentarios = db.relationship('Comentario', backref='producto', lazy=True)
    orders = db.relationship('Order', backref='producto', lazy=True)
```

**Métodos importantes:**
- `get_precio_final()` - Retorna precio con oferta si existe
- `get_descuento_porcentaje()` - Calcula % de descuento
- `tiene_stock()` - Verifica disponibilidad
- `get_imagenes_adicionales()` - Parse JSON de imágenes
- `get_average_rating()` - Promedio de calificaciones
- `get_comments_count()` - Contador de comentarios

---

### 4. Categoría (category)

**Archivo:** `app/models/category.py`
**Tabla:** `categorias`

```python
class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(100), nullable=False)
    ruta = db.Column(db.String(100), unique=True, nullable=False, index=True)
    descripcion = db.Column(db.Text)
    imagen = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)
    padre_id = db.Column(db.Integer, db.ForeignKey('categorias.id'))

    # Relaciones
    productos = db.relationship('Producto', backref='categoria', lazy=True)
    subcategorias = db.relationship('Categoria', backref=db.backref('padre', remote_side=[id]))
```

---

### 5. Orden/Pedido (order)

**Archivo:** `app/models/order.py`
**Tabla:** `orders`

```python
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, default=1)
    pago = db.Column(db.Float, nullable=False)  # Total pagado
    metodo = db.Column(db.String(50))  # paypal, payu, paymentez, datafast
    estado = db.Column(db.String(50), default='pendiente', index=True)
    transaction_id = db.Column(db.String(255))
    payment_details = db.Column(db.Text)  # JSON con detalles del pago
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    # Datos de envío
    nombre_envio = db.Column(db.String(200))
    direccion_envio = db.Column(db.Text)
    ciudad = db.Column(db.String(100))
    codigo_postal = db.Column(db.String(20))
    telefono_envio = db.Column(db.String(20))
```

**Estados posibles:**
- `pendiente` - Esperando pago
- `pagado` - Pago confirmado
- `procesando` - Preparando envío
- `enviado` - En camino
- `entregado` - Completado
- `cancelado` - Cancelado
- `reembolsado` - Devuelto dinero

---

### 6. Comentario (comment) ⭐ NUEVO: Con respuestas admin

**Archivo:** `app/models/comment.py`
**Tabla:** `comentarios`

```python
class Comentario(db.Model):
    # Estados de moderación
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_APROBADO = 'aprobado'
    ESTADO_RECHAZADO = 'rechazado'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False, index=True)
    calificacion = db.Column(db.Float, default=0)  # 1-5 estrellas
    comentario = db.Column(db.Text, nullable=False)
    estado = db.Column(db.String(20), default=ESTADO_APROBADO, index=True)
    respuesta_admin = db.Column(db.Text, nullable=True)  # ⭐ Respuesta del admin
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_moderacion = db.Column(db.DateTime, nullable=True)
```

**Métodos importantes:**
- `get_rating_stars()` - Retorna calificación como int (1-5)
- `aprobar()` - Aprobar comentario
- `rechazar()` - Rechazar comentario
- `es_aprobado()`, `es_pendiente()`, `es_rechazado()` - Check de estado
- `get_estado_badge()` - Clase Bootstrap según estado
- `get_estado_display()` - Texto legible del estado

**⭐ Visualización Frontend:**
- En `shop/product_detail.html` se muestra la `respuesta_admin` debajo de cada comentario
- Diseño destacado con borde azul y ícono de administrador
- Se muestra fecha de moderación si existe

---

### 7. Mensaje (message) ⭐ NUEVO: Sistema de mensajería bidireccional

**Archivo:** `app/models/message.py`
**Tabla:** `mensajes`

```python
class Mensaje(db.Model):
    __tablename__ = 'mensajes'

    id = db.Column(db.Integer, primary_key=True)
    remitente_tipo = db.Column(db.String(20), nullable=False)  # 'admin' o 'user'
    remitente_id = db.Column(db.Integer, nullable=False)
    destinatario_tipo = db.Column(db.String(20), nullable=False)  # 'admin' o 'user'
    destinatario_id = db.Column(db.Integer, nullable=False)
    asunto = db.Column(db.String(255), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    leido = db.Column(db.Boolean, default=False)
    fecha_leido = db.Column(db.DateTime, nullable=True)
    mensaje_padre_id = db.Column(db.Integer, db.ForeignKey('mensajes.id'))  # Threading
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación para threading
    respuestas = db.relationship('Mensaje', backref=db.backref('padre', remote_side=[id]))
```

**Métodos importantes:**
- `marcar_como_leido()` - Marca mensaje como leído
- `get_remitente_nombre()` - Obtiene nombre del remitente (admin o usuario)
- `get_destinatario_nombre()` - Obtiene nombre del destinatario
- `get_remitente_email()` - Email del remitente
- `contar_no_leidos(tipo, id)` - **ESTÁTICO:** Cuenta mensajes no leídos
- `enviar_mensaje(...)` - **ESTÁTICO:** Crea y guarda nuevo mensaje

**Flujo de mensajes:**
```
Admin → Usuario:  remitente_tipo='admin', destinatario_tipo='user'
Usuario → Admin:  remitente_tipo='user', destinatario_tipo='admin'
```

**Threading:**
- Mensajes con `mensaje_padre_id` son respuestas
- Se muestran en conversación completa
- Asunto se hereda del mensaje padre

---

### 8. Wishlist (lista de deseos)

**Archivo:** `app/models/wishlist.py`
**Tabla:** `wishlist`

```python
class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False, index=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
```

---

### 9. Cupón (coupon)

**Archivo:** `app/models/cupon.py`
**Tabla:** `cupones`

```python
class Cupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    descuento = db.Column(db.Float, nullable=False)  # Porcentaje
    tipo = db.Column(db.String(20), default='porcentaje')  # o 'fijo'
    minimo_compra = db.Column(db.Float, default=0)
    maximo_usos = db.Column(db.Integer)
    usos_actuales = db.Column(db.Integer, default=0)
    fecha_inicio = db.Column(db.DateTime)
    fecha_expiracion = db.Column(db.DateTime)
    activo = db.Column(db.Boolean, default=True)
```

**Métodos:**
- `is_valid()` - Verifica si cupón es válido
- `aplicar_descuento(monto)` - Calcula descuento
- `incrementar_uso()` - Aumenta contador de usos

---

### 10. Plantilla (template settings)

**Archivo:** `app/models/plantilla.py`
**Tabla:** `plantilla`

```python
class Plantilla(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_tienda = db.Column(db.String(200))
    logo = db.Column(db.String(255))
    color_primario = db.Column(db.String(7))
    color_secundario = db.Column(db.String(7))
    meta_titulo = db.Column(db.String(200))
    meta_descripcion = db.Column(db.Text)
    meta_keywords = db.Column(db.Text)
    email_contacto = db.Column(db.String(100))
    telefono_contacto = db.Column(db.String(20))
    direccion = db.Column(db.Text)
    facebook = db.Column(db.String(255))
    instagram = db.Column(db.String(255))
    twitter = db.Column(db.String(255))
    whatsapp = db.Column(db.String(20))
```

---

## 🛣️ Blueprints y Rutas

### Blueprint: Main

**Archivo:** `app/blueprints/main/routes.py`
**Prefijo:** `/`

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/` | GET | Página de inicio |
| `/contacto` | GET, POST | Formulario de contacto |
| `/sobre-nosotros` | GET | Página sobre nosotros |
| `/terminos` | GET | Términos y condiciones |
| `/privacidad` | GET | Política de privacidad |

---

### Blueprint: Shop

**Archivo:** `app/blueprints/shop/routes.py`
**Prefijo:** `/tienda`

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/tienda` | GET | Listado de productos (con filtros) |
| `/tienda/<ruta>` | GET | Productos por categoría |
| `/producto/<ruta>` | GET | Detalle de producto + comentarios |
| `/producto/<ruta>/comentar` | POST | Agregar comentario/reseña |
| `/buscar` | GET | Búsqueda de productos |
| `/ofertas` | GET | Productos en oferta |

**Parámetros de filtro (tienda):**
- `categoria` - ID de categoría
- `orden` - `precio_asc`, `precio_desc`, `nombre`, `nuevos`, `populares`
- `min_precio`, `max_precio` - Rango de precios
- `destacados` - Solo productos destacados

---

### Blueprint: Cart

**Archivo:** `app/blueprints/cart/routes.py`
**Prefijo:** `/carrito`

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/carrito` | GET | Ver carrito |
| `/carrito/agregar` | POST | Agregar producto al carrito |
| `/carrito/actualizar/<int:id>` | POST | Actualizar cantidad |
| `/carrito/eliminar/<int:id>` | POST | Eliminar del carrito |
| `/carrito/vaciar` | POST | Vaciar carrito completo |
| `/carrito/aplicar-cupon` | POST | Aplicar cupón de descuento |

**Estructura de sesión:**
```python
session['cart'] = {
    'producto_id': {
        'cantidad': int,
        'precio': float,
        'nombre': str,
        'imagen': str
    }
}
session['cupon'] = {
    'codigo': str,
    'descuento': float
}
```

---

### Blueprint: Checkout

**Archivo:** `app/blueprints/checkout/routes.py`
**Prefijo:** `/checkout`

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/checkout` | GET, POST | Proceso de compra |
| `/checkout/paypal` | POST | Iniciar pago PayPal |
| `/checkout/payu` | POST | Iniciar pago PayU |
| `/checkout/paymentez` | POST | Iniciar pago Paymentez |
| `/checkout/datafast` | POST | Iniciar pago Datafast |
| `/checkout/success` | GET | Página de éxito |
| `/checkout/error` | GET | Página de error |
| `/webhook/paypal` | POST | IPN de PayPal ⚠️ |
| `/webhook/payu/confirmation` | POST | Webhook PayU ⚠️ |
| `/webhook/payu/response` | GET, POST | Respuesta PayU |
| `/webhook/paymentez` | POST | Webhook Paymentez ⚠️ |
| `/webhook/datafast` | GET, POST | Callback Datafast ⚠️ |

**⚠️ IMPORTANTE - Webhooks:**
- Los webhooks son llamados directamente por las pasarelas de pago
- NO requieren autenticación de usuario
- DEBEN validar firma/signature para seguridad
- Se procesan en background y actualizan estado de órdenes
- Ver sección [Sistema de Pagos](#sistema-de-pagos) para detalles

---

### Blueprint: Auth

**Archivo:** `app/blueprints/auth/routes.py`
**Prefijo:** `/auth`

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/login` | GET, POST | Inicio de sesión usuario |
| `/register` | GET, POST | Registro de usuario |
| `/logout` | GET | Cerrar sesión |
| `/forgot-password` | GET, POST | Recuperar contraseña |
| `/reset-password/<token>` | GET, POST | Resetear contraseña |
| `/verify-email/<token>` | GET | Verificar email |

---

### Blueprint: Profile ⭐ INCLUYE MENSAJERÍA

**Archivo:** `app/blueprints/profile/routes.py`
**Prefijo:** `/perfil`

| Ruta | Método | Descripción | Auth |
|------|--------|-------------|------|
| `/perfil` | GET | Dashboard de usuario | ✓ |
| `/perfil/editar` | GET, POST | Editar perfil | ✓ |
| `/perfil/cambiar-password` | POST | Cambiar contraseña | ✓ |
| `/perfil/compras` | GET | Historial de compras | ✓ |
| `/perfil/compra/<int:id>` | GET | Detalle de orden | ✓ |
| `/perfil/wishlist` | GET | Lista de deseos | ✓ |
| `/perfil/wishlist/agregar/<int:id>` | POST | Agregar a wishlist | ✓ |
| `/perfil/wishlist/eliminar/<int:id>` | POST | Quitar de wishlist | ✓ |
| **⭐ `/perfil/mensajes`** | GET | **Bandeja entrada mensajes** | ✓ |
| **⭐ `/perfil/mensajes/enviados`** | GET | **Mensajes enviados** | ✓ |
| **⭐ `/perfil/mensajes/nuevo`** | GET, POST | **Nuevo mensaje a admin** | ✓ |
| **⭐ `/perfil/mensajes/<int:id>`** | GET | **Ver mensaje + conversación** | ✓ |
| **⭐ `/perfil/mensajes/<int:id>/responder`** | GET, POST | **Responder mensaje** | ✓ |
| **⭐ `/perfil/mensajes/<int:id>/eliminar`** | POST | **Eliminar mensaje** | ✓ |

**⭐ Sistema de Mensajería - Detalles:**

**Ubicaciones de acceso para usuarios:**
1. Navbar → Dropdown usuario → "Mensajes" (badge si hay no leídos)
2. Dashboard → Sidebar → "Mensajes" (badge si hay no leídos)
3. Dashboard → Card "Mensajes" (muestra contador)

**Flujo de mensajes usuario:**
```
1. Usuario click "Mensajes" → /perfil/mensajes
2. Ve lista recibidos/enviados en tabs
3. Click mensaje → /perfil/mensajes/123
4. Ve conversación completa (threading)
5. Puede responder con form rápido
6. Mensaje se marca como leído automáticamente
```

**Templates:**
- `profile/mensajes.html` - Lista recibidos/enviados
- `profile/mensaje_detalle.html` - Ver conversación
- `profile/mensaje_form.html` - Componer/responder

---

### Blueprint: Admin

**Archivo:** `app/blueprints/admin/routes.py`
**Prefijo:** `/admin`
**Líneas:** ~3400+ (archivo muy grande)

#### Autenticación Admin

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/admin/login` | GET, POST | Login panel admin |
| `/admin/logout` | GET | Logout admin |

#### Dashboard y Estadísticas

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/admin` | GET | Dashboard principal |
| `/admin/dashboard` | GET | Dashboard con gráficas |
| `/admin/estadisticas` | GET | Estadísticas detalladas |
| `/admin/reportes` | GET | Generación de reportes |

#### Gestión de Productos

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/admin/productos` | GET | Lista de productos |
| `/admin/productos/nuevo` | GET, POST | Crear producto |
| `/admin/productos/<int:id>/editar` | GET, POST | Editar producto |
| `/admin/productos/<int:id>/eliminar` | POST | Eliminar producto |
| `/admin/productos/ordenar` | POST | Reordenar productos (drag&drop) |
| `/admin/productos/<int:id>/imagenes` | POST | Gestionar imágenes adicionales |

#### Gestión de Categorías

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/admin/categorias` | GET | Lista de categorías |
| `/admin/categorias/nueva` | GET, POST | Crear categoría |
| `/admin/categorias/<int:id>/editar` | GET, POST | Editar categoría |
| `/admin/categorias/<int:id>/eliminar` | POST | Eliminar categoría |
| `/admin/categorias/ordenar` | POST | Reordenar categorías |

#### Gestión de Órdenes

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/admin/orders` | GET | Lista de órdenes (DataTables) |
| `/admin/orders-ajax` | GET | Datos AJAX para DataTables |
| `/admin/orders/<int:id>` | GET | Detalle de orden |
| `/admin/orders/<int:id>/estado` | POST | Cambiar estado orden |
| `/admin/orders/<int:id>/factura` | GET | Generar factura PDF |

#### Gestión de Usuarios

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/admin/usuarios` | GET | Lista de usuarios |
| `/admin/usuarios/<int:id>` | GET | Detalle de usuario |
| `/admin/usuarios/<int:id>/editar` | POST | Editar usuario |
| `/admin/usuarios/<int:id>/bloquear` | POST | Bloquear/Desbloquear |
| `/admin/usuarios/<int:id>/eliminar` | POST | Eliminar usuario |

#### Gestión de Comentarios/Reseñas

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/admin/comentarios` | GET | Lista comentarios pendientes |
| `/admin/comentarios/<int:id>/aprobar` | POST | Aprobar comentario |
| `/admin/comentarios/<int:id>/rechazar` | POST | Rechazar comentario |
| `/admin/comentarios/<int:id>/responder` | POST | Responder comentario ⭐ |
| `/admin/comentarios/<int:id>/eliminar` | POST | Eliminar comentario |

**⭐ Responder Comentarios:**
- Admin puede responder desde `/admin/comentarios`
- La respuesta se guarda en `comentarios.respuesta_admin`
- Se muestra en `shop/product_detail.html` debajo del comentario original
- Diseño destacado con borde azul y ícono de administrador

#### Sistema de Mensajería Admin

| Ruta | Método | Descripción |
|------|--------|-------------|
| **`/admin/mensajes`** | GET | Bandeja entrada admin |
| **`/admin/mensajes/enviados`** | GET | Mensajes enviados por admin |
| **`/admin/mensajes/nuevo`** | GET, POST | Nuevo mensaje a usuario |
| **`/admin/mensajes/<int:id>`** | GET | Ver mensaje + conversación |
| **`/admin/mensajes/<int:id>/responder`** | GET, POST | Responder mensaje |
| **`/admin/mensajes/<int:id>/eliminar`** | POST | Eliminar mensaje |
| **`/admin/mensajes/<int:id>/marcar-leido`** | POST | Marcar como leído (AJAX) |

**Templates admin:**
- `admin/mensajes.html` - Lista recibidos/enviados
- `admin/mensaje_detalle.html` - Ver conversación
- `admin/mensaje_form.html` - Componer/responder

**Ubicación en admin:**
- Sidebar admin → "Mensajes" (con badge de no leídos)

#### Gestión de Cupones

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/admin/cupones` | GET | Lista de cupones |
| `/admin/cupones/nuevo` | GET, POST | Crear cupón |
| `/admin/cupones/<int:id>/editar` | GET, POST | Editar cupón |
| `/admin/cupones/<int:id>/eliminar` | POST | Eliminar cupón |

#### Gestión de Administradores

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/admin/administradores` | GET | Lista de admins |
| `/admin/administradores/nuevo` | GET, POST | Crear admin |
| `/admin/administradores/<int:id>/editar` | POST | Editar admin |
| `/admin/administradores/<int:id>/eliminar` | POST | Eliminar admin |

#### Configuración

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/admin/plantilla` | GET, POST | Configurar plantilla/SEO |
| `/admin/configuracion` | GET, POST | Configuración general |

---

## 🔧 Sistemas Principales

### Sistema de Pagos

**Archivo:** `app/services/payment_service.py`

#### Pasarelas Implementadas

**1. PayPal (IPN - Instant Payment Notification)**

```python
def process_paypal_ipn(ipn_data):
    """
    Procesa notificaciones IPN de PayPal

    Flujo:
    1. Recibe POST de PayPal en /webhook/paypal
    2. Valida IPN reenviando a PayPal (validate_paypal_ipn)
    3. Verifica payment_status
    4. Actualiza orden en base de datos
    5. Envía email al cliente
    """
```

**Estados PayPal:**
- `Completed` → orden a `pagado`
- `Pending` → orden a `pendiente`
- `Refunded` → orden a `reembolsado`
- `Reversed` → orden a `cancelado`
- `Canceled_Reversal` → orden a `pagado`
- `Denied`, `Failed` → orden a `fallido`

**Configuración (.env):**
```
PAYPAL_CLIENT_ID=tu_client_id
PAYPAL_CLIENT_SECRET=tu_secret
PAYPAL_MODE=sandbox  # o 'live'
```

---

**2. PayU (América Latina)**

```python
def process_payu_payment(order_data):
    """
    Genera formulario auto-submit para PayU

    Firma MD5: api_key~merchant_id~reference~amount~currency
    """

def process_payu_confirmation(data):
    """
    Webhook de confirmación de PayU
    Valida firma MD5
    """
```

**Flujo PayU:**
1. Usuario confirma compra → genera formulario con firma
2. Formulario se auto-envía a PayU (JavaScript 3 segundos)
3. Usuario paga en PayU
4. PayU envía POST a `/webhook/payu/confirmation` (servidor)
5. PayU redirige usuario a `/webhook/payu/response` (navegador)
6. Se valida firma MD5 en ambos endpoints

**Configuración (.env):**
```
PAYU_API_KEY=tu_api_key
PAYU_MERCHANT_ID=tu_merchant_id
PAYU_ACCOUNT_ID=tu_account_id
PAYU_MODE=sandbox  # o 'production'
```

**Template:** `checkout/payu.html` - Auto-submit form

---

**3. Paymentez (Ecuador, Perú, México)**

```python
def process_paymentez_webhook(data):
    """
    Procesa webhook JSON de Paymentez
    Valida HMAC-SHA256 (opcional)
    """
```

**Estados Paymentez:**
- `success` → orden a `pagado`
- `pending` → orden a `pendiente`
- `failure` → orden a `fallido`

**Configuración (.env):**
```
PAYMENTEZ_CLIENT_APP_CODE=tu_app_code
PAYMENTEZ_CLIENT_APP_KEY=tu_app_key
PAYMENTEZ_MODE=sandbox  # o 'production'
```

---

**4. Datafast (Ecuador)**

```python
def process_datafast_callback(data):
    """
    Procesa callback GET/POST de Datafast
    Valida códigos de respuesta
    """
```

**Códigos Datafast:**
- `00` → Aprobada
- `01` → Rechazada
- `05` → No autorizada
- `12` → Transacción inválida
- etc.

**Configuración (.env):**
```
DATAFAST_MID=tu_merchant_id
DATAFAST_TID=tu_terminal_id
DATAFAST_MODE=sandbox  # o 'production'
```

---

#### ⚠️ Seguridad en Webhooks

**IMPORTANTE:** Los webhooks DEBEN validar:

1. **Firma/Signature:**
   - PayPal: Reenviar a PayPal para validación
   - PayU: Validar MD5 signature
   - Paymentez: Validar HMAC-SHA256 (opcional pero recomendado)
   - Datafast: Validar códigos de respuesta

2. **IP Whitelisting (Recomendado):**
```python
ALLOWED_IPS = {
    'paypal': ['173.0.82.0/24', '173.0.83.0/24'],
    'payu': ['IP de PayU'],
    # etc.
}

if request.remote_addr not in ALLOWED_IPS[gateway]:
    return "Forbidden", 403
```

3. **Logging:**
```python
# Registrar todos los webhooks recibidos
logger.info(f"Webhook {gateway}: {request.data}")
```

4. **Idempotencia:**
```python
# Verificar que orden no haya sido procesada antes
if order.estado == 'pagado':
    return "Already processed", 200
```

---

### Sistema de Autenticación

**Flask-Login** para usuarios y **sesiones** para admin.

#### Usuarios (Flask-Login)

```python
from flask_login import login_user, logout_user, login_required, current_user

# Login
user = Usuario.query.filter_by(email=email).first()
if user and user.check_password(password):
    login_user(user, remember=True)

# Decorador para rutas protegidas
@profile_bp.route('/perfil')
@login_required
def dashboard():
    # current_user disponible automáticamente
    return render_template('profile/dashboard.html')
```

#### Admin (Sesiones)

```python
from flask import session

# Login admin
if admin and admin.check_password(password):
    session['admin_id'] = admin.id
    session['admin_nombre'] = admin.nombre
    session['admin_rol'] = admin.rol

# Decorador personalizado
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function
```

---

### Sistema de Carrito

**Almacenamiento:** Session de Flask

```python
# Estructura session['cart']
{
    '123': {  # producto_id
        'cantidad': 2,
        'precio': 29.99,
        'nombre': 'Producto X',
        'imagen': '/static/uploads/producto.jpg'
    },
    '456': { ... }
}

# Agregar al carrito
cart = session.get('cart', {})
cart[str(producto_id)] = {
    'cantidad': cantidad,
    'precio': producto.get_precio_final(),
    'nombre': producto.titulo,
    'imagen': producto.imagen
}
session['cart'] = cart

# Calcular total
total = sum(item['cantidad'] * item['precio'] for item in cart.values())

# Aplicar cupón
if session.get('cupon'):
    descuento = session['cupon']['descuento']
    total = total * (1 - descuento / 100)
```

---

### Sistema de Emails

**Archivo:** `app/services/email_service.py`

```python
def send_email(to, subject, template, **kwargs):
    """
    Envía email usando plantillas HTML

    Parámetros:
    - to: email destinatario
    - subject: asunto
    - template: nombre del template (sin extensión)
    - **kwargs: variables para el template

    Templates en: app/templates/emails/
    """
```

**Templates de email:**
- `emails/welcome.html` - Bienvenida nuevo usuario
- `emails/order_confirmation.html` - Confirmación de orden
- `emails/order_shipped.html` - Orden enviada
- `emails/password_reset.html` - Resetear contraseña
- `emails/contact_form.html` - Formulario contacto

**Configuración SMTP (.env):**
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_password_app
```

---

### Sistema de Archivos (Uploads)

**Ubicación:** `app/static/uploads/`

**Categorías:**
- `productos/` - Imágenes de productos
- `usuarios/` - Fotos de perfil
- `categorias/` - Imágenes de categorías
- `administradores/` - Fotos de admins

**Función auxiliar:**
```python
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload(file, folder):
    """
    Guarda archivo con nombre seguro

    Returns: ruta relativa para guardar en BD
    """
    filename = secure_filename(file.filename)
    timestamp = int(time.time())
    filename = f"{timestamp}_{filename}"

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], folder, filename)
    file.save(filepath)

    return f"uploads/{folder}/{filename}"
```

---

## ⚙️ Configuración y Deployment

### Variables de Entorno (.env)

```bash
# Flask
FLASK_APP=run.py
FLASK_ENV=production  # o 'development'
SECRET_KEY=tu_clave_secreta_muy_larga_y_compleja

# Base de Datos
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ecommerce_ec
DB_USER=root
DB_PASSWORD=tu_password

# PayPal
PAYPAL_CLIENT_ID=tu_paypal_client_id
PAYPAL_CLIENT_SECRET=tu_paypal_secret
PAYPAL_MODE=sandbox  # 'sandbox' o 'live'

# PayU
PAYU_API_KEY=tu_payu_api_key
PAYU_MERCHANT_ID=tu_merchant_id
PAYU_ACCOUNT_ID=tu_account_id
PAYU_MODE=sandbox  # 'sandbox' o 'production'

# Paymentez
PAYMENTEZ_CLIENT_APP_CODE=tu_app_code
PAYMENTEZ_CLIENT_APP_KEY=tu_app_key
PAYMENTEZ_MODE=sandbox

# Datafast
DATAFAST_MID=tu_merchant_id
DATAFAST_TID=tu_terminal_id
DATAFAST_MODE=sandbox

# Email (SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_app_password

# App
APP_URL=https://tudominio.com
MAX_CONTENT_LENGTH=16777216  # 16MB max file upload
```

### Instalación

```bash
# 1. Clonar repositorio
git clone <repo_url>
cd Ecommerce_php/flask-app

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar .env
cp .env.example .env
# Editar .env con tus credenciales

# 5. Crear base de datos
mysql -u root -p
CREATE DATABASE ecommerce_ec;
exit

# 6. Ejecutar migraciones (si existen)
flask db upgrade

# O correr script de corrección
python fix_database.py

# 7. Ejecutar aplicación
python run.py
```

### Producción (Gunicorn + Nginx)

**1. Instalar Gunicorn:**
```bash
pip install gunicorn
```

**2. Crear servicio systemd:**
```ini
# /etc/systemd/system/ecommerce.service
[Unit]
Description=E-commerce Flask Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ecommerce/flask-app
Environment="PATH=/var/www/ecommerce/flask-app/venv/bin"
ExecStart=/var/www/ecommerce/flask-app/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/var/www/ecommerce/flask-app/ecommerce.sock \
    --timeout 120 \
    run:app

[Install]
WantedBy=multi-user.target
```

**3. Configurar Nginx:**
```nginx
# /etc/nginx/sites-available/ecommerce
server {
    listen 80;
    server_name tudominio.com;

    location / {
        proxy_pass http://unix:/var/www/ecommerce/flask-app/ecommerce.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/ecommerce/flask-app/app/static;
        expires 30d;
    }

    client_max_body_size 16M;
}
```

**4. Habilitar y iniciar:**
```bash
sudo systemctl enable ecommerce
sudo systemctl start ecommerce
sudo systemctl enable nginx
sudo systemctl restart nginx

# SSL con Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tudominio.com
```

---

## 👨‍💻 Guía de Desarrollo

### Agregar un nuevo Blueprint

```python
# 1. Crear estructura
mkdir app/blueprints/nuevo_modulo
touch app/blueprints/nuevo_modulo/__init__.py
touch app/blueprints/nuevo_modulo/routes.py

# 2. En __init__.py
from flask import Blueprint

nuevo_bp = Blueprint('nuevo', __name__, url_prefix='/nuevo')

from . import routes

# 3. En routes.py
from . import nuevo_bp

@nuevo_bp.route('/')
def index():
    return "Nuevo módulo"

# 4. Registrar en app/__init__.py
from app.blueprints.nuevo_modulo import nuevo_bp
app.register_blueprint(nuevo_bp)
```

### Agregar un nuevo Modelo

```python
# 1. Crear app/models/nuevo_modelo.py
from datetime import datetime
from app.extensions import db

class NuevoModelo(db.Model):
    __tablename__ = 'nuevo_tabla'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<NuevoModelo {self.nombre}>'

# 2. Importar en app/models/__init__.py
from .nuevo_modelo import NuevoModelo

# 3. Crear migración
flask db migrate -m "Agregar NuevoModelo"
flask db upgrade

# O crear tabla manualmente con fix_database.py
```

### Agregar nueva Pasarela de Pago

```python
# 1. En app/services/payment_service.py

def process_nueva_pasarela_payment(order_data):
    """
    Procesa pago con Nueva Pasarela
    """
    # Implementar lógica
    pass

def process_nueva_pasarela_webhook(data):
    """
    Procesa webhook de Nueva Pasarela
    """
    # 1. Validar firma/signature
    # 2. Obtener order por transaction_id
    # 3. Actualizar estado
    # 4. Enviar email
    pass

# 2. En app/blueprints/checkout/routes.py

@checkout_bp.route('/checkout/nueva-pasarela', methods=['POST'])
def nueva_pasarela():
    # Iniciar pago
    return process_nueva_pasarela_payment(order_data)

@checkout_bp.route('/webhook/nueva-pasarela', methods=['POST'])
def nueva_pasarela_webhook():
    data = request.json or request.form.to_dict()
    success, message = process_nueva_pasarela_webhook(data)
    return "OK" if success else "ERROR", 200 if success else 400

# 3. Agregar configuración en .env
NUEVA_PASARELA_API_KEY=...
NUEVA_PASARELA_SECRET=...
```

### Context Processors

Los context processors inyectan variables en TODOS los templates.

```python
# En app/__init__.py

@app.context_processor
def inject_global_vars():
    """Variables disponibles en todos los templates"""
    return {
        'now': datetime.now(),
        'version': '2.0',
        'support_email': 'soporte@tienda.com'
    }
```

**Actual en el sistema:**
```python
@app.context_processor
def inject_data():
    """Inyecta categorías, plantilla y contador de carrito"""
    categorias = Categoria.query.filter_by(activo=True).order_by(Categoria.orden).all()
    plantilla = Plantilla.query.first()
    cart_count = len(session.get('cart', {}))

    return {
        'categorias': categorias,
        'plantilla': plantilla,
        'cart_count': cart_count
    }

@app.context_processor
def inject_admin_data():
    """Inyecta contadores de mensajes no leídos"""
    admin_mensajes_no_leidos = 0
    user_mensajes_no_leidos = 0

    # Lógica de contadores...

    return {
        'admin_mensajes_no_leidos': admin_mensajes_no_leidos,
        'user_mensajes_no_leidos': user_mensajes_no_leidos
    }
```

---

## 🧪 Testing

### Estructura de Tests

```bash
tests/
├── __init__.py
├── conftest.py              # Fixtures pytest
├── test_models.py           # Test modelos
├── test_auth.py             # Test autenticación
├── test_cart.py             # Test carrito
├── test_checkout.py         # Test checkout
├── test_payment_webhooks.py # Test webhooks
└── test_admin.py            # Test panel admin
```

### Ejecutar Tests

```bash
# Instalar pytest
pip install pytest pytest-cov pytest-flask

# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=app tests/

# Test específico
pytest tests/test_cart.py

# Verbose
pytest -v
```

### Ejemplo de Test

```python
# tests/test_cart.py
import pytest
from flask import session

def test_add_to_cart(client, auth):
    # Login
    auth.login()

    # Agregar al carrito
    response = client.post('/carrito/agregar', data={
        'producto_id': 1,
        'cantidad': 2
    })

    assert response.status_code == 302  # Redirect

    with client.session_transaction() as sess:
        assert '1' in sess['cart']
        assert sess['cart']['1']['cantidad'] == 2

def test_apply_coupon(client, auth):
    auth.login()

    # Agregar producto al carrito
    client.post('/carrito/agregar', data={'producto_id': 1, 'cantidad': 1})

    # Aplicar cupón
    response = client.post('/carrito/aplicar-cupon', data={
        'codigo': 'DESCUENTO10'
    })

    with client.session_transaction() as sess:
        assert sess.get('cupon') is not None
        assert sess['cupon']['codigo'] == 'DESCUENTO10'
```

---

## 🔧 Mantenimiento

### Script de Corrección BD

**Archivo:** `fix_database.py`

```bash
# Ejecutar interactivamente
python fix_database.py

# Verificar todas las tablas
# Crear tablas faltantes
# Agregar índices
# Verificar integridad
```

### Backups

**MySQL Dump:**
```bash
# Backup
mysqldump -u root -p ecommerce_ec > backup_$(date +%Y%m%d).sql

# Restore
mysql -u root -p ecommerce_ec < backup_20251119.sql
```

**Backup Automatizado (Cron):**
```bash
# Crear script backup.sh
#!/bin/bash
mysqldump -u root -p"$DB_PASSWORD" ecommerce_ec | gzip > /backups/ecommerce_$(date +%Y%m%d_%H%M%S).sql.gz
find /backups -name "ecommerce_*.sql.gz" -mtime +7 -delete  # Borrar > 7 días

# Agregar a crontab
0 2 * * * /path/to/backup.sh  # 2 AM diario
```

### Logs

**Configurar logging en Flask:**
```python
# app/__init__.py
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/ecommerce.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('E-commerce startup')
```

**Ver logs:**
```bash
tail -f logs/ecommerce.log
```

### Monitoreo

**Endpoints de salud:**
```python
@app.route('/health')
def health():
    try:
        db.session.execute('SELECT 1')
        return jsonify({'status': 'healthy', 'database': 'ok'}), 200
    except:
        return jsonify({'status': 'unhealthy', 'database': 'error'}), 500
```

### Actualizar Dependencias

```bash
# Ver dependencias desactualizadas
pip list --outdated

# Actualizar todas (con cuidado)
pip install -U -r requirements.txt

# Actualizar una específica
pip install -U flask

# Regenerar requirements.txt
pip freeze > requirements.txt
```

---

## 📚 Referencias y Recursos

### Documentación Oficial

- **Flask:** https://flask.palletsprojects.com/
- **SQLAlchemy:** https://docs.sqlalchemy.org/
- **Flask-Login:** https://flask-login.readthedocs.io/
- **Bootstrap 5:** https://getbootstrap.com/docs/5.3/
- **jQuery:** https://api.jquery.com/

### APIs de Pago

- **PayPal IPN:** https://developer.paypal.com/docs/api-basics/notifications/ipn/
- **PayU:** https://developers.paymentsos.com/docs/apis.html
- **Paymentez:** https://paymentez.github.io/api-doc/
- **Datafast:** [Contactar con Datafast para documentación]

### Comandos Útiles

```bash
# Flask shell (consola interactiva)
flask shell
>>> from app.models.user import Usuario
>>> usuarios = Usuario.query.all()

# Crear admin desde shell
>>> from app.models.admin import Administrador
>>> admin = Administrador(nombre='Admin', email='admin@test.com')
>>> admin.set_password('password123')
>>> db.session.add(admin)
>>> db.session.commit()

# Ver rutas registradas
flask routes

# Limpiar cache Python
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

---

## 🎯 Checklist de Desarrollo

### Antes de Deploy

- [ ] Cambiar `FLASK_ENV=production` en `.env`
- [ ] Cambiar `SECRET_KEY` a valor seguro
- [ ] Cambiar modos de pasarelas de `sandbox` a `production`
- [ ] Configurar SMTP real (no Gmail personal)
- [ ] Configurar backups automáticos
- [ ] Configurar SSL (Let's Encrypt)
- [ ] Probar todos los webhooks en producción
- [ ] Configurar logs
- [ ] Habilitar firewall (solo 80, 443, 22)
- [ ] Configurar dominio y DNS
- [ ] Desactivar debug en templates

### Antes de cada Release

- [ ] Ejecutar tests: `pytest`
- [ ] Verificar migraciones: `flask db upgrade`
- [ ] Backup de base de datos
- [ ] Actualizar este documento si hay cambios
- [ ] Crear tag en git: `git tag v2.0.0`
- [ ] Push a producción
- [ ] Verificar logs después de deploy

---

## 📞 Soporte

**Desarrolladores:**
- Email: dev@tuempresa.com
- Slack: #ecommerce-dev
- Repositorio: [URL del repo]

**Documentación actualizada:** Noviembre 2025

---

## 📝 Changelog

### v2.0 (Noviembre 2025)
- ✅ Sistema de mensajería bidireccional admin ↔ usuario
- ✅ Visualización de respuestas admin en comentarios
- ✅ Integración completa PayU con webhooks
- ✅ Webhooks para Paymentez y Datafast
- ✅ Mejoras en sistema de cupones
- ✅ Dashboard mejorado con estadísticas
- ✅ Sistema de moderación de comentarios

### v1.5 (Octubre 2025)
- Sistema de comentarios con calificaciones
- Lista de deseos (wishlist)
- Sistema de cupones
- Panel admin con DataTables

### v1.0 (Septiembre 2025)
- Migración completa de PHP a Flask
- Sistema de autenticación
- Carrito de compras
- Integración PayPal
- Panel administrativo básico

---

**Fin de la documentación técnica.**
