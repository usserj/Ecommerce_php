"""Run this script ONCE to apply database migrations."""
import pymysql
import sys

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Cambia si tienes contraseña
    'database': 'Ecommerce_Ec',
    'charset': 'utf8mb4'
}

# SQL statements to execute
SQL_STATEMENTS = [
    # Add reset token fields to usuarios table
    """
    ALTER TABLE usuarios
    ADD COLUMN reset_token VARCHAR(255) NULL,
    ADD COLUMN reset_token_expiry DATETIME NULL
    """,

    # Add moderation fields to comentarios table
    """
    ALTER TABLE comentarios
    ADD COLUMN estado VARCHAR(20) DEFAULT 'aprobado' NOT NULL,
    ADD COLUMN respuesta_admin TEXT NULL,
    ADD COLUMN fecha_moderacion DATETIME NULL
    """,

    # Add index on estado
    """
    ALTER TABLE comentarios ADD INDEX idx_estado (estado)
    """,

    # Update existing comments
    """
    UPDATE comentarios SET estado = 'aprobado' WHERE estado IS NULL OR estado = ''
    """
]

def main():
    print("\n" + "="*60)
    print("🔧 APLICANDO MIGRACIÓN DE BASE DE DATOS")
    print("="*60 + "\n")

    try:
        # Connect to database
        print(f"📡 Conectando a MySQL ({DB_CONFIG['host']})...")
        connection = pymysql.connect(**DB_CONFIG)
        print("✅ Conexión exitosa\n")

        with connection.cursor() as cursor:
            success_count = 0
            skip_count = 0

            for i, sql in enumerate(SQL_STATEMENTS, 1):
                try:
                    print(f"⏳ Ejecutando migración {i}/{len(SQL_STATEMENTS)}...")
                    cursor.execute(sql)
                    connection.commit()
                    print(f"✅ Migración {i} aplicada exitosamente")
                    success_count += 1
                except pymysql.err.OperationalError as e:
                    if 'Duplicate column name' in str(e) or 'Duplicate key name' in str(e):
                        print(f"⊘ Migración {i} ya aplicada (omitida)")
                        skip_count += 1
                    else:
                        print(f"❌ Error en migración {i}: {e}")
                        raise
                print()

        print("="*60)
        print(f"✅ MIGRACIÓN COMPLETADA")
        print(f"   • Aplicadas: {success_count}")
        print(f"   • Omitidas: {skip_count}")
        print("="*60 + "\n")
        print("🚀 Ahora puedes reiniciar el servidor Flask:")
        print("   python run.py\n")

    except pymysql.err.OperationalError as e:
        if '1045' in str(e):  # Access denied
            print("\n❌ ERROR DE CONEXIÓN")
            print(f"   {e}")
            print("\n💡 SOLUCIÓN:")
            print("   1. Abre este archivo: fix_database.py")
            print("   2. Edita la línea 8 con tu contraseña de MySQL:")
            print("      'password': 'TU_CONTRASEÑA_AQUI',")
            print("   3. Guarda y ejecuta de nuevo\n")
        else:
            print(f"\n❌ ERROR: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}\n")
        sys.exit(1)
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == '__main__':
    main()
