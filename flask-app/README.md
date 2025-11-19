# 🛒 E-commerce Flask - Ecuador

Plataforma de comercio electrónico completa desarrollada en Flask.

---

## ✨ Características

### Frontend (Tienda):
- ✅ Catálogo de productos con categorías y subcategorías
- ✅ Sistema de ofertas y descuentos con cupones
- ✅ Carrito de compras con actualización en tiempo real
- ✅ Sistema de comentarios y calificaciones
- ✅ Lista de deseos
- ✅ Autenticación completa (registro, login, recuperación de contraseña)
- ✅ OAuth con Google y Facebook
- ✅ Perfil de usuario con historial de compras

### Backend (Administración):
- ✅ Panel administrativo completo
- ✅ Gestión de productos, categorías y subcategorías
- ✅ Sistema de cupones de descuento
- ✅ Gestión de órdenes y ventas
- ✅ Moderación de comentarios
- ✅ Analytics y tracking de visitas
- ✅ Gestión de usuarios
- ✅ Configuración de métodos de pago

### Pagos:
- ✅ PayPal
- ✅ Transferencia bancaria con comprobante
- ✅ Paymentez (Ecuador)
- ✅ Datafast (Ecuador)
- ✅ De Una (Ecuador)

### Funcionalidades Adicionales:
- ✅ Control de inventario automático
- ✅ Envío de emails (verificación, recuperación, notificaciones)
- ✅ SEO optimizado
- ✅ Responsive design
- ✅ Rate limiting para seguridad
- ✅ Hot-reload en desarrollo

---

## 📋 Requisitos

- **Python 3.10+**
- **MySQL 5.7+** (o compatible como MariaDB)
- **XAMPP** (para desarrollo local en Windows)

Opcional:
- Redis (para cache y tareas asíncronas)
- Celery (para procesamiento background)

---

## 🚀 Instalación

### 1. Verificar XAMPP
```bash
# Asegúrate de que XAMPP esté corriendo
# - Apache: Running
# - MySQL: Running
```

### 2. Instalar dependencias Python
```bash
cd flask-app
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
El archivo `.env` ya está configurado para desarrollo local. Si necesitas cambiar algo:
```bash
# Editar .env
DATABASE_URL=mysql+pymysql://root:@localhost/Ecommerce_Ec
```

### 4. Iniciar servidor
```bash
python run.py
```

El servidor iniciará en:
- **Local:** http://localhost:5000
- **Red:** http://[tu-ip]:5000
- **Admin:** http://localhost:5000/admin/login

---

## 📁 Estructura del Proyecto

```
flask-app/
├── app/
│   ├── blueprints/        # Rutas organizadas por módulo
│   │   ├── admin/         # Panel administrativo
│   │   ├── auth/          # Autenticación
│   │   ├── cart/          # Carrito de compras
│   │   ├── checkout/      # Proceso de pago
│   │   ├── main/          # Páginas principales
│   │   ├── profile/       # Perfil de usuario
│   │   └── shop/          # Catálogo de productos
│   ├── models/            # Modelos de base de datos
│   │   ├── user.py        # Usuario
│   │   ├── product.py     # Producto
│   │   ├── order.py       # Órdenes/compras
│   │   ├── comment.py     # Comentarios
│   │   ├── coupon.py      # Cupones
│   │   └── ...
│   ├── services/          # Lógica de negocio
│   │   ├── payment_service.py
│   │   ├── email_service.py
│   │   └── analytics_service.py
│   ├── templates/         # Templates HTML
│   ├── static/            # CSS, JS, imágenes
│   ├── forms/             # Formularios WTForms
│   ├── extensions.py      # Extensiones Flask
│   ├── config.py          # Configuración
│   └── __init__.py        # App factory
├── run.py                 # Entry point
├── requirements.txt       # Dependencias
├── .env                   # Variables de entorno
└── README.md              # Este archivo
```

---

## 🔧 Configuración

### Base de Datos
El sistema usa MySQL. La base de datos se inicializa automáticamente al primer arranque.

**Base de datos:** `Ecommerce_Ec`

### Métodos de Pago
Configura las credenciales de los gateways de pago en el panel de administración:
- Admin > Configuración > Métodos de Pago

### Email
Para activar el envío de emails, configura SMTP en `.env`:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-contraseña-app
```

