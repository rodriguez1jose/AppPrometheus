"""
Módulo de Formación de la Imagen Radiográfica
Proyecto_RX

Función pública:
    mostrar_formacion()
"""

from dash import html, dcc
from config import THEME as GLOBAL_THEME

# ============================================================
# PALETA ADAPTADA A PROMETEO
# ============================================================
CREMA = GLOBAL_THEME["text"]               # Texto principal (Blanco)
BEIGE = GLOBAL_THEME["text_muted"]         # Texto secundario (Gris claro)
AZUL_OSCURO = GLOBAL_THEME["bg"]           # Fondo secundario (Azul muy oscuro)
AZUL = GLOBAL_THEME["accent_cyan"]         # Acento (Celeste)
AZUL_MEDIO = GLOBAL_THEME["card_border"]   # Bordes
FONDO_CLARO = GLOBAL_THEME["card"]         # Fondo de las tarjetas


# ============================================================
# UTILIDADES DE DISEÑO
# ============================================================

def _tarjeta(titulo, contenido, icono="01"):
    """Tarjeta educativa con el mismo estilo general de Teoría."""

    return html.Div(
        [
            html.Div(
                [
                    html.Span(
                        icono,
                        className="rx-badge-pill",
                        style={
                            "display": "inline-flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "width": "48px",
                            "height": "48px",
                            "minWidth": "48px",
                            "backgroundColor": GLOBAL_THEME["accent_cyan"],
                            "color": GLOBAL_THEME["bg"],
                            "borderRadius": "12px",
                            "fontSize": "14px",
                            "fontWeight": "800",
                            "boxSizing": "border-box",
                        },
                    ),
                    html.H3(
                        titulo,
                        style={
                            "margin": "0",
                            "fontSize": "21px",
                            "lineHeight": "1.2",
                            "fontWeight": "700",
                            "color": GLOBAL_THEME["text"],
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "14px",
                    "marginBottom": "16px",
                },
            ),
            html.Div(
                contenido,
                style={
                    "color": GLOBAL_THEME["text_muted"],
                    "fontSize": "14px",
                    "lineHeight": "1.7",
                },
            ),
        ],
        className="rx-card",
        style={
            "backgroundColor": GLOBAL_THEME["card"],
            "border": f"1px solid {GLOBAL_THEME['card_border']}",
            "borderRadius": "16px",
            "padding": "24px 26px",
            "boxSizing": "border-box",
            "minHeight": "0",
        },
    )

def _imagen(nombre, alt, max_height="330px"):
    """Imagen dentro de un contenedor elegante y adaptable."""

    return html.Div(
        [
            html.Img(
                src=f"/assets/formacion/{nombre}",
                alt=alt,
                style={
                    "display": "block",
                    "width": "100%",
                    "maxWidth": "100%",
                    "height": "auto",
                    "maxHeight": max_height,
                    "objectFit": "contain",
                    "borderRadius": "12px",
                },
            )
        ],
        style={
            "width": "100%",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "overflow": "hidden",
            "backgroundColor": GLOBAL_THEME["bg"], # <-- CAMBIO A OSCURO
            "border": f"1px solid {GLOBAL_THEME['card_border']}", # <-- BORDE SUTIL
            "borderRadius": "14px",
            "padding": "10px",
            "boxSizing": "border-box",
        },
    )

def _flujo(pasos, altura="76px"):
    """Flujo horizontal."""

    elementos = []

    for i, paso in enumerate(pasos):
        elementos.append(
            html.Div(
                paso,
                className="rx-flow-step",
                style={
                    "flex": "1 1 0",
                    "minWidth": "0",
                    "height": altura,
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "padding": "8px 7px",
                    "boxSizing": "border-box",
                    "backgroundColor": GLOBAL_THEME["card"],
                    "color": GLOBAL_THEME["accent_cyan"],
                    "border": f"1px solid {GLOBAL_THEME['card_border']}",
                    "borderRadius": "12px",
                    "fontFamily": "'Inter', sans-serif",
                    "fontSize": "11px",
                    "fontWeight": "700",
                    "lineHeight": "1.2",
                    "textAlign": "center",
                    "whiteSpace": "normal",
                    "overflow": "hidden",
                    "overflowWrap": "break-word",
                },
            )
        )

        if i < len(pasos) - 1:
            elementos.append(
                html.Div(
                    "→",
                    style={
                        "flex": "0 0 24px",
                        "width": "24px",
                        "minWidth": "24px",
                        "height": altura,
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "boxSizing": "border-box",
                        "color": GLOBAL_THEME["text_muted"],
                        "fontFamily": "'Inter', sans-serif",
                        "fontSize": "20px",
                        "fontWeight": "700",
                        "lineHeight": "1",
                    },
                )
            )

    return html.Div(
        elementos,
        className="rx-flow-container",
        style={
            "display": "flex",
            "flexDirection": "row",
            "flexWrap": "nowrap",
            "alignItems": "center",
            "width": "100%",
            "minWidth": "0",
            "height": "auto",
            "gap": "5px",
            "padding": "14px 10px",
            "margin": "22px 0 28px 0",
            "boxSizing": "border-box",
            "overflow": "hidden",
            "backgroundColor": GLOBAL_THEME["bg"],
            "border": f"1px solid {GLOBAL_THEME['card_border']}",
            "borderRadius": "18px",
        },
    )

def _bloque_explicativo(etiqueta, titulo, texto):
    """Bloque corto para explicar una imagen o concepto."""

    return html.Div(
        [
            html.Div(
                etiqueta,
                style={
                    "fontSize": "10px",
                    "fontWeight": "700",
                    "letterSpacing": "1.4px",
                    "color": GLOBAL_THEME["accent_cyan"],
                    "marginBottom": "7px",
                },
            ),
            html.H3(
                titulo,
                style={
                    "margin": "0 0 8px 0",
                    "fontSize": "20px",
                    "lineHeight": "1.25",
                    "color": GLOBAL_THEME["text"],
                },
            ),
            html.P(
                texto,
                style={
                    "margin": "0",
                    "fontSize": "13px",
                    "lineHeight": "1.65",
                    "color": GLOBAL_THEME["text_muted"],
                },
            ),
        ],
        className="rx-card",
        style={
            "padding": "20px 22px",
            "backgroundColor": GLOBAL_THEME["card"],
            "border": f"1px solid {GLOBAL_THEME['card_border']}",
            "borderRadius": "16px",
            "boxSizing": "border-box",
        },
    )


# ============================================================
# SECCIÓN 1 — ATENUACIÓN
# ============================================================
def seccion_atenuacion():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        "01 · ATENUACIÓN",
                        style={"fontSize": "10px", "fontWeight": "700", "letterSpacing": "1.6px", "color": GLOBAL_THEME["accent_cyan"], "marginBottom": "8px"},
                    ),
                    html.H2(
                        "¿Qué ocurre cuando los Rayos X atraviesan el cuerpo?",
                        style={"marginBottom": "10px", "color": GLOBAL_THEME["text"]},
                    ),
                    html.P(
                        "Cuando el haz de Rayos X atraviesa al paciente, no todos los fotones llegan al detector. Parte de la radiación es absorbida o desviada por los tejidos. A esta disminución de la intensidad del haz se le llama atenuación.",
                        style={"marginBottom": "0", "color": GLOBAL_THEME["text_muted"], "fontSize": "15px", "lineHeight": "1.7"},
                    ),
                ],
                style={"marginBottom": "20px"},
            ),
            _flujo(["TUBO DE RAYOS X", "HAZ DE RAYOS X", "PACIENTE", "ATENUACIÓN", "DETECTOR", "IMAGEN"]),
            html.Div(
                [
                    _tarjeta("¿De qué depende?", [html.P("El espesor del material influye directamente: cuanto mayor es el grosor atravesado, mayor es la atenuación."), html.P("También influyen la densidad, el número atómico del material y la energía del haz.")], "01"),
                    _tarjeta("¿Qué significa en la imagen?", [html.P("Los tejidos no atenúan los Rayos X de la misma forma. Por eso diferentes cantidades de radiación llegan a diferentes zonas del detector."), html.P("Esas diferencias son fundamentales para formar el contraste radiográfico.")], "02"),
                ],
                style={"display": "grid", "gridTemplateColumns": "repeat(2, minmax(0, 1fr))", "gap": "16px", "marginBottom": "24px"},
            ),
            html.Div(
                [
                    _bloque_explicativo("APOYO VISUAL", "Lee la imagen de izquierda a derecha", "El haz sale del tubo, atraviesa diferentes tejidos y llega al detector con una intensidad modificada. Esa información será utilizada para construir la imagen radiográfica."),
                    _imagen("atenuacion.png", "Esquema de atenuación de los Rayos X"),
                ],
                style={"display": "grid", "gridTemplateColumns": "minmax(0, 0.42fr) minmax(0, 0.58fr)", "gap": "16px", "alignItems": "stretch"},
            ),
        ]
    )

