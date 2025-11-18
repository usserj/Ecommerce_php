#!/usr/bin/env python3
"""
Script de limpieza completa y reinicio del sistema.
Ejecutar con: python limpiar_y_reiniciar.py

Este script:
1. Limpia archivos de caché de Python
2. Elimina bases de datos antiguas (ecommerce_ecuador, ecommerce_ec)
3. Elimina la base de datos actual para empezar de cero
4. Reinicia todo el sistema
"""

import sys
import os
import shutil
import pymysql

def limpiar_cache():
    """Eliminar archivos de caché de Python."""
    print("\n" + "="*70)
    print("🧹 LIMPIANDO CACHÉ DE PYTHON")
    print("="*70)

    # Eliminar __pycache__
    cache_dirs = 0
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            cache_path = os.path.join(root, '__pycache__')
            shutil.rmtree(cache_path)
            cache_dirs += 1

    # Eliminar archivos .pyc
    pyc_files = 0
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
                pyc_files += 1

    print(f"✅ Eliminados {cache_dirs} directorios __pycache__")
    print(f"✅ Eliminados {pyc_files} archivos .pyc")


def limpiar_bases_datos():
    """Eliminar bases de datos antiguas."""
    print("\n" + "="*70)
    print("🗄️  LIMPIANDO BASES DE DATOS ANTIGUAS")
    print("="*70)

    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            charset='utf8mb4'
        )
        cursor = connection.cursor()

        # Bases de datos a eliminar
        bases_antiguas = ['ecommerce_ecuador', 'ecommerce_ec', 'Ecommerce_Ec']

        for db_name in bases_antiguas:
            try:
                cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
                print(f"✅ Base de datos '{db_name}' eliminada")
            except Exception as e:
                print(f"⚠️  No se pudo eliminar '{db_name}': {e}")

        cursor.close()
        connection.close()

        print("\n✅ Todas las bases de datos antiguas han sido eliminadas")

    except Exception as e:
        print(f"❌ ERROR conectando a MySQL: {e}")
        print("\n⚠️  Asegúrate de que:")
        print("   1. MySQL esté corriendo")
        print("   2. Tu usuario y contraseña sean correctos")
        print("\nSi tu MySQL tiene contraseña, edita este script y cambia:")
        print("   password=''  ->  password='TU_PASSWORD'")
        sys.exit(1)


def verificar_configuracion():
    """Verificar configuración actual."""
    print("\n" + "="*70)
    print("🔍 VERIFICANDO CONFIGURACIÓN")
    print("="*70)

    # Verificar .env
    if os.path.exists('.env'):
        print("\n📝 Archivo .env encontrado:")
        with open('.env', 'r') as f:
            for line in f:
                if 'DATABASE_URL' in line and not line.strip().startswith('#'):
                    print(f"   {line.strip()}")
                    if 'Ecommerce_Ec' in line:
                        print("   ✅ Usando el nombre de base de datos correcto: Ecommerce_Ec")
                    else:
                        print("   ❌ ADVERTENCIA: No está usando 'Ecommerce_Ec'")
    else:
        print("\n⚠️  Archivo .env NO existe")
        print("   Se creará automáticamente al ejecutar run.py")

    # Verificar .env.example
    if os.path.exists('.env.example'):
        print("\n📝 Archivo .env.example encontrado:")
        with open('.env.example', 'r') as f:
            for line in f:
                if 'DATABASE_URL' in line and not line.strip().startswith('#'):
                    print(f"   {line.strip()}")
                    break

    # Verificar config.py
    config_file = 'app/config.py'
    if os.path.exists(config_file):
        print(f"\n📝 Archivo {config_file}:")
        with open(config_file, 'r') as f:
            for line in f:
                if 'mysql' in line.lower() and 'ecommerce' in line.lower():
                    print(f"   {line.strip()}")


def main():
    """Función principal."""
    print("\n" + "="*70)
    print("🚀 SCRIPT DE LIMPIEZA Y REINICIO COMPLETO")
    print("="*70)
    print("\nEste script hará lo siguiente:")
    print("1. ✅ Limpiar archivos de caché de Python")
    print("2. ✅ Eliminar bases de datos antiguas:")
    print("   - ecommerce_ecuador")
    print("   - ecommerce_ec")
    print("   - Ecommerce_Ec")
    print("3. ✅ Verificar configuración actual")
    print("\n⚠️  ADVERTENCIA: Se eliminarán TODAS las bases de datos existentes")
    print("="*70)

    respuesta = input("\n¿Deseas continuar? (s/n): ")
    if respuesta.lower() != 's':
        print("\n❌ Operación cancelada")
        sys.exit(0)

    # Ejecutar limpieza
    limpiar_cache()
    limpiar_bases_datos()
    verificar_configuracion()

    # Instrucciones finales
    print("\n" + "="*70)
    print("✅ LIMPIEZA COMPLETA EXITOSA")
    print("="*70)
    print("\n📋 PRÓXIMOS PASOS:")
    print("\n1. Ejecuta la aplicación:")
    print("   python run.py")
    print("\n2. El sistema creará automáticamente:")
    print("   ✅ Base de datos 'Ecommerce_Ec'")
    print("   ✅ Todas las tablas")
    print("   ✅ Datos demo (productos, categorías, usuarios)")
    print("\n3. Accede a la aplicación:")
    print("   http://localhost:5000")
    print("\n4. Credenciales:")
    print("   Admin:   admin@ecommerce.ec / admin123")
    print("   Cliente: carlos.mendoza@email.com / demo123")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
