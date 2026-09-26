import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import os
import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
import re

nltk.download('punkt')
nltk.download('punkt_tab')

def entrenar_chatbot_nlp():
    print("🧠 Entrenando el modelo NLP Híbrido (Privado + Público)...")
    
    # 1. CORPUS EXPANDIDO
    datos = {
        "texto": [
            # INTENCIONES PRIVADAS ORIGINALES
            "quiero ver mis pagos", "cuanto debo", "tengo deudas pendientes", "estado de cuenta", "pagar pension",
            "cuanto deuvo", "q debo", "hay q pagar algo", "deuda de pension", "voucher de pago", 
            
            "cual es mi horario", "a que hora me toca clases", "que curso tengo hoy", "ver mi horario", "clases de hoy",
            "a q hora entro", "q toca hoy", "horario de mañana", "cuando me toca mate", "hora de salida", 
            
            "como voy en mis notas", "quiero ver mi promedio", "estoy jalando?", "cuales son mis calificaciones", "rendimiento academico",
            "q notas tengo", "pase de año?", "mi libreta", "notas del bimestre", "promedio final", 
            
            "tengo tareas pendientes", "que tareas me faltan", "actividades pendientes", "deje alguna tarea", "entregas de cursos",
            "q tareas tngo", "hay tarea hoy", "tareas para la casa", "deberes pendientes", "q dejaron de tarea", 
            
            # [NUEVO] INTENCIÓN: ASISTENCIA
            "mi asistencia", "cuantas faltas tengo", "he faltado mucho", "registro de asistencia", "asisti a clases",
            "tengo inasistencias", "ver mis faltas", "reporte de asistencia", "llegue tarde", "estado de asistencia",

            # [NUEVO] INTENCIÓN: CURSOS
            "que cursos llevo", "mis cursos", "materias matriculadas", "cursos de este año", "en que cursos estoy",
            "lista de cursos", "mis materias", "que cursos me tocan", "ver mis cursos", "cursos asignados",

            # INTENCIONES PÚBLICAS
            "requisitos de apafa", "pagar apafa", "cuota de apafa", "que es apafa", "informacion de apafa",
            "qali warma", "menu escolar", "desayuno qali warma", "alimentos qali warma", "entrega de qali warma",
            "certificado de estudios", "como saco mi certificado", "constancia de estudios", "tramitar certificado", "papeles de estudio",
            
            # FUERA DE CONTEXTO
            "hola", "que tal", "como estas", "cuentame un chiste", "va a llover hoy", 
            "quien ganara el partido", "de que equipo eres", "oye causa", "habla bateria", "que hora es"
        ],
        "intencion": [
            "pagos"] * 10 + ["horarios"] * 10 + ["notas"] * 10 + ["tareas"] * 10 + \
            ["asistencia"] * 10 + ["cursos"] * 10 + \
            ["apafa"] * 5 + ["qali_warma"] * 5 + ["certificados"] * 5 + ["desconocido"] * 10
    }
    
    df = pd.DataFrame(datos)
    
    # 2. LEMATIZACIÓN
    stemmer = SnowballStemmer('spanish')
    
    def limpiar_y_lematizar(texto):
        texto = re.sub(r'[^\w\s]', '', texto.lower())
        palabras = word_tokenize(texto)
        return " ".join([stemmer.stem(p) for p in palabras])

    print("⚙️ Lematizando el corpus de entrenamiento...")
    df['texto_procesado'] = df['texto'].apply(limpiar_y_lematizar)
    
    # 3. VECTORIZACIÓN Y ENTRENAMIENTO
    vectorizador = TfidfVectorizer()
    X = vectorizador.fit_transform(df['texto_procesado'])
    y = df['intencion']
    
    modelo_nlp = LogisticRegression()
    modelo_nlp.fit(X, y)
    
    carpeta_modelos = "modelos"
    if not os.path.exists(carpeta_modelos):
        os.makedirs(carpeta_modelos)
        
    joblib.dump(modelo_nlp, os.path.join(carpeta_modelos, "modelo_chatbot.pkl"))
    joblib.dump(vectorizador, os.path.join(carpeta_modelos, "vectorizer.pkl"))
    
    print(f"✅ ¡Modelo NLP entrenado con éxito reconociendo {len(df['intencion'].unique())} intenciones distintas!")

if __name__ == "__main__":
    entrenar_chatbot_nlp()