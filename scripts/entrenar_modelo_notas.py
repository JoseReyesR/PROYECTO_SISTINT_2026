import mysql.connector
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

def entrenar_modelo():
    print("🔄 Conectando a MySQL para extraer datos de rendimiento...")
    try:
        # Establecemos la conexión usando tus credenciales
        conexion = mysql.connector.connect(
            host='localhost',
            database='chatbot_siagie_db',
            user='root',
            password='1234'
        )
        
        # Consultamos la vista o datos directos para la Regresión Lineal
        # Tomamos como base las calificaciones y el estado de las tareas de los estudiantes
        query = """
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
        
        df = pd.read_sql(query, conexion)
        conexion.close()
        
        print(f"📊 Registros cargados para entrenamiento: {len(df)}")
        
        if len(df) == 0:
            print("⚠️ No hay suficientes datos en la BD para entrenar. Asegúrate de insertar registros en 'estudiantes' y 'estado_tareas'.")
            return None

        # Definimos las variables independientes (X) y la variable objetivo (y)
        X = df[['promedio_actual', 'tareas_entregadas', 'tareas_pendientes']]
        y = df['nota_final']
        
        # Entrenamos el modelo de Regresión Lineal
        modelo = LinearRegression()
        modelo.fit(X, y)
        
        # Guardamos el modelo entrenado
        joblib.dump(modelo, 'modelo_notas.pkl')
        print("✅ ¡Modelo de notas entrenado y guardado exitosamente como 'modelo_notas.pkl'!")
        return modelo

    except Exception as e:
        print(f"❌ Error durante el entrenamiento del modelo de notas: {e}")
        return None

if __name__ == "__main__":
    entrenar_modelo()