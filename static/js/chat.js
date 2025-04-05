document.addEventListener('DOMContentLoaded', function() {
    // Elementos principales
    const chatButton = document.getElementById('chat-button');
    const chatWidget = document.getElementById('chat-widget');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send-btn');
    const chatHeader = document.getElementById('chat-header');
    const chatCollapseBtn = document.getElementById('chat-collapse-btn');
    const chatResetBtn = document.getElementById('chat-reset-btn');

    // Estado inicial
    let isCollapsed = true;
    let isLoading = false;

    // Inicializar widget
    chatWidget.classList.add('chat-collapsed');

    // Mostrar/ocultar chat al hacer clic en el botón
    chatButton.addEventListener('click', function() {
        chatWidget.style.display = 'flex';
        chatButton.style.display = 'none';
        setTimeout(() => {
            chatWidget.classList.remove('chat-collapsed');
            scrollToBottom();
        }, 10);
    });

    // Colapsar chat
    chatCollapseBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        toggleChatCollapse();
    });

    // Toggle colapso al hacer clic en el encabezado
    chatHeader.addEventListener('click', function() {
        toggleChatCollapse();
    });

    // Resetear chat
    chatResetBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        if (confirm('¿Estás seguro de que quieres reiniciar la conversación?')) {
            resetChat();
        }
    });

    // Enviar mensaje al presionar Enter
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Enviar mensaje al hacer clic en el botón de enviar
    chatSendBtn.addEventListener('click', sendMessage);

    // Cargar historial de mensajes al inicio
    loadChatHistory();

    // Función para mostrar/ocultar el chat
    function toggleChatCollapse() {
        isCollapsed = !isCollapsed;
        
        if (isCollapsed) {
            chatWidget.classList.add('chat-collapsed');
            chatCollapseBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="none" d="M0 0h24v24H0z"/><path d="M12 13.172l4.95-4.95 1.414 1.414L12 16 5.636 9.636 7.05 8.222z" fill="currentColor"/></svg>';
        } else {
            chatWidget.classList.remove('chat-collapsed');
            chatCollapseBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="none" d="M0 0h24v24H0z"/><path d="M12 10.828l-4.95 4.95-1.414-1.414L12 8l6.364 6.364-1.414 1.414z" fill="currentColor"/></svg>';
            scrollToBottom();
        }
    }

    // Función para enviar un mensaje
    function sendMessage() {
        const mensaje = chatInput.value.trim();
        if (mensaje === '' || isLoading) return;

        // Agregar mensaje del usuario al chat
        addMessage(mensaje, 'user');
        
        // Limpiar input
        chatInput.value = '';
        
        // Mostrar indicador de carga
        showLoading();
        
        // Desplegar chat si está colapsado
        if (isCollapsed) {
            toggleChatCollapse();
        }

        // Enviar mensaje al servidor
        fetch('/chat/enviar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ mensaje: mensaje }),
        })
        .then(response => response.json())
        .then(data => {
            // Ocultar indicador de carga
            hideLoading();
            
            if (data.success) {
                // Agregar respuesta del asistente
                addMessage(data.mensaje, 'assistant');
            } else {
                // Mostrar error
                addMessage('Lo siento, ha ocurrido un error al procesar tu mensaje.', 'assistant');
                console.error('Error en la respuesta:', data.error);
            }
        })
        .catch(error => {
            // Ocultar indicador de carga
            hideLoading();
            
            // Mostrar error
            addMessage('Lo siento, ha ocurrido un error de conexión.', 'assistant');
            console.error('Error al enviar mensaje:', error);
        });
    }

    // Función para agregar un mensaje al chat
    function addMessage(content, role) {
        const messageEl = document.createElement('div');
        messageEl.className = `chat-message ${role}-message`;
        
        const avatarEl = document.createElement('div');
        avatarEl.className = `message-avatar ${role}-avatar`;
        avatarEl.textContent = role === 'user' ? 'T' : 'S';
        
        const contentEl = document.createElement('div');
        contentEl.className = 'message-content';
        contentEl.textContent = content;
        
        messageEl.appendChild(avatarEl);
        messageEl.appendChild(contentEl);
        
        chatMessages.appendChild(messageEl);
        
        // Desplazar hasta el final
        scrollToBottom();
    }

    // Función para cargar el historial de chat
    function loadChatHistory() {
        fetch('/chat/historial')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.historial.length > 0) {
                    // Limpiar mensajes actuales
                    chatMessages.innerHTML = '';
                    
                    // Agregar mensajes del historial
                    data.historial.forEach(msg => {
                        addMessage(msg.content, msg.role);
                    });
                } else {
                    // Mostrar mensaje de bienvenida si no hay historial
                    const welcomeEl = document.createElement('div');
                    welcomeEl.className = 'chat-greeting';
                    welcomeEl.textContent = '¡Hola! Soy tu asistente virtual de Spa en Ruedas. ¿En qué puedo ayudarte hoy?';
                    chatMessages.appendChild(welcomeEl);
                }
            })
            .catch(error => {
                console.error('Error al cargar historial:', error);
                
                // Mostrar mensaje de bienvenida en caso de error
                const welcomeEl = document.createElement('div');
                welcomeEl.className = 'chat-greeting';
                welcomeEl.textContent = '¡Hola! Soy tu asistente virtual de Spa en Ruedas. ¿En qué puedo ayudarte hoy?';
                chatMessages.appendChild(welcomeEl);
            });
    }

    // Función para mostrar indicador de carga
    function showLoading() {
        isLoading = true;
        chatSendBtn.disabled = true;
        
        const loadingEl = document.createElement('div');
        loadingEl.className = 'chat-loading';
        loadingEl.id = 'chat-loading';
        
        for (let i = 0; i < 3; i++) {
            const dotEl = document.createElement('span');
            loadingEl.appendChild(dotEl);
        }
        
        chatMessages.appendChild(loadingEl);
        scrollToBottom();
    }

    // Función para ocultar indicador de carga
    function hideLoading() {
        isLoading = false;
        chatSendBtn.disabled = false;
        
        const loadingEl = document.getElementById('chat-loading');
        if (loadingEl) {
            loadingEl.remove();
        }
    }

    // Función para desplazar al final de los mensajes
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Función para reiniciar el chat
    function resetChat() {
        fetch('/chat/reiniciar', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Limpiar mensajes
                chatMessages.innerHTML = '';
                
                // Mostrar mensaje de bienvenida
                const welcomeEl = document.createElement('div');
                welcomeEl.className = 'chat-greeting';
                welcomeEl.textContent = '¡Hola! Soy tu asistente virtual de Spa en Ruedas. ¿En qué puedo ayudarte hoy?';
                chatMessages.appendChild(welcomeEl);
            }
        })
        .catch(error => {
            console.error('Error al reiniciar chat:', error);
        });
    }
});
