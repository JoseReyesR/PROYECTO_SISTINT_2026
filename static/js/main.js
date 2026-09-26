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
    // 1. LÓGICA REAL DE LOGIN 
    // ==========================================
    loginForm.addEventListener('submit', async (e) => { 
        e.preventDefault();
        const codigo = document.getElementById('codigo').value;
        
        const passwordInput = document.getElementById('password');
        const password = passwordInput ? passwordInput.value : "1234"; 
        
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
                document.getElementById('home-container').style.display = 'none';
                dashboardSection.style.display = 'block';
                document.getElementById('welcome-msg').innerText = `Hola, estudiante ${data.nombre}`;
                
                chatMessages.innerHTML = '';
                
                const respBienvenida = await fetch('/bienvenida', { credentials: 'same-origin' });
                const dataBienvenida = await respBienvenida.json();

                setTimeout(() => {
                    addMessage(dataBienvenida.mensaje || `¡Hola! Ya iniciaste sesión. ¿En qué te ayudo hoy?`, 'bot');
                }, 500);
            } else {
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
            
            const loadingId = 'loading-' + Date.now();
            addMessage('<i class="fa-solid fa-ellipsis"></i>', 'bot');
            chatMessages.lastChild.id = loadingId;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'same-origin', 
                    body: JSON.stringify({ mensaje: text })
                });
                
                const data = await response.json();
                
                document.getElementById(loadingId).remove();
                
                if (response.ok && data.respuesta) {
                    addMessage(data.respuesta, 'bot');
                } else if (data.respuesta) {
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
    // [MODIFICADO] CAPACIDAD MULTIMODAL: SPEECH-TO-TEXT (RecordRTC a WAV)
    // ==========================================
    const btnMic = document.getElementById('btn-mic');
    let mediaRecorder; // Ahora alojará la instancia de RecordRTC
    let isRecording = false;

    btnMic.addEventListener('click', async () => {
        if (!isRecording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                
                // [NUEVO] Configuramos RecordRTC para grabar estrictamente en WAV a 16kHz (ideal para IA)
                mediaRecorder = new RecordRTC(stream, {
                    type: 'audio',
                    mimeType: 'audio/wav',
                    recorderType: RecordRTC.StereoAudioRecorder,
                    desiredSampRate: 16000 
                });

                // Comienza a grabar
                mediaRecorder.startRecording();
                isRecording = true;
                
                // Cambios visuales
                btnMic.style.backgroundColor = '#EEF2FF';
                btnMic.style.color = '#5A67D8';
                chatInput.placeholder = "Escuchando... (Click para enviar)";
                chatInput.disabled = true;

            } catch (err) {
                console.error("Error accediendo al micrófono:", err);
                alert("No se pudo acceder al micrófono. Verifica los permisos de tu navegador.");
            }
        } else {
            // [NUEVO] Detiene la grabación y procesa el archivo WAV
            mediaRecorder.stopRecording(async () => {
                isRecording = false;
                
                // Restauramos la interfaz visual
                btnMic.style.backgroundColor = 'transparent';
                btnMic.style.color = '#64748B';
                
                // Extraemos el archivo en formato WAV puro
                const audioBlob = mediaRecorder.getBlob();
                const formData = new FormData();
                formData.append('audio', audioBlob, 'grabacion.wav');

                // Interfaz de carga
                chatInput.placeholder = "Procesando audio en el servidor...";
                const loadingId = 'loading-audio-' + Date.now();
                addMessage('<i class="fa-solid fa-ellipsis"></i>', 'bot');
                chatMessages.lastChild.id = loadingId;

                try {
                    // Enviamos el WAV a Flask
                    const response = await fetch('/chat_audio', {
                        method: 'POST',
                        credentials: 'same-origin',
                        body: formData
                    });
                    const data = await response.json();
                    
                    document.getElementById(loadingId).remove();
                    chatInput.placeholder = "Escribe o habla aquí...";
                    chatInput.disabled = false;

                    if (response.ok) {
                        addMessage(`🎤 <i>${data.texto_reconocido}</i>`, 'user'); 
                        addMessage(data.respuesta, 'bot'); 
                    } else {
                        addMessage(data.error || "Error al procesar el audio.", 'bot');
                    }
                } catch (error) {
                    console.error(error);
                    document.getElementById(loadingId).remove();
                    addMessage("Error de conexión con el servidor de voz.", 'bot');
                    chatInput.placeholder = "Escribe o habla aquí...";
                    chatInput.disabled = false;
                }
                
                // Apagamos el micrófono para ahorrar recursos
                mediaRecorder.camera.getTracks().forEach(track => track.stop());
            });
        }
    });

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

            btnUpload.innerText = "Procesando...";
            btnUpload.disabled = true;

            try {
                const response = await fetch('/subir_imagen', {
                    method: 'POST',
                    credentials: 'same-origin', 
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
                btnUpload.innerText = "Validar Imagen";
                btnUpload.disabled = false;
                fileUpload.value = '';
            }
        });
    }
});