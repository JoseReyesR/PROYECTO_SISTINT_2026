import joblib

print("🔍 Inspeccionando los 4 archivos .pkl del proyecto SISTINT...\n")

try:
    # 1. Cargar Modelo NLP (Regresión Logística)
    print("=== 1. MODELO NLP (Regresión Logística) ===")
    modelo_chatbot = joblib.load("modelos/modelo_chatbot.pkl")
    print(f"Intenciones aprendidas (Clases): {modelo_chatbot.classes_}")
    print(f"Dimensiones de la matriz de pesos: {modelo_chatbot.coef_.shape}")
    print("*(Muestra de que la IA diferenció matemáticamente las intenciones)*\n")

    # 2. Cargar Vectorizador (TF-IDF)
    print("=== 2. VECTORIZADOR (TF-IDF) ===")
    vectorizer = joblib.load("modelos/vectorizer.pkl")
    vocabulario = vectorizer.get_feature_names_out()
    print(f"Total de palabras únicas vectorizadas: {len(vocabulario)}")
    print(f"Muestra del vocabulario (primeras 15): {vocabulario[:15]}\n")

    # 3. Cargar Modelo de Notas (Regresión Lineal)
    print("=== 3. MODELO DE NOTAS (Regresión Lineal) ===")
    modelo_notas = joblib.load("modelos/modelo_notas.pkl")
    print(f"Pesos de las variables (Promedio, Entregadas, Pendientes): {modelo_notas.coef_}")
    print(f"Intercepto base: {modelo_notas.intercept_}")
    print("*(Demuestra cómo la IA pondera cada variable para calcular la nota)*\n")

    # 4. Cargar Modelo de Perfil (K-Means)
    print("=== 4. MODELO DE PERFILAMIENTO (K-Means) ===")
    modelo_perfil = joblib.load("modelos/modelo_perfil_usuario.pkl")
    print(f"Número de grupos formados: {modelo_perfil.n_clusters}")
    print(f"Centroides exactos de cada perfil:\n{modelo_perfil.cluster_centers_}")
    print("*(Evidencia del agrupamiento no supervisado)*\n")

    print("✅ ¡Lectura exitosa! Adjunta la captura de esta consola en tu informe académico.")

except FileNotFoundError as e:
    print(f"❌ No se encontró el archivo: {e}. Asegúrate de ejecutar esto desde la raíz del proyecto.")
except Exception as e:
    print(f"❌ Error al leer los modelos: {e}")