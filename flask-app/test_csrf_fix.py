#!/usr/bin/env python
"""
Test para verificar que CSRF está deshabilitado en endpoints de IA
"""
import requests
import json
import sys

def test_chatbot_sin_csrf():
    """Prueba que el endpoint de chatbot acepta POST sin token CSRF"""
    url = "http://127.0.0.1:5000/api/ai/chat"

    print("=" * 60)
    print("TEST: Chatbot sin token CSRF")
    print("=" * 60)
    print(f"URL: {url}\n")

    payload = {
        "message": "Hola, ¿funciona sin CSRF?",
        "context": {}
    }

    headers = {
        'Content-Type': 'application/json'
        # NOTA: NO incluimos X-CSRFToken header
    }

    try:
        print("📤 Enviando POST sin token CSRF...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ SUCCESS: Endpoint acepta POST sin CSRF")
            data = response.json()
            if data.get('success'):
                print(f"✅ Respuesta del chatbot:")
                print(f'   "{data.get("response", "")[:100]}..."')
                return True
            else:
                print(f"⚠️  Response success=false: {data}")
                return False

        elif response.status_code == 400:
            print("❌ FAIL: Error 400 - CSRF todavía está bloqueando")
            print("\nRespuesta del servidor:")
            try:
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            except:
                print(response.text[:500])
            print("\n⚠️  ACCIÓN REQUERIDA:")
            print("   1. Asegúrate de haber REINICIADO Flask después de los cambios")
            print("   2. Ejecuta: Ctrl+C en el servidor Flask")
            print("   3. Ejecuta: python run.py")
            print("   4. Vuelve a ejecutar este test")
            return False

        else:
            print(f"❌ Status inesperado: {response.status_code}")
            print(response.text[:500])
            return False

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se pudo conectar al servidor Flask")
        print("\n⚠️  ACCIÓN REQUERIDA:")
        print("   1. Asegúrate de que Flask esté corriendo")
        print("   2. Ejecuta en otra terminal: cd flask-app && python run.py")
        print("   3. Espera a que inicie completamente")
        print("   4. Vuelve a ejecutar este test")
        return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n🧪 VERIFICACIÓN DE FIX DE CSRF")
    print("Este test verifica que los endpoints de IA aceptan POST sin token CSRF\n")

    success = test_chatbot_sin_csrf()

    print("\n" + "=" * 60)
    if success:
        print("✅ ¡TEST PASADO!")
        print("=" * 60)
        print("\nEl chatbot ahora funciona correctamente sin CSRF.")
        print("Pruébalo en el navegador: http://127.0.0.1:5000")
        return 0
    else:
        print("❌ TEST FALLÓ")
        print("=" * 60)
        print("\nEl error CSRF persiste. Revisa los mensajes arriba.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
