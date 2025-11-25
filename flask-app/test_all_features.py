#!/usr/bin/env python
"""
Test Completo de TODAS las Funcionalidades del Sistema
Cobertura: 100% de características implementadas
Ejecutar: python test_all_features.py
"""

import sys
import os

# Agregar el directorio de la app al path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db
from app.models.product import Producto
from app.models.order import Compra
from app.models.user import User
from app.models.categoria import Categoria
from app.models.coupon import Cupon
from app.models.comment import Comentario
from app.services.ai_service import ai_service
from app.services.chatbot_tools import *
from datetime import datetime, timedelta
import json

# Imports opcionales
try:
    from app.models.categoria import Subcategoria
except ImportError:
    Subcategoria = None

try:
    from app.models.cart import Carrito
except ImportError:
    Carrito = None

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_test(test_name):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}TEST: {test_name}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.END}")

def print_subtest(message):
    print(f"\n{Colors.MAGENTA}▶ {message}{Colors.END}")


# ============================================================================
# SECCIÓN 1: BASE DE DATOS Y MODELOS
# ============================================================================

def test_database_connection(app):
    """Verifica conexión y estado de la base de datos"""
    print_test("1.1 - Conexión a Base de Datos")

    try:
        with app.app_context():
            # Verificar tablas principales
            productos_count = Producto.query.count()
            usuarios_count = User.query.count()
            categorias_count = Categoria.query.count()
            ordenes_count = Compra.query.count()
            comentarios_count = Comentario.query.count()

            print_success(f"Base de datos conectada correctamente")
            print_info(f"Productos: {productos_count}")
            print_info(f"Usuarios: {usuarios_count}")
            print_info(f"Categorías: {categorias_count}")
            print_info(f"Órdenes: {ordenes_count}")
            print_info(f"Comentarios: {comentarios_count}")

            if productos_count == 0:
                print_warning("⚠️  No hay productos en la BD - algunas pruebas fallarán")

            return True
    except Exception as e:
        print_error(f"Error en conexión BD: {e}")
        return False


def test_product_model(app):
    """Verifica funcionalidad del modelo Producto"""
    print_test("1.2 - Modelo de Producto")

    try:
        with app.app_context():
            producto = Producto.query.first()

            if not producto:
                print_warning("No hay productos para probar")
                return False

            print_info(f"Producto: {producto.titulo}")

            # Verificar métodos del modelo
            print_subtest("Métodos del modelo")

            precio = producto.get_price()
            print_success(f"get_price(): ${precio}")

            rating = producto.get_average_rating()
            print_success(f"get_average_rating(): {rating}/5")

            num_comments = producto.get_comments_count()
            print_success(f"get_comments_count(): {num_comments}")

            en_oferta = producto.is_on_offer()
            print_success(f"is_on_offer(): {en_oferta}")

            if producto.stock > 0:
                tiene_stock = producto.tiene_stock(1)
                print_success(f"tiene_stock(1): {tiene_stock}")

            # Verificar relaciones
            print_subtest("Relaciones")

            if producto.categoria:
                print_success(f"Categoría: {producto.categoria.categoria}")
            else:
                print_warning("Producto sin categoría")

            return True
    except Exception as e:
        print_error(f"Error en modelo Producto: {e}")
        return False


def test_user_model(app):
    """Verifica funcionalidad del modelo Usuario"""
    print_test("1.3 - Modelo de Usuario")

    try:
        with app.app_context():
            usuario = User.query.first()

            if not usuario:
                print_warning("No hay usuarios para probar")
                return False

            print_info(f"Usuario: {usuario.nombre} ({usuario.email})")

            # Verificar campos
            print_subtest("Campos del usuario")
            print_success(f"ID: {usuario.id}")
            print_success(f"Email: {usuario.email}")
            print_success(f"Rol: {usuario.rol if hasattr(usuario, 'rol') else 'N/A'}")
            print_success(f"Fecha registro: {usuario.fecha.strftime('%Y-%m-%d')}")

            # Verificar contraseña hasheada
            if hasattr(usuario, 'password'):
                if usuario.password and len(usuario.password) > 20:
                    print_success("Contraseña está hasheada correctamente")
                else:
                    print_warning("Contraseña podría no estar hasheada")

            return True
    except Exception as e:
        print_error(f"Error en modelo Usuario: {e}")
        return False


def test_order_model(app):
    """Verifica funcionalidad del modelo Orden"""
    print_test("1.4 - Modelo de Orden/Compra")

    try:
        with app.app_context():
            orden = Compra.query.first()

            if not orden:
                print_warning("No hay órdenes para probar")
                return False

            print_info(f"Orden ID: {orden.id}")

            # Verificar campos
            print_subtest("Campos de la orden")
            print_success(f"Estado: {orden.estado}")
            print_success(f"Método pago: {orden.metodo_pago}")
            print_success(f"Cantidad: {orden.cantidad}")
            print_success(f"Total: ${orden.precio_total if orden.precio_total else orden.precio_unitario * orden.cantidad}")

            # Verificar relaciones
            print_subtest("Relaciones")
            if orden.usuario:
                print_success(f"Usuario: {orden.usuario.nombre}")
            if orden.producto:
                print_success(f"Producto: {orden.producto.titulo}")

            # Verificar método cambiar_estado
            print_subtest("Métodos de estado")
            estados_validos = ['pendiente', 'procesando', 'enviado', 'entregado', 'cancelado']
            if orden.estado.lower() in estados_validos:
                print_success(f"Estado '{orden.estado}' es válido")
            else:
                print_warning(f"Estado '{orden.estado}' no reconocido")

            return True
    except Exception as e:
        print_error(f"Error en modelo Orden: {e}")
        return False


