# apps/ct_modulos/simulador.py
# ============================================================
# CT-SIM — Simulador de Tomografía Computarizada
# Motor matemático + Interfaz adaptada a Prometeo
# ============================================================

import base64
import io
from functools import lru_cache

import numpy as np
from PIL import Image
from skimage.data import shepp_logan_phantom
from skimage.transform import resize, radon, iradon
from dash import Input, Output, State, dcc, html

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
    "amber": GLOBAL_THEME["accent_amber"],
    "text": GLOBAL_THEME["text"],
    "muted": GLOBAL_THEME["text_muted"],
}

# ============================================================
# 1. GENERAR FANTOMA (CON CACHÉ DETERMINISTA)
# ============================================================
@lru_cache(maxsize=8)
def _generar_fantoma_cached(size=160):
    fantoma = shepp_logan_phantom()
    fantoma = resize(fantoma, (size, size), anti_aliasing=True)
    fantoma = fantoma.astype(np.float32)
    minimo, maximo = fantoma.min(), fantoma.max()
    if maximo > minimo:
        fantoma = (fantoma - minimo) / (maximo - minimo)
    return fantoma


def generar_fantoma(size=160):
    return _generar_fantoma_cached(size).copy()

# ============================================================
# 2. GENERAR ÁNGULOS
# ============================================================
def generar_angulos(numero_proyecciones=180):
    return np.linspace(0, 180, numero_proyecciones, endpoint=False)

# ============================================================
# 3. GENERAR PROYECCIONES
# ============================================================
def generar_proyecciones(imagen, numero_proyecciones=180):
    angulos = generar_angulos(numero_proyecciones)
    imagen = np.asarray(imagen, dtype=np.float32)

    alto, ancho = imagen.shape
    if alto != ancho:
        lado = min(alto, ancho)
        inicio_y = (alto - lado) // 2
        inicio_x = (ancho - lado) // 2
        imagen = imagen[inicio_y:inicio_y + lado, inicio_x:inicio_x + lado]

    if imagen.shape != (160, 160):
        imagen = resize(imagen, (160, 160), anti_aliasing=True)

    alto, ancho = imagen.shape
    y, x = np.ogrid[:alto, :ancho]
    centro_y, centro_x = (alto - 1) / 2, (ancho - 1) / 2
    radio = min(alto, ancho) / 2
    mascara = ((x - centro_x) ** 2 + (y - centro_y) ** 2) <= radio ** 2

    imagen_radon = imagen.copy()
    imagen_radon[~mascara] = 0

    proyecciones = radon(imagen_radon, theta=angulos, circle=True)
    return proyecciones, angulos

# ============================================================
# 4. GENERAR SINOGRAMA
# ============================================================
def generar_sinograma(imagen, numero_proyecciones=180):
    return generar_proyecciones(imagen, numero_proyecciones)

# ============================================================
# 5. NORMALIZACIÓN
# ============================================================
def normalizar_imagen(imagen):
    imagen = np.asarray(imagen, dtype=np.float32)
    minimo, maximo = imagen.min(), imagen.max()
    if maximo == minimo:
        return np.zeros_like(imagen)
    return (imagen - minimo) / (maximo - minimo)


def preparar_imagen_ct(imagen, size=160):
    imagen = np.asarray(imagen)
    if imagen.ndim == 3:
        imagen = imagen.mean(axis=2)
    imagen = imagen.astype(np.float32)
    imagen = normalizar_imagen(imagen)
    alto, ancho = imagen.shape
    escala = min(size / alto, size / ancho)
    nuevo_alto = max(1, int(alto * escala))
    nuevo_ancho = max(1, int(ancho * escala))
    imagen_redimensionada = resize(imagen, (nuevo_alto, nuevo_ancho), anti_aliasing=True).astype(np.float32)
    lienzo = np.zeros((size, size), dtype=np.float32)
    inicio_y = (size - nuevo_alto) // 2
    inicio_x = (size - nuevo_ancho) // 2
    lienzo[inicio_y:inicio_y + nuevo_alto, inicio_x:inicio_x + nuevo_ancho] = imagen_redimensionada
    return lienzo

