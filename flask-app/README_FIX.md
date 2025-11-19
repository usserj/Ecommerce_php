# 🔧 Script de Corrección de Base de Datos

Este script corrige automáticamente los problemas de la base de datos, específicamente crea la tabla `mensajes` necesaria para el sistema de mensajería.

## 🚀 Uso Rápido

### Opción 1: Ejecutar directamente (RECOMENDADO)

```bash
cd flask-app
python fix_database.py
```

El script:
- ✅ Lee automáticamente la configuración desde `.env`
- ✅ Se conecta a la base de datos
- ✅ Crea la tabla `mensajes` si no existe
- ✅ Verifica todas las tablas del sistema
- ✅ Muestra un reporte completo

### Opción 2: Si no tienes .env configurado

El script te pedirá la información:

```bash
python fix_database.py
```

Ingresa cuando te pregunte:
- **Host**: localhost (presiona Enter para usar el default)
- **Puerto**: 3306 (presiona Enter para usar el default)
- **Usuario**: root (presiona Enter para usar el default)
- **Contraseña**: tu_contraseña_mysql
- **Base de datos**: ecommerce_ec (presiona Enter para usar el default)

## 📋 Qué hace el script

1. **Prueba la conexión** a MySQL/MariaDB
2. **Verifica** si la tabla `mensajes` existe
3. **Crea la tabla** si no existe con:
   - 11 campos necesarios
   - Índices para rendimiento
   - Foreign keys para integridad
   - Soporte UTF8MB4 para emojis
4. **Verifica todas las tablas** del sistema
5. **Muestra estadísticas** de mensajes si existen datos

## ✅ Salida Esperada

```
╔════════════════════════════════════════════════════════════╗
║          SCRIPT DE CORRECCIÓN DE BASE DE DATOS            ║
║                  Flask E-commerce                          ║
╚════════════════════════════════════════════════════════════╝

==============================================================
PROBANDO CONEXIÓN A BASE DE DATOS
==============================================================

✅ Conexión exitosa a ecommerce_ec en localhost

==============================================================
CREANDO TABLA MENSAJES
==============================================================

ℹ️  Creando tabla 'mensajes'...
✅ Tabla 'mensajes' creada exitosamente
ℹ️  Tabla creada con 11 campos:
  ✓ id: int
  ✓ remitente_tipo: varchar(20)
  ✓ remitente_id: int
  ✓ destinatario_tipo: varchar(20)
  ✓ destinatario_id: int
  ✓ asunto: varchar(255)
  ✓ contenido: text
  ✓ leido: tinyint(1)
  ✓ fecha_leido: datetime
  ✓ mensaje_padre_id: int
  ✓ fecha: datetime

==============================================================
VERIFICANDO TABLAS DE BASE DE DATOS
==============================================================

✅ Tabla 'usuarios' existe
✅ Tabla 'administradores' existe
✅ Tabla 'productos' existe
...

==============================================================
RESUMEN
==============================================================

✓ Conexión a base de datos establecida
✓ Tabla 'mensajes' verificada/creada
✓ Sistema de mensajería listo para usar

Próximos pasos:
1. Reinicia tu aplicación Flask
2. Ve a http://localhost:5000/admin/mensajes
3. Prueba enviar un mensaje de prueba

¡Todo listo! 🎉
```

## 🐛 Solución de Problemas

### Error: "No se pudo conectar a la base de datos"

**Solución:**
1. Verifica que MySQL/MariaDB esté ejecutándose:
   ```bash
   # Windows
   net start MySQL80

   # Linux/Mac
   sudo systemctl start mysql
   ```

2. Verifica las credenciales en `.env`:
   ```
   DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost:3306/ecommerce_ec
   ```

### Error: "Access denied for user"

**Solución:**
- Verifica el usuario y contraseña
- Asegúrate que el usuario tenga permisos CREATE TABLE:
  ```sql
  GRANT ALL PRIVILEGES ON ecommerce_ec.* TO 'tu_usuario'@'localhost';
  FLUSH PRIVILEGES;
  ```

### Error: "Unknown database 'ecommerce_ec'"

**Solución:**
Crea la base de datos primero:
```sql
CREATE DATABASE ecommerce_ec CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### La tabla ya existe pero da error

**Solución:**
El script detectará que existe y mostrará su estructura. Si hay problemas, puedes:

1. Eliminarla y recrearla (CUIDADO: perderás datos):
   ```sql
   DROP TABLE IF EXISTS mensajes;
   ```
   Luego ejecuta el script de nuevo.

2. O verificar manualmente:
   ```sql
   DESCRIBE mensajes;
   ```

## 📊 Estructura de la Tabla Mensajes

```sql
CREATE TABLE mensajes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    remitente_tipo VARCHAR(20) NOT NULL,      -- 'admin' o 'user'
    remitente_id INT NOT NULL,
    destinatario_tipo VARCHAR(20) NOT NULL,   -- 'admin' o 'user'
    destinatario_id INT NOT NULL,
    asunto VARCHAR(255) NOT NULL,
    contenido TEXT NOT NULL,
    leido BOOLEAN DEFAULT FALSE,
    fecha_leido DATETIME NULL,
    mensaje_padre_id INT NULL,                -- Para threading
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (mensaje_padre_id) REFERENCES mensajes(id) ON DELETE CASCADE,

    INDEX idx_remitente (remitente_tipo, remitente_id),
    INDEX idx_destinatario (destinatario_tipo, destinatario_id),
    INDEX idx_leido (leido),
    INDEX idx_fecha (fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## 🔍 Verificación Manual

Después de ejecutar el script, puedes verificar manualmente:

```sql
-- Ver todas las tablas
SHOW TABLES;

-- Ver estructura de mensajes
DESCRIBE mensajes;

-- Ver índices
SHOW INDEX FROM mensajes;

-- Contar registros
SELECT COUNT(*) FROM mensajes;
```

## 💡 Características del Script

- ✅ **Detecta configuración automáticamente** desde `.env`
- ✅ **No duplica tablas** - verifica antes de crear
- ✅ **Muestra progreso** con colores y emojis
- ✅ **Manejo de errores** completo
- ✅ **Verificación de integridad** de la base de datos
- ✅ **Estadísticas** de mensajes existentes
- ✅ **Compatible** con Windows, Linux y Mac

## 📝 Notas

- El script es **idempotente**: puedes ejecutarlo múltiples veces sin problemas
- **No modifica** datos existentes, solo crea estructuras faltantes
- Usa **charset utf8mb4** para soporte completo de caracteres especiales y emojis
- Los **índices** mejoran el rendimiento de las consultas
- El **foreign key** asegura integridad referencial en el threading de mensajes

## 🆘 Ayuda

Si encuentras problemas:
1. Revisa los logs de MySQL/MariaDB
2. Verifica que tengas los permisos necesarios
3. Asegúrate de que la base de datos existe
4. Comprueba que pymysql esté instalado: `pip install pymysql`

---

**¿Listo?** Ejecuta `python fix_database.py` y en segundos tendrás todo corregido. 🚀
