import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import re

# 1. Creación del dataset simulado (Basado en requerimientos del SIAGIE)
datos_simulados = {
    'consulta': [
        '¿Cuál es mi horario de clases para este ciclo?',
        'Necesito saber si tengo deudas pendientes de pensión o APAFA',
        '¿Cómo realizo el proceso de matrícula web?',
        'Quiero ver mi promedio de notas del curso de matemáticas',
        '¿A qué hora empiezan las clases el día lunes?',
        '¿Dónde pago la cuota de la matrícula?'
    ],
    'intencion': ['horario', 'pagos', 'matricula', 'notas', 'horario', 'pagos']
}
df = pd.DataFrame(datos_simulados)

# 2. Preprocesamiento de texto
def limpiar_texto(texto):
    texto = texto.lower() # Convertir a minúsculas
    texto = re.sub(r'[^\w\s]', '', texto) # Eliminar signos de puntuación
    # Aquí se podrían eliminar las "stopwords" (palabras vacías como "el", "la", "de")
    return texto

df['consulta_limpia'] = df['consulta'].apply(limpiar_texto)
print("--- Datos Limpios ---")
print(df[['consulta_limpia', 'intencion']])

# 3. Vectorización TF-IDF
vectorizador = TfidfVectorizer()
X_tfidf = vectorizador.fit_transform(df['consulta_limpia'])
y_target = df['intencion']

print("\n--- Vocabulario TF-IDF ---")
print(vectorizador.get_feature_names_out())
print("\n--- Dimensiones de la Matriz Numérica ---")
print(X_tfidf.shape) # (Número de consultas, Número de palabras únicas)