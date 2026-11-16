# apps/ct_modulos/procesamiento.py
# ============================================================
# Módulo de Procesamiento de Imágenes CT (adaptado a Prometeo)
# ============================================================
import base64
import io
import os

import cv2
import numpy as np
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate
from PIL import Image
import plotly.graph_objects as go

from config import THEME as GLOBAL_THEME

# ============================================================
# PALETA ADAPTADA
# ============================================================
THEME = {
    "bg": GLOBAL_THEME["bg"],
    "card": GLOBAL_THEME["card"],
    "border": GLOBAL_THEME["card_border"],
    "cyan": GLOBAL_THEME["accent_cyan"],
    "purple": GLOBAL_THEME["accent_purple"],
    "text": GLOBAL_THEME["text"],
    "muted": GLOBAL_THEME["text_muted"],
}

# ============================================================
# FUNCIONES DE PROCESAMIENTO (sin cambios)
# ============================================================
def procesar_base64_a_cv2(contenido_base64):
    try:
        if not contenido_base64 or "," not in contenido_base64:
            return None
        _, datos_codificados = contenido_base64.split(",", 1)
        datos_binarios = base64.b64decode(datos_codificados)
        imagen_pil = Image.open(io.BytesIO(datos_binarios)).convert("RGB")
        imagen_cv = cv2.cvtColor(np.array(imagen_pil), cv2.COLOR_RGB2BGR)
        return imagen_cv
    except Exception:
        return None


def transformar_a_base64(imagen_bgr):
    imagen_rgb = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2RGB)
    imagen_pil = Image.fromarray(imagen_rgb)
    buffer = io.BytesIO()
    imagen_pil.save(buffer, format="JPEG", quality=95)
    codificado = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{codificado}"


def estiramiento_contraste(imagen, r1, r2):
    img_float = imagen.astype(np.float32)
    if r2 <= r1:
        r2 = r1 + 1
    img_estirada = (img_float - r1) * (255.0 / (r2 - r1))
    return np.clip(img_estirada, 0, 255).astype(np.uint8)


def aplicar_correccion_gamma(imagen, gamma):
    gamma = max(float(gamma), 0.01)
    inv_gamma = 1.0 / gamma
    tabla = np.array(
        [((i / 255.0) ** inv_gamma) * 255 for i in np.arange(256)],
        dtype=np.uint8,
    )
    return cv2.LUT(imagen, tabla)


def calcular_pdf(imagen_gris):
    if len(imagen_gris.shape) == 3:
        gris = cv2.cvtColor(imagen_gris, cv2.COLOR_BGR2GRAY)
    else:
        gris = imagen_gris.copy()
    histograma = cv2.calcHist([gris], [0], None, [256], [0, 256]).flatten()
    total_pixeles = gris.size
    if total_pixeles == 0:
        return np.zeros(256, dtype=np.float32), np.arange(256)
    pdf = histograma.astype(np.float32) / float(total_pixeles)
    return pdf, np.arange(256)


def calcular_cdf(pdf):
    cdf = np.cumsum(pdf)
    if cdf[-1] > 0:
        cdf = cdf / cdf[-1]
    return cdf.astype(np.float32)


def crear_figura_histograma(imagen, titulo, theme_mode="dark"):
    is_light = (theme_mode == "light")
    bg = "#ffffff" if is_light else THEME["card"]
    bar_color = "#0284c7" if is_light else THEME["cyan"]
    text_color = "#0f172a" if is_light else THEME["text"]
    template_name = "plotly_white" if is_light else "plotly_dark"

    if imagen is None:
        gris = np.zeros((1, 1), dtype=np.uint8)
    elif len(imagen.shape) == 3:
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    else:
        gris = imagen
    hist = cv2.calcHist([gris], [0], None, [256], [0, 256]).flatten()
    figura = go.Figure()
    figura.add_trace(
        go.Bar(
            x=np.arange(256),
            y=hist,
            marker_color=bar_color,
            hovertemplate="Intensidad: %{x}<br>Píxeles: %{y}<extra></extra>",
        )
    )
    figura.update_layout(
        title=titulo,
        xaxis_title="Intensidad",
        yaxis_title="Número de píxeles",
        xaxis=dict(range=[0, 255]),
        template=template_name,
        margin=dict(l=45, r=20, t=45, b=45),
        height=300,
        paper_bgcolor=bg,
        plot_bgcolor=bg,
        font=dict(color=text_color),
    )
    return figura


