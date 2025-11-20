#!/usr/bin/env python
"""
🔍 DEBUG COMPLETO DE INTEGRACIÓN DE IA

Este script valida TODAS las funcionalidades de IA:
1. Chatbot de ventas 24/7
2. Recomendador de productos
3. Generador de descripciones
4. Análisis de reviews
5. Búsqueda inteligente

Requiere: Flask corriendo en http://127.0.0.1:5000
"""

import requests
import json
import sys
from datetime import datetime

# Colores para terminal
class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

BASE_URL = "http://127.0.0.1:5000"

def print_header(title):
    print(f"\n{Color.CYAN}{'='*70}{Color.RESET}")
    print(f"{Color.BOLD}{Color.BLUE}{title.center(70)}{Color.RESET}")
    print(f"{Color.CYAN}{'='*70}{Color.RESET}\n")

def print_success(msg):
    print(f"{Color.GREEN}✅ {msg}{Color.RESET}")

def print_error(msg):
    print(f"{Color.RED}❌ {msg}{Color.RESET}")

def print_warning(msg):
    print(f"{Color.YELLOW}⚠️  {msg}{Color.RESET}")

def print_info(msg):
    print(f"{Color.BLUE}ℹ️  {msg}{Color.RESET}")

def print_test(name):
    print(f"\n{Color.MAGENTA}🧪 TEST: {name}{Color.RESET}")
    print(f"{Color.CYAN}{'-'*70}{Color.RESET}")


# =============================================================================
# TEST 0: Health Check y Configuración
# =============================================================================

def test_health_check():
    """Verifica que la API de IA está configurada correctamente"""
    print_test("Health Check de API IA")

    url = f"{BASE_URL}/api/ai/health"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            print_info(f"Status: {data.get('status')}")
            print_info(f"Service: {data.get('service')}")

            config = data.get('config', {})
            print_info(f"API Key: {config.get('api_key', 'N/A')}")
            print_info(f"API URL: {config.get('api_url', 'N/A')}")
            print_info(f"Model: {config.get('model', 'N/A')}")

            api_conn = data.get('api_connection')
            if api_conn == 'OK':
                print_success(f"API Connection: {api_conn}")
                print_success("Health check pasó correctamente")
                return True
            else:
                print_error(f"API Connection: {api_conn}")
                print_error("DeepSeek API no está respondiendo")
                return False
        else:
            print_error(f"Status code: {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error: {e}")
        return False


# =============================================================================
# TEST 1: Chatbot de Ventas 24/7
# =============================================================================

