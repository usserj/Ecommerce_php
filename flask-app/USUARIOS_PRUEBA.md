# 👥 Usuarios de Prueba - Flask E-commerce

Este documento contiene las credenciales de los usuarios de prueba creados para el sistema.

## 🔧 Configuración Inicial

### 1. Configurar Base de Datos

El archivo `.env` ya está configurado con:

```env
DATABASE_URL=mysql+pymysql://root:@localhost/ferrete5_ecommerce
```

**Credenciales MySQL por defecto:**
- Usuario: `root`
- Contraseña: *(vacía)*
- Base de datos: `ferrete5_ecommerce`

Si tu configuración MySQL es diferente, edita el archivo `.env` y cambia la línea `DATABASE_URL`.

### 2. Crear Usuarios de Prueba

Para crear los usuarios de prueba, ejecuta:

```bash
cd flask-app
python create_test_users.py
```

Este script creará automáticamente los siguientes usuarios:

---

## 📋 Credenciales de Acceso

### 🔐 Usuario Administrador

Acceso al **Panel de Administración** del sistema:

```
┌─────────────────────────────────────────────────┐
│ ADMINISTRADOR                                   │
├─────────────────────────────────────────────────┤
│ Email:    admin@tutienda.ec                     │
│ Password: admin123                              │
│ Perfil:   administrador                         │
│ URL:      http://localhost:5000/admin/login     │
└─────────────────────────────────────────────────┘
```

**Permisos:**
- ✅ Gestión completa de productos
- ✅ Gestión de categorías y subcategorías
- ✅ Gestión de pedidos y ventas
- ✅ Gestión de usuarios y clientes
- ✅ Configuración de la tienda
- ✅ Reportes y estadísticas
- ✅ Acceso total al sistema

---

### 👤 Usuario Normal (Cliente)

Acceso a la **Tienda Online** (frontend):

```
┌─────────────────────────────────────────────────┐
│ CLIENTE DE PRUEBA                               │
├─────────────────────────────────────────────────┤
│ Nombre:   Stalin Pérez                          │
│ Email:    stalin@cliente.com                    │
│ Password: stalin123                             │
│ Estado:   ✅ Verificado                         │
│ URL:      http://localhost:5000/login           │
└─────────────────────────────────────────────────┘
```

**Funcionalidades disponibles:**
- ✅ Navegar y comprar productos
- ✅ Agregar productos al carrito
- ✅ Realizar pedidos
- ✅ Ver historial de compras
- ✅ Gestionar lista de deseos
- ✅ Escribir comentarios y reseñas
- ✅ Actualizar perfil

---

## 🚀 Inicio Rápido

### Paso 1: Iniciar el servidor

```bash
cd flask-app
python run.py
```

El servidor estará disponible en: `http://localhost:5000`

### Paso 2: Acceder al sistema

**Para pruebas de administración:**
1. Ir a: `http://localhost:5000/admin/login`
2. Email: `admin@tutienda.ec`
3. Password: `admin123`

**Para pruebas de compra (cliente):**
1. Ir a: `http://localhost:5000/login`
2. Email: `stalin@cliente.com`
3. Password: `stalin123`

---

## 🔄 Reestablecer Contraseñas

Si necesitas cambiar las contraseñas, ejecuta nuevamente:

```bash
python create_test_users.py
```

El script detectará que los usuarios ya existen y solo actualizará las contraseñas a los valores por defecto.

---

## ⚠️ Notas de Seguridad

**IMPORTANTE:** Estas credenciales son solo para **desarrollo y pruebas**.

En producción:
1. ❌ **NUNCA** uses estas contraseñas
2. ✅ Cambia todas las credenciales
3. ✅ Usa contraseñas fuertes (mínimo 12 caracteres)
4. ✅ Habilita autenticación de dos factores
5. ✅ Configura variables de entorno seguras

---

## 📝 Datos de Prueba Adicionales

Si necesitas datos de demostración completos (productos, categorías, etc.), ejecuta:

```bash
python seed_demo_data.py
```

Esto creará:
- 6 categorías de productos
- 24 productos de ejemplo
- Subcategorías
- Configuración de la tienda
- Slides del carousel

Ver: `README_DEMO_DATA.md` para más información.

---

## 🐛 Solución de Problemas

### Error: "Acceso denegado para el usuario"

Si ves este error:
```
(pymysql.err.OperationalError) (1045, "Acceso denegado...")
```

**Solución:**
1. Verifica que MySQL esté corriendo
2. Edita `.env` y ajusta las credenciales:
   ```env
   DATABASE_URL=mysql+pymysql://TU_USUARIO:TU_PASSWORD@localhost/ferrete5_ecommerce
   ```
3. Asegúrate de que la base de datos existe:
   ```sql
   CREATE DATABASE ferrete5_ecommerce CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

### Los usuarios no se crean

1. Verifica que la base de datos esté creada
2. Ejecuta las migraciones:
   ```bash
   flask db upgrade
   ```
3. Vuelve a ejecutar `python create_test_users.py`

---

## 📞 Ayuda

Para más información, consulta:
- `README.md` - Documentación general
- `README_DEMO_DATA.md` - Datos de demostración
- `COMPARACION_PHP_VS_FLASK.md` - Diferencias con versión PHP
