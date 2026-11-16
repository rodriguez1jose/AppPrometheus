#interfaz.py - rx
from dash import dcc, html
from config import THEME

# ============================================================
# DETECTOR DE TIPO DE CONSULTA IA
# ============================================================
def detectar_tipo_consulta(pregunta):
    texto = pregunta.lower()
    palabras_visual = ["cuadro", "tabla", "comparación", "comparacion", "comparar", "mapa conceptual", "mapa mental", "diagrama", "esquema"]
    if any(p in texto for p in palabras_visual): return "visual"

    palabras_imagen = ["muéstrame", "muestrame", "radiografía", "radiografia", "foto", "imagen rx", "imagen radiográfica", "imagen radiografica"]
    if any(p in texto for p in palabras_imagen): return "imagen"

    palabras_video = ["video", "vídeo", "youtube", "tutorial", "demostración", "demostracion"]
    if any(p in texto for p in palabras_video): return "video"

    return "gemini"

# ============================================================
# ESTILOS BASE
# ============================================================
STYLE_CONTAINER = {
    "backgroundColor": THEME["bg"],
    "minHeight": "100vh",
    "fontFamily": "'Inter', 'Segoe UI', sans-serif",
    "color": THEME["text"],
    "padding": "20px",
}

# ============================================================
# COMPONENTES
# ============================================================
def crear_etiqueta(texto):
    return html.Div(
        texto.upper(),
        style={
            "fontSize": "12px",
            "letterSpacing": "2px",
            "color": THEME["pink"],
            "fontWeight": "700",
            "marginBottom": "14px",
        },
    )