# ============================================================
# 6. RUIDO
# ============================================================
def agregar_ruido(sinograma, nivel_ruido=0.02, semilla=42):
    sinograma = np.asarray(sinograma, dtype=np.float32)
    rng = np.random.default_rng(semilla)
    desviacion = nivel_ruido * np.max(np.abs(sinograma))
    ruido = rng.normal(loc=0.0, scale=desviacion, size=sinograma.shape)
    return sinograma + ruido

# ============================================================
# 7. FILTRO RAMPA
# ============================================================
def filtro_rampa(proyeccion):
    proyeccion = np.asarray(proyeccion, dtype=np.float32)
    n = len(proyeccion)
    espectro = np.fft.fft(proyeccion)
    frecuencias = np.fft.fftfreq(n)
    rampa = np.abs(frecuencias)
    espectro_filtrado = espectro * rampa
    return np.real(np.fft.ifft(espectro_filtrado))

# ============================================================
# 8. FILTRAR SINOGRAMA (VECTORIZADO)
# ============================================================
def filtrar_sinograma(sinograma, tipo_filtro="ramp"):
    sinograma = np.asarray(sinograma, dtype=np.float32)
    if tipo_filtro not in ["ramp", "hamming", "cosine"]:
        raise ValueError("Filtro no válido. Usar: ramp, hamming o cosine.")
    n = sinograma.shape[0]
    frecuencias = np.fft.fftfreq(n)
    filtro = np.abs(frecuencias).astype(np.float32)
    if tipo_filtro == "hamming":
        filtro = filtro * np.hamming(n).astype(np.float32)
    elif tipo_filtro == "cosine":
        filtro = filtro * np.abs(np.cos(np.pi * frecuencias)).astype(np.float32)

    # FFT 1D vectorizada sobre todas las columnas a la vez (axis=0)
    espectro = np.fft.fft(sinograma, axis=0)
    espectro_filtrado = espectro * filtro[:, None]
    return np.real(np.fft.ifft(espectro_filtrado, axis=0)).astype(np.float32)

# ============================================================
# 9. RETROPROYECCIÓN SIMPLE (OPTIMIZADA SIN ALOCACIONES EN BUCLE)
# ============================================================
def reconstruccion_retroproyeccion(sinograma, angulos):
    sinograma = np.asarray(sinograma, dtype=np.float32)
    numero_detecciones = sinograma.shape[0]
    numero_angulos = sinograma.shape[1]
    imagen = np.zeros((numero_detecciones, numero_detecciones), dtype=np.float32)
    centro = (numero_detecciones - 1) / 2.0
    y, x = np.indices(imagen.shape, dtype=np.float32)
    x = x - centro
    y = y - centro
    detector_centro = centro
    for i, angulo in enumerate(angulos):
        theta = np.deg2rad(angulo)
        posicion = x * np.cos(theta) + y * np.sin(theta) + detector_centro
        izquierda = np.floor(posicion).astype(np.int32)
        derecha = izquierda + 1
        peso = posicion - izquierda
        mascara = (izquierda >= 0) & (derecha < numero_detecciones)
        if np.any(mascara):
            sin_col = sinograma[:, i]
            izq_m = izquierda[mascara]
            der_m = derecha[mascara]
            peso_m = peso[mascara]
            imagen[mascara] += (1.0 - peso_m) * sin_col[izq_m] + peso_m * sin_col[der_m]
    if numero_angulos > 0:
        imagen *= (np.pi / (2.0 * numero_angulos))
    return normalizar_imagen(imagen)

