# 🌱 Datos de Demostración - Tienda de Ropa

Esta guía explica cómo poblar la base de datos con datos de demostración completos para probar todas las funcionalidades del sistema.

## 📋 Contenido

- [Requisitos Previos](#requisitos-previos)
- [Instalación de Dependencias](#instalación-de-dependencias)
- [Poblar con Datos Demo](#poblar-con-datos-demo)
- [Limpiar Datos](#limpiar-datos)
- [Datos Incluidos](#datos-incluidos)
- [Credenciales de Acceso](#credenciales-de-acceso)
- [Estructura de Datos](#estructura-de-datos)

---

## 🔧 Requisitos Previos

Antes de ejecutar el script de seed, asegúrate de:

1. **Tener la base de datos configurada**
   ```bash
   # Verificar archivo .env
   DATABASE_URL=mysql+pymysql://usuario:password@localhost/nombre_bd
   ```

2. **Ejecutar las migraciones**
   ```bash
   flask db upgrade
   ```

3. **Tener el entorno virtual activado**
   ```bash
   source venv/bin/activate
   ```

---

## 📦 Instalación de Dependencias

El script necesita la librería `python-slugify` para generar URLs amigables:

```bash
pip install -r requirements.txt
```

O instalar manualmente:

```bash
pip install python-slugify
```

---

## 🚀 Poblar con Datos Demo

### Opción 1: Ejecución Básica

```bash
python seed_demo_data.py
```

Este comando:
- ✅ Limpia datos existentes (si los hay)
- ✅ Crea 5 categorías de ropa con subcategorías
- ✅ Crea 15 productos con descripciones completas
- ✅ Crea 5 usuarios de ejemplo
- ✅ Crea 2 administradores (admin y editor)
- ✅ Crea pedidos de ejemplo
- ✅ Crea reseñas y calificaciones
- ✅ Crea listas de deseos
- ✅ Configura la tienda

### Opción 2: Con Descarga de Imágenes (Futuro)

```bash
python seed_demo_data.py --download-images
```

> **Nota**: Por ahora usa URLs de Unsplash para las imágenes de productos.

---

## 🗑️ Limpiar Datos

Si necesitas resetear la base de datos y eliminar todos los datos:

### Opción 1: Con Confirmación Interactiva

```bash
python clear_demo_data.py
```

Te pedirá confirmar escribiendo "SI" antes de eliminar.

### Opción 2: Forzar Sin Confirmación

```bash
python clear_demo_data.py --force
```

⚠️ **ADVERTENCIA**: Esta acción eliminará TODOS los datos de forma permanente.

---

## 📊 Datos Incluidos

### 1️⃣ Categorías (5)

| Categoría | Subcategorías | Productos |
|-----------|--------------|-----------|
| **Camisetas** | Manga Corta, Manga Larga, Deportivas, Básicas | 3 |
| **Pantalones** | Vaqueros, Chinos, Deportivos, Joggers | 3 |
| **Vestidos** | Casuales, Fiesta, Verano, Largos | 3 |
| **Zapatos** | Deportivos, Casuales, Formales, Sandalias | 3 |
| **Accesorios** | Gorras, Cinturones, Bufandas, Mochilas | 3 |

**Total: 5 categorías, 20 subcategorías**

### 2️⃣ Productos (15)

Cada producto incluye:

- ✅ **Título descriptivo**
- ✅ **Titular atractivo**
- ✅ **Descripción detallada**
- ✅ **3 imágenes** (URLs de Unsplash)
- ✅ **Detalles técnicos** (material, cuidado, origen, etc.)
- ✅ **Precio base**
- ✅ **Algunos con ofertas** (descuentos del 15-30%)
- ✅ **Peso y costo de envío**
- ✅ **Vistas y ventas simuladas**

**Ejemplos de productos:**

- Camiseta Básica Blanca - 19.99€
- Vaqueros Slim Fit Azul - 49.99€
- Vestido Negro de Fiesta - 79.99€ (25% descuento)
- Zapatillas Running Pro - 89.99€
- Mochila Urban Laptop 15" - 49.99€ (20% descuento)

### 3️⃣ Usuarios (5)

Usuarios de demostración para probar funcionalidades de cliente:

| Nombre | Email | Password |
|--------|-------|----------|
| María García | maria@demo.com | demo123 |
| Juan Martínez | juan@demo.com | demo123 |
| Ana López | ana@demo.com | demo123 |
| Carlos Rodríguez | carlos@demo.com | demo123 |
| Laura Fernández | laura@demo.com | demo123 |

**Características:**
- ✅ Contraseñas encriptadas con bcrypt
- ✅ Emails verificados
- ✅ Modo de registro: directo

### 4️⃣ Administradores (2)

Para probar el panel de administración:

| Nombre | Email | Password | Perfil |
|--------|-------|----------|--------|
| Admin Principal | admin@tienda.com | admin123 | Administrador |
| Editor Tienda | editor@tienda.com | editor123 | Editor |

**Permisos:**
- **Administrador**: Acceso completo a todas las funcionalidades
- **Editor**: Acceso limitado a edición de contenido

### 5️⃣ Pedidos (Variable)

- Cada uno de los primeros 4 usuarios tiene entre 3-7 pedidos
- **Total aproximado**: 12-28 pedidos
- Estados: Pendiente, Procesando, Enviado, Entregado, Cancelado
- Métodos de pago: PayPal, Tarjeta, Transferencia
- Países: Ecuador, Colombia, Perú, Venezuela, México
- Ciudades ecuatorianas: Quito, Guayaquil, Cuenca, Ambato, Machala

### 6️⃣ Reseñas y Calificaciones

- Los primeros 10 productos tienen entre 2-6 reseñas cada uno
- **Total aproximado**: 40-60 reseñas
- Calificaciones entre 4.0 y 5.0 estrellas
- Comentarios realistas y variados

**Ejemplo de reseñas:**
```
⭐⭐⭐⭐⭐ "Excelente producto, muy buena calidad. Lo recomiendo 100%."
⭐⭐⭐⭐⭐ "Perfecto, tal como se describe. Llegó rápido y bien empaquetado."
⭐⭐⭐⭐ "Bien en general, aunque esperaba un poco más de calidad."
```

### 7️⃣ Listas de Deseos

- Cada usuario tiene entre 3-7 productos en su wishlist
- **Total aproximado**: 25-35 items en listas de deseos
- Permite probar funcionalidad de favoritos

### 8️⃣ Configuración de Tienda

**Comercio:**
```
Nombre: TuTienda Ecuador
Email: contacto@tutienda.ec
IVA: 15% (Ecuador - actualizado 2025)
Envío Nacional: $4.99 (gratis > $30)
Envío Internacional: $19.99 (gratis > $80)
País: Ecuador
Ciudad: Quito
```

**Plantilla:**
```
Barra Superior: "Envío gratis en compras superiores a $30"
Redes Sociales: Facebook, Instagram, Twitter, YouTube
```

---

## 🔑 Credenciales de Acceso

### 👤 Usuarios Clientes

Usa cualquiera de estos para probar la experiencia de compra:

```
Email: maria@demo.com
Password: demo123
```

```
Email: juan@demo.com
Password: demo123
```

### 👨‍💼 Administradores

Para acceder al panel de administración:

```
Email: admin@tienda.com
Password: admin123
Rol: Administrador (acceso completo)
```

```
Email: editor@tienda.com
Password: editor123
Rol: Editor (acceso limitado)
```

---

## 🏗️ Estructura de Datos

### Diagrama de Relaciones

```
Comercio ─── Plantilla
    │
Categoria ─┬─ Subcategoria
           │
        Producto ─┬─ Comentario ─── Usuario
                  ├─ Compra ─────── Usuario
                  └─ Deseo ──────── Usuario

Administrador (independiente)
```

### Tablas Pobladas

| Tabla | Registros Aprox. | Descripción |
|-------|------------------|-------------|
| `categorias` | 5 | Categorías principales |
| `subcategorias` | 20 | Subcategorías de productos |
| `productos` | 15 | Catálogo de productos |
| `usuarios` | 5 | Clientes de la tienda |
| `administradores` | 2 | Usuarios del panel admin |
| `compras` | 10-15 | Pedidos realizados |
| `comentarios` | 40-60 | Reseñas de productos |
| `deseos` | 25-35 | Items en wishlists |
| `comercio` | 1 | Configuración de la tienda |
| `plantilla` | 1 | Configuración de diseño |

---

## 🎨 Imágenes de Productos

### Fuente de Imágenes

Por defecto, el script usa **URLs de Unsplash**, un servicio de imágenes de stock de alta calidad:

```python
# Ejemplo de URLs generadas
https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500
```

### Categorías de Imágenes

| Categoría | Tipo de Imagen |
|-----------|---------------|
| Camisetas | Camisetas básicas y deportivas |
| Pantalones | Vaqueros y pantalones casuales |
| Vestidos | Vestidos elegantes y casuales |
| Zapatos | Zapatillas y calzado variado |
| Accesorios | Gorras, mochilas y accesorios |

### Personalizar Imágenes

Si quieres usar tus propias imágenes:

1. Coloca las imágenes en: `app/static/uploads/productos/`
2. Modifica el script `seed_demo_data.py`
3. Actualiza el diccionario `placeholder_images`

```python
# En seed_demo_data.py línea ~150
self.placeholder_images = {
    'Camisetas': '/static/uploads/productos/camiseta-demo.jpg',
    'Pantalones': '/static/uploads/productos/pantalon-demo.jpg',
    # ...
}
```

---

## 🧪 Casos de Uso para Testing

Con estos datos puedes probar:

### ✅ Funcionalidades de Cliente

- [x] Navegación por categorías y subcategorías
- [x] Búsqueda de productos
- [x] Ver detalles de producto
- [x] Ver productos en oferta
- [x] Agregar productos al carrito
- [x] Proceso de checkout completo
- [x] Ver historial de pedidos
- [x] Agregar/eliminar de lista de deseos
- [x] Escribir reseñas
- [x] Ver reseñas de otros usuarios
- [x] Login/logout de usuarios
- [x] Recuperación de contraseña

### ✅ Funcionalidades de Admin

- [x] Dashboard con estadísticas
- [x] Gestión de productos (CRUD)
- [x] Gestión de categorías
- [x] Gestión de usuarios
- [x] Ver y gestionar pedidos
- [x] Configuración de tienda
- [x] Gestión de descuentos
- [x] Reportes de ventas
- [x] Moderación de reseñas

### ✅ Funcionalidades del Sistema

- [x] Cálculo de precios con ofertas
- [x] Cálculo de costos de envío
- [x] Aplicación de IVA
- [x] Sistema de calificaciones
- [x] Contador de visitas/ventas
- [x] Generación de URLs amigables (slugs)

---

## 🔄 Flujo de Trabajo Recomendado

### Para Desarrollo

```bash
# 1. Configurar base de datos
flask db upgrade

# 2. Poblar con datos demo
python seed_demo_data.py

# 3. Iniciar servidor de desarrollo
flask run

# 4. Probar funcionalidades
# Navega a: http://localhost:5000

# 5. Cuando necesites resetear
python clear_demo_data.py
python seed_demo_data.py
```

### Para Testing

```bash
# 1. Crear base de datos de test
createdb tienda_test

# 2. Configurar .env.test
DATABASE_URL=mysql+pymysql://user:pass@localhost/tienda_test

# 3. Poblar datos
FLASK_ENV=testing python seed_demo_data.py

# 4. Ejecutar tests
pytest
```

---

## 📝 Notas Importantes

### ⚠️ Advertencias

1. **No usar en producción**: Estos datos son solo para desarrollo y testing
2. **Contraseñas débiles**: Las contraseñas de demo son simples y conocidas
3. **Limpiar antes de producción**: Elimina todos los datos demo antes de lanzar
4. **Imágenes externas**: Las URLs de Unsplash dependen de conexión a internet

### 💡 Tips

1. **Backup antes de limpiar**: Siempre haz backup si tienes datos importantes
2. **Personaliza los datos**: Modifica el script para ajustarlo a tus necesidades
3. **Agrega más productos**: Copia el patrón para agregar más categorías/productos
4. **Prueba todos los roles**: Login con diferentes usuarios para probar permisos

### 🐛 Troubleshooting

**Error: "python-slugify not found"**
```bash
pip install python-slugify
```

**Error: "Database connection failed"**
```bash
# Verificar .env
echo $DATABASE_URL

# Verificar MySQL está corriendo
sudo systemctl status mysql
```

**Error: "Table doesn't exist"**
```bash
# Ejecutar migraciones
flask db upgrade
```

---

## 🚀 Próximos Pasos

Después de poblar los datos demo:

1. **Explorar la tienda**
   - Navega como cliente: `http://localhost:5000`
   - Login con usuario demo

2. **Acceder al admin**
   - Panel admin: `http://localhost:5000/admin`
   - Login con admin@tienda.com

3. **Probar funcionalidades**
   - Agregar productos al carrito
   - Realizar una compra
   - Escribir reseñas
   - Gestionar productos desde admin

4. **Personalizar**
   - Modifica productos existentes
   - Agrega nuevas categorías
   - Sube tus propias imágenes
   - Ajusta precios y descuentos

---

## 📚 Referencias

- [Documentación Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Python Slugify](https://github.com/un33k/python-slugify)
- [Unsplash](https://unsplash.com/)

---

## ✨ Resumen Rápido

```bash
# Instalar dependencias
pip install -r requirements.txt

# Poblar datos
python seed_demo_data.py

# Iniciar aplicación
flask run

# Acceder como cliente
http://localhost:5000
Usuario: maria@demo.com / demo123

# Acceder como admin
http://localhost:5000/admin
Usuario: admin@tienda.com / admin123

# Limpiar todo
python clear_demo_data.py --force
```

---

**¡Listo! Tu tienda de demostración está completamente funcional.** 🎉

¿Problemas? Revisa la sección de [Troubleshooting](#-troubleshooting) o abre un issue.