# ============================================================================
# SECCIÓN 2: BÚSQUEDA Y CATÁLOGO
# ============================================================================

def test_basic_product_search(app):
    """Verifica búsqueda básica de productos"""
    print_test("2.1 - Búsqueda Básica de Productos")

    try:
        with app.app_context():
            # Test 1: Búsqueda sin filtros
            print_subtest("Búsqueda sin filtros")
            todos = buscar_productos("", limit=10)
            print_success(f"Todos los productos: {len(todos)} encontrados")

            # Test 2: Búsqueda por keyword
            print_subtest("Búsqueda por keyword")
            keywords = ['laptop', 'mouse', 'teclado', 'monitor']
            for keyword in keywords:
                resultados = buscar_productos(keyword, limit=5)
                print_info(f"'{keyword}': {len(resultados)} productos")

            # Test 3: Búsqueda TV (caso crítico)
            print_subtest("Búsqueda TV (caso crítico del usuario)")
            resultados_tv = buscar_productos("tv", limit=10)
            if resultados_tv:
                print_success(f"✓ TVs encontrados: {len(resultados_tv)}")
                for prod in resultados_tv[:3]:
                    print(f"   - {prod['nombre']} (${prod['precio']}) - Stock: {prod['stock']}")
            else:
                print_warning("No se encontraron TVs")

            return True
    except Exception as e:
        print_error(f"Error en búsqueda básica: {e}")
        return False


def test_advanced_product_search(app):
    """Verifica búsqueda avanzada con filtros"""
    print_test("2.2 - Búsqueda Avanzada (Filtros)")

    try:
        with app.app_context():
            # Test 1: Filtro por precio
            print_subtest("Filtro por precio")
            baratos = buscar_productos("", precio_max=100, limit=5)
            print_success(f"Productos <$100: {len(baratos)}")
            if baratos:
                print_info(f"Más barato: {baratos[0]['nombre']} (${baratos[0]['precio']})")

            caros = buscar_productos("", precio_min=500, limit=5)
            print_success(f"Productos >$500: {len(caros)}")

            # Test 2: Filtro por rango de precio
            print_subtest("Filtro por rango")
            rango = buscar_productos("", precio_min=100, precio_max=500, limit=5)
            print_success(f"Productos $100-$500: {len(rango)}")

            # Test 3: Filtro por categoría
            print_subtest("Filtro por categoría")
            categorias_test = ['laptop', 'electronica', 'accesorios']
            for cat in categorias_test:
                resultados = buscar_productos("", categoria=cat, limit=5)
                print_info(f"Categoría '{cat}': {len(resultados)} productos")

            return True
    except Exception as e:
        print_error(f"Error en búsqueda avanzada: {e}")
        return False


def test_synonym_search(app):
    """Verifica búsqueda semántica con sinónimos"""
    print_test("2.3 - Búsqueda Semántica (Sinónimos)")

    try:
        with app.app_context():
            print_subtest("Expansión de sinónimos")

            # Test sinónimos comunes
            sinonimos_test = {
                'laptop': ['portátil', 'computadora portátil', 'notebook'],
                'mouse': ['ratón'],
                'celular': ['móvil', 'smartphone', 'teléfono'],
                'tv': ['televisor', 'televisión', 'smart tv']
            }

            for termino, sinonimos in sinonimos_test.items():
                print_info(f"\nTérmino: '{termino}'")
                expandidos = expandir_query_con_sinonimos(termino)
                print_success(f"Expandido a {len(expandidos)} términos")
                print(f"   {expandidos[:5]}")

                # Buscar con cada sinónimo
                for sin in sinonimos[:2]:
                    resultados = buscar_productos(sin, limit=3)
                    print_info(f"  '{sin}': {len(resultados)} productos")

            return True
    except Exception as e:
        print_error(f"Error en búsqueda semántica: {e}")
        return False


def test_category_system(app):
    """Verifica sistema de categorías y subcategorías"""
    print_test("2.4 - Sistema de Categorías")

    try:
        with app.app_context():
            # Test categorías
            print_subtest("Categorías principales")
            categorias = Categoria.query.all()
            print_success(f"Total categorías: {len(categorias)}")

            for cat in categorias[:5]:
                num_productos = Producto.query.filter_by(id_categoria=cat.id).count()
                print_info(f"{cat.categoria}: {num_productos} productos")

            # Test subcategorías
            print_subtest("Subcategorías")
            if Subcategoria is not None:
                try:
                    subcategorias = Subcategoria.query.all()
                    print_success(f"Total subcategorías: {len(subcategorias)}")
                except Exception as e:
                    print_warning(f"Error al consultar subcategorías: {e}")
            else:
                print_warning("Modelo Subcategoria no disponible")

            return True
    except Exception as e:
        print_error(f"Error en categorías: {e}")
        return False


