import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib 

# 1. Dataset de entrenamiento NLP (Consultas estudiantiles)
consultas = [
    ("quiero ver mis notas", "notas"), 
    ("cuanto debo de pension", "pagos"), 
    ("horario de clases", "horario"), 
    ("tengo tareas pendientes", "tareas"),
    ("cuando es el examen", "horario"), 
    ("pagar mensualidad", "pagos"),
    ("boleta de notas", "notas"), 
    ("subir mi tarea", "tareas")
] * 10  # Multiplicamos para generar volumen de entrenamiento
df_nlp = pd.DataFrame(consultas, columns=["texto", "intencion"])

# 2. Vectorización TF-IDF (Transformar texto a números)
vectorizador = TfidfVectorizer()
X = vectorizador.fit_transform(df_nlp['texto'])
y = df_nlp['intencion']

# 3. Entrenamiento del Modelo de Clasificación (Regresión Logística)
modelo_nlp = LogisticRegression()
modelo_nlp.fit(X, y)

# 4. Exportación de los archivos .pkl
# Al ejecutar desde la raíz del proyecto, apuntamos directamente a la carpeta 'modelos'
joblib.dump(modelo_nlp, 'modelos/modelo_chatbot.pkl')
joblib.dump(vectorizador, 'modelos/vectorizer.pkl')

print("✅ Entrenamiento NLP finalizado.")
print("Archivos 'modelo_chatbot.pkl' y 'vectorizer.pkl' generados en la carpeta 'modelos'.")