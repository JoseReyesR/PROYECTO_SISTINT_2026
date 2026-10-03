from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import warnings
# Silenciamos la advertencia de Pandas sobre SQLAlchemy
warnings.filterwarnings('ignore', category=UserWarning)

import mysql.connector
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score # [NUEVO] Importado para evaluar calidad del clúster no supervisado
import joblib

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
        
        # [MODIFICADO] Usamos fit_predict para entrenar y obtener de inmediato las etiquetas generadas
        etiquetas_predichas = modelo_kmeans.fit_predict(X)
        
        # [NUEVO] VALIDACIÓN DE SILUETA (Métrica para Aprendizaje No Supervisado)
        score_silueta = silhouette_score(X, etiquetas_predichas)
        
        print("\n📊 MÉTRICA DE APRENDIZAJE NO SUPERVISADO:")
        print(f"Coeficiente de Silueta: {score_silueta:.4f}")
        print("*(Valores más cercanos a 1.0 indican clústeres densos y bien separados)*")
        
        carpeta_modelos = "modelos"
        if not os.path.exists(carpeta_modelos):
            os.makedirs(carpeta_modelos)
            
        # Exportamos el modelo entrenado
        ruta_modelo = os.path.join(carpeta_modelos, 'modelo_perfil_usuario.pkl')
        joblib.dump(modelo_kmeans, ruta_modelo)
        
        print(f"\n✅ ¡Clustering finalizado! Guardado como 'modelo_perfil_usuario.pkl'")

        # =========================================================================
        # [NUEVO] IMPRESIÓN DE LA COMPOSICIÓN DE LOS GRUPOS
        # =========================================================================
        print("\n# Composición de los grupos (verificación con joblib.load):")
        
        # 1. Cargamos el modelo guardado para la verificación
        modelo_cargado = joblib.load(ruta_modelo)
        
        # 2. Agregamos las etiquetas predichas al dataframe original
        df['cluster'] = modelo_cargado.labels_
        
        # 3. Calculamos la cantidad de alumnos y el promedio de pagos y tareas por cluster
        resumen = df.groupby('cluster').agg(
            cantidad=('cursos_matriculados', 'count'),
            promedio_pagos=('pagos_realizados', 'mean'),
            promedio_tareas=('tareas_entregadas_total', 'mean')
        ).reset_index()

        # 4. Ordenamos de menor a mayor cantidad de tareas para deducir qué grupo es cuál
        resumen_ordenado = resumen.sort_values(by='promedio_tareas')
        etiquetas_logicas = ["de actividad baja", "de actividad intermedia", "destacados"]
        resumen_ordenado['etiqueta_texto'] = etiquetas_logicas
        
        # Función auxiliar para formatear los números y quitar decimales innecesarios (.0)
        def formatear_numero(val):
            val_redondeado = round(val, 2)
            return int(val_redondeado) if val_redondeado == int(val_redondeado) else val_redondeado

        # 5. Imprimimos el resultado final cruzando los datos
        for _, fila in resumen.iterrows():
            cluster_id = int(fila['cluster'])
            cantidad = int(fila['cantidad'])
            pagos_fmt = formatear_numero(fila['promedio_pagos'])
            tareas_fmt = formatear_numero(fila['promedio_tareas'])
            
            # Obtenemos el texto semántico dinámico para este cluster
            etiqueta = resumen_ordenado[resumen_ordenado['cluster'] == cluster_id]['etiqueta_texto'].values[0]
            
            print(f"#   cluster {cluster_id}: {cantidad} estudiantes {etiqueta} ({pagos_fmt} pagos, {tareas_fmt} tareas)")

        return modelo_kmeans

    except Exception as e:
        print(f"❌ Error durante el entrenamiento del perfilamiento: {e}")
        return None

if __name__ == "__main__":
    entrenar_modelo_perfil()