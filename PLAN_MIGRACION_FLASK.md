# Plan de Migración de E-commerce PHP a Flask

## Fecha de Creación
**2025-11-18**

---

## Tabla de Contenidos
1. [Análisis del Sistema Actual](#1-análisis-del-sistema-actual)
2. [Arquitectura Propuesta en Flask](#2-arquitectura-propuesta-en-flask)
3. [Plan de Migración Detallado](#3-plan-de-migración-detallado)
4. [Equivalencias PHP-Flask](#4-equivalencias-php-flask)
5. [Gestión de Dependencias](#5-gestión-de-dependencias)
6. [Estrategia de Testing](#6-estrategia-de-testing)
7. [Deployment y DevOps](#7-deployment-y-devops)
8. [Cronograma Estimado](#8-cronograma-estimado)

---

## 1. Análisis del Sistema Actual

### 1.1 Arquitectura General
- **Framework**: PHP Vanilla (sin framework)
- **Patrón**: MVC personalizado
- **Base de Datos**: MySQL con PDO
- **Servidor Web**: Apache (implícito)
- **Arquitectura**: Monolítica separada en 2 aplicaciones:
  - **Backend**: Panel administrativo (AdminLTE)
  - **Frontend**: Sitio público

### 1.2 Estructura de Archivos

```
Ecommerce_php/
├── backend/
│   ├── ajax/              # 17 archivos AJAX
│   ├── controladores/     # 16 controladores
│   ├── modelos/          # 17 modelos
│   └── vistas/           # Templates AdminLTE
├── frontend/
│   ├── ajax/             # 4 archivos AJAX
│   ├── controladores/    # 7 controladores
│   ├── extensiones/      # PayPal, PHPMailer, Google APIs
│   ├── modelos/         # 10 modelos
│   └── vistas/          # Templates públicos
└── ecommerce.sql         # Schema MySQL
```

### 1.3 Base de Datos (16 Tablas)

#### Tablas Principales
1. **administradores** - Usuarios del panel admin
   - id, nombre, email, foto, password, perfil, estado, fecha

2. **usuarios** - Clientes del ecommerce
   - id, nombre, password, email, modo (directo/facebook/google), foto, verificacion, emailEncriptado, fecha

3. **productos** - Catálogo de productos
   - id, id_categoria, id_subcategoria, tipo (fisico/virtual), ruta, estado, titulo, titular, descripcion
   - multimedia (JSON), detalles (JSON), precio, portada, vistas, ventas
   - oferta, precioOferta, descuentoOferta, imgOferta, finOferta
   - peso, entrega, fecha

4. **categorias** - Categorías de productos
   - id, categoria, ruta, estado, oferta, precioOferta, descuentoOferta, imgOferta, finOferta, fecha

5. **subcategorias** - Subcategorías
   - id, subcategoria, id_categoria, ruta, estado, ofertadoPorCategoria, oferta, precioOferta, descuentoOferta, imgOferta, finOferta, fecha

6. **compras** - Historial de compras
   - id, id_usuario, id_producto, envio, metodo, email, direccion, pais, cantidad, detalle, pago, fecha

7. **comentarios** - Reseñas de productos
   - id, id_usuario, id_producto, calificacion, comentario, fecha

8. **deseos** - Lista de deseos
   - id, id_usuario, id_producto, fecha

9. **comercio** - Configuración de comercio
   - id, impuesto, envioNacional, envioInternacional, tasaMinimaNal, tasaMinimaInt, pais
   - modoPaypal, clienteIdPaypal, llaveSecretaPaypal
   - modoPayu, merchantIdPayu, accountIdPayu, apiKeyPayu

10. **plantilla** - Configuración de diseño
    - id, barraSuperior, textoSuperior, colorFondo, colorTexto, logo, icono
    - redesSociales, apiFacebook, pixelFacebook, googleAnalytics, fecha

11. **slide** - Carrusel principal
    - id, nombre, imgFondo, tipoSlide, imgProducto, estiloImgProducto, estiloTextoSlide
    - titulo1, titulo2, titulo3, boton, url, orden, fecha

12. **banner** - Banners promocionales
    - id, ruta, tipo, img, estado, fecha

13. **cabeceras** - Metadatos SEO
    - id, ruta, titulo, descripcion, palabrasClaves, portada, fecha

14. **notificaciones** - Contadores para admin
    - id, nuevosUsuarios, nuevasVentas, nuevasVisitas

15. **visitaspaises** - Analytics por país
    - id, pais, codigo, cantidad, fecha

16. **visitaspersonas** - Analytics por IP
    - id, ip, pais, visitas, fecha

### 1.4 Funcionalidades Principales

#### Autenticación y Usuarios
- ✅ Registro de usuarios con validación
- ✅ Login tradicional (email/password)
- ✅ Login social (Facebook, Google OAuth)
- ✅ Verificación de email (PHPMailer)
- ✅ Recuperación de contraseña
- ✅ Google reCAPTCHA
- ✅ Gestión de perfiles
- ✅ Subida de fotos de perfil
- ✅ Eliminación de cuentas

#### Catálogo de Productos
- ✅ CRUD completo de productos
- ✅ Categorías y subcategorías multinivel
- ✅ Productos físicos y virtuales
- ✅ Multimedia (múltiples imágenes)
- ✅ Sistema de ofertas y descuentos
- ✅ Ofertas por categoría/subcategoría
- ✅ Gestión de inventario
- ✅ SEO (metadatos, rutas amigables)
- ✅ Tracking de vistas y ventas

#### E-commerce
- ✅ Carrito de compras (localStorage + sesión)
- ✅ Cálculo de impuestos
- ✅ Cálculo de envío (nacional/internacional)
- ✅ Integración PayPal
- ✅ Integración PayU
- ✅ Conversión de divisas (API externa)
- ✅ Validación de precios en servidor
- ✅ Historial de compras
- ✅ Verificación de productos comprados

#### Interacción Social
- ✅ Sistema de comentarios
- ✅ Calificaciones (ratings)
- ✅ Lista de deseos
- ✅ Formulario de contacto

#### Panel Administrativo
- ✅ Dashboard con estadísticas
- ✅ Gestión de administradores
- ✅ Gestión de usuarios
- ✅ Gestión de productos (DataTables)
- ✅ Gestión de categorías/subcategorías
- ✅ Configuración de comercio
- ✅ Gestión de slides
- ✅ Gestión de banners
- ✅ Reportes de ventas
- ✅ Analytics de visitas
- ✅ Notificaciones en tiempo real
- ✅ Editor WYSIWYG (CKEditor)

### 1.5 Integraciones Externas

#### Pasarelas de Pago
- **PayPal REST API SDK** (vendor/paypal/rest-api-sdk-php)
  - Modo sandbox/producción
  - Procesamiento de pagos
  - Webhooks de confirmación

- **PayU** (integración personalizada)
  - merchantId, accountId, apiKey
  - Modo test/live

#### Email
- **PHPMailer**
  - Verificación de cuentas
  - Recuperación de contraseñas
  - Formulario de contacto
  - Notificaciones de compra

#### APIs de Terceros
- **Google OAuth 2.0** (vendor/google/apiclient)
- **Facebook Login SDK**
- **Google reCAPTCHA**
- **Currency Converter API** (free.currconv.com)

#### Frontend Libraries
- jQuery 3.x
- Bootstrap 3.x
- AdminLTE 2.x
- DataTables
- Chart.js
- SweetAlert
- CKEditor
- Ion.RangeSlider
- Morris.js (gráficos)
- FullCalendar
- Select2
- Bootstrap DatePicker/TimePicker/ColorPicker

### 1.6 Flujos Críticos

#### Flujo de Compra
1. Usuario navega catálogo
2. Añade productos al carrito (localStorage)
3. Procede a checkout
4. Selecciona método de pago (PayPal/PayU)
5. Sistema valida precios en servidor
6. Redirige a pasarela de pago
7. Usuario completa pago
8. Webhook/Callback confirma pago
9. Se registra compra en BD
10. Se envía email de confirmación
11. Se actualiza contador de ventas
12. Se crea registro para comentario

#### Flujo de Autenticación
1. Usuario se registra
2. Sistema encripta password (crypt con salt)
3. Se envía email de verificación
4. Usuario hace clic en link
5. Se marca cuenta como verificada
6. Usuario puede iniciar sesión
7. Se valida reCAPTCHA
8. Se crea sesión PHP
9. Redirige a página anterior

### 1.7 Seguridad Actual
- ✅ Passwords hasheados con crypt() y salt
- ✅ Validación de entrada con regex
- ✅ Prepared statements (PDO)
- ✅ Verificación de precios en servidor
- ✅ Hash MD5 para validar totales
- ✅ Google reCAPTCHA
- ⚠️ Sin protección CSRF
- ⚠️ Sin rate limiting
- ⚠️ Sin 2FA
- ⚠️ Sin auditoría de seguridad

---

## 2. Arquitectura Propuesta en Flask

### 2.1 Stack Tecnológico

#### Backend
- **Framework**: Flask 3.x
- **ORM**: SQLAlchemy (Flask-SQLAlchemy)
- **Migraciones**: Flask-Migrate (Alembic)
- **Autenticación**: Flask-Login
- **Formularios**: Flask-WTF
- **API REST**: Flask-RESTful o Flask-RESTX
- **Tareas Asíncronas**: Celery + Redis
- **Cache**: Flask-Caching (Redis)
- **Email**: Flask-Mail
- **Admin**: Flask-Admin
- **CORS**: Flask-CORS
- **Validación**: Marshmallow
- **OAuth**: Authlib
- **Seguridad**: Flask-Talisman, Flask-Limiter

#### Base de Datos
- **Producción**: PostgreSQL 15+ (recomendado) o MySQL 8+
- **Desarrollo**: SQLite

#### Frontend
- **Templates**: Jinja2 (integrado en Flask)
- **CSS Framework**: Bootstrap 5.x
- **Admin Panel**: Flask-Admin o AdminLTE con Jinja2
- **JavaScript**:
  - Alpine.js o Vue.js 3 (modo ligero)
  - Axios para AJAX
  - Chart.js para gráficos

#### DevOps
- **Containerización**: Docker + Docker Compose
- **WSGI Server**: Gunicorn
- **Reverse Proxy**: Nginx
- **Variables de Entorno**: python-dotenv
- **Testing**: pytest, pytest-flask
- **Linting**: flake8, black
- **CI/CD**: GitHub Actions

### 2.2 Estructura de Proyecto Flask

```
ecommerce-flask/
├── .env                          # Variables de entorno
├── .env.example                  # Ejemplo de configuración
├── .gitignore
├── requirements.txt              # Dependencias Python
├── requirements-dev.txt          # Dependencias de desarrollo
├── docker-compose.yml
├── Dockerfile
├── README.md
├── CHANGELOG.md
├── pytest.ini
├── setup.py
│
├── migrations/                   # Migraciones Alembic
│   └── versions/
│
├── tests/                        # Tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_products.py
│   ├── test_cart.py
│   └── test_payments.py
│
├── app/                          # Aplicación principal
│   ├── __init__.py              # Factory pattern
│   ├── config.py                # Configuración
│   ├── extensions.py            # Inicialización de extensiones
│   ├── cli.py                   # Comandos CLI
│   │
│   ├── models/                  # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── admin.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── order.py
│   │   ├── comment.py
│   │   ├── wishlist.py
│   │   ├── visit.py
│   │   └── setting.py
│   │
│   ├── schemas/                 # Schemas Marshmallow
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   └── order.py
│   │
│   ├── forms/                   # Formularios WTForms
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── product.py
│   │   └── profile.py
│   │
│   ├── blueprints/              # Blueprints (módulos)
│   │   │
│   │   ├── main/               # Frontend público
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── utils.py
│   │   │
│   │   ├── auth/               # Autenticación
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── oauth.py
│   │   │   └── utils.py
│   │   │
│   │   ├── shop/               # Catálogo y productos
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── utils.py
│   │   │
│   │   ├── cart/               # Carrito de compras
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── utils.py
│   │   │
│   │   ├── checkout/           # Proceso de pago
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── paypal.py
│   │   │   └── payu.py
│   │   │
│   │   ├── profile/            # Perfil de usuario
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   │
│   │   ├── admin/              # Panel administrativo
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── products.py
│   │   │   ├── users.py
│   │   │   ├── orders.py
│   │   │   └── analytics.py
│   │   │
│   │   └── api/                # API REST (opcional)
│   │       ├── __init__.py
│   │       ├── v1/
│   │       │   ├── __init__.py
│   │       │   ├── products.py
│   │       │   ├── cart.py
│   │       │   └── auth.py
│   │       └── decorators.py
│   │
│   ├── services/               # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── email_service.py
│   │   ├── payment_service.py
│   │   ├── storage_service.py
│   │   ├── currency_service.py
│   │   └── analytics_service.py
│   │
│   ├── tasks/                  # Tareas Celery
│   │   ├── __init__.py
│   │   ├── email_tasks.py
│   │   └── analytics_tasks.py
│   │
│   ├── utils/                  # Utilidades
│   │   ├── __init__.py
│   │   ├── decorators.py
│   │   ├── validators.py
│   │   ├── helpers.py
│   │   └── security.py
│   │
│   ├── templates/              # Templates Jinja2
│   │   ├── base.html
│   │   ├── errors/
│   │   │   ├── 404.html
│   │   │   └── 500.html
│   │   ├── main/
│   │   │   ├── index.html
│   │   │   ├── about.html
│   │   │   └── contact.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   └── reset_password.html
│   │   ├── shop/
│   │   │   ├── products.html
│   │   │   ├── product_detail.html
│   │   │   └── search.html
│   │   ├── cart/
│   │   │   ├── cart.html
│   │   │   └── checkout.html
│   │   ├── profile/
│   │   │   ├── dashboard.html
│   │   │   ├── orders.html
│   │   │   └── wishlist.html
│   │   ├── admin/
│   │   │   ├── base.html
│   │   │   ├── dashboard.html
│   │   │   ├── products/
│   │   │   ├── users/
│   │   │   └── settings/
│   │   └── emails/
│   │       ├── verification.html
│   │       ├── reset_password.html
│   │       └── order_confirmation.html
│   │
│   └── static/                 # Archivos estáticos
│       ├── css/
│       │   ├── style.css
│       │   └── admin.css
│       ├── js/
│       │   ├── main.js
│       │   ├── cart.js
│       │   └── admin.js
│       ├── img/
│       │   ├── products/
│       │   ├── categories/
│       │   ├── users/
│       │   └── banners/
│       └── uploads/
│
└── run.py                      # Punto de entrada
```

### 2.3 Modelos SQLAlchemy (Principales)

```python
# app/models/user.py
from app.extensions import db, bcrypt
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255))
    foto = db.Column(db.String(255))
    modo = db.Column(db.String(20), default='directo')  # directo, facebook, google
    verificacion = db.Column(db.Integer, default=1)  # 0=verificado, 1=pendiente
    email_encriptado = db.Column(db.String(255))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    compras = db.relationship('Compra', backref='usuario', lazy='dynamic')
    comentarios = db.relationship('Comentario', backref='usuario', lazy='dynamic')
    deseos = db.relationship('Deseo', backref='usuario', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
```

```python
# app/models/product.py
class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    id_subcategoria = db.Column(db.Integer, db.ForeignKey('subcategorias.id'))
    tipo = db.Column(db.String(20))  # fisico, virtual
    ruta = db.Column(db.String(255), unique=True, index=True)
    estado = db.Column(db.Integer, default=1)
    titulo = db.Column(db.String(255), nullable=False)
    titular = db.Column(db.Text)
    descripcion = db.Column(db.Text)
    multimedia = db.Column(db.JSON)  # Lista de imágenes
    detalles = db.Column(db.JSON)  # Características del producto
    precio = db.Column(db.Float, nullable=False)
    portada = db.Column(db.String(255))
    vistas = db.Column(db.Integer, default=0)
    ventas = db.Column(db.Integer, default=0)
    oferta = db.Column(db.Integer, default=0)
    precio_oferta = db.Column(db.Float)
    descuento_oferta = db.Column(db.Integer)
    img_oferta = db.Column(db.String(255))
    fin_oferta = db.Column(db.DateTime)
    peso = db.Column(db.Float)
    entrega = db.Column(db.Float)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    categoria = db.relationship('Categoria', backref='productos')
    comentarios = db.relationship('Comentario', backref='producto', lazy='dynamic')
```

### 2.4 Configuración de la Aplicación

```python
# app/config.py
import os
from datetime import timedelta

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/ecommerce'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # PayPal
    PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'sandbox')
    PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
    PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET')

    # Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

    # reCAPTCHA
    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')

    # Upload
    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # Cache
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    # Celery
    CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

---

## 3. Plan de Migración Detallado

### 3.1 Enfoque de Migración

**Opción Recomendada: Migración Incremental (Strangler Pattern)**

1. **Fase 1**: Setup inicial y migración de datos
2. **Fase 2**: API REST para funcionalidades core
3. **Fase 3**: Migración del frontend público
4. **Fase 4**: Migración del panel administrativo
5. **Fase 5**: Testing exhaustivo
6. **Fase 6**: Despliegue progresivo

### 3.2 Fase 1: Setup Inicial (Semana 1-2)

#### 1.1 Preparación del Entorno

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias base
pip install flask flask-sqlalchemy flask-migrate flask-login
pip install flask-wtf flask-mail flask-cors flask-admin
pip install python-dotenv psycopg2-binary pymysql
pip install paypalrestsdk authlib redis celery
pip install pytest pytest-flask pytest-cov
```

#### 1.2 Crear Estructura del Proyecto

```bash
mkdir ecommerce-flask
cd ecommerce-flask

# Crear estructura de carpetas
mkdir -p app/{models,schemas,forms,blueprints,services,tasks,utils,templates,static}
mkdir -p app/blueprints/{main,auth,shop,cart,checkout,profile,admin,api}
mkdir -p tests migrations
```

#### 1.3 Inicializar Git

```bash
git init
echo "venv/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".env" >> .gitignore
echo "instance/" >> .gitignore
git add .
git commit -m "Initial Flask project structure"
```

#### 1.4 Migración de Base de Datos

**Paso 1: Análisis del Schema MySQL**

```bash
# Exportar solo estructura (sin datos)
mysqldump -u user -p --no-data ecommerce > schema_only.sql

# Exportar datos
mysqldump -u user -p --no-create-info ecommerce > data_only.sql
```

**Paso 2: Crear Modelos SQLAlchemy**

Convertir las 16 tablas a modelos Python (ver sección 2.3)

**Paso 3: Inicializar Migraciones**

```bash
flask db init
flask db migrate -m "Initial migration from PHP"
flask db upgrade
```

**Paso 4: Migrar Datos**

```python
# scripts/migrate_data.py
import MySQLdb
from app import create_app, db
from app.models import User, Product, Category, Order

def migrate_users():
    # Conectar a MySQL antiguo
    mysql_conn = MySQLdb.connect(
        host="localhost",
        user="user",
        passwd="pass",
        db="ecommerce"
    )
    cursor = mysql_conn.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("SELECT * FROM usuarios")
    users = cursor.fetchall()

    for user_data in users:
        user = User(
            id=user_data['id'],
            nombre=user_data['nombre'],
            email=user_data['email'],
            password_hash=user_data['password'],  # Mantener hash original
            foto=user_data['foto'],
            modo=user_data['modo'],
            verificacion=user_data['verificacion'],
            email_encriptado=user_data['emailEncriptado'],
            fecha=user_data['fecha']
        )
        db.session.add(user)

    db.session.commit()
    cursor.close()
    mysql_conn.close()

# Similar para otras tablas...
```

### 3.3 Fase 2: Autenticación y Usuarios (Semana 3-4)

#### 2.1 Implementar Sistema de Autenticación

```python
# app/blueprints/auth/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.forms.auth import LoginForm, RegisterForm
from app.models.user import User
from app.services.email_service import send_verification_email
from app.extensions import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            nombre=form.nombre.data,
            email=form.email.data,
            modo='directo'
        )
        user.set_password(form.password.data)

        # Generar token de verificación
        token = user.generate_verification_token()

        db.session.add(user)
        db.session.commit()

        # Enviar email de verificación (async con Celery)
        send_verification_email.delay(user.email, token)

        flash('Por favor revise su email para verificar su cuenta.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Email o contraseña incorrectos', 'error')
            return redirect(url_for('auth.login'))

        if user.verificacion == 1:
            flash('Debe verificar su email antes de iniciar sesión', 'warning')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.index'))

    return render_template('auth/login.html', form=form)
```

#### 2.2 OAuth Social Login

```python
# app/blueprints/auth/oauth.py
from authlib.integrations.flask_client import OAuth
from app.extensions import oauth

google = oauth.register(
    name='google',
    client_id=current_app.config['GOOGLE_CLIENT_ID'],
    client_secret=current_app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@auth_bp.route('/login/google')
def google_login():
    redirect_uri = url_for('auth.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/login/google/callback')
def google_callback():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')

    # Buscar o crear usuario
    user = User.query.filter_by(email=user_info['email']).first()
    if not user:
        user = User(
            nombre=user_info['name'],
            email=user_info['email'],
            foto=user_info.get('picture'),
            modo='google',
            verificacion=0  # Ya verificado por Google
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for('main.index'))
```

### 3.4 Fase 3: Catálogo de Productos (Semana 5-6)

#### 3.1 Rutas de Productos

```python
# app/blueprints/shop/routes.py
from flask import Blueprint, render_template, request, abort
from app.models.product import Producto
from app.models.category import Categoria
from sqlalchemy import or_

shop_bp = Blueprint('shop', __name__, url_prefix='/tienda')

@shop_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    categoria = request.args.get('categoria')

    query = Producto.query.filter_by(estado=1)

    if categoria:
        query = query.filter_by(id_categoria=categoria)

    productos = query.paginate(page=page, per_page=12)
    categorias = Categoria.query.filter_by(estado=1).all()

    return render_template('shop/products.html',
                         productos=productos,
                         categorias=categorias)

@shop_bp.route('/producto/<ruta>')
def product_detail(ruta):
    producto = Producto.query.filter_by(ruta=ruta, estado=1).first_or_404()

    # Incrementar vistas
    producto.vistas += 1
    db.session.commit()

    # Productos relacionados
    relacionados = Producto.query.filter(
        Producto.id_categoria == producto.id_categoria,
        Producto.id != producto.id,
        Producto.estado == 1
    ).limit(4).all()

    return render_template('shop/product_detail.html',
                         producto=producto,
                         relacionados=relacionados)

@shop_bp.route('/buscar')
def search():
    q = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)

    if not q:
        return redirect(url_for('shop.index'))

    productos = Producto.query.filter(
        or_(
            Producto.titulo.like(f'%{q}%'),
            Producto.descripcion.like(f'%{q}%')
        ),
        Producto.estado == 1
    ).paginate(page=page, per_page=12)

    return render_template('shop/search.html',
                         productos=productos,
                         query=q)
```

### 3.5 Fase 4: Carrito y Checkout (Semana 7-8)

#### 4.1 Gestión del Carrito

```python
# app/blueprints/cart/routes.py
from flask import Blueprint, render_template, request, jsonify, session
from app.models.product import Producto
from app.services.currency_service import convert_currency

cart_bp = Blueprint('cart', __name__, url_prefix='/carrito')

@cart_bp.route('/')
def index():
    cart_items = session.get('cart', [])

    # Obtener detalles de productos
    products = []
    total = 0

    for item in cart_items:
        producto = Producto.query.get(item['id'])
        if producto:
            precio = producto.precio_oferta or producto.precio
            subtotal = precio * item['cantidad']
            products.append({
                'producto': producto,
                'cantidad': item['cantidad'],
                'precio': precio,
                'subtotal': subtotal
            })
            total += subtotal

    return render_template('cart/cart.html',
                         products=products,
                         total=total)

@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    producto_id = data.get('producto_id')
    cantidad = data.get('cantidad', 1)

    # Validar producto
    producto = Producto.query.get_or_404(producto_id)

    # Obtener carrito de sesión
    cart = session.get('cart', [])

    # Buscar si ya existe
    found = False
    for item in cart:
        if item['id'] == producto_id:
            item['cantidad'] += cantidad
            found = True
            break

    if not found:
        cart.append({
            'id': producto_id,
            'cantidad': cantidad
        })

    session['cart'] = cart
    session.modified = True

    return jsonify({
        'success': True,
        'cart_count': len(cart)
    })

@cart_bp.route('/remove/<int:producto_id>', methods=['POST'])
def remove_from_cart(producto_id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != producto_id]
    session['cart'] = cart
    session.modified = True

    return jsonify({'success': True})
```

#### 4.2 Integración de PayPal

```python
# app/blueprints/checkout/paypal.py
import paypalrestsdk
from flask import current_app, url_for
from app.models.comercio import Comercio

def configure_paypal():
    config = Comercio.query.first()
    paypalrestsdk.configure({
        "mode": config.modo_paypal,  # sandbox o live
        "client_id": config.cliente_id_paypal,
        "client_secret": config.llave_secreta_paypal
    })

def create_payment(items, total, shipping, tax):
    configure_paypal()

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": url_for('checkout.paypal_execute', _external=True),
            "cancel_url": url_for('cart.index', _external=True)
        },
        "transactions": [{
            "item_list": {
                "items": items
            },
            "amount": {
                "total": str(total),
                "currency": "USD",
                "details": {
                    "subtotal": str(total - shipping - tax),
                    "shipping": str(shipping),
                    "tax": str(tax)
                }
            },
            "description": "Compra en Tienda Virtual"
        }]
    })

    if payment.create():
        return payment
    else:
        raise Exception(payment.error)

@checkout_bp.route('/paypal/execute')
@login_required
def paypal_execute():
    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')

    configure_paypal()
    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        # Procesar orden
        process_order(payment, current_user.id)
        flash('Pago completado exitosamente', 'success')
        return redirect(url_for('profile.orders'))
    else:
        flash('Error al procesar el pago', 'error')
        return redirect(url_for('cart.index'))
```

### 3.6 Fase 5: Panel Administrativo (Semana 9-10)

#### 5.1 Flask-Admin

```python
# app/blueprints/admin/__init__.py
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, request

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.perfil == 'administrador'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))

def init_admin(app, db):
    admin = Admin(app, name='Panel Admin', template_mode='bootstrap4')

    # Agregar vistas
    from app.models import User, Producto, Categoria, Compra, Administrador

    admin.add_view(SecureModelView(Administrador, db.session, name='Administradores'))
    admin.add_view(SecureModelView(User, db.session, name='Usuarios'))
    admin.add_view(SecureModelView(Producto, db.session, name='Productos'))
    admin.add_view(SecureModelView(Categoria, db.session, name='Categorías'))
    admin.add_view(SecureModelView(Compra, db.session, name='Ventas'))
```

### 3.7 Fase 6: Testing (Semana 11)

```python
# tests/test_auth.py
import pytest
from app.models import User

def test_register(client):
    response = client.post('/auth/register', data={
        'nombre': 'Test User',
        'email': 'test@test.com',
        'password': 'password123',
        'password2': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert User.query.filter_by(email='test@test.com').first() is not None

def test_login(client, user):
    response = client.post('/auth/login', data={
        'email': user.email,
        'password': 'password'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Bienvenido' in response.data

# tests/test_products.py
def test_product_list(client):
    response = client.get('/tienda/')
    assert response.status_code == 200

def test_product_detail(client, product):
    response = client.get(f'/tienda/producto/{product.ruta}')
    assert response.status_code == 200
    assert product.titulo.encode() in response.data
```

### 3.8 Fase 7: Deployment (Semana 12)

#### 7.1 Docker Setup

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicación
COPY . .

# Crear usuario no-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "run:app"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://postgres:password@db:5432/ecommerce
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./app/static/uploads:/app/app/static/uploads

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=ecommerce
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  celery:
    build: .
    command: celery -A app.celery worker --loglevel=info
    depends_on:
      - redis
      - db
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/ecommerce
      - REDIS_URL=redis://redis:6379/0

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./app/static:/app/static
    depends_on:
      - web

volumes:
  postgres_data:
```

---

## 4. Equivalencias PHP-Flask

### 4.1 Conceptos Básicos

| PHP | Flask |
|-----|-------|
| `$_GET` | `request.args` |
| `$_POST` | `request.form` |
| `$_FILES` | `request.files` |
| `$_SESSION` | `session` |
| `$_COOKIE` | `request.cookies` |
| `$_SERVER` | `request.environ` |
| `header('Location: ...')` | `redirect(url_for(...))` |
| `json_encode()` | `jsonify()` |
| `include/require` | `import` |
| `echo` | `return` |
| `die()` | `abort()` |

### 4.2 Base de Datos

| PHP (PDO) | Flask (SQLAlchemy) |
|-----------|-------------------|
| `$stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?")` | `User.query.filter_by(id=user_id).first()` |
| `$stmt->execute([$id])` | - |
| `$stmt->fetch(PDO::FETCH_ASSOC)` | `.first()` |
| `$stmt->fetchAll()` | `.all()` |
| `$pdo->lastInsertId()` | `db.session.add(obj); db.session.commit()` |
| Manual SQL | ORM automático |

### 4.3 Autenticación

| PHP | Flask (Flask-Login) |
|-----|---------------------|
| `$_SESSION['usuario_id'] = $id` | `login_user(user)` |
| `unset($_SESSION['usuario_id'])` | `logout_user()` |
| `isset($_SESSION['usuario_id'])` | `current_user.is_authenticated` |
| `$_SESSION['usuario']` | `current_user` |
| Verificación manual | `@login_required` decorator |

### 4.4 Validación

| PHP | Flask (WTForms) |
|-----|-----------------|
| `preg_match('/regex/', $input)` | `form.field.validators` |
| Validación manual en controlador | Validación declarativa en Form |
| `filter_var($email, FILTER_VALIDATE_EMAIL)` | `EmailField()` |

### 4.5 Templates

| PHP | Jinja2 |
|-----|--------|
| `<?php echo $var ?>` | `{{ var }}` |
| `<?php if($cond): ?>...<?php endif ?>` | `{% if cond %}...{% endif %}` |
| `<?php foreach($items as $item): ?>` | `{% for item in items %}` |
| `<?php include 'file.php' ?>` | `{% include 'file.html' %}` |
| `htmlspecialchars()` | Automático (Jinja2) |

---

## 5. Gestión de Dependencias

### 5.1 Requirements.txt

```txt
# Core
Flask==3.0.0
Werkzeug==3.0.1

# Database
SQLAlchemy==2.0.23
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
psycopg2-binary==2.9.9
PyMySQL==1.1.0

# Auth
Flask-Login==0.6.3
Flask-Bcrypt==1.0.1
Authlib==1.3.0

# Forms
Flask-WTF==1.2.1
WTForms==3.1.1
email-validator==2.1.0

# Email
Flask-Mail==0.9.1

# Admin
Flask-Admin==1.6.1

# API
Flask-RESTX==1.3.0
Flask-CORS==4.0.0
marshmallow==3.20.1

# Payments
paypalrestsdk==1.13.1

# Tasks
celery==5.3.4
redis==5.0.1
Flask-Caching==2.1.0

# Utils
python-dotenv==1.0.0
Pillow==10.1.0
requests==2.31.0

# Security
Flask-Talisman==1.1.0
Flask-Limiter==3.5.0

# Development
pytest==7.4.3
pytest-flask==1.3.0
pytest-cov==4.1.0
flake8==6.1.0
black==23.12.0

# Production
gunicorn==21.2.0
```

### 5.2 Instalación

```bash
# Desarrollo
pip install -r requirements.txt

# Producción
pip install -r requirements.txt --no-dev
```

---

## 6. Estrategia de Testing

### 6.1 Estructura de Tests

```
tests/
├── conftest.py           # Fixtures compartidos
├── test_auth.py          # Tests de autenticación
├── test_products.py      # Tests de productos
├── test_cart.py          # Tests de carrito
├── test_checkout.py      # Tests de checkout
├── test_admin.py         # Tests de admin
└── test_api.py           # Tests de API
```

### 6.2 Fixtures

```python
# tests/conftest.py
import pytest
from app import create_app, db
from app.models import User, Producto, Categoria

@pytest.fixture
def app():
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user(app):
    user = User(nombre='Test', email='test@test.com', modo='directo', verificacion=0)
    user.set_password('password')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def product(app):
    categoria = Categoria(categoria='Test', ruta='test', estado=1)
    db.session.add(categoria)
    db.session.commit()

    producto = Producto(
        titulo='Test Product',
        ruta='test-product',
        precio=100.0,
        id_categoria=categoria.id,
        estado=1
    )
    db.session.add(producto)
    db.session.commit()
    return producto
```

### 6.3 Cobertura

```bash
# Ejecutar tests con cobertura
pytest --cov=app --cov-report=html

# Ver reporte
open htmlcov/index.html
```

---

## 7. Deployment y DevOps

### 7.1 Variables de Entorno

```bash
# .env.example
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

DATABASE_URL=postgresql://user:pass@localhost/ecommerce
REDIS_URL=redis://localhost:6379/0

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-password

PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=your-client-id
PAYPAL_CLIENT_SECRET=your-client-secret

GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

RECAPTCHA_PUBLIC_KEY=your-recaptcha-public-key
RECAPTCHA_PRIVATE_KEY=your-recaptcha-private-key
```

### 7.2 Nginx Configuration

```nginx
# nginx.conf
upstream app {
    server web:5000;
}

server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 7.3 CI/CD con GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost/test
      run: |
        pytest --cov=app
```

---

## 8. Cronograma Estimado

### Semanas 1-2: Setup
- [ ] Configurar entorno de desarrollo
- [ ] Crear estructura del proyecto
- [ ] Configurar base de datos
- [ ] Migrar schema y datos

### Semanas 3-4: Autenticación
- [ ] Implementar registro/login
- [ ] Integrar OAuth (Google, Facebook)
- [ ] Sistema de verificación de email
- [ ] Recuperación de contraseña

### Semanas 5-6: Productos
- [ ] Modelos de productos/categorías
- [ ] Vistas de catálogo
- [ ] Búsqueda y filtros
- [ ] Detalle de producto

### Semanas 7-8: Carrito y Pago
- [ ] Sistema de carrito
- [ ] Integración PayPal
- [ ] Integración PayU
- [ ] Proceso de checkout

### Semanas 9-10: Panel Admin
- [ ] Flask-Admin setup
- [ ] Gestión de productos
- [ ] Gestión de usuarios
- [ ] Reportes y analytics

### Semana 11: Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] E2E tests
- [ ] Performance testing

### Semana 12: Deployment
- [ ] Configurar Docker
- [ ] Setup CI/CD
- [ ] Deploy a staging
- [ ] Deploy a producción

---

## 9. Checklist de Migración

### Pre-Migración
- [ ] Backup completo de BD actual
- [ ] Documentar configuración actual
- [ ] Identificar dependencias críticas
- [ ] Planificar downtime

### Durante Migración
- [ ] Migrar schema de BD
- [ ] Migrar datos
- [ ] Validar integridad de datos
- [ ] Configurar servicios externos

### Post-Migración
- [ ] Testing exhaustivo
- [ ] Validar todas las funcionalidades
- [ ] Monitoreo de errores
- [ ] Rollback plan listo

### Validación
- [ ] Usuarios pueden registrarse/login
- [ ] Productos se muestran correctamente
- [ ] Carrito funciona
- [ ] Pagos se procesan
- [ ] Emails se envían
- [ ] Panel admin accesible
- [ ] Performance aceptable

---

## 10. Notas Importantes

### Compatibilidad de Passwords
Los passwords actuales están hasheados con `crypt()` de PHP. Flask usa `bcrypt`.

**Solución**: Mantener compatibilidad temporal:

```python
class User(UserMixin, db.Model):
    def check_password(self, password):
        # Intentar primero con bcrypt (nuevo)
        if self.password_hash.startswith('$2a$') or self.password_hash.startswith('$2b$'):
            return bcrypt.check_password_hash(self.password_hash, password)

        # Fallback a crypt (legacy PHP)
        import crypt
        return self.password_hash == crypt.crypt(password, self.password_hash)

    def migrate_password(self, password):
        """Migrar de crypt a bcrypt cuando el usuario inicie sesión"""
        if not self.password_hash.startswith('$2'):
            self.set_password(password)
            db.session.commit()
```

### Sesiones PHP vs Flask
PHP guarda sesiones en archivos. Flask usa cookies firmadas.

**Migración**: Las sesiones actuales se perderán. Avisar a usuarios que deberán volver a iniciar sesión.

### Archivos Subidos
Mantener la misma estructura de carpetas para compatibilidad:
```
static/
  uploads/
    productos/
    usuarios/
    categorias/
    banners/
```

---

## Conclusión

Este plan de migración proporciona una ruta clara y detallada para migrar el e-commerce de PHP a Flask. El enfoque incremental minimiza riesgos y permite validar cada fase antes de continuar.

**Próximos Pasos:**
1. Revisar y aprobar este plan
2. Configurar entorno de desarrollo
3. Comenzar Fase 1: Setup y migración de datos

**Contacto para Dudas:**
Crear issues en el repositorio o contactar al equipo de desarrollo.

---

**Última Actualización**: 2025-11-18
**Versión**: 1.0
