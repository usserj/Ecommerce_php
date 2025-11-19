#!/usr/bin/env python
"""
Script para probar la API de IA directamente

Uso:
    python test_ai_api.py
"""

import requests
import json

# URL de la API (cambiar si es necesario)
BASE_URL = "http://127.0.0.1:5000"

def test_health():
    """Probar el endpoint de health"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)

    url = f"{BASE_URL}/api/ai/health"
    print(f"📡 GET {url}")

    try:
        response = requests.get(url, timeout=10)
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Respuesta:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_chat():
    """Probar el endpoint del chatbot"""
    print("\n" + "="*60)
    print("TEST 2: Chatbot")
    print("="*60)

    url = f"{BASE_URL}/api/ai/chat"
    print(f"📡 POST {url}")

    payload = {
        "message": "Hola, ¿cuál es tu nombre?",
        "context": {}
    }

    headers = {
        "Content-Type": "application/json"
    }

    print(f"📤 Payload:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )

        print(f"\n✅ Status: {response.status_code}")
        print(f"📄 Headers de respuesta:")
        print(f"  Content-Type: {response.headers.get('Content-Type')}")

        print(f"\n📥 Respuesta:")

        # Intentar parsear como JSON
        try:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return response.status_code == 200 and data.get('success', False)
        except json.JSONDecodeError:
            print(f"❌ No es JSON válido:")
            print(response.text[:500])
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_deepseek_direct():
    """Probar la API de DeepSeek directamente"""
    print("\n" + "="*60)
    print("TEST 3: DeepSeek API Directa")
    print("="*60)

    url = "https://api.deepseek.com/chat/completions"
    api_key = "sk-5967b2b9feb7438dadd1059f600094c9"

    print(f"📡 POST {url}")

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a test assistant."},
            {"role": "user", "content": "Say 'test successful' if you receive this."}
        ],
        "stream": False,
        "temperature": 0.7,
        "max_tokens": 50
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print(f"📤 Payload:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )

        print(f"\n✅ Status: {response.status_code}")
        print(f"📄 Respuesta:")

        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"❌ Error {response.status_code}:")
            print(response.text[:500])
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "🤖 TEST DE API DE INTELIGENCIA ARTIFICIAL")
    print("="*60)

    results = []

    # Test 1: Health Check
    results.append(("Health Check", test_health()))

    # Test 2: Chatbot
    results.append(("Chatbot", test_chat()))

    # Test 3: DeepSeek Directo
    results.append(("DeepSeek API", test_deepseek_direct()))

    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE TESTS")
    print("="*60)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    total = len(results)
    passed = sum(1 for _, r in results if r)

    print(f"\nTotal: {passed}/{total} tests pasados")

    if passed == total:
        print("\n🎉 ¡Todos los tests pasaron!")
    else:
        print("\n⚠️  Algunos tests fallaron. Revisa los logs arriba.")
