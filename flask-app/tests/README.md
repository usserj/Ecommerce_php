# Testing Suite - Flask E-commerce

Suite completa de tests para la aplicación Flask de e-commerce.

## 📋 Tabla de Contenidos

- [Instalación](#instalación)
- [Ejecución de Tests](#ejecución-de-tests)
- [Estructura de Tests](#estructura-de-tests)
- [Cobertura de Código](#cobertura-de-código)
- [Fixtures](#fixtures)
- [Marcadores de Tests](#marcadores-de-tests)
- [CI/CD Integration](#cicd-integration)

## 🔧 Instalación

### 1. Instalar dependencias de testing

```bash
cd flask-app
pip install -r requirements-dev.txt
```

### 2. Configurar variables de entorno para testing

```bash
export FLASK_ENV=testing
export DATABASE_URL=sqlite:///:memory:
```

## 🚀 Ejecución de Tests

### Ejecutar todos los tests

```bash
pytest
```

### Ejecutar con cobertura

```bash
pytest --cov=app --cov-report=html
```

### Ejecutar tests específicos

```bash
# Por archivo
pytest tests/test_models.py

# Por clase
pytest tests/test_models.py::TestUsuarioModel

# Por función
pytest tests/test_models.py::TestUsuarioModel::test_create_user

# Por marcador
pytest -m unit          # Solo tests unitarios
pytest -m integration   # Solo tests de integración
pytest -m "not slow"    # Excluir tests lentos
```

### Ejecutar con verbosidad

```bash
# Verboso
pytest -v

# Muy verboso
pytest -vv

# Mostrar print statements
pytest -s
```

### Ejecutar en paralelo (más rápido)

```bash
pip install pytest-xdist
pytest -n auto  # Usa todos los CPU cores
pytest -n 4     # Usa 4 workers
```

## 📁 Estructura de Tests

```
tests/
├── __init__.py
├── conftest.py              # Configuración y fixtures
├── README.md                # Esta documentación
│
├── test_models.py           # Tests unitarios de modelos
├── test_auth_routes.py      # Tests de autenticación
├── test_cart_routes.py      # Tests de carrito/checkout
├── test_services.py         # Tests de servicios
│
└── [Futuros tests]
    ├── test_shop_routes.py      # Tests de tienda
    ├── test_profile_routes.py   # Tests de perfil
    ├── test_admin_routes.py     # Tests de admin
    └── test_api.py              # Tests de API REST
```

## 📊 Cobertura de Tests

### Generar reporte de cobertura

```bash
# HTML (recomendado)
pytest --cov=app --cov-report=html
open htmlcov/index.html  # Ver reporte en navegador

# Terminal
pytest --cov=app --cov-report=term-missing

# XML (para CI/CD)
pytest --cov=app --cov-report=xml
```

### Objetivos de cobertura

- **Modelos**: >90%
- **Servicios**: >85%
- **Rutas**: >80%
- **Total**: >85%

### Ver cobertura actual

```bash
pytest --cov=app --cov-report=term
```

## 🔧 Fixtures

Las fixtures están definidas en `conftest.py` y están disponibles automáticamente para todos los tests.

### Fixtures de Aplicación

```python
def test_example(app, client):
    """app: Instancia de Flask app
       client: Cliente de testing"""
    response = client.get('/')
    assert response.status_code == 200
```

### Fixtures de Base de Datos

```python
def test_with_db(db_session, init_database):
    """db_session: Sesión de SQLAlchemy
       init_database: DB inicializada con datos de prueba"""
    from app.models.user import Usuario
    user = Usuario.query.first()
    assert user is not None
```

### Fixtures de Usuarios

```python
def test_authenticated(authenticated_client, test_user):
    """authenticated_client: Cliente con sesión iniciada
       test_user: Usuario de prueba"""
    response = authenticated_client.get('/profile/dashboard')
    assert response.status_code == 200
```

### Fixtures de Productos

```python
def test_product(test_producto, test_producto_oferta):
    """test_producto: Producto normal
       test_producto_oferta: Producto con descuento"""
    assert test_producto_oferta.is_on_offer() is True
```

### Fixtures de Mock

```python
def test_email(mock_email_send):
    """mock_email_send: Mock para envío de emails"""
    send_email('test@example.com', 'Subject', 'Body')
    assert mock_email_send.called

def test_oauth(mock_oauth_google):
    """mock_oauth_google: Mock para OAuth de Google"""
    # Test OAuth flow
```

### Fixtures Disponibles

| Fixture | Tipo | Descripción |
|---------|------|-------------|
| `app` | Aplicación | Instancia Flask |
| `client` | Aplicación | Test client |
| `db_session` | Base de Datos | Sesión SQLAlchemy |
| `init_database` | Base de Datos | DB con datos iniciales |
| `test_user` | Usuario | Usuario de prueba |
| `test_admin` | Usuario | Admin de prueba |
| `authenticated_client` | Usuario | Cliente autenticado |
| `admin_client` | Usuario | Cliente admin autenticado |
| `test_categoria` | Producto | Categoría de prueba |
| `test_producto` | Producto | Producto de prueba |
| `test_producto_oferta` | Producto | Producto con oferta |
| `test_compra` | Orden | Compra de prueba |
| `test_comentario` | Comentario | Comentario de prueba |
| `test_deseo` | Wishlist | Item de wishlist |
| `client_with_cart` | Carrito | Cliente con carrito |
| `mock_email_send` | Mock | Mock de email |
| `mock_paypal_payment` | Mock | Mock de PayPal |
| `mock_oauth_google` | Mock | Mock de Google OAuth |
| `mock_oauth_facebook` | Mock | Mock de Facebook OAuth |

## 🏷️ Marcadores de Tests

Los tests están categorizados con marcadores para facilitar su ejecución:

### Por Tipo

```bash
pytest -m unit          # Tests unitarios
pytest -m integration   # Tests de integración
pytest -m functional    # Tests funcionales
```

### Por Componente

```bash
pytest -m models        # Tests de modelos
pytest -m blueprints    # Tests de rutas
pytest -m services      # Tests de servicios
```

### Por Funcionalidad

```bash
pytest -m auth          # Tests de autenticación
pytest -m cart          # Tests de carrito
pytest -m payment       # Tests de pagos
pytest -m email         # Tests de email
```

### Por Velocidad

```bash
pytest -m "not slow"    # Excluir tests lentos
pytest -m slow          # Solo tests lentos
```

### Combinar Marcadores

```bash
# Tests unitarios de modelos
pytest -m "unit and models"

# Tests de integración excepto lentos
pytest -m "integration and not slow"

# Tests de autenticación y carrito
pytest -m "auth or cart"
```

## 📝 Escribir Nuevos Tests

### Template para Test Unitario

```python
import pytest
from app.models.user import Usuario

@pytest.mark.unit
@pytest.mark.models
class TestMyFeature:
    """Tests for my feature"""

    def test_feature_works(self, db_session):
        """Test that feature works as expected"""
        # Arrange
        user = Usuario(nombre='Test', email='test@test.com')
        db_session.add(user)
        db_session.commit()

        # Act
        result = user.some_method()

        # Assert
        assert result is not None
```

### Template para Test de Integración

```python
import pytest

@pytest.mark.integration
@pytest.mark.blueprints
class TestMyRoute:
    """Tests for my route"""

    def test_route_returns_200(self, client):
        """Test route returns 200"""
        response = client.get('/my-route')
        assert response.status_code == 200

    def test_route_requires_auth(self, client):
        """Test route requires authentication"""
        response = client.get('/protected-route', follow_redirects=True)
        assert b'login' in response.data.lower()

    def test_route_with_auth(self, authenticated_client):
        """Test route with authentication"""
        response = authenticated_client.get('/protected-route')
        assert response.status_code == 200
```

### Mejores Prácticas

1. **AAA Pattern**: Arrange, Act, Assert
   ```python
   def test_example():
       # Arrange: Preparar datos
       user = create_user()

       # Act: Ejecutar función
       result = user.do_something()

       # Assert: Verificar resultado
       assert result == expected
   ```

2. **Nombres Descriptivos**
   ```python
   # ✅ Bueno
   def test_user_cannot_login_with_wrong_password(self):
       ...

   # ❌ Malo
   def test_login(self):
       ...
   ```

3. **Un Assert por Concepto**
   ```python
   # ✅ Bueno
   def test_user_creation():
       user = Usuario(nombre='Test', email='test@test.com')
       assert user.nombre == 'Test'

   def test_user_email():
       user = Usuario(nombre='Test', email='test@test.com')
       assert user.email == 'test@test.com'

   # ❌ Malo (demasiados asserts)
   def test_user():
       user = Usuario(nombre='Test', email='test@test.com')
       assert user.nombre == 'Test'
       assert user.email == 'test@test.com'
       assert user.activo is True
       # etc...
   ```

4. **Usar Fixtures en lugar de Setup/Teardown**
   ```python
   # ✅ Bueno
   def test_with_user(test_user):
       assert test_user.nombre == 'Test User'

   # ❌ Malo
   def test_user(self):
       self.user = Usuario(...)
       assert self.user.nombre == 'Test'
       # teardown manual
   ```

## 🔄 CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

### GitLab CI

```yaml
# .gitlab-ci.yml
test:
  stage: test
  image: python:3.9
  script:
    - pip install -r requirements-dev.txt
    - pytest --cov=app --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

## 🐛 Debugging Tests

### Ejecutar con debugger

```bash
# Usar pytest con --pdb
pytest --pdb  # Para al primer fallo

# Usar ipdb
pip install ipdb
pytest --pdbcls=IPython.terminal.debugger:TerminalPdb
```

### Ver output detallado

```bash
# Mostrar prints
pytest -s

# Mostrar logs
pytest --log-cli-level=DEBUG

# Mostrar warnings
pytest -W all
```

### Ejecutar un solo test con debug

```python
# Agregar breakpoint en el test
def test_example():
    import pdb; pdb.set_trace()
    # o en Python 3.7+
    breakpoint()
    assert True
```

## 📈 Métricas de Calidad

### Ejecutar linters

```bash
# Flake8
flake8 app/ tests/

# Black (formatter)
black --check app/ tests/

# isort (imports)
isort --check app/ tests/

# Pylint
pylint app/

# Type checking
mypy app/
```

### Security scan

```bash
# Bandit (security)
bandit -r app/

# Safety (dependencies)
safety check
```

## 🔍 Troubleshooting

### Tests fallan con error de imports

```bash
# Asegúrate de estar en el directorio correcto
cd flask-app

# Instala la app en modo editable
pip install -e .
```

### Base de datos no se crea

```bash
# Verifica que DATABASE_URL esté configurado
export DATABASE_URL=sqlite:///:memory:

# O usa la configuración de testing
export FLASK_ENV=testing
```

### Fixtures no se encuentran

```bash
# Verifica que conftest.py esté en tests/
ls tests/conftest.py

# Ejecuta con -v para ver fixtures disponibles
pytest --fixtures
```

## 📚 Recursos Adicionales

- [Pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/2.3.x/testing/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Factory Boy Documentation](https://factoryboy.readthedocs.io/)

## ✅ Checklist de Testing

Antes de hacer commit:

- [ ] Todos los tests pasan
- [ ] Cobertura >85%
- [ ] No hay warnings
- [ ] Linters pasan (flake8, black, isort)
- [ ] Tests nuevos para features nuevos
- [ ] Documentación actualizada

```bash
# Ejecutar todo
pytest && flake8 app/ tests/ && black --check app/ tests/ && isort --check app/ tests/
```

---

**🎯 Happy Testing!**
