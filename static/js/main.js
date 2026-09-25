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

    // ==========================================
    // 1. [MODIFICADO] LÓGICA REAL DE LOGIN 
    // ==========================================
    loginForm.addEventListener('submit', async (e) => { // [MODIFICADO] Convertido a función asíncrona
        e.preventDefault();
        const codigo = document.getElementById('codigo').value;
        
        // [NUEVO] Obtenemos la contraseña del formulario (asegúrate de que el input tenga id="password")
        // Si en tu HTML no le pusiste ID, usa temporalmente "1234"
        const passwordInput = document.getElementById('password');
        const password = passwordInput ? passwordInput.value : "1234"; 
        
        // [NUEVO] Petición real al backend (Flask) para iniciar sesión
        try {
            const formData = new FormData();
            formData.append('codigo', codigo);
            formData.append('password', password);

            const response = await fetch('/login', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();

            if (data.ok) {
                // Ocultar el contenedor principal y mostrar dashboard solo si Flask lo aprueba
                document.getElementById('home-container').style.display = 'none';
                dashboardSection.style.display = 'block';
                document.getElementById('welcome-msg').innerText = `Hola, estudiante ${data.nombre}`;
                // [NUEVO] Limpiamos todo el historial de chat de la sesión anterior
                chatMessages.innerHTML = '';
                
                // [NUEVO] Consumimos el modelo de Perfilamiento para un saludo personalizado
                const respBienvenida = await fetch('/bienvenida', { credentials: 'same-origin' });
                const dataBienvenida = await respBienvenida.json();

                // Mensaje inicial del bot
                setTimeout(() => {
                    addMessage(dataBienvenida.mensaje || `¡Hola! Ya iniciaste sesión. ¿En qué te ayudo hoy?`, 'bot');
                }, 500);
            } else {
                // [NUEVO] Muestra alerta si la contraseña o usuario son incorrectos
                alert(data.mensaje); 
            }
        } catch (error) {
            console.error("Error en el login:", error);
            alert("Error conectando con el servidor Flask.");
        }
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
                    credentials: 'same-origin', // ¡Esto ya lo tenías bien! Mantiene viva la sesión
                    body: JSON.stringify({ mensaje: text })
                });
                
                const data = await response.json();
                
                document.getElementById(loadingId).remove();
                
                // [MODIFICADO] Mejor manejo de errores por si la sesión expira
                if (response.ok && data.respuesta) {
                    addMessage(data.respuesta, 'bot');
                } else if (data.respuesta) {
                    addMessage(data.respuesta, 'bot'); // Mostrará "La sesión expiró"
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
                    credentials: 'same-origin', // [NUEVO] Obligatorio para que Flask no bloquee la subida
                    body: formData
                });
                
                const data = await response.json();
                
                if(response.ok) {
                    alert(data.mensaje || "Imagen procesada");
                } else {
                    alert(data.error || "Error procesando la imagen");
                }
                
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