#!/usr/bin/env python3
"""
Script completo de validación y migración de base de datos.
Compara modelos SQLAlchemy con estructura real de MySQL y genera migraciones.
"""

import pymysql
import sys
import re
from sqlalchemy import inspect, create_engine
from sqlalchemy.dialects import mysql
from app import create_app
from app.extensions import db

# Colores para la consola
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Imprimir encabezado."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}\n")

def print_success(text):
    """Imprimir éxito."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text):
    """Imprimir advertencia."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    """Imprimir error."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    """Imprimir información."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def get_db_connection(app):
    """Obtener conexión a MySQL."""
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']

    # Parsear URI
    match = re.match(r'mysql\+pymysql://([^:]+):([^@]*)@([^/]+)/(.+)', db_uri)
    if not match:
        print_error("No se pudo parsear la URI de la base de datos")
        return None

    user, password, host, database = match.groups()

    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password if password else '',
            database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print_success(f"Conectado a base de datos: {database}")
        return connection
    except Exception as e:
        print_error(f"Error conectando a MySQL: {e}")
        return None

def get_db_tables(connection):
    """Obtener todas las tablas de la base de datos."""
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = [list(row.values())[0] for row in cursor.fetchall()]
    return tables

def get_db_columns(connection, table_name):
    """Obtener todas las columnas de una tabla."""
    with connection.cursor() as cursor:
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()

    column_info = {}
    for col in columns:
        column_info[col['Field']] = {
            'type': col['Type'],
            'null': col['Null'],
            'key': col['Key'],
            'default': col['Default'],
            'extra': col['Extra']
        }

    return column_info

def get_sqlalchemy_type_as_mysql(column_type):
    """Convertir tipo SQLAlchemy a tipo MySQL."""
    type_str = str(column_type)

    # Tipos básicos
    if 'INTEGER' in type_str:
        return 'int(11)'
    elif 'VARCHAR' in type_str:
        # Extraer longitud
        match = re.search(r'VARCHAR\((\d+)\)', type_str)
        if match:
            return f"varchar({match.group(1)})"
        return 'varchar(255)'
    elif 'TEXT' in type_str:
        return 'text'
    elif 'DATETIME' in type_str:
        return 'datetime'
    elif 'NUMERIC' in type_str or 'DECIMAL' in type_str:
        match = re.search(r'NUMERIC\((\d+),\s*(\d+)\)', type_str)
        if match:
            return f"decimal({match.group(1)},{match.group(2)})"
        return 'decimal(10,2)'
    elif 'FLOAT' in type_str:
        return 'float'
    elif 'JSON' in type_str:
        return 'json'
    elif 'BOOLEAN' in type_str or 'TINYINT(1)' in type_str:
        return 'tinyint(1)'
    else:
        return type_str.lower()

def get_model_columns(model):
    """Obtener todas las columnas de un modelo SQLAlchemy."""
    inspector = inspect(model)
    columns = {}

    for column in inspector.columns:
        mysql_type = get_sqlalchemy_type_as_mysql(column.type)

        columns[column.name] = {
            'type': mysql_type,
            'nullable': column.nullable,
            'primary_key': column.primary_key,
            'default': column.default,
            'foreign_key': len(column.foreign_keys) > 0
        }

    return columns

