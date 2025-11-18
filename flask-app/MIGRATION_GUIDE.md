# Guía de Migración de Datos PHP → Flask

## 📋 Descripción

Este documento describe el proceso de migración de datos desde la base de datos PHP original a la nueva aplicación Flask.

## 🎯 Alcance

El script `migrate_data.py` migra:

### Datos de Base de Datos (16 tablas)
- ✅ **Usuarios** - Con contraseñas legacy preservadas
- ✅ **Administradores** - Cuentas de administración
- ✅ **Categorías** - Categorías de productos
- ✅ **Subcategorías** - Subcategorías anidadas
- ✅ **Productos** - Todos los productos con multimedia
- ✅ **Compras** - Órdenes de compra
- ✅ **Comentarios** - Reviews y calificaciones
- ✅ **Wishlist (Deseos)** - Lista de deseos
- ✅ **Comercio** - Configuración de comercio
- ✅ **Plantilla** - Configuración de tema
- ✅ **Slides** - Carousel principal
- ✅ **Banners** - Banners promocionales
- ✅ **Cabeceras** - Metadatos SEO
- ✅ **Notificaciones** - Contadores
- ✅ **Visitas País** - Analytics por país
- ✅ **Visitas Persona** - Analytics por IP

### Archivos
- 📁 Imágenes de usuarios (avatares)
- 📁 Imágenes de productos
- 📁 Imágenes de categorías
- 📁 Slides del carousel
- 📁 Banners
- 📁 Logos y assets

## 🔧 Requisitos Previos

### 1. Dependencias Python

Asegúrate de tener todas las dependencias instaladas:

```bash
pip install -r requirements.txt
```

Dependencias clave:
- `PyMySQL==1.1.0` - Conector MySQL
- `SQLAlchemy==2.0.23` - ORM
- `Flask-SQLAlchemy==3.1.1` - Integración Flask

### 2. Base de Datos Origen

La base de datos PHP MySQL debe estar:
- ✅ Accesible desde el servidor donde correrás el script
- ✅ Con las credenciales correctas
- ✅ Con todos los datos que deseas migrar

### 3. Base de Datos Destino

Crea la base de datos Flask (si no existe):

```bash
# Opción 1: MySQL
mysql -u root -p
CREATE DATABASE ecommerce_flask CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Opción 2: PostgreSQL
psql -U postgres
CREATE DATABASE ecommerce_flask ENCODING 'UTF8';
\q
```

### 4. Variables de Entorno

Configura el archivo `.env` en el directorio `flask-app/`:

```bash
# Database
DATABASE_URL=mysql+pymysql://root:password@localhost/ecommerce_flask

# Secret Key
SECRET_KEY=your-secret-key-here

# Email (opcional para migración)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## 🚀 Cómo Ejecutar la Migración

### Paso 1: Navegar al directorio Flask

```bash
cd flask-app
```

### Paso 2: Hacer el script ejecutable (Linux/Mac)

```bash
chmod +x migrate_data.py
```

### Paso 3: Ejecutar el script

```bash
python migrate_data.py
```

### Paso 4: Proporcionar la configuración

El script te pedirá la siguiente información:

```
📋 Configuración de migración:

Host BD origen (default: localhost): localhost
Usuario BD origen (default: root): root
Password BD origen: ********
Nombre BD origen (default: ecommerce): ecommerce

