import mysql.connector
from mysql.connector import Error

def obtener_conexion():
    """
    Establece la conexión con la base de datos MySQL del proyecto[cite: 1].
    Ajusta el 'user' y 'password' según la configuración de tu servidor local (ej. XAMPP o Workbench).
    """
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            database='chatbot_siagie_db',
            user='root', 
            password='1234'  # MODIFICADO: Se agregó la contraseña de tu Workbench
        )
        return conexion
    except Error as e:
        print(f"❌ Error al conectar a MySQL: {e}")
        return None

def obtener_estudiante(codigo_anonimizado):
    """
    Realiza la consulta SQL para validar si el estudiante existe en el sistema.
    """
    try:
        conexion = obtener_conexion()
        if conexion and conexion.is_connected():
            # dictionary=True nos permite acceder a los datos por nombre de columna
            cursor = conexion.cursor(dictionary=True) 
            
            # Buscamos al estudiante en la tabla anonimizada[cite: 1]
            query = """
                SELECT id_estudiante, codigo_anonimizado, nivel_educativo, grado, seccion, estado_riesgo 
                FROM estudiantes 
                WHERE codigo_anonimizado = %s
            """
            cursor.execute(query, (codigo_anonimizado,))
            estudiante = cursor.fetchone()
            
            return estudiante
            
    except Error as e:
        print(f"❌ Error en la consulta a la base de datos: {e}")
        return None
    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()

# Prueba de conexión rápida (Solo se ejecuta si corres este archivo directamente)
if __name__ == "__main__":
    print("Probando conexión a la base de datos...")
    con = obtener_conexion()
    if con and con.is_connected():
        print("✅ ¡Conexión exitosa a chatbot_siagie_db en MySQL!")
        con.close()