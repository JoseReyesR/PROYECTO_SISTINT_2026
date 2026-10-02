import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os
import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
import re

nltk.download('punkt')
nltk.download('punkt_tab')

def entrenar_chatbot_nlp_riguroso():
    print("🧠 Entrenando el modelo NLP con Validación Experimental (Corpus 300+)...")
    
    # 1. CORPUS EXPANDIDO (30 ejemplos por clase = 300 registros)
    datos = {
        "texto": [
            # 1. PAGOS
            "quiero ver mis pagos", "cuanto debo", "tengo deudas pendientes", "estado de cuenta", "pagar pension",
            "cuanto deuvo", "q debo", "hay q pagar algo", "deuda de pension", "voucher de pago", 
            "mensualidad", "debo este mes", "donde pago la pension", "numero de cuenta para pagar", "como pago la cuota", 
            "me falta pagar", "deuda actual", "quiero cancelar mi deuda", "pago de matricula", "confirmar pago", 
            "envie mi voucher", "validar mi pago", "cuanto es la cuota", "recibo de pago", "costo de la pension", 
            "estoy al dia en pagos", "pagos atrasados", "morosidad", "donde deposito", "caja del colegio",
            
            # 2. HORARIOS
            "cual es mi horario", "a que hora me toca clases", "que curso tengo hoy", "ver mi horario", "clases de hoy",
            "a q hora entro", "q toca hoy", "horario de mañana", "cuando me toca mate", "hora de salida",
            "a que hora termina la clase", "horario del martes", "que toca el lunes", "horario de recreo", "a que hora empieza", 
            "horario escolar", "cronograma de clases", "toca educacion fisica", "hora de ingreso", "turno tarde", 
            "turno mañana", "malla horaria", "hora de tutoria", "a que hora salimos", "cuando hay clases", 
            "dias de clase", "feriado escolar", "horario de examenes", "cuando toca computo", "toca ingles hoy",
            
            # 3. NOTAS
            "como voy en mis notas", "quiero ver mi promedio", "estoy jalando?", "cuales son mis calificaciones", "rendimiento academico",
            "q notas tengo", "pase de año?", "mi libreta", "notas del bimestre", "promedio final",
            "aprobe el curso", "nota de matematica", "saque buena nota", "libreta de notas", "donde veo mis notas", 
            "reporte de calificaciones", "desaprobe", "estoy invicto", "boleta de notas", "notas finales", 
            "cual es mi puntaje", "me falta nota", "promedios", "libreta virtual", "notas de historia", 
            "nota del examen", "calificacion final", "nota minima para aprobar", "cuadro de merito", "mis resultados",
            
            # 4. TAREAS
            "tengo tareas pendientes", "que tareas me faltan", "actividades pendientes", "deje alguna tarea", "entregas de cursos",
            "q tareas tngo", "hay tarea hoy", "tareas para la casa", "deberes pendientes", "q dejaron de tarea",
            "cual es la tarea", "donde subo mi tarea", "tarea de mate", "trabajo de investigacion", "plazo de la tarea", 
            "hasta cuando presento", "no hice la tarea", "tarea atrasada", "practicas pendientes", "asginaciones", 
            "proyecto final", "exposicion", "que hay para mañana", "ejercicios de casa", "mandaron tarea", 
            "revisar mis tareas", "tarea revisada", "entregar trabajo", "enviar tarea", "plataforma de tareas",
            
            # 5. ASISTENCIA
            "mi asistencia", "cuantas faltas tengo", "he faltado mucho", "registro de asistencia", "asisti a clases",
            "tengo inasistencias", "ver mis faltas", "reporte de asistencia", "llegue tarde", "estado de asistencia",
            "tardanzas", "justificar falta", "cuantas veces falte", "inasistencia injustificada", "me pusieron falta", 
            "asistencia de hoy", "estuve presente", "llamar lista", "control de asistencia", "faltas acumuladas", 
            "cuantas faltas para jalar", "justificacion medica", "llegue temprano", "asistencia del mes", "faltas permitidas", 
            "reporte de tardanzas", "limite de inasistencias", "puedo faltar hoy", "inasistencias del bimestre", "ausencias",
            
            # 6. CURSOS
            "que cursos llevo", "mis cursos", "materias matriculadas", "cursos de este año", "en que cursos estoy",
            "lista de cursos", "mis materias", "que cursos me tocan", "ver mis cursos", "cursos asignados",
            "malla curricular", "areas de estudio", "nombre de los cursos", "cursos de secundaria", "curso de mate", 
            "profesor del curso", "cuantos cursos son", "cursos extracurriculares", "talleres", "curso de ciencias", 
            "materias de hoy", "asignaturas", "cursos reprobados", "cursos aprobados", "creditos del curso", 
            "silabo del curso", "que es este curso", "curso obligatorio", "curso electivo", "lista de profesores",
            
            # 7. APAFA
            "requisitos de apafa", "pagar apafa", "cuota de apafa", "que es apafa", "informacion de apafa",
            "inscripcion apafa", "reunion de apafa", "directiva apafa", "pago anual apafa", "deuda apafa", 
            "donde se paga apafa", "voucher apafa", "asamblea de padres", "comite de aula", "presidente de apafa", 
            "monto de apafa", "multa apafa", "empadronamiento apafa", "carnet de apafa", "donacion apafa", 
            "actividades de apafa", "kermesse apafa", "asamblea general", "elecciones apafa", "reuniones de padres", 
            "multa por no ir a reunion", "directiva de padres", "escuela de padres", "constancia de no adeudo apafa", "beneficios apafa",
            
            # 8. QALI WARMA
            "qali warma", "menu escolar", "desayuno qali warma", "alimentos qali warma", "entrega de qali warma",
            "productos qali warma", "cuando reparten alimentos", "raciones", "desayuno escolar", "cronograma qali warma", 
            "almuerzo escolar", "qali warma hoy", "recojo de alimentos", "canasta qali warma", "beneficiarios qali warma", 
            "programa qali warma", "que daran hoy", "alimentos del estado", "nutritivo", "lonchera escolar", 
            "avena qali warma", "leche qali warma", "raciones de comida", "quejas qali warma", "control de alimentos", 
            "proveedor qali warma", "entrega de canastas", "qaliwarma", "menu del dia", "raciones estado",
            
            # 9. CERTIFICADOS
            "certificado de estudios", "como saco mi certificado", "constancia de estudios", "tramitar certificado", "papeles de estudio",
            "constancia de matricula", "constancia de conducta", "certificado oficial", "visado de certificado", "solicitar certificado", 
            "cuanto cuesta el certificado", "requisitos certificado", "mesa de partes certificado", "recojo de certificado", "tiempo de tramite", 
            "certificado de notas", "constancia de tercio superior", "certificado de egresado", "documentos para traslado", "constancia de estudios vigente", 
            "formato de certificado", "certificado ugel", "firma de director", "tramites documentarios", "sacar papeles", 
            "solicitud de constancia", "formato unico de tramite", "emitir certificado", "duplicado de certificado", "certificado digital",
            
            # 10. DESCONOCIDO / CHITCHAT
            "hola", "que tal", "como estas", "cuentame un chiste", "va a llover hoy", 
            "quien ganara el partido", "de que equipo eres", "oye causa", "habla bateria", "que hora es",
            "buenos dias", "buenas tardes", "buenas noches", "adios", "chao", 
            "eres un robot", "como te llamas", "cuantos años tienes", "me aburro", "que haces", 
            "te gusta la pizza", "dime algo", "eres humano", "inteligencia artificial", "saludos", 
            "alianza o u", "juega peru", "ayudame con algo", "no se que hacer", "dimelo"
        ],
        "intencion": (
            ["pagos"] * 30 + ["horarios"] * 30 + ["notas"] * 30 + ["tareas"] * 30 + 
            ["asistencia"] * 30 + ["cursos"] * 30 + ["apafa"] * 30 + ["qali_warma"] * 30 + 
            ["certificados"] * 30 + ["desconocido"] * 30
        )
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
    
    # 3. PARTICIÓN DE DATOS (Data Split 80/20)
    # Separamos ANTES de vectorizar para evitar Data Leakage
    X_train, X_test, y_train, y_test = train_test_split(
        df['texto_procesado'], 
        df['intencion'], 
        test_size=0.2, 
        random_state=42, 
        stratify=df['intencion'] # Garantiza misma proporción de clases
    )
    
    # 4. VECTORIZACIÓN (Aprende solo de Train, transforma Test)
    vectorizador = TfidfVectorizer()
    X_train_vec = vectorizador.fit_transform(X_train)
    X_test_vec = vectorizador.transform(X_test)
    
    # 5. ENTRENAMIENTO
    modelo_nlp = LogisticRegression()
    modelo_nlp.fit(X_train_vec, y_train)
    
    # 6. EVALUACIÓN EXPERIMENTAL REAL
    y_pred = modelo_nlp.predict(X_test_vec)
    
    print("\n📊 REPORTE DE CLASIFICACIÓN REAL SOBRE CONJUNTO DE PRUEBA (TEST SET):")
    print(classification_report(y_test, y_pred))
    
    # 7. GUARDADO
    carpeta_modelos = "modelos"
    if not os.path.exists(carpeta_modelos):
        os.makedirs(carpeta_modelos)
        
    joblib.dump(modelo_nlp, os.path.join(carpeta_modelos, "modelo_chatbot.pkl"))
    joblib.dump(vectorizador, os.path.join(carpeta_modelos, "vectorizer.pkl"))
    
    print(f"✅ ¡Modelo NLP entrenado y validado experimentalmente con éxito!")

if __name__ == "__main__":
    entrenar_chatbot_nlp_riguroso()