URL BD destino (default: mysql+pymysql://root:password@localhost/ecommerce_flask):
[Enter para usar default]

Directorio archivos origen (default: ../): ../
Directorio archivos destino (default: app/static/uploads): app/static/uploads
```

### Paso 5: Confirmar la migración

```
⚠️  ADVERTENCIA: Esta operación migrará todos los datos
¿Deseas continuar? (si/no): si
```

## 📊 Proceso de Migración

El script ejecutará los siguientes pasos:

1. **Conexión a BDs** - Conecta a origen (PHP) y destino (Flask)
2. **Creación de tablas** - Crea todas las tablas SQLAlchemy
3. **Migración de usuarios** - Preserva contraseñas legacy
4. **Migración de administradores** - Cuentas admin
5. **Migración de categorías** - Estructura de categorías
6. **Migración de productos** - Todos los productos
7. **Migración de órdenes** - Historial de compras
8. **Migración de comentarios** - Reviews
9. **Migración de wishlist** - Favoritos
10. **Migración de configuraciones** - Comercio, plantilla, SEO
11. **Migración de multimedia** - Slides, banners
12. **Migración de analytics** - Visitas
13. **Copia de archivos** - Imágenes y uploads
14. **Verificación** - Comprueba integridad
15. **Reporte** - Genera resumen

## 📈 Salida del Script

### Durante la Ejecución

```
🚀 INICIANDO MIGRACIÓN DE DATOS PHP → FLASK
============================================================

🔌 Conectando a base de datos origen...
✅ Conectado a base de datos origen

🔌 Conectando a base de datos destino...
✅ Conectado a base de datos destino

👥 Migrando usuarios...
  ✅ 150 usuarios migrados

👨‍💼 Migrando administradores...
  ✅ 3 administradores migrados

📁 Migrando categorías...
  ✅ 12 categorías migradas

📂 Migrando subcategorías...
  ✅ 35 subcategorías migradas

📦 Migrando productos...
  ✅ 248 productos migrados

...
```

### Reporte Final

```
============================================================
📝 REPORTE DE MIGRACIÓN
============================================================

✅ Registros migrados:
  • Usuarios: 150
  • Administradores: 3
  • Categorías: 12
  • Subcategorías: 35
  • Productos: 248
  • Compras: 523
  • Comentarios: 89
  • Wishlist: 67
  • Slides: 5
  • Banners: 8
  • Visitas (país): 1243
  • Visitas (IP): 2567
  • Archivos copiados: 342

📦 Total de registros migrados: 2950

✅ Sin errores

============================================================
📄 Reporte guardado en: migration_report.txt

⏱️  Tiempo total: 0:02:34

✅ MIGRACIÓN COMPLETADA EXITOSAMENTE
```

## 🔒 Seguridad - Contraseñas Legacy

### ¿Cómo funciona?

El sistema preserva las contraseñas hasheadas con `crypt()` de PHP:

1. **Durante la migración**: Las contraseñas se copian tal cual (hash legacy)
2. **Primer login**: El sistema detecta hash legacy y lo valida con `crypt()`
3. **Migración automática**: Si la contraseña es correcta, se rehashea con bcrypt
4. **Siguientes logins**: Ya usan bcrypt nativo de Flask

### Implementación

En `app/models/user.py`:

```python
def check_password(self, password):
    # Si es bcrypt (nuevo)
    if self.password.startswith(('$2a', '$2b', '$2y')):
        return bcrypt.check_password_hash(self.password, password)

    # Si es crypt legacy (PHP)
    if self.password == crypt.crypt(password, self.password):
        # Migrar a bcrypt
        self.migrate_password(password)
        return True

    return False
```

## 🧪 Verificación Post-Migración

### 1. Verificar conteo de registros

```bash
# Desde Flask shell
python
>>> from app import create_app, db
>>> from app.models.user import Usuario
>>> from app.models.product import Producto

>>> app = create_app()
>>> with app.app_context():
...     print(f"Usuarios: {Usuario.query.count()}")
...     print(f"Productos: {Producto.query.count()}")
```

### 2. Verificar relaciones

```python
>>> with app.app_context():
...     # Verificar producto con categoría
...     producto = Producto.query.first()
...     print(f"Producto: {producto.titulo}")
...     print(f"Categoría: {producto.categoria.nombre}")
...
...     # Verificar usuario con compras
...     usuario = Usuario.query.first()
...     print(f"Usuario: {usuario.nombre}")
...     print(f"Compras: {len(usuario.compras)}")
```

### 3. Verificar archivos

```bash
ls -la app/static/uploads/productos/
ls -la app/static/uploads/usuarios/
```

### 4. Probar login

```bash
# Iniciar aplicación
flask run

# Abrir navegador
# http://localhost:5000/auth/login
# Probar con credenciales de usuario PHP
```

## ⚠️ Solución de Problemas

### Error: "Can't connect to MySQL server"

**Problema**: No se puede conectar a la BD origen

**Solución**:
```bash
# Verificar que MySQL esté corriendo
sudo systemctl status mysql

# Verificar credenciales
mysql -u root -p -h localhost

# Verificar puerto
netstat -tlnp | grep 3306
```

### Error: "Table already exists"

**Problema**: Las tablas ya existen en BD destino

**Solución**:
```bash
# Opción 1: Eliminar BD y recrear
mysql -u root -p
DROP DATABASE ecommerce_flask;
CREATE DATABASE ecommerce_flask CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Opción 2: Truncar tablas
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.drop_all()
...     db.create_all()
```

### Error: "Foreign key constraint fails"

**Problema**: Error de integridad referencial

**Solución**: El script migra en orden correcto, pero si hay datos huérfanos en PHP:

```python
# Modificar script para ignorar registros huérfanos
# En cada función migrate_*, agregar try-except más específico
```

### Error: "File not found" al copiar archivos

**Problema**: Directorio de archivos origen no existe

**Solución**:
```bash
# Verificar ruta correcta
ls -la ../uploads/

# Ajustar ruta en el script o al ejecutar
```

### Algunos usuarios no pueden hacer login

**Problema**: Contraseñas no migran correctamente

**Solución**:
```python
# Opción 1: Reset password para ese usuario
from app.models.user import Usuario
with app.app_context():
    user = Usuario.query.filter_by(email='user@example.com').first()
    user.set_password('nueva_password')
    db.session.commit()

# Opción 2: Forzar uso de bcrypt desde el inicio
# (Requiere que usuarios restablezcan password)
```

## 📝 Notas Importantes

### ⚠️ Antes de Ejecutar

1. **Hacer backup** de la base de datos PHP original:
   ```bash
   mysqldump -u root -p ecommerce > backup_ecommerce_$(date +%Y%m%d).sql
   ```

2. **Probar primero** en ambiente de desarrollo/staging

3. **Verificar espacio en disco** para archivos

4. **Planificar downtime** si es producción

### ✅ Después de Ejecutar

1. **Revisar el reporte** `migration_report.txt`
2. **Verificar errores** (si los hay)
3. **Probar funcionalidades**:
   - Login de usuarios
   - Vista de productos
   - Proceso de compra
   - Panel admin
4. **Verificar archivos** (imágenes se cargan correctamente)

### 🔄 Re-ejecución

Si necesitas re-ejecutar la migración:

```bash
# Limpiar BD destino
mysql -u root -p
DROP DATABASE ecommerce_flask;
CREATE DATABASE ecommerce_flask CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Ejecutar migración nuevamente
python migrate_data.py
```

## 📚 Recursos Adicionales

- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)
- [SQLAlchemy Core Documentation](https://docs.sqlalchemy.org/)
- [PyMySQL Documentation](https://pymysql.readthedocs.io/)
- [Plan de Migración Completo](../PLAN_MIGRACION_FLASK.md)

## 🆘 Soporte

Si encuentras problemas durante la migración:

1. Revisa los logs de error en `migration_report.txt`
2. Verifica la documentación de este archivo
3. Consulta el plan de migración principal
4. Revisa los logs de Flask: `flask-app/logs/`

## 📊 Ejemplo Completo

```bash
# Paso 1: Preparación
cd /path/to/Ecommerce_php/flask-app
source venv/bin/activate  # Si usas virtualenv
pip install -r requirements.txt

# Paso 2: Configurar .env
cp .env.example .env
nano .env  # Editar con tus credenciales

# Paso 3: Backup
mysqldump -u root -p ecommerce > ../backup_$(date +%Y%m%d).sql

# Paso 4: Crear BD destino
mysql -u root -p -e "CREATE DATABASE ecommerce_flask CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Paso 5: Migrar
python migrate_data.py

# Paso 6: Verificar
python
>>> from app import create_app, db
>>> from app.models.user import Usuario
>>> app = create_app()
>>> with app.app_context():
...     print(Usuario.query.count())

# Paso 7: Probar
flask run
# Abrir http://localhost:5000
```

---

**✅ ¡Migración completada!** Ahora tienes todos tus datos PHP en Flask con integridad preservada.