### OAuth (Opcional)
Para activar login con Google/Facebook, configura las credenciales en `.env`:
```env
GOOGLE_CLIENT_ID=tu-client-id
GOOGLE_CLIENT_SECRET=tu-client-secret
```

---

## 👤 Acceso Inicial

### Usuario Admin por Defecto:
- **Email:** admin@ecommerce.ec
- **Contraseña:** admin123

⚠️ **IMPORTANTE:** Cambia la contraseña del admin después del primer login.

---

## 🛠️ Comandos Útiles

### Desarrollo
```bash
# Iniciar servidor en modo desarrollo (con hot-reload)
python run.py

# Verificar que el app funciona
python -c "from app import create_app; create_app()"
```

### Producción
```bash
# Usar Gunicorn (Linux/Mac)
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"

# Usar Waitress (Windows)
pip install waitress
waitress-serve --port=5000 --call app:create_app
```

---

## 🔒 Seguridad

Antes de deployment a producción:

1. ✅ Cambia `SECRET_KEY` en `.env` a un valor aleatorio seguro
2. ✅ Cambia credenciales del admin por defecto
3. ✅ Configura `SESSION_COOKIE_SECURE=True` si usas HTTPS
4. ✅ Actualiza `FLASK_ENV=production`
5. ✅ Revisa y limita rate limits según tu necesidad
6. ✅ Configura backup automático de la base de datos
7. ✅ Usa un servidor WSGI (Gunicorn, uWSGI) en lugar de Flask development server

---

## 📊 Base de Datos

### Tablas Principales:
- **usuarios** - Usuarios registrados
- **administradores** - Usuarios admin
- **productos** - Catálogo de productos
- **categorias** - Categorías de productos
- **subcategorias** - Subcategorías
- **compras** - Órdenes/ventas
- **comentarios** - Comentarios y calificaciones
- **cupones** - Cupones de descuento
- **deseos** - Lista de deseos
- **comercio** - Configuración de la tienda
- **notificaciones** - Contadores del sistema
- **visitas_pais** - Analytics por país
- **visitas_persona** - Tracking de visitas

---

## 🐛 Solución de Problemas

### Error: "Can't connect to MySQL server"
**Solución:** Verifica que XAMPP MySQL esté corriendo

### Error: "Address already in use"
**Solución:** Ya hay un servidor corriendo en el puerto 5000
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <numero> /F

# Linux/Mac
lsof -ti:5000 | xargs kill
```

### Error: "ModuleNotFoundError"
**Solución:** Instala las dependencias
```bash
pip install -r requirements.txt
```

---

## 📝 Tecnologías Utilizadas

### Backend:
- **Flask** 3.0.0 - Framework web
- **SQLAlchemy** 2.0.23 - ORM
- **Flask-Login** - Autenticación
- **Flask-WTF** - Formularios con CSRF
- **Flask-Limiter** - Rate limiting
- **Authlib** - OAuth

### Frontend:
- **Bootstrap 5** - UI Framework
- **jQuery** - JavaScript
- **Font Awesome** - Iconos

### Base de Datos:
- **MySQL** 5.7+ / **MariaDB**
- **PyMySQL** - Conector Python

### Pagos:
- **PayPal REST SDK**
- Integración con gateways ecuatorianos

---

## 📄 Licencia

Este proyecto es privado y confidencial.

---

## 👨‍💻 Soporte

Para soporte técnico, contacta al equipo de desarrollo.

---

**Desarrollado con ❤️ en Ecuador**
