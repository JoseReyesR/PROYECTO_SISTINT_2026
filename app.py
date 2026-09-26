from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import mysql.connector
import joblib
import os
import pandas as pd # Necesario para pasarle datos de la BD a los modelos
import speech_recognition as sr # [NUEVO] Librería académica para procesamiento de voz

# Importamos las funciones de tus scripts de IA
from modelo_imagenes import analizar_documento
from chatbot import responder_chatbot
from conexion_sql import obtener_conexion # Importamos la conexión a BD

app = Flask(__name__)
app.secret_key = "clave_super_secreta"

# ==========================================
# CONFIGURACIÓN DE SESIONES Y LOGIN
# ==========================================
app.config['SESSION_COOKIE_SAMESITE'] = "Lax"
app.config['SESSION_COOKIE_SECURE'] = False

# Configuración centralizada para subida de archivos
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Aseguramos que exista la carpeta para guardar las imágenes temporales
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# ==========================================
# CARGA DE MÚLTIPLES MODELOS ML
# ==========================================
try:
    modelo_notas = joblib.load("modelos/modelo_notas.pkl") 
    print("✅ Modelo de Riesgo Académico cargado correctamente.")
except Exception as e:
    modelo_notas = None
    print(f"⚠️ Error al cargar el modelo de notas: {e}")

try:
    modelo_perfil = joblib.load("modelos/modelo_perfil_usuario.pkl")
    print("✅ Modelo de Perfilamiento cargado correctamente.")
except Exception as e:
    modelo_perfil = None
    print(f"⚠️ Error al cargar el modelo de perfilamiento: {e}")

# ==========================================
# FUNCIÓN AUXILIAR DE SEGURIDAD
# ==========================================
def logueado():
    """Verifica si CUALQUIER usuario (padre, profe, estudiante) ha iniciado sesión"""
    return "nombre" in session

# ==========================================
# RUTAS WEB DEL SISTEMA
# ==========================================

@app.route("/")
def inicio():
    # Destruye cualquier sesión activa al recargar la página (F5)
    session.clear()
    return render_template("index.html")

# ==========================================
# RUTA DE LOGIN UNIVERSAL
# ==========================================
@app.route("/login", methods=["POST"])
def login():
    """Valida las credenciales reales contra la base de datos permitiendo múltiples roles"""
    codigo_o_usuario = request.form.get("codigo") # Puede recibir "EST-001" o "padre_familia1"
    password = request.form.get("password")

    from conexion_sql import validar_login_universal
    
    usuario = validar_login_universal(codigo_o_usuario, password)

    if usuario is None:
        return jsonify({"ok": False, "mensaje": "Usuario no encontrado o contraseña incorrecta"})

    # Guardamos datos en sesión dependiendo del rol
    session["id_usuario"] = usuario['id_usuario']
    session["rol_id"] = usuario['rol_id']
    
    # Si es estudiante (rol_id == 4), guardamos su ID de estudiante para el chatbot
    if usuario['rol_id'] == 4 and usuario['id_estudiante']:
        session["id_estudiante"] = usuario['id_estudiante']
        session["nombre"] = usuario['codigo_anonimizado']
    else:
        # Para padres o profes, usamos su username
        session["nombre"] = usuario['username']

    return jsonify({
        "ok": True,
        "nombre": session["nombre"],
        "rol": usuario['rol_id']
    })

# ==========================================
# RUTA DE BIENVENIDA CON INTELIGENCIA ARTIFICIAL
# ==========================================
@app.route("/bienvenida", methods=["GET"])
def bienvenida():
    """Genera un saludo adaptativo basado en el perfil del usuario (Estudiante o General)"""
    if not logueado():
        return jsonify({"ok": False, "mensaje": "No autorizado"}), 401

    nombre = session["nombre"]
    id_estudiante = session.get("id_estudiante") # Puede ser None si es un padre o profesor
    interes = "institucional" # Valor por defecto para no estudiantes
    
    # Predecimos el perfil usando datos reales SOLO si es un estudiante
    if id_estudiante and modelo_perfil:
        try:
            conexion = obtener_conexion()
            if conexion:
                query = "SELECT cursos_matriculados, pagos_realizados, tareas_entregadas_total FROM dataset_perfil_usuario WHERE id_estudiante = %s"
                df_perfil = pd.read_sql(query, conexion, params=(id_estudiante,))
                conexion.close()
                
                if len(df_perfil) > 0:
                    interes = modelo_perfil.predict(df_perfil)[0]
        except Exception as e:
            print(f"Error al predecir perfil: {e}")

    contexto_map = {
        "pagos": "he visto que consultas mucho sobre 💰 pagos",
        "horario": "veo que te estás organizando bastante con tus clases",
        "tareas": "he visto que entregas a tiempo tus 📚 tareas",
        "institucional": "bienvenido al portal institucional"
    }
    
    contexto = contexto_map.get(interes, "es tu primera vez o tienes consultas variadas")
    
    # Diferenciamos el mensaje si es un alumno o un padre/profesor
    if id_estudiante:
        mensaje = f"Hey {nombre} 👋 {contexto}. ¿En qué puedo ayudarte hoy?"
    else:
        mensaje = f"Hola {nombre} 👋 {contexto}. ¿En qué te puedo orientar hoy?"
    
    return jsonify({"ok": True, "mensaje": mensaje})

