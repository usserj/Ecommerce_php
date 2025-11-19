#!/usr/bin/env python3
"""
Script de verificación para acceso móvil.
Verifica que todo esté configurado correctamente para acceder desde móvil.
"""
import socket
import sys
import os
from pathlib import Path

def get_local_ip():
    """Obtener IP local de la máquina."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None

def check_port_available(port=5000):
    """Verificar si el puerto está disponible o en uso."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0  # True si está en uso (servidor corriendo)

def check_xampp_mysql():
    """Verificar si MySQL está accesible."""
    try:
        import pymysql
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='Ecommerce_Ec'
        )
        connection.close()
        return True
    except Exception as e:
        return False

def check_flask_app():
    """Verificar si la app Flask puede importarse."""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from app import create_app
        app = create_app()
        return True
    except Exception as e:
        return False, str(e)

def main():
    """Ejecutar todas las verificaciones."""
    print("="*70)
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN PARA ACCESO MÓVIL")
    print("="*70 + "\n")

    # 1. Obtener IP local
    print("1️⃣  Verificando IP local...")
    local_ip = get_local_ip()
    if local_ip:
        print(f"   ✅ IP local detectada: {local_ip}")
        print(f"   📱 URL para móvil: http://{local_ip}:5000\n")
    else:
        print("   ❌ No se pudo detectar la IP local")
        print("   💡 Ejecuta 'ipconfig' para ver tu IP manualmente\n")

    # 2. Verificar si el puerto 5000 está en uso
    print("2️⃣  Verificando servidor Flask...")
    if check_port_available(5000):
        print("   ✅ Servidor Flask corriendo en puerto 5000")
        if local_ip:
            print(f"   🌐 Accesible en: http://{local_ip}:5000\n")
    else:
        print("   ⚠️  Puerto 5000 no está en uso")
        print("   💡 Ejecuta 'python run.py' para iniciar el servidor\n")

    # 3. Verificar MySQL
    print("3️⃣  Verificando MySQL (XAMPP)...")
    if check_xampp_mysql():
        print("   ✅ MySQL está corriendo y accesible")
        print("   ✅ Base de datos 'Ecommerce_Ec' existe\n")
    else:
        print("   ❌ No se pudo conectar a MySQL")
        print("   💡 Verifica que XAMPP MySQL esté corriendo\n")

    # 4. Verificar app Flask
    print("4️⃣  Verificando aplicación Flask...")
    result = check_flask_app()
    if result is True:
        print("   ✅ App Flask puede importarse correctamente\n")
    else:
        print("   ❌ Error al importar app Flask")
        if isinstance(result, tuple):
            print(f"   ⚠️  Error: {result[1]}\n")

    # 5. Verificar archivo .env
    print("5️⃣  Verificando configuración (.env)...")
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        print("   ✅ Archivo .env existe\n")
    else:
        print("   ❌ Archivo .env no encontrado")
        print("   💡 Copia .env.example a .env\n")

    # Resumen final
    print("="*70)
    print("📋 RESUMEN Y PRÓXIMOS PASOS")
    print("="*70 + "\n")

    if local_ip:
        print(f"✅ Tu IP actual: {local_ip}")
        print(f"✅ URL para acceder desde móvil: http://{local_ip}:5000\n")

        print("📱 PASOS PARA ACCEDER DESDE MÓVIL:\n")
        print("1. Asegúrate de que el servidor Flask esté corriendo:")
        print("   python run.py\n")
        print("2. Conecta tu móvil al mismo WiFi (red 192.168.3.x)\n")
        print("3. Abre el navegador en tu móvil y ve a:")
        print(f"   http://{local_ip}:5000\n")

        print("🔥 CONFIGURAR FIREWALL (solo primera vez):\n")
        print("   PowerShell como Administrador:")
        print('   New-NetFirewallRule -DisplayName "Flask Server - Puerto 5000" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow -Profile Private,Public\n')
    else:
        print("⚠️  No se pudo detectar tu IP local")
        print("💡 Ejecuta 'ipconfig' en PowerShell y busca tu IPv4\n")

    print("="*70)
    print("📖 Para más información, consulta: ACCESO_MOVIL.md")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