# ============================================================
# SECCIÓN 2 — INTERACCIONES
# ============================================================
def seccion_interacciones():
    return html.Div(
        [
            html.Div(
                [
                    html.Div("02 · INTERACCIÓN RX–MATERIA", style={"fontSize": "10px", "fontWeight": "700", "letterSpacing": "1.6px", "color": GLOBAL_THEME["accent_cyan"], "marginBottom": "8px"}),
                    html.H2("¿Cómo interactúan los Rayos X con la materia?", style={"marginBottom": "10px", "color": GLOBAL_THEME["text"]}),
                    html.P("Durante el paso por el paciente pueden ocurrir diferentes interacciones. Dos de las más importantes son el efecto fotoeléctrico y el efecto Compton.", style={"marginBottom": "0", "color": GLOBAL_THEME["text_muted"], "fontSize": "15px", "lineHeight": "1.7"}),
                ],
                style={"marginBottom": "22px"},
            ),
            html.Div(
                [
                    html.Div([
                        _tarjeta("Efecto fotoeléctrico", [html.P("El fotón de Rayos X es absorbido completamente por un átomo y expulsa un electrón de una capa interna."), html.P("El fotón desaparece y su energía se transfiere al material. Esta interacción contribuye fuertemente al contraste de la imagen.")], "01"),
                        html.Div(style={"height": "12px"}),
                        _imagen("efecto_fotoelectrico.png", "Efecto fotoeléctrico", "280px"),
                    ]),
                    html.Div([
                        _tarjeta("Efecto Compton", [html.P("El fotón interactúa con un electrón y sale desviado en otra dirección con menor energía."), html.P("El fotón dispersado puede llegar al detector desde una dirección diferente y producir radiación dispersa.")], "02"),
                        html.Div(style={"height": "12px"}),
                        _imagen("efecto_compton.png", "Efecto Compton", "280px"),
                    ]),
                ],
                style={"display": "grid", "gridTemplateColumns": "repeat(2, minmax(0, 1fr))", "gap": "18px"},
            ),
        ]
    )

