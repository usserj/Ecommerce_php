# 🚀 Guía de Setup Local con VS Code

Guía paso a paso para ejecutar la aplicación Flask E-commerce en VS Code de manera local.

## 📋 Prerequisitos

### 1. Software Necesario

- **VS Code**: [Descargar aquí](https://code.visualstudio.com/)
- **Python 3.11+**: [Descargar aquí](https://www.python.org/downloads/)
- **MySQL 8.0+**: [Descargar aquí](https://dev.mysql.com/downloads/)
- **Git**: [Descargar aquí](https://git-scm.com/downloads)

### 2. Verificar Instalaciones

```bash
# Python
python3 --version  # Debe ser 3.11 o superior

# MySQL
mysql --version

# Git
git --version
```

## 🛠️ Instalación Paso a Paso

### Paso 1: Clonar el Repositorio (si no lo has hecho)

```bash
cd ~/proyectos  # o donde quieras tener el proyecto
git clone https://github.com/your-org/Ecommerce_php.git
cd Ecommerce_php/flask-app
```

### Paso 2: Abrir en VS Code

```bash
code .
```

O desde VS Code: `File > Open Folder` y selecciona `flask-app`

### Paso 3: Instalar Extensiones Recomendadas

VS Code te preguntará si quieres instalar las extensiones recomendadas. **Dale que sí**.

O manualmente:
1. Presiona `Ctrl+Shift+X` (o `Cmd+Shift+X` en Mac)
2. Busca e instala:
   - **Python** (Microsoft)
   - **Pylance** (Microsoft)
   - **Python Test Adapter**
   - **Jinja** (wholroyd.jinja)
   - **GitLens** (opcional pero útil)

### Paso 4: Crear Entorno Virtual

Abre la terminal integrada en VS Code (`Ctrl+` ` o ``Cmd+` ` en Mac):

```bash
# Crear virtualenv
python3 -m venv venv

# Activar virtualenv
# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate

# Deberías ver (venv) al inicio de tu línea de comando
```

**VS Code debería detectar automáticamente el virtualenv**. Si no:
1. Presiona `Ctrl+Shift+P` (o `Cmd+Shift+P`)
2. Escribe "Python: Select Interpreter"
3. Selecciona `./venv/bin/python`

### Paso 5: Instalar Dependencias Python

Con el virtualenv activado:

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar dependencias de producción
pip install -r requirements.txt

# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt
```

Esto tomará unos minutos. Verás algo como:
```
Successfully installed Flask-3.0.0 SQLAlchemy-2.0.23 ...
```

### Paso 6: Configurar MySQL

#### En Linux/Mac:

```bash
# Iniciar MySQL
sudo systemctl start mysql  # Linux
# o
brew services start mysql   # Mac

# Entrar a MySQL como root
mysql -u root -p
# (puede que no tenga password, solo presiona Enter)
```

#### En Windows:

Abre MySQL Workbench o la consola de MySQL.

#### Crear Base de Datos:

```sql
-- Crear base de datos
CREATE DATABASE ecommerce_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear usuario (opcional, puedes usar root)
CREATE USER 'ecommerce_user'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON ecommerce_dev.* TO 'ecommerce_user'@'localhost';
FLUSH PRIVILEGES;

-- Verificar
SHOW DATABASES;

-- Salir
EXIT;
```

### Paso 7: Instalar Redis (Opcional pero Recomendado)

#### En Linux:

```bash
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

#### En Mac:

```bash
brew install redis
brew services start redis
```

#### En Windows:

Descargar desde: https://github.com/microsoftarchive/redis/releases

O usar **WSL** (Windows Subsystem for Linux) para instalar Redis.

**Verificar:**
```bash
redis-cli ping
# Debe responder: PONG
```

### Paso 8: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Abrir en VS Code
code .env
```

Edita `.env` con estos valores **mínimos para local**:

```env
# ================================
# CONFIGURACIÓN LOCAL VS CODE
# ================================

# Flask
SECRET_KEY=dev-secret-key-change-this-in-production
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1

# Database
DATABASE_URL=mysql+pymysql://ecommerce_user:password123@localhost:3306/ecommerce_dev
# O si usas root:
# DATABASE_URL=mysql+pymysql://root:tu-password@localhost:3306/ecommerce_dev

# Redis (si lo instalaste)
REDIS_URL=redis://localhost:6379/0

# Email - Modo de prueba (los emails se imprimen en consola)
MAIL_SERVER=localhost
MAIL_PORT=25
MAIL_USE_TLS=False
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=noreply@localhost

# OAuth - Dejar vacío por ahora (opcional)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
FACEBOOK_CLIENT_ID=
FACEBOOK_CLIENT_SECRET=

# PayPal - Modo sandbox (pruebas)
PAYPAL_CLIENT_ID=test
PAYPAL_CLIENT_SECRET=test
PAYPAL_MODE=sandbox

# Otros
WTF_CSRF_ENABLED=True
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
```

**IMPORTANTE**: Cambia `password123` por la contraseña que pusiste en MySQL.

### Paso 9: Crear las Tablas de la Base de Datos

En la terminal de VS Code (con virtualenv activo):

```bash
# Inicializar migraciones (si es primera vez)
flask db init  # Solo la primera vez

# Crear migración inicial
flask db migrate -m "Initial migration"

# Aplicar migraciones
flask db upgrade

# O usar el comando directo
flask init-db
```

Deberías ver:
```
INFO  [alembic.runtime.migration] Running upgrade ...
Database initialized successfully.
```

**Verificar en MySQL:**
```bash
mysql -u ecommerce_user -p ecommerce_dev
# o
mysql -u root -p ecommerce_dev

# Dentro de MySQL:
SHOW TABLES;
# Deberías ver: usuarios, productos, categorias, etc.
```

### Paso 10: Crear Datos de Prueba

#### Opción A: Con Flask Shell

```bash
flask shell
```

Ejecuta este código:

```python
from app import db
from app.models.user import Usuario
from app.models.admin import Administrador
from app.models.categoria import Categoria
from app.models.product import Producto
from app.models.comercio import Comercio
from app.models.setting import Plantilla

# Crear usuario de prueba
user = Usuario(
    nombre='Usuario Test',
    email='test@test.com',
    verificado=True,
    activo=True
)
user.set_password('password123')
db.session.add(user)

# Crear admin
admin = Administrador(
    nombre='Admin',
    email='admin@test.com',
    rol='admin',
    activo=True
)
admin.set_password('admin123')
db.session.add(admin)

# Crear configuración de comercio
comercio = Comercio(
    nombre='Mi Tienda',
    email='tienda@test.com',
    telefono='123456789',
    moneda='USD',
    impuesto=10.0,
    costo_envio=5.0
)
db.session.add(comercio)

# Crear plantilla
plantilla = Plantilla(
    titulo='Mi Tienda Demo',
    color_primario='#007bff',
    color_secundario='#6c757d'
)
db.session.add(plantilla)

# Crear categoría
categoria = Categoria(
    nombre='Electrónica',
    descripcion='Productos electrónicos',
    estado=True
)
db.session.add(categoria)
db.session.commit()

# Crear productos
productos = [
    Producto(
        titulo='Laptop Dell XPS 13',
        descripcion='Laptop ultraligera con pantalla 4K',
        precio=1299.99,
        stock=15,
        categoria_id=categoria.id,
        estado=True,
        destacado=True
    ),
    Producto(
        titulo='iPhone 15 Pro',
        descripcion='Smartphone con chip A17 Pro',
        precio=999.99,
        precio_oferta=899.99,
        stock=30,
        categoria_id=categoria.id,
        estado=True,
        destacado=True
    ),
    Producto(
        titulo='AirPods Pro 2',
        descripcion='Auriculares con cancelación de ruido',
        precio=249.99,
        stock=50,
        categoria_id=categoria.id,
        estado=True
    ),
    Producto(
        titulo='Magic Keyboard',
        descripcion='Teclado inalámbrico para Mac',
        precio=99.99,
        precio_oferta=79.99,
        stock=25,
        categoria_id=categoria.id,
        estado=True
    ),
    Producto(
        titulo='Samsung Galaxy Watch 6',
        descripcion='Smartwatch con monitor de salud',
        precio=299.99,
        stock=20,
        categoria_id=categoria.id,
        estado=True,
        destacado=True
    )
]

for p in productos:
    db.session.add(p)

db.session.commit()

print("✅ Datos de prueba creados exitosamente!")
print(f"✅ {len(productos)} productos creados")
print(f"✅ Usuario: test@test.com / password123")
print(f"✅ Admin: admin@test.com / admin123")

exit()
```

## ▶️ Ejecutar la Aplicación

### Método 1: Desde la Terminal de VS Code

```bash
# Con virtualenv activado
flask run

# O con auto-reload
flask run --reload
```

Verás:
```
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Restarting with stat
```

### Método 2: Con el Debugger de VS Code (RECOMENDADO)

1. Ve a la pestaña "Run and Debug" (icono de play con bicho en la barra lateral)
2. Selecciona **"Flask: Run Development Server"**
3. Presiona el botón verde ▶️ o presiona `F5`

**Ventajas del debugger:**
- ✅ Puedes poner breakpoints
- ✅ Ver variables en tiempo real
- ✅ Step through code
- ✅ Console interactiva
- ✅ Auto-reload en cambios

### Método 3: Atajo de Teclado

Presiona `F5` directamente (seleccionará la configuración por defecto)

## 🌐 Acceder a la Aplicación

Una vez corriendo, abre tu navegador en:

- **Home**: http://127.0.0.1:5000
- **Login**: http://127.0.0.1:5000/auth/login
- **Register**: http://127.0.0.1:5000/auth/register
- **Productos**: http://127.0.0.1:5000/tienda/productos
- **Admin**: http://127.0.0.1:5000/admin
- **Health**: http://127.0.0.1:5000/health

**Credenciales de prueba:**
- Usuario: `test@test.com` / `password123`
- Admin: `admin@test.com` / `admin123`

## 🐛 Debugging en VS Code

### Poner Breakpoints

1. Abre un archivo Python (ej: `app/blueprints/auth/routes.py`)
2. Haz clic en el margen izquierdo junto al número de línea
3. Aparecerá un punto rojo
4. Ejecuta la app con `F5`
5. Cuando el código llegue a esa línea, se detendrá

### Inspeccionar Variables

Cuando el debugger se detiene:
- **VARIABLES**: Panel izquierdo muestra todas las variables
- **WATCH**: Agrega expresiones para monitorear
- **CALL STACK**: Ve la pila de llamadas
- **DEBUG CONSOLE**: Ejecuta código Python en el contexto actual

### Comandos del Debugger

- `F5`: Continue
- `F10`: Step Over (siguiente línea)
- `F11`: Step Into (entrar a función)
- `Shift+F11`: Step Out (salir de función)
- `Ctrl+Shift+F5`: Restart
- `Shift+F5`: Stop

## 🧪 Ejecutar Tests en VS Code

### Método 1: Desde el Testing Panel

1. Ve a la pestaña "Testing" (icono de matraz en la barra lateral)
2. VS Code debería detectar automáticamente los tests
3. Haz clic en ▶️ junto a un test para ejecutarlo
4. O haz clic en "Run All Tests"

### Método 2: Desde Terminal

```bash
# Todos los tests
pytest

# Con verbosidad
pytest -v

# Solo tests unitarios
pytest -m unit

# Con coverage
pytest --cov=app --cov-report=html
```

### Método 3: Con Debugger

1. Ve a "Run and Debug"
2. Selecciona **"Python: Run Tests"**
3. Presiona F5
4. Puedes poner breakpoints en los tests

## 📝 Comandos Útiles de Flask

```bash
# Flask shell interactivo
flask shell

# Ver rutas disponibles
flask routes

# Crear migraciones
flask db migrate -m "Descripción del cambio"

# Aplicar migraciones
flask db upgrade

# Revertir migración
flask db downgrade

# Inicializar BD
flask init-db
```

## 🛠️ Atajos de VS Code Útiles

| Atajo | Acción |
|-------|--------|
| `Ctrl+` ` | Abrir/cerrar terminal |
| `Ctrl+Shift+P` | Command Palette |
| `Ctrl+P` | Quick Open (buscar archivos) |
| `Ctrl+Shift+F` | Buscar en archivos |
| `Ctrl+B` | Toggle sidebar |
| `F5` | Start debugging |
| `Ctrl+Shift+D` | Debug view |
| `Ctrl+Shift+E` | Explorer view |
| `Ctrl+Shift+G` | Source Control (Git) |
| `Ctrl+K Ctrl+S` | Keyboard shortcuts |
| `Ctrl+Shift+X` | Extensions |

## 🔍 Troubleshooting

### Error: "No module named 'flask'"

**Solución:**
```bash
# Verificar que el virtualenv esté activo
which python  # Debe mostrar .../venv/bin/python

# Si no está activo
source venv/bin/activate

# Reinstalar
pip install -r requirements.txt
```

### Error: "Access denied for user"

**Solución:**
```bash
# Verificar credenciales en .env
# Asegúrate que coincidan con las de MySQL

# Probar conexión
mysql -u ecommerce_user -p
# Ingresa la contraseña

# Si falla, recrear usuario:
mysql -u root -p
CREATE USER 'ecommerce_user'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON ecommerce_dev.* TO 'ecommerce_user'@'localhost';
FLUSH PRIVILEGES;
```

### Error: "Port 5000 already in use"

**Solución:**
```bash
# Ver qué está usando el puerto
lsof -i :5000

# Matar el proceso
kill -9 <PID>

# O usar otro puerto
flask run --port 5001
```

### VS Code no detecta el virtualenv

**Solución:**
1. `Ctrl+Shift+P`
2. "Python: Select Interpreter"
3. Selecciona `./venv/bin/python`
4. Reinicia VS Code

### Tests no aparecen en el Testing Panel

**Solución:**
1. `Ctrl+Shift+P`
2. "Python: Configure Tests"
3. Selecciona "pytest"
4. Selecciona "tests" como directorio
5. Reload window

### Error: "Can't connect to MySQL server"

**Solución:**
```bash
# Linux
sudo systemctl start mysql
sudo systemctl status mysql

# Mac
brew services start mysql
brew services list

# Verificar
mysql -u root -p
```

### Los cambios no se reflejan automáticamente

**Solución:**
```bash
# Asegúrate que FLASK_DEBUG=1 en .env
# Ejecuta con:
flask run --reload

# O usa el debugger de VS Code
```

## 📂 Estructura del Proyecto en VS Code

```
flask-app/
├── .vscode/               ← Configuración de VS Code
│   ├── settings.json      ← Settings del workspace
│   ├── launch.json        ← Configuración de debugging
│   ├── tasks.json         ← Tareas automatizadas
│   └── extensions.json    ← Extensiones recomendadas
├── app/
│   ├── blueprints/        ← Rutas (auth, shop, etc.)
│   ├── models/            ← Modelos SQLAlchemy
│   ├── services/          ← Lógica de negocio
│   ├── templates/         ← Templates Jinja2
│   └── static/            ← CSS, JS, imágenes
├── tests/                 ← Tests con pytest
├── venv/                  ← Virtual environment
├── .env                   ← Variables de entorno (NO commitear)
├── requirements.txt       ← Dependencias
└── run.py                 ← Punto de entrada
```

## 🎨 Extensiones Recomendadas

Ya están configuradas en `.vscode/extensions.json`:

- **Python** - Soporte completo de Python
- **Pylance** - IntelliSense avanzado
- **Jinja** - Syntax highlighting para templates
- **GitLens** - Git supercharged
- **Python Test Adapter** - Run tests desde UI
- **Auto Close Tag** - Cierra tags HTML automáticamente
- **Path Intellisense** - Autocomplete de paths

VS Code te preguntará si quieres instalarlas al abrir el proyecto.

## 💡 Tips Productivos

### 1. Snippets Útiles

En VS Code, empieza a escribir:
- `def` → autocompleta función
- `class` → autocompleta clase
- `if` → autocompleta if statement

### 2. Multi-cursor

`Alt+Click` para agregar cursores múltiples

### 3. Buscar y Reemplazar

`Ctrl+H` para buscar y reemplazar en el archivo actual
`Ctrl+Shift+H` para buscar y reemplazar en todo el proyecto

### 4. Ir a Definición

`Ctrl+Click` o `F12` en un símbolo para ir a su definición

### 5. Ver Referencias

`Shift+F12` para ver dónde se usa un símbolo

### 6. Renombrar Símbolo

`F2` para renombrar una variable/función en todos lados

### 7. Terminal Split

`Ctrl+Shift+5` para dividir la terminal

## 🎯 Siguiente Paso

Una vez que tengas todo funcionando:

1. ✅ Familiarízate con la estructura del código
2. ✅ Pon breakpoints y debuggea
3. ✅ Ejecuta los tests
4. ✅ Intenta hacer un cambio pequeño
5. ✅ Lee la documentación en `/docs`

## 📚 Recursos Adicionales

- [VS Code Python Tutorial](https://code.visualstudio.com/docs/python/python-tutorial)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pytest Documentation](https://docs.pytest.org/)

---

¡Listo! Ahora tienes un entorno de desarrollo completo en VS Code. 🚀

Si tienes algún problema, revisa la sección de Troubleshooting o pregunta.
