#!/usr/bin/env python
"""
Simple test server to verify AI endpoints work
Run with: python test_server.py
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# DeepSeek Configuration
DEEPSEEK_API_KEY = 'sk-5967b2b9feb7438dadd1059f600094c9'
DEEPSEEK_API_URL = 'https://api.deepseek.com/chat/completions'
DEEPSEEK_MODEL = 'deepseek-chat'


def call_deepseek_api(messages, max_tokens=500, temperature=0.7):
    """Call DeepSeek API"""
    try:
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': DEEPSEEK_MODEL,
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'stream': False
        }

        logger.info(f"📡 Calling DeepSeek API: {DEEPSEEK_API_URL}")
        logger.debug(f"Payload: {payload}")

        response = requests.post(
            DEEPSEEK_API_URL,
            json=payload,
            headers=headers,
            timeout=30
        )

        logger.info(f"✅ DeepSeek response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'message': data['choices'][0]['message']['content'],
                'usage': data.get('usage', {})
            }
        else:
            logger.error(f"❌ DeepSeek API error: {response.status_code} - {response.text[:500]}")
            return {
                'success': False,
                'error': f'API returned status {response.status_code}'
            }

    except Exception as e:
        logger.error(f"❌ Exception calling DeepSeek: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }


@app.route('/api/ai/health', methods=['GET'])
def health():
    """Health check endpoint"""
    logger.info("📊 Health check requested")

    response = {
        'status': 'healthy',
        'service': 'AI Service with DeepSeek (Test Server)',
        'timestamp': datetime.now().isoformat(),
        'config': {
            'api_key': DEEPSEEK_API_KEY[:15] + '...' + DEEPSEEK_API_KEY[-4:],
            'api_url': DEEPSEEK_API_URL,
            'model': DEEPSEEK_MODEL
        }
    }

    # Test API connection
    try:
        test_result = call_deepseek_api(
            messages=[
                {"role": "system", "content": "You are a test assistant."},
                {"role": "user", "content": "Say 'ok' if you receive this."}
            ],
            max_tokens=10,
            temperature=0
        )

        if test_result['success']:
            response['api_connection'] = 'OK'
            response['message'] = 'API de DeepSeek funcionando correctamente'
            response['test_response'] = test_result['message']
        else:
            response['api_connection'] = 'ERROR'
            response['error'] = test_result.get('error', 'Unknown error')

    except Exception as e:
        response['api_connection'] = 'ERROR'
        response['error'] = str(e)

    return jsonify(response)


@app.route('/api/ai/chat', methods=['POST', 'OPTIONS'])
def chat():
    """Chatbot endpoint"""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        logger.info(f"📥 Chat request from {request.remote_addr}")
        logger.debug(f"Content-Type: {request.content_type}")

        data = request.get_json(force=True)
        logger.debug(f"JSON received: {data}")

        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'No message provided'
            }), 400

        user_message = data['message']
        logger.info(f"💬 User message: {user_message}")

        # Build conversation context
        messages = [
            {
                "role": "system",
                "content": "Eres un asistente de ventas amable y profesional para una tienda ecommerce ecuatoriana. "
                          "Tu nombre es AssistBot y tu trabajo es ayudar a los clientes con información sobre productos, "
                          "procesos de compra, métodos de pago y envío. Responde de manera concisa y útil en español."
            },
            {
                "role": "user",
                "content": user_message
            }
        ]

        # Call DeepSeek API
        result = call_deepseek_api(messages, max_tokens=500, temperature=0.7)

        if result['success']:
            logger.info(f"✅ Response generated successfully")
            return jsonify({
                'success': True,
                'message': result['message'],
                'session_id': 'test-session',
                'timestamp': datetime.now().isoformat()
            })
        else:
            logger.error(f"❌ Failed to generate response: {result.get('error')}")
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }), 500

    except Exception as e:
        logger.error(f"❌ Exception in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'debug': {
                'content_type': request.content_type,
                'raw_data': str(request.data[:200])
            }
        }), 500


@app.route('/')
def index():
    """Simple index page"""
    return """
    <html>
    <head><title>AI Test Server</title></head>
    <body>
        <h1>🤖 AI Test Server</h1>
        <p>Test endpoints:</p>
        <ul>
            <li><a href="/api/ai/health">GET /api/ai/health</a> - Health check</li>
            <li>POST /api/ai/chat - Chatbot (use test_ai_api.py)</li>
        </ul>
    </body>
    </html>
    """


if __name__ == '__main__':
    logger.info("🚀 Starting AI Test Server...")
    logger.info(f"📡 DeepSeek API URL: {DEEPSEEK_API_URL}")
    logger.info(f"🔑 API Key: {DEEPSEEK_API_KEY[:15]}...{DEEPSEEK_API_KEY[-4:]}")
    app.run(host='0.0.0.0', port=5000, debug=True)
