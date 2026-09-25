import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import os
import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
import re

# Descargar paquetes necesarios de NLTK (solo se descargan la primera vez)
nltk.download('punkt')
nltk.download('punkt_tab')

def entrenar_chatbot_nlp():
    print("🧠 Entrenando el modelo NLP Avanzado del Chatbot...")
    
    # ==========================================
    # 1. CORPUS EXPANDIDO (100 Frases)
    # Incluye regionalismos ("jalando", "causa"), errores ortográficos ("tngo", "deuvo") 
    # y la nueva intención "desconocido" (Out of Scope).
    # ==========================================
    datos = {
        "texto": [
            # INTENCIÓN: PAGOS
            "quiero ver mis pagos", "cuanto debo", "tengo deudas pendientes", "estado de cuenta", "pagar pension",
            "cuanto deuvo", "q debo", "hay q pagar algo", "deuda de apafa", "voucher de pago", 
            "pension atrasada", "cuanto es la pension", "debo algo al colegio", "me toca pagar", "mensualidad", 
            "costo de matricula", "donde pago", "nro de cuenta", "cuanto falta pagar", "historial de pagos",
            
            # INTENCIÓN: HORARIOS
            "cual es mi horario", "a que hora me toca clases", "que curso tengo hoy", "ver mi horario", "clases de hoy",
            "a q hora entro", "q toca hoy", "horario de mañana", "cuando me toca mate", "hora de salida", 
            "hora de recreo", "cronograma de clases", "q dias estudio", "turno mañana o tarde", "horario de la semana", 
            "a que hora empiezan las clases", "mi itinerario", "cursos de hoy", "a que hora salgo", "q toca ahora",
            
            # INTENCIÓN: NOTAS
            "como voy en mis notas", "quiero ver mi promedio", "estoy jalando?", "cuales son mis calificaciones", "rendimiento academico",
            "q notas tengo", "pase de año?", "mi libreta", "notas del bimestre", "promedio final", 
            "cuanto saque en mate", "estoy aprobado", "me jalaron", "quiero ver mis notas", "calificaciones actuales", 
            "historial de notas", "mi ponderado", "he jalado algun curso", "como voy en el colegio", "mis resultados",
            
            # INTENCIÓN: TAREAS
            "tengo tareas pendientes", "que tareas me faltan", "actividades pendientes", "deje alguna tarea", "entregas de cursos",
            "q tareas tngo", "hay tarea hoy", "tareas para la casa", "deberes pendientes", "q dejaron de tarea", 
            "trabajos grupales", "practicas para enviar", "falta entregar algo?", "asignaciones pendientes", "tareas atrasadas", 
            "tengo que enviar algo", "proyectos finales", "que trabajos me faltan", "mis tareas", "reportes por enviar",
            
            # INTENCIÓN: DESCONOCIDO (Out of Scope / Fuera de Contexto)
            "hola", "que tal", "como estas", "cuentame un chiste", "va a llover hoy", 
            "quien ganara el partido", "de que equipo eres", "oye causa", "habla bateria", "que hora es", 
            "quien es el presidente", "como preparo ceviche", "cantame una cancion", "buenos dias", "adios", 
            "chao", "eres un robot", "me aburro", "que haces", "te gusta el futbol"
        ],
        "intencion": [
            "pagos"] * 20 + ["horarios"] * 20 + ["notas"] * 20 + ["tareas"] * 20 + ["desconocido"] * 20
    }
    
    df = pd.DataFrame(datos)
    
    # ==========================================
    # 2. LEMATIZACIÓN PREVIA (Stemming en Español)
    # Reduce palabras a su raíz para disminuir la confusión del modelo.
    # ==========================================
    stemmer = SnowballStemmer('spanish')
    
    def limpiar_y_lematizar(texto):
        # Quitar signos de puntuación y convertir a minúsculas
        texto = re.sub(r'[^\w\s]', '', texto.lower())
        palabras = word_tokenize(texto)
        # Extraer la raíz de cada palabra (ej. "pagaré", "pagado" -> "pag")
        palabras_raiz = [stemmer.stem(p) for p in palabras]
        return " ".join(palabras_raiz)

    # Aplicamos la limpieza al corpus
    print("⚙️ Lematizando el corpus de entrenamiento...")
    df['texto_procesado'] = df['texto'].apply(limpiar_y_lematizar)
    
    # ==========================================
    # 3. VECTORIZACIÓN Y ENTRENAMIENTO
    # Se usa TF-IDF y Regresión Logística por su alta eficiencia y rapidez[cite: 4, 5].
    # ==========================================
    vectorizador = TfidfVectorizer()
    X = vectorizador.fit_transform(df['texto_procesado'])
    y = df['intencion']
    
    modelo_nlp = LogisticRegression()
    modelo_nlp.fit(X, y)
    
    # Guardar los archivos
    carpeta_modelos = "modelos"
    if not os.path.exists(carpeta_modelos):
        os.makedirs(carpeta_modelos)
        
    ruta_modelo = os.path.join(carpeta_modelos, "modelo_chatbot.pkl")
    ruta_vectorizador = os.path.join(carpeta_modelos, "vectorizer.pkl")
    
    joblib.dump(modelo_nlp, ruta_modelo)
    joblib.dump(vectorizador, ruta_vectorizador)
    
    print(f"✅ ¡Modelo NLP avanzado entrenado con éxito con {len(df)} frases!")
    print(f"📁 Archivos generados: '{ruta_modelo}' y '{ruta_vectorizador}'")

if __name__ == "__main__":
    entrenar_chatbot_nlp()