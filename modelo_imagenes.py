from PIL import Image
import pytesseract
import os
# Este archivo actuará como una dependencia para tu servidor web. De acuerdo con tu diseño, 
# cuando el estudiante suba una imagen desde la interfaz, tu archivo app.py la guardará mediante secure_filename
# Descomenta y ajusta esta línea si instalaste Tesseract en la ruta por defecto de Windows
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def analizar_pagina_web(ruta_imagen):
    """
    Realiza la extracción de características visuales y validación de formatos (DNI o vouchers).
    """
    # Verificamos que el archivo realmente exista antes de procesarlo
    if not os.path.exists(ruta_imagen):
        return "Error: No se encontró la imagen en la ruta especificada."
        
    try:
        # 1. Preparación de datos visuales
        imagen = Image.open(ruta_imagen)
        
        # 2. Extracción de características mediante OCR
        texto_extraido = pytesseract.image_to_string(imagen).lower()
        
        # 3. Clasificación básica para validación de formatos
        if "dni" in texto_extraido or "reniec" in texto_extraido:
            return "Validación exitosa: Documento de Identidad (DNI) detectado."
        elif "voucher" in texto_extraido or "bcp" in texto_extraido or "pago" in texto_extraido or "transferencia" in texto_extraido:
            return "Validación exitosa: Comprobante de pago (Voucher) detectado."
        else:
            return "Alerta: La imagen cargada no cumple con la estructura de un DNI o Voucher académico."
            
    except Exception as e:
        return f"Error en el procesamiento de la imagen: {str(e)}"

# Prueba local rápida (Solo se ejecuta si corres este archivo directamente)
if __name__ == "__main__":
    print("--- Módulo de IA Visual Listo ---")
    print("Esperando la conexión desde app.py para procesar rutas de imágenes...")