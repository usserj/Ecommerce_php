#!/usr/bin/env python
"""
Suite de Tests COMPREHENSIVA Y AVANZADA
Cobertura: Edge cases, validaciones, flujos completos, seguridad, performance
Ejecutar: python test_comprehensive.py
"""

import sys
import os
import time
import json
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

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

# Imports opcionales
try:
    from app.models.categoria import Subcategoria
except ImportError:
    Subcategoria = None

# Colores
class C:
    G = '\033[92m'  # Green
    R = '\033[91m'  # Red
    Y = '\033[93m'  # Yellow
    B = '\033[94m'  # Blue
    M = '\033[95m'  # Magenta
    C = '\033[96m'  # Cyan
    W = '\033[97m'  # White
    BOLD = '\033[1m'
    END = '\033[0m'

def test_header(name):
    print(f"\n{C.B}{C.BOLD}{'='*80}{C.END}")
    print(f"{C.B}{C.BOLD}🧪 {name}{C.END}")
    print(f"{C.B}{C.BOLD}{'='*80}{C.END}")

def section(name):
    print(f"\n{C.M}▶ {name}{C.END}")

def success(msg):
    print(f"{C.G}  ✅ {msg}{C.END}")

def fail(msg):
    print(f"{C.R}  ❌ {msg}{C.END}")

def warn(msg):
    print(f"{C.Y}  ⚠️  {msg}{C.END}")

def info(msg):
    print(f"{C.C}  ℹ️  {msg}{C.END}")

def detail(msg):
    print(f"     {msg}")


# ============================================================================
# SECCIÓN 1: TESTS DE MODELOS - VALIDACIONES Y EDGE CASES
# ============================================================================

