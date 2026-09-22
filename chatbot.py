import joblib

# 1. Cargar los modelos NLP entrenados en memoria
try:
    modelo_nlp = joblib.load('modelos/modelo_chatbot.pkl')
    vectorizador = joblib.load('modelos/vectorizer.pkl')
    print("✅ Motor Conversacional NLP cargado correctamente.")
except Exception as e:
    print(f"⚠️ Error al cargar el modelo NLP: {e}")

def responder_chatbot(mensaje, id_estudiante="Estudiante"):
    """
    Procesa el mensaje del usuario, detecta la intención matemática y devuelve una respuesta estructurada.
    """
    try:
        # Transformar el texto entrante a formato numérico (matriz TF-IDF)
        X_mensaje = vectorizador.transform([mensaje.lower()])
        
        # Predecir la intención usando Regresión Logística[cite: 14]
        intencion = modelo_nlp.predict(X_mensaje)[0]
        
        # Árbol de respuestas basado en la clasificación
        if intencion == "pagos":
            return f"💰 {id_estudiante}, he detectado una consulta sobre pagos. Puedes revisar tu estado de cuenta detallado en la sección 'Tu Rendimiento' o acercarte a tesorería."
        elif intencion == "horario":
            return f"📅 Sobre tu horario: Las clases inician a las 8:00 AM. Recuerda revisar el portal para posibles cambios de aula."
        elif intencion == "notas":
            return "📊 Para ver tus notas detalladas y promedios, utiliza el panel de predicción de rendimiento en tu dashboard."
        elif intencion == "tareas":
            return "📚 Tienes tareas pendientes. Recuerda que la entrega oportuna impacta directamente en tu riesgo académico."
        else:
            return "🤔 Entiendo tu consulta, pero necesito más detalles. ¿Podrías reformularla usando otras palabras?"
            
    except Exception as e:
        return "⚠️ Ocurrió un error al procesar tu mensaje. Intenta nuevamente."