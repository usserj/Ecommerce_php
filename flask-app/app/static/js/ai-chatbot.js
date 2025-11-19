/**
 * Widget de Chatbot con IA para E-commerce
 *
 * Características:
 * - Widget flotante responsive
 * - Historial de conversación persistente
 * - Indicador de escritura ("typing...")
 * - Auto-scroll
 * - Manejo de errores robusto
 * - Compatible con Bootstrap 5
 */

class AIChatbot {
    constructor(config) {
        this.apiUrl = config.apiUrl;
        this.userName = config.userName;
        this.userId = config.userId;
        this.cartCount = config.cartCount;
        this.storeName = config.storeName;

        this.isOpen = false;
        this.isTyping = false;
        this.conversationHistory = this.loadHistory();

        this.init();
    }

    init() {
        // Crear estructura HTML del widget
        this.render();

        // Adjuntar event listeners
        this.attachEventListeners();

        // Mostrar mensaje de bienvenida si es primera vez
        if (this.conversationHistory.length === 0) {
            this.addWelcomeMessage();
        } else {
            // Restaurar historial visual
            this.restoreHistory();
        }
    }

    render() {
        const widgetHTML = `
            <div id="ai-chatbot-widget" class="ai-chatbot-widget">
                <!-- Botón flotante -->
                <button id="chatbot-toggle" class="chatbot-toggle-btn">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    <span class="chatbot-badge">¿Dudas?</span>
                </button>

                <!-- Ventana de chat -->
                <div id="chatbot-window" class="chatbot-window" style="display: none;">
                    <div class="chatbot-header">
                        <div class="chatbot-header-info">
                            <div class="chatbot-avatar">
                                <i class="fas fa-robot"></i>
                            </div>
                            <div>
                                <h6 class="mb-0">${this.escapeHTML(this.storeName)}</h6>
                                <p class="chatbot-status mb-0">
                                    <span class="status-dot"></span>
                                    En línea
                                </p>
                            </div>
                        </div>
                        <button id="chatbot-close" class="chatbot-close-btn">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>

                    <div id="chatbot-messages" class="chatbot-messages">
                        <!-- Mensajes aquí -->
                    </div>

                    <div class="chatbot-suggestions" id="chatbot-suggestions">
                        <button class="suggestion-chip" data-message="¿Tienen envío gratis?">
                            📦 ¿Envío gratis?
                        </button>
                        <button class="suggestion-chip" data-message="¿Cuáles son los productos más vendidos?">
                            ⭐ Más vendidos
                        </button>
                        <button class="suggestion-chip" data-message="¿Qué métodos de pago aceptan?">
                            💳 Métodos de pago
                        </button>
                    </div>

                    <div class="chatbot-input-container">
                        <input
                            type="text"
                            id="chatbot-input"
                            class="chatbot-input"
                            placeholder="Escribe tu mensaje..."
                            autocomplete="off"
                        />
                        <button id="chatbot-send" class="chatbot-send-btn">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Inyectar en el DOM
        document.body.insertAdjacentHTML('beforeend', widgetHTML);
    }

    attachEventListeners() {
        // Toggle chatbot
        document.getElementById('chatbot-toggle').addEventListener('click', () => {
            this.toggleChat();
        });

        // Cerrar chatbot
        document.getElementById('chatbot-close').addEventListener('click', () => {
            this.closeChat();
        });

        // Enviar mensaje
        document.getElementById('chatbot-send').addEventListener('click', () => {
            this.sendMessage();
        });

        // Enter para enviar
        document.getElementById('chatbot-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // Sugerencias rápidas
        document.querySelectorAll('.suggestion-chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                const message = e.target.getAttribute('data-message');
                this.sendMessage(message);
            });
        });
    }

    toggleChat() {
        const window = document.getElementById('chatbot-window');
        const toggle = document.getElementById('chatbot-toggle');

        if (this.isOpen) {
            window.style.display = 'none';
            toggle.style.display = 'flex';
            this.isOpen = false;
        } else {
            window.style.display = 'flex';
            toggle.style.display = 'none';
            this.isOpen = true;

            // Focus en input
            document.getElementById('chatbot-input').focus();

            // Scroll al final
            this.scrollToBottom();
        }
    }

    closeChat() {
        document.getElementById('chatbot-window').style.display = 'none';
        document.getElementById('chatbot-toggle').style.display = 'flex';
        this.isOpen = false;
    }

    async sendMessage(text = null) {
        const input = document.getElementById('chatbot-input');
        const message = (text || input.value).trim();

        if (!message) return;

        // Limpiar input
        input.value = '';

        // Ocultar sugerencias después del primer mensaje
        document.getElementById('chatbot-suggestions').style.display = 'none';

        // Agregar mensaje del usuario al UI
        this.addMessage(message, 'user');

        // Guardar en historial
        this.conversationHistory.push({
            role: 'user',
            content: message,
            timestamp: new Date().toISOString()
        });
        this.saveHistory();

        // Mostrar indicador de escritura
        this.showTypingIndicator();

        try {
            // Preparar contexto
            const context = this.getContext();

            // Llamar a la API
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    context: context
                })
            });

            const data = await response.json();

            // Ocultar indicador
            this.hideTypingIndicator();

            if (data.success && data.response) {
                // Agregar respuesta del bot
                this.addMessage(data.response, 'bot');

                // Guardar en historial
                this.conversationHistory.push({
                    role: 'assistant',
                    content: data.response,
                    timestamp: new Date().toISOString()
                });
                this.saveHistory();
            } else {
                throw new Error(data.error || 'Error desconocido');
            }

        } catch (error) {
            console.error('Error en chatbot:', error);
            this.hideTypingIndicator();

            // Mensaje de error amigable
            this.addMessage(
                'Lo siento, estoy teniendo problemas técnicos. Por favor intenta de nuevo en un momento. 😅',
                'bot'
            );
        }
    }

    addMessage(text, sender) {
        const messagesContainer = document.getElementById('chatbot-messages');
        const messageClass = sender === 'user' ? 'user-message' : 'bot-message';

        const messageHTML = `
            <div class="chatbot-message ${messageClass}">
                <div class="message-content">${this.escapeHTML(text)}</div>
                <div class="message-time">${this.getTime()}</div>
            </div>
        `;

        messagesContainer.insertAdjacentHTML('beforeend', messageHTML);
        this.scrollToBottom();
    }

    addWelcomeMessage() {
        const greeting = this.userName
            ? `¡Hola ${this.escapeHTML(this.userName)}! 👋`
            : '¡Hola! 👋';

        const welcomeText = `${greeting} Soy tu asistente de compras. ¿En qué puedo ayudarte hoy?`;

        this.addMessage(welcomeText, 'bot');

        // Guardar en historial
        this.conversationHistory.push({
            role: 'assistant',
            content: welcomeText,
            timestamp: new Date().toISOString()
        });
        this.saveHistory();
    }

    restoreHistory() {
        // Restaurar mensajes del historial
        this.conversationHistory.forEach(msg => {
            const sender = msg.role === 'user' ? 'user' : 'bot';
            this.addMessage(msg.content, sender);
        });
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatbot-messages');

        const typingHTML = `
            <div class="chatbot-message bot-message typing-indicator" id="typing-indicator">
                <div class="message-content">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;

        messagesContainer.insertAdjacentHTML('beforeend', typingHTML);
        this.isTyping = true;
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
        this.isTyping = false;
    }