def test_chatbot():
    """Prueba el chatbot con diferentes tipos de preguntas"""
    print_test("1. Chatbot de Ventas 24/7")

    url = f"{BASE_URL}/api/ai/chat"

    # Diferentes escenarios de prueba
    test_cases = [
        {
            "name": "Saludo básico",
            "message": "Hola, ¿cómo estás?",
            "expect_keywords": ["hola", "ayud"]
        },
        {
            "name": "Pregunta sobre envíos",
            "message": "¿Hacen envíos a todo Ecuador?",
            "expect_keywords": ["ecuador", "envío"]
        },
        {
            "name": "Pregunta sobre métodos de pago",
            "message": "¿Qué métodos de pago aceptan?",
            "expect_keywords": ["pago", "paypal"]
        },
        {
            "name": "Pregunta sobre garantía",
            "message": "¿Tienen garantía los productos?",
            "expect_keywords": ["garantía", "días"]
        }
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{Color.YELLOW}Caso {i}: {test_case['name']}{Color.RESET}")
        print(f"Pregunta: \"{test_case['message']}\"")

        payload = {
            "message": test_case['message'],
            "context": {}
        }

        try:
            response = requests.post(url, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()

                if data.get('success'):
                    bot_response = data.get('response', '')
                    print(f"Respuesta: \"{bot_response[:150]}...\"" if len(bot_response) > 150 else f"Respuesta: \"{bot_response}\"")

                    # Verificar keywords esperadas
                    found_keywords = [kw for kw in test_case['expect_keywords']
                                     if kw.lower() in bot_response.lower()]

                    if found_keywords:
                        print_success(f"Keywords encontradas: {', '.join(found_keywords)}")
                        results.append(True)
                    else:
                        print_warning(f"No se encontraron keywords esperadas: {test_case['expect_keywords']}")
                        results.append(False)
                else:
                    print_error(f"Success=false: {data.get('error')}")
                    results.append(False)
            else:
                print_error(f"Status {response.status_code}")
                results.append(False)

        except Exception as e:
            print_error(f"Error: {e}")
            results.append(False)

    passed = sum(results)
    total = len(results)

    print(f"\n{Color.BOLD}Resultado: {passed}/{total} casos pasaron{Color.RESET}")
    return passed == total


# =============================================================================
# TEST 2: Recomendador de Productos
# =============================================================================

def test_recomendador():
    """Prueba el recomendador de productos"""
    print_test("2. Recomendador de Productos Inteligente")

    # Primero necesitamos obtener un producto de prueba
    url_productos = f"{BASE_URL}/api/productos"

    try:
        # Intentar obtener lista de productos
        print_info("Obteniendo productos de la tienda...")
        response = requests.get(url_productos, timeout=10)

        if response.status_code == 200:
            # Si hay productos, usar el primero
            productos = response.json()
            if productos and len(productos) > 0:
                producto_id = productos[0].get('id')
                producto_nombre = productos[0].get('nombre', 'Producto')
                print_info(f"Usando producto: ID={producto_id}, Nombre={producto_nombre}")
            else:
                print_warning("No hay productos en la BD, usando ID=1 por defecto")
                producto_id = 1
        else:
            print_warning(f"No se pudo obtener productos (status {response.status_code}), usando ID=1")
            producto_id = 1
    except:
        print_warning("Error al obtener productos, usando ID=1")
        producto_id = 1

    # Probar endpoint de recomendaciones
    url_recomendaciones = f"{BASE_URL}/api/ai/recomendaciones/{producto_id}"

    try:
        print_info(f"Solicitando recomendaciones para producto ID={producto_id}...")
        response = requests.get(url_recomendaciones, timeout=30)

        if response.status_code == 200:
            data = response.json()

            if data.get('success'):
                recs = data.get('recomendaciones', {})

                complementarios = recs.get('complementarios', [])
                similares = recs.get('similares', [])
                frecuentes = recs.get('frecuentes_juntos', [])

                print_info(f"Productos complementarios: {len(complementarios)} sugerencias")
                print_info(f"Productos similares: {len(similares)} sugerencias")
                print_info(f"Frecuentemente juntos: {len(frecuentes)} sugerencias")

                if complementarios or similares or frecuentes:
                    print_success("Recomendaciones generadas correctamente")
                    return True
                else:
                    print_warning("No se generaron recomendaciones (puede ser esperado si no hay suficientes productos)")
                    return True  # No es un error crítico
            else:
                print_error(f"Success=false: {data.get('error')}")
                return False
        else:
            print_error(f"Status {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error: {e}")
        return False


# =============================================================================
# TEST 3: Generador de Descripciones
# =============================================================================

def test_generador_descripciones():
    """Prueba el generador de descripciones de productos"""
    print_test("3. Generador de Descripciones de Productos")

    url = f"{BASE_URL}/api/ai/generar-descripcion"

    # Datos de prueba
    payload = {
        "nombre": "Smartphone Samsung Galaxy S23",
        "categoria": "Electrónica",
        "precio": 899.99,
        "caracteristicas": [
            "Pantalla AMOLED 6.1 pulgadas",
            "Cámara 50MP",
            "Procesador Snapdragon 8 Gen 2",
            "Batería 3900mAh"
        ]
    }

    try:
        print_info("Generando descripciones para producto de prueba...")
        print_info(f"Producto: {payload['nombre']}")

        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()

            if data.get('success'):
                desc_corta = data.get('descripcion_corta', '')
                desc_larga = data.get('descripcion_larga', '')

                print(f"\n{Color.YELLOW}Descripción Corta:{Color.RESET}")
                print(f"{desc_corta}\n")

                print(f"{Color.YELLOW}Descripción Larga:{Color.RESET}")
                print(f"{desc_larga[:200]}..." if len(desc_larga) > 200 else desc_larga)

                if desc_corta and desc_larga:
                    print_success("Descripciones generadas correctamente")
                    return True
                else:
                    print_error("Descripciones vacías")
                    return False
            else:
                print_error(f"Success=false: {data.get('error')}")
                return False
        else:
            print_error(f"Status {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error: {e}")
        return False


# =============================================================================
# TEST 4: Análisis de Reviews
# =============================================================================

def test_analisis_reviews():
    """Prueba el análisis de reviews con IA"""
    print_test("4. Análisis de Reviews con IA")

    url = f"{BASE_URL}/api/ai/analizar-reviews"

    # Reviews de prueba
    payload = {
        "producto_id": 1,
        "reviews": [
            {
                "texto": "Excelente producto, llegó rápido y en perfectas condiciones. Muy recomendado!",
                "calificacion": 5
            },
            {
                "texto": "Buena calidad pero el precio es un poco alto para lo que ofrece",
                "calificacion": 4
            },
            {
                "texto": "No me gustó, la batería dura muy poco y el servicio al cliente es pésimo",
                "calificacion": 2
            },
            {
                "texto": "Cumple con lo prometido, buen producto en general",
                "calificacion": 4
            }
        ]
    }

    try:
        print_info(f"Analizando {len(payload['reviews'])} reviews...")

        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()

            if data.get('success'):
                analisis = data.get('analisis', {})

                print_info(f"Sentimiento: {analisis.get('sentimiento', 'N/A')}")
                print_info(f"Score de Calidad: {analisis.get('score_calidad', 'N/A')}/100")

                positivos = analisis.get('aspectos_positivos', [])
                negativos = analisis.get('aspectos_negativos', [])
                recomendaciones = analisis.get('recomendaciones', [])

                print(f"\n{Color.GREEN}Aspectos Positivos:{Color.RESET}")
                for asp in positivos:
                    print(f"  • {asp}")

                print(f"\n{Color.RED}Aspectos Negativos:{Color.RESET}")
                for asp in negativos:
                    print(f"  • {asp}")

                print(f"\n{Color.YELLOW}Recomendaciones:{Color.RESET}")
                for rec in recomendaciones:
                    print(f"  • {rec}")

                if analisis.get('sentimiento') and analisis.get('score_calidad'):
                    print_success("Análisis de reviews completado")
                    return True
                else:
                    print_error("Análisis incompleto")
                    return False
            else:
                print_error(f"Success=false: {data.get('error')}")
                return False
        else:
            print_error(f"Status {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error: {e}")
        return False


# =============================================================================
# TEST 5: Búsqueda Inteligente
# =============================================================================

def test_busqueda_inteligente():
    """Prueba la búsqueda inteligente con NLP"""
    print_test("5. Búsqueda Inteligente con NLP")

    url = f"{BASE_URL}/api/ai/busqueda-inteligente"

    # Casos de prueba de búsqueda
    test_cases = [
        {
            "query": "celular barato con buena cámara",
            "description": "Búsqueda con intención de compra"
        },
        {
            "query": "laptop para programar",
            "description": "Búsqueda por uso específico"
        },
        {
            "query": "regalo para mamá",
            "description": "Búsqueda contextual"
        }
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{Color.YELLOW}Búsqueda {i}: {test_case['description']}{Color.RESET}")
        print(f"Query: \"{test_case['query']}\"")

        payload = {"query": test_case['query']}

        try:
            response = requests.post(url, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()

                if data.get('success'):
                    resultado = data.get('resultado', {})

                    intencion = resultado.get('intencion', 'N/A')
                    categorias = resultado.get('categorias_sugeridas', [])
                    filtros = resultado.get('filtros_sugeridos', {})

                    print_info(f"Intención detectada: {intencion}")
                    print_info(f"Categorías sugeridas: {', '.join(categorias) if categorias else 'Ninguna'}")
                    print_info(f"Filtros: {json.dumps(filtros, ensure_ascii=False)}")

                    if intencion and intencion != 'N/A':
                        print_success("Búsqueda procesada correctamente")
                        results.append(True)
                    else:
                        print_warning("Intención no detectada")
                        results.append(False)
                else:
                    print_error(f"Success=false: {data.get('error')}")
                    results.append(False)
            else:
                print_error(f"Status {response.status_code}")
                results.append(False)

        except Exception as e:
            print_error(f"Error: {e}")
            results.append(False)

    passed = sum(results)
    total = len(results)

    print(f"\n{Color.BOLD}Resultado: {passed}/{total} búsquedas procesadas{Color.RESET}")
    return passed > 0  # Al menos una debe pasar


# =============================================================================
# MAIN
# =============================================================================

def main():
    print_header("🤖 DEBUG COMPLETO DE INTEGRACIÓN DE IA CON DEEPSEEK")

    print(f"{Color.CYAN}Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Color.RESET}")
    print(f"{Color.CYAN}Base URL: {BASE_URL}{Color.RESET}")

    # Primero verificar que Flask está corriendo
    try:
        requests.get(BASE_URL, timeout=2)
    except:
        print_error("\n❌ Flask no está corriendo en http://127.0.0.1:5000")
        print_info("Ejecuta: cd flask-app && python run.py")
        return 1

    # Ejecutar todos los tests
    results = {}

    print_header("INICIANDO TESTS")

    results['health'] = test_health_check()

    if not results['health']:
        print_error("\n⚠️  Health check falló. Revisa la configuración de DeepSeek API.")
        print_info("Continuando con tests de endpoints...")

    results['chatbot'] = test_chatbot()
    results['recomendador'] = test_recomendador()
    results['descripciones'] = test_generador_descripciones()
    results['reviews'] = test_analisis_reviews()
    results['busqueda'] = test_busqueda_inteligente()

    # Resumen final
    print_header("📊 RESUMEN DE RESULTADOS")

    tests = [
        ('Health Check', results['health']),
        ('Chatbot 24/7', results['chatbot']),
        ('Recomendador', results['recomendador']),
        ('Generador de Descripciones', results['descripciones']),
        ('Análisis de Reviews', results['reviews']),
        ('Búsqueda Inteligente', results['busqueda'])
    ]

    for name, passed in tests:
        status = f"{Color.GREEN}✅ PASS{Color.RESET}" if passed else f"{Color.RED}❌ FAIL{Color.RESET}"
        print(f"{name.ljust(30)} {status}")

    passed_count = sum(1 for _, p in tests if p)
    total_count = len(tests)

    print(f"\n{Color.BOLD}Total: {passed_count}/{total_count} tests pasaron{Color.RESET}")

    if passed_count == total_count:
        print_header("🎉 ¡TODOS LOS TESTS PASARON!")
        print_success("La integración de IA está funcionando correctamente")
        return 0
    else:
        print_header("⚠️  ALGUNOS TESTS FALLARON")
        print_warning(f"{total_count - passed_count} de {total_count} tests necesitan atención")
        print_info("\nRevisa los logs arriba para ver detalles de los errores")
        return 1


if __name__ == '__main__':
    sys.exit(main())
