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

# Inicializamos el stemmer en español fuera de la función para mayor rendimiento
stemmer = SnowballStemmer('spanish')

# [MODIFICADO] Hacemos que id_estudiante sea opcional (None por defecto) para permitir chat público
def responder_chatbot(mensaje, id_estudiante=None):
    """
    Procesa el mensaje del usuario, detecta la intención y consulta la BD.
    """
    # 1. Limpieza y Lematización del mensaje del usuario
    mensaje_limpio = re.sub(r'[^\w\s]', '', mensaje.lower())
    palabras = word_tokenize(mensaje_limpio)
    mensaje_lematizado = " ".join([stemmer.stem(p) for p in palabras])
    
    # 2. Identificación de la intención usando el texto lematizado
    texto_vectorizado = vectorizador.transform([mensaje_lematizado])
    intencion = modelo_nlp.predict(texto_vectorizado)[0]
    
    # ==========================================
    # [NUEVO] BARRERA DE SEGURIDAD DE DATOS (MODELO HÍBRIDO)
    # Protege la información acedémica según la Ley N° 29733[cite: 9]
    # ==========================================
    intenciones_privadas = ["pagos", "horarios", "notas", "tareas"]
    
    if intencion in intenciones_privadas and id_estudiante is None:
        return {
            "intencion": intencion, 
            "respuesta": "🔒 Para consultar tu información académica personal (notas, pagos, horarios o tareas), por favor **inicia sesión** en el Portal del Estudiante."
        }
    
    respuesta = ""
    
    # Consulta de información en base de datos
    conexion = obtener_conexion()
    if not conexion:
        return {"respuesta": "Error de conexión a la base de datos."}
        
    cursor = conexion.cursor(dictionary=True)
    
    try:
        # Generación de respuestas dinámicas
        
        # Manejo de "Out of Scope" (Fuera de contexto)
        if intencion == "desconocido":
            respuesta = "Lo siento, soy un asistente académico. Solo puedo ayudarte con temas institucionales, matrícula, notas, pagos, horarios y tareas."
            
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
                
        elif intencion == "tareas":
            query = """
                SELECT c.nombre AS curso, t.titulo, t.fecha_vencimiento, et.estado 
                FROM estado_tareas et
                JOIN tareas t ON et.id_tarea = t.id_tarea
                JOIN cursos c ON t.id_curso = c.id_curso
                WHERE et.id_estudiante = %s AND et.estado IN ('Pendiente', 'Atrasada')
                ORDER BY t.fecha_vencimiento ASC
            """
            cursor.execute(query, (id_estudiante,))
            tareas_pendientes = cursor.fetchall()
            
            if tareas_pendientes:
                respuesta = "📚 Estas son tus tareas asignadas que faltan entregar:\n"
                for tarea in tareas_pendientes:
                    respuesta += f"- {tarea['curso']}: {tarea['titulo']} | Vence: {tarea['fecha_vencimiento']} | Estado: {tarea['estado']}\n"
            else:
                respuesta = "✅ ¡Felicidades! Al parecer has entregado todo y no tienes tareas pendientes."
                
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
            # Consultas institucionales públicas (APAFA, Qali Warma, etc.)[cite: 9]
            cursor.execute("SELECT respuesta_predefinida FROM intenciones_nlp WHERE nombre_intencion = %s", (intencion,))
            resultado_bd = cursor.fetchone()
            if resultado_bd:
                respuesta = resultado_bd['respuesta_predefinida']
            else:
                respuesta = "He detectado tu consulta, pero aún estoy aprendiendo a procesarla."

        # Registro del historial de consultas
        # [MODIFICADO] Asignamos un usuario genérico (ej. 1) si es una consulta anónima para evitar errores de llave foránea
        id_historial = id_estudiante if id_estudiante is not None else 1
        cursor.execute("""
            INSERT INTO historial_consultas (id_usuario, id_intencion, mensaje_texto, modalidad) 
            VALUES (%s, (SELECT id_intencion FROM intenciones_nlp WHERE nombre_intencion = %s LIMIT 1), %s, 'Texto')
        """, (id_historial, intencion, mensaje))
        conexion.commit()

    except Exception as e:
        respuesta = f"Hubo un error al procesar tu consulta: {e}"
    finally:
        cursor.close()
        conexion.close()

    return {"intencion": intencion, "respuesta": respuesta}

# Prueba rápida
if __name__ == "__main__":
    # Simulamos pruebas de chat público (sin iniciar sesión) y privado
    pruebas = [
        {"mensaje": "informacion de apafa", "id": None}, 
        {"mensaje": "cuanto deuvo de pension", "id": None}, 
        {"mensaje": "cuanto deuvo de pension", "id": 1}
    ]
    
    for p in pruebas:
        resultado = responder_chatbot(p["mensaje"], p["id"])
        print(f"\nUsuario (Logueado: {p['id'] is not None}): {p['mensaje']}")
        print(f"Intención detectada: {resultado['intencion']}")
        print(f"Chatbot responde:\n{resultado['respuesta']}")