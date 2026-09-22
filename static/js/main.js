// static/js/main.js

document.addEventListener("DOMContentLoaded", () => {
    // Referencias del DOM
    const loginForm = document.getElementById('login-form');
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
        
        // Ocultar el contenedor principal completo y mostrar dashboard
        document.getElementById('home-container').style.display = 'none';
        dashboardSection.style.display = 'block';
        document.getElementById('welcome-msg').innerText = `Hola, estudiante ${codigo}`;
        
        // Mensaje inicial del bot
        setTimeout(() => {
            addMessage(`¡Hola! Ya iniciaste sesión. ¿En qué te ayudo hoy?`, 'bot');
        }, 500);
    });

    // 2. Abrir / Cerrar el Widget del Chat
    btnOpenChat.addEventListener('click', () => {
        chatWindow.style.display = 'flex';
        btnOpenChat.style.display = 'none';
    });

    btnCloseChat.addEventListener('click', () => {
        chatWindow.style.display = 'none';
        btnOpenChat.style.display = 'flex';
    });

    // 3. Lógica para enviar mensajes (Texto)
    function addMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', sender);
        msgDiv.innerHTML = text;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    btnSendChat.addEventListener('click', async () => {
        const text = chatInput.value.trim();
        if (text) {
            addMessage(text, 'user');
            chatInput.value = '';
            
            // Indicador de carga
            const loadingId = 'loading-' + Date.now();
            addMessage('<i class="fa-solid fa-ellipsis"></i>', 'bot');
            chatMessages.lastChild.id = loadingId;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mensaje: text })
                });
                
                const data = await response.json();
                
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

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            btnSendChat.click();
        }
    });


    // ==========================================
    // CAPACIDAD MULTIMODAL: SPEECH-TO-TEXT
    // ==========================================
    const btnMic = document.getElementById('btn-mic');
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.lang = 'es-PE';
        recognition.continuous = false;
        recognition.interimResults = false;

        btnMic.addEventListener('click', () => {
            btnMic.style.backgroundColor = '#EEF2FF';
            btnMic.style.color = '#5A67D8';
            chatInput.placeholder = "Escuchando...";
            recognition.start();
        });

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            chatInput.value = transcript;
            
            btnMic.style.backgroundColor = 'transparent';
            btnMic.style.color = '#64748B';
            chatInput.placeholder = "Escribe o habla aquí...";
            
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


    // ==========================================
    // CAPACIDAD MULTIMODAL: SUBIDA DE IMÁGENES
    // ==========================================
    const fileUpload = document.getElementById('file-upload');
    // Nota: Asegúrate de que en tu index.html el botón diga id="btn-upload" en lugar del onclick actual
    const btnUpload = document.getElementById('btn-upload'); 

    if (btnUpload) {
        btnUpload.addEventListener('click', async () => {
            const file = fileUpload.files[0];
            
            if (!file) {
                alert("Por favor, selecciona una imagen primero.");
                return;
            }

            const formData = new FormData();
            formData.append("imagen", file);

            // Cambiar estado del botón mientras procesa
            btnUpload.innerText = "Procesando...";
            btnUpload.disabled = true;

            try {
                // Petición al backend Flask
                const response = await fetch('/subir_imagen', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                // Mostrar resultado de la IA Visual
                alert(data.mensaje);
                
            } catch (error) {
                console.error(error);
                alert("Error de conexión al servidor. Revisa si Flask está corriendo.");
            } finally {
                // Restaurar botón e input
                btnUpload.innerText = "Validar Imagen";
                btnUpload.disabled = false;
                fileUpload.value = '';
            }
        });
    }
});