from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import mysql.connector
import joblib
import os

# Importamos la función de tu script de IA Visual
from modelo_imagenes import analizar_pagina_web 
from chatbot import responder_chatbot

app = Flask(__name__)
app.secret_key = "clave_super_secreta"
app.config["UPLOAD_FOLDER"] = "static/uploads"

# Aseguramos que exista la carpeta para guardar las imágenes temporales
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# 1. Cargar el Modelo de Machine Learning exportado (Regresión Lineal)[cite: 3]
try:
    # MODIFICADO: Se actualizó la ruta para que busque dentro de la carpeta 'modelos'
    modelo_notas = joblib.load("modelos/modelo_notas.pkl") 
    print("✅ Modelo de Riesgo Académico cargado correctamente.")
except Exception as e:
    print(f"⚠️ Error al cargar el modelo: {e}")

# ==========================================
# RUTAS WEB DEL SISTEMA
# ==========================================

@app.route("/")
def inicio():
    # Aquí conectaremos el HTML más adelante
    #return "<h1>¡Servidor Flask Activo!</h1><p>El Asistente Virtual Inteligente está en línea.</p>"
    # Flask buscará automáticamente 'index.html' dentro de la carpeta 'templates'[cite: 5]
    return render_template("index.html")

@app.route("/notas", methods=["GET"])
def notas():
    """
    Ruta para predecir el riesgo académico usando el modelo de Regresión Lineal[cite: 3].
    """
    import pandas as pd
    # Simulación temporal de datos de un estudiante para probar el endpoint
    nuevo_estudiante = pd.DataFrame({'promedio_actual': [10.5], 'tareas_entregadas': [4], 'tareas_pendientes': [6]})
    
    if modelo_notas:
        nota_estimada = modelo_notas.predict(nuevo_estudiante)[0]
        riesgo = "ALTO" if nota_estimada < 11 else "MEDIO" if nota_estimada < 14 else "BAJO"
        return jsonify({
            "nota_estimada": round(nota_estimada, 1),
            "nivel_riesgo": riesgo
        })
    return jsonify({"error": "Modelo predictivo no disponible."})

@app.route("/subir_imagen", methods=["POST"])
def subir_imagen():
    """
    Ruta para recibir vouchers o DNI y procesarlos con IA Visual[cite: 3].
    """
    if "imagen" not in request.files:
        return jsonify({"error": "No se envió ninguna imagen."})
        
    archivo = request.files["imagen"]
    if archivo.filename == "":
        return jsonify({"error": "Archivo vacío."})
    
    # Guardado seguro del archivo[cite: 3]
    nombre_seguro = secure_filename(archivo.filename)
    ruta = os.path.join(app.config["UPLOAD_FOLDER"], nombre_seguro)
    archivo.save(ruta)
    
    # Análisis con tu script modelo_imagenes.py[cite: 3]
    resultado_ia = analizar_pagina_web(ruta)
    
    return jsonify({
        "archivo_recibido": nombre_seguro,
        "analisis_visual": resultado_ia
    })
    
    
@app.route("/chat", methods=["POST"])
def chat():
    """
    Endpoint que recibe el texto del frontend (escrito o dictado por voz) y lo procesa con la IA.
    """
    datos = request.get_json()
    if not datos or "mensaje" not in datos:
        return jsonify({"error": "No se recibió ningún mensaje."}), 400
        
    mensaje_usuario = datos["mensaje"]
    
    # Aquí podríamos extraer el código del alumno desde session["id_estudiante"], 
    # pero para esta prueba usaremos un valor por defecto.
    respuesta_ia = responder_chatbot(mensaje_usuario)
    
    return jsonify({
        "respuesta": respuesta_ia
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    
    