# ============================================================
# 10. RECONSTRUCCIÓN FBP
# ============================================================
def reconstruir_fbp(sinograma, angulos, tipo_filtro="ramp"):
    if tipo_filtro not in ["ramp", "hamming", "cosine"]:
        raise ValueError("Filtro no válido.")
    reconstruida = iradon(sinograma, theta=angulos, filter_name=tipo_filtro, circle=True)
    return normalizar_imagen(reconstruida)

# ============================================================
# 11. SIMULACIÓN COMPLETA
# ============================================================
def simular_ct(imagen=None, size=160, numero_proyecciones=180, filtro="ramp",
               agregar_ruido_sinograma=False, nivel_ruido=0.02):
    if imagen is None:
        imagen = generar_fantoma(size=size)
    else:
        imagen = preparar_imagen_ct(imagen, size=size)

    sinograma, angulos = generar_sinograma(imagen, numero_proyecciones)
    sinograma_original = sinograma.copy()

    if agregar_ruido_sinograma:
        sinograma = agregar_ruido(sinograma, nivel_ruido=nivel_ruido)

    sinograma_filtrado = filtrar_sinograma(sinograma, tipo_filtro=filtro)
    retroproyeccion = reconstruccion_retroproyeccion(sinograma, angulos)
    reconstruida = reconstruir_fbp(sinograma, angulos, tipo_filtro=filtro)

    return {
        "imagen_original": imagen,
        "sinograma": sinograma,
        "sinograma_original": sinograma_original,
        "angulos": angulos,
        "retroproyeccion": retroproyeccion,
        "reconstruccion": reconstruida,
        "filtro": filtro,
        "numero_proyecciones": numero_proyecciones,
        "ruido": agregar_ruido_sinograma,
        "nivel_ruido": nivel_ruido,
        "sinograma_filtrado": sinograma_filtrado,
    }

# ============================================================
# 12. MÉTRICAS
# ============================================================
def calcular_rmse(referencia, reconstruccion):
    referencia = normalizar_imagen(referencia)
    reconstruccion = normalizar_imagen(reconstruccion)
    diferencia = referencia - reconstruccion
    return float(np.sqrt(np.mean(diferencia ** 2)))


def calcular_correlacion(referencia, reconstruccion):
    ref = np.asarray(referencia, dtype=np.float32).ravel()
    rec = np.asarray(reconstruccion, dtype=np.float32).ravel()
    if np.std(ref) == 0 or np.std(rec) == 0:
        return 0.0
    return float(np.corrcoef(ref, rec)[0, 1])

# ============================================================
# 13. UTILIDADES DE IMAGEN PARA DASH
# ============================================================
def matriz_a_base64(matriz):
    """Convierte una matriz NumPy en una imagen base64 PNG."""
    matriz = np.asarray(matriz, dtype=np.float32)
    matriz = normalizar_imagen(matriz)
    matriz_uint8 = (matriz * 255).astype(np.uint8)
    imagen = Image.fromarray(matriz_uint8)
    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


ESTILO_TARJETA_IMAGEN = {
    "width": "100%",
    "maxHeight": "280px",
    "objectFit": "contain",
    "borderRadius": "8px",
    "border": f"1px solid {THEME['border']}",
    "backgroundColor": THEME["bg"],
}


