#!/usr/bin/env python3
"""
Script de verificación de configuración.
Ejecutar con: python verificar_configuracion.py

Este script verifica que toda la configuración esté usando el nombre correcto
de base de datos: Ecommerce_Ec
"""

import sys
import os
import pymysql
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def mostrar_header(titulo):
    """Mostrar header formateado."""
    print("\n" + "="*70)
    print(titulo)
    print("="*70)

def verificar_archivos_env():
    """Verificar archivos .env y .env.example."""
    mostrar_header("📝 VERIFICANDO ARCHIVOS DE CONFIGURACIÓN")

    archivos = ['.env', '.env.example']

    for archivo in archivos:
        print(f"\n🔍 Archivo: {archivo}")
        if os.path.exists(archivo):
            print("   ✅ Existe")
            with open(archivo, 'r') as f:
                for i, line in enumerate(f, 1):
                    if 'DATABASE_URL' in line and not line.strip().startswith('#'):
                        print(f"   Línea {i}: {line.strip()}")

                        # Verificar que use Ecommerce_Ec
                        if 'Ecommerce_Ec' in line:
                            print("   ✅ CORRECTO: Usa 'Ecommerce_Ec'")
                        elif 'ecommerce_ec' in line.lower():
                            print("   ⚠️  ADVERTENCIA: Usa minúsculas, debería ser 'Ecommerce_Ec'")
                        elif 'ecommerce_ecuador' in line.lower():
                            print("   ❌ ERROR: Usa 'ecommerce_ecuador', debe ser 'Ecommerce_Ec'")
                        elif 'ferrete' in line.lower():
                            print("   ❌ ERROR: Usa 'ferrete', debe ser 'Ecommerce_Ec'")
        else:
            print("   ⚠️  NO EXISTE")

def verificar_variable_entorno():
    """Verificar variable de entorno DATABASE_URL."""
    mostrar_header("🔧 VERIFICANDO VARIABLE DE ENTORNO")

    database_url = os.environ.get('DATABASE_URL')

    if database_url:
        print(f"\n✅ DATABASE_URL configurada:")
        print(f"   {database_url}")

        if 'Ecommerce_Ec' in database_url:
            print("   ✅ CORRECTO: Usa 'Ecommerce_Ec'")
        elif 'ecommerce_ec' in database_url.lower():
            print("   ⚠️  ADVERTENCIA: Usa minúsculas, debería ser 'Ecommerce_Ec'")
        elif 'ecommerce_ecuador' in database_url.lower():
            print("   ❌ ERROR: Usa 'ecommerce_ecuador', debe ser 'Ecommerce_Ec'")
        else:
            print("   ⚠️  ADVERTENCIA: No reconoce el nombre de la base de datos")
    else:
        print("\n⚠️  DATABASE_URL NO configurada")
        print("   Se usará el valor por defecto de app/config.py")

def verificar_config_py():
    """Verificar app/config.py."""
    mostrar_header("📄 VERIFICANDO app/config.py")

    config_file = 'app/config.py'

    if os.path.exists(config_file):
        print(f"\n✅ Archivo existe: {config_file}")
        with open(config_file, 'r') as f:
            lineas = f.readlines()
            for i, line in enumerate(lineas, 1):
                if 'SQLALCHEMY_DATABASE_URI' in line and 'mysql' in line.lower():
                    print(f"   Línea {i}: {line.strip()}")

                    if i + 1 < len(lineas):
                        next_line = lineas[i]
                        if 'mysql' in next_line:
                            print(f"   Línea {i+1}: {next_line.strip()}")

                    if 'Ecommerce_Ec' in line or (i + 1 < len(lineas) and 'Ecommerce_Ec' in lineas[i]):
                        print("   ✅ CORRECTO: Usa 'Ecommerce_Ec'")
    else:
        print(f"\n❌ Archivo NO existe: {config_file}")

