#!/usr/bin/env python3
"""
Script de diagnóstico completo para identificar problemas.
Ejecutar con: python diagnostico.py
"""
import sys
import os
import pymysql

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*70)
print("DIAGNÓSTICO DEL SISTEMA E-COMMERCE")
print("="*70)

# 1. Verificar importaciones
print("\n[1/6] Verificando importaciones de Python...")
try:
    from app import create_app
    from app.extensions import db
    from app.models import Categoria, Subcategoria, Producto, User, Administrador
    print("✅ Todas las importaciones OK")
except Exception as e:
    print(f"❌ ERROR en importaciones: {e}")
    sys.exit(1)

# 2. Verificar conexión a MySQL
print("\n[2/6] Verificando conexión a MySQL...")
try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        charset='utf8mb4'
    )
    print("✅ Conexión a MySQL OK")
    connection.close()
except Exception as e:
    print(f"❌ ERROR conectando a MySQL: {e}")
    print("   Asegúrate de que MySQL esté corriendo")
    sys.exit(1)

# 3. Verificar base de datos Ecommerce_Ec
print("\n[3/6] Verificando base de datos 'Ecommerce_Ec'...")
try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        charset='utf8mb4'
    )
    cursor = connection.cursor()
    cursor.execute("SHOW DATABASES LIKE 'Ecommerce_Ec'")
    result = cursor.fetchone()

    if result:
        print("✅ Base de datos 'Ecommerce_Ec' existe")
    else:
        print("⚠️  Base de datos 'Ecommerce_Ec' NO existe")
        print("   Creando base de datos...")
        cursor.execute("CREATE DATABASE Ecommerce_Ec CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✅ Base de datos 'Ecommerce_Ec' creada")

    cursor.close()
    connection.close()
except Exception as e:
    print(f"❌ ERROR con base de datos: {e}")
    sys.exit(1)

# 4. Verificar tablas
print("\n[4/6] Verificando tablas...")
try:
    app = create_app()

    with app.app_context():
        # Crear tablas si no existen
        db.create_all()

        # Verificar que las tablas existen
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        required_tables = ['categorias', 'subcategorias', 'productos', 'usuarios', 'administradores']

        print(f"   Tablas encontradas: {len(tables)}")
        for table in required_tables:
            if table in tables:
                print(f"   ✅ {table}")
            else:
                print(f"   ❌ {table} NO EXISTE")

except Exception as e:
    print(f"❌ ERROR verificando tablas: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. Verificar datos
print("\n[5/6] Verificando datos en la base de datos...")
try:
    app = create_app()

    with app.app_context():
        cat_count = Categoria.query.count()
        subcat_count = Subcategoria.query.count()
        prod_count = Producto.query.count()
        user_count = User.query.count()
        admin_count = Administrador.query.count()

        print(f"   Categorías:     {cat_count}")
        print(f"   Subcategorías:  {subcat_count}")
        print(f"   Productos:      {prod_count}")
        print(f"   Usuarios:       {user_count}")
        print(f"   Administradores: {admin_count}")

        if cat_count == 0 or prod_count == 0 or admin_count == 0:
            print("\n⚠️  LA BASE DE DATOS ESTÁ VACÍA - NECESITA POBLARSE")

            respuesta = input("\n¿Deseas poblar la base de datos ahora? (s/n): ")
            if respuesta.lower() == 's':
                print("\n[6/6] Poblando base de datos...")
                from setup_demo import EcommerceDemoSetup

                setup = EcommerceDemoSetup()

                # Limpiar datos
                setup.clear_data()

                # Crear datos
                setup.create_admin_users()
                setup.create_regular_users()
                productos = setup.create_categories_and_products()
                setup.create_store_settings()

                usuarios = User.query.all()
                setup.create_sample_orders(usuarios, productos)
                setup.create_reviews(usuarios, productos)
                setup.create_wishlists(usuarios, productos)

                # Verificar de nuevo
                cat_count = Categoria.query.count()
                prod_count = Producto.query.count()
                admin_count = Administrador.query.count()

                print(f"\n✅ DATOS CREADOS:")
                print(f"   Categorías:     {cat_count}")
                print(f"   Productos:      {prod_count}")
                print(f"   Administradores: {admin_count}")

                print("\n" + "="*70)
                print("✅ SISTEMA LISTO PARA USAR")
                print("="*70)
                print("\n📋 CREDENCIALES:")
                print("   Admin: admin@ecommerce.ec / admin123")
                print("   Cliente: carlos.mendoza@email.com / demo123")
                print("\n🚀 Ejecuta: python run.py")
                print("   Luego visita: http://localhost:5000")
                print("="*70)
        else:
            print("\n✅ La base de datos ya tiene datos")

            # Mostrar algunas categorías
            print("\n📂 CATEGORÍAS:")
            categorias = Categoria.query.all()
            for cat in categorias[:5]:
                print(f"   - {cat.categoria}")

            # Mostrar algunos productos
            print("\n📦 PRODUCTOS:")
            productos = Producto.query.limit(5).all()
            for prod in productos:
                print(f"   - {prod.titulo} - ${prod.precio}")

            print("\n✅ SISTEMA LISTO - Ejecuta: python run.py")

except Exception as e:
    print(f"\n❌ ERROR verificando datos: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
