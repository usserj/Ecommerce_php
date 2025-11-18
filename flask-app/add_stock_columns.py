#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to add missing stock columns to productos table.
Fixes the database schema mismatch after pulling Ecuador seed data.

Usage:
    python add_stock_columns.py
"""
import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

from app import create_app
from app.extensions import db


def add_stock_columns():
    """Add stock and stock_minimo columns to productos table."""
    print("\n" + "="*60)
    print("AGREGAR COLUMNAS DE STOCK A PRODUCTOS")
    print("="*60 + "\n")

    app = create_app()

    with app.app_context():
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('productos')]

            print(f"Columnas actuales en tabla 'productos': {len(columns)}")

            needs_stock = 'stock' not in columns
            needs_stock_minimo = 'stock_minimo' not in columns

            if not needs_stock and not needs_stock_minimo:
                print("\n[OK] Las columnas 'stock' y 'stock_minimo' ya existen.")
                print("No se necesita ninguna migracion.\n")
                return True

            # Add missing columns
            if needs_stock:
                print("\n[*] Agregando columna 'stock'...")
                db.session.execute(db.text(
                    "ALTER TABLE productos ADD COLUMN stock INTEGER DEFAULT 0 COMMENT 'Stock disponible'"
                ))
                print("[OK] Columna 'stock' agregada exitosamente.")

            if needs_stock_minimo:
                print("\n[*] Agregando columna 'stock_minimo'...")
                db.session.execute(db.text(
                    "ALTER TABLE productos ADD COLUMN stock_minimo INTEGER DEFAULT 5 COMMENT 'Alerta de stock bajo'"
                ))
                print("[OK] Columna 'stock_minimo' agregada exitosamente.")

            db.session.commit()

            # Verify columns were added
            inspector = db.inspect(db.engine)
            new_columns = [col['name'] for col in inspector.get_columns('productos')]

            print("\n" + "="*60)
            print("[OK] MIGRACION COMPLETADA EXITOSAMENTE")
            print("="*60)
            print(f"\nColumnas en tabla 'productos': {len(new_columns)}")

            if 'stock' in new_columns and 'stock_minimo' in new_columns:
                print("\n[OK] Columnas 'stock' y 'stock_minimo' verificadas en la base de datos.")

            print("\nAhora puedes ejecutar la aplicacion sin errores:")
            print("  python run.py")
            print("="*60 + "\n")

            return True

        except Exception as e:
            print(f"\n[ERROR] Error durante la migracion: {e}")
            db.session.rollback()
            return False


if __name__ == '__main__':
    try:
        success = add_stock_columns()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[!] Operacion cancelada por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
