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

def obtener_estudiante_login(codigo_anonimizado, password_ingresada):
    """
    [MODIFICADO] Realiza un JOIN entre estudiantes y usuarios para validar credenciales reales.
    """
    try:
        conexion = obtener_conexion()
        if conexion and conexion.is_connected():
            cursor = conexion.cursor(dictionary=True) 
            
            # Buscamos al estudiante y traemos su contraseña de la tabla usuarios vinculada
            query = """
                SELECT e.id_estudiante, e.codigo_anonimizado, u.password_hash 
                FROM estudiantes e
                JOIN usuarios u ON e.id_usuario = u.id_usuario
                WHERE e.codigo_anonimizado = %s
            """
            cursor.execute(query, (codigo_anonimizado,))
            estudiante = cursor.fetchone()
            
            # Si el estudiante existe y la contraseña coincide
            if estudiante and estudiante['password_hash'] == password_ingresada:
                return estudiante # Login exitoso
            else:
                return None # Contraseña incorrecta o usuario no encontrado
            
    except Error as e:
        print(f"❌ Error en la consulta de login: {e}")
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