# ============================================================
# SECCIÓN 3 — RADIACIÓN DISPERSA
# ============================================================
def seccion_dispersion():
    return html.Div(
        [
            html.Div(
                [
                    html.Div("03 · RADIACIÓN DISPERSA", style={"fontSize": "10px", "fontWeight": "700", "letterSpacing": "1.6px", "color": GLOBAL_THEME["accent_cyan"], "marginBottom": "8px"}),
                    html.H2("¿Qué es la radiación dispersa?", style={"marginBottom": "10px", "color": GLOBAL_THEME["text"]}),
                    html.P("No toda la radiación que sale del paciente sigue el camino original hacia el detector. Parte cambia de dirección por interacciones como el efecto Compton.", style={"marginBottom": "0", "color": GLOBAL_THEME["text_muted"], "fontSize": "15px", "lineHeight": "1.7"}),
                ],
                style={"marginBottom": "22px"},
            ),
            _flujo(["HAZ PRIMARIO", "PACIENTE", "INTERACCIÓN", "RADIACIÓN DISPERSA", "DETECTOR", "IMAGEN"]),
            html.Div(
                [
                    _tarjeta("Radiación primaria", [html.P("Es la radiación que atraviesa el paciente sin desviarse significativamente y continúa hacia el detector."), html.P("Es la principal responsable de transportar información útil para formar la imagen.")], "01"),
                    _tarjeta("Radiación dispersa", [html.P("Es la radiación que cambia de dirección después de interactuar con la materia."), html.P("Al llegar al detector desde direcciones no deseadas puede reducir el contraste y añadir señal que no representa correctamente la anatomía.")], "02"),
                ],
                style={"display": "grid", "gridTemplateColumns": "repeat(2, minmax(0, 1fr))", "gap": "16px", "marginBottom": "22px"},
            ),
            html.Div(
                [
                    _imagen("radiacion_dispersa.png", "Radiación primaria y radiación dispersa", "360px"),
                    _bloque_explicativo("¿POR QUÉ IMPORTA?", "La dispersión puede degradar la imagen", "La radiación dispersa agrega señal no deseada al detector. Esto puede disminuir el contraste radiográfico y dificultar la diferenciación entre estructuras."),
                ],
                style={"display": "grid", "gridTemplateColumns": "minmax(0, 0.62fr) minmax(0, 0.38fr)", "gap": "16px", "alignItems": "stretch"},
            ),
        ]
    )