def calcular_estadisticas(imagen):
    if len(imagen.shape) == 3:
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    else:
        gris = imagen
    return float(np.mean(gris)), float(np.std(gris))


def ecualizacion_histograma(imagen):
    if len(imagen.shape) == 3:
        img_ycrcb = cv2.cvtColor(imagen, cv2.COLOR_BGR2YCrCb)
        canal_y = img_ycrcb[:, :, 0]
        pdf, _ = calcular_pdf(canal_y)
        cdf = calcular_cdf(pdf)
        tabla = np.clip((cdf * 255.0), 0, 255).astype(np.uint8)
        img_ycrcb[:, :, 0] = cv2.LUT(canal_y, tabla)
        return cv2.cvtColor(img_ycrcb, cv2.COLOR_YCrCb2BGR)
    else:
        pdf, _ = calcular_pdf(imagen)
        cdf = calcular_cdf(pdf)
        tabla = np.clip((cdf * 255.0), 0, 255).astype(np.uint8)
        return cv2.LUT(imagen, tabla)


def _construir_filtro_rampa(n, ventana="CUADRADA"):
    n = int(n)
    if n % 2 != 0:
        n += 1
    centro = n // 2
    k = np.arange(n) - centro
    k_abs = np.abs(k).astype(np.float32)
    rampa = k_abs.copy()
    k_norm = np.clip(k / centro, -1.0, 1.0)
    if ventana == "HAMMING":
        w = 0.54 + 0.46 * np.cos(np.pi * k_norm)
    elif ventana == "COSENO":
        w = np.cos(np.pi * k_norm / 2.0)
    else:
        w = np.ones(n, dtype=np.float32)
    w = np.clip(w, 0.0, 1.0)
    return (rampa * w).astype(np.float32)


def retroproyeccion_filtrada(imagen, ventana="CUADRADA"):
    if len(imagen.shape) == 3:
        img_ycrcb = cv2.cvtColor(imagen, cv2.COLOR_BGR2YCrCb)
        canal_y = img_ycrcb[:, :, 0].astype(np.float32)
    else:
        img_ycrcb = None
        canal_y = imagen.astype(np.float32)

    alto, ancho = canal_y.shape
    n = max(alto, ancho)
    filtro_1d = _construir_filtro_rampa(n, ventana=ventana)
    cy, cx = alto // 2, ancho // 2
    yy, xx = np.indices((alto, ancho))
    radio = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2).astype(np.int32)
    radio = np.clip(radio, 0, n - 1)
    filtro_2d = filtro_1d[radio]
    espectro = np.fft.fftshift(np.fft.fft2(canal_y))
    espectro_filtrado = espectro * filtro_2d
    reconstruida = np.real(np.fft.ifft2(np.fft.ifftshift(espectro_filtrado)))
    reconstruida = cv2.normalize(reconstruida, None, 0, 255, cv2.NORM_MINMAX)
    reconstruida = reconstruida.astype(np.uint8)
    canal_y_uint8 = canal_y.astype(np.uint8)
    _, mascara = cv2.threshold(canal_y_uint8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel_morf = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel_morf)
    mezcla = cv2.addWeighted(canal_y_uint8, 0.6, reconstruida, 0.4, 0)
    resultado_enmascarado = cv2.bitwise_and(mezcla, mezcla, mask=mascara)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    resultado_final = clahe.apply(resultado_enmascarado)
    if img_ycrcb is not None:
        img_ycrcb[:, :, 0] = resultado_final
        return cv2.cvtColor(img_ycrcb, cv2.COLOR_YCrCb2BGR)
    return resultado_final