# ==========================================
# RUTA DE PREDICCIÓN DE RIESGO
# ==========================================
@app.route("/notas", methods=["GET"])
def notas():
    """Ruta para predecir el riesgo académico usando el modelo de Regresión Lineal."""
    if not logueado():
        return jsonify({"error": "Debes iniciar sesión primero."}), 401
        
    if not modelo_notas:
        return jsonify({"error": "Modelo predictivo no disponible."})
        
    id_estudiante = session.get("id_estudiante")
    
    if not id_estudiante:
        return jsonify({"error": "Solo los estudiantes tienen acceso al análisis de rendimiento."})
    
    try:
        conexion = obtener_conexion()
        if conexion:
            query = "SELECT promedio_actual, tareas_entregadas, tareas_pendientes FROM dataset_rendimiento WHERE id_estudiante = %s"
            df_estudiante = pd.read_sql(query, conexion, params=(id_estudiante,))
            conexion.close()
            
            if len(df_estudiante) > 0:
                nota_estimada = modelo_notas.predict(df_estudiante)[0]
                riesgo = "ALTO" if nota_estimada < 11 else "MEDIO" if nota_estimada < 14 else "BAJO"
                return jsonify({
                    "nota_estimada": round(nota_estimada, 1),
                    "nivel_riesgo": riesgo
                })
            else:
                return jsonify({"error": "No tienes suficientes datos académicos registrados."})
    except Exception as e:
        return jsonify({"error": f"Error al calcular riesgo: {e}"})

# ==========================================
# RUTA DE CHAT HÍBRIDO (PÚBLICO Y PRIVADO)
# ==========================================
@app.route("/chat", methods=["POST"])
def chat():
    """Endpoint que recibe el texto del frontend y lo procesa con la IA."""
    datos = request.get_json()
    if not datos or "mensaje" not in datos:
        return jsonify({"error": "No se recibió ningún mensaje."}), 400
        
    mensaje_usuario = datos["mensaje"]
    
    # Obtenemos el ID del estudiante solo si ha iniciado sesión, de lo contrario es None
    id_estudiante = session.get("id_estudiante", None) 
    
    # Pasamos el mensaje a la IA. El chatbot decidirá si le responde o le pide login.
    respuesta_ia = responder_chatbot(mensaje_usuario, id_estudiante)
    
    return jsonify({
        "respuesta": respuesta_ia.get("respuesta", "Lo siento, tuve un error al procesar tu consulta.")
    })

# ==========================================
# [NUEVO] RUTA DE CHAT POR VOZ (SPEECH-TO-TEXT)
# ==========================================
@app.route("/chat_audio", methods=["POST"])
def chat_audio():
    """Recibe un archivo de audio del frontend, lo convierte a texto y lo procesa con la IA."""
    if "audio" not in request.files:
        return jsonify({"error": "No se envió ningún archivo de audio."}), 400

    archivo_audio = request.files["audio"]
    if archivo_audio.filename == "":
        return jsonify({"error": "Archivo de audio vacío."}), 400

    # Guardamos el audio temporalmente en el servidor
    nombre_seguro = secure_filename("grabacion_temporal.wav")
    ruta_audio = os.path.join(app.config["UPLOAD_FOLDER"], nombre_seguro)
    archivo_audio.save(ruta_audio)

    id_estudiante = session.get("id_estudiante", None)

    try:
        # Procesamiento de la señal de voz utilizando la librería académica
        reconocedor = sr.Recognizer()
        with sr.AudioFile(ruta_audio) as origen:
            # Lee el archivo de audio guardado
            audio_data = reconocedor.record(origen)
            # Convierte la señal en texto
            texto_transcrito = reconocedor.recognize_google(audio_data, language="es-PE")
        
        # Una vez que tenemos el texto, lo pasamos al modelo NLP del chatbot
        respuesta_ia = responder_chatbot(texto_transcrito, id_estudiante)
        
        # Limpiamos el archivo temporal para no saturar el servidor
        os.remove(ruta_audio)

        return jsonify({
            "texto_reconocido": texto_transcrito,
            "respuesta": respuesta_ia.get("respuesta", "Lo siento, tuve un error al procesar tu consulta.")
        })

    except sr.UnknownValueError:
        if os.path.exists(ruta_audio): os.remove(ruta_audio)
        return jsonify({"error": "No pude entender el audio. Intenta hablar más claro."}), 400
    except sr.RequestError:
        if os.path.exists(ruta_audio): os.remove(ruta_audio)
        return jsonify({"error": "Error de conexión con el servicio de reconocimiento de voz."}), 500
    except Exception as e:
        if os.path.exists(ruta_audio): os.remove(ruta_audio)
        return jsonify({"error": f"Error procesando el audio: {e}"}), 500

# ==========================================
# RUTA DE IA VISUAL
# ==========================================
@app.route("/subir_imagen", methods=["POST"])
def subir_imagen():
    """Ruta unificada para recibir vouchers o DNI y procesarlos con IA Visual."""
    if not logueado():
        return jsonify({"error": "No autorizado", "valido": False}), 401

    if "imagen" not in request.files:
        return jsonify({"error": "No se envió ninguna imagen.", "valido": False}), 400
        
    archivo = request.files["imagen"]
    
    if archivo.filename == "":
        return jsonify({"error": "Archivo vacío.", "valido": False}), 400
    
    nombre_seguro = secure_filename(archivo.filename)
    ruta = os.path.join(app.config["UPLOAD_FOLDER"], nombre_seguro)
    archivo.save(ruta)
    
    # Análisis visual con tu script modelo_imagenes.py
    resultado_ia = analizar_documento(ruta)
    
    return jsonify(resultado_ia)

if __name__ == "__main__":
    app.run(debug=True, port=5000)