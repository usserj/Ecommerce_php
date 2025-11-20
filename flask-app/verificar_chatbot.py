#!/usr/bin/env python
"""
Script de verificación rápida del chatbot
Ejecutar después de reiniciar Flask para confirmar que funciona
"""
import requests
import json
import sys

# Colores para terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}ℹ️  {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def test_chatbot():
    """Prueba el endpoint del chatbot"""
    url = "http://127.0.0.1:5000/api/ai/chat"

    print_info("Probando chatbot...")
    print(f"URL: {url}")

    # Payload de prueba
    payload = {
        "message": "Hola, ¿me puedes ayudar?",
        "context": {}
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            if data.get('success'):
                print_success("¡Chatbot funcionando correctamente!")
                print(f"\n{BLUE}Respuesta del chatbot:{RESET}")
                print(f'"{data.get("response", "")}"')
                return True
            else:
                print_error("Chatbot devolvió success=false")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                return False

        elif response.status_code == 400:
            print_error("Error 400 - Bad Request")
            print_warning("El problema de CSRF debería estar resuelto.")
            print_warning("Asegúrate de haber reiniciado el servidor Flask.")
            try:
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            except:
                print(response.text[:500])
            return False

        else:
            print_error(f"Status code inesperado: {response.status_code}")
            try:
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            except:
                print(response.text[:500])
            return False

    except requests.exceptions.ConnectionError:
        print_error("No se pudo conectar al servidor Flask")
        print_info("Asegúrate de que Flask esté corriendo en http://127.0.0.1:5000")
        print_info("Ejecuta: python run.py")
        return False

    except Exception as e:
        print_error(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_health():
    """Prueba el endpoint de health check"""
    url = "http://127.0.0.1:5000/api/ai/health"

    print_info("Probando health check...")

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print_success("Health check OK")

            if data.get('api_connection') == 'OK':
                print_success("API de DeepSeek conectada correctamente")
            else:
                print_warning(f"API connection: {data.get('api_connection')}")

            return True
        else:
            print_error(f"Health check falló: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print_error("Servidor Flask no disponible")
        return False

    except Exception as e:
        print_error(f"Error: {e}")
        return False

def main():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  🤖 VERIFICACIÓN DE CHATBOT DE IA{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    # Test 1: Health Check
    print(f"\n{BLUE}[1/2] Health Check{RESET}")
    print("-" * 60)
    health_ok = test_health()

    # Test 2: Chatbot
    print(f"\n{BLUE}[2/2] Chatbot{RESET}")
    print("-" * 60)
    chatbot_ok = test_chatbot()

    # Resumen
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  RESUMEN{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    if health_ok and chatbot_ok:
        print_success("¡Todos los tests pasaron!")
        print_info("El chatbot está listo para usar en el frontend")
        print(f"\n{BLUE}Pruébalo en tu navegador:{RESET}")
        print("http://127.0.0.1:5000")
        return 0
    else:
        print_error("Algunos tests fallaron")
        print_info("\nPasos para solucionar:")
        print("1. Asegúrate de que Flask esté corriendo: python run.py")
        print("2. Verifica que no haya errores en los logs de Flask")
        print("3. Si el error persiste, revisa los logs arriba")
        return 1

if __name__ == '__main__':
    sys.exit(main())
