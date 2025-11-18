# PLAN DE MIGRACIÓN PHP A FLASK/PYTHON

## ANÁLISIS DE COMPRENSIÓN ACTUAL DEL PROYECTO

### ✅ Lo que COMPRENDO COMPLETAMENTE (85%)

#### 1. **Arquitectura y Patrones** (100%)
- ✅ Patrón MVC implementado
- ✅ Separación backend/frontend
- ✅ Front Controller pattern
- ✅ Flujo de datos completo
- ✅ Routing basado en parámetros GET

#### 2. **Backend - Lógica de Negocio** (90%)
- ✅ **Controladores** (16 archivos):
  - Todos los métodos documentados
  - Validaciones con regex entendidas
  - Procesamiento de imágenes (redimensionamiento)
  - Lógica de ofertas y descuentos
  - Sistema de activación/desactivación

- ✅ **Modelos** (16 archivos):
  - Conexión PDO y prepared statements
  - Métodos CRUD completos
  - Consultas SQL complejas
  - Relaciones entre tablas

- ✅ **AJAX** (15+ archivos):
  - Peticiones asíncronas
  - DataTables implementation
  - Activación en tiempo real

#### 3. **Frontend - Lógica del Cliente** (85%)
- ✅ **Carrito de compras** (`carrito-de-compras.js`):
  - LocalStorage para persistencia
  - Agregar/quitar productos
  - Cálculo de subtotales y totales
  - Manejo de productos físicos vs virtuales
  - Tarifas de envío nacional/internacional
  - Cambio de divisas con API externa
  - Integración PayPal (botones, create order, approve)
  - Integración PayU (formulario, firma MD5, redirect)
  - Validación de totales con MD5

- ✅ **Gestión de productos** (`gestorProductos.js`):
  - DataTables con AJAX
  - Activar/desactivar productos
  - Validación de títulos duplicados
  - Generación de URL amigables (slugs)

- ✅ **Usuarios** (`usuarios.js`):
  - Registro con validaciones
  - Login y recuperación de contraseña
  - Validación de email repetido
  - Sistema de calificaciones (1-5 estrellas)
  - Lista de deseos
  - Cambio de foto de perfil
  - Formulario de contacto

#### 4. **Base de Datos** (100%)
- ✅ Estructura completa de 16 tablas
- ✅ Relaciones entre tablas
- ✅ Campos JSON (multimedia, detalles)
- ✅ Sistema de timestamps

#### 5. **Seguridad** (90%)
- ✅ Prepared statements (PDO)
- ✅ Validaciones con regex
- ✅ Encriptación de contraseñas (crypt)
- ✅ Validación de precios en servidor
- ✅ Sanitización de entradas
- ✅ Validación de archivos subidos

---

### ⚠️ Lo que NECESITO PROFUNDIZAR (15%)

#### 1. **Vistas HTML Completas** (70% entendido)
**Lo que sé**:
- Estructura general de módulos
- Integración de jQuery/AJAX
- Uso de Bootstrap

**Lo que necesito**:
- Ver TODAS las vistas completas
- Entender estructura HTML exacta de formularios
- Identificar todos los IDs y clases usados por JavaScript
- Validar compatibilidad de templates con Jinja2

**Archivos a revisar**:
```
backend/vistas/modulos/*.php
frontend/vistas/modulos/*.php
```

#### 2. **Configuración de Servidor** (50% entendido)
**Lo que sé**:
- URL rewriting básico
- Estructura de directorios

**Lo que necesito**:
- Ver `.htaccess` completo
- Entender reglas de rewrite exactas
- Identificar variables de entorno
- Ver configuración de permisos

**Archivos a buscar**:
```
.htaccess
php.ini settings
apache/nginx config
```

#### 3. **Integraciones de Pago - Detalles Técnicos** (75% entendido)
**Lo que sé**:
- Flujo general de PayPal y PayU
- Creación de órdenes y procesamiento
- Validación de firmas MD5

**Lo que necesito**:
- Códigos completos de comercio (merchantId, apiKey)
- URLs exactas de webhooks
- Manejo de respuestas de confirmación
- Testing en sandbox vs producción
- Manejo de errores y refunds

**Archivos a revisar**:
```
frontend/vistas/modulos/finalizar-compra.php
frontend/vistas/modulos/finalizar-compra-payu.php
frontend/ajax/carrito.ajax.php (completo)
```