def compare_tables_and_columns(app, connection):
    """Comparar todas las tablas y columnas entre modelos y BD."""

    print_header("ANÁLISIS DE MODELOS VS BASE DE DATOS")

    # Obtener todos los modelos
    models = {
        'usuarios': 'app.models.user.User',
        'administradores': 'app.models.admin.Administrador',
        'productos': 'app.models.product.Producto',
        'categorias': 'app.models.categoria.Categoria',
        'subcategorias': 'app.models.categoria.Subcategoria',
        'compras': 'app.models.order.Compra',
        'comentarios': 'app.models.comment.Comentario',
        'deseos': 'app.models.wishlist.Deseo',
        'cupones': 'app.models.cupon.Cupon',
        'stock_movements': 'app.models.stock_movement.StockMovement',
        'addresses': 'app.models.address.Address',
    }

    # Obtener tablas de la BD
    db_tables = get_db_tables(connection)

    missing_columns = []
    extra_columns = []
    type_mismatches = []
    missing_tables = []

    for table_name, model_path in models.items():
        print(f"\n{Colors.BOLD}Tabla: {table_name}{Colors.END}")

        # Verificar si la tabla existe
        if table_name not in db_tables:
            print_error(f"Tabla '{table_name}' NO EXISTE en la base de datos")
            missing_tables.append(table_name)
            continue

        # Importar el modelo
        try:
            module_name, class_name = model_path.rsplit('.', 1)
            module = __import__(module_name, fromlist=[class_name])
            model = getattr(module, class_name)
        except Exception as e:
            print_warning(f"No se pudo importar modelo {model_path}: {e}")
            continue

        # Obtener columnas del modelo y de la BD
        model_columns = get_model_columns(model)
        db_columns = get_db_columns(connection, table_name)

        # Comparar columnas
        model_col_names = set(model_columns.keys())
        db_col_names = set(db_columns.keys())

        # Columnas faltantes en BD
        missing_in_db = model_col_names - db_col_names
        if missing_in_db:
            for col in missing_in_db:
                print_error(f"  Columna '{col}' falta en BD (existe en modelo)")
                missing_columns.append({
                    'table': table_name,
                    'column': col,
                    'info': model_columns[col]
                })

        # Columnas extra en BD
        extra_in_db = db_col_names - model_col_names
        if extra_in_db:
            for col in extra_in_db:
                print_warning(f"  Columna '{col}' existe en BD pero no en modelo")
                extra_columns.append({
                    'table': table_name,
                    'column': col,
                    'info': db_columns[col]
                })

        # Columnas comunes - verificar tipos
        common_columns = model_col_names & db_col_names
        if common_columns:
            print_success(f"  {len(common_columns)} columnas en común")

            for col in common_columns:
                model_type = model_columns[col]['type']
                db_type = db_columns[col]['type']

                # Normalizar tipos para comparación
                model_type_norm = model_type.lower().replace(' ', '')
                db_type_norm = db_type.lower().replace(' ', '')

                # Comparación flexible de tipos
                if not types_match(model_type_norm, db_type_norm):
                    print_warning(f"    Tipo diferente en '{col}': Modelo='{model_type}' vs BD='{db_type}'")
                    type_mismatches.append({
                        'table': table_name,
                        'column': col,
                        'model_type': model_type,
                        'db_type': db_type
                    })

    return {
        'missing_columns': missing_columns,
        'extra_columns': extra_columns,
        'type_mismatches': type_mismatches,
        'missing_tables': missing_tables
    }

def types_match(type1, type2):
    """Verificar si dos tipos son compatibles."""
    # Normalizar
    type1 = type1.replace('(11)', '').replace(' ', '')
    type2 = type2.replace('(11)', '').replace(' ', '')

    # Equivalencias comunes
    equivalents = [
        {'int', 'integer'},
        {'text', 'longtext', 'mediumtext'},
        {'tinyint(1)', 'boolean'},
        {'varchar', 'string'},
    ]

    if type1 == type2:
        return True

    for equiv_set in equivalents:
        if any(t in type1 for t in equiv_set) and any(t in type2 for t in equiv_set):
            return True

    return False

def generate_migration_sql(analysis_result):
    """Generar SQL de migración basado en el análisis."""

    print_header("GENERACIÓN DE SCRIPT DE MIGRACIÓN")

    sql_statements = []

    # Crear tablas faltantes
    if analysis_result['missing_tables']:
        print_info("Tablas faltantes detectadas:")
        for table in analysis_result['missing_tables']:
            print(f"  - {table}")
        print_warning("NOTA: Crear tablas completas requiere definiciones manuales")
        sql_statements.append(f"-- CREAR TABLAS FALTANTES: {', '.join(analysis_result['missing_tables'])}")

    # Agregar columnas faltantes
    if analysis_result['missing_columns']:
        print_info(f"{len(analysis_result['missing_columns'])} columnas faltantes en BD")

        for item in analysis_result['missing_columns']:
            table = item['table']
            column = item['column']
            info = item['info']

            # Construir tipo SQL
            col_type = info['type']
            nullable = "NULL" if info['nullable'] else "NOT NULL"

            # Default
            default = ""
            if info['default'] is not None:
                if hasattr(info['default'], 'arg'):
                    default_val = info['default'].arg
                    if isinstance(default_val, str):
                        default = f"DEFAULT '{default_val}'"
                    elif callable(default_val):
                        default = "DEFAULT CURRENT_TIMESTAMP" if 'datetime' in col_type.lower() else ""
                    else:
                        default = f"DEFAULT {default_val}"

            sql = f"ALTER TABLE {table} ADD COLUMN {column} {col_type} {nullable} {default};".strip()
            sql_statements.append(sql)
            print(f"  {Colors.GREEN}+{Colors.END} {table}.{column}")

    return sql_statements