def aplicar_filtro_seleccionado(imagen, tipo_filtro, parametro_slider):
    parametro_slider = float(parametro_slider)
    ksize = max(1, int(parametro_slider))
    if ksize % 2 == 0:
        ksize += 1
    kernel_morfologico = np.ones((ksize, ksize), np.uint8)

    if tipo_filtro == "GAUSSIANO":
        sigma = max(parametro_slider, 0.1)
        return cv2.GaussianBlur(imagen, (0, 0), sigmaX=sigma, sigmaY=sigma)
    if tipo_filtro == "MEDIANA":
        return cv2.medianBlur(imagen, ksize=ksize)
    if tipo_filtro == "MINIMO":
        return cv2.erode(imagen, kernel_morfologico, iterations=1)
    if tipo_filtro == "MAXIMO":
        return cv2.dilate(imagen, kernel_morfologico, iterations=1)
    if tipo_filtro == "RANGO":
        img_max = cv2.dilate(imagen, kernel_morfologico, iterations=1)
        img_min = cv2.erode(imagen, kernel_morfologico, iterations=1)
        return cv2.absdiff(img_max, img_min)
    if tipo_filtro == "ECUALIZACION_CDF":
        return ecualizacion_histograma(imagen)
    if tipo_filtro == "FBP_CUADRADA":
        return retroproyeccion_filtrada(imagen, ventana="CUADRADA")
    if tipo_filtro == "FBP_HAMMING":
        return retroproyeccion_filtrada(imagen, ventana="HAMMING")
    if tipo_filtro == "FBP_COSENO":
        return retroproyeccion_filtrada(imagen, ventana="COSENO")
    if tipo_filtro == "RAMPA_PURA":
        return retroproyeccion_filtrada(imagen, ventana="CUADRADA")
    return imagen