#### 4. **Sistema de Correos - PHPMailer** (60% entendido)
**Lo que sé**:
- Se usa PHPMailer
- Envío de confirmaciones y verificaciones

**Lo que necesito**:
- Ver configuración SMTP completa
- Templates de emails
- Manejo de errores de envío
- Configuración de credenciales

**Archivos a revisar**:
```
frontend/extensiones/PHPMailer/*
frontend/plantillas-correo/*
Buscar configuración SMTP en controladores
```

#### 5. **Dependencias Externas** (70% entendido)
**Lo que sé**:
- Bower components (AdminLTE, plugins)
- Composer packages
- Librerías JavaScript

**Lo que necesito**:
- Ver `bower.json` y `composer.json`
- Identificar TODAS las dependencias
- Ver versiones específicas
- Entender qué es crítico vs opcional

---

## PLAN COMPLETO DE MIGRACIÓN A FLASK/PYTHON

### FASE 1: ANÁLISIS Y PREPARACIÓN (1-2 semanas)

#### 1.1 Inventario Completo
```bash
# Tareas:
□ Leer TODOS los archivos PHP (controladores, modelos, vistas)
□ Documentar TODAS las funciones y sus parámetros
□ Extraer TODAS las queries SQL
□ Mapear TODAS las rutas del aplicativo
□ Identificar TODAS las dependencias externas
□ Documentar configuraciones de servidor
```

#### 1.2 Análisis de Dependencias
```python
# PHP → Python equivalencias:

PHP                        →  Python/Flask
─────────────────────────────────────────────────────
PDO                        →  SQLAlchemy
crypt()                    →  bcrypt / passlib
json_encode/decode         →  json module
$_SESSION                  →  Flask sessions
$_POST/$_GET               →  request.form / request.args
header('Location:')        →  redirect()
file_get_contents()        →  requests library
imagecreatefromjpeg()      →  Pillow (PIL)
preg_match()               →  re module
PHPMailer                  →  Flask-Mail
```

#### 1.3 Crear Inventario de APIs
```
PayPal SDK for PHP  →  paypalrestsdk (Python)
PayU API            →  requests + custom implementation
Currency API        →  requests
Geolocation API     →  requests
```

---

### FASE 2: CONFIGURACIÓN DEL ENTORNO FLASK (1 semana)

#### 2.1 Estructura del Proyecto Flask
```
ecommerce_flask/
│
├── app/
│   ├── __init__.py              # Inicialización Flask
│   ├── config.py                # Configuraciones
│   ├── models.py                # Modelos SQLAlchemy
│   │
│   ├── admin/                   # Blueprint Admin (Backend)
│   │   ├── __init__.py
│   │   ├── routes.py           # Rutas del admin
│   │   ├── forms.py            # WTForms
│   │   └── templates/          # Templates Jinja2
│   │
│   ├── shop/                    # Blueprint Shop (Frontend)
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── forms.py
│   │   └── templates/
│   │
│   ├── api/                     # API REST (AJAX endpoints)
│   │   ├── __init__.py
│   │   ├── productos.py
│   │   ├── carrito.py
│   │   └── usuarios.py
│   │
│   ├── static/                  # Archivos estáticos
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   │
│   └── utils/                   # Utilidades
│       ├── __init__.py
│       ├── image_processing.py
│       ├── email.py
│       └── payments.py
│
├── migrations/                  # Migraciones Alembic
├── tests/                       # Tests unitarios
├── requirements.txt             # Dependencias Python
├── .env                         # Variables de entorno
└── run.py                       # Punto de entrada
```

#### 2.2 requirements.txt
```txt
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-WTF==1.2.1
Flask-Mail==0.9.1
Flask-Migrate==4.0.5
Pillow==10.1.0
bcrypt==4.1.1
passlib==1.7.4
paypalrestsdk==1.13.1
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
```

---

### FASE 3: MIGRACIÓN DE BASE DE DATOS (1 semana)

#### 3.1 Crear Modelos SQLAlchemy

