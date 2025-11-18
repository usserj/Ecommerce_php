#!/usr/bin/env python3
"""
Script de migración de datos desde PHP a Flask
Migra todos los datos de la base de datos MySQL original a la nueva aplicación Flask
"""

import os
import sys
import shutil
import json
from datetime import datetime
from pathlib import Path
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app, db
from app.models.user import Usuario
from app.models.admin import Administrador
from app.models.product import Producto
from app.models.categoria import Categoria, Subcategoria
from app.models.order import Compra
from app.models.comment import Comentario
from app.models.wishlist import Deseo
from app.models.comercio import Comercio
from app.models.setting import Plantilla, Slide, Banner, Cabecera
from app.models.notification import Notificacion
from app.models.visit import VisitaPais, VisitaPersona


class DataMigration:
    """
    Clase principal para migración de datos
    """

    def __init__(self, source_db_config, target_db_url, source_files_dir, target_files_dir):
        """
        Inicializa la migración

        Args:
            source_db_config: Dict con configuración de BD origen (host, user, password, database)
            target_db_url: URL de BD destino (SQLAlchemy)
            source_files_dir: Directorio de archivos origen (PHP)
            target_files_dir: Directorio de archivos destino (Flask)
        """
        self.source_db_config = source_db_config
        self.target_db_url = target_db_url
        self.source_files_dir = Path(source_files_dir)
        self.target_files_dir = Path(target_files_dir)

        # Connection to source database
        self.source_conn = None
        self.source_cursor = None

        # Flask app and session
        self.app = None
        self.session = None

        # Migration statistics
        self.stats = {
            'usuarios': 0,
            'administradores': 0,
            'categorias': 0,
            'subcategorias': 0,
            'productos': 0,
            'compras': 0,
            'comentarios': 0,
            'deseos': 0,
            'comercio': 0,
            'plantillas': 0,
            'slides': 0,
            'banners': 0,
            'cabeceras': 0,
            'notificaciones': 0,
            'visitaspaises': 0,
            'visitaspersonas': 0,
            'archivos_copiados': 0,
            'errores': []
        }

    def connect_source(self):
        """Conecta a la base de datos origen (MySQL PHP)"""
        print("🔌 Conectando a base de datos origen...")
        try:
            self.source_conn = pymysql.connect(
                host=self.source_db_config['host'],
                user=self.source_db_config['user'],
                password=self.source_db_config['password'],
                database=self.source_db_config['database'],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            self.source_cursor = self.source_conn.cursor()
            print("✅ Conectado a base de datos origen")
        except Exception as e:
            print(f"❌ Error al conectar a BD origen: {e}")
            sys.exit(1)

    def connect_target(self):
        """Conecta a la base de datos destino (Flask)"""
        print("🔌 Conectando a base de datos destino...")
        try:
            self.app = create_app('development')
            with self.app.app_context():
                # Create all tables
                db.create_all()
                self.session = db.session
                print("✅ Conectado a base de datos destino")
        except Exception as e:
            print(f"❌ Error al conectar a BD destino: {e}")
            sys.exit(1)

    def migrate_usuarios(self):
        """Migra usuarios preservando contraseñas legacy"""
        print("\n👥 Migrando usuarios...")

        self.source_cursor.execute("SELECT * FROM usuarios ORDER BY id")
        usuarios = self.source_cursor.fetchall()

        for user_data in usuarios:
            try:
                # Create user with legacy password
                usuario = Usuario(
                    id=user_data['id'],
                    nombre=user_data['nombre'],
                    email=user_data['email'],
                    password=user_data['password'],  # Keep legacy hash
                    foto=user_data.get('foto'),
                    fecha_registro=user_data.get('fecha_registro'),
                    google_id=user_data.get('google_id'),
                    facebook_id=user_data.get('facebook_id'),
                    verificado=bool(user_data.get('verificado', 0)),
                    activo=bool(user_data.get('activo', 1))
                )

                self.session.add(usuario)
                self.stats['usuarios'] += 1

            except Exception as e:
                error_msg = f"Error migrando usuario {user_data.get('id')}: {e}"
                print(f"  ⚠️  {error_msg}")
                self.stats['errores'].append(error_msg)

        self.session.commit()
        print(f"  ✅ {self.stats['usuarios']} usuarios migrados")

    def migrate_administradores(self):
        """Migra administradores"""
        print("\n👨‍💼 Migrando administradores...")

        self.source_cursor.execute("SELECT * FROM administradores ORDER BY id")
        admins = self.source_cursor.fetchall()

        for admin_data in admins:
            try:
                admin = Administrador(
                    id=admin_data['id'],
                    nombre=admin_data['nombre'],
                    email=admin_data['email'],
                    password=admin_data['password'],  # Keep legacy hash
                    rol=admin_data.get('rol', 'admin'),
                    fecha_registro=admin_data.get('fecha_registro'),
                    activo=bool(admin_data.get('activo', 1))
                )

                self.session.add(admin)
                self.stats['administradores'] += 1

            except Exception as e:
                error_msg = f"Error migrando admin {admin_data.get('id')}: {e}"
                print(f"  ⚠️  {error_msg}")
                self.stats['errores'].append(error_msg)

        self.session.commit()
        print(f"  ✅ {self.stats['administradores']} administradores migrados")

    def migrate_categorias(self):
        """Migra categorías y subcategorías"""
        print("\n📁 Migrando categorías...")

        # Migrate categories
        self.source_cursor.execute("SELECT * FROM categorias ORDER BY id")
        categorias = self.source_cursor.fetchall()

        for cat_data in categorias:
            try:
                categoria = Categoria(
                    id=cat_data['id'],
                    nombre=cat_data['nombre'],
                    descripcion=cat_data.get('descripcion'),
                    imagen=cat_data.get('imagen'),
                    estado=bool(cat_data.get('estado', 1)),
                    fecha_creacion=cat_data.get('fecha_creacion')
                )

                self.session.add(categoria)
                self.stats['categorias'] += 1

            except Exception as e:
                error_msg = f"Error migrando categoría {cat_data.get('id')}: {e}"
                print(f"  ⚠️  {error_msg}")
                self.stats['errores'].append(error_msg)

        self.session.commit()
        print(f"  ✅ {self.stats['categorias']} categorías migradas")

        # Migrate subcategories
        print("\n📂 Migrando subcategorías...")
        self.source_cursor.execute("SELECT * FROM subcategorias ORDER BY id")
        subcategorias = self.source_cursor.fetchall()

        for subcat_data in subcategorias:
            try:
                subcategoria = Subcategoria(
                    id=subcat_data['id'],
                    nombre=subcat_data['nombre'],
                    descripcion=subcat_data.get('descripcion'),
                    categoria_id=subcat_data['categoria_id'],
                    estado=bool(subcat_data.get('estado', 1)),
                    fecha_creacion=subcat_data.get('fecha_creacion')
                )

                self.session.add(subcategoria)
                self.stats['subcategorias'] += 1

            except Exception as e:
                error_msg = f"Error migrando subcategoría {subcat_data.get('id')}: {e}"
                print(f"  ⚠️  {error_msg}")
                self.stats['errores'].append(error_msg)

        self.session.commit()
        print(f"  ✅ {self.stats['subcategorias']} subcategorías migradas")

    def migrate_productos(self):
        """Migra productos"""
        print("\n📦 Migrando productos...")

        self.source_cursor.execute("SELECT * FROM productos ORDER BY id")
        productos = self.source_cursor.fetchall()

        for prod_data in productos:
            try:
                # Parse JSON fields if they exist
                multimedia = prod_data.get('multimedia')
                if multimedia and isinstance(multimedia, str):
                    try:
                        multimedia = json.loads(multimedia)
                    except:
                        multimedia = None

                detalles = prod_data.get('detalles')
                if detalles and isinstance(detalles, str):
                    try:
                        detalles = json.loads(detalles)
                    except:
                        detalles = None

                producto = Producto(
                    id=prod_data['id'],
                    titulo=prod_data['titulo'],
                    descripcion=prod_data.get('descripcion'),
                    imagen=prod_data.get('imagen'),
                    multimedia=multimedia,
                    precio=float(prod_data.get('precio', 0)),
                    precio_oferta=float(prod_data.get('precio_oferta', 0)) if prod_data.get('precio_oferta') else None,
                    stock=int(prod_data.get('stock', 0)),
                    categoria_id=prod_data.get('categoria_id'),
                    subcategoria_id=prod_data.get('subcategoria_id'),
                    detalles=detalles,
                    ventas=int(prod_data.get('ventas', 0)),
                    vistas=int(prod_data.get('vistas', 0)),
                    estado=bool(prod_data.get('estado', 1)),
                    destacado=bool(prod_data.get('destacado', 0)),
                    fecha_creacion=prod_data.get('fecha_creacion'),
                    fecha_actualizacion=prod_data.get('fecha_actualizacion')
                )

                self.session.add(producto)
                self.stats['productos'] += 1

            except Exception as e:
                error_msg = f"Error migrando producto {prod_data.get('id')}: {e}"
                print(f"  ⚠️  {error_msg}")
                self.stats['errores'].append(error_msg)

        self.session.commit()
        print(f"  ✅ {self.stats['productos']} productos migrados")

    def migrate_compras(self):
        """Migra órdenes de compra"""
        print("\n🛒 Migrando compras...")

        self.source_cursor.execute("SELECT * FROM compras ORDER BY id")
        compras = self.source_cursor.fetchall()

        for compra_data in compras:
            try:
                # Parse detalles_envio if JSON
                detalles_envio = compra_data.get('detalles_envio')
                if detalles_envio and isinstance(detalles_envio, str):
                    try:
                        detalles_envio = json.loads(detalles_envio)
                    except:
                        detalles_envio = None

                compra = Compra(
                    id=compra_data['id'],
                    usuario_id=compra_data['usuario_id'],
                    producto_id=compra_data['producto_id'],
                    cantidad=int(compra_data.get('cantidad', 1)),
                    precio_unitario=float(compra_data.get('precio_unitario', 0)),
                    total=float(compra_data.get('total', 0)),
                    metodo_pago=compra_data.get('metodo_pago'),
                    estado=compra_data.get('estado', 'pendiente'),
                    detalles_envio=detalles_envio,
                    transaccion_id=compra_data.get('transaccion_id'),
                    fecha_compra=compra_data.get('fecha_compra'),
                    fecha_actualizacion=compra_data.get('fecha_actualizacion')
                )

                self.session.add(compra)
                self.stats['compras'] += 1

            except Exception as e:
                error_msg = f"Error migrando compra {compra_data.get('id')}: {e}"
                print(f"  ⚠️  {error_msg}")
                self.stats['errores'].append(error_msg)

        self.session.commit()
        print(f"  ✅ {self.stats['compras']} compras migradas")

    def migrate_comentarios(self):
        """Migra comentarios y calificaciones"""
        print("\n💬 Migrando comentarios...")

        self.source_cursor.execute("SELECT * FROM comentarios ORDER BY id")
        comentarios = self.source_cursor.fetchall()

        for com_data in comentarios:
            try:
                comentario = Comentario(
                    id=com_data['id'],
                    usuario_id=com_data['usuario_id'],
                    producto_id=com_data['producto_id'],
                    comentario=com_data['comentario'],
                    calificacion=int(com_data.get('calificacion', 5)),
                    estado=bool(com_data.get('estado', 1)),
                    fecha=com_data.get('fecha')
                )

                self.session.add(comentario)
                self.stats['comentarios'] += 1

            except Exception as e:
                error_msg = f"Error migrando comentario {com_data.get('id')}: {e}"
                print(f"  ⚠️  {error_msg}")
                self.stats['errores'].append(error_msg)

        self.session.commit()
        print(f"  ✅ {self.stats['comentarios']} comentarios migrados")

    def migrate_deseos(self):
        """Migra wishlist"""
        print("\n❤️  Migrando wishlist...")

        self.source_cursor.execute("SELECT * FROM deseos ORDER BY id")
        deseos = self.source_cursor.fetchall()

        for deseo_data in deseos:
            try:
                deseo = Deseo(
                    id=deseo_data['id'],
                    usuario_id=deseo_data['usuario_id'],
                    producto_id=deseo_data['producto_id'],
                    fecha_agregado=deseo_data.get('fecha_agregado')
                )

                self.session.add(deseo)
                self.stats['deseos'] += 1

            except Exception as e:
                error_msg = f"Error migrando deseo {deseo_data.get('id')}: {e}"
                print(f"  ⚠️  {error_msg}")
                self.stats['errores'].append(error_msg)

        self.session.commit()
        print(f"  ✅ {self.stats['deseos']} items de wishlist migrados")

    def migrate_comercio(self):
        """Migra configuración de comercio"""
        print("\n💰 Migrando configuración de comercio...")

        self.source_cursor.execute("SELECT * FROM comercio LIMIT 1")
        comercio_data = self.source_cursor.fetchone()

        if comercio_data:
            try:
                comercio = Comercio(
                    id=comercio_data['id'],
                    nombre=comercio_data.get('nombre'),
                    email=comercio_data.get('email'),
                    telefono=comercio_data.get('telefono'),
                    direccion=comercio_data.get('direccion'),
                    moneda=comercio_data.get('moneda', 'USD'),
                    impuesto=float(comercio_data.get('impuesto', 0)),
                    costo_envio=float(comercio_data.get('costo_envio', 0)),
                    paypal_client_id=comercio_data.get('paypal_client_id'),
                    paypal_secret=comercio_data.get('paypal_secret'),
                    paypal_mode=comercio_data.get('paypal_mode', 'sandbox'),
                    payu_merchant_id=comercio_data.get('payu_merchant_id'),
                    payu_api_key=comercio_data.get('payu_api_key'),
                    payu_account_id=comercio_data.get('payu_account_id')
                )

                self.session.add(comercio)
                self.stats['comercio'] += 1

            except Exception as e:
                error_msg = f"Error migrando comercio: {e}"
                print(f"  ⚠️  {error_msg}")
                self.stats['errores'].append(error_msg)

        self.session.commit()
        print(f"  ✅ Configuración de comercio migrada")

    def migrate_plantilla(self):
        """Migra configuración de plantilla"""
        print("\n🎨 Migrando configuración de plantilla...")

        self.source_cursor.execute("SELECT * FROM plantilla LIMIT 1")
        plantilla_data = self.source_cursor.fetchone()

        if plantilla_data:
            try:
                plantilla = Plantilla(
                    id=plantilla_data['id'],
                    titulo=plantilla_data.get('titulo'),
                    logo=plantilla_data.get('logo'),
                    favicon=plantilla_data.get('favicon'),
                    color_primario=plantilla_data.get('color_primario'),
                    color_secundario=plantilla_data.get('color_secundario'),
                    facebook=plantilla_data.get('facebook'),
                    instagram=plantilla_data.get('instagram'),
                    twitter=plantilla_data.get('twitter'),
                    youtube=plantilla_data.get('youtube'),
                    whatsapp=plantilla_data.get('whatsapp')
                )

                self.session.add(plantilla)
                self.stats['plantillas'] += 1

            except Exception as e:
                error_msg = f"Error migrando plantilla: {e}"
                print(f"  ⚠️  {error_msg}")
                self.stats['errores'].append(error_msg)

        self.session.commit()
        print(f"  ✅ Configuración de plantilla migrada")

    def migrate_slides(self):
        """Migra slides del carousel"""
        print("\n🖼️  Migrando slides...")

        self.source_cursor.execute("SELECT * FROM slide ORDER BY orden")
        slides = self.source_cursor.fetchall()

        for slide_data in slides:
            try:
                slide = Slide(
                    id=slide_data['id'],
                    titulo=slide_data.get('titulo'),
                    descripcion=slide_data.get('descripcion'),
                    imagen=slide_data.get('imagen'),
                    enlace=slide_data.get('enlace'),
                    orden=int(slide_data.get('orden', 0)),
                    estado=bool(slide_data.get('estado', 1))
                )

                self.session.add(slide)
                self.stats['slides'] += 1

            except Exception as e:
                error_msg = f"Error migrando slide {slide_data.get('id')}: {e}"
                print(f"  ⚠️  {error_msg}")
                self.stats['errores'].append(error_msg)

        self.session.commit()
        print(f"  ✅ {self.stats['slides']} slides migrados")

    def migrate_banners(self):
        """Migra banners"""
        print("\n🎯 Migrando banners...")

        self.source_cursor.execute("SELECT * FROM banner ORDER BY id")
        banners = self.source_cursor.fetchall()

        for banner_data in banners:
            try:
                banner = Banner(
                    id=banner_data['id'],
                    titulo=banner_data.get('titulo'),
                    imagen=banner_data.get('imagen'),
                    enlace=banner_data.get('enlace'),
                    posicion=banner_data.get('posicion'),
                    estado=bool(banner_data.get('estado', 1))
                )

                self.session.add(banner)
                self.stats['banners'] += 1

            except Exception as e:
                error_msg = f"Error migrando banner {banner_data.get('id')}: {e}"
                print(f"  ⚠️  {error_msg}")
                self.stats['errores'].append(error_msg)

        self.session.commit()
        print(f"  ✅ {self.stats['banners']} banners migrados")

    def migrate_cabeceras(self):
        """Migra metadatos SEO"""
        print("\n🔍 Migrando cabeceras SEO...")

        self.source_cursor.execute("SELECT * FROM cabeceras LIMIT 1")
        cabecera_data = self.source_cursor.fetchone()

        if cabecera_data:
            try:
                cabecera = Cabecera(
                    id=cabecera_data['id'],
                    titulo=cabecera_data.get('titulo'),
                    descripcion=cabecera_data.get('descripcion'),
                    palabras_clave=cabecera_data.get('palabras_clave'),
                    autor=cabecera_data.get('autor'),
                    imagen_og=cabecera_data.get('imagen_og')
                )

                self.session.add(cabecera)
                self.stats['cabeceras'] += 1

            except Exception as e:
                error_msg = f"Error migrando cabecera: {e}"
                print(f"  ⚠️  {error_msg}")
                self.stats['errores'].append(error_msg)

        self.session.commit()
        print(f"  ✅ Cabecera SEO migrada")

    def migrate_notificaciones(self):
        """Migra notificaciones/contadores"""
        print("\n🔔 Migrando notificaciones...")

        self.source_cursor.execute("SELECT * FROM notificaciones LIMIT 1")
        notif_data = self.source_cursor.fetchone()

        if notif_data:
            try:
                notificacion = Notificacion(
                    id=notif_data['id'],
                    nuevos_usuarios=int(notif_data.get('nuevos_usuarios', 0)),
                    nuevas_compras=int(notif_data.get('nuevas_compras', 0)),
                    nuevos_comentarios=int(notif_data.get('nuevos_comentarios', 0)),
                    contactos=int(notif_data.get('contactos', 0))
                )

                self.session.add(notificacion)
                self.stats['notificaciones'] += 1

            except Exception as e:
                error_msg = f"Error migrando notificaciones: {e}"
                print(f"  ⚠️  {error_msg}")
                self.stats['errores'].append(error_msg)

        self.session.commit()
        print(f"  ✅ Notificaciones migradas")

    def migrate_visitas(self):
        """Migra analytics de visitas"""
        print("\n📊 Migrando visitas...")

        # Visitas por país
        self.source_cursor.execute("SELECT * FROM visitaspaises ORDER BY id")
        visitas_paises = self.source_cursor.fetchall()

        for visita_data in visitas_paises:
            try:
                visita = VisitaPais(
                    id=visita_data['id'],
                    pais=visita_data['pais'],
                    cantidad=int(visita_data.get('cantidad', 1)),
                    fecha=visita_data.get('fecha')
                )

                self.session.add(visita)
                self.stats['visitaspaises'] += 1

            except Exception as e:
                error_msg = f"Error migrando visita país {visita_data.get('id')}: {e}"
                print(f"  ⚠️  {error_msg}")
                self.stats['errores'].append(error_msg)

        self.session.commit()
        print(f"  ✅ {self.stats['visitaspaises']} visitas por país migradas")

        # Visitas por persona/IP
        self.source_cursor.execute("SELECT * FROM visitaspersonas ORDER BY id")
        visitas_personas = self.source_cursor.fetchall()

        for visita_data in visitas_personas:
            try:
                visita = VisitaPersona(
                    id=visita_data['id'],
                    ip=visita_data['ip'],
                    fecha=visita_data.get('fecha')
                )

                self.session.add(visita)
                self.stats['visitaspersonas'] += 1

            except Exception as e:
                error_msg = f"Error migrando visita persona {visita_data.get('id')}: {e}"
                print(f"  ⚠️  {error_msg}")
                self.stats['errores'].append(error_msg)

        self.session.commit()
        print(f"  ✅ {self.stats['visitaspersonas']} visitas por IP migradas")

    def migrate_files(self):
        """Copia archivos (imágenes, uploads)"""
        print("\n📁 Copiando archivos...")

        if not self.source_files_dir.exists():
            print(f"  ⚠️  Directorio origen no existe: {self.source_files_dir}")
            return

        # Create target directories
        self.target_files_dir.mkdir(parents=True, exist_ok=True)

        # Directories to copy
        directories_to_copy = [
            'uploads/usuarios',
            'uploads/productos',
            'uploads/categorias',
            'uploads/slides',
            'uploads/banners',
            'uploads/logos'
        ]

        for dir_path in directories_to_copy:
            source_dir = self.source_files_dir / dir_path
            target_dir = self.target_files_dir / dir_path

            if source_dir.exists():
                print(f"  📂 Copiando {dir_path}...")
                target_dir.mkdir(parents=True, exist_ok=True)

                try:
                    # Copy all files in directory
                    for file_path in source_dir.rglob('*'):
                        if file_path.is_file():
                            relative_path = file_path.relative_to(source_dir)
                            target_file = target_dir / relative_path
                            target_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(file_path, target_file)
                            self.stats['archivos_copiados'] += 1

                    print(f"    ✅ Directorio copiado")

                except Exception as e:
                    error_msg = f"Error copiando {dir_path}: {e}"
                    print(f"    ⚠️  {error_msg}")
                    self.stats['errores'].append(error_msg)
            else:
                print(f"  ⚠️  Directorio no existe: {source_dir}")

        print(f"  ✅ {self.stats['archivos_copiados']} archivos copiados")

    def verify_migration(self):
        """Verifica la integridad de la migración"""
        print("\n🔍 Verificando integridad de datos...")

        verification = {
            'usuarios': Usuario.query.count(),
            'administradores': Administrador.query.count(),
            'categorias': Categoria.query.count(),
            'subcategorias': Subcategoria.query.count(),
            'productos': Producto.query.count(),
            'compras': Compra.query.count(),
            'comentarios': Comentario.query.count(),
            'deseos': Deseo.query.count(),
        }

        print("\n📊 Resumen de verificación:")
        for table, count in verification.items():
            print(f"  {table}: {count} registros")

        return verification

    def generate_report(self):
        """Genera reporte de migración"""
        print("\n" + "="*60)
        print("📝 REPORTE DE MIGRACIÓN")
        print("="*60)

        print("\n✅ Registros migrados:")
        print(f"  • Usuarios: {self.stats['usuarios']}")
        print(f"  • Administradores: {self.stats['administradores']}")
        print(f"  • Categorías: {self.stats['categorias']}")
        print(f"  • Subcategorías: {self.stats['subcategorias']}")
        print(f"  • Productos: {self.stats['productos']}")
        print(f"  • Compras: {self.stats['compras']}")
        print(f"  • Comentarios: {self.stats['comentarios']}")
        print(f"  • Wishlist: {self.stats['deseos']}")
        print(f"  • Slides: {self.stats['slides']}")
        print(f"  • Banners: {self.stats['banners']}")
        print(f"  • Visitas (país): {self.stats['visitaspaises']}")
        print(f"  • Visitas (IP): {self.stats['visitaspersonas']}")
        print(f"  • Archivos copiados: {self.stats['archivos_copiados']}")

        total_records = sum([
            self.stats['usuarios'],
            self.stats['administradores'],
            self.stats['categorias'],
            self.stats['subcategorias'],
            self.stats['productos'],
            self.stats['compras'],
            self.stats['comentarios'],
            self.stats['deseos'],
            self.stats['slides'],
            self.stats['banners'],
            self.stats['visitaspaises'],
            self.stats['visitaspersonas']
        ])

        print(f"\n📦 Total de registros migrados: {total_records}")

        if self.stats['errores']:
            print(f"\n⚠️  Errores encontrados: {len(self.stats['errores'])}")
            for error in self.stats['errores'][:10]:  # Show first 10 errors
                print(f"  • {error}")
            if len(self.stats['errores']) > 10:
                print(f"  ... y {len(self.stats['errores']) - 10} errores más")
        else:
            print("\n✅ Sin errores")

        print("\n" + "="*60)

        # Save report to file
        report_file = Path('migration_report.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"Reporte de Migración - {datetime.now()}\n")
            f.write("="*60 + "\n\n")
            f.write(f"Usuarios: {self.stats['usuarios']}\n")
            f.write(f"Administradores: {self.stats['administradores']}\n")
            f.write(f"Categorías: {self.stats['categorias']}\n")
            f.write(f"Subcategorías: {self.stats['subcategorias']}\n")
            f.write(f"Productos: {self.stats['productos']}\n")
            f.write(f"Compras: {self.stats['compras']}\n")
            f.write(f"Comentarios: {self.stats['comentarios']}\n")
            f.write(f"Wishlist: {self.stats['deseos']}\n")
            f.write(f"Slides: {self.stats['slides']}\n")
            f.write(f"Banners: {self.stats['banners']}\n")
            f.write(f"Visitas país: {self.stats['visitaspaises']}\n")
            f.write(f"Visitas IP: {self.stats['visitaspersonas']}\n")
            f.write(f"Archivos: {self.stats['archivos_copiados']}\n")
            f.write(f"\nTotal registros: {total_records}\n")
            f.write(f"Errores: {len(self.stats['errores'])}\n\n")

            if self.stats['errores']:
                f.write("\nErrores:\n")
                for error in self.stats['errores']:
                    f.write(f"  • {error}\n")

        print(f"📄 Reporte guardado en: {report_file}")

    def run(self):
        """Ejecuta la migración completa"""
        print("="*60)
        print("🚀 INICIANDO MIGRACIÓN DE DATOS PHP → FLASK")
        print("="*60)

        start_time = datetime.now()

        try:
            # Connect to databases
            self.connect_source()
            self.connect_target()

            with self.app.app_context():
                # Migrate all data
                self.migrate_usuarios()
                self.migrate_administradores()
                self.migrate_categorias()
                self.migrate_productos()
                self.migrate_compras()
                self.migrate_comentarios()
                self.migrate_deseos()
                self.migrate_comercio()
                self.migrate_plantilla()
                self.migrate_slides()
                self.migrate_banners()
                self.migrate_cabeceras()
                self.migrate_notificaciones()
                self.migrate_visitas()

                # Copy files
                self.migrate_files()

                # Verify migration
                self.verify_migration()

            # Generate report
            self.generate_report()

            end_time = datetime.now()
            duration = end_time - start_time

            print(f"\n⏱️  Tiempo total: {duration}")
            print("\n✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")

        except Exception as e:
            print(f"\n❌ ERROR FATAL EN MIGRACIÓN: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        finally:
            # Close connections
            if self.source_cursor:
                self.source_cursor.close()
            if self.source_conn:
                self.source_conn.close()


def main():
    """Función principal"""
    print("\n" + "="*60)
    print("  SCRIPT DE MIGRACIÓN PHP → FLASK")
    print("  E-commerce Data Migration Tool")
    print("="*60 + "\n")

    # Configuration
    print("📋 Configuración de migración:\n")

    # Source database (PHP MySQL)
    source_db_config = {
        'host': input("Host BD origen (default: localhost): ").strip() or 'localhost',
        'user': input("Usuario BD origen (default: root): ").strip() or 'root',
        'password': input("Password BD origen: ").strip(),
        'database': input("Nombre BD origen (default: ecommerce): ").strip() or 'ecommerce'
    }

    # Target database (Flask)
    default_target_url = 'mysql+pymysql://root:@localhost/Ecommerce_Ec'
    target_db_url = input(f"URL BD destino (default: {default_target_url}): ").strip() or default_target_url

    # File directories
    default_source_files = '../'
    source_files_dir = input(f"Directorio archivos origen (default: {default_source_files}): ").strip() or default_source_files

    default_target_files = 'app/static/uploads'
    target_files_dir = input(f"Directorio archivos destino (default: {default_target_files}): ").strip() or default_target_files

    # Confirm
    print("\n" + "="*60)
    print("⚠️  ADVERTENCIA: Esta operación migrará todos los datos")
    print("="*60)
    confirm = input("\n¿Deseas continuar? (si/no): ").strip().lower()

    if confirm not in ['si', 's', 'yes', 'y']:
        print("❌ Migración cancelada")
        sys.exit(0)

    # Run migration
    migration = DataMigration(
        source_db_config=source_db_config,
        target_db_url=target_db_url,
        source_files_dir=source_files_dir,
        target_files_dir=target_files_dir
    )

    migration.run()


if __name__ == '__main__':
    main()
