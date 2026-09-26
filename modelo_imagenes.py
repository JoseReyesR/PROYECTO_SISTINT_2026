import os
import cv2 
import numpy as np 
import pytesseract
from PIL import Image
from dotenv import load_dotenv

# 1. Cargar las variables de entorno locales (el archivo .env)
load_dotenv()

# 2. Configurar Tesseract de forma dinámica
tesseract_path = os.getenv("TESSERACT_PATH")
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

# [NUEVO] Función de Machine Learning (Feature Matching) con ORB
def comparar_con_referencia(img_cv, ruta_plantilla="plantilla_referencia.jpg"):
    """
    Compara la imagen subida contra una plantilla oficial usando OpenCV ORB.
    Devuelve True si encuentra suficientes puntos en común.
    """
    # Intentamos cargar la plantilla maestra del servidor
    plantilla = cv2.imread(ruta_plantilla)
    if plantilla is None:
        return False, 0 # Si no existe el archivo de plantilla, omitimos este paso

    # Convertimos ambas imágenes a escala de grises para el análisis matemático
    img1 = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(plantilla, cv2.COLOR_BGR2GRAY)

    # Inicializamos el algoritmo ORB (buscaremos hasta 500 puntos clave)
    orb = cv2.ORB_create(nfeatures=500)

    # Extraemos los puntos clave (keypoints) y descriptores de ambas imágenes
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    # Si alguna imagen es completamente plana y no tiene descriptores, fallamos
    if des1 is None or des2 is None:
        return False, 0

    # Inicializamos el comparador de Fuerza Bruta (Brute Force Matcher)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    
    # Cruzamos los descriptores para encontrar coincidencias exactas
    coincidencias = bf.match(des1, des2)

    # Si la IA encuentra más de 30 puntos estructurales idénticos, confirmamos que es el mismo tipo de documento
    puntos_encontrados = len(coincidencias)
    if puntos_encontrados > 30:
        return True, puntos_encontrados
        
    return False, puntos_encontrados

def analizar_documento(ruta_imagen):
    """
    Analiza las dimensiones, compara con plantillas ORB y extrae texto con OCR.
    """
    try:
        # 1. Carga de imagen con OpenCV
        img_cv = cv2.imread(ruta_imagen)
        if img_cv is None:
            return {"valido": False, "tipo": "Error", "mensaje": "No se pudo leer la imagen."}

        alto, ancho = img_cv.shape[:2]
        
        # 2. Validación estructural geométrica
        proporcion = max(alto, ancho) / min(alto, ancho)
        if proporcion < 1.15:
            return {
                "valido": False, 
                "tipo": "Rechazado", 
                "mensaje": "⚠️ La estructura de la imagen no coincide con un documento válido (DNI o Voucher)."
            }

        # 3. [NUEVO] Comparación estricta contra la plantilla maestra usando ORB
        es_identico, nivel_similitud = comparar_con_referencia(img_cv, "plantilla_referencia.jpg")

        # 4. Preprocesamiento para OCR
        gris = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        _, imagen_procesada = cv2.threshold(gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        img_pil = Image.fromarray(imagen_procesada)
        texto_extraido = pytesseract.image_to_string(img_pil).lower()
        
        # 5. [MODIFICADO] Lógica de validación híbrida (Visual + Texto)
        if any(palabra in texto_extraido for palabra in ["banco", "voucher", "pago", "operacion", "s/", "transferencia", "referencia"]):
            return {"valido": True, "tipo": "Voucher", "mensaje": "✅ Comprobante de pago validado por estructura y texto."}
        elif es_identico:
            return {"valido": True, "tipo": "Documento Oficial", "mensaje": f"✅ Documento validado por reconocimiento visual ORB ({nivel_similitud} puntos de coincidencia)."}           
                    
        elif any(palabra in texto_extraido for palabra in ["dni", "identidad", "reniec", "registro nacional", "apellido", "nombres", "nacimiento", "civil", "sexo", "per"]):
            return {"valido": True, "tipo": "DNI", "mensaje": "✅ Documento de identidad validado por estructura y texto."}
            
        else:
            return {"valido": False, "tipo": "Desconocido", "mensaje": "⚠️ Estructura válida, pero no detectamos coincidencias visuales ni palabras clave."}
            
    except Exception as e:
        return {"valido": False, "tipo": "Error", "mensaje": f"❌ Error en la IA Visual: {str(e)}"}

if __name__ == "__main__":
    print("Iniciando prueba local de IA Visual con Feature Matching y OCR...")