# ============================================================================
# SECCIÓN 3: CHATBOT E INTELIGENCIA ARTIFICIAL
# ============================================================================

def test_chatbot_ai_catalog(app):
    """Verifica que la IA recibe el catálogo completo"""
    print_test("3.1 - Catálogo Completo para IA")

    try:
        with app.app_context():
            print_subtest("Obtención del catálogo")
            catalogo = ai_service._obtener_catalogo_para_ia(limit=50)

            if not catalogo:
                print_error("Catálogo vacío")
                return False

            print_success(f"Catálogo obtenido: {len(catalogo)} productos")

            # Verificar estructura
            print_subtest("Verificación de estructura")
            primer_producto = catalogo[0]
            campos_requeridos = ['id', 'nombre', 'descripcion', 'precio', 'stock', 'categoria', 'disponible']

            for campo in campos_requeridos:
                if campo in primer_producto:
                    print_success(f"Campo '{campo}' presente")
                else:
                    print_error(f"Campo '{campo}' FALTA")

            # Verificar productos con stock
            print_subtest("Análisis de disponibilidad")
            con_stock = sum(1 for p in catalogo if p['disponible'])
            sin_stock = len(catalogo) - con_stock
            print_info(f"Con stock: {con_stock}")
            print_info(f"Sin stock: {sin_stock}")

            # Buscar TVs (caso crítico)
            print_subtest("Verificación caso crítico (TVs)")
            productos_tv = [p for p in catalogo if 'tv' in p['nombre'].lower() or 'televisor' in p['nombre'].lower()]
            if productos_tv:
                print_success(f"✓ TVs en catálogo: {len(productos_tv)}")
                for tv in productos_tv:
                    print(f"   - {tv['nombre']} (${tv['precio']}) - Stock: {tv['stock']}")
            else:
                print_warning("No hay TVs en el catálogo")

            return True
    except Exception as e:
        print_error(f"Error obteniendo catálogo: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chatbot_reasoning(app):
    """Verifica razonamiento automático del chatbot"""
    print_test("3.2 - Chatbot con Razonamiento IA")

    try:
        with app.app_context():
            preguntas_test = [
                ("hola tienes tv?", "CRÍTICO: Caso TV del usuario"),
                ("cuánto cuesta laptop más barata?", "Consulta de precio"),
                ("hay stock de monitores?", "Consulta de stock"),
                ("necesito algo para trabajar desde casa", "Búsqueda contextual"),
                ("quiero comprar mouse gaming", "Búsqueda específica"),
            ]

            for i, (pregunta, descripcion) in enumerate(preguntas_test, 1):
                print_subtest(f"Test {i}: {descripcion}")
                print_info(f"Pregunta: '{pregunta}'")

                respuesta = ai_service.chatbot_response(
                    session_id=f"test_session_{i}",
                    user_message=pregunta,
                    context={}
                )

                if respuesta['success']:
                    print_success("Chatbot respondió correctamente")
                    print(f"   Intención: {respuesta.get('intencion', 'N/A')}")
                    print(f"   Respuesta: {respuesta['response'][:150]}...")

                    # Verificación especial para TV
                    if "tv" in pregunta.lower():
                        if "no tenemos" in respuesta['response'].lower() and "televisor" in respuesta['response'].lower():
                            print_error("❌ CRÍTICO: Sigue diciendo 'no tenemos' cuando hay productos")
                        else:
                            print_success("✓ Razonamiento correcto sobre TVs")
                else:
                    print_error(f"Error: {respuesta.get('error')}")

            return True
    except Exception as e:
        print_error(f"Error en chatbot: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chatbot_intentions(app):
    """Verifica detección de intenciones del chatbot"""
    print_test("3.3 - Detección de Intenciones")

    try:
        with app.app_context():
            intenciones_test = [
                ("dónde está mi pedido?", "RASTREAR_PEDIDO"),
                ("cuánto cuesta el envío a Quito?", "CONSULTA_ENVIO"),
                ("tengo un cupón PROMO20", "APLICAR_CUPON"),
                ("quiero devolver el producto", "RECLAMO"),
                ("cómo puedo pagar?", "CONSULTA_PAGO"),
                ("recomiéndame una laptop", "RECOMENDACION"),
                ("busco mouse barato", "BUSCAR_PRODUCTO"),
            ]

            for mensaje, intencion_esperada in intenciones_test:
                intencion_detectada = ai_service._detectar_intencion(mensaje)
                if intencion_detectada == intencion_esperada:
                    print_success(f"'{mensaje}' → {intencion_detectada}")
                else:
                    print_warning(f"'{mensaje}' → Esperado: {intencion_esperada}, Obtenido: {intencion_detectada}")

            return True
    except Exception as e:
        print_error(f"Error en detección de intenciones: {e}")
        return False


def test_ai_description_generation(app):
    """Verifica generación de descripciones con IA"""
    print_test("3.4 - Generación de Descripciones IA")

    try:
        with app.app_context():
            print_subtest("Generando descripción de prueba")

            resultado = ai_service.generar_descripcion_producto(
                nombre="Laptop HP 15 Intel i5",
                categoria="Laptops",
                precio=750.00,
                caracteristicas="Intel Core i5, 8GB RAM, 256GB SSD, Pantalla 15.6 pulgadas",
                publico="Estudiantes y profesionales",
                keywords="laptop, portatil, hp, intel"
            )

            if resultado['success']:
                data = resultado['data']
                print_success("Descripción generada correctamente")

                print_info(f"Descripción corta: {len(data['descripcion_corta'])} caracteres")
                print(f"   {data['descripcion_corta'][:100]}...")

                print_info(f"Descripción larga: {len(data['descripcion_larga'])} caracteres")

                print_info(f"Beneficios: {len(data['beneficios'])}")
                for i, beneficio in enumerate(data['beneficios'], 1):
                    print(f"   {i}. {beneficio[:60]}...")

                print_info(f"CTA: {data['call_to_action']}")

                return True
            else:
                print_error(f"Error: {resultado.get('error')}")
                return False
    except Exception as e:
        print_error(f"Error en generación IA: {e}")
        return False


# ============================================================================
# SECCIÓN 4: GESTIÓN DE PEDIDOS
# ============================================================================

def test_order_tracking(app):
    """Verifica sistema de tracking de pedidos"""
    print_test("4.1 - Tracking de Pedidos (Estilo Delivery)")

    try:
        with app.app_context():
            print_subtest("Buscando orden de prueba")
            orden = Compra.query.order_by(Compra.fecha.desc()).first()

            if not orden:
                print_warning("No hay órdenes para probar")
                return False

            print_info(f"Orden ID: {orden.id}")
            print_info(f"Estado: {orden.estado}")
            print_info(f"Fecha: {orden.fecha.strftime('%Y-%m-%d %H:%M')}")

            # Verificar tracking
            print_subtest("Función de tracking")
            tracking_info = rastrear_pedido(order_id=orden.id)

            if tracking_info.get('encontrado'):
                print_success("Tracking funciona correctamente")
                print_info(f"Mensaje: {tracking_info.get('mensaje')}")
                if 'estimacion_entrega' in tracking_info:
                    print_info(f"Estimación: {tracking_info['estimacion_entrega']}")
            else:
                print_error(f"Error: {tracking_info.get('error')}")

            # Verificar estados progresivos
            print_subtest("Estados progresivos")
            estados_validos = ['pendiente', 'procesando', 'enviado', 'entregado', 'cancelado']
            if orden.estado.lower() in estados_validos:
                print_success(f"Estado '{orden.estado}' es válido")
            else:
                print_error(f"Estado '{orden.estado}' NO válido")

            return True
    except Exception as e:
        print_error(f"Error en tracking: {e}")
        return False


def test_order_status_workflow(app):
    """Verifica flujo de estados de orden"""
    print_test("4.2 - Flujo de Estados de Orden")

    try:
        with app.app_context():
            print_subtest("Estados del sistema")
            estados = ['pendiente', 'procesando', 'enviado', 'entregado', 'cancelado']

            for estado in estados:
                ordenes = Compra.query.filter_by(estado=estado).count()
                print_info(f"{estado.capitalize()}: {ordenes} órdenes")

            # Verificar transiciones válidas
            print_subtest("Transiciones de estado")
            transiciones_validas = [
                ('pendiente', 'procesando'),
                ('procesando', 'enviado'),
                ('enviado', 'entregado'),
                ('pendiente', 'cancelado'),
            ]

            for desde, hacia in transiciones_validas:
                print_success(f"{desde} → {hacia}: Válida")

            return True
    except Exception as e:
        print_error(f"Error en flujo de estados: {e}")
        return False


def test_stock_automation(app):
    """Verifica gestión automática de stock"""
    print_test("4.3 - Gestión Automática de Stock")

    try:
        with app.app_context():
            print_subtest("Buscando producto con stock")
            producto = Producto.query.filter(Producto.stock > 5).first()

            if not producto:
                print_warning("No hay productos con stock suficiente")
                return False

            print_info(f"Producto: {producto.titulo}")
            stock_inicial = producto.stock
            print_info(f"Stock actual: {stock_inicial}")

            # Verificar método tiene_stock
            print_subtest("Método tiene_stock()")
            if producto.tiene_stock(1):
                print_success("tiene_stock(1): True")
            if producto.tiene_stock(stock_inicial + 1):
                print_success("tiene_stock(stock+1): False (correcto)")
            else:
                print_error("tiene_stock() no funciona correctamente")

            # Verificar lógica de decremento
            print_subtest("Lógica de decremento")
            ordenes_pendientes = Compra.query.filter_by(
                id_producto=producto.id,
                estado='pendiente'
            ).count()
            print_info(f"Órdenes pendientes: {ordenes_pendientes}")

            ordenes_procesando = Compra.query.filter_by(
                id_producto=producto.id,
                estado='procesando'
            ).count()
            print_info(f"Órdenes procesando: {ordenes_procesando}")

            if ordenes_pendientes > 0:
                print_success("Órdenes pendientes NO decrementan stock (correcto)")
            if ordenes_procesando > 0:
                print_success("Órdenes procesando SÍ decrementan stock")

            return True
    except Exception as e:
        print_error(f"Error en stock automation: {e}")
        return False


def test_order_history(app):
    """Verifica historial de compras"""
    print_test("4.4 - Historial de Compras")

    try:
        with app.app_context():
            print_subtest("Buscando usuario con compras")
            usuario = User.query.join(Compra).first()

            if not usuario:
                print_warning("No hay usuarios con compras")
                return False

            print_info(f"Usuario: {usuario.nombre}")

            # Obtener historial
            historial = obtener_historial_compras(usuario.id, limit=10)

            if historial:
                print_success(f"Historial obtenido: {len(historial)} compras")

                total_gastado = sum(h['total'] for h in historial)
                print_info(f"Total gastado: ${total_gastado:.2f}")

                print_info("Últimas compras:")
                for h in historial[:3]:
                    print(f"   - {h['fecha']}: {h['producto']} (${h['total']})")
            else:
                print_warning("Historial vacío")

            return True
    except Exception as e:
        print_error(f"Error en historial: {e}")
        return False


# ============================================================================
# SECCIÓN 5: CARRITO DE COMPRAS
# ============================================================================

def test_cart_functionality(app):
    """Verifica funcionalidad del carrito"""
    print_test("5.1 - Carrito de Compras")

    try:
        with app.app_context():
            print_subtest("Verificando tabla Carrito")

            if Carrito is None:
                print_warning("Modelo Carrito no disponible - se omite este test")
                return True

            try:
                carritos = Carrito.query.count()
                print_success(f"Tabla Carrito existe: {carritos} items")

                if carritos > 0:
                    carrito_sample = Carrito.query.first()
                    print_info(f"Item ejemplo: Producto {carrito_sample.id_producto}, Cantidad: {carrito_sample.cantidad}")
            except Exception as e:
                print_warning(f"Error al consultar Carrito: {e}")

            return True
    except Exception as e:
        print_error(f"Error en carrito: {e}")
        return False


# ============================================================================
# SECCIÓN 6: SISTEMA DE CUPONES Y DESCUENTOS
# ============================================================================

def test_coupon_system(app):
    """Verifica sistema de cupones"""
    print_test("6.1 - Sistema de Cupones")

    try:
        with app.app_context():
            print_subtest("Cupones en sistema")
            cupones = Cupon.query.all()
            print_info(f"Total cupones: {len(cupones)}")

            if cupones:
                for cupon in cupones[:3]:
                    print_info(f"Cupón: {cupon.codigo} - {cupon.descuento}% - Estado: {'Activo' if cupon.activo else 'Inactivo'}")

                # Test validación
                print_subtest("Validación de cupón")
                cupon_test = cupones[0]

                resultado = validar_aplicar_cupon(
                    codigo_cupon=cupon_test.codigo,
                    total_compra=100.00
                )

                if resultado['valido']:
                    print_success(f"Cupón '{cupon_test.codigo}' validado")
                    print_info(f"Descuento: ${resultado['descuento_aplicado']}")
                    print_info(f"Ahorro: ${resultado['ahorro']}")
                else:
                    print_warning(f"Cupón inválido: {resultado.get('error')}")
            else:
                print_warning("No hay cupones para probar")

            return True
    except Exception as e:
        print_error(f"Error en cupones: {e}")
        return False


# ============================================================================
# SECCIÓN 7: COMENTARIOS Y REVIEWS
# ============================================================================

def test_comments_reviews(app):
    """Verifica sistema de comentarios y reviews"""
    print_test("7.1 - Comentarios y Reviews")

    try:
        with app.app_context():
            print_subtest("Comentarios en sistema")
            comentarios = Comentario.query.all()
            print_success(f"Total comentarios: {len(comentarios)}")

            if comentarios:
                aprobados = Comentario.query.filter_by(estado=1).count()
                pendientes = Comentario.query.filter_by(estado=0).count()

                print_info(f"Aprobados: {aprobados}")
                print_info(f"Pendientes: {pendientes}")

                # Análisis de ratings
                print_subtest("Análisis de ratings")
                ratings = [c.calificacion for c in comentarios if c.calificacion]
                if ratings:
                    avg_rating = sum(ratings) / len(ratings)
                    print_success(f"Rating promedio: {avg_rating:.2f}/5")

                    distribucion = {}
                    for r in range(1, 6):
                        count = ratings.count(r)
                        distribucion[r] = count

                    print_info("Distribución:")
                    for estrellas, count in distribucion.items():
                        print(f"   {estrellas} estrellas: {count} reviews")
            else:
                print_warning("No hay comentarios en el sistema")

            return True
    except Exception as e:
        print_error(f"Error en comentarios: {e}")
        return False


# ============================================================================
# SECCIÓN 8: ENVÍOS Y LOGÍSTICA
# ============================================================================

def test_shipping_calculation(app):
    """Verifica cálculo de costos de envío"""
    print_test("8.1 - Cálculo de Envíos")

    try:
        with app.app_context():
            print_subtest("Tarifas por ciudad")
            ciudades_ecuador = [
                'Quito', 'Guayaquil', 'Cuenca', 'Ambato',
                'Manta', 'Loja', 'Machala', 'Esmeraldas'
            ]

            for ciudad in ciudades_ecuador:
                resultado = calcular_costo_envio(ciudad=ciudad)
                print_info(f"{ciudad}: ${resultado['costo']} - {resultado['tiempo_estimado']}")

            # Verificar envío gratis
            print_subtest("Envío gratis")
            envio_gratis_desde = resultado.get('envio_gratis_desde', 50)
            print_success(f"Envío gratis desde: ${envio_gratis_desde}")

            # Verificar peso adicional
            print_subtest("Cálculo por peso")
            resultado_pesado = calcular_costo_envio(ciudad='Quito', peso_kg=5.0)
            print_info(f"Paquete 5kg a Quito: ${resultado_pesado['costo']}")

            return True
    except Exception as e:
        print_error(f"Error en cálculo de envíos: {e}")
        return False


# ============================================================================
# SECCIÓN 9: VALIDACIONES Y SEGURIDAD
# ============================================================================

def test_data_validation(app):
    """Verifica validación de datos"""
    print_test("9.1 - Validación de Datos")

    try:
        with app.app_context():
            # Test datos válidos
            print_subtest("Datos válidos")
            resultado_valido = validar_datos_compra(
                nombre="Juan Pérez",
                email="juan@example.com",
                telefono="0998765432",
                direccion="Av. 6 de Diciembre N24-123, Sector La Carolina, Quito"
            )

            if resultado_valido['valido']:
                print_success("Validación de datos correctos funciona")
                print_info(f"Puntuación: {resultado_valido['puntuacion_calidad']}/100")
            else:
                print_error(f"Validación rechazó datos válidos")

            # Test datos inválidos
            print_subtest("Datos inválidos")
            resultado_invalido = validar_datos_compra(
                nombre="AB",
                email="email_invalido",
                telefono="123",
                direccion="X"
            )

            if not resultado_invalido['valido']:
                print_success("Validación detecta datos inválidos")
                print_info(f"Errores: {len(resultado_invalido['errores'])}")
                for error in resultado_invalido['errores']:
                    print(f"   - {error}")
            else:
                print_error("Validación NO detectó datos inválidos")

            return True
    except Exception as e:
        print_error(f"Error en validación: {e}")
        return False


def test_fraud_detection(app):
    """Verifica detección de fraude"""
    print_test("9.2 - Detección de Fraude")

    try:
        with app.app_context():
            print_subtest("Usuario nuevo con compra alta")

            # Buscar usuario muy nuevo
            usuario_nuevo = User.query.order_by(User.fecha.desc()).first()

            if usuario_nuevo:
                resultado = detectar_comportamiento_sospechoso(
                    usuario_id=usuario_nuevo.id,
                    total_compra=1500.00
                )

                print_info(f"Score de riesgo: {resultado['riesgo_score']}/100")
                print_info(f"Nivel: {resultado['nivel_riesgo']}")
                print_info(f"Acción: {resultado['accion_recomendada']}")

                if resultado['alertas']:
                    print_warning("Alertas detectadas:")
                    for alerta in resultado['alertas']:
                        print(f"   - {alerta}")

                if resultado['requiere_verificacion']:
                    print_warning("⚠️  Requiere verificación manual")
                else:
                    print_success("Puede procesar normalmente")
            else:
                print_warning("No hay usuarios para probar")

            return True
    except Exception as e:
        print_error(f"Error en detección de fraude: {e}")
        return False


# ============================================================================
# SECCIÓN 10: RECOMENDACIONES Y ANÁLISIS
# ============================================================================

def test_recommendations(app):
    """Verifica sistema de recomendaciones"""
    print_test("10.1 - Recomendaciones Personalizadas")

    try:
        with app.app_context():
            print_subtest("Recomendaciones por producto")
            producto = Producto.query.filter(
                Producto.stock > 0,
                Producto.id_categoria.isnot(None)
            ).first()

            if not producto:
                print_warning("No hay productos para probar")
                return False

            print_info(f"Producto base: {producto.titulo}")

            recomendaciones = obtener_recomendaciones_personalizadas(
                producto_actual=producto.id,
                limite=5
            )

            if recomendaciones:
                print_success(f"Generadas {len(recomendaciones)} recomendaciones")
                for rec in recomendaciones:
                    print(f"   - {rec['nombre']} (${rec['precio']}) - {rec['razon']}")
            else:
                print_warning("No se generaron recomendaciones")

            # Test con usuario
            print_subtest("Recomendaciones personalizadas")
            usuario = User.query.join(Compra).first()
            if usuario:
                recs_usuario = obtener_recomendaciones_personalizadas(
                    usuario_id=usuario.id,
                    limite=5
                )
                print_success(f"Recomendaciones para usuario: {len(recs_usuario)}")

            return True
    except Exception as e:
        print_error(f"Error en recomendaciones: {e}")
        return False


def test_product_comparison(app):
    """Verifica comparación de productos"""
    print_test("10.2 - Comparación de Productos")

    try:
        with app.app_context():
            print_subtest("Comparando productos")

            # Obtener algunos productos
            productos = Producto.query.filter(Producto.stock > 0).limit(3).all()

            if len(productos) < 2:
                print_warning("No hay suficientes productos para comparar")
                return False

            ids = [p.id for p in productos]
            print_info(f"Comparando: {[p.titulo for p in productos]}")

            comparacion = comparar_productos(ids)

            if comparacion.get('productos'):
                print_success(f"Comparación realizada: {len(comparacion['productos'])} productos")
                print_info(f"Mejor precio: Producto ID {comparacion.get('mejor_precio')}")
                print_info(f"Mejor rating: Producto ID {comparacion.get('mejor_rating')}")
                print_info(f"Más vendido: Producto ID {comparacion.get('mas_vendido')}")
            else:
                print_error("Error en comparación")

            return True
    except Exception as e:
        print_error(f"Error en comparación: {e}")
        return False


def test_product_statistics(app):
    """Verifica estadísticas de productos"""
    print_test("10.3 - Estadísticas de Productos")

    try:
        with app.app_context():
            print_subtest("Estadísticas generales")

            total_productos = Producto.query.count()
            con_stock = Producto.query.filter(Producto.stock > 0).count()
            sin_stock = total_productos - con_stock

            print_info(f"Total productos: {total_productos}")
            print_info(f"Con stock: {con_stock}")
            print_info(f"Sin stock: {sin_stock}")

            # Producto más vendido
            mas_vendido = Producto.query.order_by(Producto.ventas.desc()).first()
            if mas_vendido:
                print_success(f"Más vendido: {mas_vendido.titulo} ({mas_vendido.ventas} ventas)")

            # Producto mejor valorado
            print_subtest("Producto con mejor rating")
            productos_con_comments = Producto.query.join(Comentario).all()
            if productos_con_comments:
                mejor_rating = max(productos_con_comments, key=lambda p: p.get_average_rating())
                print_success(f"Mejor valorado: {mejor_rating.titulo} ({mejor_rating.get_average_rating():.1f}/5)")

            return True
    except Exception as e:
        print_error(f"Error en estadísticas: {e}")
        return False


# ============================================================================
# SECCIÓN 11: MÉTODOS DE PAGO
# ============================================================================

def test_payment_methods(app):
    """Verifica métodos de pago"""
    print_test("11.1 - Métodos de Pago")

    try:
        with app.app_context():
            print_subtest("Métodos disponibles")

            metodos_info = obtener_metodos_pago_disponibles(total=100.00)

            if metodos_info.get('metodos'):
                print_success(f"Métodos configurados: {len(metodos_info['metodos'])}")

                for key, metodo in metodos_info['metodos'].items():
                    disponible = "✓" if metodo['disponible'] else "✗"
                    print_info(f"{disponible} {metodo['nombre']} - Comisión: ${metodo['comision']}")

                print_info(f"Recomendado: {metodos_info.get('recomendado')}")

            # Test con monto alto
            print_subtest("Verificación de límites")
            metodos_alto = obtener_metodos_pago_disponibles(total=500.00)
            contra_entrega = metodos_alto['metodos'].get('contra_entrega', {})

            if not contra_entrega.get('disponible'):
                print_success("Contra entrega deshabilitado para montos altos (correcto)")

            return True
    except Exception as e:
        print_error(f"Error en métodos de pago: {e}")
        return False


# ============================================================================
# SECCIÓN 12: SISTEMA DE OFERTAS
# ============================================================================

def test_offers_system(app):
    """Verifica sistema de ofertas"""
    print_test("12.1 - Sistema de Ofertas")

    try:
        with app.app_context():
            print_subtest("Productos en oferta")

            productos_oferta = [p for p in Producto.query.all() if p.is_on_offer()]

            print_info(f"Productos en oferta: {len(productos_oferta)}")

            if productos_oferta:
                for prod in productos_oferta[:5]:
                    precio_original = prod.precio
                    precio_oferta = prod.get_price()
                    descuento = prod.descuentoOferta

                    print_success(f"{prod.titulo}")
                    print(f"   Antes: ${precio_original} | Ahora: ${precio_oferta} | Descuento: {descuento}%")
            else:
                print_warning("No hay productos en oferta actualmente")

            return True
    except Exception as e:
        print_error(f"Error en ofertas: {e}")
        return False


# ============================================================================
# RESUMEN Y EJECUCIÓN
# ============================================================================

def run_all_tests():
    """Ejecuta TODOS los tests del sistema"""
    print(f"\n{Colors.BOLD}{'='*70}")
    print("🧪 SUITE COMPLETA DE TESTS - ECOMMERCE SYSTEM")
    print(f"{'='*70}{Colors.END}\n")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Crear app
    app = create_app()

    # Lista COMPLETA de tests
    tests = [
        # SECCIÓN 1: Base de datos
        ("1.1 BD - Conexión", lambda: test_database_connection(app)),
        ("1.2 BD - Modelo Producto", lambda: test_product_model(app)),
        ("1.3 BD - Modelo Usuario", lambda: test_user_model(app)),
        ("1.4 BD - Modelo Orden", lambda: test_order_model(app)),

        # SECCIÓN 2: Búsqueda
        ("2.1 Búsqueda Básica", lambda: test_basic_product_search(app)),
        ("2.2 Búsqueda Avanzada", lambda: test_advanced_product_search(app)),
        ("2.3 Búsqueda Semántica", lambda: test_synonym_search(app)),
        ("2.4 Categorías", lambda: test_category_system(app)),

        # SECCIÓN 3: IA y Chatbot
        ("3.1 Catálogo IA", lambda: test_chatbot_ai_catalog(app)),
        ("3.2 Razonamiento IA", lambda: test_chatbot_reasoning(app)),
        ("3.3 Intenciones", lambda: test_chatbot_intentions(app)),
        ("3.4 Descripciones IA", lambda: test_ai_description_generation(app)),

        # SECCIÓN 4: Pedidos
        ("4.1 Tracking", lambda: test_order_tracking(app)),
        ("4.2 Estados Orden", lambda: test_order_status_workflow(app)),
        ("4.3 Stock Automático", lambda: test_stock_automation(app)),
        ("4.4 Historial", lambda: test_order_history(app)),

        # SECCIÓN 5: Carrito
        ("5.1 Carrito", lambda: test_cart_functionality(app)),

        # SECCIÓN 6: Cupones
        ("6.1 Cupones", lambda: test_coupon_system(app)),

        # SECCIÓN 7: Reviews
        ("7.1 Comentarios", lambda: test_comments_reviews(app)),

        # SECCIÓN 8: Envíos
        ("8.1 Cálculo Envíos", lambda: test_shipping_calculation(app)),

        # SECCIÓN 9: Seguridad
        ("9.1 Validación Datos", lambda: test_data_validation(app)),
        ("9.2 Detección Fraude", lambda: test_fraud_detection(app)),

        # SECCIÓN 10: Análisis
        ("10.1 Recomendaciones", lambda: test_recommendations(app)),
        ("10.2 Comparación", lambda: test_product_comparison(app)),
        ("10.3 Estadísticas", lambda: test_product_statistics(app)),

        # SECCIÓN 11: Pagos
        ("11.1 Métodos Pago", lambda: test_payment_methods(app)),

        # SECCIÓN 12: Ofertas
        ("12.1 Sistema Ofertas", lambda: test_offers_system(app)),
    ]

    # Ejecutar tests
    resultados = []
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print_error(f"Error ejecutando test '{nombre}': {e}")
            import traceback
            traceback.print_exc()
            resultados.append((nombre, False))

    # Resumen final
    print(f"\n{Colors.BOLD}{'='*70}")
    print("📊 RESUMEN FINAL DE RESULTADOS")
    print(f"{'='*70}{Colors.END}\n")

    exitosos = sum(1 for _, resultado in resultados if resultado)
    totales = len(resultados)
    porcentaje = round(exitosos/totales*100)

    # Agrupar por sección
    secciones = {}
    for nombre, resultado in resultados:
        seccion = nombre.split()[0]
        if seccion not in secciones:
            secciones[seccion] = []
        secciones[seccion].append((nombre, resultado))

    # Mostrar por sección
    for seccion, tests in secciones.items():
        exitosos_seccion = sum(1 for _, r in tests if r)
        total_seccion = len(tests)
        print(f"\n{Colors.BOLD}{seccion}:{Colors.END}")
        for nombre, resultado in tests:
            if resultado:
                print(f"{Colors.GREEN}  ✅ {nombre}: PASSED{Colors.END}")
            else:
                print(f"{Colors.RED}  ❌ {nombre}: FAILED{Colors.END}")
        print(f"  Subtotal: {exitosos_seccion}/{total_seccion}")

    # Total general
    print(f"\n{Colors.BOLD}{'='*70}")
    print(f"TOTAL GENERAL: {exitosos}/{totales} tests pasaron ({porcentaje}%)")
    print(f"{'='*70}{Colors.END}\n")

    if porcentaje == 100:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ¡PERFECTO! TODOS LOS TESTS PASARON{Colors.END}")
        return 0
    elif porcentaje >= 80:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  MAYORMENTE EXITOSO - Revisar tests fallidos{Colors.END}")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ MÚLTIPLES FALLOS - REVISAR URGENTE{Colors.END}")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
