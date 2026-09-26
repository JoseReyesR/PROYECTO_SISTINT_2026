import joblib
import re 
import nltk 
from nltk.stem.snowball import SnowballStemmer 
from nltk.tokenize import word_tokenize 
from conexion_sql import obtener_conexion

print("Cargando modelos NLP...")
modelo_nlp = joblib.load("modelos/modelo_chatbot.pkl")
vectorizador = joblib.load("modelos/vectorizer.pkl")

stemmer = SnowballStemmer('spanish')

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
    # [MODIFICADO] BARRERA DE SEGURIDAD DE DATOS
    # ==========================================
    # [NUEVO] Se añadieron 'asistencia' y 'cursos' a las rutas protegidas
    intenciones_privadas = ["pagos", "horarios", "notas", "tareas", "asistencia", "cursos"]
    
    if intencion in intenciones_privadas and id_estudiante is None:
        return {
            "intencion": intencion, 
            "respuesta": "🔒 Para consultar tu información académica personal, por favor **inicia sesión** en el Portal del Estudiante."
        }
    
    respuesta = ""
    
    conexion = obtener_conexion()
    if not conexion:
        return {"respuesta": "Error de conexión a la base de datos."}
        
    cursor = conexion.cursor(dictionary=True)
    
    try:
        if intencion == "desconocido":
            respuesta = "Lo siento, soy un asistente académico. Solo puedo ayudarte con temas institucionales, matrícula, notas, pagos, horarios, cursos, asistencia y tareas."
            
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
                
        # ==========================================
        # [NUEVO] INTENCIONES DE CURSOS Y ASISTENCIA
        # ==========================================
        elif intencion == "cursos":
            query = """
                SELECT c.nombre, m.anio_escolar 
                FROM matriculas m
                JOIN cursos c ON m.id_curso = c.id_curso
                WHERE m.id_estudiante = %s
            """
            cursor.execute(query, (id_estudiante,))
            cursos_matriculados = cursor.fetchall()
            
            if cursos_matriculados:
                respuesta = "📘 Estás matriculado en los siguientes cursos:\n"
                for c in cursos_matriculados:
                    respuesta += f"- {c['nombre']} (Año: {c['anio_escolar']})\n"
            else:
                respuesta = "No se encontraron cursos matriculados para tu perfil."

        elif intencion == "asistencia":
            query = """
                SELECT a.fecha, a.estado 
                FROM asistencias a
                JOIN matriculas m ON a.id_matricula = m.id_matricula
                WHERE m.id_estudiante = %s
                ORDER BY a.fecha DESC LIMIT 7
            """
            cursor.execute(query, (id_estudiante,))
            asistencias = cursor.fetchall()
            
            if asistencias:
                respuesta = "📅 Tu registro de asistencia reciente:\n"
                for a in asistencias:
                    respuesta += f"- Fecha: {a['fecha']} | Estado: {a['estado']}\n"
            else:
                respuesta = "No tienes registros de asistencia en el sistema."
        
        else:
            # Consultas institucionales públicas (APAFA, Qali Warma, etc.)
            cursor.execute("SELECT respuesta_predefinida FROM intenciones_nlp WHERE nombre_intencion = %s", (intencion,))
            resultado_bd = cursor.fetchone()
            if resultado_bd:
                respuesta = resultado_bd['respuesta_predefinida']
            else:
                respuesta = "He detectado tu consulta, pero aún estoy aprendiendo a procesarla."

        # Registro del historial de consultas
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