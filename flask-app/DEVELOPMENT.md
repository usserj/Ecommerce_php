# 🛠️ Guía de Desarrollo - E-commerce Ecuador

## 📋 Tabla de Contenidos
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Arquitectura Modular (Estilo Odoo)](#arquitectura-modular)
- [Agregar Nuevas Funcionalidades](#agregar-nuevas-funcionalidades)
- [Modelos de Base de Datos](#modelos-de-base-de-datos)
- [Sistema de Blueprints](#sistema-de-blueprints)
- [Servicios](#servicios)
- [Testing](#testing)

---

## 🏗️ Estructura del Proyecto

```
flask-app/
├── app/
│   ├── blueprints/          # Módulos funcionales (estilo Odoo)
│   │   ├── admin/          # Panel administrativo
│   │   ├── auth/           # Autenticación
│   │   ├── cart/           # Carrito de compras
│   │   ├── checkout/       # Proceso de pago
│   │   ├── main/           # Rutas principales
│   │   ├── payment/        # Pasarelas de pago
│   │   ├── profile/        # Perfil de usuario
│   │   └── shop/           # Catálogo y productos
│   ├── models/              # Modelos ORM (similar a Odoo models)
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── comment.py
│   │   ├── wishlist.py
│   │   └── ...
│   ├── services/            # Lógica de negocio (similar a Odoo services)
│   │   ├── email_service.py
│   │   ├── payment_service.py
│   │   ├── ai_service.py
│   │   └── ...
│   ├── static/              # Assets estáticos
│   │   ├── css/
│   │   ├── js/
│   │   └── uploads/
│   ├── templates/           # Vistas (similar a Odoo views)
│   ├── utils/               # Utilidades y helpers
│   ├── config.py            # Configuración central
│   ├── extensions.py        # Extensiones Flask (db, mail, etc.)
│   └── __init__.py          # Factory de la aplicación
├── migrations/              # Migraciones SQL
├── logs/                    # Logs estructurados
├── tests/                   # Tests unitarios y de integración
└── run.py                   # Punto de entrada
```

---

## 🧩 Arquitectura Modular (Estilo Odoo)

Esta aplicación sigue principios de arquitectura similares a **Odoo ERP**:

### 1. **Separación de Responsabilidades**
- **Models**: Definición de datos y lógica de dominio
- **Services**: Lógica de negocio compleja
- **Blueprints**: Controladores/rutas HTTP
- **Templates**: Presentación

### 2. **Modularidad por Funcionalidad**
Cada blueprint es un módulo independiente con su propia lógica:

```python
# Ejemplo: blueprints/shop/
shop/
├── __init__.py       # Registro del blueprint
├── routes.py         # Rutas HTTP
└── forms.py          # Formularios (si aplica)
```

### 3. **Extensibilidad**
Agregar nuevas funcionalidades es tan simple como:
1. Crear un nuevo blueprint
2. Definir modelos necesarios
3. Registrar en `app/__init__.py`

---

## ➕ Agregar Nuevas Funcionalidades

### Ejemplo: Agregar Sistema de Puntos de Lealtad

#### **Paso 1: Crear Modelo**
```python
# app/models/loyalty.py
from datetime import datetime
from app.extensions import db

class LoyaltyPoints(db.Model):
    """Modelo de puntos de lealtad."""
    __tablename__ = 'loyalty_points'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    points = db.Column(db.Integer, default=0)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def add_points(self, amount, reason):
        """Agregar puntos con auditoría."""
        self.points += amount
        # Registrar en log
        db.session.commit()

    def redeem_points(self, amount):
        """Canjear puntos."""
        if self.points >= amount:
            self.points -= amount
            db.session.commit()
            return True
        return False
```

#### **Paso 2: Crear Migración**
```sql
-- migrations/003_loyalty_points.sql
CREATE TABLE IF NOT EXISTS loyalty_points (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    points INT DEFAULT 0,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE CASCADE
);
```

#### **Paso 3: Crear Blueprint**
```python
# app/blueprints/loyalty/__init__.py
from flask import Blueprint

loyalty_bp = Blueprint('loyalty', __name__, url_prefix='/loyalty')

from app.blueprints.loyalty import routes
```

```python
# app/blueprints/loyalty/routes.py
from flask import render_template, jsonify
from flask_login import login_required, current_user
from app.blueprints.loyalty import loyalty_bp
from app.models.loyalty import LoyaltyPoints

@loyalty_bp.route('/')
@login_required
def index():
    """Ver puntos del usuario."""
    points = LoyaltyPoints.query.filter_by(user_id=current_user.id).first()
    return render_template('loyalty/index.html', points=points)

@loyalty_bp.route('/redeem', methods=['POST'])
@login_required
def redeem():
    """Canjear puntos."""
    # Lógica de canje
    pass
```

#### **Paso 4: Registrar Blueprint**
```python
# app/__init__.py
def register_blueprints(app):
    # ... blueprints existentes ...
    from app.blueprints.loyalty import loyalty_bp
    app.register_blueprint(loyalty_bp)
```

#### **Paso 5: Crear Template**
```html
<!-- app/templates/loyalty/index.html -->
{% extends "base.html" %}
{% block content %}
<h1>Mis Puntos de Lealtad</h1>
<p>Puntos disponibles: {{ points.points if points else 0 }}</p>
{% endblock %}
```

---

## 💾 Modelos de Base de Datos

### Convenciones de Nomenclatura

1. **Nombres de Tablas**: Snake_case, plural en español
   - ✅ `usuarios`, `productos`, `compras`
   - ❌ `User`, `product`, `orders`

2. **Nombres de Columnas**: Snake_case en español
   - ✅ `id_usuario`, `fecha_creacion`, `precio_total`
   - ❌ `userID`, `createdAt`, `totalPrice`

3. **Relaciones**: Usar nombres descriptivos
```python
# ✅ Correcto
class Usuario(db.Model):
    compras = db.relationship('Compra', backref='usuario', lazy='dynamic')

# ❌ Evitar
class User(db.Model):
    orders = db.relationship('Order', backref='user', lazy='dynamic')
```

### Ejemplo de Modelo Completo

```python
"""Modelo de Producto con todas las mejores prácticas."""
from datetime import datetime
from app.extensions import db

class Producto(db.Model):
    """
    Modelo de producto.

    Attributes:
        id: ID único del producto
        titulo: Nombre del producto
        precio: Precio en USD
        stock: Cantidad disponible
        estado: 1=activo, 0=inactivo
    """
    __tablename__ = 'productos'

    # Columnas
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False, index=True)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    estado = db.Column(db.Integer, default=1, index=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    comentarios = db.relationship('Comentario', backref='producto', lazy='dynamic', cascade='all, delete-orphan')
    compras = db.relationship('Compra', backref='producto', lazy='dynamic')

    # Métodos de instancia
    def is_available(self):
        """Verificar si el producto está disponible."""
        return self.estado == 1 and self.stock > 0

    def decrement_stock(self, cantidad):
        """Decrementar stock con validación."""
        if self.stock >= cantidad:
            self.stock -= cantidad
            db.session.commit()
            return True
        return False

    def increment_stock(self, cantidad):
        """Incrementar stock."""
        self.stock += cantidad
        db.session.commit()

    # Métodos de clase
    @classmethod
    def get_active_products(cls):
        """Obtener todos los productos activos."""
        return cls.query.filter_by(estado=1).all()

    @classmethod
    def search(cls, query):
        """Búsqueda de productos."""
        return cls.query.filter(
            cls.titulo.ilike(f'%{query}%'),
            cls.estado == 1
        ).all()

    def __repr__(self):
        return f'<Producto {self.id}: {self.titulo}>'
```

---

## 🔌 Sistema de Blueprints

### Anatomía de un Blueprint

```python
# app/blueprints/ejemplo/__init__.py
from flask import Blueprint

ejemplo_bp = Blueprint(
    'ejemplo',                    # Nombre del blueprint
    __name__,
    url_prefix='/ejemplo',        # Prefijo de URL
    template_folder='templates',  # Carpeta de templates (opcional)
    static_folder='static'        # Carpeta de statics (opcional)
)

from app.blueprints.ejemplo import routes
```

```python
# app/blueprints/ejemplo/routes.py
from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app.blueprints.ejemplo import ejemplo_bp
from app.extensions import db
from app.models.ejemplo import Ejemplo

@ejemplo_bp.route('/')
def index():
    """Página principal del módulo."""
    return render_template('ejemplo/index.html')

@ejemplo_bp.route('/api/data')
@login_required
def api_data():
    """Endpoint API del módulo."""
    data = Ejemplo.query.all()
    return jsonify([item.to_dict() for item in data])

@ejemplo_bp.route('/create', methods=['POST'])
@login_required
def create():
    """Crear nuevo registro."""
    data = request.get_json()
    nuevo = Ejemplo(**data)
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({'success': True, 'id': nuevo.id})
```

---

## 🔧 Servicios

Los servicios encapsulan lógica de negocio compleja:

```python
# app/services/loyalty_service.py
"""Servicio de puntos de lealtad."""
from app.extensions import db
from app.models.loyalty import LoyaltyPoints
from app.models.order import Compra
from app.utils.logger import log_user_action
import logging

logger = logging.getLogger('ecommerce')

class LoyaltyService:
    """Gestión de puntos de lealtad."""

    POINTS_PER_DOLLAR = 10  # 10 puntos por cada $1 gastado

    @staticmethod
    def award_points_for_order(order_id):
        """Otorgar puntos por compra."""
        try:
            order = Compra.query.get(order_id)
            if not order:
                return False

            # Calcular puntos
            points = int(order.get_total() * LoyaltyService.POINTS_PER_DOLLAR)

            # Buscar o crear registro de puntos
            loyalty = LoyaltyPoints.query.filter_by(user_id=order.id_usuario).first()
            if not loyalty:
                loyalty = LoyaltyPoints(user_id=order.id_usuario, points=0)
                db.session.add(loyalty)

            # Agregar puntos
            loyalty.add_points(points, f"Compra #{order.id}")

            log_user_action(logger, order.id_usuario, 'loyalty_points_awarded',
                          f"Otorgados {points} puntos por compra #{order.id}")

            return True
        except Exception as e:
            logger.error(f"Error awarding loyalty points: {e}")
            return False

    @staticmethod
    def redeem_points(user_id, points_to_redeem):
        """Canjear puntos por descuento."""
        loyalty = LoyaltyPoints.query.filter_by(user_id=user_id).first()
        if not loyalty:
            return None

        if loyalty.redeem_points(points_to_redeem):
            # Convertir puntos a descuento (100 puntos = $10)
            discount_amount = points_to_redeem / 10
            log_user_action(logger, user_id, 'loyalty_points_redeemed',
                          f"Canjeados {points_to_redeem} puntos por ${discount_amount}")
            return discount_amount

        return None
```

---

## 🧪 Testing

### Estructura de Tests

```python
# tests/test_loyalty.py
import pytest
from app import create_app, db
from app.models.user import User
from app.models.loyalty import LoyaltyPoints
from app.services.loyalty_service import LoyaltyService

@pytest.fixture
def app():
    """Crear app de testing."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente de testing."""
    return app.test_client()

def test_award_points(app):
    """Test: Otorgar puntos por compra."""
    with app.app_context():
        # Crear usuario y orden
        user = User(nombre='Test', email='test@test.com')
        db.session.add(user)
        db.session.commit()

        # Otorgar puntos
        success = LoyaltyService.award_points_for_order(order_id=1)
        assert success

        # Verificar puntos
        loyalty = LoyaltyPoints.query.filter_by(user_id=user.id).first()
        assert loyalty.points > 0
```

---

## 📝 Mejores Prácticas

### 1. **Logging Estructurado**
```python
from app.utils.logger import log_user_action
import logging

logger = logging.getLogger('ecommerce')

# ✅ Usar logging estructurado
log_user_action(logger, user_id=123, action='purchase', details='Order #456')

# ❌ Evitar prints
print(f"User {user_id} purchased order {order_id}")
```

### 2. **Manejo de Errores**
```python
# ✅ Manejo específico de errores
try:
    producto.decrement_stock(cantidad)
except InsufficientStockError as e:
    flash('Stock insuficiente', 'error')
    return redirect(url_for('shop.product', id=producto.id))
except Exception as e:
    logger.error(f"Error inesperado: {e}", exc_info=True)
    flash('Error al procesar la solicitud', 'error')
```

### 3. **Validación de Datos**
```python
# ✅ Validar siempre los datos de entrada
from app.utils.validators import validate_email, validate_phone

def create_user(data):
    if not validate_email(data['email']):
        raise ValueError('Email inválido')

    if not validate_phone(data['telefono']):
        raise ValueError('Teléfono inválido')

    # Crear usuario...
```

### 4. **Transacciones de Base de Datos**
```python
# ✅ Usar try-except para transacciones
try:
    db.session.add(nuevo_registro)
    db.session.commit()
except Exception as e:
    db.session.rollback()
    logger.error(f"Error guardando registro: {e}")
    raise
```

---

## 🚀 Comandos Útiles

```bash
# Ejecutar la aplicación
python run.py

# Ejecutar migraciones
python run_migration_simple.py

# Ejecutar tests
pytest tests/

# Linter
flake8 app/

# Ver logs en tiempo real
tail -f logs/app.log | jq
```

---

## 📚 Recursos Adicionales

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Odoo Development](https://www.odoo.com/documentation/16.0/developer.html)

---

**Mantenido por**: Equipo de Desarrollo E-commerce Ecuador
**Última actualización**: 2025-11-23
