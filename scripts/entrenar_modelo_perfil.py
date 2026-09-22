import mysql.connector
import pandas as pd
from sklearn.linear_model import LogisticRegression
import joblib
import os

def entrenar_modelo_perfil():
    print("🔄 Conectando a MySQL para entrenar el modelo de Perfilamiento...")
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            database='chatbot_siagie_db',
            user='root',
            password='1234'
        )
        
        # Extraemos los datos de la vista dataset_perfil_usuario
        query = "SELECT cursos_matriculados, pagos_realizados, tareas_entregadas_total FROM dataset_perfil_usuario"
        df = pd.read_sql(query, conexion)
        conexion.close()
        
        if len(df) == 0:
            print("⚠️ No hay datos suficientes para entrenar.")
            return

        # Generamos etiquetas simuladas de perfiles para el prototipo
        # 0 = Desorganizado/Riesgo, 1 = Regular, 2 = Organizado/Responsable
        def definir_perfil(row):
            if row['tareas_entregadas_total'] >= 2 and row['pagos_realizados'] > 0:
                return "tareas" # Perfil enfocado en tareas/organizado
            elif row['pagos_realizados'] == 0:
                return "pagos" # Perfil con problemas de pagos
            else:
                return "horario" # Perfil estándar
                
        df['etiqueta_perfil'] = df.apply(definir_perfil, axis=1)
        
        # Variables independientes (X) y variable objetivo (y)
        X = df[['cursos_matriculados', 'pagos_realizados', 'tareas_entregadas_total']]
        y = df['etiqueta_perfil']
        
        # Entrenamiento con Regresión Logística
        modelo_perfil = LogisticRegression()
        modelo_perfil.fit(X, y)
        
        # Guardado en la carpeta de modelos
        carpeta_modelos = "modelos"
        if not os.path.exists(carpeta_modelos):
            os.makedirs(carpeta_modelos)
            
        ruta_modelo = os.path.join(carpeta_modelos, 'modelo_perfil_usuario.pkl')
        joblib.dump(modelo_perfil, ruta_modelo)
        
        print(f"✅ ¡Modelo de perfilamiento entrenado y guardado en '{ruta_modelo}'!")

    except Exception as e:
        print(f"❌ Error durante el entrenamiento: {e}")

if __name__ == "__main__":
    entrenar_modelo_perfil()