# ============================================================
# 14. LAYOUT DEL SIMULADOR
# ============================================================
def simulador_layout():
    return html.Div(
        style={
            "padding": "30px",
            "backgroundColor": THEME["bg"],
            "minHeight": "100vh",
            "color": THEME["text"],
            "fontFamily": "'Inter', 'Segoe UI', sans-serif",
        },
        children=[
            # ----- HERO -----
            html.Div(
                style={
                    "background": f"linear-gradient(135deg, {THEME['card']} 0%, {THEME['bg']} 100%)",
                    "border": f"1px solid {THEME['border']}",
                    "borderRadius": "16px",
                    "padding": "30px 35px",
                    "marginBottom": "24px",
                },
                children=[
                    html.Div(
                        "SIMULADOR CT",
                        style={
                            "fontSize": "11px",
                            "fontWeight": "700",
                            "letterSpacing": "2px",
                            "color": THEME["cyan"],
                            "marginBottom": "10px",
                        },
                    ),
                    html.H1(
                        "Simulador de Tomografía Computarizada",
                        style={"fontSize": "34px", "fontWeight": "700", "margin": "0 0 10px 0"},
                    ),
                    html.P(
                        "Genera proyecciones a partir de un fantoma, construye el sinograma, "
                        "aplica filtros de reconstrucción y compara los resultados de la "
                        "retroproyección simple frente a la retroproyección filtrada (FBP).",
                        style={"color": THEME["muted"], "fontSize": "15px", "lineHeight": "1.7", "margin": "0"},
                    ),
                ],
            ),

            # ----- CONTROLES -----
            html.Div(
                style={
                    "backgroundColor": THEME["card"],
                    "border": f"1px solid {THEME['border']}",
                    "borderRadius": "16px",
                    "padding": "24px",
                    "marginBottom": "24px",
                },
                children=[
                    html.H3(
                        "Parámetros de simulación",
                        style={"color": THEME["cyan"], "marginTop": "0", "marginBottom": "20px", "fontSize": "18px"},
                    ),
                    html.Div(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                            "gap": "24px",
                        },
                        children=[
                            # Número de proyecciones
                            html.Div([
                                html.Label("Número de proyecciones", style={"fontWeight": "600", "display": "block", "marginBottom": "8px"}),
                                dcc.Slider(
                                    id="ct-sim-proyecciones",
                                    min=30, max=360, step=10, value=180,
                                    marks={30: "30", 90: "90", 180: "180", 270: "270", 360: "360"},
                                ),
                            ]),
                            # Filtro
                            html.Div([
                                html.Label("Filtro de reconstrucción", style={"fontWeight": "600", "display": "block", "marginBottom": "8px"}),
                                dcc.Dropdown(
                                    id="ct-sim-filtro",
                                    options=[
                                        {"label": "Ramp (Ram-Lak)", "value": "ramp"},
                                        {"label": "Hamming", "value": "hamming"},
                                        {"label": "Cosine", "value": "cosine"},
                                    ],
                                    value="ramp",
                                    clearable=False,
                                    style={"fontSize": "13px", "color": THEME["text"]},
                                ),
                            ]),
                            # Ruido
                            html.Div([
                                html.Label("Ruido gaussiano en el sinograma", style={"fontWeight": "600", "display": "block", "marginBottom": "8px"}),
                                dcc.Checklist(
                                    id="ct-sim-ruido",
                                    options=[{"label": " Añadir ruido", "value": "si"}],
                                    value=[],
                                    labelStyle={"color": THEME["text"], "fontSize": "14px"},
                                ),
                            ]),
                            # Tamaño del fantoma
                            html.Div([
                                html.Label("Tamaño del fantoma (px)", style={"fontWeight": "600", "display": "block", "marginBottom": "8px"}),
                                dcc.Slider(
                                    id="ct-sim-size",
                                    min=100, max=256, step=4, value=160,
                                    marks={100: "100", 160: "160", 200: "200", 256: "256"},
                                ),
                            ]),
                        ],
                    ),
                    html.Div(
                        style={"marginTop": "20px", "textAlign": "center"},
                        children=[
                            html.Button(
                                [
                                    html.I(className="fa-solid fa-play", style={"marginRight": "8px"}),
                                    "Ejecutar simulación",
                                ],
                                id="ct-sim-ejecutar",
                                n_clicks=0,
                                style={
                                    "backgroundColor": THEME["cyan"],
                                    "color": THEME["bg"],
                                    "border": "none",
                                    "borderRadius": "10px",
                                    "padding": "13px 30px",
                                    "fontSize": "14px",
                                    "fontWeight": "700",
                                    "cursor": "pointer",
                                    "letterSpacing": "0.5px",
                                },
                            ),
                        ],
                    ),
                ],
            ),

            # ----- MÉTRICAS -----
            html.Div(
                id="ct-sim-metricas",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
                    "gap": "16px",
                    "marginBottom": "24px",
                },
            ),

            # ----- RESULTADOS -----
            html.Div(
                id="ct-sim-resultados",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))",
                    "gap": "20px",
                },
            ),

            # Store interno para mantener los resultados
            dcc.Store(id="ct-sim-store-resultados"),
        ],
    )


