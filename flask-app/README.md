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

Si tienes datos en la base de datos PHP:

```bash
# Editar DATABASE_URL en .env para apuntar a la BD antigua
# Luego ejecutar:
flask migrate-data
```

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
│   │   └── (pendiente)
│   │
│   └── static/                  # Archivos estáticos
│       └── (pendiente)
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
# Inicializar base de datos
flask init-db

# Migrar datos desde PHP
flask migrate-data

# Crear migraciones
flask db migrate -m "Descripción"

# Aplicar migraciones
flask db upgrade

# Revertir migración
flask db downgrade
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

## TODO

- [ ] Completar templates Jinja2
- [ ] Implementar PayU completamente
- [ ] Agregar más tests
- [ ] Documentar API REST
- [ ] Agregar internacionalización (i18n)
- [ ] Implementar Celery para tareas asíncronas
- [ ] Agregar panel de administración avanzado (Flask-Admin)

## Autor

Migración realizada por Claude AI Assistant
Proyecto original: Sistema E-commerce PHP
