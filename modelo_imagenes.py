import os
import cv2 # [NUEVO] Librería de Visión por Computadora para análisis estructural
import numpy as np # [NUEVO] Para manejo de matrices de imágenes
import pytesseract
from PIL import Image
from dotenv import load_dotenv

# 1. Cargar las variables de entorno locales (el archivo .env)
load_dotenv()

# 2. Configurar Tesseract de forma dinámica
tesseract_path = os.getenv("TESSERACT_PATH")
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

# [MODIFICADO] Función de análisis ahora incluye validación estructural con OpenCV
def analizar_documento(ruta_imagen):
    """
    Analiza las dimensiones de la imagen, aplica filtros de visión por computadora
    y extrae texto para validación preliminar (DNI/Voucher).
    """
    try:
        # 1. [NUEVO] Carga de imagen con OpenCV para análisis estructural
        img_cv = cv2.imread(ruta_imagen)
        if img_cv is None:
            return {"valido": False, "tipo": "Error", "mensaje": "No se pudo leer la imagen."}

        alto, ancho = img_cv.shape[:2]
        
        # 2. [NUEVO] Validación estructural geométrica
        # Calculamos la proporción. Los DNI y Vouchers son rectangulares. 
        # Si la imagen es un cuadrado casi perfecto (proporción cercana a 1.0), se rechaza.
        proporcion = max(alto, ancho) / min(alto, ancho)
        if proporcion < 1.15:
            return {
                "valido": False, 
                "tipo": "Rechazado", 
                "mensaje": "⚠️ La estructura de la imagen no coincide con un documento válido (DNI o Voucher)."
            }

        # 3. [NUEVO] Preprocesamiento de la imagen para mejorar la precisión del OCR
        # Convertimos a escala de grises
        gris = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        # Aplicamos umbralización adaptativa (Otsu) para resaltar el texto del fondo
        _, imagen_procesada = cv2.threshold(gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Convertimos la matriz de OpenCV de vuelta a formato PIL para Tesseract
        img_pil = Image.fromarray(imagen_procesada)
        
        # 4. [MODIFICADO] Extracción de texto usando Tesseract en la imagen mejorada
        # Agregamos lang="spa" para que reconozca tildes y caracteres en español
       # texto_extraido = pytesseract.image_to_string(img_pil, lang="spa").lower()
        texto_extraido = pytesseract.image_to_string(img_pil).lower()
        
        # 5. [MODIFICADO] Validación invertida (Prioridad al Voucher)
        # Agregamos "referencia" a la lista, ya que aparece en tu imagen
        if any(palabra in texto_extraido for palabra in ["banco", "voucher", "pago", "operacion", "s/", "transferencia", "referencia"]):
            return {"valido": True, "tipo": "Voucher", "mensaje": "✅ Comprobante de pago validado por estructura y texto."}
            
        elif any(palabra in texto_extraido for palabra in ["dni", "identidad", "reniec", "registro nacional", "apellido", "nombres", "nacimiento", "civil", "sexo", "per"]):
            return {"valido": True, "tipo": "DNI", "mensaje": "✅ Documento de identidad validado por estructura y texto."}
            
        else:
            return {"valido": False, "tipo": "Desconocido", "mensaje": "⚠️ Estructura válida, pero no se detectaron palabras clave. Asegúrate de que la imagen sea nítida."}
            
    except Exception as e:
        return {"valido": False, "tipo": "Error", "mensaje": f"❌ Error en la IA Visual: {str(e)}"}

# 3. Función de prueba rápida
if __name__ == "__main__":
    print("Iniciando prueba local de IA Visual con OpenCV y Tesseract OCR...")
    print(f"Ruta configurada: {tesseract_path if tesseract_path else 'Por defecto del sistema'}")
    # print(analizar_documento("prueba.jpg"))