import mysql.connector
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import os
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
        # Consultamos la vista o datos directos para la Regresión Lineal
        # Variable en caso no hay dataset en bd
        query_dataset_rendimiento = """
            SELECT 
                e.id_estudiante,
                COALESCE(AVG(et.calificacion), 10.0) AS promedio_actual,
                SUM(CASE WHEN et.estado = 'Entregada' THEN 1 ELSE 0 END) AS tareas_entregadas,
                SUM(CASE WHEN et.estado = 'Pendiente' OR et.estado = 'Atrasada' THEN 1 ELSE 0 END) AS tareas_pendientes,
                -- Definimos una nota final simulada para entrenar el modelo (o basada en un cálculo ponderado)
                COALESCE(AVG(et.calificacion), 10.0) * 0.7 + (SUM(CASE WHEN et.estado = 'Entregada' THEN 1 ELSE 0 END) * 0.5) as nota_final
            FROM estudiantes e
            LEFT JOIN estado_tareas et ON e.id_estudiante = et.id_estudiante
            GROUP BY e.id_estudiante
        """        

        
        # [MODIFICADO] Consultamos la vista que ya incluye la nota_final calculada en SQL
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
        
        # Entrenamos el modelo de Regresión Lineal de Scikit-learn
        print("⚙️ Entrenando el algoritmo predictivo...")
        modelo = LinearRegression()
        modelo.fit(X, y)
        
        # 1.Definir la carpeta y crearla si no existe
        carpeta_modelos = "modelos"
        if not os.path.exists(carpeta_modelos):
            os.makedirs(carpeta_modelos)
            
          # 2.  Definir la ruta completa y guardar el archivo binario
        ruta_modelo = os.path.join(carpeta_modelos, 'modelo_notas.pkl')
        # Guardamos el modelo entrenado
        joblib.dump(modelo, ruta_modelo)
        
        print("✅ ¡Modelo predictivo entrenado y guardado exitosamente como 'modelo_notas.pkl'!")
        return modelo

    except Exception as e:
        print(f"❌ Error durante el entrenamiento del modelo de notas: {e}")
        return None

if __name__ == "__main__":
    entrenar_modelo()