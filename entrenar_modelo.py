import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import re
# NUEVO: Importamos las librerías exigidas para partición de datos, regresión logística y evaluación
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

# 1. Creación del dataset simulado (Basado en requerimientos del SIAGIE)
# MODIFICADO: Agregamos más ejemplos para que el modelo tenga suficientes datos al dividirse
datos_simulados = {
    'consulta': [
        '¿Cuál es mi horario de clases para este ciclo?',
        'Necesito saber si tengo deudas pendientes de pensión o APAFA',
        '¿Cómo realizo el proceso de matrícula web?',
        'Quiero ver mi promedio de notas del curso de matemáticas',
        '¿A qué hora empiezan las clases el día lunes?',
        '¿Dónde pago la cuota de la matrícula?',
        'Ayuda con el sistema de intranet, no puedo entrar', # NUEVO
        '¿Cuándo inician las matrículas rezagadas?' # NUEVO
    ],
    'intencion': ['horario', 'pagos', 'matricula', 'notas', 'horario', 'pagos', 'soporte', 'matricula'] # MODIFICADO
}
df = pd.DataFrame(datos_simulados)

# 2. Preprocesamiento de texto
def limpiar_texto(texto):
    texto = texto.lower() 
    texto = re.sub(r'[^\w\s]', '', texto) 
    return texto

df['consulta_limpia'] = df['consulta'].apply(limpiar_texto)
# ELIMINADO: Se eliminaron los "print" de datos limpios para mantener la consola enfocada en los resultados del modelo

# 3. Vectorización TF-IDF
vectorizador = TfidfVectorizer()
# MODIFICADO: Cambiamos el nombre de las variables a X e y (estándar en Machine Learning para "features" y "target")
X = vectorizador.fit_transform(df['consulta_limpia'])
y = df['intencion']

# ELIMINADO: Se eliminaron los "print" de vocabulario y dimensiones de matriz

# 4. Partición de datos exigida por el diseño experimental (Train/Test)
# NUEVO: Dividimos el 70% de datos para entrenar el algoritmo y el 30% para probar su eficacia
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 5. Entrenamiento del Modelo de Regresión Logística
# NUEVO: Creamos el modelo inteligente y lo entrenamos con los datos particionados
modelo = LogisticRegression()
modelo.fit(X_train, y_train)

# 6. Evaluación del modelo con métricas de clasificación
# NUEVO: Hacemos que el modelo clasifique los datos de prueba y mostramos su precisión
y_pred = modelo.predict(X_test)
print("--- Reporte de Clasificación en Datos de Prueba ---")
print(classification_report(y_test, y_pred, zero_division=0))

# 7. Prueba en tiempo real con una consulta nueva
# NUEVO: Simulamos que un estudiante real escribe en el chatbot
consulta_nueva = ["hola, necesito pagar la mensualidad del colegio"]
consulta_nueva_limpia = [limpiar_texto(consulta_nueva[0])]
X_nueva = vectorizador.transform(consulta_nueva_limpia)
prediccion = modelo.predict(X_nueva)

print(f"\nConsulta del estudiante: '{consulta_nueva[0]}'")
print(f"Intención detectada por la IA: {prediccion[0].upper()}")