# ============================================================
# PÁGINA DE INICIO
# ============================================================
def crear_inicio():
    return html.Div(
        [
            crear_etiqueta("Radiología · Imagenología"),
            html.H1(
                ["Plataforma Educativa de ", html.Span("Rayos X", style={"color": THEME["pink"]})],
                style={"fontSize": "44px", "fontWeight": "700", "lineHeight": "1.15", "letterSpacing": "-1px", "margin": "0 0 14px 0", "color": THEME["text"]},
            ),
            html.P(
                "Explora la física detrás de los Rayos X, la formación de imágenes, el procesamiento digital, el análisis radiográfico y un asistente de IA especializado — todo en un solo recorrido interactivo.",
                style={"fontSize": "16px", "lineHeight": "1.7", "maxWidth": "820px", "color": THEME["text_secondary"], "margin": "0 0 28px 0"},
            ),
            html.Div(style={"width": "65px", "height": "3px", "backgroundColor": THEME["pink"], "marginBottom": "32px"}),
            dcc.Link(
                html.Button(
                    "COMENZAR RECORRIDO  →",
                    style={
                        "backgroundColor": THEME["accent_cyan"], "color": THEME["bg"], "border": "none",
                        "borderRadius": "7px", "padding": "12px 22px", "fontSize": "14px",
                        "fontWeight": "700", "letterSpacing": "0.8px", "cursor": "pointer", "marginBottom": "35px",
                    },
                ),
                href="/imaging/rx/fundamentos",
                style={"textDecoration": "none"},
            ),
            html.Div(
                [
                    html.H2("Comienza tu recorrido", style={"fontSize": "23px", "fontWeight": "700", "margin": "0 0 7px 0", "color": THEME["text"]}),
                    html.P("Explora la plataforma paso a paso.", style={"fontSize": "14px", "color": THEME["text_secondary"], "margin": "0 0 22px 0"}),
                    html.Div(
                        [
                            crear_tarjeta("fa-solid fa-radiation", "Fundamentos de RX", "Comprende la naturaleza de los Rayos X, sus propiedades y los principios físicos.", "/fundamentos"),
                            crear_tarjeta("fa-solid fa-image", "Formación de imagen", "Explora la atenuación, las interacciones con la materia y la imagen radiográfica.", "/formacion"),
                            crear_tarjeta("fa-solid fa-sliders", "Procesamiento", "Trabaja con imágenes radiográficas y comprende técnicas de procesamiento digital.", "/procesamiento"),
                            crear_tarjeta("fa-solid fa-chart-line", "Análisis", "Obtén información cuantitativa de las imágenes y compara resultados.", "/analisis"),
                        ],
                        style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))", "gap": "18px", "maxWidth": "1100px"},
                    ),
                ]
            ),
            html.Div(
                [
                    html.Br(),
                    html.Div("UN POCO DE HISTORIA", style={"fontSize": "18px", "letterSpacing": "2px", "fontWeight": "700", "color": THEME["pink"], "marginBottom": "10px"}),
                    html.H2("De Röntgen a Curie: los orígenes de los Rayos X", style={"fontSize": "23px", "fontWeight": "700", "margin": "0 0 7px 0", "color": THEME["text"]}),
                ]
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("BIENVENIDO AL MUNDO DE LOS RAYOS X", style={"fontSize": "12px", "letterSpacing": "2px", "fontWeight": "700", "color": THEME["pink"], "marginBottom": "12px"}),
                            html.H2("Una ventana al interior del cuerpo humano", style={"fontSize": "29px", "fontWeight": "700", "lineHeight": "1.25", "color": THEME["text"], "margin": "0 0 15px 0"}),
                            html.P(
                                "Los Rayos X revolucionaron la medicina al permitir observar el interior del cuerpo humano sin cirugía. En esta plataforma podrás seguir el recorrido completo: desde la producción hasta el análisis de una imagen radiográfica.",
                                style={"fontSize": "15px", "lineHeight": "1.7", "color": THEME["card_text_secondary"], "margin": "0 0 22px 0"},
                            ),
                            html.Div(
                                [
                                    html.Div("1895", style={"fontSize": "24px", "fontWeight": "700", "color": THEME["pink"], "minWidth": "65px"}),
                                    html.Div(
                                        [
                                            html.Div("Descubrimiento de los Rayos X", style={"fontSize": "15px", "fontWeight": "700", "color": THEME["text"], "marginBottom": "4px"}),
                                            html.Div("Wilhelm Conrad Röntgen identifica una nueva forma de radiación.", style={"fontSize": "14px", "lineHeight": "1.5", "color": THEME["card_text_secondary"]}),
                                        ],
                                        style={"borderLeft": f"2px solid {THEME['pink']}", "paddingLeft": "16px"},
                                    ),
                                ],
                                style={"display": "flex", "alignItems": "center", "gap": "12px", "marginBottom": "24px"},
                            ),
                        ],
                        style={"flex": "1.35", "minWidth": "350px"},
                    ),
                    html.Div(
                        [
                            html.Div("UN POCO DE HISTORIA", style={"fontSize": "11px", "letterSpacing": "1.8px", "fontWeight": "700", "color": THEME["pink"], "marginBottom": "12px", "textAlign": "center"}),
                            html.Div(
                                [
                                    html.Img(src="/assets/interfaz/primera_radiografia.jpg", style={"width": "100%", "maxWidth": "245px", "height": "145px", "objectFit": "contain", "borderRadius": "8px", "display": "block", "marginBottom": "12px"}),
                                    html.Div("La primera radiografía", style={"fontSize": "15px", "fontWeight": "700", "color": THEME["text"], "textAlign": "center"}),
                                ],
                                style={
                                    "minHeight": "220px", "display": "flex", "flexDirection": "column", "alignItems": "center", "justifyContent": "center",
                                    "backgroundColor": THEME["bg_secondary"], "border": f"2px dashed {THEME['border']}", "borderRadius": "12px", "padding": "20px",
                                },
                            ),
                        ],
                        style={"flex": "0.8", "minWidth": "260px", "maxWidth": "330px"},
                    ),
                ],
                style={
                    "display": "flex", "alignItems": "center", "gap": "42px", "backgroundColor": THEME["card"],
                    "border": f"1px solid {THEME['border']}", "borderRadius": "16px", "padding": "32px 34px",
                    "maxWidth": "1100px", "boxSizing": "border-box", "marginTop": "20px", "marginBottom": "42px",
                },
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("PERSONAJES QUE TRANSFORMARON LA CIENCIA", style={"fontSize": "11px", "letterSpacing": "1.8px", "fontWeight": "700", "color": THEME["pink"], "marginBottom": "8px"}),
                            html.H3("Marie Curie", style={"fontSize": "23px", "fontWeight": "700", "color": THEME["text"], "margin": "0 0 8px 0"}),
                            html.P(
                                "Marie Curie fue una figura fundamental en el estudio de la radiactividad y recibió el Premio Nobel de Física en 1903.",
                                style={"fontSize": "14px", "lineHeight": "1.7", "color": THEME["card_text_secondary"], "margin": "0"},
                            ),
                        ],
                        style={"flex": "1", "minWidth": "300px"},
                    ),
                    html.Div(
                        [html.Img(src="/assets/interfaz/marie_curie.jpg", style={"width": "150px", "height": "150px", "objectFit": "cover", "borderRadius": "10px"})],
                        style={"flexShrink": "0", "padding": "5px", "border": f"2px solid {THEME['border']}", "borderRadius": "12px", "backgroundColor": THEME["bg_secondary"]},
                    ),
                ],
                style={
                    "display": "flex", "alignItems": "center", "justifyContent": "space-between", "gap": "28px",
                    "backgroundColor": THEME["card"], "border": f"1px solid {THEME['border']}", "borderRadius": "14px",
                    "padding": "22px 26px", "maxWidth": "1100px", "boxSizing": "border-box", "marginBottom": "42px",
                },
            ),
        ],
        style=STYLE_CONTAINER
    )