# ============================================================
# 15. CALLBACKS
# ============================================================
def registrar_callbacks_simulador(app):

    @app.callback(
        Output("ct-sim-metricas", "children"),
        Output("ct-sim-resultados", "children"),
        Output("ct-sim-store-resultados", "data"),
        Input("ct-sim-ejecutar", "n_clicks"),
        State("ct-sim-proyecciones", "value"),
        State("ct-sim-filtro", "value"),
        State("ct-sim-ruido", "value"),
        State("ct-sim-size", "value"),
        prevent_initial_call=True,
    )
    def ejecutar_simulacion(n_clicks, num_proy, filtro, ruido_valor, size):
        if not n_clicks:
            return [], [], None

        usar_ruido = bool(ruido_valor)

        # --- Ejecutar simulación ---
        resultados = simular_ct(
            size=int(size),
            numero_proyecciones=int(num_proy),
            filtro=filtro,
            agregar_ruido_sinograma=usar_ruido,
            nivel_ruido=0.02,
        )

        # --- Métricas ---
        rmse = calcular_rmse(resultados["imagen_original"], resultados["reconstruccion"])
        correlacion = calcular_correlacion(resultados["imagen_original"], resultados["reconstruccion"])

        metricas = [
            _tarjeta_metrica("Proyecciones", f"{resultados['numero_proyecciones']}", THEME["cyan"]),
            _tarjeta_metrica("Filtro", resultados["filtro"].capitalize(), THEME["purple"]),
            _tarjeta_metrica("Ruido", "Sí" if usar_ruido else "No", THEME["amber"]),
            _tarjeta_metrica("RMSE", f"{rmse:.4f}", THEME["cyan"]),
            _tarjeta_metrica("Correlación", f"{correlacion:.4f}", THEME["purple"]),
        ]

        # --- Imágenes ---
        resultados_visuales = [
            _tarjeta_imagen("Fantoma original", matriz_a_base64(resultados["imagen_original"])),
            _tarjeta_imagen("Sinograma", matriz_a_base64(resultados["sinograma"])),
            _tarjeta_imagen("Retroproyección simple", matriz_a_base64(resultados["retroproyeccion"])),
            _tarjeta_imagen(f"Reconstrucción FBP ({resultados['filtro']})", matriz_a_base64(resultados["reconstruccion"])),
        ]

        return metricas, resultados_visuales, {"ok": True}


def _tarjeta_metrica(titulo, valor, color):
    return html.Div(
        className="info-card",
        style={
            "borderRadius": "12px",
            "padding": "16px 18px",
        },
        children=[
            html.Div(titulo.upper(), style={
                "fontSize": "10px", "fontWeight": "700", "letterSpacing": "1.4px",
                "color": THEME["muted"], "marginBottom": "6px",
            }),
            html.Div(valor, style={"fontSize": "22px", "fontWeight": "800", "color": color}),
        ],
    )


def _tarjeta_imagen(titulo, src):
    return html.Div(
        className="info-card",
        style={
            "borderRadius": "14px",
            "padding": "16px",
        },
        children=[
            html.Div(titulo, style={
                "fontSize": "12px", "fontWeight": "700",
                "color": THEME["cyan"], "marginBottom": "10px",
            }),
            html.Img(src=src, style=ESTILO_TARJETA_IMAGEN),
        ],
    )