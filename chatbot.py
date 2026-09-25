import joblib
import re # [NUEVO] Expresiones regulares para limpiar texto
import nltk # [NUEVO] Librería de procesamiento de lenguaje
from nltk.stem.snowball import SnowballStemmer # [NUEVO] Para extraer la raíz de las palabras
from nltk.tokenize import word_tokenize # [NUEVO] Para separar oraciones en palabras
from conexion_sql import obtener_conexion

print("Cargando modelos NLP...")
# Cargar los modelos previamente entrenados
modelo_nlp = joblib.load("modelos/modelo_chatbot.pkl")
vectorizador = joblib.load("modelos/vectorizer.pkl")

# [NUEVO] Inicializamos el stemmer en español fuera de la función para mayor rendimiento
stemmer = SnowballStemmer('spanish')

def responder_chatbot(mensaje, id_estudiante):
    """
    Procesa el mensaje del estudiante, detecta la intención y consulta la BD.
    """
    # 1. [NUEVO] Limpieza y Lematización del mensaje del usuario
    # Convertimos "tengo deudas pendientes?" a "teng deud pendient" para coincidir con el entrenamiento
    mensaje_limpio = re.sub(r'[^\w\s]', '', mensaje.lower())
    palabras = word_tokenize(mensaje_limpio)
    mensaje_lematizado = " ".join([stemmer.stem(p) for p in palabras])
    
    # 2. [MODIFICADO] Identificación de la intención usando el texto lematizado
    texto_vectorizado = vectorizador.transform([mensaje_lematizado])
    intencion = modelo_nlp.predict(texto_vectorizado)[0]
    
    respuesta = ""
    
    # Consulta de información en base de datos[cite: 3]
    conexion = obtener_conexion()
    if not conexion:
        return {"respuesta": "Error de conexión a la base de datos."}
        
    cursor = conexion.cursor(dictionary=True)
    
    try:
        # Generación de respuestas dinámicas[cite: 3]
        
        # [NUEVO] Manejo de "Out of Scope" (Fuera de contexto)
        if intencion == "desconocido":
            respuesta = "Lo siento, soy un asistente académico. Solo puedo ayudarte con temas como notas, pagos, horarios y tareas."
            
        elif intencion == "pagos":
            query = "SELECT concepto, monto, estado FROM pagos WHERE id_estudiante = %s"
            cursor.execute(query, (id_estudiante,))
            deudas = cursor.fetchall()
            
            if deudas:
                respuesta = "💰 Tus pagos pendientes:\n"
                for d in deudas:
                    respuesta += f"- {d['concepto']} | S/ {d['monto']} | {d['estado']}\n"
            else:
                respuesta = "✅ No tienes pagos registrados o deudas pendientes."
                
        elif intencion == "horarios":
            query = """
                SELECT c.nombre, h.dia_semana, h.hora_inicio 
                FROM horarios h
                JOIN cursos c ON h.id_curso = c.id_curso
                JOIN matriculas m ON c.id_curso = m.id_curso
                WHERE m.id_estudiante = %s
            """
            cursor.execute(query, (id_estudiante,))
            clases = cursor.fetchall()
            
            if clases:
                respuesta = "📅 Tu horario semanal:\n"
                for c in clases:
                    respuesta += f"- {c['nombre']} | {c['dia_semana']} | {c['hora_inicio']}\n"
            else:
                respuesta = "No se encontraron horarios matriculados."

        elif intencion == "notas":
            query = "SELECT promedio_actual, tareas_entregadas, tareas_pendientes FROM dataset_rendimiento WHERE id_estudiante = %s"
            cursor.execute(query, (id_estudiante,))
            rendimiento = cursor.fetchone()
            
            if rendimiento:
                respuesta = f"📊 Tu rendimiento académico:\n- Promedio actual: {rendimiento['promedio_actual']}\n- Tareas entregadas: {rendimiento['tareas_entregadas']}\n- Tareas pendientes: {rendimiento['tareas_pendientes']}"
            else:
                respuesta = "No hay notas registradas aún."
        
        else:
            # [MODIFICADO] Ahora extraemos la respuesta predefinida desde la BD para las nuevas intenciones (apafa, qali_warma, etc.)
            cursor.execute("SELECT respuesta_predefinida FROM intenciones_nlp WHERE nombre_intencion = %s", (intencion,))
            resultado_bd = cursor.fetchone()
            if resultado_bd:
                respuesta = resultado_bd['respuesta_predefinida']
            else:
                respuesta = "He detectado tu consulta, pero aún estoy aprendiendo a procesarla."

        # 3. Registro del historial de consultas[cite: 3]
        # Se guarda la interacción para tener memoria (Asumimos id_usuario = 1 temporalmente para el estudiante en el prototipo)
        cursor.execute("""
            INSERT INTO historial_consultas (id_usuario, id_intencion, mensaje_texto, modalidad) 
            VALUES (1, (SELECT id_intencion FROM intenciones_nlp WHERE nombre_intencion = %s LIMIT 1), %s, 'Texto')
        """, (intencion, mensaje))
        conexion.commit()

    except Exception as e:
        respuesta = f"Hubo un error al procesar tu consulta: {e}"
    finally:
        cursor.close()
        conexion.close()

    return {"intencion": intencion, "respuesta": respuesta}

# Prueba rápida
if __name__ == "__main__":
    # Simulamos pruebas con regionalismos y "Out of Scope"
    pruebas = ["cuanto deuvo de pension", "oye causa cuentame un chiste", "q tareas tngo"]
    
    for p in pruebas:
        resultado = responder_chatbot(p, 1)
        print(f"\nUsuario: {p}")
        print(f"Intención detectada: {resultado['intencion']}")
        print(f"Chatbot responde:\n{resultado['respuesta']}")