# ============================================================
# COMPONENTES DEL SIDEBAR (MENÚ LATERAL)
# ============================================================
def crear_logo():
    return html.Div(
        [
            html.Div(
                [
                    html.Img(
                        src="/assets/interfaz/logo_rx.svg",
                        style={"width": "38px", "height": "38px", "marginRight": "12px", "objectFit": "contain"}
                    ),
                    html.Span("RAYOS X", style={"fontSize": "25px", "fontWeight": "700", "letterSpacing": "1.5px", "color": THEME["text"]}),
                ],
                style={"display": "flex", "alignItems": "center"},
            ),
            html.Div("LIBRO ELECTRÓNICO INTERACTIVO", style={"fontSize": "9px", "letterSpacing": "1.4px", "color": THEME["pink"], "marginTop": "8px", "fontWeight": "700"}),
            html.Div(style={"height": "1px", "backgroundColor": THEME["border"], "marginTop": "22px", "marginBottom": "25px"}),
        ]
    )
# 1. Menú lateral (Navegación nativa con dcc.Link)
def crear_item_menu(icono, texto, ruta, ruta_actual=""):
    full_ruta = f"/imaging/rx{ruta}" if ruta != "/" else "/imaging/rx"
    es_activo = (ruta_actual == full_ruta)
    
    color_texto = THEME["accent_cyan"] if es_activo else THEME["text_muted"]
    bg_item = "rgba(56, 189, 248, 0.12)" if es_activo else "transparent"

    return dcc.Link(
        html.Div(
            [
                html.I(className=f"{icono} fa-fw", style={"marginRight": "12px", "fontSize": "15px", "color": THEME["accent_cyan"]}),
                html.Span(texto, style={"fontSize": "13.5px", "fontWeight": "600" if es_activo else "500"}),
            ],
            className="sidebar-link",
            style={
                "display": "flex", 
                "alignItems": "center", 
                "padding": "11px 14px", 
                "borderRadius": "10px", 
                "color": color_texto, 
                "backgroundColor": bg_item,
                "marginBottom": "3px", 
                "transition": "all 0.15s ease", 
                "width": "100%",
                "boxSizing": "border-box",
            }
        ),
        href=full_ruta,
        style={"textDecoration": "none", "display": "block", "width": "100%"}
    )

