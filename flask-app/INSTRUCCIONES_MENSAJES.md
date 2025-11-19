# Instrucciones para Crear la Tabla de Mensajes

La tabla `mensajes` es necesaria para el sistema de mensajería interna entre administradores y usuarios.

## Opción 1: Usando el Script Python (Recomendado)

Ejecuta el siguiente comando en la terminal:

```bash
cd flask-app
python create_mensajes_table.py
```

Este script:
- ✅ Se conecta automáticamente a la base de datos configurada
- ✅ Crea la tabla si no existe
- ✅ Muestra mensajes de confirmación
- ✅ No da error si la tabla ya existe

## Opción 2: Usando SQL Directo

Si prefieres ejecutar SQL manualmente:

### En Windows (MySQL Command Line):

```bash
mysql -u root -p ecommerce_ec < create_mensajes_table.sql
```

### En phpMyAdmin o MySQL Workbench:

1. Abre el archivo `create_mensajes_table.sql`
2. Copia todo el contenido
3. Pégalo en la ventana de consultas SQL
4. Ejecuta el script

## Opción 3: Desde la Aplicación Flask (Automático)

La tabla se creará automáticamente al iniciar la aplicación si:
- La función `auto_init_database()` está habilitada en `app/__init__.py`
- La base de datos está configurada correctamente en `.env`

## Verificar que la Tabla Existe

Ejecuta esta consulta SQL:

```sql
USE ecommerce_ec;
SHOW TABLES LIKE 'mensajes';
DESCRIBE mensajes;
```

Deberías ver una tabla con los siguientes campos:
- `id` (INT, PRIMARY KEY)
- `remitente_tipo` (VARCHAR(20))
- `remitente_id` (INT)
- `destinatario_tipo` (VARCHAR(20))
- `destinatario_id` (INT)
- `asunto` (VARCHAR(255))
- `contenido` (TEXT)
- `leido` (BOOLEAN)
- `fecha_leido` (DATETIME)
- `mensaje_padre_id` (INT, NULLABLE)
- `fecha` (DATETIME)

## Estructura de la Tabla

```sql
CREATE TABLE mensajes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    remitente_tipo VARCHAR(20) NOT NULL,
    remitente_id INT NOT NULL,
    destinatario_tipo VARCHAR(20) NOT NULL,
    destinatario_id INT NOT NULL,
    asunto VARCHAR(255) NOT NULL,
    contenido TEXT NOT NULL,
    leido BOOLEAN DEFAULT FALSE,
    fecha_leido DATETIME NULL,
    mensaje_padre_id INT NULL,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mensaje_padre_id) REFERENCES mensajes(id) ON DELETE CASCADE,
    INDEX idx_remitente (remitente_tipo, remitente_id),
    INDEX idx_destinatario (destinatario_tipo, destinatario_id),
    INDEX idx_leido (leido),
    INDEX idx_fecha (fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Solución de Problemas

### Error: "Access denied"
- Verifica las credenciales de MySQL en el archivo `.env`
- Asegúrate de que el usuario tenga permisos para crear tablas

### Error: "Database doesn't exist"
- Crea la base de datos primero: `CREATE DATABASE ecommerce_ec;`
- O ejecuta el script de inicialización completo

### Error: "Table already exists"
- No es un error real, la tabla ya está creada
- Puedes continuar usando la aplicación normalmente

## Después de Crear la Tabla

Una vez creada la tabla, podrás:
1. Acceder a `/admin/mensajes` en la aplicación
2. Ver mensajes recibidos y enviados
3. Componer nuevos mensajes a usuarios
4. Responder mensajes existentes
5. Ver el contador de mensajes no leídos en la navegación del admin

## Contacto

Si tienes problemas, revisa:
- Los logs de la aplicación Flask
- Los logs de MySQL/MariaDB
- El archivo `PLAN_MIGRACION.md` para más detalles sobre la implementación
