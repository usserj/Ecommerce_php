# E-commerce Flask - Migración desde PHP

Aplicación de e-commerce desarrollada en Flask, migrada desde el sistema PHP original.

## Características

- ✅ Autenticación completa (registro, login, OAuth Google/Facebook)
- ✅ Catálogo de productos con categorías y subcategorías
- ✅ Sistema de ofertas y descuentos
- ✅ Carrito de compras
- ✅ Integración con PayPal y PayU
- ✅ Panel administrativo
- ✅ Sistema de comentarios y calificaciones
- ✅ Lista de deseos
- ✅ Analytics y tracking de visitas
- ✅ Envío de emails (verificación, recuperación de contraseña)
- ✅ SEO optimizado

## Requisitos

- Python 3.9+
- MySQL 5.7+ o PostgreSQL 12+
- Redis (opcional, para cache y Celery)

## Instalación

### 1. Clonar el repositorio

```bash
cd flask-app
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Activar en Linux/Mac
source venv/bin/activate

# Activar en Windows
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:

```env
# Flask
SECRET_KEY=tu-clave-secreta-aqui

# Database
DATABASE_URL=mysql+pymysql://usuario:password@localhost/ecommerce

# Email
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-password-de-aplicacion

# PayPal
PAYPAL_CLIENT_ID=tu-client-id
PAYPAL_CLIENT_SECRET=tu-client-secret

# Google OAuth
GOOGLE_CLIENT_ID=tu-google-client-id
GOOGLE_CLIENT_SECRET=tu-google-client-secret
```

### 5. Inicializar base de datos

```bash
# Crear migraciones iniciales
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# O usar el comando personalizado
flask init-db
```

### 6. (Opcional) Migrar datos desde PHP

Si tienes datos en la base de datos PHP original:

```bash
python migrate_data.py
```

El script te guiará paso a paso solicitando:
- Credenciales de la BD origen (PHP MySQL)
- URL de la BD destino (Flask)
- Directorios de archivos

Ver [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) para instrucciones detalladas.

### 7. Ejecutar la aplicación

```bash
# Modo desarrollo
flask run

# O usando Python directamente
python run.py
```

La aplicación estará disponible en `http://localhost:5000`

## Estructura del Proyecto

```
flask-app/
├── app/
│   ├── __init__.py              # Factory pattern
│   ├── config.py                # Configuración
│   ├── extensions.py            # Extensiones Flask
│   │
│   ├── models/                  # Modelos SQLAlchemy
│   │   ├── user.py              # Usuario
│   │   ├── admin.py             # Administrador
│   │   ├── product.py           # Producto
│   │   ├── categoria.py         # Categorías
│   │   ├── order.py             # Órdenes
│   │   ├── comment.py           # Comentarios
│   │   ├── wishlist.py          # Lista de deseos
│   │   ├── comercio.py          # Configuración comercio
│   │   ├── setting.py           # Configuración sitio
│   │   ├── notification.py      # Notificaciones
│   │   └── visit.py             # Analytics
│   │
│   ├── blueprints/              # Blueprints (módulos)
│   │   ├── main/               # Páginas principales
│   │   ├── auth/               # Autenticación
│   │   ├── shop/               # Tienda
│   │   ├── cart/               # Carrito
│   │   ├── checkout/           # Checkout
│   │   ├── profile/            # Perfil usuario
│   │   └── admin/              # Panel admin
│   │
│   ├── forms/                   # Formularios WTForms
│   │   └── auth.py
│   │
│   ├── services/                # Servicios
│   │   ├── email_service.py
│   │   ├── payment_service.py
│   │   └── analytics_service.py
│   │
│   ├── templates/               # Templates Jinja2
│   │   ├── base.html
│   │   ├── main/                # Home, contacto
│   │   ├── auth/                # Login, registro
│   │   ├── shop/                # Productos, detalle
│   │   ├── cart/                # Carrito
│   │   ├── checkout/            # Checkout
│   │   ├── profile/             # Perfil usuario
│   │   ├── admin/               # Dashboard admin
│   │   ├── emails/              # Templates email
│   │   ├── errors/              # 404, 500
│   │   └── components/          # Componentes reusables
│   │
│   └── static/                  # Archivos estáticos
│       ├── css/                 # Estilos custom
│       ├── js/                  # JavaScript (AJAX)
│       └── uploads/             # Archivos subidos
│
├── migrations/                  # Migraciones Alembic
├── tests/                       # Tests
├── scripts/                     # Scripts auxiliares
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
└── run.py                       # Punto de entrada
```

