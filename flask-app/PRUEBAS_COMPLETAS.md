# ✅ PASOS PARA SINCRONIZAR Y PROBAR TODO

## 🔧 Paso 1: Sincronizar Cambios desde GitHub

```powershell
cd C:\Users\jorge.ulloa\Documents\claude_dev\flask_ecommerce
git fetch origin
git reset --hard origin/claude/plan-flask-migration-017kumZqSK9WGpLF5ypzmLiw
```

---

## 🗄️ Paso 2: Limpiar Bases de Datos Antiguas

Conecta a MySQL y ejecuta:

```sql
DROP DATABASE IF EXISTS ecommerce_ecuador;
DROP DATABASE IF EXISTS ecommerce_ec;
DROP DATABASE IF EXISTS Ecommerce_Ec;
```

O desde PowerShell:

```powershell
mysql -u root -e "DROP DATABASE IF EXISTS ecommerce_ecuador; DROP DATABASE IF EXISTS ecommerce_ec; DROP DATABASE IF EXISTS Ecommerce_Ec;"
```

---

## 📝 Paso 3: Borrar el archivo .env local

```powershell
cd flask-app
Remove-Item .env -ErrorAction SilentlyContinue
```

---

## 🚀 Paso 4: Ejecutar la Aplicación

```powershell
python run.py
```

---

## ✅ Qué Verás (Salida Esperada)

```
📝 Creando archivo .env desde .env.example...
✅ Archivo .env creado.

============================================================
🚀 INICIALIZACIÓN AUTOMÁTICA DE BASE DE DATOS
============================================================

🗄️  Verificando base de datos...
Creating database 'Ecommerce_Ec'...
✅ Database 'Ecommerce_Ec' created successfully!

Creating database tables...
✅ Database tables created successfully!

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
 * Running on http://127.0.0.1:5000
```

---

## 🎯 Qué se Creó Automáticamente

### 📦 Productos Demo (24 productos)

**1. Electrónica** (4 productos)
- Smartphone Galaxy Pro 5G - $899.99
- Laptop HP 15.6" i7 16GB RAM - $1,299.99 (15% OFF)
- Audífonos Bluetooth Premium - $159.99 (20% OFF)
- Mouse Gamer RGB 16000 DPI - $45.99

**2. Hogar y Cocina** (3 productos)
- Licuadora Industrial 2000W - $89.99
- Cafetera Espresso Automática - $349.99 (25% OFF)
- Juego de Sartenes Antiadherentes - $79.99

**3. Moda y Accesorios** (3 productos)
- Zapatillas Deportivas Running - $89.99
- Mochila Urbana Laptop 17" - $54.99 (10% OFF)
- Reloj Inteligente Smartwatch - $129.99

**4. Deportes y Fitness** (3 productos)
- Pesas Ajustables 2.5kg - 24kg - $299.99
- Colchoneta Yoga Premium 6mm - $34.99 (15% OFF)
- Bicicleta Spinning Profesional - $449.99

**5. Libros y Educación** (3 productos)
- El Poder del Ahora - $18.99
- Hábitos Atómicos - $21.99 (10% OFF)
- Curso Completo de Programación Python - $45.99

**6. Belleza y Salud** (2 productos)
- Proteína Whey Isolate 2kg - $59.99
- Set de Cuidado Facial Completo - $89.99 (20% OFF)

### 👥 Usuarios Demo

**Administradores:**
- admin@ecommerce.ec / admin123 (Administrador Principal)
- editor@ecommerce.ec / editor123 (Editor de Contenido)

**Clientes:**
- carlos.mendoza@email.com / demo123
- maria.gonzalez@email.com / demo123
- luis.torres@email.com / demo123
- ana.rodriguez@email.com / demo123
- pedro.ramirez@email.com / demo123

### 🛍️ Datos Adicionales
- 10-15 pedidos de ejemplo
- 30-40 reseñas de productos
- Listas de deseos con productos

---

## 🧪 Pasos para Probar el Sistema End-to-End

### 1. Verificar Productos y Categorías

```
✅ Ve a: http://localhost:5000
✅ Deberías ver productos en la página principal
✅ Haz clic en "Ofertas" - deberías ver productos con descuento
✅ Navega por las categorías del menú
```

### 2. Probar Carrito de Compras (COMPLETO)