```python
# app/models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    id_subcategoria = db.Column(db.Integer, db.ForeignKey('subcategorias.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    ruta = db.Column(db.String(255), unique=True, nullable=False)
    estado = db.Column(db.Boolean, default=True)
    titulo = db.Column(db.String(200), nullable=False)
    titular = db.Column(db.String(255))
    descripcion = db.Column(db.Text)
    multimedia = db.Column(db.JSON)  # JSON directo en MySQL 5.7+
    detalles = db.Column(db.JSON)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    portada = db.Column(db.String(255))
    oferta = db.Column(db.Boolean, default=False)
    precio_oferta = db.Column(db.Numeric(10, 2))
    descuento_oferta = db.Column(db.Integer)
    img_oferta = db.Column(db.String(255))
    fin_oferta = db.Column(db.Date)
    peso = db.Column(db.Numeric(10, 2))
    entrega = db.Column(db.Integer)
    ventas = db.Column(db.Integer, default=0)
    vistas = db.Column(db.Integer, default=0)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    categoria = db.relationship('Categoria', backref='productos')
    subcategoria = db.relationship('Subcategoria', backref='productos')

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'precio': float(self.precio),
            'precio_oferta': float(self.precio_oferta) if self.precio_oferta else None,
            'imagen': self.portada,
            'ruta': self.ruta,
            # ... más campos
        }

    @property
    def precio_final(self):
        return self.precio_oferta if self.oferta else self.precio

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    direccion = db.Column(db.Text)
    telefono = db.Column(db.String(20))
    foto = db.Column(db.String(255))
    verificado = db.Column(db.Boolean, default=False)
    codigo_verificacion = db.Column(db.String(100))
    estado = db.Column(db.Boolean, default=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    compras = db.relationship('Compra', backref='usuario', lazy='dynamic')
    deseos = db.relationship('Deseo', backref='usuario', lazy='dynamic')

    def set_password(self, password):
        from passlib.hash import bcrypt
        self.password_hash = bcrypt.hash(password)

    def check_password(self, password):
        from passlib.hash import bcrypt
        return bcrypt.verify(password, self.password_hash)

class Compra(db.Model):
    __tablename__ = 'compras'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    productos = db.Column(db.JSON)  # Lista de productos comprados
    total = db.Column(db.Numeric(10, 2), nullable=False)
    metodo_pago = db.Column(db.String(50), nullable=False)
    transaccion_id = db.Column(db.String(100))
    estado = db.Column(db.String(50), default='pendiente')
    direccion_envio = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def get_productos(self):
        return json.loads(self.productos) if isinstance(self.productos, str) else self.productos

# ... más modelos (Categoria, Subcategoria, Administrador, etc.)
```

#### 3.2 Migración de Datos
```python
# scripts/migrate_data.py

from app import create_app, db
from app.models import Producto, Usuario, Compra
import pymysql
import json

def migrate_from_php_db():
    """Migra datos de la BD PHP a la nueva estructura"""

    # Conexión a BD antigua
    old_conn = pymysql.connect(
        host='localhost',
        user='ferrete5_juanu',
        password='*****',
        database='ferrete5_ecommerce'
    )

    cursor = old_conn.cursor(pymysql.cursors.DictCursor)

    # Migrar productos
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()

    for p in productos:
        nuevo_producto = Producto(
            id=p['id'],
            id_categoria=p['id_categoria'],
            id_subcategoria=p['id_subcategoria'],
            tipo=p['tipo'],
            ruta=p['ruta'],
            estado=bool(p['estado']),
            titulo=p['titulo'],
            titular=p['titular'],
            descripcion=p['descripcion'],
            multimedia=json.loads(p['multimedia']) if p['multimedia'] else [],
            detalles=json.loads(p['detalles']) if p['detalles'] else {},
            precio=p['precio'],
            portada=p['portada'],
            oferta=bool(p['oferta']),
            precio_oferta=p['precioOferta'],
            descuento_oferta=p['descuentoOferta'],
            img_oferta=p['imgOferta'],
            fin_oferta=p['finOferta'],
            peso=p['peso'],
            entrega=p['entrega'],
            ventas=p['ventas'],
            vistas=p['vistas'],
            fecha=p['fecha']
        )
        db.session.add(nuevo_producto)

    db.session.commit()
    print(f"Migrados {len(productos)} productos")

    # Migrar usuarios
    # ... similar

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        migrate_from_php_db()
```

---

### FASE 4: MIGRACIÓN DEL BACKEND (3-4 semanas)

#### 4.1 Configuración Flask
```python
# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Registrar blueprints
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.shop import bp as shop_bp
    app.register_blueprint(shop_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
```