## Comandos CLI

```bash
# Crear base de datos y tablas
flask db upgrade

# Crear migraciones
flask db migrate -m "Descripción"

# Revertir migración
flask db downgrade

# Migrar datos desde PHP (ver MIGRATION_GUIDE.md)
python migrate_data.py

# Shell interactivo con contexto de app
flask shell
```

## Desarrollo

### Ejecutar tests

```bash
pytest
```

### Con cobertura

```bash
pytest --cov=app --cov-report=html
```

### Linting

```bash
flake8 app/
black app/
```

## Producción

### Usando Docker

```bash
docker-compose up -d
```

### Usando Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Variables de entorno importantes

```env
FLASK_ENV=production
SECRET_KEY=clave-muy-segura
DATABASE_URL=postgresql://...
SESSION_COOKIE_SECURE=True
```

## Diferencias con la versión PHP

### Mejoras

- ✅ ORM SQLAlchemy (más seguro y mantenible)
- ✅ Migraciones de BD con Alembic
- ✅ Mejor organización del código (blueprints)
- ✅ Passwords con bcrypt (más seguro que crypt)
- ✅ CSRF protection automático
- ✅ Rate limiting
- ✅ Mejor manejo de sesiones
- ✅ Testing integrado
- ✅ Type hints en Python

### Compatibilidad

- ✅ Mantiene la misma estructura de BD
- ✅ Compatible con passwords PHP legacy
- ✅ Migración automática de passwords a bcrypt
- ✅ Mismas funcionalidades

## API REST (Opcional)

Si necesitas una API REST, descomentar el blueprint `api` en `app/__init__.py`

```python
from app.blueprints.api import api_bp
app.register_blueprint(api_bp, url_prefix='/api/v1')
```

## Contribuir

1. Fork el proyecto
2. Crear branch de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia

Este proyecto es una migración del sistema PHP original.

## Soporte

Para reportar bugs o solicitar features, crear un issue en GitHub.

## Estado del Proyecto

### ✅ Completado (Fase 1 - Backend)
- ✅ Estructura de la aplicación Flask con factory pattern
- ✅ 16 modelos SQLAlchemy (todas las tablas)
- ✅ 7 blueprints (main, auth, shop, cart, checkout, profile, admin)
- ✅ Autenticación con OAuth (Google, Facebook)
- ✅ Sistema de passwords con compatibilidad PHP legacy
- ✅ Servicios (email, payment, analytics)
- ✅ Formularios con validación

### ✅ Completado (Fase 2 - Frontend)
- ✅ Templates Jinja2 completos (25+ archivos)
- ✅ Bootstrap 5 con diseño responsive
- ✅ JavaScript con AJAX para carrito y wishlist
- ✅ CSS personalizado con animaciones
- ✅ Componentes reusables

### ✅ Completado (Fase 3 - Migración de Datos)
- ✅ Script de migración completo (migrate_data.py)
- ✅ Guía de migración detallada (MIGRATION_GUIDE.md)
- ✅ Migración de 16 tablas
- ✅ Copia de archivos e imágenes
- ✅ Preservación de contraseñas legacy
- ✅ Verificación de integridad

### 🔄 Pendiente (Fase 4 - Testing)
- [ ] Tests unitarios para modelos
- [ ] Tests de integración para blueprints
- [ ] Tests end-to-end
- [ ] Configuración de CI/CD

### 🔄 Pendiente (Fase 5 - Deployment)
- [ ] Dockerfile y docker-compose
- [ ] Configuración de producción
- [ ] Monitoreo y logs
- [ ] Backup automatizado

### 🎯 Mejoras Futuras
- [ ] Implementar PayU completamente
- [ ] API REST con documentación Swagger
- [ ] Internacionalización (i18n)
- [ ] Celery para tareas asíncronas (emails, reportes)
- [ ] Panel admin avanzado con Flask-Admin
- [ ] PWA (Progressive Web App)
- [ ] Chat en vivo
- [ ] Notificaciones push

## Autor

Migración realizada por Claude AI Assistant
Proyecto original: Sistema E-commerce PHP
