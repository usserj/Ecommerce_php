#!/usr/bin/env python3
"""
Script simple para verificar y poblar la base de datos.
Ejecutar con: python verificar_y_poblar.py
"""
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import Categoria, Subcategoria, Producto, User, Administrador

def verificar_datos():
    """Verificar datos existentes en la BD."""
    app = create_app()

    with app.app_context():
        print("\n" + "="*60)
        print("VERIFICACIÓN DE DATOS EN LA BASE DE DATOS")
        print("="*60)

        try:
            cat_count = Categoria.query.count()
            subcat_count = Subcategoria.query.count()
            prod_count = Producto.query.count()
            user_count = User.query.count()
            admin_count = Administrador.query.count()

            print(f"\n📊 ESTADO ACTUAL:")
            print(f"   Categorías:     {cat_count}")
            print(f"   Subcategorías:  {subcat_count}")
            print(f"   Productos:      {prod_count}")
            print(f"   Usuarios:       {user_count}")
            print(f"   Administradores: {admin_count}")

            if cat_count == 0 or prod_count == 0:
                print("\n⚠️  LA BASE DE DATOS ESTÁ VACÍA")
                print("\nEjecutando seed de datos...")
                poblar_datos()
            else:
                print("\n✅ La base de datos contiene datos")

                # Mostrar algunas categorías
                print("\n📂 CATEGORÍAS:")
                categorias = Categoria.query.all()
                for cat in categorias:
                    print(f"   - {cat.categoria} (ID: {cat.id})")

                # Mostrar algunos productos
                print("\n📦 PRODUCTOS (primeros 5):")
                productos = Producto.query.limit(5).all()
                for prod in productos:
                    print(f"   - {prod.titulo} - ${prod.precio} (Stock: {prod.stock})")

        except Exception as e:
            print(f"\n❌ ERROR al verificar datos: {e}")
            import traceback
            traceback.print_exc()

def poblar_datos():
    """Poblar base de datos con datos demo."""
    try:
        from setup_demo import EcommerceDemoSetup

        setup = EcommerceDemoSetup()

        # Ejecutar seed completo
        setup.run()

    except Exception as e:
        print(f"\n❌ ERROR al poblar datos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    verificar_datos()