def mapear_tumor(imagen_preprocesada, umbral_min, umbral_max):
    if len(imagen_preprocesada.shape) == 3:
        gris = cv2.cvtColor(imagen_preprocesada, cv2.COLOR_BGR2GRAY)
    else:
        gris = imagen_preprocesada.copy()

    umbral_min = int(np.clip(umbral_min, 0, 255))
    umbral_max = int(np.clip(umbral_max, 0, 255))
    if umbral_min > umbral_max:
        umbral_min, umbral_max = umbral_max, umbral_min

    mascara = cv2.inRange(gris, umbral_min, umbral_max)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mascara_limpia = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)
    mascara_limpia = cv2.morphologyEx(mascara_limpia, cv2.MORPH_CLOSE, kernel)

    contornos, _ = cv2.findContours(mascara_limpia, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    alto, ancho = gris.shape[:2]
    pixeles_totales = alto * ancho
    pixeles_tumor = cv2.countNonZero(mascara_limpia)
    porcentaje_ocupado = (pixeles_tumor / pixeles_totales) * 100 if pixeles_totales > 0 else 0.0

    if len(imagen_preprocesada.shape) == 2:
        resultado_mapa = cv2.cvtColor(imagen_preprocesada, cv2.COLOR_GRAY2BGR)
    else:
        resultado_mapa = imagen_preprocesada.copy()

    cv2.drawContours(resultado_mapa, contornos, -1, (0, 255, 0), 2)
    return resultado_mapa, pixeles_tumor, porcentaje_ocupado


# ============================================================
# ESTILOS
# ============================================================
ESTILO_PANEL = {
    "backgroundColor": THEME["card"],
    "padding": "25px",
    "borderRadius": "12px",
    "border": f"1px solid {THEME['border']}",
    "boxShadow": "0 4px 12px rgba(0,0,0,0.3)",
    "color": THEME["text"],
    "textAlign": "left",
    "marginBottom": "25px",
}

ESTILO_TARJETA_IMAGEN = {
    "maxWidth": "420px",
    "width": "100%",
    "maxHeight": "400px",
    "objectFit": "contain",
    "borderRadius": "8px",
    "border": f"1px solid {THEME['border']}",
    "backgroundColor": THEME["bg"],
}


# ============================================================
# LAYOUT
# ============================================================
def procesamiento_layout():
    return html.Div(
        style={
            "fontFamily": "'Inter', 'Segoe UI', sans-serif",
            "textAlign": "center",
            "padding": "30px",
            "backgroundColor": THEME["bg"],
            "minHeight": "100vh",
            "color": THEME["text"],
        },
        children=[
            html.H1(
                "CT-SIM — Procesamiento de Imágenes",
                style={
                    "color": THEME["cyan"],
                    "fontWeight": "700",
                    "letterSpacing": "0.5px",
                },
            ),
            html.P(
                "Laboratorio educativo para estudiar contraste, gamma, histogramas y filtros de imágenes médicas.",
                style={"color": THEME["muted"], "marginTop": "-10px", "marginBottom": "30px"},
            ),
            # --- ZONA DE CARGA ---
            html.Div(
                style={"width": "75%", "margin": "0 auto", "padding": "10px"},
                children=[
                    dcc.Upload(
                        id="ct-cargar-imagen",
                        children=html.Div(
                            [
                                "Arrastra y suelta una imagen médica aquí o ",
                                html.A(
                                    "Explorar Archivos",
                                    style={
                                        "color": THEME["cyan"],
                                        "fontWeight": "bold",
                                        "textDecoration": "none",
                                    },
                                ),
                            ]
                        ),
                        style={
                            "width": "100%",
                            "height": "90px",
                            "lineHeight": "90px",
                            "borderWidth": "2px",
                            "borderStyle": "dashed",
                            "borderRadius": "10px",
                            "textAlign": "center",
                            "backgroundColor": THEME["card"],
                            "cursor": "pointer",
                            "color": THEME["muted"],
                            "borderColor": THEME["border"],
                        },
                        multiple=False,
                    )
                ],
            ),
            # --- CONTROLES Y MÉTRICAS ---
            html.Div(
                style={
                    "width": "75%",
                    "margin": "20px auto",
                    "display": "grid",
                    "gridTemplateColumns": "2fr 1fr",
                    "gap": "25px",
                },
                children=[
                    # Panel de parámetros
                    html.Div(
                        style=ESTILO_PANEL,
                        children=[
                            html.H3(
                                "Parámetros de Procesamiento Espacial",
                                style={
                                    "color": THEME["cyan"],
                                    "borderBottom": f"1px solid {THEME['border']}",
                                    "paddingBottom": "8px",
                                    "marginTop": "0",
                                },
                            ),
                            html.Label(
                                "1. Estiramiento de Contraste (Realce de Densidad):",
                                style={"fontWeight": "600", "color": THEME["text"]},
                            ),
                            dcc.RangeSlider(
                                id="ct-rango-contraste",
                                min=0, max=255, step=1, value=[0, 255],
                                marks={0: "0", 128: "128", 255: "255"},
                            ),
                            html.Div(
                                id="ct-texto-contraste-actual",
                                style={"fontSize": "12px", "color": THEME["muted"], "marginBottom": "20px"},
                            ),
                            html.Label(
                                "2. Corrección Gamma (Luminancia No Lineal):",
                                style={"fontWeight": "600", "color": THEME["text"]},
                            ),
                            dcc.Slider(
                                id="ct-slider-gamma",
                                min=0.1, max=5.0, step=0.1, value=1.0,
                                marks={0.1: "0.1", 1.0: "1.0", 5.0: "5.0"},
                            ),
                            html.Div(
                                id="ct-texto-gamma-actual",
                                style={"fontSize": "12px", "color": THEME["muted"], "marginBottom": "20px"},
                            ),
                            html.Label(
                                "3. Selección de Algoritmo de Filtrado:",
                                style={"fontWeight": "600", "color": THEME["text"]},
                            ),
                            dcc.Dropdown(
                                id="ct-selector-filtro",
                                options=[
                                    {"label": "Filtro Gaussiano (Suavizado Lineal)", "value": "GAUSSIANO"},
                                    {"label": "Filtro de Mediana (Ruido de Impulso)", "value": "MEDIANA"},
                                    {"label": "Filtro de Mínimo (Erosión / Sombras)", "value": "MINIMO"},
                                    {"label": "Filtro de Máximo (Dilatación / Luces)", "value": "MAXIMO"},
                                    {"label": "Filtro de Rango (Mapa de Textura)", "value": "RANGO"},
                                    {"label": "Ecualización por CDF (PDF Acumulada)", "value": "ECUALIZACION_CDF"},
                                    {"label": "FBP — Cuadrada / Ram-Lak (Extra nítida, ruidosa)", "value": "FBP_CUADRADA"},
                                    {"label": "FBP — Coseno (Equilibrada, limpia y definida)", "value": "FBP_COSENO"},
                                    {"label": "FBP — Hamming (Muy suave, homogénea, sin ruido)", "value": "FBP_HAMMING"},
                                    {"label": "Filtro Rampa puro (Reconstrucción)", "value": "RAMPA_PURA"},
                                ],
                                value="GAUSSIANO",
                                clearable=False,
                                style={"fontSize": "13px", "color": THEME["text"], "marginTop": "5px"},
                            ),
                            html.Label(
                                "Intensidad de Ventana / Sigma:",
                                style={"fontSize": "12px", "color": THEME["muted"], "marginTop": "10px", "display": "block"},
                            ),
                            dcc.Slider(
                                id="ct-slider-parametro-filtro",
                                min=1.0, max=15.0, step=1.0, value=3.0,
                                marks={i: str(i) for i in range(1, 16, 2)},
                            ),
                            html.Div(
                                id="ct-texto-filtro-actual",
                                style={"fontSize": "12px", "color": THEME["muted"], "marginBottom": "20px"},
                            ),
                            html.Label(
                                "4. Umbral de Segmentación / ROI:",
                                style={"fontWeight": "600", "color": THEME["text"]},
                            ),
                            dcc.RangeSlider(
                                id="ct-rango-corte",
                                min=0, max=255, step=1, value=[170, 255],
                                marks={0: "0", 128: "128", 255: "255"},
                            ),
                            html.Div(
                                id="ct-texto-corte-actual",
                                style={"fontSize": "12px", "color": THEME["muted"]},
                            ),
                        ],
                    ),
                    # Panel de métricas
                    html.Div(
                        style={**ESTILO_PANEL, "display": "flex", "flexDirection": "column", "justifyContent": "space-between"},
                        children=[
                            html.Div(
                                [
                                    html.H3(
                                        "Biometría Computacional",
                                        style={
                                            "color": THEME["purple"],
                                            "borderBottom": f"1px solid {THEME['border']}",
                                            "paddingBottom": "8px",
                                            "marginTop": "0",
                                        },
                                    ),
                                    html.Div(
                                        style={"marginTop": "20px"},
                                        children=[
                                            html.P("Tamaño absoluto detectado:", style={"color": THEME["muted"], "margin": "0"}),
                                            html.H2(
                                                id="ct-metrica-pixeles",
                                                children="0 px",
                                                style={"color": THEME["cyan"], "marginTop": "5px", "fontWeight": "bold"},
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        style={"marginTop": "20px"},
                                        children=[
                                            html.P("Porcentaje de área de interés (ROI):", style={"color": THEME["muted"], "margin": "0"}),
                                            html.H2(
                                                id="ct-metrica-porcentaje",
                                                children="0.00 %",
                                                style={"color": THEME["purple"], "marginTop": "5px", "fontWeight": "bold"},
                                            ),
                                        ],
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Button(
                                        "Exportar Mapa de Segmentación",
                                        id="ct-btn-descargar",
                                        style={
                                            "width": "100%",
                                            "padding": "12px",
                                            "backgroundColor": THEME["cyan"],
                                            "color": THEME["bg"],
                                            "border": "none",
                                            "borderRadius": "6px",
                                            "fontWeight": "bold",
                                            "cursor": "pointer",
                                            "fontSize": "14px",
                                        },
                                    ),
                                    dcc.Download(id="ct-componente-descarga"),
                                ]
                            ),
                        ],
                    ),
                ],
            ),
            # --- IMÁGENES ---
            html.Div(
                style={"display": "flex", "justifyContent": "center", "gap": "30px", "marginTop": "20px", "flexWrap": "wrap"},
                children=[
                    html.Div([
                        html.H4("Imagen Original", style={"color": THEME["muted"]}),
                        html.Img(id="ct-imagen-original", style=ESTILO_TARJETA_IMAGEN),
                    ]),
                    html.Div([
                        html.H4("Fase Preprocesada (Contraste + Gamma + Filtro)", style={"color": THEME["muted"]}),
                        html.Img(id="ct-imagen-contraste", style=ESTILO_TARJETA_IMAGEN),
                    ]),
                    html.Div([
                        html.H4("Segmentación / Región de Interés (ROI)", style={"color": THEME["muted"]}),
                        html.Img(id="ct-imagen-corte", style=ESTILO_TARJETA_IMAGEN),
                    ]),
                ],
            ),
            # --- HISTOGRAMAS ---
            html.Div(
                [
                    html.Div(
                        [
                            html.H3(
                                "Comparación de Histogramas",
                                style={"color": THEME["cyan"], "borderBottom": f"1px solid {THEME['border']}", "paddingBottom": "8px"},
                            ),
                            html.P(
                                "Permite comprobar cómo cambia la distribución de intensidades después del procesamiento.",
                                style={"color": THEME["muted"]},
                            ),
                        ],
                        style={"gridColumn": "1 / -1"},
                    ),
                    html.Div(
                        dcc.Graph(id="ct-histograma-original", config={"displayModeBar": False}),
                        style={"backgroundColor": THEME["card"], "padding": "10px", "borderRadius": "10px"},
                    ),
                    html.Div(
                        dcc.Graph(id="ct-histograma-procesado", config={"displayModeBar": False}),
                        style={"backgroundColor": THEME["card"], "padding": "10px", "borderRadius": "10px"},
                    ),
                ],
                style={
                    "width": "75%", "margin": "25px auto", "display": "grid",
                    "gridTemplateColumns": "1fr 1fr", "gap": "20px",
                },
            ),
            # --- ESTADÍSTICAS ---
            html.Div(
                [
                    html.Div(id="ct-estadisticas-original"),
                    html.Div(id="ct-estadisticas-procesado"),
                ],
                style={
                    "width": "75%", "margin": "0 auto 30px auto", "display": "grid",
                    "gridTemplateColumns": "1fr 1fr", "gap": "20px", "color": THEME["muted"],
                },
            ),
            dcc.Store(id="ct-store-imagen-b64"),
        ],
    )


# ============================================================
# CALLBACKS
# ============================================================
def registrar_callbacks_procesamiento(app):

    @app.callback(
        [
            Output("ct-imagen-original", "src"),
            Output("ct-imagen-contraste", "src"),
            Output("ct-imagen-corte", "src"),
            Output("ct-texto-contraste-actual", "children"),
            Output("ct-texto-gamma-actual", "children"),
            Output("ct-texto-filtro-actual", "children"),
            Output("ct-texto-corte-actual", "children"),
            Output("ct-metrica-pixeles", "children"),
            Output("ct-metrica-porcentaje", "children"),
            Output("ct-histograma-original", "figure"),
            Output("ct-histograma-procesado", "figure"),
            Output("ct-estadisticas-original", "children"),
            Output("ct-estadisticas-procesado", "children"),
            Output("ct-store-imagen-b64", "data"),
        ],
        [
            Input("ct-cargar-imagen", "contents"),
            Input("ct-rango-contraste", "value"),
            Input("ct-slider-gamma", "value"),
            Input("ct-selector-filtro", "value"),
            Input("ct-slider-parametro-filtro", "value"),
            Input("ct-rango-corte", "value"),
        ],
        [
            State("theme-store", "data"),
        ],
    )
    def actualizar_interfaz_ct(
        contenido_imagen, valores_contraste, valor_gamma,
        tipo_filtro, parametro_filtro, valores_corte,
        theme_mode="dark",
    ):
        if contenido_imagen is None:
            return (
                "", "", "",
                "Esperando archivo...", "Esperando archivo...",
                "Esperando filtro...", "Esperando archivo...",
                "0 px", "0.00 %",
                crear_figura_histograma(None, "Histograma original", theme_mode=theme_mode),
                crear_figura_histograma(None, "Histograma procesado", theme_mode=theme_mode),
                "Media: — | Desviación estándar: —",
                "Media: — | Desviación estándar: —",
                "",
            )

        imagen_cv = procesar_base64_a_cv2(contenido_imagen)
        if imagen_cv is None:
            return (
                "", "", "",
                "Formato no válido", "Formato no válido",
                "Formato no válido", "Formato no válido",
                "Error", "Error",
                crear_figura_histograma(None, "Histograma original", theme_mode=theme_mode),
                crear_figura_histograma(None, "Histograma procesado", theme_mode=theme_mode),
                "Media: — | Desviación estándar: —",
                "Media: — | Desviación estándar: —",
                "",
            )

        url_original = transformar_a_base64(imagen_cv)

        r1, r2 = valores_contraste
        img_procesada = estiramiento_contraste(imagen_cv, r1, r2)
        texto_contraste = f"Mapeo de histograma: [{r1} -> {r2}]."

        img_procesada = aplicar_correccion_gamma(img_procesada, valor_gamma)
        texto_gamma = f"Luminancia matemática: γ = {valor_gamma:.1f}."

        img_procesada = aplicar_filtro_seleccionado(img_procesada, tipo_filtro, parametro_filtro)

        if tipo_filtro == "GAUSSIANO":
            texto_filtro = f"Matriz Gaussiana lineal: Sigma = {float(parametro_filtro):.1f}."
        elif tipo_filtro == "ECUALIZACION_CDF":
            texto_filtro = "Transformación T(r) = (L-1)·CDF(r) — PDF acumulada sobre luminancia."
        elif tipo_filtro == "FBP_CUADRADA":
            texto_filtro = "FBP con ventana CUADRADA (Ram-Lak): Extraordinariamente duro y pixelado, máxima resolución pero alto ruido y anillos de Gibbs."
        elif tipo_filtro == "FBP_COSENO":
            texto_filtro = "FBP con ventana COSENO: Equilibrado, limpio y definido. Bordes claros y naturales con bajo grano."
        elif tipo_filtro == "FBP_HAMMING":
            texto_filtro = "FBP con ventana HAMMING: Muy suave, homogéneo y terso. El nivel de ruido más bajo de todos."
        elif tipo_filtro == "RAMPA_PURA":
            texto_filtro = "Filtro Rampa puro: H(f)=|f| — kernel clásico de reconstrucción tomográfica (Ram-Lak)."
        else:
            k_impar = int(parametro_filtro) if int(parametro_filtro) % 2 != 0 else int(parametro_filtro) + 1
            texto_filtro = f"Operador Estadístico [{tipo_filtro}]: Ventana = {k_impar}x{k_impar}."

        url_contraste = transformar_a_base64(img_procesada)

        c1, c2 = valores_corte
        img_mapeada, total_px, porc_roi = mapear_tumor(img_procesada, c1, c2)
        url_corte = transformar_a_base64(img_mapeada)
        texto_corte = f"Filtrado por ventana de densidad óptica: [{c1}, {c2}]."

        txt_px = f"{total_px:,} px"
        txt_porc = f"{porc_roi:.2f} %"

        hist_original = crear_figura_histograma(imagen_cv, "Histograma — imagen original", theme_mode=theme_mode)
        hist_procesado = crear_figura_histograma(img_procesada, "Histograma — imagen procesada", theme_mode=theme_mode)

        media_o, std_o = calcular_estadisticas(imagen_cv)
        media_p, std_p = calcular_estadisticas(img_procesada)

        estadistica_original = html.Div(
            [
                html.Strong("Original: ", style={"color": THEME["cyan"]}),
                html.Span(f"Media = {media_o:.2f} | Desviación estándar = {std_o:.2f}"),
            ],
            style={"backgroundColor": THEME["card"], "padding": "15px", "borderRadius": "8px"},
        )

        estadistica_procesado = html.Div(
            [
                html.Strong("Procesada: ", style={"color": THEME["purple"]}),
                html.Span(f"Media = {media_p:.2f} | Desviación estándar = {std_p:.2f}"),
            ],
            style={"backgroundColor": THEME["card"], "padding": "15px", "borderRadius": "8px"},
        )

        return (
            url_original, url_contraste, url_corte,
            texto_contraste, texto_gamma, texto_filtro, texto_corte,
            txt_px, txt_porc,
            hist_original, hist_procesado,
            estadistica_original, estadistica_procesado,
            url_corte,
        )

    @app.callback(
        Output("ct-componente-descarga", "data"),
        Input("ct-btn-descargar", "n_clicks"),
        State("ct-store-imagen-b64", "data"),
        prevent_initial_call=True,
    )
    def guardar_archivo_procesado_ct(n_clicks, datos_b64_store):
        if not datos_b64_store:
            raise PreventUpdate
        try:
            _, cuerpo_codificado = datos_b64_store.split(",", 1)
            datos_binarios = base64.b64decode(cuerpo_codificado)
            return dcc.send_bytes(datos_binarios, filename="segmentacion_roi.jpg")
        except Exception:
            raise PreventUpdate