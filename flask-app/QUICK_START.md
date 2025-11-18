# 🚀 Quick Start - Guía Rápida

## 📍 Ubicación del Código

```
/home/user/Ecommerce_php/flask-app  ← Abre ESTE directorio en VS Code
```

## ⚡ 3 Comandos para Empezar

```bash
# 1. Ir al directorio
cd /home/user/Ecommerce_php/flask-app

# 2. Abrir VS Code
code .

# 3. Ya está conectado a Git! Verifica:
git status
```

## 📊 Estado del Proyecto

✅ **Todo completado y commiteado:**
- Fase 1: Backend (5c8427f)
- Fase 2: Frontend (85c37d1)
- Fase 3: Migración de Datos (004d7fd)
- Fase 4: Testing (7352333)
- Fase 5: Deployment (3c38ebe)
- VS Code Config (31cc20e)

## 🎯 Siguiente Paso: Ejecutar Local

### 1. Crear Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar MySQL

```bash
mysql -u root -p

# Dentro de MySQL:
CREATE DATABASE ecommerce_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ecommerce_user'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON ecommerce_dev.* TO 'ecommerce_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Configurar .env

```bash
cp .env.example .env
nano .env
```

Mínimo necesario:
```env
SECRET_KEY=dev-secret-key
FLASK_ENV=development
DATABASE_URL=mysql+pymysql://ecommerce_user:password123@localhost:3306/ecommerce_dev
```

### 4. Crear Tablas

```bash
flask db upgrade
```

### 5. Crear Datos de Prueba

```bash
flask shell

# Dentro del shell, copia y pega:
from app import db
from app.models.user import Usuario
from app.models.categoria import Categoria
from app.models.product import Producto
from app.models.comercio import Comercio
from app.models.setting import Plantilla

user = Usuario(nombre='Test', email='test@test.com', verificado=True, activo=True)
user.set_password('password123')
db.session.add(user)

comercio = Comercio(nombre='Tienda', email='tienda@test.com', telefono='123456789', moneda='USD', impuesto=10.0, costo_envio=5.0)
db.session.add(comercio)

plantilla = Plantilla(titulo='Mi Tienda', color_primario='#007bff', color_secundario='#6c757d')
db.session.add(plantilla)

categoria = Categoria(nombre='Electrónica', descripcion='Productos electrónicos', estado=True)
db.session.add(categoria)
db.session.commit()

productos = [
    Producto(titulo='Laptop', descripcion='Laptop de alta gama', precio=1299.99, stock=10, categoria_id=1, estado=True, destacado=True),
    Producto(titulo='iPhone', descripcion='Smartphone', precio=999.99, precio_oferta=899.99, stock=20, categoria_id=1, estado=True)
]
for p in productos:
    db.session.add(p)
db.session.commit()

print("✅ Datos creados!")
exit()
```

### 6. Ejecutar

En VS Code:
- Presiona **F5**

O desde terminal:
```bash
flask run
```

### 7. Abrir Navegador

```
http://localhost:5000
```

Login: `test@test.com` / `password123`

## 🔗 Git - Comandos Útiles

```bash
# Ver estado
git status

# Ver branch actual
git branch

# Ver commits
git log --oneline -10

# Crear nuevo branch
git checkout -b mi-branch

# Ver cambios
git diff

# Agregar cambios
git add .

# Commit
git commit -m "Mi cambio"

# Push
git push origin mi-branch
```

## 📁 Estructura Importante

```
flask-app/
├── app/                   ← Código principal
│   ├── blueprints/       ← Rutas (auth, shop, cart, etc.)
│   ├── models/           ← Base de datos (SQLAlchemy)
│   ├── templates/        ← HTML (Jinja2)
│   ├── static/           ← CSS, JS, imágenes
│   └── services/         ← Lógica de negocio
├── tests/                ← Tests (pytest)
├── .vscode/              ← Config de VS Code (ya está)
├── .env                  ← Variables de entorno (CREAR)
├── requirements.txt      ← Dependencias
└── run.py                ← Punto de entrada
```

## 🐛 Debugging en VS Code

1. Pon un **breakpoint**: Click en el margen izquierdo junto al número de línea
2. Presiona **F5**
3. El código se detendrá en el breakpoint
4. Inspecciona variables en el panel izquierdo
5. Usa **F10** (siguiente línea) o **F11** (entrar a función)

## 🧪 Ejecutar Tests

```bash
# Todos los tests
pytest

# Con coverage
pytest --cov=app --cov-report=html

# Solo unitarios
pytest -m unit
```

O usa el panel de Testing en VS Code (icono de matraz 🧪)

## 📚 Documentación

- **README.md**: Visión general del proyecto
- **VSCODE_SETUP.md**: Setup detallado de VS Code (800+ líneas)
- **DEPLOYMENT.md**: Deploy en producción
- **MIGRATION_GUIDE.md**: Migrar datos desde PHP
- **tests/README.md**: Guía de testing

## ⚡ Atajos de VS Code

| Atajo | Acción |
|-------|--------|
| **F5** | Run con debugger |
| **Ctrl+`** | Abrir terminal |
| **Ctrl+P** | Buscar archivo |
| **Ctrl+Shift+F** | Buscar en proyecto |
| **Ctrl+Shift+G** | Ver Git |
| **F12** | Ir a definición |
| **Shift+F12** | Ver referencias |

## 🆘 Ayuda Rápida

### Python virtual environment no se activa en VS Code

```bash
# Ctrl+Shift+P
# Escribe: "Python: Select Interpreter"
# Selecciona: ./venv/bin/python
```

### No veo el código en VS Code

Asegúrate de abrir **el directorio correcto**:
```bash
cd /home/user/Ecommerce_php/flask-app
code .
```

**NO** abras `/home/user/Ecommerce_php` (el padre), abre **`flask-app`**.

### MySQL no conecta

Verifica que esté corriendo:
```bash
sudo systemctl status mysql  # Linux
brew services list           # Mac
```

Y que el password en `.env` sea correcto.

### Port 5000 ya en uso

```bash
lsof -i :5000
kill -9 <PID>
```

O usa otro puerto:
```bash
flask run --port 5001
```

## 🎉 ¡Listo!

Ahora tienes todo el código Flask migrado listo para trabajar en VS Code.

¿Necesitas ayuda? Lee los documentos completos:
- `VSCODE_SETUP.md` - Setup detallado
- `DEPLOYMENT.md` - Deploy en producción
- `README.md` - Documentación general
