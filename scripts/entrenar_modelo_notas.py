from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import mysql.connector
import pandas as pd
import numpy as np # [NUEVO] Importado para operaciones matemáticas en las métricas
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split # [NUEVO] Para aislar datos de prueba
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score # [NUEVO] Métricas exigidas
import joblib
import os

def entrenar_modelo():
    print("🔄 Iniciando entrenamiento de Regresión Lineal...")
    
    try:
        # Establecemos la conexión usando tus credenciales
        conexion = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            database=os.getenv("DB_NAME", "chatbot_siagie_db"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "")
        )
        
        # Consultamos la vista que ya incluye la nota_final calculada en SQL
        query = "SELECT promedio_actual, tareas_entregadas, tareas_pendientes, nota_final FROM dataset_rendimiento"
        df = pd.read_sql(query, conexion)
        conexion.close()
        
        print(f"📊 Registros extraídos de la vista para entrenamiento: {len(df)}")
        
        if len(df) == 0:
            print("⚠️ No hay suficientes datos en la BD para entrenar. Asegúrate de tener registros en la vista.")
            return None

        # Definimos las variables independientes (X) y la variable objetivo (y)
        X = df[['promedio_actual', 'tareas_entregadas', 'tareas_pendientes']]
        y = df['nota_final']
        
        # [NUEVO] PARTICIÓN DE DATOS: 80% para entrenar, 20% oculto para evaluar
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # [MODIFICADO] Entrenamos el modelo SOLO con los datos de entrenamiento (X_train)
        print("⚙️ Entrenando el algoritmo predictivo...")
        modelo = LinearRegression()
        modelo.fit(X_train, y_train)
        
        # [NUEVO] EVALUACIÓN EXPERIMENTAL SOBRE DATOS NO VISTOS
        y_pred = modelo.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        print("\n📊 MÉTRICAS REALES DE PREDICCIÓN (Conjunto de Prueba):")
        print(f"MAE (Error Absoluto Medio): {mae:.2f} puntos")
        print(f"RMSE (Raíz Error Cuadrático Medio): {rmse:.2f} puntos")
        print(f"R² (Varianza explicada): {r2:.4f}")
        
        # 1.Definir la carpeta y crearla si no existe
        carpeta_modelos = "modelos"
        if not os.path.exists(carpeta_modelos):
            os.makedirs(carpeta_modelos)
            
        # 2. Definir la ruta completa y guardar el archivo binario
        ruta_modelo = os.path.join(carpeta_modelos, 'modelo_notas.pkl')
        # Guardamos el modelo entrenado
        joblib.dump(modelo, ruta_modelo)
        
        print("\n✅ ¡Modelo predictivo entrenado y guardado exitosamente como 'modelo_notas.pkl'!")
        return modelo

    except Exception as e:
        print(f"❌ Error durante el entrenamiento del modelo de notas: {e}")
        return None

if __name__ == "__main__":
    entrenar_modelo()