**A. Agregar al Carrito:**
```
✅ Haz clic en cualquier producto
✅ Haz clic en "Agregar al Carrito"
✅ Deberías ver mensaje de éxito
✅ El contador del carrito (badge) debe actualizarse
```

**B. Ver Carrito:**
```
✅ Haz clic en el ícono del carrito
✅ Deberías ver los productos agregados
✅ Verifica cantidades y precios
```

**C. Actualizar Cantidad:**
```
✅ En la página del carrito, cambia la cantidad
✅ Haz clic en "Actualizar"
✅ El total debe recalcularse
```

**D. Eliminar Producto:**
```
✅ Haz clic en "Eliminar" junto a un producto
✅ El producto debe desaparecer del carrito
✅ El total debe actualizarse
```

**E. Proceder al Checkout:**
```
✅ Inicia sesión como cliente (carlos.mendoza@email.com / demo123)
✅ Haz clic en "Proceder al Pago"
✅ Completa el formulario de envío
✅ Confirma el pedido
```

### 3. Probar Panel de Administración

```
✅ Ve a: http://localhost:5000/admin/login
✅ Inicia sesión: admin@ecommerce.ec / admin123
✅ Verifica que veas:
   - Dashboard con estadísticas
   - 6 categorías creadas
   - 24 productos creados
   - Usuarios (2 admins + 5 clientes)
   - Pedidos de ejemplo
✅ Prueba editar un producto
✅ Prueba crear una nueva categoría
```

### 4. Probar Búsqueda y Filtros

```
✅ Usa la barra de búsqueda
✅ Busca "laptop" - debería encontrar el producto
✅ Filtra por categoría
✅ Filtra por rango de precio
✅ Ordena por precio (menor a mayor, mayor a menor)
```

### 5. Probar Perfil de Usuario

```
✅ Inicia sesión como cliente
✅ Ve a tu perfil
✅ Verifica historial de pedidos
✅ Prueba lista de deseos:
   - Agrega productos a favoritos
   - Elimina productos de favoritos
✅ Actualiza información del perfil
```

---

## 🐛 Si Algo No Funciona

### Problema: No veo productos

```powershell
# Verifica que se crearon en la BD
mysql -u root -e "USE Ecommerce_Ec; SELECT COUNT(*) FROM productos;"
mysql -u root -e "USE Ecommerce_Ec; SELECT COUNT(*) FROM categorias;"
```

Deberías ver:
- 24 productos
- 6 categorías

### Problema: Carrito no funciona

Revisa la consola del navegador (F12) para errores JavaScript.
Verifica que las rutas sean `/carrito/add`, `/carrito/update`, etc.

### Problema: Error de base de datos

```powershell
# Borra todo y empieza de nuevo
mysql -u root -e "DROP DATABASE IF EXISTS Ecommerce_Ec;"
cd flask-app
Remove-Item .env
python run.py
```

---

## 📊 Verificación Final

Ejecuta estos comandos para verificar que todo se creó:

```sql
USE Ecommerce_Ec;

-- Ver categorías
SELECT id, categoria FROM categorias;

-- Ver productos
SELECT id, titulo, precio, stock, estado FROM productos LIMIT 10;

-- Ver usuarios
SELECT id, nombre, email FROM usuarios;

-- Ver administradores
SELECT id, nombre, email, perfil FROM administradores;

-- Ver pedidos
SELECT COUNT(*) as total_pedidos FROM compras;

-- Ver reseñas
SELECT COUNT(*) as total_reviews FROM comentarios;
```

---

## ✅ Checklist Completo

- [ ] Git sincronizado
- [ ] Base de datos Ecommerce_Ec creada
- [ ] 6 categorías creadas
- [ ] 24+ productos creados
- [ ] 2 administradores creados
- [ ] 5 clientes creados
- [ ] Productos visibles en home
- [ ] Carrito: Agregar producto funciona
- [ ] Carrito: Actualizar cantidad funciona
- [ ] Carrito: Eliminar producto funciona
- [ ] Carrito: Proceder al checkout funciona
- [ ] Login de usuario funciona
- [ ] Login de admin funciona
- [ ] Panel admin muestra datos
- [ ] Búsqueda de productos funciona
- [ ] Filtros funcionan
- [ ] Lista de deseos funciona

---

**Si todos los checks pasan, el sistema está 100% funcional** ✅