```python
# config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://user:password@localhost/ecommerce_flask'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'app/static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max

    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # PayPal
    PAYPAL_MODE = os.environ.get('PAYPAL_MODE') or 'sandbox'
    PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
    PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET')

    # PayU
    PAYU_MERCHANT_ID = os.environ.get('PAYU_MERCHANT_ID')
    PAYU_ACCOUNT_ID = os.environ.get('PAYU_ACCOUNT_ID')
    PAYU_API_KEY = os.environ.get('PAYU_API_KEY')
    PAYU_MODE = os.environ.get('PAYU_MODE') or 'sandbox'
```

#### 4.2 Migrar Controlador de Productos

**PHP Original** (`productos.controlador.php`):
```php
static public function ctrMostrarProductos($item, $valor){
    $tabla = "productos";
    $respuesta = ModeloProductos::mdlMostrarProductos($tabla, $item, $valor);
    return $respuesta;
}
```

**Flask Equivalente** (`app/admin/routes.py`):
```python
from flask import Blueprint, render_template, request, jsonify
from app.models import Producto, Categoria
from app import db

bp = Blueprint('admin', __name__)

@bp.route('/productos')
@login_required
def productos():
    """Lista de productos - vista principal"""
    productos = Producto.query.order_by(Producto.id.desc()).all()
    categorias = Categoria.query.filter_by(estado=True).all()
    return render_template('admin/productos.html',
                         productos=productos,
                         categorias=categorias)

@bp.route('/productos/<int:id>')
@login_required
def producto_detalle(id):
    """Detalle de un producto específico"""
    producto = Producto.query.get_or_404(id)
    return render_template('admin/producto_detalle.html', producto=producto)

@bp.route('/productos/crear', methods=['GET', 'POST'])
@login_required
def producto_crear():
    """Crear nuevo producto"""
    if request.method == 'POST':
        # Validación
        titulo = request.form.get('titulo')
        if not titulo or not re.match(r'^[a-zA-Z0-9ñÑáéíóúÁÉÍÓÚ ]+$', titulo):
            flash('Título inválido', 'error')
            return redirect(url_for('admin.producto_crear'))

        # Procesar imágenes
        portada = request.files.get('foto_portada')
        if portada:
            from app.utils.image_processing import resize_and_save
            portada_path = resize_and_save(portada, (1280, 720), 'cabeceras')

        # Crear producto
        nuevo_producto = Producto(
            titulo=titulo,
            id_categoria=request.form.get('categoria'),
            id_subcategoria=request.form.get('subcategoria'),
            tipo=request.form.get('tipo'),
            ruta=slugify(titulo),
            descripcion=request.form.get('descripcion'),
            precio=request.form.get('precio'),
            peso=request.form.get('peso'),
            entrega=request.form.get('entrega'),
            portada=portada_path
        )

        db.session.add(nuevo_producto)
        db.session.commit()

        flash('Producto creado exitosamente', 'success')
        return redirect(url_for('admin.productos'))

    categorias = Categoria.query.filter_by(estado=True).all()
    return render_template('admin/producto_form.html', categorias=categorias)
```

#### 4.3 Utilidad de Procesamiento de Imágenes

**PHP Original**:
```php
list($ancho, $alto) = getimagesize($datos["tmp_name"]);
$nuevoAncho = 1280;
$nuevoAlto = 720;
$origen = imagecreatefromjpeg($datos["tmp_name"]);
$destino = imagecreatetruecolor($nuevoAncho, $nuevoAlto);
imagecopyresized($destino, $origen, 0, 0, 0, 0, $nuevoAncho, $nuevoAlto, $ancho, $alto);
imagejpeg($destino, $rutaPortada);
```

**Python Equivalente** (`app/utils/image_processing.py`):
```python
from PIL import Image
import os
from werkzeug.utils import secure_filename
from flask import current_app

def resize_and_save(file, size, folder):
    """
    Redimensiona y guarda una imagen

    Args:
        file: FileStorage object
        size: Tupla (ancho, alto)
        folder: Carpeta destino (relativo a uploads)

    Returns:
        Ruta relativa de la imagen guardada
    """
    filename = secure_filename(file.filename)

    # Crear directorio si no existe
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(upload_path, exist_ok=True)

    # Abrir imagen original
    img = Image.open(file)

    # Redimensionar manteniendo aspecto
    img.thumbnail(size, Image.LANCZOS)

    # Crear imagen nueva con tamaño exacto
    new_img = Image.new('RGB', size, (255, 255, 255))

    # Centrar imagen redimensionada
    offset = ((size[0] - img.size[0]) // 2, (size[1] - img.size[1]) // 2)
    new_img.paste(img, offset)

    # Guardar
    save_path = os.path.join(upload_path, filename)
    new_img.save(save_path, 'JPEG', quality=90)

    # Retornar ruta relativa
    return os.path.join('uploads', folder, filename)

def allowed_file(filename, allowed_extensions={'jpg', 'jpeg', 'png'}):
    """Valida extensión de archivo"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
```

