#!/usr/bin/env python
"""
Script para limpiar todos los datos de demostración de la base de datos.

ADVERTENCIA: Este script eliminará TODOS los datos de la base de datos.
Úsalo solo si quieres resetear completamente el sistema.
"""
import os
import sys

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import (
    User, Administrador, Producto, Categoria, Subcategoria,
    Compra, Comentario, Deseo, Comercio, Plantilla, Slide,
    Banner, Cabecera, Notificacion, VisitaPais, VisitaPersona
)


def clear_all_data():
    """Limpiar todos los datos de la base de datos."""
    app = create_app()

    with app.app_context():
        print("=" * 60)
        print("⚠️  ADVERTENCIA: LIMPIEZA DE DATOS")
        print("=" * 60)
        print("\nEste script eliminará TODOS los datos de la base de datos.")
        print("Esta acción NO se puede deshacer.")
        print("\n¿Estás seguro de que quieres continuar?")

        if '--force' not in sys.argv:
            respuesta = input("\nEscribe 'SI' para continuar: ")
            if respuesta.upper() != 'SI':
                print("\n❌ Operación cancelada")
                sys.exit(0)

        print("\n🗑️  Iniciando limpieza de datos...")

        try:
            # Orden importante por las relaciones
            models_to_clear = [
                ('Comentarios', Comentario),
                ('Deseos', Deseo),
                ('Compras', Compra),
                ('Notificaciones', Notificacion),
                ('Productos', Producto),
                ('Subcategorías', Subcategoria),
                ('Categorías', Categoria),
                ('Usuarios', User),
                ('Administradores', Administrador),
                ('Visitas País', VisitaPais),
                ('Visitas Persona', VisitaPersona),
                ('Slides', Slide),
                ('Banners', Banner),
                ('Cabeceras', Cabecera),
                ('Plantillas', Plantilla),
                ('Comercio', Comercio),
            ]

            total_deleted = 0

            for model_name, model_class in models_to_clear:
                count = model_class.query.count()
                if count > 0:
                    model_class.query.delete()
                    print(f"  ✓ {model_name}: {count} registros eliminados")
                    total_deleted += count

            db.session.commit()

            print("\n" + "=" * 60)
            print("✅ LIMPIEZA COMPLETADA")
            print("=" * 60)
            print(f"\nTotal de registros eliminados: {total_deleted}")
            print("\n💡 La base de datos está ahora vacía.")
            print("   Puedes ejecutar 'python seed_demo_data.py' para poblar con datos de demo.")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            sys.exit(1)


if __name__ == '__main__':
    clear_all_data()
