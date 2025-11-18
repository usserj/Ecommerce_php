#!/usr/bin/env python3
"""
Script para crear usuarios de prueba manualmente.

Este script crea:
1. Usuario administrador para acceso al panel de administración
2. Usuario normal para pruebas de compras en la tienda

IMPORTANTE: Ejecutar con: python create_test_users.py
"""
import sys
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.admin import Administrador


def create_test_users():
    """Crea usuarios de prueba en la base de datos."""
    app = create_app('development')

    with app.app_context():
        print("=" * 60)
        print("CREANDO USUARIOS DE PRUEBA")
        print("=" * 60)

        # 1. Crear usuario ADMINISTRADOR
        print("\n[1/2] Creando usuario administrador...")
        admin_email = 'admin@tutienda.ec'
        admin = Administrador.query.filter_by(email=admin_email).first()

        if admin:
            print(f"   ⚠️  El administrador '{admin_email}' ya existe. Actualizando contraseña...")
            admin.set_password('admin123')
            admin.perfil = 'administrador'
            admin.estado = 1
        else:
            admin = Administrador(
                nombre='Administrador',
                email=admin_email,
                foto='',
                perfil='administrador',
                estado=1
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print(f"   ✅ Administrador creado: {admin_email}")

        # 2. Crear usuario NORMAL (Stalin)
        print("\n[2/2] Creando usuario normal 'Stalin'...")
        user_email = 'stalin@cliente.com'
        user = User.query.filter_by(email=user_email).first()

        if user:
            print(f"   ⚠️  El usuario '{user_email}' ya existe. Actualizando contraseña...")
            user.set_password('stalin123')
            user.verificacion = 0  # Verificado
            user.modo = 'directo'
        else:
            user = User(
                nombre='Stalin Pérez',
                email=user_email,
                foto='',
                modo='directo',
                verificacion=0  # 0 = verificado, 1 = pendiente
            )
            user.set_password('stalin123')
            db.session.add(user)
            print(f"   ✅ Usuario creado: {user_email}")

        # Guardar cambios
        try:
            db.session.commit()
            print("\n" + "=" * 60)
            print("✅ USUARIOS CREADOS EXITOSAMENTE")
            print("=" * 60)

            print("\n📋 CREDENCIALES DE ACCESO:\n")
            print("┌─────────────────────────────────────────────────────────┐")
            print("│ USUARIO ADMINISTRADOR (Panel de Administración)        │")
            print("├─────────────────────────────────────────────────────────┤")
            print("│ Email:    admin@tutienda.ec                             │")
            print("│ Password: admin123                                      │")
            print("│ Perfil:   administrador                                 │")
            print("│ URL:      /admin/login                                  │")
            print("└─────────────────────────────────────────────────────────┘")

            print("\n┌─────────────────────────────────────────────────────────┐")
            print("│ USUARIO NORMAL (Cliente de la tienda)                  │")
            print("├─────────────────────────────────────────────────────────┤")
            print("│ Nombre:   Stalin Pérez                                  │")
            print("│ Email:    stalin@cliente.com                            │")
            print("│ Password: stalin123                                     │")
            print("│ Estado:   Verificado                                    │")
            print("│ URL:      /login                                        │")
            print("└─────────────────────────────────────────────────────────┘")

            print("\n💡 INSTRUCCIONES:")
            print("   1. Inicia el servidor: python run.py")
            print("   2. Admin: http://localhost:5000/admin/login")
            print("   3. Cliente: http://localhost:5000/login")
            print()

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR al guardar usuarios: {e}")
            sys.exit(1)


if __name__ == '__main__':
    create_test_users()