def verificar_bases_datos_mysql():
    """Verificar bases de datos existentes en MySQL."""
    mostrar_header("🗄️  VERIFICANDO BASES DE DATOS EN MYSQL")

    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            charset='utf8mb4'
        )
        cursor = connection.cursor()

        # Listar todas las bases de datos
        cursor.execute("SHOW DATABASES")
        bases = cursor.fetchall()

        print("\n📊 Bases de datos en MySQL:")

        bases_ecommerce = []
        for (db_name,) in bases:
            if 'ecommerce' in db_name.lower() or 'ferrete' in db_name.lower():
                bases_ecommerce.append(db_name)
                if db_name == 'Ecommerce_Ec':
                    print(f"   ✅ {db_name} (CORRECTO)")
                elif db_name.lower() == 'ecommerce_ec':
                    print(f"   ⚠️  {db_name} (debería ser 'Ecommerce_Ec' con mayúsculas)")
                elif db_name.lower() == 'ecommerce_ecuador':
                    print(f"   ❌ {db_name} (base antigua - ELIMINAR)")
                elif 'ferrete' in db_name.lower():
                    print(f"   ❌ {db_name} (base antigua - ELIMINAR)")
                else:
                    print(f"   ⚠️  {db_name}")

        if not bases_ecommerce:
            print("   ⚠️  No se encontraron bases de datos de e-commerce")
            print("      Se creará 'Ecommerce_Ec' al ejecutar run.py")

        # Si existe Ecommerce_Ec, mostrar sus tablas
        if 'Ecommerce_Ec' in bases_ecommerce:
            cursor.execute("USE Ecommerce_Ec")
            cursor.execute("SHOW TABLES")
            tablas = cursor.fetchall()

            print(f"\n📋 Tablas en Ecommerce_Ec: {len(tablas)}")
            if len(tablas) > 0:
                for (tabla,) in tablas:
                    print(f"   - {tabla}")

                # Contar registros en tablas principales
                print("\n📊 Registros en tablas principales:")
                tablas_principales = ['categorias', 'productos', 'usuarios', 'administradores']
                for tabla in tablas_principales:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                        count = cursor.fetchone()[0]
                        print(f"   {tabla:20} {count:5} registros")
                    except:
                        pass

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"\n❌ ERROR conectando a MySQL: {e}")
        print("\n⚠️  Verifica que MySQL esté corriendo")

def verificar_app_flask():
    """Verificar configuración de app Flask."""
    mostrar_header("🐍 VERIFICANDO APLICACIÓN FLASK")

    try:
        from app import create_app

        app = create_app()

        database_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        print(f"\n✅ Flask app configurada")
        print(f"   SQLALCHEMY_DATABASE_URI: {database_uri}")

        if 'Ecommerce_Ec' in database_uri:
            print("   ✅ CORRECTO: Usa 'Ecommerce_Ec'")
        elif 'ecommerce_ec' in database_uri.lower():
            print("   ⚠️  ADVERTENCIA: Usa minúsculas")
        elif 'ecommerce_ecuador' in database_uri.lower():
            print("   ❌ ERROR: Usa 'ecommerce_ecuador'")

    except Exception as e:
        print(f"\n❌ ERROR cargando Flask app: {e}")

def main():
    """Función principal."""
    print("\n" + "="*70)
    print("🔍 VERIFICACIÓN COMPLETA DE CONFIGURACIÓN")
    print("="*70)

    verificar_archivos_env()
    verificar_variable_entorno()
    verificar_config_py()
    verificar_bases_datos_mysql()
    verificar_app_flask()

    mostrar_header("✅ VERIFICACIÓN COMPLETADA")

    print("\n📋 RESUMEN:")
    print("\n✅ SI TODO ESTÁ CORRECTO:")
    print("   - .env y .env.example usan: mysql+pymysql://root:@localhost/Ecommerce_Ec")
    print("   - app/config.py usa: Ecommerce_Ec")
    print("   - Solo existe una base de datos: Ecommerce_Ec")
    print("   - Flask app usa: Ecommerce_Ec")

    print("\n❌ SI HAY PROBLEMAS:")
    print("   1. Ejecuta: python limpiar_y_reiniciar.py")
    print("   2. Luego ejecuta: python run.py")

    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    main()