def execute_migration(connection, sql_statements, auto_execute=False):
    """Ejecutar migración."""

    if not sql_statements:
        print_success("No hay migraciones que ejecutar")
        return True

    print_header("EJECUCIÓN DE MIGRACIÓN")

    print(f"\n{Colors.BOLD}Se ejecutarán {len(sql_statements)} comandos SQL:{Colors.END}\n")

    for i, sql in enumerate(sql_statements, 1):
        if sql.startswith('--'):
            print(f"{Colors.YELLOW}{sql}{Colors.END}")
            continue
        print(f"[{i}] {sql}")

    if not auto_execute:
        print(f"\n{Colors.YELLOW}¿Ejecutar migración? (s/n): {Colors.END}", end='')
        response = input().lower().strip()

        if response != 's':
            print_warning("Migración cancelada por el usuario")
            return False

    print("\nEjecutando migración...\n")

    executed = 0
    errors = 0

    with connection.cursor() as cursor:
        for i, sql in enumerate(sql_statements, 1):
            if sql.startswith('--'):
                continue

            try:
                cursor.execute(sql)
                connection.commit()
                print_success(f"[{i}] Ejecutado correctamente")
                executed += 1
            except pymysql.err.OperationalError as e:
                if 'Duplicate column' in str(e):
                    print_warning(f"[{i}] Columna ya existe (omitiendo)")
                else:
                    print_error(f"[{i}] Error: {e}")
                    errors += 1
            except Exception as e:
                print_error(f"[{i}] Error: {e}")
                errors += 1

    print(f"\n{Colors.BOLD}Resumen:{Colors.END}")
    print_success(f"Ejecutados: {executed}")
    if errors > 0:
        print_error(f"Errores: {errors}")

    return errors == 0

def save_report(analysis_result, sql_statements, filename='db_validation_report.txt'):
    """Guardar reporte detallado."""

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("REPORTE DE VALIDACIÓN DE BASE DE DATOS\n")
        f.write("=" * 80 + "\n\n")

        f.write("RESUMEN:\n")
        f.write(f"  - Tablas faltantes: {len(analysis_result['missing_tables'])}\n")
        f.write(f"  - Columnas faltantes: {len(analysis_result['missing_columns'])}\n")
        f.write(f"  - Columnas extra: {len(analysis_result['extra_columns'])}\n")
        f.write(f"  - Diferencias de tipo: {len(analysis_result['type_mismatches'])}\n\n")

        if analysis_result['missing_tables']:
            f.write("\nTABLAS FALTANTES:\n")
            for table in analysis_result['missing_tables']:
                f.write(f"  - {table}\n")

        if analysis_result['missing_columns']:
            f.write("\nCOLUMNAS FALTANTES EN BD:\n")
            for item in analysis_result['missing_columns']:
                f.write(f"  - {item['table']}.{item['column']} ({item['info']['type']})\n")

        if analysis_result['extra_columns']:
            f.write("\nCOLUMNAS EXTRA EN BD (no en modelo):\n")
            for item in analysis_result['extra_columns']:
                f.write(f"  - {item['table']}.{item['column']}\n")

        if analysis_result['type_mismatches']:
            f.write("\nDIFERENCIAS DE TIPO:\n")
            for item in analysis_result['type_mismatches']:
                f.write(f"  - {item['table']}.{item['column']}: {item['model_type']} vs {item['db_type']}\n")

        f.write("\n\nSCRIPT DE MIGRACIÓN:\n")
        f.write("=" * 80 + "\n")
        for sql in sql_statements:
            f.write(sql + "\n")

    print_success(f"Reporte guardado en: {filename}")

def main():
    """Función principal."""

    print_header("🔍 VALIDACIÓN Y MIGRACIÓN DE BASE DE DATOS")

    # Crear aplicación Flask
    app = create_app()

    with app.app_context():
        # Conectar a MySQL
        connection = get_db_connection(app)
        if not connection:
            return 1

        try:
            # Analizar diferencias
            analysis_result = compare_tables_and_columns(app, connection)

            # Generar script de migración
            sql_statements = generate_migration_sql(analysis_result)

            # Guardar reporte
            save_report(analysis_result, sql_statements)

            # Ejecutar migración
            if sql_statements:
                success = execute_migration(connection, sql_statements, auto_execute=False)

                if success:
                    print_header("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
                else:
                    print_header("⚠️  MIGRACIÓN COMPLETADA CON ERRORES")
                    return 1
            else:
                print_header("✅ BASE DE DATOS SINCRONIZADA")

            return 0

        finally:
            connection.close()
            print_info("Conexión cerrada")

if __name__ == '__main__':
    sys.exit(main())
