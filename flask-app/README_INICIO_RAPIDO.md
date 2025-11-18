# ⚡ INICIO RÁPIDO - E-commerce Ecuador

## 🚀 Configuración Automática en 2 Pasos

Todo se configura **AUTOMÁTICAMENTE** al iniciar la aplicación por primera vez.

---

## 📋 Requisitos Previos

Asegúrate de tener instalado:

- ✅ Python 3.8+
- ✅ MySQL corriendo (con usuario `root` sin contraseña, o edita `.env`)
- ✅ pip (gestor de paquetes Python)

---

## 🎯 Paso 1: Instalar Dependencias

```bash
cd flask-app
pip install -r requirements.txt
```

---

## 🎯 Paso 2: Ejecutar la Aplicación

```bash
python run.py
```

**¡ESO ES TODO!** 🎉

---

## ✨ ¿Qué Sucede Automáticamente?

Cuando ejecutas `python run.py` por primera vez:

### 1️⃣ Crea archivo `.env` automáticamente
Si no existe, copia `.env.example` a `.env`

### 2️⃣ Crea la base de datos automáticamente
Crea la base de datos `ecommerce_ecuador` en MySQL

### 3️⃣ Crea todas las tablas automáticamente
Genera el esquema completo de la base de datos

### 4️⃣ Puebla con datos demo automáticamente
Si la base de datos está vacía, crea:
- 📦 24+ productos en 6 categorías (Electrónica, Hogar, Moda, Deportes, Libros, Belleza)
- 👥 2 administradores + 5 clientes
- 🛍️ Pedidos, reseñas y listas de deseos de ejemplo
- ⚙️ Configuración de tienda para Ecuador (IVA 15%, envíos en USD)

### 5️⃣ Inicia el servidor
La aplicación estará disponible en: **http://localhost:5000**

---

## 📋 Verás algo como esto:

```
📝 Creando archivo .env desde .env.example...
✅ Archivo .env creado. Puedes editarlo con tus credenciales.

============================================================
🚀 INICIALIZACIÓN AUTOMÁTICA DE BASE DE DATOS
============================================================
Creating database 'ecommerce_ecuador'...
Database 'ecommerce_ecuador' created successfully!
Creating database tables...
Database tables created successfully!

🌱 Base de datos vacía detectada. Poblando con datos demo...
============================================================
👤 Creando administradores...
✅ 2 administradores creados
👥 Creando usuarios clientes...
✅ 5 usuarios creados
📦 Creando categorías y productos...
✅ 6 categorías, 24 subcategorías, 24 productos creados
⚙️  Configurando tienda...
✅ Configuración de tienda creada
🛍️  Creando pedidos de ejemplo...
✅ 12 pedidos creados
⭐ Creando reseñas...
✅ 35 reseñas creadas
❤️  Creando listas de deseos...
✅ 28 items agregados a listas de deseos

✅ DATOS DEMO CREADOS EXITOSAMENTE
============================================================

📋 CREDENCIALES DE ACCESO:

🔐 ADMIN:
   Email:    admin@ecommerce.ec
   Password: admin123
   URL:      http://localhost:5000/admin/login

👤 CLIENTES (password: demo123):
   - carlos.mendoza@email.com
   - maria.gonzalez@email.com
   - luis.torres@email.com
   URL:      http://localhost:5000/login

============================================================

 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
Press CTRL+C to quit
```

---

## 👥 Credenciales de Acceso

### 🔐 Panel de Administración

```
URL:      http://localhost:5000/admin/login

Administrador Principal:
Email:    admin@ecommerce.ec
Password: admin123

Editor:
Email:    editor@ecommerce.ec
Password: editor123
```

### 👤 Usuarios Clientes

```
URL:      http://localhost:5000/login

Todos tienen el password: demo123

Emails disponibles:
- carlos.mendoza@email.com
- maria.gonzalez@email.com
- luis.torres@email.com
- ana.rodriguez@email.com
- pedro.ramirez@email.com
```

---

## 🔧 Configuración Personalizada (Opcional)

Si tu MySQL tiene contraseña o configuración diferente, edita `.env`:

```env
# Cambiar esta línea:
DATABASE_URL=mysql+pymysql://root:@localhost/ecommerce_ecuador

# Por ejemplo, si tu root tiene password "mipassword":
DATABASE_URL=mysql+pymysql://root:mipassword@localhost/ecommerce_ecuador

# O si usas otro usuario:
DATABASE_URL=mysql+pymysql://miusuario:mipassword@localhost/ecommerce_ecuador
```

Luego ejecuta nuevamente:
```bash
python run.py
```

---

## 🔄 Resetear Datos

Si quieres empezar de nuevo con datos frescos:

**Opción 1: Borrar la base de datos**
```bash
mysql -u root -p
```
```sql
DROP DATABASE ecommerce_ecuador;
exit;
```

Luego ejecuta:
```bash
python run.py
```

**Opción 2: Ejecutar script de setup manual**
```bash
python setup_demo.py
```

---

## ⚙️ Configuración de Tienda (Ecuador)

La configuración por defecto incluye:

- **País**: Ecuador
- **Moneda**: USD (Dólares estadounidenses)
- **IVA**: 15% (2025)
- **Envío Nacional**: $5.99
  - 🎁 GRATIS en compras > $40
- **Envío Internacional**: $25.99
  - 🎁 GRATIS en compras > $100

---

## 📦 Categorías de Productos

El sistema viene pre-cargado con:

1. 📱 **Electrónica**
   - Celulares, Computadoras, Audio, Accesorios

2. 🏠 **Hogar y Cocina**
   - Electrodomésticos, Muebles, Decoración, Cocina

3. 👕 **Moda y Accesorios**
   - Ropa Hombre, Ropa Mujer, Calzado, Accesorios

4. 🏋️ **Deportes y Fitness**
   - Gimnasio, Yoga, Ciclismo, Outdoor

5. 📚 **Libros y Educación**
   - Desarrollo Personal, Negocios, Ficción, Académicos

6. 💄 **Belleza y Salud**
   - Cuidado Personal, Suplementos, Cosméticos, Bienestar

---

## 🐛 Solución de Problemas

### Error: "Can't connect to MySQL server"

**Solución**: Inicia MySQL

```bash
# Windows (PowerShell como admin)
net start MySQL

# Linux/Mac
sudo service mysql start
```

### Error: "Access denied for user 'root'"

**Solución**: Edita `.env` con tus credenciales correctas de MySQL

```env
DATABASE_URL=mysql+pymysql://TU_USUARIO:TU_PASSWORD@localhost/ecommerce_ecuador
```

### Error: "ModuleNotFoundError"

**Solución**: Instala las dependencias

```bash
pip install -r requirements.txt
```

### Los datos no se crean automáticamente

**Solución**: Ejecuta el script manual

```bash
python setup_demo.py
```

---

## 💡 Próximos Pasos

1. ✅ Explora el catálogo de productos
2. ✅ Prueba el flujo de compra como cliente
3. ✅ Accede al panel de administración
4. ✅ Agrega tus propios productos
5. ✅ Personaliza categorías
6. ✅ Configura métodos de pago (PayPal, PayU)
7. ✅ Configura notificaciones por email

---

## 📚 Más Documentación

- `README.md` - Documentación completa
- `README_SETUP.md` - Guía de setup detallada
- `DEPLOYMENT.md` - Despliegue en producción
- `MIGRATION_GUIDE.md` - Migración desde PHP

---

## 🔒 Seguridad

**⚠️ IMPORTANTE**: Las credenciales demo son SOLO para desarrollo local.

En producción debes:
1. Cambiar TODAS las contraseñas
2. Usar contraseñas fuertes (mínimo 12 caracteres)
3. Cambiar el `SECRET_KEY` en `.env`
4. Habilitar HTTPS
5. Configurar variables de entorno seguras
6. Nunca subir `.env` al repositorio

---

## 📞 Soporte

¿Problemas? Consulta:
- `README_SETUP.md` para configuración detallada
- `README.md` para documentación completa
- Reporta issues en el repositorio

---

**¡Listo! Tu e-commerce está funcionando.** 🎉

Solo ejecuta `python run.py` y todo se configura automáticamente.
