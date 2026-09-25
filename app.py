from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import mysql.connector
import joblib
import os
import pandas as pd # [NUEVO] Necesario para pasarle datos de la BD a los modelos

# Importamos las funciones de tus scripts de IA
from modelo_imagenes import analizar_documento
from chatbot import responder_chatbot
from conexion_sql import obtener_conexion # [NUEVO] Importamos la conexión a BD

app = Flask(__name__)
app.secret_key = "clave_super_secreta"

# ==========================================
# [NUEVO] CONFIGURACIÓN DE SESIONES Y LOGIN
# ==========================================
app.config['SESSION_COOKIE_SAMESITE'] = "Lax"
app.config['SESSION_COOKIE_SECURE'] = False
PASSWORD_DEMO = "1234" # Contraseña general para el prototipo

# Configuración centralizada para subida de archivos
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Aseguramos que exista la carpeta para guardar las imágenes temporales
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# ==========================================
# [MODIFICADO] CARGA DE MÚLTIPLES MODELOS ML
# ==========================================
try:
    modelo_notas = joblib.load("modelos/modelo_notas.pkl") 
    print("✅ Modelo de Riesgo Académico cargado correctamente.")
except Exception as e:
    modelo_notas = None
    print(f"⚠️ Error al cargar el modelo de notas: {e}")

try:
    # [NUEVO] Cargamos el modelo de perfilamiento que recién creaste
    modelo_perfil = joblib.load("modelos/modelo_perfil_usuario.pkl")
    print("✅ Modelo de Perfilamiento cargado correctamente.")
except Exception as e:
    modelo_perfil = None
    print(f"⚠️ Error al cargar el modelo de perfilamiento: {e}")

# ==========================================
# [NUEVO] FUNCIÓN AUXILIAR DE SEGURIDAD
# ==========================================
def logueado():
    """Verifica si un estudiante ha iniciado sesión"""
    return "id_estudiante" in session

# ==========================================
# RUTAS WEB DEL SISTEMA
# ==========================================

@app.route("/")
def inicio():
    # Flask buscará automáticamente 'index.html' dentro de la carpeta 'templates'
    return render_template("index.html")

# [NUEVO] RUTA DE LOGIN
# [MODIFICADO] RUTA DE LOGIN REAL
@app.route("/login", methods=["POST"])
def login():
    """Valida las credenciales reales contra la base de datos"""
    codigo = request.form.get("codigo")
    password = request.form.get("password")

    # Importa la nueva función desde conexion_sql (asegúrate de actualizar el import arriba)
    from conexion_sql import obtener_estudiante_login
    
    # Validamos enviando tanto el código como el password a MySQL
    estudiante = obtener_estudiante_login(codigo, password)

    if estudiante is None:
        return jsonify({"ok": False, "mensaje": "Código no encontrado o contraseña incorrecta"})

    # Guardamos los datos en la memoria segura del servidor
    session["id_estudiante"] = estudiante['id_estudiante']
    session["nombre"] = estudiante['codigo_anonimizado']

    return jsonify({
        "ok": True,
        "nombre": estudiante['codigo_anonimizado']
    })

# [NUEVO] RUTA DE BIENVENIDA CON INTELIGENCIA ARTIFICIAL
@app.route("/bienvenida", methods=["GET"])
def bienvenida():
    """Genera un saludo adaptativo basado en el perfil predictivo del alumno"""
    if not logueado():
        return jsonify({"ok": False, "mensaje": "No autorizado"}), 401

    nombre = session["nombre"]
    id_estudiante = session["id_estudiante"]
    interes = "horario" # Valor por defecto
    
    # Predecimos el perfil usando datos reales de la BD
    if modelo_perfil:
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
        "tareas": "he visto que entregas a tiempo tus 📚 tareas"
    }
    
    contexto = contexto_map.get(interes, "es tu primera vez o tienes consultas variadas")
    mensaje = f"Hey {nombre} 👋 {contexto}. ¿En qué puedo ayudarte hoy?"
    
    return jsonify({"ok": True, "mensaje": mensaje})

@app.route("/notas", methods=["GET"])
def notas():
    """Ruta para predecir el riesgo académico usando el modelo de Regresión Lineal."""
    # [MODIFICADO] Bloqueamos acceso anónimo y extraemos datos reales de BD en vez de simulados
    if not logueado():
        return jsonify({"error": "Debes iniciar sesión primero."}), 401
        
    if not modelo_notas:
        return jsonify({"error": "Modelo predictivo no disponible."})
        
    id_estudiante = session["id_estudiante"]
    
    try:
        conexion = obtener_conexion()
        if conexion:
            # Traemos las variables reales del alumno desde tu vista SQL
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

@app.route("/chat", methods=["POST"])
def chat():
    """Endpoint que recibe el texto del frontend y lo procesa con la IA."""
    # [MODIFICADO] Bloqueamos acceso anónimo
    if not logueado():
        return jsonify({"respuesta": "La sesión expiró. Vuelve a iniciar sesión."}), 401

    datos = request.get_json()
    if not datos or "mensaje" not in datos:
        return jsonify({"error": "No se recibió ningún mensaje."}), 400
        
    mensaje_usuario = datos["mensaje"]
    id_estudiante = session["id_estudiante"] # [NUEVO] Obtenemos ID real de sesión
    
    # [MODIFICADO] Pasamos el id_estudiante al chatbot para que consulte su deuda específica
    respuesta_ia = responder_chatbot(mensaje_usuario, id_estudiante)
    
    # [MODIFICADO] Manejamos el diccionario que devuelve responder_chatbot (intencion, respuesta)
    return jsonify({
        "respuesta": respuesta_ia.get("respuesta", "Lo siento, tuve un error al procesar tu consulta.")
    })

@app.route("/subir_imagen", methods=["POST"])
def subir_imagen():
    """Ruta unificada para recibir vouchers o DNI y procesarlos con IA Visual."""
    # [MODIFICADO] Bloqueamos acceso anónimo para seguridad
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