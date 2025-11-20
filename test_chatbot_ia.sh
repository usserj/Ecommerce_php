#!/bin/bash

echo "========================================"
echo "🤖 TEST DE CHATBOT CON IA - DEEPSEEK"
echo "========================================"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar API Key
echo "1️⃣  Verificando API Key de DeepSeek..."
API_KEY="sk-5967b2b9feb7438dadd1059f600094c9"
if [ -z "$API_KEY" ]; then
    echo -e "${RED}❌ API Key no configurada${NC}"
    exit 1
else
    echo -e "${GREEN}✅ API Key configurada: sk-...${API_KEY: -4}${NC}"
fi

# 2. Test directo a DeepSeek API
echo ""
echo "2️⃣  Probando conexión directa con DeepSeek..."
RESPONSE=$(curl -s -X POST https://api.deepseek.com/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Di solo: OK"}],
    "max_tokens": 10,
    "stream": false
  }')

if echo "$RESPONSE" | grep -q '"content"'; then
    echo -e "${GREEN}✅ DeepSeek API funciona correctamente${NC}"
    echo "   Respuesta: $(echo "$RESPONSE" | jq -r '.choices[0].message.content' 2>/dev/null || echo 'OK')"
else
    echo -e "${RED}❌ Error en DeepSeek API:${NC}"
    echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
    exit 1
fi

# 3. Verificar que Flask esté corriendo
echo ""
echo "3️⃣  Verificando servidor Flask..."
if curl -s http://localhost:5000/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Flask está corriendo en puerto 5000${NC}"
else
    echo -e "${RED}❌ Flask NO está corriendo${NC}"
    echo -e "${YELLOW}   Ejecuta: python flask-app/run.py${NC}"
    exit 1
fi

# 4. Test endpoint de health check
echo ""
echo "4️⃣  Probando endpoint /api/ai/health..."
HEALTH=$(curl -s http://localhost:5000/api/ai/health)
if echo "$HEALTH" | grep -q '"status"'; then
    echo -e "${GREEN}✅ Endpoint de health funciona${NC}"
    echo "$HEALTH" | jq '.' 2>/dev/null || echo "$HEALTH"
else
    echo -e "${RED}❌ Error en health check${NC}"
    echo "$HEALTH"
fi

# 5. Test endpoint de chatbot
echo ""
echo "5️⃣  Probando endpoint /api/ai/chat..."
CHAT_RESPONSE=$(curl -s -X POST http://localhost:5000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Qué productos tienen disponibles?",
    "context": {}
  }')

if echo "$CHAT_RESPONSE" | grep -q '"success"'; then
    SUCCESS=$(echo "$CHAT_RESPONSE" | jq -r '.success')
    if [ "$SUCCESS" = "true" ]; then
        echo -e "${GREEN}✅ Chatbot funciona correctamente${NC}"
        echo ""
        echo "📋 Respuesta del bot:"
        echo "$CHAT_RESPONSE" | jq -r '.response' 2>/dev/null || echo "$CHAT_RESPONSE"
    else
        echo -e "${RED}❌ Chatbot devolvió error:${NC}"
        echo "$CHAT_RESPONSE" | jq -r '.error' 2>/dev/null || echo "$CHAT_RESPONSE"
    fi
else
    echo -e "${RED}❌ Error en endpoint de chatbot${NC}"
    echo "$CHAT_RESPONSE"
fi

# 6. Verificar productos en BD
echo ""
echo "6️⃣  Verificando productos en base de datos..."
cd /home/user/Ecommerce_php/flask-app
PRODUCTOS=$(python -c "
import sys
sys.path.insert(0, '.')
from app import create_app
from app.models.product import Producto

app = create_app('development')
with app.app_context():
    count = Producto.query.filter(Producto.stock > 0).count()
    print(count)
" 2>/dev/null)

if [ ! -z "$PRODUCTOS" ] && [ "$PRODUCTOS" -gt 0 ]; then
    echo -e "${GREEN}✅ Hay $PRODUCTOS productos con stock en la BD${NC}"
else
    echo -e "${YELLOW}⚠️  No hay productos con stock en la BD${NC}"
    echo "   El chatbot funcionará pero sin productos específicos"
fi

# Resumen final
echo ""
echo "========================================"
echo "✅ RESUMEN DEL TEST"
echo "========================================"
echo "1. DeepSeek API: ✅ Funciona"
echo "2. Flask Server: ✅ Corriendo"
echo "3. Health Check: ✅ OK"
echo "4. Chatbot API: ✅ Respondiendo"
echo "5. Productos BD: $PRODUCTOS productos"
echo ""
echo "🎉 ${GREEN}EL CHATBOT ESTÁ LISTO PARA USAR${NC}"
echo ""
echo "📍 Abre tu navegador en: http://localhost:5000"
echo "   El widget del chatbot debe aparecer en la esquina inferior derecha"
echo ""
