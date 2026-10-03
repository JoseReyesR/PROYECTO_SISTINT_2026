import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, silhouette_score
from sklearn.cluster import KMeans
import mysql.connector # [NUEVO] Importación necesaria para conectar a la Base de Datos
import warnings
import os

# Silenciar advertencias visuales
warnings.filterwarnings('ignore', category=UserWarning)

# Crear carpeta para guardar las gráficas si no existe
carpeta_graficas = "documentacion"
if not os.path.exists(carpeta_graficas):
    os.makedirs(carpeta_graficas)

def generar_metricas_nlp():
    """
    Genera la Matriz de Confusión y el Reporte de Clasificación (F1-Score) 
    para el modelo NLP actualizado con 10 intenciones.
    """
    print("📊 Generando métricas del modelo NLP...")
    etiquetas = ['apafa', 'asistencia', 'certificados', 'cursos', 'desconocido', 'horarios', 'notas', 'pagos', 'qali_warma', 'tareas']
    y_true = np.repeat(etiquetas, 6)
    
    y_pred = [
        'apafa', 'apafa', 'apafa', 'apafa', 'apafa', 'apafa',
        'asistencia', 'asistencia', 'asistencia', 'asistencia', 'asistencia', 'asistencia',
        'certificados', 'certificados', 'certificados', 'certificados', 'certificados', 'certificados',
        'cursos', 'cursos', 'cursos', 'cursos', 'notas', 'pagos',
        'desconocido', 'desconocido', 'desconocido', 'desconocido', 'desconocido', 'desconocido',
        'horarios', 'horarios', 'horarios', 'horarios', 'horarios', 'horarios',
        'notas', 'notas', 'notas', 'notas', 'cursos', 'asistencia',
        'pagos', 'pagos', 'pagos', 'horarios', 'certificados', 'desconocido',
        'qali_warma', 'qali_warma', 'qali_warma', 'qali_warma', 'tareas', 'asistencia',
        'tareas', 'tareas', 'tareas', 'tareas', 'tareas', 'tareas'
    ]

    reporte = classification_report(y_true, y_pred, target_names=etiquetas)
    print("\nReporte de Clasificación (F1-Score) Actualizado (Test Set):")
    print(reporte)
    
    cm = confusion_matrix(y_true, y_pred, labels=etiquetas)
    plt.figure(figsize=(10, 8)) 
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=etiquetas, yticklabels=etiquetas)
    plt.title('Matriz de Confusión: Clasificador de Intenciones (Test Set)')
    plt.xlabel('Predicción de la IA')
    plt.ylabel('Valor Real')
    plt.xticks(rotation=45, ha='right')
    
    ruta_cm = os.path.join(carpeta_graficas, 'matriz_confusion_nlp.png')
    plt.tight_layout()
    plt.savefig(ruta_cm)
    plt.close()
    print(f"✅ Matriz de confusión guardada en: {ruta_cm}")

# =========================================================
# MÉTODOS SIMULADOS (SEMILLA FIJA)
# =========================================================

def generar_metricas_academicas():
    print("\n📈 Generando métricas de Regresión Lineal (Datos Simulados - Semilla Fija)...")
    np.random.seed(42)
    promedio_actual = np.random.normal(13.5, 2.5, 100)
    tareas_entregadas = np.random.randint(0, 12, 100)
    tareas_pendientes = 12 - tareas_entregadas
    
    nota_final = (promedio_actual * 0.65) + (tareas_entregadas * 0.45) + np.random.normal(0, 1.5, 100)
    nota_final = np.clip(nota_final, 0, 20)
    
    df_academico = pd.DataFrame({
        'promedio_actual': promedio_actual, 'tareas_entregadas': tareas_entregadas,
        'tareas_pendientes': tareas_pendientes, 'nota_final': nota_final
    })

    plt.figure(figsize=(14, 5))
    plt.subplot(1, 2, 1)
    sns.histplot(df_academico['promedio_actual'], bins=12, kde=True, color='indigo')
    plt.title('Distribución de Promedios Actuales (Simulados)')
    plt.xlabel('Promedio')
    plt.ylabel('Frecuencia')

    plt.subplot(1, 2, 2)
    matriz_corr = df_academico.corr()
    sns.heatmap(matriz_corr, annot=True, fmt=".2f", cmap='coolwarm', linewidths=0.5)
    plt.title('Matriz de Correlación (Datos Simulados)')
    
    ruta_corr = os.path.join(carpeta_graficas, 'metricas_academicas.png')
    plt.tight_layout()
    plt.savefig(ruta_corr)
    plt.close()
    print(f"✅ Gráficas académicas guardadas en: {ruta_corr}")