# ============================================================
# SECCIÓN 4 — CONTRASTE
# ============================================================
def seccion_contraste():
    return html.Div(
        [
            html.Div(
                [
                    html.Div("04 · CONTRASTE RADIOGRÁFICO", style={"fontSize": "10px", "fontWeight": "700", "letterSpacing": "1.6px", "color": GLOBAL_THEME["accent_cyan"], "marginBottom": "8px"}),
                    html.H2("¿Cómo se forma el contraste?", style={"marginBottom": "10px", "color": GLOBAL_THEME["text"]}),
                    html.P("El contraste permite diferenciar unas estructuras de otras en la radiografía. Se origina porque los distintos tejidos atenúan el haz de Rayos X de manera diferente.", style={"marginBottom": "0", "color": GLOBAL_THEME["text_muted"], "fontSize": "15px", "lineHeight": "1.7"}),
                ],
                style={"marginBottom": "20px"},
            ),
            _flujo(["TEJIDOS DIFERENTES", "ATENUACIÓN DIFERENTE", "RX TRANSMITIDOS DIFERENTES", "SEÑAL DIFERENTE", "VALORES DE PÍXEL", "CONTRASTE"]),
            html.Div(
                [
                    _tarjeta("La idea física", [html.P("La densidad, el espesor y el número atómico de los tejidos influyen en cuánto se atenúa el haz."), html.P("Como resultado, no todas las zonas del detector reciben la misma cantidad de radiación.")], "01"),
                    _tarjeta("La idea en la imagen", [html.P("El detector convierte esas diferencias de radiación en diferencias de señal."), html.P("Después, esas diferencias se representan como distintos valores de píxel y tonos de gris.")], "02"),
                ],
                style={"display": "grid", "gridTemplateColumns": "repeat(2, minmax(0, 1fr))", "gap": "16px", "marginBottom": "22px"},
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("APOYO VISUAL", style={"fontSize": "10px", "fontWeight": "700", "letterSpacing": "1.5px", "color": GLOBAL_THEME["accent_cyan"], "marginBottom": "8px"}),
                            html.H3("¿Qué estamos viendo en una radiografía?", style={"margin": "0 0 14px 0", "fontSize": "22px", "lineHeight": "1.25", "color": GLOBAL_THEME["text"]}),
                            _imagen("contraste_radiografico.jpg", "Radiografía de tórax para observar el contraste radiográfico", "380px"),
                        ],
                        style={"backgroundColor": GLOBAL_THEME["card"], "border": f"1px solid {GLOBAL_THEME['card_border']}", "borderRadius": "16px", "padding": "22px", "boxSizing": "border-box"},
                    ),
                ],
                style={"marginTop": "22px"},
            ),
        ]
    )

# ============================================================
# SECCIÓN 5 — DETECTORES
# ============================================================
def seccion_detectores():
    return html.Div(
        [
            html.Div(
                [
                    html.Div("05 · DETECTORES", style={"fontSize": "10px", "fontWeight": "700", "letterSpacing": "1.6px", "color": GLOBAL_THEME["accent_cyan"], "marginBottom": "8px"}),
                    html.H2("¿Cómo se convierte la radiación en una señal?", style={"marginBottom": "10px", "color": GLOBAL_THEME["text"]}),
                    html.P("El detector recibe los Rayos X que atravesaron al paciente y los transforma en una señal que posteriormente puede convertirse en una imagen.", style={"marginBottom": "24px", "color": GLOBAL_THEME["text_muted"], "fontSize": "15px", "lineHeight": "1.7"}),
                ],
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H3("Tipos de detectores", style={"margin": "0 0 8px 0", "fontSize": "24px", "lineHeight": "1.2", "color": GLOBAL_THEME["text"]}),
                            _imagen("detectores.png", "Tipos de detectores de Rayos X", "300px"),
                        ],
                        style={"backgroundColor": GLOBAL_THEME["card"], "border": f"1px solid {GLOBAL_THEME['card_border']}", "borderRadius": "16px", "padding": "22px", "boxSizing": "border-box"},
                    ),
                ],
                style={"marginBottom": "18px"},
            ),
        ]
    )

# ============================================================
# SECCIÓN 6 — RADIOGRAFÍA DIGITAL
# ============================================================
def seccion_radiografia_digital():
    return html.Div(
        [
            html.Div(
                [
                    html.Div("06 · RADIOGRAFÍA DIGITAL", style={"fontSize": "10px", "fontWeight": "700", "letterSpacing": "1.6px", "color": GLOBAL_THEME["accent_cyan"], "marginBottom": "8px"}),
                    html.H2("¿Cómo se transforma la señal en una imagen digital?", style={"marginBottom": "10px", "color": GLOBAL_THEME["text"]}),
                    html.P("Después de recibir los Rayos X, el detector genera una señal que es procesada y convertida en datos digitales. Estos datos se organizan para construir la imagen radiográfica.", style={"marginBottom": "24px", "color": GLOBAL_THEME["text_muted"], "fontSize": "15px", "lineHeight": "1.7"}),
                ],
            ),
            _flujo(["RAYOS X", "DETECTOR", "SEÑAL", "CONVERSIÓN A/D", "DATOS DIGITALES", "MATRIZ DE PÍXELES", "IMAGEN"], altura="72px"),
        ]
    )

# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================
def mostrar_formacion():
    return html.Div(
        [
            # HERO
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("FORMACIÓN · RADIOLOGÍA", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "2px", "color": GLOBAL_THEME["accent_cyan"], "marginBottom": "14px"}),
                            html.H1("Formación de la Imagen Radiográfica", style={"margin": "0", "fontSize": "42px", "lineHeight": "1.1", "fontWeight": "700", "color": GLOBAL_THEME["text"]}),
                            html.P("Comprende cómo los Rayos X atraviesan el cuerpo, interactúan con los tejidos y se convierten en una imagen médica.", style={"margin": "16px 0 0 0", "maxWidth": "760px", "fontSize": "15px", "lineHeight": "1.7", "color": GLOBAL_THEME["text_muted"]}),
                            html.Div(style={"width": "70px", "height": "3px", "backgroundColor": GLOBAL_THEME["accent_cyan"], "borderRadius": "3px", "marginTop": "24px"}),
                        ],
                        style={"position": "relative", "zIndex": "2"},
                    ),
                    html.Img(src="/assets/formacion/manitos1.svg", style={"position": "absolute", "right": "55px", "top": "50%", "transform": "translateY(-50%)", "width": "180px", "height": "auto", "pointerEvents": "none"}),
                ],
                className="rx-hero-card",
                style={
                    "position": "relative", "overflow": "hidden",
                    "background": "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
                    "border": f"1px solid {GLOBAL_THEME['card_border']}", "borderRadius": "18px",
                    "padding": "42px 46px", "marginBottom": "28px", "minHeight": "220px",
                    "boxSizing": "border-box", "display": "flex", "alignItems": "center",
                    "boxShadow": "0 12px 30px rgba(0, 0, 0, 0.18)",
                },
            ),
            
            # PESTAÑAS
            dcc.Tabs(
                id="formacion-tabs",
                value="atenuacion",
                style={"borderBottom": "1px solid #334155", "marginBottom": "20px"},
                children=[
                    dcc.Tab(label="Atenuación", value="atenuacion", style={"backgroundColor": "#1e293b", "border": "1px solid #334155", "color": "#94a3b8", "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px"}, selected_style={"backgroundColor": "#38bdf8", "border": "1px solid #38bdf8", "color": "#0f172a", "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px", "fontWeight": "bold"}, children=seccion_atenuacion()),
                    dcc.Tab(label="Interacciones", value="interacciones", style={"backgroundColor": "#1e293b", "border": "1px solid #334155", "color": "#94a3b8", "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px"}, selected_style={"backgroundColor": "#38bdf8", "border": "1px solid #38bdf8", "color": "#0f172a", "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px", "fontWeight": "bold"}, children=seccion_interacciones()),
                    dcc.Tab(label="Dispersión", value="dispersion", style={"backgroundColor": "#1e293b", "border": "1px solid #334155", "color": "#94a3b8", "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px"}, selected_style={"backgroundColor": "#38bdf8", "border": "1px solid #38bdf8", "color": "#0f172a", "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px", "fontWeight": "bold"}, children=seccion_dispersion()),
                    dcc.Tab(label="Contraste", value="contraste", style={"backgroundColor": "#1e293b", "border": "1px solid #334155", "color": "#94a3b8", "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px"}, selected_style={"backgroundColor": "#38bdf8", "border": "1px solid #38bdf8", "color": "#0f172a", "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px", "fontWeight": "bold"}, children=seccion_contraste()),
                    dcc.Tab(label="Detectores", value="detectores", style={"backgroundColor": "#1e293b", "border": "1px solid #334155", "color": "#94a3b8", "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px"}, selected_style={"backgroundColor": "#38bdf8", "border": "1px solid #38bdf8", "color": "#0f172a", "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px", "fontWeight": "bold"}, children=seccion_detectores()),
                    dcc.Tab(label="Radiografía digital", value="digital", style={"backgroundColor": "#1e293b", "border": "1px solid #334155", "color": "#94a3b8", "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px"}, selected_style={"backgroundColor": "#38bdf8", "border": "1px solid #38bdf8", "color": "#0f172a", "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px", "fontWeight": "bold"}, children=seccion_radiografia_digital()),
                ],
            ),
        ]
    )