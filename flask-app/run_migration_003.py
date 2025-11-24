#!/usr/bin/env python3
"""
Script para ejecutar migración 003 - Crear tablas faltantes.
"""

import pymysql
import sys
from app import create_app

def run_migration():
    """Execute SQL migration 003."""
    app = create_app()

    with app.app_context():
        try:
            print("🔄 Ejecutando migración 003 - Crear tablas faltantes...")

            # Get database connection info from config
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']

            # Extract connection details
            import re
            match = re.match(r'mysql\+pymysql://([^:]+):([^@]*)@([^/]+)/(.+)', db_uri)
            if not match:
                print("❌ No se pudo parsear la URI de la base de datos")
                return False

            user, password, host, database = match.groups()

            # Read SQL file
            print("📖 Leyendo archivo de migración...")
            with open('migrations/003_create_missing_tables.sql', 'r', encoding='utf-8') as f:
                sql_content = f.read()

            # Connect to database
            connection = pymysql.connect(
                host=host,
                user=user,
                password=password if password else '',
                database=database,
                cursorclass=pymysql.cursors.DictCursor
            )

            print(f"✅ Conectado a base de datos: {database}\n")

            # Limpiar comentarios de línea
            lines = sql_content.split('\n')
            cleaned_lines = []
            for line in lines:
                # Remover comentarios -- pero preservar líneas con código
                if line.strip().startswith('--'):
                    continue
                cleaned_lines.append(line)

            sql_cleaned = '\n'.join(cleaned_lines)

            # Split por ; pero solo fuera de paréntesis
            statements = []
            current_statement = []
            paren_depth = 0

            for char in sql_cleaned:
                current_statement.append(char)
                if char == '(':
                    paren_depth += 1
                elif char == ')':
                    paren_depth -= 1
                elif char == ';' and paren_depth == 0:
                    stmt = ''.join(current_statement).strip()
                    if stmt and not stmt.startswith('--'):
                        statements.append(stmt)
                    current_statement = []

            # Agregar última sentencia si existe
            if current_statement:
                stmt = ''.join(current_statement).strip()
                if stmt and not stmt.startswith('--'):
                    statements.append(stmt)

            print(f"📝 Ejecutando {len(statements)} declaraciones SQL...\n")
            print("=" * 80)

            executed = 0
            skipped = 0

            with connection.cursor() as cursor:
                for i, statement in enumerate(statements, 1):
                    # Skip vacíos
                    if not statement or statement.isspace():
                        continue

                    # Skip SELECT verification queries (execute but don't count)
                    if statement.strip().upper().startswith('SELECT'):
                        try:
                            cursor.execute(statement)
                            results = cursor.fetchall()
                            if results:
                                print(f"\n[{i}] 📊 Verificación:")
                                for row in results:
                                    print(f"     {row}")
                        except:
                            pass
                        skipped += 1
                        continue

                    try:
                        print(f"\n[{i}] 🔧 {statement[:80]}...")
                        cursor.execute(statement)
                        connection.commit()
                        executed += 1
                        print(f"     ✅ Ejecutado correctamente")
                    except pymysql.err.OperationalError as e:
                        error_str = str(e)
                        if 'already exists' in error_str or 'Duplicate' in error_str:
                            print(f"     ⚠️  Ya existe (omitiendo)")
                            skipped += 1
                        else:
                            print(f"     ❌ Error: {e}")
                            raise

            print("\n" + "=" * 80)
            print(f"\n📊 Resumen de Migración:")
            print(f"   ✅ Ejecutados: {executed}")
            print(f"   ⏭️  Omitidos: {skipped}")

            # Verify tables exist
            print("\n" + "=" * 80)
            print("🔍 Verificando tablas creadas...\n")

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT TABLE_NAME, TABLE_ROWS
                    FROM information_schema.TABLES
                    WHERE TABLE_SCHEMA = %s
                    AND TABLE_NAME IN ('stock_movements', 'addresses', 'stock_reservations')
                    ORDER BY TABLE_NAME
                """, (database,))

                tables = cursor.fetchall()

                if tables:
                    print("✅ Tablas encontradas:")
                    for table in tables:
                        print(f"   ✓ {table['TABLE_NAME']} ({table['TABLE_ROWS']} registros)")
                else:
                    print("⚠️  No se encontraron las tablas")

            connection.close()
            print("\n✅ Migración 003 completada exitosamente!\n")
            return True

        except Exception as e:
            print(f"\n❌ Error en migración: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