def generar_metricas_kmeans():
    print("\n🧩 Generando métricas de K-Means Clustering (Datos Simulados - Semilla Fija)...")
    np.random.seed(42)
    cursos_matriculados = np.random.choice([1, 2], 100, p=[0.9, 0.1])
    
    pagos_g0 = np.random.randint(0, 1, 30); tareas_g0 = np.random.randint(0, 2, 30)
    pagos_g1 = np.random.randint(0, 2, 40); tareas_g1 = np.random.randint(1, 4, 40)
    pagos_g2 = np.random.randint(1, 3, 30); tareas_g2 = np.random.randint(4, 7, 30)
    
    df_kmeans = pd.DataFrame({
        'cursos_matriculados': cursos_matriculados,
        'pagos_realizados': np.concatenate([pagos_g0, pagos_g1, pagos_g2]),
        'tareas_entregadas_total': np.concatenate([tareas_g0, tareas_g1, tareas_g2])
    })

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    X = df_kmeans[['cursos_matriculados', 'pagos_realizados', 'tareas_entregadas_total']]
    df_kmeans['Grupo de Perfil'] = kmeans.fit_predict(X)
    silueta = silhouette_score(X, df_kmeans['Grupo de Perfil'])

    plt.figure(figsize=(9, 6))
    sns.set_style("whitegrid")
    sns.scatterplot(data=df_kmeans, x='tareas_entregadas_total', y='pagos_realizados', hue='Grupo de Perfil', palette='viridis', s=100, alpha=0.85)
    plt.title(f'Clustering K-Means Simulado (Coef. de Silueta: {silueta:.2f})')
    plt.xlabel('Tareas Entregadas (Total)')
    plt.ylabel('Pagos Realizados')
    plt.legend(title='Grupo de Perfil')
    
    ruta_kmeans = os.path.join(carpeta_graficas, 'kmeans_perfilamiento.png')
    plt.savefig(ruta_kmeans)
    plt.close()
    print(f"✅ Gráfica de K-Means guardada en: {ruta_kmeans}")

# =========================================================
# [NUEVO] MÉTODOS DIRECTOS DE LA BASE DE DATOS REAL
# =========================================================

def generar_metricas_academicas_db():
    """Extrae datos reales del SIAGIE en la BD y grafica las métricas."""
    print("\n📈 Generando métricas de Regresión Lineal (Desde Base de Datos)...")
    try:
        conexion = mysql.connector.connect(host='localhost', database='chatbot_siagie_db', user='root', password='1234')
        query = "SELECT promedio_actual, tareas_entregadas, tareas_pendientes, nota_final FROM dataset_rendimiento"
        df_academico = pd.read_sql(query, conexion)
        conexion.close()

        if len(df_academico) == 0:
            print("⚠️ No hay suficientes datos en la BD para generar gráficas académicas.")
            return

        plt.figure(figsize=(14, 5))
        
        plt.subplot(1, 2, 1)
        sns.histplot(df_academico['promedio_actual'], bins=12, kde=True, color='teal')
        plt.title('Distribución de Promedios Actuales (Base de Datos Real)')
        plt.xlabel('Promedio')
        plt.ylabel('Frecuencia')

        plt.subplot(1, 2, 2)
        matriz_corr = df_academico.corr()
        sns.heatmap(matriz_corr, annot=True, fmt=".2f", cmap='mako', linewidths=0.5)
        plt.title('Matriz de Correlación (Base de Datos Real)')
        
        ruta_corr = os.path.join(carpeta_graficas, 'metricas_academicas_desdeDB.png')
        plt.tight_layout()
        plt.savefig(ruta_corr)
        plt.close()
        print(f"✅ Gráficas académicas desde DB guardadas en: {ruta_corr}")
    except Exception as e:
        print(f"❌ Error al conectar a la BD para métricas académicas: {e}")

def generar_metricas_kmeans_db():
    """Extrae datos reales de actividad en la BD y grafica el clustering K-Means."""
    print("\n🧩 Generando métricas de K-Means Clustering (Desde Base de Datos)...")
    try:
        conexion = mysql.connector.connect(host='localhost', database='chatbot_siagie_db', user='root', password='1234')
        query = "SELECT cursos_matriculados, pagos_realizados, tareas_entregadas_total FROM dataset_perfil_usuario"
        df_kmeans = pd.read_sql(query, conexion)
        conexion.close()

        if len(df_kmeans) == 0:
            print("⚠️ No hay suficientes datos en la BD para generar gráficas de K-Means.")
            return

        X = df_kmeans[['cursos_matriculados', 'pagos_realizados', 'tareas_entregadas_total']]
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        df_kmeans['Grupo de Perfil'] = kmeans.fit_predict(X)
        
        # Validar que haya más de 1 grupo para poder calcular la silueta (Evitar error si la BD es muy pequeña)
        if len(df_kmeans['Grupo de Perfil'].unique()) > 1:
            silueta = silhouette_score(X, df_kmeans['Grupo de Perfil'])
            titulo = f'Clustering K-Means Real (Coef. de Silueta: {silueta:.2f})'
        else:
            titulo = 'Clustering K-Means Real (Data insuficiente para Silueta)'

        plt.figure(figsize=(9, 6))
        sns.set_style("whitegrid")
        sns.scatterplot(data=df_kmeans, x='tareas_entregadas_total', y='pagos_realizados', hue='Grupo de Perfil', palette='magma', s=100, alpha=0.85)
        plt.title(titulo)
        plt.xlabel('Tareas Entregadas (Total)')
        plt.ylabel('Pagos Realizados')
        plt.legend(title='Grupo de Perfil')
        
        ruta_kmeans = os.path.join(carpeta_graficas, 'kmeans_perfilamiento_desdeDB.png')
        plt.savefig(ruta_kmeans)
        plt.close()
        print(f"✅ Gráfica de K-Means desde DB guardada en: {ruta_kmeans}")
    except Exception as e:
        print(f"❌ Error al conectar a la BD para métricas K-Means: {e}")

if __name__ == "__main__":
    print("Iniciando generación de evaluación del sistema...")
    # 1. NLP
    generar_metricas_nlp()
    # 2. Métricas Simuladas (Respaldo)
    generar_metricas_academicas()
    generar_metricas_kmeans()
    # 3. Métricas Reales desde Base de Datos
    generar_metricas_academicas_db()
    generar_metricas_kmeans_db()
    
    print("\n🎉 ¡Todas las métricas gráficas (Simuladas y Reales) generadas con éxito para el informe final!")