---

### FASE 5: MIGRACIÓN DEL FRONTEND (2-3 semanas)

#### 5.1 Carrito de Compras

**JavaScript se mantiene igual** (95% compatible):
- LocalStorage funciona idéntico
- AJAX solo cambia las URLs
- Lógica del carrito es independiente del backend

**Cambios necesarios**:
```javascript
// PHP: ajax/carrito.ajax.php
// Flask: /api/carrito

// Antes (PHP)
$.ajax({
    url: rutaOculta + "ajax/carrito.ajax.php",
    method: "POST",
    data: datos,
    // ...
})

// Después (Flask)
$.ajax({
    url: "/api/carrito/procesar",  // Nueva ruta
    method: "POST",
    data: JSON.stringify(datos),   // JSON en lugar de FormData
    contentType: "application/json",
    // ...
})
```

#### 5.2 API Endpoints para AJAX

```python
# app/api/carrito.py

from flask import Blueprint, request, jsonify, session
from app.models import Producto, Compra, Usuario
from app import db
import hashlib

bp = Blueprint('api_carrito', __name__)

@bp.route('/carrito/procesar', methods=['POST'])
def procesar_carrito():
    """Procesa pago de PayPal o PayU"""
    data = request.get_json()

    # Validar total encriptado (MD5)
    total = data.get('total')
    total_encriptado = data.get('totalEncriptado')

    if hashlib.md5(str(total).encode()).hexdigest() != total_encriptado:
        return jsonify({'error': 'Total manipulado'}), 400

    # Validar precios de productos
    productos_carrito = data.get('idProductoArray', [])
    for idx, producto_id in enumerate(productos_carrito):
        producto = Producto.query.get(producto_id)
        precio_enviado = float(data['valorItemArray'][idx])
        precio_real = float(producto.precio_final)

        if precio_enviado != precio_real:
            return jsonify({'error': 'Precio manipulado'}), 400

    # Todo validado, proceder con pago
    if data.get('metodoPago') == 'paypal':
        return procesar_paypal(data)
    elif data.get('metodoPago') == 'payu':
        return procesar_payu(data)

def procesar_paypal(data):
    """Redirige a PayPal"""
    import paypalrestsdk
    from flask import current_app

    paypalrestsdk.configure({
        "mode": current_app.config['PAYPAL_MODE'],
        "client_id": current_app.config['PAYPAL_CLIENT_ID'],
        "client_secret": current_app.config['PAYPAL_CLIENT_SECRET']
    })

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://localhost:5000/pago/exito",
            "cancel_url": "http://localhost:5000/pago/cancelado"
        },
        "transactions": [{
            "amount": {
                "total": data['total'],
                "currency": data['divisa']
            },
            "description": "Compra en ecommerce"
        }]
    })

    if payment.create():
        # Encontrar URL de aprobación
        for link in payment.links:
            if link.rel == "approval_url":
                return jsonify({'redirect': link.href})
    else:
        return jsonify({'error': payment.error}), 400

@bp.route('/carrito/webhook-paypal', methods=['POST'])
def webhook_paypal():
    """Webhook de confirmación de PayPal"""
    data = request.get_json()

    # Guardar compra en BD
    nueva_compra = Compra(
        id_usuario=session.get('user_id'),
        productos=data['productos'],
        total=data['total'],
        metodo_pago='PayPal',
        transaccion_id=data['transaction_id'],
        estado='completado'
    )

    db.session.add(nueva_compra)
    db.session.commit()

    # Actualizar ventas de productos
    # ... (similar a PHP)

    return jsonify({'status': 'ok'})
```

#### 5.3 Templates Jinja2

**PHP Original** (`frontend/vistas/modulos/productos.php`):
```php
<?php foreach($productos as $producto): ?>
    <div class="product">
        <h3><?php echo $producto["titulo"]; ?></h3>
        <p>$<?php echo $producto["precio"]; ?></p>
        <button class="agregarCarrito"
                idProducto="<?php echo $producto["id"]; ?>"
                titulo="<?php echo $producto["titulo"]; ?>"
                precio="<?php echo $producto["precio"]; ?>">
            Agregar al carrito
        </button>
    </div>
<?php endforeach; ?>
```

