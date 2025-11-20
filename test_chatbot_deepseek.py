#!/usr/bin/env python3
"""
Script de prueba para verificar que el chatbot usa DeepSeek API
"""
import sys
import os

# Agregar ruta del proyecto al sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'flask-app'))

import requests
import json

def test_deepseek_api_direct():
    """Test directo a DeepSeek API"""
    print("=" * 80)
    print("TEST 1: Llamada directa a DeepSeek API")
    print("=" * 80)

    api_key = "sk-5967b2b9feb7438dadd1059f600094c9"
    api_url = "https://api.deepseek.com/chat/completions"

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Eres un asistente útil."},
            {"role": "user", "content": "Hola, ¿cómo estás?"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        print(f"📤 Enviando request a: {api_url}")
        print(f"🔑 API Key: {api_key[:20]}...")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")
        print()

        response = requests.post(api_url, headers=headers, json=payload, timeout=30)

        print(f"📥 Status Code: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        print()

        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            tokens_used = data.get('usage', {}).get('total_tokens', 0)

            print("✅ ÉXITO: DeepSeek API funciona correctamente")
            print(f"🤖 Respuesta: {content}")
            print(f"📊 Tokens usados: {tokens_used}")
            return True
        else:
            print(f"❌ ERROR: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"💥 EXCEPCIÓN: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_flask_ai_service():
    """Test del servicio de IA de Flask"""
    print("\n")
    print("=" * 80)
    print("TEST 2: Servicio de IA de Flask")
    print("=" * 80)

    try:
        from app import create_app
        from app.services.ai_service import ai_service

        app = create_app('development')

        with app.app_context():
            print("📝 Llamando a ai_service.chatbot_response()...")

            result = ai_service.chatbot_response(
                session_id="test-session-123",
                user_message="¿Tienen laptops disponibles?",
                context={},
                usuario_id=None
            )

            print(f"\n📊 Resultado del servicio:")
            print(f"  Success: {result['success']}")
            print(f"  Response: {result['response'][:200]}..." if len(result['response']) > 200 else f"  Response: {result['response']}")
            print(f"  Error: {result.get('error')}")

            if result['success']:
                print("\n✅ ÉXITO: El servicio de IA funciona correctamente")
                print("🤖 El chatbot SÍ está usando DeepSeek API")
                return True
            else:
                print(f"\n❌ ERROR: {result.get('error')}")
                return False

    except Exception as e:
        print(f"💥 EXCEPCIÓN: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_flask_endpoint():
    """Test del endpoint HTTP /api/ai/chat"""
    print("\n")
    print("=" * 80)
    print("TEST 3: Endpoint HTTP /api/ai/chat")
    print("=" * 80)
    print("⚠️  NOTA: Este test requiere que el servidor Flask esté corriendo")
    print("⚠️  Ejecuta: cd flask-app && python run.py")
    print()

    base_url = "http://localhost:5000"
    endpoint = f"{base_url}/api/ai/chat"

    # Primero verificar que el servidor esté corriendo
    try:
        health_check = requests.get(f"{base_url}/health", timeout=5)
        if health_check.status_code != 200:
            print(f"⚠️  El servidor Flask no responde en {base_url}")
            print(f"   Por favor ejecuta: cd flask-app && python run.py")
            return None
    except requests.exceptions.ConnectionError:
        print(f"⚠️  No se puede conectar al servidor en {base_url}")
        print(f"   Por favor ejecuta: cd flask-app && python run.py")
        return None

    # Test del chatbot endpoint
    payload = {
        "message": "¿Qué productos tienen disponibles?",
        "context": {}
    }

    try:
        print(f"📤 Enviando POST a: {endpoint}")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")
        print()

        response = requests.post(endpoint, json=payload, timeout=30)

        print(f"📥 Status Code: {response.status_code}")
        print(f"📥 Content-Type: {response.headers.get('Content-Type')}")
        print()

        if response.status_code == 200:
            data = response.json()

            print("✅ ÉXITO: Endpoint funciona correctamente")
            print(f"🤖 Success: {data.get('success')}")
            print(f"🤖 Respuesta: {data.get('response', '')[:200]}...")
            print(f"🕐 Timestamp: {data.get('timestamp')}")

            if data.get('success'):
                print("\n✅ El chatbot en el endpoint SÍ está usando DeepSeek API")
                return True
            else:
                print(f"\n⚠️  El endpoint respondió pero con success=False")
                print(f"   Error: {data.get('error')}")
                return False
        else:
            print(f"❌ ERROR: Status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False

    except Exception as e:
        print(f"💥 EXCEPCIÓN: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n")
    print("🤖" * 40)
    print("VERIFICACIÓN DE CHATBOT CON DEEPSEEK API")
    print("🤖" * 40)
    print()

    results = []

    # Test 1: DeepSeek API directo
    results.append(("DeepSeek API Directo", test_deepseek_api_direct()))

    # Test 2: Servicio de IA de Flask
    results.append(("Servicio de IA Flask", test_flask_ai_service()))

    # Test 3: Endpoint HTTP
    result_endpoint = test_flask_endpoint()
    if result_endpoint is not None:
        results.append(("Endpoint HTTP /api/ai/chat", result_endpoint))

    # Resumen
    print("\n")
    print("=" * 80)
    print("RESUMEN DE PRUEBAS")
    print("=" * 80)

    all_passed = True
    for name, result in results:
        if result is True:
            print(f"✅ {name}: PASÓ")
        elif result is False:
            print(f"❌ {name}: FALLÓ")
            all_passed = False
        else:
            print(f"⚠️  {name}: NO EJECUTADO")

    print()
    if all_passed and len([r for r in results if r[1] is True]) > 0:
        print("🎉" * 40)
        print("¡ÉXITO! El chatbot SÍ está usando DeepSeek API correctamente")
        print("🎉" * 40)
        print()
        print("SIGUIENTE PASO:")
        print("1. Abre el navegador en http://localhost:5000")
        print("2. Abre la consola del navegador (F12)")
        print("3. Haz clic en el botón del chatbot")
        print("4. Haz clic en el ícono de papelera (🗑️) para LIMPIAR el historial")
        print("5. Escribe un mensaje nuevo al chatbot")
        print("6. Verifica en la consola que dice '📤 Enviando mensaje al chatbot'")
        print("7. Verifica que la respuesta sea del API y no una respuesta genérica")
    else:
        print("❌" * 40)
        print("HAY PROBLEMAS CON EL CHATBOT")
        print("❌" * 40)
        print()
        print("Revisa los errores arriba para más detalles")

    print()


if __name__ == "__main__":
    main()
