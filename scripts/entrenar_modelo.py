import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import re
# NUEVO: Importamos la librería para conversión de voz a texto
import speech_recognition as sr 

# 1. Dataset Simulado Ampliado
datos_simulados = {
    'consulta': [
        '¿Cuál es mi horario de clases para este ciclo?',
        'Necesito saber si tengo deudas pendientes de pensión o APAFA',
        '¿Cómo realizo el proceso de matrícula web?',
        'Quiero ver mi promedio de notas del curso de matemáticas',
        '¿A qué hora empiezan las clases el día lunes?',
        '¿Dónde pago la cuota de la matrícula?',
        'Ayuda con el sistema de intranet, no puedo entrar', 
        '¿Cuándo inician las matrículas rezagadas?',
        'quiero pagar mi mensualidad', # NUEVO: Agregamos vocabulario de pagos
        'dime mis notas' # NUEVO: Agregamos vocabulario de notas
    ],
    'intencion': ['horario', 'pagos', 'matricula', 'notas', 'horario', 'pagos', 'soporte', 'matricula', 'pagos', 'notas'] 
}
df = pd.DataFrame(datos_simulados)

# 2. Preprocesamiento de texto
def limpiar_texto(texto):
    texto = texto.lower()
    return re.sub(r'[^\w\s]', '', texto) 

df['consulta_limpia'] = df['consulta'].apply(limpiar_texto)

# 3. Vectorización TF-IDF
vectorizador = TfidfVectorizer()
X = vectorizador.fit_transform(df['consulta_limpia'])
y = df['intencion']

# 4. Partición de datos
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 5. Entrenamiento del Modelo
modelo = LogisticRegression()
modelo.fit(X_train, y_train)

# ELIMINADO: Se eliminó el reporte de clasificación (classification_report) momentáneamente para enfocarnos en la prueba de voz.
# ELIMINADO: Se eliminó la variable consulta_nueva con texto estático escrito a mano.

# NUEVO: Función para capturar audio del micrófono y convertirlo a texto
def escuchar_estudiante():
    reconocedor = sr.Recognizer()
    with sr.Microphone() as origen:
        print("\n" + "="*50)
        print("🎤 ESTOY ESCUCHANDO... (Habla ahora, ej: 'quiero pagar mi mensualidad')")
        print("="*50)
        # Ajusta el ruido de fondo y escucha
        reconocedor.adjust_for_ambient_noise(origen)
        audio = reconocedor.listen(origen)
        
        try:
            print("⏳ Procesando voz a texto...")
            # Convierte el audio a texto usando Google Speech Recognition
            texto_transcrito = reconocedor.recognize_google(audio, language="es-PE")
            return texto_transcrito
        except sr.UnknownValueError:
            print("❌ No pude entender el audio. Intenta hablar más claro.")
            return None
        except sr.RequestError:
            print("❌ Error de conexión con el servicio de reconocimiento.")
            return None

# MODIFICADO: Evaluamos la IA usando el texto que proviene del micrófono
consulta_voz = escuchar_estudiante()

if consulta_voz:
    print(f"\n🗣️ Tú dijiste: '{consulta_voz}'")
    
    # Procesamos la voz transcrita pasándola por el mismo flujo NLP
    consulta_limpia = [limpiar_texto(consulta_voz)]
    X_nueva = vectorizador.transform(consulta_limpia)
    prediccion = modelo.predict(X_nueva)
    
    print(f"🤖 Intención detectada por la IA: {prediccion[0].upper()}")