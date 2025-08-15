import os
import numpy as np
import rasterio
from PIL import Image
from matplotlib import cm


carpeta_entrada = r".\ejercicio_raster-main\insumos"
carpeta_salida = os.path.join(r".\ImagenesPng", "procesadas")
os.makedirs(carpeta_salida, exist_ok=True)

#Hago una funcion para poder obtener el mapa de colores con matplotlib
def obtener_colormap(nombre_archivo):
    if "ndwi" in nombre_archivo.lower():
        return cm.get_cmap("Blues")
    else:
        return cm.get_cmap("RdYlGn")

#Funcion para procesar la imagen
def procesar_imagen(ruta_tiff, ruta_salida):
    #Leo el archivo tiff y guardo su array de la banda1
    with rasterio.open(ruta_tiff) as src:
        data = src.read(1)

    #Creo máscaras para los datos -999 y -998 para identificar píxeles sin valor o de nubes y filtrar todos los demás datos
    mascara_transparente = (data == -999)
    mascara_nubes = (data == -998)
    mascara_valores = ~(mascara_transparente | mascara_nubes)

    # Normalizo la imagen, calculo los valores minimos y maximos del filtro pasado
    min_val = np.nanmin(data[mascara_valores])
    max_val = np.nanmax(data[mascara_valores])
    norm = (data - min_val) / (max_val - min_val)

    #Analiza el mapa de colores y aplica el mapa de color a los valorez normalizados pasandolos a RGB
    cmap = obtener_colormap(os.path.basename(ruta_tiff))
    colores = cmap(norm)[:, :, :3]  # RGB

    # Convertir valores 01 a 0-255
    rgb = (colores * 255).astype(np.uint8)

    # Se coloca la máscara en -998 a valores en blanco
    rgb[mascara_nubes] = [255, 255, 255]

    # Inicializar alpha un array con los valores en 255 opacos
    alpha = np.full(data.shape, 255, dtype=np.uint8)

    # Hago los píxeles que tienen valor -999 en transparentes
    alpha[mascara_transparente] = 0
    mascara_negros = np.all(rgb == [0, 0, 0], axis=-1)
    alpha[mascara_negros] = 0

    # Combinar RGBA para guardarlos como una imagen png
    rgba = np.dstack((rgb, alpha))
    imagen = Image.fromarray(rgba, mode="RGBA")
    imagen.save(ruta_salida)

    print(f"Guardado en: {ruta_salida}")

#Creo una funcion para que lea cada imagen de la carpeta en isumos para aplicarles todo el proceso a las imageness
for archivo in os.listdir(carpeta_entrada):
    if archivo.lower().endswith((".tiff", ".tif")):
        ruta_tiff = os.path.join(carpeta_entrada, archivo)
        nombre_salida = os.path.splitext(archivo)[0] + "_procesada.png"
        ruta_salida = os.path.join(carpeta_salida, nombre_salida)
        print(f"Procesando: {ruta_tiff}")
        procesar_imagen(ruta_tiff, ruta_salida)

print("Procesamiento completado.")
