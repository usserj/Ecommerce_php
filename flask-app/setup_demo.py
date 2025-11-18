#!/usr/bin/env python3
"""
Script completo para configurar la base de datos y poblar con datos demo.

Plataforma de E-commerce Ecuador
================================

Este script:
1. Crea la base de datos si no existe
2. Crea todas las tablas
3. Poblar con datos de demostración variados
4. Crea usuarios demo para pruebas

IMPORTANTE: Ejecutar con: python setup_demo.py
"""
import sys
import os
import random
import pymysql
from datetime import datetime, timedelta
from slugify import slugify

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import (
    User, Administrador, Producto, Categoria, Subcategoria,
    Compra, Comentario, Deseo, Comercio, Plantilla
)


class EcommerceDemoSetup:
    """Setup completo de ecommerce con datos demo."""

    def __init__(self):
        """Inicializar setup."""
        self.app = create_app()

        # Datos de categorías y productos variados para Ecuador
        self.categorias_data = {
            'Electrónica': {
                'subcategorias': ['Celulares', 'Computadoras', 'Audio', 'Accesorios'],
                'productos': [
                    {
                        'titulo': 'Smartphone Galaxy Pro 5G',
                        'titular': 'Última generación con 5G y cámara de 108MP',
                        'descripcion': 'Smartphone de alta gama con pantalla AMOLED 6.7", procesador Snapdragon 8 Gen 2, 12GB RAM, 256GB almacenamiento. Incluye cargador rápido 65W.',
                        'precio': 899.99,
                        'stock': 15,
                        'detalles': {'pantalla': '6.7" AMOLED', 'ram': '12GB', 'almacenamiento': '256GB', 'bateria': '5000mAh'}
                    },
                    {
                        'titulo': 'Laptop HP 15.6" i7 16GB RAM',
                        'titular': 'Potencia y rendimiento para trabajo y estudio',
                        'descripcion': 'Laptop profesional con procesador Intel Core i7 de 11va generación, 16GB RAM DDR4, SSD 512GB, pantalla Full HD, teclado retroiluminado.',
                        'precio': 1299.99,
                        'stock': 8,
                        'oferta': True,
                        'descuento': 15,
                        'detalles': {'procesador': 'Intel i7-1165G7', 'ram': '16GB DDR4', 'almacenamiento': '512GB SSD', 'pantalla': '15.6" Full HD'}
                    },
                    {
                        'titulo': 'Audífonos Bluetooth Premium',
                        'titular': 'Cancelación de ruido activa',
                        'descripcion': 'Audífonos inalámbricos con cancelación activa de ruido, hasta 30 horas de batería, estuche de carga incluido. Audio de alta fidelidad.',
                        'precio': 159.99,
                        'stock': 25,
                        'oferta': True,
                        'descuento': 20,
                        'detalles': {'bateria': '30 horas', 'conexion': 'Bluetooth 5.2', 'anc': 'Sí'}
                    },
                    {
                        'titulo': 'Mouse Gamer RGB 16000 DPI',
                        'titular': 'Precisión profesional para gaming',
                        'descripcion': 'Mouse gaming con sensor óptico de alta precisión, 7 botones programables, iluminación RGB personalizable, cable trenzado.',
                        'precio': 45.99,
                        'stock': 30,
                        'detalles': {'dpi': '16000', 'botones': '7 programables', 'rgb': 'Sí'}
                    },
                ]
            },
            'Hogar y Cocina': {
                'subcategorias': ['Electrodomésticos', 'Muebles', 'Decoración', 'Cocina'],
                'productos': [
                    {
                        'titulo': 'Licuadora Industrial 2000W',
                        'titular': 'Potencia profesional para tu cocina',
                        'descripcion': 'Licuadora de alto rendimiento con motor de 2000W, jarra de vidrio de 2.5L, 10 velocidades, función pulso. Ideal para batidos y smoothies.',
                        'precio': 89.99,
                        'stock': 12,
                        'detalles': {'potencia': '2000W', 'capacidad': '2.5L', 'material': 'Vidrio templado'}
                    },
                    {
                        'titulo': 'Cafetera Espresso Automática',
                        'titular': 'Café de barista en tu casa',
                        'descripcion': 'Cafetera espresso con espumador de leche, presión de 19 bares, depósito de 1.8L, bandeja calienta tazas. Prepara cappuccino y latte.',
                        'precio': 349.99,
                        'stock': 6,
                        'oferta': True,
                        'descuento': 25,
                        'detalles': {'presion': '19 bares', 'capacidad': '1.8L', 'espumador': 'Incluido'}
                    },
                    {
                        'titulo': 'Juego de Sartenes Antiadherentes',
                        'titular': 'Set de 5 piezas profesional',
                        'descripcion': 'Set de sartenes con recubrimiento antiadherente de cerámica, aptas para inducción, libres de PFOA. Incluye 20cm, 24cm y 28cm.',
                        'precio': 79.99,
                        'stock': 18,
                        'detalles': {'piezas': '5', 'material': 'Aluminio con cerámica', 'induccion': 'Sí'}
                    },
                ]
            },
            'Moda y Accesorios': {
                'subcategorias': ['Ropa Hombre', 'Ropa Mujer', 'Calzado', 'Accesorios'],
                'productos': [
                    {
                        'titulo': 'Zapatillas Deportivas Running',
                        'titular': 'Tecnología de amortiguación profesional',
                        'descripcion': 'Zapatillas de running con tecnología Air Cushion, upper transpirable, suela de goma antideslizante. Perfectas para entrenamientos.',
                        'precio': 89.99,
                        'stock': 20,
                        'detalles': {'material': 'Mesh transpirable', 'suela': 'Goma', 'tecnologia': 'Air Cushion'}
                    },
                    {
                        'titulo': 'Mochila Urbana Laptop 17"',
                        'titular': 'Funcional y moderna',
                        'descripcion': 'Mochila con compartimento acolchado para laptop hasta 17", puerto USB de carga, material resistente al agua, múltiples bolsillos.',
                        'precio': 54.99,
                        'stock': 25,
                        'oferta': True,
                        'descuento': 10,
                        'detalles': {'capacidad': '30L', 'laptop': '17"', 'usb': 'Sí', 'impermeable': 'Sí'}
                    },
                    {
                        'titulo': 'Reloj Inteligente Smartwatch',
                        'titular': 'Monitorea tu salud 24/7',
                        'descripcion': 'Smartwatch con monitor de frecuencia cardíaca, oxígeno en sangre, seguimiento de sueño, 50+ modos deportivos, resistente al agua IP68.',
                        'precio': 129.99,
                        'stock': 15,
                        'detalles': {'pantalla': '1.4" AMOLED', 'bateria': '7 días', 'resistencia': 'IP68'}
                    },
                ]
            },
            'Deportes y Fitness': {
                'subcategorias': ['Gimnasio', 'Yoga', 'Ciclismo', 'Outdoor'],
                'productos': [
                    {
                        'titulo': 'Pesas Ajustables 2.5kg - 24kg',
                        'titular': 'Set completo para entrenamiento en casa',
                        'descripcion': 'Juego de mancuernas ajustables con sistema de selección rápida, reemplazan 15 pares de pesas. Incluye base de almacenamiento.',
                        'precio': 299.99,
                        'stock': 10,
                        'detalles': {'peso_max': '24kg por mancuerna', 'niveles': '15', 'material': 'Acero'}
                    },
                    {
                        'titulo': 'Colchoneta Yoga Premium 6mm',
                        'titular': 'Antideslizante y ecológica',
                        'descripcion': 'Mat de yoga de TPE ecológico, grosor 6mm, superficie antideslizante, incluye correa de transporte. Ideal para yoga y pilates.',
                        'precio': 34.99,
                        'stock': 30,
                        'oferta': True,
                        'descuento': 15,
                        'detalles': {'grosor': '6mm', 'material': 'TPE ecológico', 'dimensiones': '183x61cm'}
                    },
                    {
                        'titulo': 'Bicicleta Spinning Profesional',
                        'titular': 'Entrenamiento intenso en casa',
                        'descripcion': 'Bicicleta estática con volante de 22kg, asiento y manubrio ajustables, monitor LCD, soporta hasta 150kg. Transmisión por correa silenciosa.',
                        'precio': 449.99,
                        'stock': 5,
                        'detalles': {'volante': '22kg', 'peso_max': '150kg', 'monitor': 'LCD', 'transmision': 'Correa'}
                    },
                ]
            },
            'Libros y Educación': {
                'subcategorias': ['Desarrollo Personal', 'Negocios', 'Ficción', 'Académicos'],
                'productos': [
                    {
                        'titulo': 'El Poder del Ahora - Eckhart Tolle',
                        'titular': 'Bestseller de desarrollo personal',
                        'descripcion': 'Guía espiritual para alcanzar la paz interior y vivir el momento presente. Edición en español, tapa blanda, 256 páginas.',
                        'precio': 18.99,
                        'stock': 40,
                        'detalles': {'autor': 'Eckhart Tolle', 'paginas': '256', 'idioma': 'Español', 'editorial': 'Gaia'}
                    },
                    {
                        'titulo': 'Hábitos Atómicos - James Clear',
                        'titular': 'Cambios pequeños, resultados extraordinarios',
                        'descripcion': 'Método probado para crear buenos hábitos y romper los malos. Bestseller del New York Times. Incluye guía práctica.',
                        'precio': 21.99,
                        'stock': 35,
                        'oferta': True,
                        'descuento': 10,
                        'detalles': {'autor': 'James Clear', 'paginas': '328', 'idioma': 'Español'}
                    },
                    {
                        'titulo': 'Curso Completo de Programación Python',
                        'titular': 'De principiante a experto',
                        'descripcion': 'Libro completo de programación en Python con ejercicios prácticos, proyectos reales y acceso a recursos online. 500 páginas.',
                        'precio': 45.99,
                        'stock': 20,
                        'detalles': {'nivel': 'Principiante a Avanzado', 'paginas': '500', 'incluye': 'Código online'}
                    },
                ]
            },
            'Belleza y Salud': {
                'subcategorias': ['Cuidado Personal', 'Suplementos', 'Cosméticos', 'Bienestar'],
                'productos': [
                    {
                        'titulo': 'Proteína Whey Isolate 2kg',
                        'titular': '25g de proteína por porción',
                        'descripcion': 'Proteína aislada de suero de leche, bajo en carbohidratos y grasas. Sabor chocolate. Ideal post-entrenamiento. Sin gluten.',
                        'precio': 59.99,
                        'stock': 28,
                        'detalles': {'peso': '2kg', 'proteina': '25g por porción', 'sabor': 'Chocolate', 'porciones': '60'}
                    },
                    {
                        'titulo': 'Set de Cuidado Facial Completo',
                        'titular': 'Rutina profesional para tu piel',
                        'descripcion': 'Kit de 5 productos: limpiador, tónico, serum vitamina C, crema hidratante y protector solar SPF 50. Para todo tipo de piel.',
                        'precio': 89.99,
                        'stock': 15,
                        'oferta': True,
                        'descuento': 20,
                        'detalles': {'piezas': '5 productos', 'spf': '50', 'tipo_piel': 'Todo tipo'}
                    },
                ]
            }
        }

        # Usuarios demo para crear
        self.usuarios_demo = [
            {
                'nombre': 'Carlos Mendoza',
                'email': 'carlos.mendoza@email.com',
                'password': 'demo123',
                'verificado': True
            },
            {
                'nombre': 'María González',
                'email': 'maria.gonzalez@email.com',
                'password': 'demo123',
                'verificado': True
            },
            {
                'nombre': 'Luis Torres',
                'email': 'luis.torres@email.com',
                'password': 'demo123',
                'verificado': True
            },
            {
                'nombre': 'Ana Rodríguez',
                'email': 'ana.rodriguez@email.com',
                'password': 'demo123',
                'verificado': True
            },
            {
                'nombre': 'Pedro Ramírez',
                'email': 'pedro.ramirez@email.com',
                'password': 'demo123',
                'verificado': True
            }
        ]

        # Administradores demo
        self.admins_demo = [
            {
                'nombre': 'Administrador Principal',
                'email': 'admin@ecommerce.ec',
                'password': 'admin123',
                'perfil': 'administrador'
            },
            {
                'nombre': 'Editor de Contenido',
                'email': 'editor@ecommerce.ec',
                'password': 'editor123',
                'perfil': 'editor'
            }
        ]

    def create_database(self):
        """Crear base de datos si no existe."""
        print("\n🗄️  Verificando base de datos...")

        # Extraer configuración de la URL
        db_url = self.app.config['SQLALCHEMY_DATABASE_URI']
        # mysql+pymysql://user:pass@host/dbname
        parts = db_url.split('/')
        db_name = parts[-1].split('?')[0]  # Ecommerce_Ec

        # Conectar sin especificar base de datos
        connection_url = '/'.join(parts[:-1])

        try:
            # Parsear credenciales
            auth_part = connection_url.split('//')[1].split('@')[0]
            if ':' in auth_part:
                user, password = auth_part.split(':')
            else:
                user = auth_part
                password = ''

            host = connection_url.split('@')[1]

            # Conectar a MySQL
            connection = pymysql.connect(
                host=host,
                user=user,
                password=password
            )

            cursor = connection.cursor()

            # Crear base de datos si no existe
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Base de datos '{db_name}' lista")

            cursor.close()
            connection.close()

        except Exception as e:
            print(f"❌ Error creando base de datos: {e}")
            print("\n⚠️  Asegúrate de que MySQL esté corriendo y las credenciales sean correctas.")
            sys.exit(1)

    def create_tables(self):
        """Crear todas las tablas."""
        print("\n📋 Creando tablas...")

        with self.app.app_context():
            db.create_all()
            print("✅ Tablas creadas")

    def clear_data(self):
        """Limpiar datos existentes."""
        print("\n🧹 Limpiando datos existentes...")

        with self.app.app_context():
            # Orden importante por foreign keys
            Deseo.query.delete()
            Comentario.query.delete()
            Compra.query.delete()
            Producto.query.delete()
            Subcategoria.query.delete()
            Categoria.query.delete()
            User.query.delete()
            Administrador.query.delete()
            Plantilla.query.delete()
            Comercio.query.delete()

            db.session.commit()
            print("✅ Datos limpiados")

    def create_admin_users(self):
        """Crear usuarios administradores."""
        print("\n👤 Creando administradores...")

        admins = []
        for admin_data in self.admins_demo:
            admin = Administrador(
                nombre=admin_data['nombre'],
                email=admin_data['email'],
                perfil=admin_data['perfil'],
                estado=1,
                foto=''
            )
            admin.set_password(admin_data['password'])
            db.session.add(admin)
            admins.append(admin)

        db.session.commit()
        print(f"✅ {len(admins)} administradores creados")
        return admins

    def create_regular_users(self):
        """Crear usuarios regulares."""
        print("\n👥 Creando usuarios clientes...")

        usuarios = []
        for user_data in self.usuarios_demo:
            user = User(
                nombre=user_data['nombre'],
                email=user_data['email'],
                modo='directo',
                verificacion=0 if user_data['verificado'] else 1,
                foto=''
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            usuarios.append(user)

        db.session.commit()
        print(f"✅ {len(usuarios)} usuarios creados")
        return usuarios

    def create_categories_and_products(self):
        """Crear categorías, subcategorías y productos."""
        print("\n📦 Creando categorías y productos...")

        productos_creados = []
        cat_count = 0
        subcat_count = 0
        prod_count = 0

        for cat_nombre, cat_data in self.categorias_data.items():
            # Crear categoría
            categoria = Categoria(
                categoria=cat_nombre,
                ruta=slugify(cat_nombre),
                estado=1
            )
            db.session.add(categoria)
            db.session.flush()
            cat_count += 1

            # Crear subcategorías
            subcategorias = []
            for i, subcat_nombre in enumerate(cat_data['subcategorias']):
                subcategoria = Subcategoria(
                    subcategoria=subcat_nombre,
                    ruta=slugify(f"{cat_nombre}-{subcat_nombre}"),
                    id_categoria=categoria.id,
                    estado=1
                )
                db.session.add(subcategoria)
                subcategorias.append(subcategoria)
                subcat_count += 1

            db.session.flush()

            # Crear productos
            for prod_data in cat_data['productos']:
                # Asignar subcategoría aleatoria de esta categoría
                subcategoria = random.choice(subcategorias)

                # Calcular precio de oferta
                precio_oferta = None
                oferta = 0
                descuento_oferta = 0

                if prod_data.get('oferta'):
                    oferta = 1
                    descuento_oferta = prod_data.get('descuento', 0)
                    precio_oferta = round(prod_data['precio'] * (1 - descuento_oferta / 100), 2)

                producto = Producto(
                    titulo=prod_data['titulo'],
                    titular=prod_data['titular'],
                    descripcion=prod_data['descripcion'],
                    precio=prod_data['precio'],
                    oferta=oferta,
                    precioOferta=precio_oferta or 0,
                    descuentoOferta=descuento_oferta,
                    portada='placeholder.jpg',
                    multimedia=[],
                    detalles=prod_data.get('detalles', {}),
                    vistas=random.randint(50, 500),
                    ventas=random.randint(5, 100),
                    stock=prod_data.get('stock', 10),
                    stock_minimo=5,
                    estado=1,
                    id_categoria=categoria.id,
                    id_subcategoria=subcategoria.id,
                    ruta=slugify(prod_data['titulo']),
                    fecha=datetime.utcnow() - timedelta(days=random.randint(1, 90))
                )
                db.session.add(producto)
                productos_creados.append(producto)
                prod_count += 1

        db.session.commit()
        print(f"✅ {cat_count} categorías, {subcat_count} subcategorías, {prod_count} productos creados")
        return productos_creados

    def create_store_settings(self):
        """Crear configuración de la tienda."""
        print("\n⚙️  Configurando tienda...")

        # Configuración de comercio
        comercio = Comercio(
            impuesto=15.0,  # IVA Ecuador 15%
            envioNacional=5.99,
            envioInternacional=25.99,
            tasaMinimaNal=40.0,  # Envío gratis > $40
            tasaMinimaInt=100.0,
            pais='Ecuador',
            modoPaypal='sandbox',
            modoPayu='test'
        )
        db.session.add(comercio)

        # Plantilla/diseño
        redes_sociales = {
            'facebook': 'https://facebook.com/ecommerce.ec',
            'instagram': 'https://instagram.com/ecommerce.ec',
            'twitter': 'https://twitter.com/ecommerce_ec',
            'youtube': ''
        }

        plantilla = Plantilla(
            barraSuperior='¡Envío GRATIS en compras superiores a $40 en Ecuador!',
            textoSuperior='Bienvenido a E-commerce Ecuador - Tu tienda online de confianza',
            colorFondo='#ffffff',
            colorTexto='#333333',
            redesSociales=redes_sociales
        )
        db.session.add(plantilla)

        db.session.commit()
        print("✅ Configuración de tienda creada")

    def create_sample_orders(self, usuarios, productos):
        """Crear pedidos de ejemplo."""
        print("\n🛍️  Creando pedidos de ejemplo...")

        compras = []
        estados = ['pendiente', 'procesando', 'enviado', 'entregado', 'cancelado']

        # Crear 10-15 pedidos
        for _ in range(random.randint(10, 15)):
            usuario = random.choice(usuarios)
            producto = random.choice(productos)
            cantidad = random.randint(1, 3)

            # Usar precio de oferta si existe
            precio_unitario = producto.precioOferta if producto.precioOferta else producto.precio
            subtotal = precio_unitario * cantidad

            compra = Compra(
                id_usuario=usuario.id,
                id_producto=producto.id,
                cantidad=cantidad,
                precio=precio_unitario,
                subtotal=subtotal,
                estado=random.choice(estados),
                metodoPago=random.choice(['paypal', 'payu', 'transferencia']),
                direccionEnvio=f"Av. Principal #{random.randint(100, 999)}, Quito, Ecuador",
                fecha=datetime.utcnow() - timedelta(days=random.randint(1, 60))
            )
            db.session.add(compra)
            compras.append(compra)

        db.session.commit()
        print(f"✅ {len(compras)} pedidos creados")
        return compras

    def create_reviews(self, usuarios, productos):
        """Crear reseñas de productos."""
        print("\n⭐ Creando reseñas...")

        comentarios = []
        textos_review = [
            "Excelente producto, llegó en perfectas condiciones. Muy recomendado!",
            "Buena calidad por el precio. Estoy satisfecho con mi compra.",
            "Superó mis expectativas. El envío fue rápido y el producto es tal como se describe.",
            "Muy buen producto, aunque el envío tardó un poco más de lo esperado.",
            "Calidad premium, definitivamente volvería a comprar.",
            "Producto original y bien empacado. Servicio al cliente excelente.",
            "Relación calidad-precio inmejorable. Lo recomiendo 100%.",
            "Llegó antes de lo esperado. Muy contento con la compra.",
        ]

        # 30-40 reseñas distribuidas
        for _ in range(random.randint(30, 40)):
            usuario = random.choice(usuarios)
            producto = random.choice(productos)

            # Verificar que no haya review duplicado
            existe = any(c.id_usuario == usuario.id and c.id_producto == producto.id for c in comentarios)
            if existe:
                continue

            calificacion = random.choices([3.0, 4.0, 4.5, 5.0], weights=[5, 15, 30, 50])[0]

            comentario = Comentario(
                id_usuario=usuario.id,
                id_producto=producto.id,
                calificacion=calificacion,
                comentario=random.choice(textos_review),
                fecha=datetime.utcnow() - timedelta(days=random.randint(1, 45))
            )
            db.session.add(comentario)
            comentarios.append(comentario)

        db.session.commit()
        print(f"✅ {len(comentarios)} reseñas creadas")
        return comentarios

    def create_wishlists(self, usuarios, productos):
        """Crear listas de deseos."""
        print("\n❤️  Creando listas de deseos...")

        deseos = []

        for usuario in usuarios:
            # 3-8 productos por usuario
            num_productos = random.randint(3, 8)
            productos_seleccionados = random.sample(productos, min(num_productos, len(productos)))

            for producto in productos_seleccionados:
                deseo = Deseo(
                    id_usuario=usuario.id,
                    id_producto=producto.id,
                    fecha=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )
                db.session.add(deseo)
                deseos.append(deseo)

        db.session.commit()
        print(f"✅ {len(deseos)} items agregados a listas de deseos")
        return deseos

    def print_credentials(self):
        """Mostrar credenciales de acceso."""
        print("\n" + "=" * 70)
        print("✅ SETUP COMPLETADO EXITOSAMENTE")
        print("=" * 70)

        print("\n📋 CREDENCIALES DE ACCESO:\n")

        print("┌" + "─" * 68 + "┐")
        print("│ " + "ADMINISTRADORES".center(66) + " │")
        print("├" + "─" * 68 + "┤")
        for admin in self.admins_demo:
            print(f"│ Email:    {admin['email']:<55} │")
            print(f"│ Password: {admin['password']:<55} │")
            print(f"│ Perfil:   {admin['perfil']:<55} │")
            print("├" + "─" * 68 + "┤")
        print("│ URL:      http://localhost:5000/admin/login" + " " * 24 + "│")
        print("└" + "─" * 68 + "┘")

        print("\n┌" + "─" * 68 + "┐")
        print("│ " + "USUARIOS CLIENTES (DEMO)".center(66) + " │")
        print("├" + "─" * 68 + "┤")
        for user in self.usuarios_demo[:3]:  # Mostrar solo los primeros 3
            print(f"│ {user['nombre']:<30} {user['email']:<37} │")
        print(f"│ Password (todos): demo123" + " " * 42 + "│")
        print("├" + "─" * 68 + "┤")
        print("│ URL:      http://localhost:5000/login" + " " * 30 + "│")
        print("└" + "─" * 68 + "┘")

        print("\n💡 INSTRUCCIONES:")
        print("   1. Inicia el servidor: python run.py")
        print("   2. Abre tu navegador en: http://localhost:5000")
        print("   3. Explora la tienda o inicia sesión con las credenciales arriba")
        print()

    def run(self):
        """Ejecutar setup completo."""
        print("=" * 70)
        print("🚀 SETUP DE E-COMMERCE ECUADOR - DATOS DEMO")
        print("=" * 70)

        try:
            # 1. Crear base de datos
            self.create_database()

            # 2. Crear tablas
            self.create_tables()

            with self.app.app_context():
                # 3. Limpiar datos existentes
                self.clear_data()

                # 4. Crear administradores
                admins = self.create_admin_users()

                # 5. Crear usuarios
                usuarios = self.create_regular_users()

                # 6. Crear categorías y productos
                productos = self.create_categories_and_products()

                # 7. Configuración de tienda
                self.create_store_settings()

                # 8. Crear pedidos de ejemplo
                self.create_sample_orders(usuarios, productos)

                # 9. Crear reseñas
                self.create_reviews(usuarios, productos)

                # 10. Crear listas de deseos
                self.create_wishlists(usuarios, productos)

            # 11. Mostrar credenciales
            self.print_credentials()

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    setup = EcommerceDemoSetup()
    setup.run()
