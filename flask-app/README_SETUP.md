# 🚀 Guía de Configuración Rápida - E-commerce Ecuador

Esta guía te ayudará a configurar y poblar la base de datos con datos de demostración en minutos.

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener:

- ✅ Python 3.8 o superior instalado
- ✅ MySQL 5.7 o superior corriendo
- ✅ Pip (gestor de paquetes de Python)

---

## 🎯 Instalación Rápida (3 Pasos)

### Paso 1: Instalar Dependencias

```bash
cd flask-app
pip install -r requirements.txt
```

### Paso 2: Configurar Base de Datos

Edita el archivo `.env` o copia `.env.example` a `.env`:

```bash
cp .env.example .env
```

**Configuración por defecto** (MySQL con root sin contraseña):

```env
DATABASE_URL=mysql+pymysql://root:@localhost/Ecommerce_Ec
```

**Si tu MySQL tiene contraseña**, edita `.env`:

```env
DATABASE_URL=mysql+pymysql://root:TU_PASSWORD@localhost/Ecommerce_Ec
```

### Paso 3: Configurar Sistema Completo

Ejecuta el script de setup automático:

```bash
python setup_demo.py
```

Este script hará TODO automáticamente:
- ✅ Crea la base de datos `Ecommerce_Ec`
- ✅ Crea todas las tablas necesarias
- ✅ Pobla con datos de demostración (productos, categorías, usuarios)
- ✅ Configura usuarios administradores y clientes
- ✅ Genera pedidos y reseñas de ejemplo

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

### 👤 Usuarios Clientes (para probar compras)

```
URL:      http://localhost:5000/login

Todos los usuarios demo tienen la contraseña: demo123

Emails disponibles:
- carlos.mendoza@email.com
- maria.gonzalez@email.com
- luis.torres@email.com
- ana.rodriguez@email.com
- pedro.ramirez@email.com
```

---

## 🏃 Iniciar el Servidor

```bash
python run.py
```

El servidor estará disponible en: **http://localhost:5000**

---

## 📦 ¿Qué Datos se Crean?

El script `setup_demo.py` crea:

### Productos (24+ productos en 6 categorías):
- 📱 Electrónica (smartphones, laptops, audífonos)
- 🏠 Hogar y Cocina (electrodomésticos, utensilios)
- 👕 Moda y Accesorios (zapatillas, mochilas, relojes)
- 🏋️ Deportes y Fitness (pesas, yoga, bicicletas)
- 📚 Libros y Educación (desarrollo personal, programación)
- 💄 Belleza y Salud (suplementos, cuidado facial)

### Usuarios:
- 2 administradores (admin + editor)
- 5 clientes demo

### Datos adicionales:
- 10-15 pedidos de ejemplo
- 30-40 reseñas de productos
- Listas de deseos
- Configuración de tienda (IVA 15% Ecuador, envíos, etc.)

---

## 🔄 Resetear Datos

Si quieres empezar de nuevo con datos frescos:

```bash
python setup_demo.py
```

El script detectará datos existentes, los limpiará y creará todo nuevamente.

---

## ⚙️ Configuración de la Tienda

La configuración por defecto para Ecuador incluye:

- **IVA**: 15% (impuesto Ecuador 2025)
- **Envío Nacional**: $5.99 (GRATIS en compras > $40)
- **Envío Internacional**: $25.99 (GRATIS en compras > $100)
- **Moneda**: Dólares estadounidenses (USD)
- **País**: Ecuador

---

## 🐛 Solución de Problemas

### Error: "Acceso denegado para el usuario"

**Causa**: Credenciales incorrectas de MySQL

**Solución**:
1. Verifica que MySQL esté corriendo
2. Confirma tu usuario y contraseña de MySQL
3. Edita `.env` con tus credenciales correctas:
   ```env
   DATABASE_URL=mysql+pymysql://TU_USUARIO:TU_PASSWORD@localhost/Ecommerce_Ec
   ```

### Error: "Can't connect to MySQL server"

**Causa**: MySQL no está corriendo

**Solución**:
```bash
# Windows
net start MySQL

# Linux/Mac
sudo service mysql start
# o
sudo systemctl start mysql
```

### Error: "ModuleNotFoundError"

**Causa**: Dependencias no instaladas

**Solución**:
```bash
pip install -r requirements.txt
```

### La base de datos no se crea

**Solución manual**:
```bash
mysql -u root -p
```

Luego en el prompt de MySQL:
```sql
CREATE DATABASE Ecommerce_Ec CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;
```

Ejecuta nuevamente:
```bash
python setup_demo.py
```

---

## 📚 Documentación Adicional

- `README.md` - Documentación general del proyecto
- `DEPLOYMENT.md` - Guía de despliegue en producción
- `QUICK_START.md` - Inicio rápido
- `MIGRATION_GUIDE.md` - Migración desde PHP
- `README_DEMO_DATA.md` - Detalles de datos de demostración

---

## 🔒 Seguridad

**⚠️ IMPORTANTE**: Las credenciales demo son solo para desarrollo local.

**En producción**:
1. ❌ NUNCA uses estas contraseñas
2. ✅ Cambia TODAS las credenciales
3. ✅ Usa contraseñas fuertes (mínimo 12 caracteres)
4. ✅ Habilita HTTPS
5. ✅ Configura variables de entorno seguras
6. ✅ Cambia el `SECRET_KEY` en producción

---

## 💡 Próximos Pasos

1. ✅ Ejecuta `python setup_demo.py`
2. ✅ Inicia el servidor con `python run.py`
3. ✅ Explora el panel de administración
4. ✅ Prueba el flujo de compra como cliente
5. ✅ Personaliza productos y categorías
6. ✅ Configura métodos de pago (PayPal, PayU)
7. ✅ Configura email para notificaciones

---

## 📞 Soporte

Para más información o ayuda:
- Revisa la documentación en la carpeta `/docs`
- Consulta `README.md` para guías detalladas
- Reporta issues en el repositorio del proyecto

---

**¡Listo! Tu e-commerce de Ecuador está configurado y listo para usar.** 🎉