# 2. Tarjeta de inicio (Enlace nativo con dcc.Link)
def crear_tarjeta(icono, titulo, descripcion, ruta):
    ruta_correcta = f"/imaging/rx{ruta}" if ruta.startswith("/") else ruta
    return html.Div(
        [
            html.Div(
                [
                    html.I(className=icono, style={"fontSize": "22px", "marginRight": "12px", "color": THEME["accent_cyan"], "width": "24px", "textAlign": "center"}),
                    html.Span(titulo, style={"fontSize": "18px", "fontWeight": "700", "color": THEME["card_text"]}),
                ],
                style={"display": "flex", "alignItems": "center", "marginBottom": "18px"},
            ),
            html.P(
                descripcion,
                style={"fontSize": "14px", "lineHeight": "1.6", "color": THEME["card_text_secondary"], "margin": "0 0 20px 0"},
            ),
            dcc.Link(
                "Explorar →",
                href=ruta_correcta,
                className="explorar-link",
            ),
        ],
        style={
            "backgroundColor": THEME["card"], 
            "border": f"1px solid {THEME['border']}",
            "borderRadius": "14px",
            "padding": "26px 28px",
            "minHeight": "190px",
            "boxSizing": "border-box",
            "boxShadow": "0 4px 12px rgba(0,0,0, 0.2)",
        },
    )

# 3. Sidebar (Navegación unificada con dcc.Link y resaltado activo)
def crear_sidebar(pathname="/imaging/rx"):
    return html.Div(
        [
            crear_logo(),
            html.Div(
                "CONTENIDO",
                style={"fontSize": "9px", "letterSpacing": "1.7px", "color": THEME["accent_cyan"], "marginBottom": "12px", "paddingLeft": "13px", "fontWeight": "700"},
            ),
            # --- BOTÓN VOLVER A IMAGING ---
            dcc.Link(
                html.Div(
                    [
                        html.I(className="fa-solid fa-arrow-left", style={"marginRight": "12px", "fontSize": "14px", "color": THEME["text_muted"]}),
                        html.Span("Volver a Imagenología", style={"fontSize": "13px", "fontWeight": "500"}),
                    ],
                    className="sidebar-link",
                    style={"display": "flex", "alignItems": "center", "padding": "11px 14px", "borderRadius": "10px", "color": THEME["text_muted"], "marginBottom": "15px", "border": f"1px solid {THEME['border']}"}
                ),
                href="/imaging",
                style={"textDecoration": "none", "display": "block", "width": "100%"}
            ),
            # Menú navegable con rutas maestras
            crear_item_menu("fa-solid fa-house", "Inicio", "/", pathname),
            crear_item_menu("fa-solid fa-radiation", "Fundamentos de RX", "/fundamentos", pathname),
            crear_item_menu("fa-solid fa-image", "Formación de imagen", "/formacion", pathname),
            crear_item_menu("fa-solid fa-sliders", "Procesamiento", "/procesamiento", pathname),
            crear_item_menu("fa-solid fa-chart-line", "Análisis", "/analisis", pathname),
            crear_item_menu("fa-solid fa-clipboard-check", "Actividades", "/actividades", pathname),
        ],
        style={
            "width": "270px",
            "minWidth": "270px",
            "backgroundColor": THEME["bg_secondary"],
            "borderRight": f"1px solid {THEME['border']}",
            "padding": "28px 18px",
            "position": "sticky",
            "top": "0",
            "height": "100vh",
            "overflowY": "auto",
            "boxSizing": "border-box",
            "fontFamily": "'Inter', 'Segoe UI', sans-serif",
        },
    )