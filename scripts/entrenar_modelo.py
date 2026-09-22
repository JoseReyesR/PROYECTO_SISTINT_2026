import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import os

def entrenar_chatbot_nlp():
    print("🧠 Entrenando el modelo NLP del Chatbot...")
    
    # 1. Dataset de entrenamiento (Frases comunes de estudiantes)
    # En un entorno de producción masivo, esto vendría de la base de datos, 
    # pero para el prototipo usamos un corpus predefinido de intenciones.
    datos = {
        "texto": [
            "quiero ver mis pagos", "cuanto debo", "tengo deudas pendientes", "estado de cuenta", "pagar pension",
            "cual es mi horario", "a que hora me toca clases", "que curso tengo hoy", "ver mi horario", "clases de hoy",
            "como voy en mis notas", "quiero ver mi promedio", "estoy jalando?", "cuales son mis calificaciones", "rendimiento academico",
            "tengo tareas pendientes", "que tareas me faltan", "actividades pendientes", "deje alguna tarea", "entregas de cursos"
        ],
        "intencion": [
            "pagos", "pagos", "pagos", "pagos", "pagos",
            "horarios", "horarios", "horarios", "horarios", "horarios",
            "notas", "notas", "notas", "notas", "notas",
            "tareas", "tareas", "tareas", "tareas", "tareas"
        ]
    }
    
    df = pd.DataFrame(datos)
    
    # 2. Vectorización TF-IDF: Convierte el texto a números para que la IA lo entienda
    vectorizador = TfidfVectorizer()
    X = vectorizador.fit_transform(df['texto'])
    y = df['intencion']
    
    # 3. Entrenamiento con Regresión Logística
    modelo_nlp = LogisticRegression()
    modelo_nlp.fit(X, y)
    
    # 4. Asegurarnos de guardar los archivos en la carpeta correcta
    carpeta_modelos = "modelos"
    if not os.path.exists(carpeta_modelos):
        os.makedirs(carpeta_modelos)
        
    ruta_modelo = os.path.join(carpeta_modelos, "modelo_chatbot.pkl")
    ruta_vectorizador = os.path.join(carpeta_modelos, "vectorizer.pkl")
    
    # 5. Exportar los archivos .pkl
    joblib.dump(modelo_nlp, ruta_modelo)
    joblib.dump(vectorizador, ruta_vectorizador)
    
    print(f"✅ ¡Modelo NLP entrenado con éxito!")
    print(f"📁 Archivos generados: '{ruta_modelo}' y '{ruta_vectorizador}'")

if __name__ == "__main__":
    entrenar_chatbot_nlp()