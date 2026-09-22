import joblib
from conexion_sql import obtener_conexion

print("Cargando modelos NLP...")
# Cargar los modelos previamente entrenados
modelo_nlp = joblib.load("modelos/modelo_chatbot.pkl")
vectorizador = joblib.load("modelos/vectorizer.pkl")

def responder_chatbot(mensaje, id_estudiante):
    """
    Procesa el mensaje del estudiante, detecta la intención y consulta la BD.
    """
    # 1. Identificación de la intención del usuario mediante NLP
    texto_vectorizado = vectorizador.transform([mensaje])
    intencion = modelo_nlp.predict(texto_vectorizado)[0]
    
    respuesta = ""
    
    # 2. Consulta de información en base de datos[cite: 3]
    conexion = obtener_conexion()
    if not conexion:
        return {"respuesta": "Error de conexión a la base de datos."}
        
    cursor = conexion.cursor(dictionary=True)
    
    try:
        # Generación de respuestas dinámicas[cite: 3]
        if intencion == "pagos":
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
            respuesta = "He detectado una consulta sobre tus tareas o cursos, pero aún estoy aprendiendo a mostrar esos detalles."

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
    # Simulamos que el estudiante con ID 1 pregunta por sus deudas
    prueba_mensaje = "cuanto debo de pension"
    resultado = responder_chatbot(prueba_mensaje, 1)
    print(f"\nUsuario: {prueba_mensaje}")
    print(f"Intención detectada: {resultado['intencion']}")
    print(f"Chatbot responde:\n{resultado['respuesta']}")