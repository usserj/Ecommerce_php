#!/usr/bin/env python
"""
Script para poblar la base de datos con datos de demostración de una tienda de ropa.

Incluye:
- Categorías y subcategorías de ropa
- Productos con imágenes
- Usuarios y administradores
- Pedidos de ejemplo
- Comentarios y reseñas
- Listas de deseos
"""
import os
import sys
import random
import requests
from datetime import datetime, timedelta
from slugify import slugify

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import (
    User, Administrador, Producto, Categoria, Subcategoria,
    Compra, Comentario, Deseo, Comercio, Plantilla
)


class DemoDataSeeder:
    """Clase para poblar datos de demostración."""

    def __init__(self, download_images=False):
        """Inicializar seeder."""
        self.app = create_app()
        self.download_images = download_images
        self.image_dir = os.path.join('app', 'static', 'uploads', 'demo')

        # Datos de categorías y productos
        self.categorias_data = {
            'Camisetas': {
                'subcategorias': ['Manga Corta', 'Manga Larga', 'Deportivas', 'Básicas'],
                'productos': [
                    {
                        'titulo': 'Camiseta Básica Blanca',
                        'titular': 'Camiseta de algodón 100% perfecta para el día a día',
                        'descripcion': 'Camiseta básica de algodón premium, corte clásico y cómodo. Ideal para combinar con cualquier outfit. Disponible en varios colores.',
                        'precio': 19.99,
                        'detalles': {'material': '100% Algodón', 'cuidado': 'Lavar a máquina', 'origen': 'España'}
                    },
                    {
                        'titulo': 'Camiseta Estampada Vintage',
                        'titular': 'Diseño retro con estampado exclusivo',
                        'descripcion': 'Camiseta con estampado vintage único. Algodón suave y resistente. Perfecta para un look casual.',
                        'precio': 24.99,
                        'detalles': {'material': '95% Algodón, 5% Elastano', 'cuidado': 'Lavar del revés', 'origen': 'Portugal'}
                    },
                    {
                        'titulo': 'Camiseta Deportiva Dry-Fit',
                        'titular': 'Tecnología de secado rápido para deportistas',
                        'descripcion': 'Camiseta técnica con tejido transpirable. Perfecta para running, gym o cualquier actividad deportiva.',
                        'precio': 29.99,
                        'oferta': True,
                        'descuento': 20,
                        'detalles': {'material': '100% Poliéster', 'tecnología': 'Dry-Fit', 'cuidado': 'No usar suavizante'}
                    },
                ]
            },
            'Pantalones': {
                'subcategorias': ['Vaqueros', 'Chinos', 'Deportivos', 'Joggers'],
                'productos': [
                    {
                        'titulo': 'Vaqueros Slim Fit Azul',
                        'titular': 'Corte moderno y favorecedor',
                        'descripcion': 'Vaqueros de corte slim con lavado medio. Perfectos para cualquier ocasión, cómodos y duraderos.',
                        'precio': 49.99,
                        'detalles': {'material': '98% Algodón, 2% Elastano', 'corte': 'Slim Fit', 'lavado': 'Medio'}
                    },
                    {
                        'titulo': 'Pantalón Chino Beige',
                        'titular': 'Elegancia casual para el día a día',
                        'descripcion': 'Pantalón chino de corte regular. Versátil y cómodo, perfecto para looks smart-casual.',
                        'precio': 39.99,
                        'oferta': True,
                        'descuento': 15,
                        'detalles': {'material': '97% Algodón, 3% Elastano', 'corte': 'Regular Fit', 'bolsillos': '5 bolsillos'}
                    },
                    {
                        'titulo': 'Joggers Deportivos Negro',
                        'titular': 'Comodidad máxima para tu día a día',
                        'descripcion': 'Pantalón jogger de tejido suave y elástico. Con cordón ajustable y bolsillos laterales.',
                        'precio': 34.99,
                        'detalles': {'material': '80% Algodón, 20% Poliéster', 'ajuste': 'Cintura elástica', 'bolsillos': '3 bolsillos'}
                    },
                ]
            },
            'Vestidos': {
                'subcategorias': ['Casuales', 'Fiesta', 'Verano', 'Largos'],
                'productos': [
                    {
                        'titulo': 'Vestido Floral Primavera',
                        'titular': 'Estampado floral perfecto para la temporada',
                        'descripcion': 'Vestido midi con estampado floral. Corte femenino y favorecedor. Ideal para ocasiones especiales.',
                        'precio': 59.99,
                        'detalles': {'material': '100% Viscosa', 'largo': 'Midi', 'cierre': 'Cremallera lateral'}
                    },
                    {
                        'titulo': 'Vestido Negro de Fiesta',
                        'titular': 'Elegancia atemporal',
                        'descripcion': 'Vestido de cóctel en color negro. Diseño sofisticado y elegante. Perfecto para eventos formales.',
                        'precio': 79.99,
                        'oferta': True,
                        'descuento': 25,
                        'detalles': {'material': '95% Poliéster, 5% Elastano', 'largo': 'Por la rodilla', 'forro': 'Incluido'}
                    },
                    {
                        'titulo': 'Vestido Veraniego Blanco',
                        'titular': 'Frescura y estilo para el verano',
                        'descripcion': 'Vestido ligero de algodón con bordados. Perfecto para días calurosos.',
                        'precio': 44.99,
                        'detalles': {'material': '100% Algodón', 'largo': 'Corto', 'mangas': 'Sin mangas'}
                    },
                ]
            },
            'Zapatos': {
                'subcategorias': ['Deportivos', 'Casuales', 'Formales', 'Sandalias'],
                'productos': [
                    {
                        'titulo': 'Zapatillas Running Pro',
                        'titular': 'Tecnología de amortiguación avanzada',
                        'descripcion': 'Zapatillas de running con suela de gel y upper transpirable. Máxima comodidad en cada paso.',
                        'precio': 89.99,
                        'detalles': {'material': 'Malla transpirable', 'suela': 'Gel amortiguador', 'uso': 'Running'}
                    },
                    {
                        'titulo': 'Zapatos Oxford Cuero',
                        'titular': 'Elegancia clásica en cuero genuino',
                        'descripcion': 'Zapatos Oxford de cuero de alta calidad. Perfectos para looks formales y de oficina.',
                        'precio': 99.99,
                        'oferta': True,
                        'descuento': 30,
                        'detalles': {'material': 'Cuero genuino', 'suela': 'Cuero', 'cierre': 'Cordones'}
                    },
                    {
                        'titulo': 'Sandalias Verano Confort',
                        'titular': 'Comodidad para días soleados',
                        'descripcion': 'Sandalias ergonómicas con plantilla acolchada. Perfectas para playa y paseos.',
                        'precio': 34.99,
                        'detalles': {'material': 'Sintético', 'suela': 'EVA', 'plantilla': 'Acolchada'}
                    },
                ]
            },
            'Accesorios': {
                'subcategorias': ['Gorras', 'Cinturones', 'Bufandas', 'Mochilas'],
                'productos': [
                    {
                        'titulo': 'Gorra Baseball Ajustable',
                        'titular': 'Estilo urbano con protección solar',
                        'descripcion': 'Gorra de béisbol con visera curvada. Cierre ajustable en la parte trasera.',
                        'precio': 19.99,
                        'detalles': {'material': '100% Algodón', 'visera': 'Curvada', 'ajuste': 'Regulable'}
                    },
                    {
                        'titulo': 'Cinturón Cuero Clásico',
                        'titular': 'Accesorio esencial de cuero genuino',
                        'descripcion': 'Cinturón de cuero de alta calidad con hebilla metálica. Reversible negro/marrón.',
                        'precio': 29.99,
                        'detalles': {'material': 'Cuero genuino', 'hebilla': 'Acero inoxidable', 'ancho': '3.5 cm'}
                    },
                    {
                        'titulo': 'Mochila Urban Laptop 15"',
                        'titular': 'Funcionalidad y estilo urbano',
                        'descripcion': 'Mochila con compartimento acolchado para laptop. Múltiples bolsillos organizadores.',
                        'precio': 49.99,
                        'oferta': True,
                        'descuento': 20,
                        'detalles': {'capacidad': '20L', 'laptop': 'Hasta 15"', 'material': 'Nylon resistente'}
                    },
                ]
            }
        }

        # URLs de imágenes placeholder por categoría
        self.placeholder_images = {
            'Camisetas': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500',
            'Pantalones': 'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=500',
            'Vestidos': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=500',
            'Zapatos': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=500',
            'Accesorios': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500',
        }

    def clear_data(self):
        """Limpiar datos existentes."""
        print("🗑️  Limpiando datos existentes...")

        try:
            # Orden importante por las relaciones
            Comentario.query.delete()
            Deseo.query.delete()
            Compra.query.delete()
            Producto.query.delete()
            Subcategoria.query.delete()
            Categoria.query.delete()
            User.query.delete()
            Administrador.query.delete()

            db.session.commit()
            print("✅ Datos limpiados correctamente")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error limpiando datos: {e}")
            raise

    def create_categories(self):
        """Crear categorías y subcategorías."""
        print("\n📁 Creando categorías y subcategorías...")

        categorias = {}

        for cat_nombre, cat_data in self.categorias_data.items():
            # Crear categoría
            ruta = slugify(cat_nombre)
            categoria = Categoria(
                categoria=cat_nombre,
                ruta=ruta,
                estado=1,
                oferta=0
            )
            db.session.add(categoria)
            db.session.flush()  # Para obtener el ID

            categorias[cat_nombre] = {
                'categoria': categoria,
                'subcategorias': {}
            }

            # Crear subcategorías
            for subcat_nombre in cat_data['subcategorias']:
                ruta_sub = f"{ruta}-{slugify(subcat_nombre)}"
                subcategoria = Subcategoria(
                    subcategoria=subcat_nombre,
                    id_categoria=categoria.id,
                    ruta=ruta_sub,
                    estado=1,
                    oferta=0
                )
                db.session.add(subcategoria)
                db.session.flush()

                categorias[cat_nombre]['subcategorias'][subcat_nombre] = subcategoria

            print(f"  ✓ {cat_nombre} ({len(cat_data['subcategorias'])} subcategorías)")

        db.session.commit()
        print(f"✅ Creadas {len(categorias)} categorías")

        return categorias

    def create_products(self, categorias):
        """Crear productos."""
        print("\n🛍️  Creando productos...")

        productos_creados = []

        for cat_nombre, cat_data in self.categorias_data.items():
            categoria_obj = categorias[cat_nombre]['categoria']
            subcategorias = list(categorias[cat_nombre]['subcategorias'].values())

            for idx, prod_data in enumerate(cat_data['productos']):
                # Seleccionar subcategoría aleatoria
                subcategoria = subcategorias[idx % len(subcategorias)]

                # Calcular precio de oferta si aplica
                precio_oferta = 0
                descuento = 0
                fin_oferta = None

                if prod_data.get('oferta', False):
                    descuento = prod_data.get('descuento', 15)
                    precio_oferta = round(prod_data['precio'] * (1 - descuento/100), 2)
                    fin_oferta = datetime.utcnow() + timedelta(days=30)

                # Generar imágenes
                base_image = self.placeholder_images.get(cat_nombre, 'https://via.placeholder.com/500')
                multimedia = [
                    f"{base_image}&sig={idx}",
                    f"{base_image}&sig={idx+100}",
                    f"{base_image}&sig={idx+200}"
                ]

                # Crear producto
                ruta = slugify(prod_data['titulo'])
                producto = Producto(
                    id_categoria=categoria_obj.id,
                    id_subcategoria=subcategoria.id,
                    tipo='fisico',
                    ruta=f"{ruta}-{random.randint(1000, 9999)}",
                    estado=1,
                    titulo=prod_data['titulo'],
                    titular=prod_data['titular'],
                    descripcion=prod_data['descripcion'],
                    multimedia=multimedia,
                    detalles=prod_data['detalles'],
                    precio=prod_data['precio'],
                    portada=multimedia[0],
                    vistas=random.randint(50, 500),
                    ventas=random.randint(5, 100),
                    oferta=1 if prod_data.get('oferta', False) else 0,
                    precioOferta=precio_oferta,
                    descuentoOferta=descuento,
                    finOferta=fin_oferta,
                    peso=random.uniform(0.2, 2.0),
                    entrega=random.uniform(5.0, 15.0)
                )

                db.session.add(producto)
                productos_creados.append(producto)

            print(f"  ✓ {cat_nombre}: {len(cat_data['productos'])} productos")

        db.session.commit()
        print(f"✅ Creados {len(productos_creados)} productos")

        return productos_creados

    def create_users(self):
        """Crear usuarios de demostración."""
        print("\n👥 Creando usuarios...")

        usuarios = []

        # Usuarios de ejemplo
        usuarios_data = [
            {'nombre': 'María García', 'email': 'maria@demo.com'},
            {'nombre': 'Juan Martínez', 'email': 'juan@demo.com'},
            {'nombre': 'Ana López', 'email': 'ana@demo.com'},
            {'nombre': 'Carlos Rodríguez', 'email': 'carlos@demo.com'},
            {'nombre': 'Laura Fernández', 'email': 'laura@demo.com'},
        ]

        for user_data in usuarios_data:
            user = User(
                nombre=user_data['nombre'],
                email=user_data['email'],
                modo='directo',
                verificacion=0  # Ya verificado
            )
            user.set_password('demo123')  # Contraseña de demo

            db.session.add(user)
            usuarios.append(user)

        db.session.commit()
        print(f"✅ Creados {len(usuarios)} usuarios (password: demo123)")

        return usuarios

    def create_admins(self):
        """Crear administradores."""
        print("\n👨‍💼 Creando administradores...")

        admins = []

        # Administrador principal
        admin = Administrador(
            nombre='Admin Principal',
            email='admin@tienda.com',
            perfil='administrador',
            estado=1
        )
        admin.set_password('admin123')
        db.session.add(admin)
        admins.append(admin)

        # Editor
        editor = Administrador(
            nombre='Editor Tienda',
            email='editor@tienda.com',
            perfil='editor',
            estado=1
        )
        editor.set_password('editor123')
        db.session.add(editor)
        admins.append(editor)

        db.session.commit()
        print(f"✅ Creados {len(admins)} administradores")
        print("   - admin@tienda.com / admin123 (Administrador)")
        print("   - editor@tienda.com / editor123 (Editor)")

        return admins

    def create_orders(self, usuarios, productos):
        """Crear pedidos de ejemplo."""
        print("\n📦 Creando pedidos...")

        pedidos = []
        paises = ['España', 'México', 'Argentina', 'Colombia', 'Chile']
        metodos = ['paypal', 'tarjeta', 'transferencia']

        # Crear varios pedidos por usuario
        for usuario in usuarios[:3]:  # Solo primeros 3 usuarios
            num_pedidos = random.randint(2, 5)

            for _ in range(num_pedidos):
                producto = random.choice(productos)
                cantidad = random.randint(1, 3)

                # Calcular total
                precio_unitario = producto.get_price()
                subtotal = precio_unitario * cantidad
                envio = producto.entrega
                total = subtotal + envio

                # Crear pedido
                pedido = Compra(
                    id_usuario=usuario.id,
                    id_producto=producto.id,
                    envio=int(envio),
                    metodo=random.choice(metodos),
                    email=usuario.email,
                    direccion=f"Calle Demo {random.randint(1, 100)}, Piso {random.randint(1, 5)}",
                    pais=random.choice(paises),
                    cantidad=cantidad,
                    detalle=f"Pedido de {producto.titulo}",
                    pago=str(round(total, 2)),
                    fecha=datetime.utcnow() - timedelta(days=random.randint(1, 90))
                )

                db.session.add(pedido)
                pedidos.append(pedido)

        db.session.commit()
        print(f"✅ Creados {len(pedidos)} pedidos")

        return pedidos

    def create_reviews(self, usuarios, productos):
        """Crear reseñas y comentarios."""
        print("\n⭐ Creando reseñas...")

        comentarios = []

        reviews_texts = [
            "Excelente producto, muy buena calidad. Lo recomiendo 100%.",
            "Perfecto, tal como se describe. Llegó rápido y bien empaquetado.",
            "Muy contento con la compra. La talla es correcta y el material es bueno.",
            "Buena relación calidad-precio. Volveré a comprar.",
            "Me encanta! Justo lo que buscaba. Gracias!",
            "Producto de calidad, aunque tardó un poco en llegar.",
            "Súper cómodo y el diseño es precioso. Muy recomendable.",
            "Bien en general, aunque esperaba un poco más de calidad.",
            "Perfecto para el día a día. Muy satisfecho con la compra.",
            "Excelente servicio y producto de primera. 5 estrellas!"
        ]

        # Crear varias reseñas para productos populares
        for producto in productos[:10]:  # Primeros 10 productos
            num_reviews = random.randint(2, 6)

            for _ in range(num_reviews):
                usuario = random.choice(usuarios)
                calificacion = random.choice([4.0, 4.5, 5.0, 5.0, 5.0])  # Más probabilidad de 5 estrellas

                comentario = Comentario(
                    id_usuario=usuario.id,
                    id_producto=producto.id,
                    calificacion=calificacion,
                    comentario=random.choice(reviews_texts),
                    fecha=datetime.utcnow() - timedelta(days=random.randint(1, 60))
                )

                db.session.add(comentario)
                comentarios.append(comentario)

        db.session.commit()
        print(f"✅ Creadas {len(comentarios)} reseñas")

        return comentarios

    def create_wishlists(self, usuarios, productos):
        """Crear listas de deseos."""
        print("\n❤️  Creando listas de deseos...")

        deseos = []

        for usuario in usuarios:
            # Cada usuario tendrá 3-7 productos en su wishlist
            num_deseos = random.randint(3, 7)
            productos_wishlist = random.sample(productos, min(num_deseos, len(productos)))

            for producto in productos_wishlist:
                deseo = Deseo(
                    id_usuario=usuario.id,
                    id_producto=producto.id,
                    fecha=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )
                db.session.add(deseo)
                deseos.append(deseo)

        db.session.commit()
        print(f"✅ Creadas {len(deseos)} items en listas de deseos")

        return deseos

    def create_store_settings(self):
        """Crear configuración de la tienda."""
        print("\n⚙️  Creando configuración de tienda...")

        # Comercio
        comercio = Comercio(
            impuesto=21.0,  # IVA 21%
            envioNacional=5.99,
            envioInternacional=15.99,
            tasaMinimaNal=50.0,
            tasaMinimaInt=100.0,
            pais='España',
            modoPaypal='sandbox',
            modoPayu='test'
        )
        db.session.add(comercio)

        # Plantilla
        redesSociales = {
            'facebook': 'https://facebook.com/mitienda',
            'instagram': 'https://instagram.com/mitienda',
            'twitter': 'https://twitter.com/mitienda',
            'youtube': 'https://youtube.com/mitienda'
        }

        plantilla = Plantilla(
            barraSuperior='Envío gratis en pedidos superiores a 50€',
            textoSuperior='¡Bienvenido a MiTienda Fashion!',
            colorFondo='#ffffff',
            colorTexto='#000000',
            redesSociales=redesSociales
        )
        db.session.add(plantilla)

        db.session.commit()
        print("✅ Configuración de tienda creada")

    def run(self):
        """Ejecutar seed completo."""
        with self.app.app_context():
            print("=" * 60)
            print("🌱 INICIANDO SEED DE DATOS DE DEMOSTRACIÓN")
            print("=" * 60)

            try:
                # 1. Limpiar datos existentes
                self.clear_data()

                # 2. Crear categorías
                categorias = self.create_categories()

                # 3. Crear productos
                productos = self.create_products(categorias)

                # 4. Crear usuarios
                usuarios = self.create_users()

                # 5. Crear administradores
                admins = self.create_admins()

                # 6. Crear pedidos
                pedidos = self.create_orders(usuarios, productos)

                # 7. Crear reseñas
                comentarios = self.create_reviews(usuarios, productos)

                # 8. Crear listas de deseos
                deseos = self.create_wishlists(usuarios, productos)

                # 9. Configuración de tienda
                self.create_store_settings()

                print("\n" + "=" * 60)
                print("✅ SEED COMPLETADO EXITOSAMENTE")
                print("=" * 60)
                print("\n📊 RESUMEN:")
                print(f"   - Categorías: {len(categorias)}")
                print(f"   - Productos: {len(productos)}")
                print(f"   - Usuarios: {len(usuarios)}")
                print(f"   - Administradores: {len(admins)}")
                print(f"   - Pedidos: {len(pedidos)}")
                print(f"   - Reseñas: {len(comentarios)}")
                print(f"   - Lista de deseos: {len(deseos)}")
                print("\n🔑 CREDENCIALES:")
                print("\n   Usuarios (password: demo123):")
                for user in usuarios[:3]:
                    print(f"   - {user.email}")
                print("\n   Administradores:")
                print("   - admin@tienda.com / admin123 (Administrador)")
                print("   - editor@tienda.com / editor123 (Editor)")
                print("\n🌐 La tienda está lista para usar!")
                print("=" * 60)

            except Exception as e:
                print(f"\n❌ ERROR: {e}")
                import traceback
                traceback.print_exc()
                db.session.rollback()
                sys.exit(1)


if __name__ == '__main__':
    # Parsear argumentos
    download_images = '--download-images' in sys.argv

    if download_images:
        print("📸 Modo: Descarga de imágenes activada")

    seeder = DemoDataSeeder(download_images=download_images)
    seeder.run()
