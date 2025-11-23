# ⚠️ MIGRACIÓN REQUERIDA ANTES DE EJECUTAR

## 🚨 ACCIÓN INMEDIATA NECESARIA

**El código ahora usa columnas de base de datos que NO existen todavía.**
**Debes ejecutar la migración SQL ANTES de iniciar la aplicación.**

---

## 📋 Instrucciones Paso a Paso

### **Opción 1: Usando Python (Recomendado)**

```bash
# Desde la carpeta flask-app/
cd /home/user/Ecommerce_php/flask-app

# Ejecutar script de migración
python run_migration_simple.py
```

**Requisitos**:
- MySQL debe estar corriendo
- Base de datos: `Ecommerce_Ec`
- Usuario: `root` (sin contraseña)

---

### **Opción 2: Usando MySQL directamente**

```bash
# Método 1: Desde línea de comandos
mysql -u root -p Ecommerce_Ec < migrations/002_orden_estados_stock_audit.sql

# Método 2: Desde MySQL CLI
mysql -u root -p
USE Ecommerce_Ec;
SOURCE /home/user/Ecommerce_php/flask-app/migrations/002_orden_estados_stock_audit.sql;
```

---

## ✅ ¿Qué hace la migración?

### 1. **Agrega columnas a tabla `compras`**:
- `precio_total` DECIMAL(10,2) - Precio total incluyendo envío
- `estado` VARCHAR(20) - Estado de la orden (pendiente, procesando, enviado, entregado, cancelado)
- `tracking` VARCHAR(100) - Código de seguimiento
- `fecha_estado` DATETIME - Fecha de última actualización de estado

### 2. **Crea tabla `stock_movements`**:
Auditoría completa de todos los movimientos de stock:
- Ventas
- Cancelaciones
- Ajustes manuales
- Devoluciones

### 3. **Crea tabla `stock_reservations`**:
Reservas temporales durante el proceso de checkout (previene overselling)

### 4. **Actualiza datos existentes**:
- Calcula `precio_total` para órdenes antiguas
- Marca órdenes antiguas como 'entregado'

---

## 🔍 Verificar que la Migración Funcionó

```bash
# Conectar a MySQL
mysql -u root -p Ecommerce_Ec

# Verificar columnas
DESCRIBE compras;

# Deberías ver las nuevas columnas:
# - precio_total
# - estado
# - tracking
# - fecha_estado

# Verificar nuevas tablas
SHOW TABLES LIKE 'stock%';

# Deberías ver:
# - stock_movements
# - stock_reservations

# Salir
EXIT;
```

---

## ❌ Si NO Ejecutas la Migración

La aplicación **fallará** con estos errores:

```
OperationalError: (1054, "Unknown column 'compras.precio_total' in 'field list'")
OperationalError: (1054, "Unknown column 'compras.estado' in 'field list'")
OperationalError: (1054, "Unknown column 'compras.tracking' in 'field list'")
```

**Ubicaciones afectadas**:
- ❌ Admin Dashboard - No cargará
- ❌ Reportes - Queries fallarán
- ❌ Historial de Órdenes - Error al mostrar
- ❌ Proceso de Pago - No podrá crear órdenes
- ❌ Panel de Órdenes - No funcionará

---

## 🛠️ Solución de Problemas

### Error: "Can't connect to MySQL server"
```bash
# Verificar que MySQL está corriendo
sudo systemctl status mysql
# o
sudo service mysql status

# Iniciar MySQL si está detenido
sudo systemctl start mysql
# o
sudo service mysql start
```

### Error: "Access denied for user 'root'"
```bash
# La migración usa usuario 'root' sin contraseña
# Si tu MySQL tiene contraseña, edita:
# flask-app/run_migration_simple.py línea 12-13

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'TU_CONTRASEÑA_AQUI',  # ← Cambiar aquí
    'database': 'Ecommerce_Ec',
    'charset': 'utf8mb4'
}
```

### Error: "Unknown database 'Ecommerce_Ec'"
```bash
# Crear la base de datos primero
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS Ecommerce_Ec CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

---

## 📊 Salida Esperada de la Migración

```
================================================================================
🚀 DATABASE MIGRATION - Order States & Stock Audit
================================================================================

🔄 Connecting to database...
✅ Connected to database: Ecommerce_Ec

📖 Reading migration file...
📝 Found 15 SQL statements

================================================================================

[1] 🔧 ALTER TABLE compras ADD COLUMN precio_total DECIMAL(10,2) DEFAULT NULL...
     ✅ Success

[2] 🔧 ALTER TABLE compras ADD COLUMN estado VARCHAR(20) DEFAULT 'pendiente'...
     ✅ Success

[3] 🔧 ALTER TABLE compras ADD COLUMN tracking VARCHAR(100) DEFAULT NULL...
     ✅ Success

[4] 🔧 ALTER TABLE compras ADD COLUMN fecha_estado DATETIME DEFAULT CURRENT...
     ✅ Success

[5] 🔧 ALTER TABLE compras ADD INDEX idx_estado (estado), ADD INDEX idx_fech...
     ✅ Success

[6] 🔧 UPDATE compras SET precio_total = CAST(pago AS DECIMAL(10,2)) + COALE...
     ✅ Success

[7] 🔧 UPDATE compras SET estado = 'entregado', fecha_estado = fecha WHERE e...
     ✅ Success

[8] 🔧 CREATE TABLE IF NOT EXISTS stock_movements...
     ✅ Success

[9] 🔧 CREATE TABLE IF NOT EXISTS stock_reservations...
     ✅ Success

================================================================================

📊 Migration Summary:
   ✅ Executed successfully: 9
   ⏭️  Skipped: 6
   ❌ Errors: 0

================================================================================
🔍 Verifying migration...

📋 Required columns status:
   ✅ precio_total
   ✅ estado
   ✅ tracking
   ✅ fecha_estado

   ✅ stock_movements table
   ✅ stock_reservations table

✅ ✅ ✅ Migration completed successfully!
   All 4 required columns exist in 'compras' table

🔌 Database connection closed

================================================================================
✅ MIGRATION COMPLETED SUCCESSFULLY
================================================================================
```

---

## 🚀 Después de la Migración

1. **Iniciar la aplicación**:
```bash
cd /home/user/Ecommerce_php/flask-app
python run.py
```

2. **Verificar funcionamiento**:
- ✅ Admin Dashboard debe cargar sin errores
- ✅ Reportes deben generar gráficas
- ✅ Órdenes deben mostrar estados
- ✅ Proceso de pago debe funcionar

3. **Revisar logs**:
```bash
tail -f logs/app.log
```

---

## 📞 Soporte

Si encuentras problemas durante la migración:

1. **Backup de la base de datos**:
```bash
mysqldump -u root -p Ecommerce_Ec > backup_antes_migracion.sql
```

2. **Ejecutar migración con logs detallados**:
```bash
python run_migration_simple.py 2>&1 | tee migration_log.txt
```

3. **Revisar el log generado**: `migration_log.txt`

---

**⚠️ NO EJECUTES LA APLICACIÓN SIN CORRER LA MIGRACIÓN PRIMERO ⚠️**

El sistema NO funcionará hasta que se ejecute la migración SQL.

---

**Última actualización**: 2025-11-23
**Versión**: 002 - Order States & Stock Audit
