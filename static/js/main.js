// static/js/main.js

document.addEventListener("DOMContentLoaded", () => {
    // Referencias del DOM
    const loginForm = document.getElementById('login-form');
    const loginSection = document.getElementById('login-section');
    const dashboardSection = document.getElementById('dashboard-section');
    
    // Referencias del Chatbot
    const chatWindow = document.getElementById('chat-window');
    const btnOpenChat = document.getElementById('open-chat');
    const btnCloseChat = document.getElementById('close-chat');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const btnSendChat = document.getElementById('btn-send-chat');

    // 1. Simulación de Login
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const codigo = document.getElementById('codigo').value;
        
        // Ocultar login y mostrar dashboard
       // loginSection.style.display = 'none';
       // Ocultar el contenedor principal completo y mostrar dashboard
        document.getElementById('home-container').style.display = 'none';
        dashboardSection.style.display = 'block';
        document.getElementById('welcome-msg').innerText = `Hola, estudiante ${codigo}`;
        
        // Si el chat estaba abierto, lo podemos dejar abierto, o mostrar un mensaje inicial
        setTimeout(() => {
            addMessage(`¡Hola! Ya iniciaste sesión. ¿En qué te ayudo hoy?`, 'bot');
        }, 500);
    });

    // 2. Abrir / Cerrar el Widget del Chat
    btnOpenChat.addEventListener('click', () => {
        chatWindow.style.display = 'flex';
        btnOpenChat.style.display = 'none'; // Oculta el botón redondo
    });

    btnCloseChat.addEventListener('click', () => {
        chatWindow.style.display = 'none';
        btnOpenChat.style.display = 'flex'; // Muestra el botón redondo
    });

    // 3. Lógica para enviar mensajes
    function addMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', sender);
        msgDiv.innerHTML = text;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll hacia abajo
    }

    btnSendChat.addEventListener('click', () => {
        const text = chatInput.value.trim();
        if (text) {
            addMessage(text, 'user');
            chatInput.value = '';
            
            // Simulación de respuesta de la IA
            setTimeout(() => {
                addMessage("Estoy procesando tu solicitud...", 'bot');
            }, 800);
        }
    });

    // Permitir envío con la tecla Enter
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            btnSendChat.click();
        }
    });
});