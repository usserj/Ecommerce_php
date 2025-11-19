#!/usr/bin/env python3
"""
Script para corregir problemas de la base de datos.

Este script:
1. Crea la tabla mensajes si no existe
2. Verifica la estructura de la base de datos
3. Reporta cualquier problema encontrado

Uso:
    python fix_database.py
"""

import os
import sys
import pymysql
from urllib.parse import urlparse

# Colores para la consola
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_header(msg):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"{msg}")
    print(f"{'='*60}{Colors.END}\n")

def get_database_config():
    """Obtener configuración de base de datos desde .env o pedir al usuario."""

    # Intentar leer desde .env
    env_path = os.path.join(os.path.dirname(__file__), '.env')

    if os.path.exists(env_path):
        print_info("Leyendo configuración desde .env...")
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    db_url = line.split('=', 1)[1].strip().strip('"').strip("'")
                    parsed = urlparse(db_url)
                    return {
                        'host': parsed.hostname or 'localhost',
                        'port': parsed.port or 3306,
                        'user': parsed.username or 'root',
                        'password': parsed.password or '',
                        'database': parsed.path.lstrip('/') or 'ecommerce_ec'
                    }

    # Si no existe .env, pedir al usuario
    print_warning("No se encontró archivo .env. Por favor ingrese la configuración:")

    return {
        'host': input("Host (localhost): ").strip() or 'localhost',
        'port': int(input("Puerto (3306): ").strip() or 3306),
        'user': input("Usuario (root): ").strip() or 'root',
        'password': input("Contraseña: ").strip(),
        'database': input("Base de datos (ecommerce_ec): ").strip() or 'ecommerce_ec'
    }

def test_connection(config):
    """Probar conexión a la base de datos."""
    print_header("PROBANDO CONEXIÓN A BASE DE DATOS")

    try:
        connection = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            charset='utf8mb4'
        )
        connection.close()
        print_success(f"Conexión exitosa a {config['database']} en {config['host']}")
        return True
    except Exception as e:
        print_error(f"No se pudo conectar a la base de datos: {e}")
        return False

def create_mensajes_table(config):
    """Crear tabla mensajes si no existe."""
    print_header("CREANDO TABLA MENSAJES")

    try:
        connection = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            charset='utf8mb4'
        )

        with connection.cursor() as cursor:
            # Verificar si la tabla existe
            cursor.execute("SHOW TABLES LIKE 'mensajes'")
            exists = cursor.fetchone()

            if exists:
                print_warning("La tabla 'mensajes' ya existe")

                # Mostrar estructura
                cursor.execute("DESCRIBE mensajes")
                columns = cursor.fetchall()
                print_info("Estructura actual de la tabla:")
                for col in columns:
                    print(f"  - {col[0]}: {col[1]}")

                return True

            # Crear la tabla
            print_info("Creando tabla 'mensajes'...")

            create_sql = """
            CREATE TABLE mensajes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                remitente_tipo VARCHAR(20) NOT NULL COMMENT 'admin o user',
                remitente_id INT NOT NULL,
                destinatario_tipo VARCHAR(20) NOT NULL COMMENT 'admin o user',
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            COMMENT='Sistema de mensajería interna admin-usuario';
            """

            cursor.execute(create_sql)
            connection.commit()

            print_success("Tabla 'mensajes' creada exitosamente")

            # Verificar estructura
            cursor.execute("DESCRIBE mensajes")
            columns = cursor.fetchall()
            print_info(f"Tabla creada con {len(columns)} campos:")
            for col in columns:
                print(f"  ✓ {col[0]}: {col[1]}")

            return True

    except Exception as e:
        print_error(f"Error al crear tabla mensajes: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()

def verify_tables(config):
    """Verificar que todas las tablas necesarias existan."""
    print_header("VERIFICANDO TABLAS DE BASE DE DATOS")

    required_tables = [
        'usuarios',
        'administradores',
        'productos',
        'categorias',
        'subcategorias',
        'compras',
        'comentarios',
        'deseos',
        'comercio',
        'plantilla',
        'slides',
        'banners',
        'cabeceras',
        'notificaciones',
        'visita_pais',
        'visita_persona',
        'cupones',
        'mensajes'
    ]

    try:
        connection = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            charset='utf8mb4'
        )

        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            existing_tables = [table[0] for table in cursor.fetchall()]

            print_info(f"Tablas encontradas: {len(existing_tables)}")

            missing = []
            for table in required_tables:
                if table in existing_tables:
                    print_success(f"Tabla '{table}' existe")
                else:
                    print_warning(f"Tabla '{table}' NO existe")
                    missing.append(table)

            if missing:
                print_warning(f"\nTablas faltantes: {', '.join(missing)}")
                print_info("Nota: Algunas tablas pueden tener nombres diferentes")
            else:
                print_success("\n¡Todas las tablas requeridas están presentes!")

            return len(missing) == 0

    except Exception as e:
        print_error(f"Error al verificar tablas: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()

def check_mensajes_data(config):
    """Verificar datos en la tabla mensajes."""
    print_header("VERIFICANDO DATOS DE MENSAJES")

    try:
        connection = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            charset='utf8mb4'
        )

        with connection.cursor() as cursor:
            # Contar mensajes
            cursor.execute("SELECT COUNT(*) FROM mensajes")
            total = cursor.fetchone()[0]

            if total == 0:
                print_info("La tabla está vacía (esto es normal en una instalación nueva)")
            else:
                print_info(f"Total de mensajes: {total}")

                # Mensajes por tipo
                cursor.execute("""
                    SELECT destinatario_tipo, COUNT(*)
                    FROM mensajes
                    GROUP BY destinatario_tipo
                """)
                for tipo, count in cursor.fetchall():
                    print(f"  - Mensajes para {tipo}: {count}")

                # Mensajes no leídos
                cursor.execute("SELECT COUNT(*) FROM mensajes WHERE leido = FALSE")
                no_leidos = cursor.fetchone()[0]
                print(f"  - Mensajes no leídos: {no_leidos}")

            return True

    except Exception as e:
        print_error(f"Error al verificar datos: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()

def main():
    """Función principal."""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          SCRIPT DE CORRECCIÓN DE BASE DE DATOS            ║")
    print("║                  Flask E-commerce                          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(Colors.END)

    # Obtener configuración
    config = get_database_config()

    # Probar conexión
    if not test_connection(config):
        print_error("\nNo se pudo conectar a la base de datos.")
        print_info("Verifica que:")
        print("  1. MySQL/MariaDB esté ejecutándose")
        print("  2. Las credenciales sean correctas")
        print("  3. La base de datos exista")
        return False

    # Crear tabla mensajes
    if not create_mensajes_table(config):
        print_error("\nNo se pudo crear la tabla mensajes")
        return False

    # Verificar todas las tablas
    verify_tables(config)

    # Verificar datos de mensajes
    check_mensajes_data(config)

    # Resumen final
    print_header("RESUMEN")
    print_success("✓ Conexión a base de datos establecida")
    print_success("✓ Tabla 'mensajes' verificada/creada")
    print_success("✓ Sistema de mensajería listo para usar")

    print(f"\n{Colors.BOLD}Próximos pasos:{Colors.END}")
    print("1. Reinicia tu aplicación Flask")
    print("2. Ve a http://localhost:5000/admin/mensajes")
    print("3. Prueba enviar un mensaje de prueba")

    print(f"\n{Colors.GREEN}{Colors.BOLD}¡Todo listo! 🎉{Colors.END}\n")

    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Operación cancelada por el usuario{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nError inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