    scrollToBottom() {
        const container = document.getElementById('chatbot-messages');
        setTimeout(() => {
            container.scrollTop = container.scrollHeight;
        }, 100);
    }

    getContext() {
        /**
         * Obtiene contexto de la página actual
         * - Productos visibles
         * - Carrito
         */
        const context = {
            carrito: {},
            productos: []
        };

        // Obtener carrito del contador
        if (this.cartCount > 0) {
            context.carrito = {
                total_items: this.cartCount
            };
        }

        // Intentar obtener productos de la página actual
        // (Esto requiere que los productos tengan atributos data-*)
        try {
            const productCards = document.querySelectorAll('[data-producto-id]');
            productCards.forEach(card => {
                const producto = {
                    id: card.getAttribute('data-producto-id'),
                    nombre: card.getAttribute('data-producto-nombre'),
                    precio: parseFloat(card.getAttribute('data-producto-precio')),
                    categoria: card.getAttribute('data-producto-categoria') || ''
                };
                context.productos.push(producto);
            });
        } catch (e) {
            console.warn('No se pudieron obtener productos del contexto:', e);
        }

        return context;
    }

    loadHistory() {
        /**
         * Carga historial de conversación desde sessionStorage
         */
        try {
            const stored = sessionStorage.getItem('chatbot_history');
            return stored ? JSON.parse(stored) : [];
        } catch (e) {
            console.error('Error al cargar historial:', e);
            return [];
        }
    }

    saveHistory() {
        /**
         * Guarda historial en sessionStorage
         * Limita a últimos 50 mensajes
         */
        try {
            const limited = this.conversationHistory.slice(-50);
            sessionStorage.setItem('chatbot_history', JSON.stringify(limited));
        } catch (e) {
            console.error('Error al guardar historial:', e);
        }
    }

    getTime() {
        const now = new Date();
        return now.getHours().toString().padStart(2, '0') + ':' +
               now.getMinutes().toString().padStart(2, '0');
    }

    escapeHTML(text) {
        /**
         * Escapa HTML para prevenir XSS
         */
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Verificar que estamos en la tienda (no en admin)
    if (!window.location.pathname.startsWith('/admin')) {
        // Inicializar con config desde Flask
        if (typeof window.CHATBOT_CONFIG !== 'undefined') {
            window.chatbot = new AIChatbot(window.CHATBOT_CONFIG);
        } else {
            console.error('CHATBOT_CONFIG no está definido');
        }
    }
});