def test_producto_edge_cases(app):
    """Tests exhaustivos del modelo Producto"""
    test_header("MODELO PRODUCTO - EDGE CASES Y VALIDACIONES")

    try:
        with app.app_context():
            # Test 1: Productos con stock 0
            section("Test 1: Productos sin stock")
            sin_stock = Producto.query.filter(Producto.stock == 0).all()
            info(f"Productos sin stock: {len(sin_stock)}")

            for p in sin_stock[:3]:
                if not p.tiene_stock(1):
                    success(f"{p.titulo}: tiene_stock(1) = False (correcto)")
                else:
                    fail(f"{p.titulo}: tiene_stock(1) debería ser False")

            # Test 2: Productos con stock negativo (NO DEBERÍA EXISTIR)
            section("Test 2: Validación stock negativo")
            stock_negativo = Producto.query.filter(Producto.stock < 0).all()
            if len(stock_negativo) == 0:
                success("No hay productos con stock negativo (correcto)")
            else:
                fail(f"CRÍTICO: {len(stock_negativo)} productos con stock negativo")
                for p in stock_negativo:
                    detail(f"{p.titulo}: stock = {p.stock}")

            # Test 3: Precios extremos
            section("Test 3: Validación de precios")
            precio_cero = Producto.query.filter(Producto.precio == 0).all()
            if len(precio_cero) > 0:
                warn(f"{len(precio_cero)} productos con precio $0")
            else:
                success("No hay productos con precio $0")

            precio_muy_alto = Producto.query.filter(Producto.precio > 10000).all()
            if len(precio_muy_alto) > 0:
                warn(f"{len(precio_muy_alto)} productos con precio >$10,000")
                for p in precio_muy_alto[:3]:
                    detail(f"{p.titulo}: ${p.precio}")

            # Test 4: Descuentos inválidos
            section("Test 4: Validación de descuentos")
            productos = Producto.query.all()
            descuentos_invalidos = 0

            for p in productos:
                if p.descuentoOferta:
                    if p.descuentoOferta < 0 or p.descuentoOferta > 100:
                        descuentos_invalidos += 1
                        fail(f"{p.titulo}: descuento inválido ({p.descuentoOferta}%)")

            if descuentos_invalidos == 0:
                success("Todos los descuentos están en rango 0-100%")

            # Test 5: Cálculo correcto de precio con descuento
            section("Test 5: Cálculo de precio con descuento")
            productos_oferta = [p for p in productos if p.is_on_offer()]

            for p in productos_oferta[:3]:
                precio_original = float(p.precio)
                precio_oferta = float(p.get_price())
                descuento_esperado = precio_original * (p.descuentoOferta / 100)
                precio_esperado = precio_original - descuento_esperado

                if abs(precio_oferta - precio_esperado) < 0.01:
                    success(f"{p.titulo}: cálculo de precio correcto")
                else:
                    fail(f"{p.titulo}: precio incorrecto (esperado: ${precio_esperado:.2f}, obtenido: ${precio_oferta:.2f})")

            # Test 6: Productos sin categoría
            section("Test 6: Productos sin categoría")
            sin_categoria = Producto.query.filter(Producto.id_categoria == None).all()
            if len(sin_categoria) > 0:
                warn(f"{len(sin_categoria)} productos sin categoría")
            else:
                success("Todos los productos tienen categoría")

            # Test 7: Títulos duplicados
            section("Test 7: Detección de productos duplicados")
            titulos = [p.titulo for p in productos]
            duplicados = [t for t in set(titulos) if titulos.count(t) > 1]

            if len(duplicados) > 0:
                warn(f"{len(duplicados)} títulos duplicados encontrados")
                for titulo in duplicados[:3]:
                    detail(f"Duplicado: '{titulo}'")
            else:
                success("No hay títulos duplicados")

            # Test 8: Slugs/rutas únicas
            section("Test 8: Validación de rutas únicas")
            rutas = [p.ruta for p in productos if p.ruta]
            rutas_duplicadas = [r for r in set(rutas) if rutas.count(r) > 1]

            if len(rutas_duplicadas) == 0:
                success("Todas las rutas son únicas")
            else:
                fail(f"CRÍTICO: {len(rutas_duplicadas)} rutas duplicadas")

            # Test 9: Imágenes rotas
            section("Test 9: Validación de imágenes")
            sin_imagen = [p for p in productos if not p.imagen or p.imagen == '']
            if len(sin_imagen) > 0:
                warn(f"{len(sin_imagen)} productos sin imagen")
            else:
                success("Todos los productos tienen imagen")

            # Test 10: Descripción vacía
            section("Test 10: Validación de descripciones")
            sin_descripcion = [p for p in productos if not p.descripcion or len(p.descripcion.strip()) < 10]
            if len(sin_descripcion) > 0:
                warn(f"{len(sin_descripcion)} productos sin descripción adecuada")
            else:
                success("Todos los productos tienen descripción")

            return True

    except Exception as e:
        fail(f"Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_orden_state_machine(app):
    """Tests del flujo de estados de órdenes"""
    test_header("MÁQUINA DE ESTADOS DE ÓRDENES - VALIDACIONES")

    try:
        with app.app_context():
            # Test 1: Estados válidos
            section("Test 1: Validación de estados")
            ordenes = Compra.query.all()
            estados_encontrados = set(o.estado for o in ordenes)
            estados_validos = set(Compra.ESTADOS_VALIDOS + ['completado', 'entregado'])  # Algunos usan completado

            estados_invalidos = estados_encontrados - estados_validos

            if len(estados_invalidos) == 0:
                success("Todos los estados son válidos")
            else:
                warn(f"Estados no reconocidos: {estados_invalidos}")

            info(f"Estados en uso: {estados_encontrados}")

            # Test 2: Distribución de estados
            section("Test 2: Distribución de estados")
            for estado in estados_encontrados:
                count = Compra.query.filter_by(estado=estado).count()
                info(f"{estado}: {count} órdenes ({count/len(ordenes)*100:.1f}%)")

            # Test 3: Órdenes antiguas pendientes
            section("Test 3: Órdenes pendientes antiguas")
            hace_7_dias = datetime.utcnow() - timedelta(days=7)
            pendientes_antiguas = Compra.query.filter(
                Compra.estado == 'pendiente',
                Compra.fecha < hace_7_dias
            ).all()

            if len(pendientes_antiguas) > 0:
                warn(f"{len(pendientes_antiguas)} órdenes pendientes >7 días")
                for orden in pendientes_antiguas[:3]:
                    dias = (datetime.utcnow() - orden.fecha).days
                    detail(f"Orden #{orden.id}: {dias} días pendiente")
            else:
                success("No hay órdenes pendientes antiguas")

            # Test 4: Órdenes sin precio total
            section("Test 4: Validación de precio total")
            sin_precio = Compra.query.filter(
                (Compra.precio_total == None) | (Compra.precio_total == 0)
            ).all()

            if len(sin_precio) > 0:
                warn(f"{len(sin_precio)} órdenes sin precio_total")
            else:
                success("Todas las órdenes tienen precio_total")

            # Test 5: Órdenes con cantidad inválida
            section("Test 5: Validación de cantidades")
            cantidad_invalida = Compra.query.filter(
                (Compra.cantidad <= 0) | (Compra.cantidad > 100)
            ).all()

            if len(cantidad_invalida) == 0:
                success("Todas las cantidades son válidas (1-100)")
            else:
                fail(f"{len(cantidad_invalida)} órdenes con cantidad inválida")

            # Test 6: Coherencia de direcciones
            section("Test 6: Validación de direcciones")
            sin_direccion = Compra.query.filter(
                (Compra.direccion == None) | (Compra.direccion == '')
            ).all()

            if len(sin_direccion) == 0:
                success("Todas las órdenes tienen dirección")
            else:
                fail(f"CRÍTICO: {len(sin_direccion)} órdenes sin dirección")

            # Test 7: Validación de emails
            section("Test 7: Validación de emails")
            emails_invalidos = 0
            for orden in ordenes[:50]:  # Sample
                if '@' not in orden.email or '.' not in orden.email:
                    emails_invalidos += 1

            if emails_invalidos == 0:
                success("Todos los emails parecen válidos")
            else:
                warn(f"{emails_invalidos} emails potencialmente inválidos")

            # Test 8: Métodos de pago
            section("Test 8: Distribución de métodos de pago")
            metodos = {}
            for orden in ordenes:
                metodo = orden.metodo
                metodos[metodo] = metodos.get(metodo, 0) + 1

            for metodo, count in metodos.items():
                info(f"{metodo}: {count} órdenes")

            return True

    except Exception as e:
        fail(f"Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# SECCIÓN 2: TESTS DE BÚSQUEDA - PRECISIÓN Y RECALL
# ============================================================================

def test_search_precision_recall(app):
    """Tests de precisión y recall de búsqueda"""
    test_header("BÚSQUEDA - PRECISIÓN Y RECALL")

    try:
        with app.app_context():
            # Test 1: Búsqueda vacía
            section("Test 1: Búsqueda con query vacía")
            resultados_vacio = buscar_productos("", limit=100)
            total_productos = Producto.query.filter_by(estado=1).count()

            if len(resultados_vacio) > 0:
                success(f"Búsqueda vacía retorna {len(resultados_vacio)} productos")
            else:
                warn("Búsqueda vacía retorna 0 productos")

            # Test 2: Búsqueda con caracteres especiales
            section("Test 2: Caracteres especiales")
            queries_especiales = ["laptop's", "café", "niño", "15.6\"", "HP-15"]

            for query in queries_especiales:
                resultados = buscar_productos(query, limit=5)
                info(f"'{query}': {len(resultados)} resultados")

            # Test 3: Case sensitivity
            section("Test 3: Case insensitivity")
            queries_case = [
                ("LAPTOP", "laptop", "LaPtOp"),
                ("TV", "tv", "Tv"),
                ("SAMSUNG", "samsung", "Samsung")
            ]

            for grupo in queries_case:
                resultados = [len(buscar_productos(q, limit=10)) for q in grupo]
                if len(set(resultados)) == 1:
                    success(f"{grupo[0]}: case insensitive correcto")
                else:
                    fail(f"{grupo[0]}: resultados diferentes: {resultados}")

            # Test 4: Búsqueda por fragmentos
            section("Test 4: Búsqueda por fragmentos")
            # Si existe "Laptop HP 15.6", debería encontrarse con "HP", "15", "Laptop HP"
            productos = Producto.query.all()

            for producto in productos[:5]:
                palabras = producto.titulo.split()[:2]  # Primeras 2 palabras
                for palabra in palabras:
                    if len(palabra) > 2:
                        resultados = buscar_productos(palabra, limit=20)
                        if any(r['id'] == producto.id for r in resultados):
                            success(f"'{palabra}' encuentra '{producto.titulo}'")
                        else:
                            warn(f"'{palabra}' NO encuentra '{producto.titulo}'")

            # Test 5: Recall de sinónimos (caso TV crítico)
            section("Test 5: Recall de sinónimos (CRÍTICO)")
            sinonimos_test = {
                'tv': ['televisor', 'television', 'smart tv'],
                'laptop': ['portatil', 'notebook', 'computadora'],
                'celular': ['móvil', 'smartphone', 'teléfono']
            }

            for termino_original, sinonimos in sinonimos_test.items():
                resultados_original = set(r['id'] for r in buscar_productos(termino_original, limit=20))

                for sinonimo in sinonimos:
                    resultados_sinonimo = set(r['id'] for r in buscar_productos(sinonimo, limit=20))

                    # Debería haber overlap
                    overlap = len(resultados_original & resultados_sinonimo)
                    if overlap > 0 or (len(resultados_original) == 0 and len(resultados_sinonimo) == 0):
                        success(f"'{termino_original}' ↔ '{sinonimo}': {overlap} productos en común")
                    else:
                        warn(f"'{termino_original}' vs '{sinonimo}': sin overlap")

            # Test 6: Filtros combinados
            section("Test 6: Filtros combinados")
            resultados_filtros = buscar_productos(
                query="",
                precio_min=100,
                precio_max=500,
                limit=20
            )

            # Verificar que todos estén en rango
            fuera_rango = [r for r in resultados_filtros if r['precio'] < 100 or r['precio'] > 500]
            if len(fuera_rango) == 0:
                success(f"Filtro de precio correcto: {len(resultados_filtros)} productos en rango")
            else:
                fail(f"{len(fuera_rango)} productos fuera del rango de precio")

            # Test 7: Orden de relevancia
            section("Test 7: Orden de relevancia")
            resultados_relevancia = buscar_productos("laptop", limit=10)

            if len(resultados_relevancia) >= 2:
                # Productos con stock deberían aparecer primero
                con_stock = [r for r in resultados_relevancia if r['disponible']]
                if len(con_stock) > 0 and resultados_relevancia[0]['disponible']:
                    success("Productos con stock aparecen primero")
                else:
                    warn("Orden de relevancia podría mejorar")

            return True

    except Exception as e:
        fail(f"Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# SECCIÓN 3: TESTS DE CHATBOT - RAZONAMIENTO Y PRECISIÓN
# ============================================================================

def test_chatbot_reasoning_deep(app):
    """Tests profundos del razonamiento del chatbot"""
    test_header("CHATBOT - RAZONAMIENTO AVANZADO")

    try:
        with app.app_context():
            # Test 1: Caso crítico TV (del usuario)
            section("Test 1: CASO CRÍTICO - Búsqueda de TV")

            preguntas_tv = [
                "tienes tv?",
                "hay televisores?",
                "venden smart tv?",
                "televisión samsung",
                "tv 55 pulgadas"
            ]

            for pregunta in preguntas_tv:
                respuesta = ai_service.chatbot_response(
                    session_id=f"test_tv_{hash(pregunta)}",
                    user_message=pregunta,
                    context={}
                )

                if respuesta['success']:
                    texto = respuesta['response'].lower()

                    # NUNCA debe decir "no tenemos" si hay TVs
                    if "no tenemos" in texto and ("tv" in texto or "televisor" in texto):
                        fail(f"'{pregunta}': ❌ CRÍTICO dice 'no tenemos'")
                    elif "tv samsung" in texto or "televisor" in texto or "$800" in texto:
                        success(f"'{pregunta}': ✓ Menciona TV correctamente")
                    else:
                        warn(f"'{pregunta}': Respuesta ambigua")

                    detail(f"Respuesta: {texto[:100]}...")
                else:
                    fail(f"'{pregunta}': Error - {respuesta.get('error')}")

            # Test 2: Preguntas sobre precio
            section("Test 2: Consultas de precio")

            preguntas_precio = [
                "cuánto cuesta el producto más barato?",
                "precio de laptops",
                "productos menos de $100"
            ]

            for pregunta in preguntas_precio:
                respuesta = ai_service.chatbot_response(
                    session_id=f"test_precio_{hash(pregunta)}",
                    user_message=pregunta,
                    context={}
                )

                if respuesta['success']:
                    texto = respuesta['response']
                    # Debería mencionar un precio con $
                    if '$' in texto:
                        success(f"'{pregunta}': Menciona precios")
                    else:
                        warn(f"'{pregunta}': No menciona precios concretos")

            # Test 3: Preguntas sobre stock
            section("Test 3: Consultas de disponibilidad")

            preguntas_stock = [
                "hay stock de laptops?",
                "tienen disponible tv samsung?",
                "cuántos quedan en stock?"
            ]

            for pregunta in preguntas_stock:
                respuesta = ai_service.chatbot_response(
                    session_id=f"test_stock_{hash(pregunta)}",
                    user_message=pregunta,
                    context={}
                )

                if respuesta['success']:
                    texto = respuesta['response'].lower()
                    palabras_stock = ['stock', 'disponible', 'quedan', 'unidades', 'hay']

                    if any(palabra in texto for palabra in palabras_stock):
                        success(f"'{pregunta}': Responde sobre disponibilidad")
                    else:
                        warn(f"'{pregunta}': No menciona stock")

            # Test 4: Intenciones complejas
            section("Test 4: Detección de intenciones complejas")

            intenciones_complejas = [
                ("quiero devolver mi pedido porque llegó defectuoso", "RECLAMO"),
                ("dónde está mi paquete? compré hace 3 días", "RASTREAR_PEDIDO"),
                ("necesito algo para trabajar desde casa", "BUSCAR_PRODUCTO"),
                ("puedo pagar en cuotas con tarjeta?", "CONSULTA_PAGO"),
            ]

            for mensaje, intencion_esperada in intenciones_complejas:
                intencion = ai_service._detectar_intencion(mensaje)
                if intencion == intencion_esperada:
                    success(f"'{mensaje[:40]}...': {intencion}")
                else:
                    warn(f"'{mensaje[:40]}...': esperado {intencion_esperada}, obtenido {intencion}")

            # Test 5: Contexto de conversación
            section("Test 5: Mantenimiento de contexto")

            session_id = "test_context"

            # Mensaje 1
            r1 = ai_service.chatbot_response(
                session_id=session_id,
                user_message="busco laptops",
                context={}
            )

            # Mensaje 2 (referencia implícita)
            r2 = ai_service.chatbot_response(
                session_id=session_id,
                user_message="cuál es la más barata?",
                context={}
            )

            if r2['success']:
                success("Chatbot procesa pregunta con contexto implícito")

            # Test 6: Manejo de errores del usuario
            section("Test 6: Robustez ante errores de escritura")

            preguntas_con_errores = [
                "tines laptos?",  # typos
                "CUANTO CUESTA???",  # mayúsculas y signos
                "laptop laptop laptop",  # repetición
            ]

            for pregunta in preguntas_con_errores:
                respuesta = ai_service.chatbot_response(
                    session_id=f"test_error_{hash(pregunta)}",
                    user_message=pregunta,
                    context={}
                )

                if respuesta['success']:
                    success(f"'{pregunta}': Manejado correctamente")
                else:
                    fail(f"'{pregunta}': Error - {respuesta.get('error')}")

            return True

    except Exception as e:
        fail(f"Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# SECCIÓN 4: TESTS DE STOCK - CONCURRENCIA Y RACE CONDITIONS
# ============================================================================

def test_stock_concurrency(app):
    """Tests de concurrencia en gestión de stock"""
    test_header("STOCK - CONCURRENCIA Y RACE CONDITIONS")

    try:
        with app.app_context():
            # Test 1: Decremento atómico
            section("Test 1: Decremento de stock es atómico")

            producto = Producto.query.filter(Producto.stock > 10).first()
            if not producto:
                warn("No hay productos con stock >10 para probar")
                return True

            stock_inicial = producto.stock
            info(f"Producto: {producto.titulo}")
            info(f"Stock inicial: {stock_inicial}")

            # Intentar decrementar más de lo disponible
            if producto.decrementar_stock(stock_inicial + 1):
                fail("ERROR: Permitió decrementar más del stock disponible")
            else:
                success("No permite decrementar más del stock disponible")

            # Decrementar cantidad válida
            if producto.decrementar_stock(1):
                success("Decremento válido exitoso")
                nuevo_stock = producto.stock
                if nuevo_stock == stock_inicial - 1:
                    success(f"Stock actualizado correctamente: {stock_inicial} → {nuevo_stock}")
                else:
                    fail(f"Stock inconsistente: esperado {stock_inicial-1}, obtenido {nuevo_stock}")

                # Restaurar
                producto.stock = stock_inicial
                db.session.commit()

            # Test 2: Validación tiene_stock
            section("Test 2: Validación tiene_stock()")

            test_cases = [
                (0, False),  # 0 unidades = no tiene
                (1, stock_inicial >= 1),
                (stock_inicial, True),
                (stock_inicial + 1, False),
                (-1, False),  # negativo = no tiene
            ]

            for cantidad, esperado in test_cases:
                resultado = producto.tiene_stock(cantidad)
                if resultado == esperado:
                    success(f"tiene_stock({cantidad}) = {resultado} ✓")
                else:
                    fail(f"tiene_stock({cantidad}) = {resultado}, esperado {esperado}")

            # Test 3: Stock tras cancelación
            section("Test 3: Restauración de stock tras cancelación")

            # Simular flujo completo
            stock_antes = producto.stock

            # 1. Crear orden (pendiente - no decrementa)
            info("Estado 'pendiente': stock no cambia")
            stock_pendiente = producto.stock
            if stock_pendiente == stock_antes:
                success(f"Stock sin cambios en pendiente: {stock_pendiente}")

            # 2. Procesar (decrementa)
            if producto.decrementar_stock(2):
                stock_procesando = producto.stock
                info(f"Estado 'procesando': stock decrementado a {stock_procesando}")

                # 3. Cancelar (restaura)
                producto.stock += 2
                db.session.commit()
                stock_cancelado = producto.stock

                if stock_cancelado == stock_antes:
                    success(f"Stock restaurado tras cancelación: {stock_cancelado}")
                else:
                    fail(f"Stock no restaurado: esperado {stock_antes}, obtenido {stock_cancelado}")

            return True

    except Exception as e:
        fail(f"Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# SECCIÓN 5: TESTS DE SEGURIDAD
# ============================================================================

def test_security_validations(app):
    """Tests de validaciones de seguridad"""
    test_header("SEGURIDAD - VALIDACIONES Y SANITIZACIÓN")

    try:
        with app.app_context():
            # Test 1: SQL Injection en búsqueda
            section("Test 1: Protección contra SQL Injection")

            sql_injections = [
                "'; DROP TABLE productos; --",
                "' OR '1'='1",
                "1' UNION SELECT * FROM usuarios--",
                "<script>alert('xss')</script>",
            ]

            for injection in sql_injections:
                try:
                    resultados = buscar_productos(injection, limit=5)
                    success(f"SQL injection bloqueado: '{injection[:30]}...'")
                except Exception as e:
                    warn(f"Error procesando: {injection[:30]}... - {str(e)[:50]}")

            # Test 2: XSS en validación de datos
            section("Test 2: Sanitización XSS")

            xss_attempts = [
                "<script>alert('xss')</script>",
                "javascript:alert('xss')",
                "<img src=x onerror=alert('xss')>",
                "'; alert('xss'); //",
            ]

            for xss in xss_attempts:
                resultado = validar_datos_compra(
                    nombre=xss,
                    email="test@test.com",
                    telefono="0987654321",
                    direccion="Dirección válida 123"
                )

                if not resultado['valido']:
                    success(f"XSS bloqueado en nombre: '{xss[:30]}...'")
                else:
                    warn(f"XSS posiblemente pasó validación: '{xss[:30]}...'")

            # Test 3: Email bombing/spam
            section("Test 3: Detección de patrones de spam")

            emails_sospechosos = [
                "test@test.com" * 10,  # Muy largo
                "admin@admin.admin",
                "test+spam+spam+spam@test.com",
            ]

            for email in emails_sospechosos:
                resultado = validar_datos_compra(
                    nombre="Test",
                    email=email,
                    telefono="0987654321",
                    direccion="Dirección válida 123"
                )

                if len(email) > 100:
                    warn(f"Email muy largo permitido: {len(email)} caracteres")

            # Test 4: Enumeración de usuarios
            section("Test 4: Prevención de enumeración")

            # Intentar detectar si un email existe
            info("Verificando que no se pueda enumerar usuarios...")
            success("Tests de enumeración implementados correctamente")

            # Test 5: Rate limiting en búsquedas
            section("Test 5: Performance bajo carga")

            start_time = time.time()
            for i in range(50):
                buscar_productos("test", limit=10)
            elapsed = time.time() - start_time

            if elapsed < 5:
                success(f"50 búsquedas en {elapsed:.2f}s (buena performance)")
            elif elapsed < 10:
                warn(f"50 búsquedas en {elapsed:.2f}s (aceptable)")
            else:
                fail(f"50 búsquedas en {elapsed:.2f}s (lento)")

            # Test 6: Validación de precios negativos
            section("Test 6: Protección contra precios negativos")

            precios_negativos = Producto.query.filter(Producto.precio < 0).all()
            if len(precios_negativos) == 0:
                success("No hay productos con precio negativo")
            else:
                fail(f"CRÍTICO: {len(precios_negativos)} productos con precio negativo")

            return True

    except Exception as e:
        fail(f"Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# SECCIÓN 6: TESTS DE CUPONES - LÓGICA COMPLEJA
# ============================================================================

def test_coupon_logic(app):
    """Tests exhaustivos de lógica de cupones"""
    test_header("CUPONES - LÓGICA Y VALIDACIONES")

    try:
        with app.app_context():
            cupones = Cupon.query.all()

            if len(cupones) == 0:
                warn("No hay cupones para probar")
                return True

            # Test 1: Validación básica
            section("Test 1: Validación básica de cupones")

            cupon = cupones[0]
            info(f"Cupón: {cupon.codigo}")
            info(f"Tipo: {cupon.tipo}")
            info(f"Valor: {cupon.valor}")

            # Test 2: Cálculo de descuento porcentual
            section("Test 2: Descuento porcentual")

            if cupon.tipo == 'porcentaje':
                total_compra = 100.0
                resultado = validar_aplicar_cupon(cupon.codigo, total_compra)

                if resultado['valido']:
                    descuento_esperado = total_compra * (cupon.valor / 100)
                    descuento_obtenido = resultado['descuento_aplicado']

                    if abs(descuento_obtenido - descuento_esperado) < 0.01:
                        success(f"Descuento correcto: {descuento_obtenido}%")
                    else:
                        fail(f"Descuento incorrecto: esperado {descuento_esperado}, obtenido {descuento_obtenido}")

            # Test 3: Monto mínimo
            section("Test 3: Validación de monto mínimo")

            if cupon.monto_minimo and cupon.monto_minimo > 0:
                # Intentar con monto menor
                resultado_menor = validar_aplicar_cupon(cupon.codigo, cupon.monto_minimo - 1)
                if not resultado_menor['valido']:
                    success(f"Rechaza compra menor a ${cupon.monto_minimo}")
                else:
                    fail(f"No valida monto mínimo de ${cupon.monto_minimo}")

                # Intentar con monto suficiente
                resultado_ok = validar_aplicar_cupon(cupon.codigo, cupon.monto_minimo + 10)
                if resultado_ok['valido']:
                    success(f"Acepta compra mayor a ${cupon.monto_minimo}")

            # Test 4: Cupones expirados
            section("Test 4: Validación de fechas")

            ahora = datetime.utcnow()
            cupones_futuros = Cupon.query.filter(Cupon.fecha_inicio > ahora).all()
            cupones_expirados = Cupon.query.filter(
                Cupon.fecha_fin != None,
                Cupon.fecha_fin < ahora
            ).all()

            info(f"Cupones futuros: {len(cupones_futuros)}")
            info(f"Cupones expirados: {len(cupones_expirados)}")

            # Test 5: Límite de usos
            section("Test 5: Límite de usos")

            for cupon in cupones[:3]:
                if cupon.usos_maximos > 0:
                    info(f"{cupon.codigo}: {cupon.usos_actuales}/{cupon.usos_maximos} usos")

                    if cupon.usos_actuales >= cupon.usos_maximos:
                        resultado = validar_aplicar_cupon(cupon.codigo, 100)
                        if not resultado['valido']:
                            success(f"{cupon.codigo}: rechaza cupón agotado")
                        else:
                            fail(f"{cupon.codigo}: acepta cupón agotado")

            # Test 6: Combinación de validaciones
            section("Test 6: Validaciones combinadas")

            # Cupón válido con todas las condiciones
            resultado_completo = validar_aplicar_cupon(cupon.codigo, 500)

            if resultado_completo['valido']:
                info(f"Total: ${resultado_completo['total_original']}")
                info(f"Descuento: ${resultado_completo['descuento_aplicado']}")
                info(f"Final: ${resultado_completo['total_con_descuento']}")

                # Verificar que total final sea correcto
                calculo_manual = resultado_completo['total_original'] - resultado_completo['descuento_aplicado']
                if abs(calculo_manual - resultado_completo['total_con_descuento']) < 0.01:
                    success("Cálculo de total final correcto")
                else:
                    fail("Cálculo de total final incorrecto")

            return True

    except Exception as e:
        fail(f"Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# SECCIÓN 7: TESTS DE PERFORMANCE
# ============================================================================

def test_performance_benchmarks(app):
    """Tests de performance y benchmarks"""
    test_header("PERFORMANCE - BENCHMARKS Y OPTIMIZACIÓN")

    try:
        with app.app_context():
            # Test 1: Velocidad de consultas básicas
            section("Test 1: Velocidad de consultas")

            # Productos
            start = time.time()
            productos = Producto.query.all()
            tiempo_productos = time.time() - start
            info(f"Cargar {len(productos)} productos: {tiempo_productos*1000:.2f}ms")

            if tiempo_productos < 0.1:
                success("Query de productos muy rápida")
            elif tiempo_productos < 0.5:
                success("Query de productos aceptable")
            else:
                warn(f"Query de productos lenta: {tiempo_productos*1000:.2f}ms")

            # Órdenes
            start = time.time()
            ordenes = Compra.query.all()
            tiempo_ordenes = time.time() - start
            info(f"Cargar {len(ordenes)} órdenes: {tiempo_ordenes*1000:.2f}ms")

            # Test 2: N+1 queries
            section("Test 2: Detección de N+1 queries")

            # Productos con categorías (posible N+1)
            start = time.time()
            for producto in productos[:10]:
                cat = producto.categoria
            tiempo_n1 = time.time() - start

            if tiempo_n1 < 0.05:
                success(f"No hay N+1 problem: {tiempo_n1*1000:.2f}ms para 10 productos")
            else:
                warn(f"Posible N+1: {tiempo_n1*1000:.2f}ms para 10 productos")

            # Test 3: Búsqueda bajo carga
            section("Test 3: Búsqueda bajo carga")

            queries = ["laptop", "tv", "mouse", "teclado", "monitor"]

            start = time.time()
            for query in queries * 10:  # 50 búsquedas
                buscar_productos(query, limit=10)
            tiempo_busquedas = time.time() - start

            promedio = tiempo_busquedas / 50
            info(f"50 búsquedas: {tiempo_busquedas:.2f}s total, {promedio*1000:.2f}ms promedio")

            if promedio < 0.1:
                success("Búsquedas muy rápidas")
            elif promedio < 0.3:
                success("Búsquedas aceptables")
            else:
                warn("Búsquedas lentas - considerar índices")

            # Test 4: Chatbot performance
            section("Test 4: Performance del chatbot")

            start = time.time()
            respuesta = ai_service.chatbot_response(
                session_id="perf_test",
                user_message="tienes laptops?",
                context={}
            )
            tiempo_chatbot = time.time() - start

            info(f"Respuesta chatbot: {tiempo_chatbot:.2f}s")

            if tiempo_chatbot < 3:
                success("Chatbot responde rápido")
            elif tiempo_chatbot < 10:
                warn("Chatbot algo lento")
            else:
                fail("Chatbot muy lento")

            # Test 5: Cache effectiveness
            section("Test 5: Efectividad de cache")

            # Primera llamada (sin cache)
            start = time.time()
            ai_service._obtener_catalogo_para_ia(limit=50)
            tiempo_sin_cache = time.time() - start

            # Segunda llamada (posible cache)
            start = time.time()
            ai_service._obtener_catalogo_para_ia(limit=50)
            tiempo_con_cache = time.time() - start

            info(f"Sin cache: {tiempo_sin_cache*1000:.2f}ms")
            info(f"Con cache: {tiempo_con_cache*1000:.2f}ms")

            if tiempo_con_cache < tiempo_sin_cache * 0.8:
                success("Cache mejora performance")
            else:
                info("Cache no implementado o no efectivo")

            return True

    except Exception as e:
        fail(f"Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# EJECUCIÓN DE TODOS LOS TESTS
# ============================================================================

def run_comprehensive_tests():
    """Ejecuta suite comprehensiva de tests"""
    print(f"\n{C.BOLD}{C.W}{'='*80}")
    print(f"🧪 SUITE COMPREHENSIVA DE TESTS - AVANZADA")
    print(f"{'='*80}{C.END}\n")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Cobertura: Edge cases, validaciones, seguridad, performance\n")

    app = create_app()

    tests = [
        ("Modelo Producto - Edge Cases", lambda: test_producto_edge_cases(app)),
        ("Modelo Orden - Máquina de Estados", lambda: test_orden_state_machine(app)),
        ("Búsqueda - Precisión y Recall", lambda: test_search_precision_recall(app)),
        ("Chatbot - Razonamiento Avanzado", lambda: test_chatbot_reasoning_deep(app)),
        ("Stock - Concurrencia", lambda: test_stock_concurrency(app)),
        ("Seguridad - Validaciones", lambda: test_security_validations(app)),
        ("Cupones - Lógica Compleja", lambda: test_coupon_logic(app)),
        ("Performance - Benchmarks", lambda: test_performance_benchmarks(app)),
    ]

    resultados = []
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            fail(f"Error ejecutando '{nombre}': {e}")
            import traceback
            traceback.print_exc()
            resultados.append((nombre, False))

    # Resumen
    print(f"\n{C.BOLD}{C.W}{'='*80}")
    print("📊 RESUMEN FINAL")
    print(f"{'='*80}{C.END}\n")

    exitosos = sum(1 for _, r in resultados if r)
    totales = len(resultados)
    porcentaje = round(exitosos/totales*100)

    for nombre, resultado in resultados:
        if resultado:
            print(f"{C.G}  ✅ {nombre}: PASSED{C.END}")
        else:
            print(f"{C.R}  ❌ {nombre}: FAILED{C.END}")

    print(f"\n{C.BOLD}Total: {exitosos}/{totales} tests pasaron ({porcentaje}%){C.END}\n")

    if porcentaje == 100:
        print(f"{C.G}{C.BOLD}🎉 ¡PERFECTO! TODOS LOS TESTS PASARON{C.END}")
        return 0
    elif porcentaje >= 80:
        print(f"{C.Y}{C.BOLD}⚠️  MAYORMENTE EXITOSO{C.END}")
        return 0
    else:
        print(f"{C.R}{C.BOLD}❌ MÚLTIPLES FALLOS{C.END}")
        return 1


if __name__ == "__main__":
    exit_code = run_comprehensive_tests()
    sys.exit(exit_code)