**Flask/Jinja2 Equivalente** (`app/shop/templates/productos.html`):
```html
{% for producto in productos %}
    <div class="product">
        <h3>{{ producto.titulo }}</h3>
        <p>${{ producto.precio }}</p>
        <button class="agregarCarrito"
                data-id="{{ producto.id }}"
                data-titulo="{{ producto.titulo }}"
                data-precio="{{ producto.precio }}">
            Agregar al carrito
        </button>
    </div>
{% endfor %}
```

---

### FASE 6: SISTEMA DE CORREOS (1 semana)

```python
# app/utils/email.py

from flask_mail import Message
from flask import render_template, current_app
from app import mail
from threading import Thread

def send_async_email(app, msg):
    """Envía email de forma asíncrona"""
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    """Envía un email"""
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body

    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()

def send_verification_email(user):
    """Envía email de verificación de cuenta"""
    token = user.codigo_verificacion

    send_email(
        subject='Verifica tu cuenta',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[user.email],
        text_body=render_template('email/verificacion.txt', user=user, token=token),
        html_body=render_template('email/verificacion.html', user=user, token=token)
    )

def send_password_reset_email(user, new_password):
    """Envía email con nueva contraseña"""
    send_email(
        subject='Recuperación de contraseña',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[user.email],
        text_body=f'Tu nueva contraseña es: {new_password}',
        html_body=render_template('email/reset_password.html',
                                 user=user,
                                 new_password=new_password)
    )

def send_purchase_confirmation(compra):
    """Envía confirmación de compra"""
    user = compra.usuario

    send_email(
        subject='Confirmación de compra',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[user.email],
        text_body=render_template('email/compra.txt', compra=compra),
        html_body=render_template('email/compra.html', compra=compra)
    )
```

---

### FASE 7: TESTING (2 semanas)

#### 7.1 Tests Unitarios
```python
# tests/test_productos.py

import unittest
from app import create_app, db
from app.models import Producto, Categoria

class ProductoTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_crear_producto(self):
        """Test crear producto"""
        categoria = Categoria(nombre='Electrónica', ruta='electronica')
        db.session.add(categoria)
        db.session.commit()

        producto = Producto(
            titulo='Laptop HP',
            id_categoria=categoria.id,
            tipo='fisico',
            ruta='laptop-hp',
            precio=899.99
        )
        db.session.add(producto)
        db.session.commit()

        self.assertIsNotNone(producto.id)
        self.assertEqual(producto.titulo, 'Laptop HP')

    def test_precio_final_con_oferta(self):
        """Test cálculo de precio final con oferta"""
        producto = Producto(
            titulo='Mouse',
            precio=50.00,
            oferta=True,
            precio_oferta=35.00
        )

        self.assertEqual(producto.precio_final, 35.00)

    def test_precio_final_sin_oferta(self):
        """Test cálculo de precio final sin oferta"""
        producto = Producto(
            titulo='Teclado',
            precio=75.00,
            oferta=False
        )

        self.assertEqual(producto.precio_final, 75.00)
```

#### 7.2 Tests de Integración
```python
# tests/test_carrito.py

import unittest
from app import create_app, db
from app.models import Producto, Usuario, Compra

class CarritoTestCase(unittest.TestCase):

    def test_agregar_producto_al_carrito(self):
        """Test agregar producto al carrito (API)"""
        with self.app.test_client() as client:
            # Crear usuario de prueba
            response = client.post('/api/login', json={
                'email': 'test@example.com',
                'password': 'test123'
            })

            # Agregar producto al carrito
            response = client.post('/api/carrito/agregar', json={
                'producto_id': 1,
                'cantidad': 2
            })

            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['success'])
```

---

### FASE 8: DEPLOYMENT (1 semana)

#### 8.1 Configuración de Producción

