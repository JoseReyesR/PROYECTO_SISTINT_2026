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

    btnSendChat.addEventListener('click', async () => {
        const text = chatInput.value.trim();
        if (text) {
            addMessage(text, 'user');
            chatInput.value = '';
            
            // Agregamos un indicador de "escribiendo..."
            const loadingId = 'loading-' + Date.now();
            addMessage('<i class="fa-solid fa-ellipsis"></i>', 'bot');
            chatMessages.lastChild.id = loadingId;

            try {
                // Conexión real con el backend Flask (Ruta NLP)
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mensaje: text })
                });
                
                const data = await response.json();
                
                // Remover indicador de carga y mostrar respuesta de la IA
                document.getElementById(loadingId).remove();
                if (data.respuesta) {
                    addMessage(data.respuesta, 'bot');
                } else {
                    addMessage("Error de conexión con la IA.", 'bot');
                }
            } catch (error) {
                document.getElementById(loadingId).remove();
                addMessage("Servidor fuera de línea.", 'bot');
            }
        }
    });

    // Permitir envío con la tecla Enter
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            btnSendChat.click();
        }
    });


    // ==========================================
    // CAPACIDAD MULTIMODAL: SPEECH-TO-TEXT
    // ==========================================
    const btnMic = document.getElementById('btn-mic');
    
    // Verificamos si el navegador soporta el reconocimiento de voz
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.lang = 'es-PE'; // Español de Perú
        recognition.continuous = false;
        recognition.interimResults = false;

        btnMic.addEventListener('click', () => {
            // Cambiamos el estilo visual para indicar que está grabando
            btnMic.style.backgroundColor = '#EEF2FF';
            btnMic.style.color = '#5A67D8';
            chatInput.placeholder = "Escuchando...";
            
            recognition.start();
        });

        recognition.onresult = (event) => {
            // Capturamos el texto transcrito
            const transcript = event.results[0][0].transcript;
            chatInput.value = transcript;
            
            // Restauramos el estilo del botón
            btnMic.style.backgroundColor = 'transparent';
            btnMic.style.color = '#64748B';
            chatInput.placeholder = "Escribe o habla aquí...";
            
            // Simulamos el clic en enviar automáticamente
            btnSendChat.click();
        };

        recognition.onerror = (event) => {
            console.error("Error en el micrófono: ", event.error);
            btnMic.style.backgroundColor = 'transparent';
            btnMic.style.color = '#64748B';
            chatInput.placeholder = "Error al escuchar. Intenta de nuevo.";
        };
    } else {
        btnMic.addEventListener('click', () => {
            alert("Tu navegador no soporta el reconocimiento de voz. Por favor, usa Google Chrome.");
        });
    }
});