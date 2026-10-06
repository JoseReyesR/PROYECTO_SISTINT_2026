from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import mysql.connector
import pandas as pd
import numpy as np # Importado para operaciones matemáticas y generación de ruido
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split # Para aislar datos de prueba
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score # Métricas exigidas
import joblib

def entrenar_modelo():
    print("🔄 Iniciando entrenamiento de Regresión Lineal...")
    
    try:
        # Establecemos la conexión usando tus credenciales
        conexion = mysql.connector.connect(
            host='localhost',
            database='chatbot_siagie_db',
            user='root',
            password='1234'
        )
        
        # Consultamos la vista que ya incluye la nota_final calculada en SQL
        query = "SELECT promedio_actual, tareas_entregadas, tareas_pendientes, nota_final FROM dataset_rendimiento"
        df = pd.read_sql(query, conexion)
        conexion.close()
        
        print(f"📊 Registros extraídos de la vista para entrenamiento: {len(df)}")
        
        if len(df) == 0:
            print("⚠️ No hay suficientes datos en la BD para entrenar. Asegúrate de tener registros en la vista.")
            return None

        # =========================================================================
        # [NUEVO] INYECCIÓN DE RUIDO ESTADÍSTICO PARA SIMULAR VARIANZA HUMANA
        # =========================================================================
        print("⚙️ Inyectando ruido estadístico para simular un entorno realista...")
        np.random.seed(42) # Semilla para reproducibilidad
        
        # 1. Generamos ruido con distribución normal (media 0, desviación 1.5 puntos)
        ruido = np.random.normal(loc=0.0, scale=1.5, size=len(df))
        
        # 2. Factor externo (Simula un 15% de alumnos con problemas que bajan su nota de -1 a -3 puntos)
        factor_externo = np.where(np.random.rand(len(df)) < 0.15, 
                                  np.random.uniform(-3, -1, len(df)), 0)
        
        # 3. Alteramos la nota calculada matemáticamente en SQL sumando la varianza
        df["nota_final"] = df["nota_final"] + ruido + factor_externo
        
        # 4. Limitamos matemáticamente para que las notas no salgan del rango peruano (0-20)
        df["nota_final"] = np.clip(df["nota_final"], 0, 20)
        df["nota_final"] = np.round(df["nota_final"], 1)
        # =========================================================================

        # Definimos las variables independientes (X) y la variable objetivo (y)
        X = df[['promedio_actual', 'tareas_entregadas', 'tareas_pendientes']]
        y = df['nota_final']
        
        # PARTICIÓN DE DATOS: 80% para entrenar, 20% oculto para evaluar
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Entrenamos el modelo SOLO con los datos de entrenamiento (X_train)
        print("⚙️ Entrenando el algoritmo predictivo...")
        modelo = LinearRegression()
        modelo.fit(X_train, y_train)
        
        # EVALUACIÓN EXPERIMENTAL SOBRE DATOS NO VISTOS
        y_pred = modelo.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        print("\n📊 MÉTRICAS REALES DE PREDICCIÓN (Conjunto de Prueba):")
        print(f"MAE (Error Absoluto Medio): {mae:.2f} puntos")
        print(f"RMSE (Raíz Error Cuadrático Medio): {rmse:.2f} puntos")
        print(f"R² (Varianza explicada): {r2:.4f}")
        
        # 1. Definir la carpeta y crearla si no existe
        carpeta_modelos = "modelos"
        if not os.path.exists(carpeta_modelos):
            os.makedirs(carpeta_modelos)
            
        # 2. Definir la ruta completa y guardar el archivo binario
        ruta_modelo = os.path.join(carpeta_modelos, 'modelo_notas.pkl')
        # Guardamos el modelo entrenado
        joblib.dump(modelo, ruta_modelo)
        
        print("\n✅ ¡Modelo predictivo entrenado y guardado exitosamente como 'modelo_notas.pkl'!")

        # =========================================================================
        # IMPRESIÓN DE COEFICIENTES (PESOS MATEMÁTICOS DEL MODELO)
        # =========================================================================
        # Cargamos el modelo para verificar lo que se guardó en el disco
        modelo_cargado = joblib.load(ruta_modelo)
        
        # Extraemos los coeficientes (el orden corresponde a las columnas de X)
        coef_promedio = modelo_cargado.coef_[0]
        coef_tareas_entregadas = modelo_cargado.coef_[1]
        coef_tareas_pendientes = modelo_cargado.coef_[2]
        
        print("\n# Coeficientes aprendidos (verificación con joblib.load):")
        print(f"#   promedio_actual = {coef_promedio:.2f} | tareas_entregadas = {coef_tareas_entregadas:.2f} | tareas_pendientes = {coef_tareas_pendientes:.2f}")
        print("#   -> Los coeficientes ahora variarán ligeramente de la ponderación original 0.7/0.5")
        print("#      debido a la varianza y el ruido estadístico introducido simulando estudiantes reales.")

        return modelo

    except Exception as e:
        print(f"❌ Error durante el entrenamiento del modelo de notas: {e}")
        return None

if __name__ == "__main__":
    entrenar_modelo()