**Gunicorn** (servidor WSGI):
```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

**Nginx** (reverse proxy):
```nginx
server {
    listen 80;
    server_name tudominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/app/static;
    }
}
```

**Supervisor** (mantener proceso corriendo):
```ini
[program:ecommerce_flask]
command=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 "app:create_app()"
directory=/path/to/ecommerce_flask
user=www-data
autostart=true
autorestart=true
```

---

## RESUMEN DE LO QUE NECESITO PARA MIGRACIÓN COMPLETA

### 📋 Checklist de Información Necesaria

#### ✅ Código Fuente
- [x] Todos los controladores PHP (leídos)
- [x] Todos los modelos PHP (leídos)
- [ ] **TODAS las vistas PHP completas** (necesito leer 100%)
- [x] JavaScript principal (carrito, productos, usuarios)
- [ ] **Todos los archivos JavaScript** (faltan algunos)

#### ⚠️ Configuraciones
- [ ] `.htaccess` completo con reglas de rewrite
- [ ] `php.ini` settings relevantes
- [ ] Variables de entorno
- [ ] Credenciales de producción (PayPal, PayU, SMTP)

#### ⚠️ Integraciones
- [ ] **Códigos completos de PayPal** (client_id, secret, webhooks)
- [ ] **Códigos completos de PayU** (merchant_id, api_key, account_id)
- [ ] **Configuración SMTP completa** (servidor, puerto, credenciales)
- [ ] APIs de terceros (geolocalización, conversión de divisas)

#### ⚠️ Templates y Assets
- [ ] Todos los templates HTML completos
- [ ] Estructura completa de CSS
- [ ] Todas las imágenes y assets
- [ ] Librerías JavaScript (versiones exactas)

#### ✅ Base de Datos
- [x] Estructura de todas las tablas
- [x] Relaciones y foreign keys
- [x] Datos de ejemplo
- [ ] Triggers, stored procedures (si existen)

---

## ESTIMACIÓN DE TIEMPO TOTAL

| Fase | Tiempo Estimado | Dependencias |
|------|----------------|--------------|
| 1. Análisis y Preparación | 1-2 semanas | Acceso completo al código |
| 2. Configuración Flask | 1 semana | - |
| 3. Migración BD | 1 semana | Fase 2 completa |
| 4. Migración Backend | 3-4 semanas | Fase 3 completa |
| 5. Migración Frontend | 2-3 semanas | Fase 4 completa |
| 6. Sistema de Correos | 1 semana | Credenciales SMTP |
| 7. Testing | 2 semanas | Fases 4-6 completas |
| 8. Deployment | 1 semana | Todo completo |
| **TOTAL** | **12-16 semanas** | **~3-4 meses** |

---

## CONCLUSIÓN

### ¿Entiendo el proyecto?

**SÍ**, al **85-90%**:
- ✅ Arquitectura MVC completa
- ✅ Lógica de negocio (backend)
- ✅ Flujos principales (productos, carrito, pagos, usuarios)
- ✅ Base de datos
- ✅ Seguridad y validaciones
- ✅ JavaScript del frontend (carrito, productos, usuarios)

**Necesito profundizar (10-15%)**:
- ⚠️ Vistas HTML completas (para templates Jinja2)
- ⚠️ Configuración exacta de servidor
- ⚠️ Detalles técnicos de integraciones de pago
- ⚠️ Sistema completo de emails
- ⚠️ Dependencias exactas y versiones

### ¿Puedo migrar el proyecto a Flask/Python?

**SÍ, completamente**. Con la información que ya tengo puedo migrar el **80%** del proyecto.

**Para completar el 20% restante necesito**:
1. Leer TODAS las vistas PHP para crear templates Jinja2
2. Ver configuraciones de servidor (.htaccess)
3. Obtener credenciales y códigos de producción
4. Verificar templates de emails
5. Confirmar versiones exactas de librerías

### Plan de Acción Inmediato

Si quieres que proceda con la migración:

1. **Puedo empezar YA** con:
   - Configuración inicial de Flask
   - Modelos SQLAlchemy (tengo estructura completa)
   - Migración de controladores principales
   - API endpoints para AJAX
   - Utilidades (procesamiento de imágenes, validaciones)

2. **Necesito que me proporciones**:
   - Acceso para leer archivos faltantes
   - Credenciales de desarrollo (puedo usar sandbox)
   - Decisión sobre hosting (Heroku, DigitalOcean, AWS, etc.)

3. **Cronograma sugerido**:
   - **Semanas 1-2**: Setup completo + modelos
   - **Semanas 3-6**: Backend admin completo
   - **Semanas 7-9**: Frontend shop + carrito
   - **Semanas 10-12**: Testing + deployment

¿Quieres que proceda con la migración? ¿O prefieres que primero complete la documentación leyendo los archivos faltantes?
