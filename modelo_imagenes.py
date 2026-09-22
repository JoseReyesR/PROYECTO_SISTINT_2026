import os
import pytesseract
from PIL import Image
from dotenv import load_dotenv

# 1. Cargar las variables de entorno locales (el archivo .env)
load_dotenv()

# 2. Configurar Tesseract de forma dinámica
# Si un compañero usa Windows y puso la ruta en su .env, la tomará.
# Si usa Mac/Linux, la variable estará vacía y usará la ruta del sistema por defecto.
tesseract_path = os.getenv("TESSERACT_PATH")
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

def analizar_documento(ruta_imagen):
    """
    Extrae texto de una imagen y realiza validación básica de formatos (DNI/Voucher).
    """
    try:
        # Abrir la imagen subida
        img = Image.open(ruta_imagen)
        
        # Extraer texto usando Tesseract en español
       # texto_extraido = pytesseract.image_to_string(img, lang="spa").lower()
        texto_extraido = pytesseract.image_to_string(img).lower()
        # Validación
        if "dni" in texto_extraido or "documento" in texto_extraido:
            return {"valido": True, "tipo": "DNI", "mensaje": "✅ Documento de identidad validado correctamente."}
        elif "banco" in texto_extraido or "voucher" in texto_extraido or "pago" in texto_extraido:
            return {"valido": True, "tipo": "Voucher", "mensaje": "✅ Comprobante de pago validado correctamente."}
        else:
            return {"valido": False, "tipo": "Desconocido", "mensaje": "⚠️ No detectamos palabras clave. Asegúrate de que la imagen sea nítida."}
            
    except Exception as e:
        return {"valido": False, "tipo": "Error", "mensaje": f"❌ Error en el OCR: {str(e)}"}

# 3. Función de prueba rápida para tus compañeros
if __name__ == "__main__":
    print("Iniciando prueba local de Tesseract OCR...")
    print(f"Ruta configurada: {tesseract_path if tesseract_path else 'Por defecto del sistema'}")
    # Puedes colocar una imagen de prueba llamada 'prueba.jpg' en tu raíz para probar este script directamente
    # print(analizar_documento("prueba.jpg"))