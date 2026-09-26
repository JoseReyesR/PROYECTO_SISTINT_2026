import warnings
# Silenciamos la advertencia de Pandas sobre SQLAlchemy
warnings.filterwarnings('ignore', category=UserWarning)

import mysql.connector
import pandas as pd
from sklearn.cluster import KMeans
import joblib
import os

def entrenar_modelo_perfil():
    print("🔄 Iniciando entrenamiento de Clustering (K-Means)...")
    
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            database='chatbot_siagie_db',
            user='root',
            password='1234'
        )
        
        # Extraemos las tres variables de tu dataset original
        query = "SELECT cursos_matriculados, pagos_realizados, tareas_entregadas_total FROM dataset_perfil_usuario"
        df = pd.read_sql(query, conexion)
        conexion.close()
        
        print(f"📊 Registros extraídos para perfilamiento: {len(df)}")
        
        if len(df) == 0:
            print("⚠️ No hay suficientes datos en la BD para agrupar perfiles.")
            return None

        # Definimos las variables independientes (X) usando tus columnas exactas. 
        # Al ser Aprendizaje No Supervisado, no usamos etiquetas 'y'.
        X = df[['cursos_matriculados', 'pagos_realizados', 'tareas_entregadas_total']]
        
        # Configuramos K-Means para descubrir 3 grupos naturales (Ej: Inactivo, Regular, Sobresaliente)
        print("⚙️ Agrupando estudiantes mediante aprendizaje no supervisado...")
        modelo_kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        modelo_kmeans.fit(X)
        
        carpeta_modelos = "modelos"
        if not os.path.exists(carpeta_modelos):
            os.makedirs(carpeta_modelos)
            
        # Exportamos el modelo entrenado
        ruta_modelo = os.path.join(carpeta_modelos, 'modelo_perfil_usuario.pkl')
        joblib.dump(modelo_kmeans, ruta_modelo)
        
        print("✅ ¡Clustering finalizado! Guardado como 'modelo_perfil_usuario.pkl'")
        return modelo_kmeans

    except Exception as e:
        print(f"❌ Error durante el entrenamiento del perfilamiento: {e}")
        return None

if __name__ == "__main__":
    entrenar_modelo_perfil()