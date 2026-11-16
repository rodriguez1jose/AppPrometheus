import cv2
import matplotlib.pyplot as plt


# ============================================================
# FUNCIÓN PRINCIPAL DE PROCESAMIENTO CLAHE
# ============================================================

def procesar_clahe(ruta_imagen):


    # ========================================================
    # 1. Cargar imagen en escala de grises
    # ========================================================

    imagen = cv2.imread(
        ruta_imagen,
        cv2.IMREAD_GRAYSCALE
    )


    if imagen is None:
        raise FileNotFoundError(
            f"No se pudo cargar: {ruta_imagen}"
        )


    # ========================================================
    # 2. Ecualización global
    # ========================================================

    imagen_equalizada = cv2.equalizeHist(
        imagen
    )


    # ========================================================
    # 3. Crear CLAHE
    # ========================================================

    clip_limit = 2.0
    tile_grid = (8, 8)


    clahe = cv2.createCLAHE(
        clipLimit=clip_limit,
        tileGridSize=tile_grid
    )


    # ========================================================
    # 4. Aplicar CLAHE
    # ========================================================

    imagen_clahe = clahe.apply(
        imagen
    )


    # ========================================================
    # 5. Mostrar comparación
    # ========================================================

    fig, axes = plt.subplots(
        2,
        3,
        figsize=(16, 9)
    )


    # -------------------------------
    # Imagen original
    # -------------------------------

    axes[0,0].imshow(
        imagen,
        cmap="gray"
    )

    axes[0,0].set_title(
        "TC original"
    )

    axes[0,0].axis("off")


    # -------------------------------
    # Ecualización global
    # -------------------------------

    axes[0,1].imshow(
        imagen_equalizada,
        cmap="gray"
    )

    axes[0,1].set_title(
        "Ecualización global"
    )

    axes[0,1].axis("off")


    # -------------------------------
    # CLAHE
    # -------------------------------

    axes[0,2].imshow(
        imagen_clahe,
        cmap="gray"
    )

    axes[0,2].set_title(
        "CLAHE"
    )

    axes[0,2].axis("off")



    # -------------------------------
    # Histograma original
    # -------------------------------

    axes[1,0].hist(
        imagen.ravel(),
        bins=256,
        range=(0,256)
    )

    axes[1,0].set_title(
        "Histograma original"
    )


    axes[1,0].set_xlabel(
        "Nivel de gris"
    )

    axes[1,0].set_ylabel(
        "Número de píxeles"
    )



    # -------------------------------
    # Histograma ecualización
    # -------------------------------

    axes[1,1].hist(
        imagen_equalizada.ravel(),
        bins=256,
        range=(0,256)
    )

    axes[1,1].set_title(
        "Histograma - Ecualización global"
    )

    axes[1,1].set_xlabel(
        "Nivel de gris"
    )

    axes[1,1].set_ylabel(
        "Número de píxeles"
    )



    # -------------------------------
    # Histograma CLAHE
    # -------------------------------

    axes[1,2].hist(
        imagen_clahe.ravel(),
        bins=256,
        range=(0,256)
    )

    axes[1,2].set_title(
        "Histograma - CLAHE"
    )

    axes[1,2].set_xlabel(
        "Nivel de gris"
    )

    axes[1,2].set_ylabel(
        "Número de píxeles"
    )


    plt.tight_layout()



    # ========================================================
    # 6. Crear contexto para Gemini
    # ========================================================


    contexto = f"""

=========================================
ANÁLISIS DE IMAGEN DE TOMOGRAFÍA COMPUTARIZADA
=========================================


Archivo:
{ruta_imagen}


Tamaño de imagen:
{imagen.shape[1]} x {imagen.shape[0]} píxeles



=========================================
MÉTODOS APLICADOS
=========================================


1. Ecualización global de histograma

2. CLAHE
   (Contrast Limited Adaptive Histogram Equalization)



=========================================
IMAGEN ORIGINAL
=========================================


Media:
{imagen.mean():.2f}


Desviación estándar:
{imagen.std():.2f}



=========================================
ECUALIZACIÓN GLOBAL
=========================================


Media:
{imagen_equalizada.mean():.2f}


Desviación estándar:
{imagen_equalizada.std():.2f}



=========================================
CLAHE
=========================================


Media:
{imagen_clahe.mean():.2f}


Desviación estándar:
{imagen_clahe.std():.2f}



=========================================
PARÁMETROS CLAHE
=========================================


clipLimit:
{clip_limit}


tileGridSize:
{tile_grid[0]} x {tile_grid[1]}


"""


    return contexto, imagen_clahe



# ============================================================
# EJECUCIÓN DIRECTA DEL ARCHIVO
# ============================================================


if __name__ == "__main__":


    ruta = "imagenes/tc/tc1.jpeg"


    contexto, imagen = procesar_clahe(
        ruta
    )


    print(contexto)


    plt.show()
    