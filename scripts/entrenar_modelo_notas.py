import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import joblib # NUEVO: Librería para exportar y guardar el modelo entrenado[cite: 2]

# 1. Dataset Simulado de Historial Académico
# Variables predictoras definidas en la metodología: promedio, tareas entregadas y pendientes[cite: 2]
datos_academicos = {
    'promedio_actual': [14.5, 10.2, 16.0, 08.5, 13.0, 11.5, 17.5, 09.0, 12.5, 15.0, 10.0, 18.0],
    'tareas_entregadas': [8, 3, 10, 2, 7, 5, 11, 4, 6, 9, 3, 12],
    'tareas_pendientes': [2, 7, 0, 8, 3, 5, 0, 6, 4, 1, 7, 0],
    'nota_final': [15.0, 09.5, 17.0, 07.5, 13.5, 11.0, 18.0, 08.5, 12.5, 16.0, 09.0, 19.0]
}
df_notas = pd.DataFrame(datos_academicos)

# 2. Separar características (X) y variable objetivo (y)
X = df_notas[['promedio_actual', 'tareas_entregadas', 'tareas_pendientes']]
y = df_notas['nota_final']

# 3. Partición de datos experimentales (Train/Test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Entrenamiento del Modelo de Regresión Lineal[cite: 1, 2]
modelo_regresion = LinearRegression()
modelo_regresion.fit(X_train, y_train)

# 5. Evaluación de precisión del modelo
precision = modelo_regresion.score(X_test, y_test)
print(f"--- Rendimiento del Algoritmo ---")
print(f"Precisión (R²): {precision * 100:.2f}%\n")

# 6. Guardar el modelo entrenado para la integración con Flask[cite: 1, 2]
# NUEVO: Genera un archivo binario para no tener que reentrenar cada vez que alguien consulta
joblib.dump(modelo_regresion, 'modelo_notas.pkl')
print("✅ Archivo 'modelo_notas.pkl' generado exitosamente.")

# 7. Prueba Predictiva en Tiempo Real
# Simulamos un alumno con promedio de 10.5, 4 tareas entregadas y 6 pendientes
nuevo_estudiante = pd.DataFrame({'promedio_actual': [10.5], 'tareas_entregadas': [4], 'tareas_pendientes': [6]})
nota_estimada = modelo_regresion.predict(nuevo_estudiante)[0]

print("\n--- Predicción de Riesgo Académico ---")
print(f"Nota final estimada por la IA: {nota_estimada:.1f}")

# Sistema de Alertas Tempranas[cite: 1]
if nota_estimada < 11:
    print("⚠️ Nivel de riesgo: Riesgo ALTO (Posible repitencia detectada)")
elif nota_estimada < 14:
    print("⚠️ Nivel de riesgo: Riesgo MEDIO (Requiere apoyo pedagógico)")
else:
    print("✅ Nivel de riesgo: Riesgo BAJO (Rendimiento óptimo)")
    