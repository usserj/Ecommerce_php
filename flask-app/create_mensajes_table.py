#!/usr/bin/env python3
"""Script para crear la tabla mensajes en la base de datos."""

import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.utils.db_init import create_mensajes_table

def main():
    """Create mensajes table."""
    print("=" * 60)
    print("CREACIÓN DE TABLA MENSAJES")
    print("=" * 60)

    # Create Flask app
    app = create_app()

    # Get database URL from config
    database_url = app.config.get('SQLALCHEMY_DATABASE_URI')

    if not database_url:
        print("❌ Error: No se encontró la configuración de base de datos")
        return False

    print(f"\nBase de datos: {database_url.split('@')[-1] if '@' in database_url else database_url}")
    print("\nCreando tabla 'mensajes'...")

    # Create table
    success = create_mensajes_table(database_url)

    if success:
        print("\n" + "=" * 60)
        print("✅ TABLA CREADA EXITOSAMENTE")
        print("=" * 60)
        print("\nLa tabla 'mensajes' está lista para usar.")
        print("Ahora puedes acceder a /admin/mensajes en la aplicación.")
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ ERROR AL CREAR LA TABLA")
        print("=" * 60)
        print("\nPor favor revisa los mensajes de error arriba.")
        print("Si la tabla ya existe, puedes ignorar este error.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
