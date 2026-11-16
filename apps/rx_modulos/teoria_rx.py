"""
Módulo de Teoría y Física de Rayos X
Proyecto_RX - Integrante 2

Función pública:
    mostrar_teoria()

Secciones:
    1. Fundamentos de Rayos X
    2. Producción de Rayos X
    3. Tubo de Rayos X
    4. Parámetros
    5. Filtración
    6. Colimación
"""

from dash import html, dcc, Input, Output
from config import THEME as GLOBAL_THEME

# Paleta adaptada a Prometeo para el Módulo de Teoría
# Todos los colores se toman del tema global para mantener la armonía.

# ============================================================
# UTILIDADES DE DISEÑO
# ============================================================

def _tarjeta(titulo, contenido, icono=None):
    if icono is None:
        icon_elem = html.I(className="fa-solid fa-book-bookmark")
    elif isinstance(icono, str):
        icon_elem = html.I(className=icono) if icono.startswith("fa-") else html.Span(icono)
    else:
        icon_elem = icono
    return html.Div(
        [
            html.Div(
                [
                    html.Span(
                        icon_elem,
                        style={
                            "fontSize": "22px",
                            "marginRight": "12px",
                            "color": GLOBAL_THEME["accent_cyan"]
                        }
                    ),
                    html.H3(
                        titulo,
                        style={
                            "margin": "0",
                            "fontSize": "21px",
                            "lineHeight": "1.2",
                            "fontWeight": "700",
                            "color": GLOBAL_THEME["accent_cyan"]
                        }
                    ),
                ],
                style={"display": "flex", "alignItems": "center", "marginBottom": "16px"},
            ),
            html.Div(
                contenido,
                style={
                    "color": GLOBAL_THEME["text_muted"],
                    "fontSize": "14px",
                    "lineHeight": "1.7",
                }
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


def _imagen(nombre, alt):
    return html.Div(
        [
            html.Img(
                src=f"/assets/teoria/{nombre}",
                alt=alt,
                style={
                    "display": "block",
                    "width": "100%",
                    "maxWidth": "100%",
                    "height": "auto",
                    "maxHeight": "330px",
                    "objectFit": "contain",
                    "borderRadius": "12px",
                },
            )
        ],
        className="teoria-imagen",
        style={
            "width": "100%",
            "maxWidth": "100%",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "overflow": "hidden",
            "backgroundColor": GLOBAL_THEME["bg"],
            "border": f"1px solid {GLOBAL_THEME['card_border']}",
            "borderRadius": "14px",
            "padding": "10px",
            "boxSizing": "border-box",
        },
    )

def _flujo(pasos):
    """
    Flujo horizontal con estilos INLINE.
    """
    elementos = []

    for i, paso in enumerate(pasos):
        elementos.append(
            html.Div(
                paso,
                className="rx-flow-step",
                style={
                    "flex": "1 1 0",
                    "minWidth": "0",
                    "width": "auto",
                    "height": "58px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "padding": "6px 4px",
                    "boxSizing": "border-box",
                    "backgroundColor": GLOBAL_THEME["card_border"],
                    "color": GLOBAL_THEME["text"],
                    "border": f"1px solid {GLOBAL_THEME['card_border']}",
                    "borderRadius": "11px",
                    "fontFamily": "'Lora', Georgia, serif",
                    "fontSize": "10px",
                    "fontWeight": "700",
                    "lineHeight": "1.15",
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
                        "flex": "0 0 22px",
                        "width": "22px",
                        "minWidth": "22px",
                        "height": "58px",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "boxSizing": "border-box",
                        "color": GLOBAL_THEME["text_muted"],
                        "fontFamily": "'Lora', Georgia, serif",
                        "fontSize": "18px",
                        "fontWeight": "700",
                        "lineHeight": "1",
                        "textAlign": "center",
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
            "maxWidth": "100%",
            "minWidth": "0",
            "height": "92px",
            "gap": "5px",
            "padding": "16px 10px",
            "margin": "24px 0 30px 0",
            "boxSizing": "border-box",
            "overflow": "hidden",
            "backgroundColor": GLOBAL_THEME["bg"],
            "border": f"1px solid {GLOBAL_THEME['card_border']}",
            "borderRadius": "18px",
        },
    )


# ============================================================
# SECCIÓN 1 — FUNDAMENTOS
# ============================================================

def seccion_fundamentos():
    return html.Div(
        [
            # ENCABEZADO
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                "CONCEPTO ESENCIAL",
                                style={
                                    "fontSize": "11px",
                                    "fontWeight": "700",
                                    "letterSpacing": "1.8px",
                                    "color": GLOBAL_THEME["accent_cyan"],
                                    "marginBottom": "8px",
                                },
                            ),
                            html.H2(
                                "¿Qué son los Rayos X?",
                                className="teoria-section-title",
                                style={"marginBottom": "10px"},
                            ),
                            html.P(
                                "Los Rayos X son una forma de radiación "
                                "electromagnética. Son ondas de energía "
                                "electromagnética de alta energía y forman "
                                "parte de la radiación ionizante.",
                                className="teoria-intro",
                                style={
                                    "marginBottom": "0",
                                    "maxWidth": "820px",
                                },
                            ),
                        ],
                    ),
                ],
                style={"marginBottom": "22px"},
            ),

            # BLOQUE VISUAL PRINCIPAL
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                "01 · UNA VENTANA AL INTERIOR DEL CUERPO",
                                style={
                                    "fontSize": "10px",
                                    "fontWeight": "700",
                                    "letterSpacing": "1.4px",
                                    "color": GLOBAL_THEME["accent_cyan"],
                                    "marginBottom": "12px",
                                },
                            ),
                            html.H3(
                                "La radiografía permite ver lo que el ojo no puede.",
                                style={
                                    "margin": "0 0 14px 0",
                                    "fontSize": "25px",
                                    "lineHeight": "1.25",
                                    "fontWeight": "700",
                                    "color": GLOBAL_THEME["text"],
                                },
                            ),
                            html.P(
                                "La imagen radiográfica se forma porque los "
                                "tejidos del cuerpo atenúan los Rayos X de "
                                "manera diferente al atravesarlos.",
                                style={
                                    "margin": "0 0 18px 0",
                                    "fontSize": "14px",
                                    "lineHeight": "1.7",
                                    "color": GLOBAL_THEME["text_muted"],
                                },
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        "RADIOGRAFÍA",
                                        style={
                                            "fontSize": "10px",
                                            "fontWeight": "700",
                                            "letterSpacing": "1px",
                                            "color": GLOBAL_THEME["bg"],
                                            "backgroundColor": GLOBAL_THEME["accent_cyan"],
                                            "padding": "7px 10px",
                                            "borderRadius": "999px",
                                        },
                                    ),
                                    html.Span(
                                        "Atenuación → contraste → imagen",
                                        style={
                                            "fontSize": "12px",
                                            "color": GLOBAL_THEME["text_muted"],
                                            "marginLeft": "10px",
                                        },
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "alignItems": "center",
                                    "flexWrap": "wrap",
                                    "gap": "4px",
                                },
                            ),
                        ],
                        style={
                            "flex": "1 1 48%",
                            "minWidth": "280px",
                            "padding": "28px 30px",
                            "boxSizing": "border-box",
                        },
                    ),
                    html.Div(
                        [
                            _imagen(
                                "rayos_x_intro.jpg",
                                "Imagen introductoria sobre Rayos X y radiografía",
                            )
                        ],
                        style={
                            "flex": "1 1 42%",
                            "minWidth": "280px",
                            "padding": "18px",
                            "boxSizing": "border-box",
                        },
                    ),
                ],
                className="rx-hero-card",
                style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "alignItems": "center",
                    "gap": "8px",
                    "background": f"linear-gradient(135deg, {GLOBAL_THEME['card']} 0%, {GLOBAL_THEME['bg']} 100%)",
                    "border": f"1px solid {GLOBAL_THEME['card_border']}",
                    "borderRadius": "18px",
                    "overflow": "hidden",
                    "marginBottom": "30px",
                    "boxShadow": "0 10px 24px rgba(0,0,0,0.4)",
                },
            ),

            # CONCEPTOS CLAVE
            html.Div(
                [
                    html.Div(
                        [
                            html.H3(
                                "Conceptos clave",
                                style={
                                    "margin": "0",
                                    "fontSize": "21px",
                                    "color": GLOBAL_THEME["text"],
                                },
                            ),
                            html.P(
                                "Las cuatro ideas que debes dominar antes de avanzar.",
                                style={
                                    "margin": "5px 0 0 0",
                                    "fontSize": "13px",
                                    "color": GLOBAL_THEME["text_muted"],
                                },
                            ),
                        ],
                        style={"marginBottom": "16px"},
                    ),
                    html.Div(
                        [
                            _tarjeta(
                                "Naturaleza",
                                [
                                    html.P("Los Rayos X son ondas electromagnéticas de alta frecuencia."),
                                    html.P("No tienen masa ni carga eléctrica; son energía."),
                                ],
                                "01",
                            ),
                            _tarjeta(
                                "Características",
                                [
                                    html.P("Presentan longitudes de onda muy cortas y frecuencias mayores que las de la luz visible."),
                                    html.P("El material de las diapositivas indica un rango aproximado de 0,01 a 10 nm."),
                                ],
                                "02",
                            ),
                            _tarjeta(
                                "Radiación ionizante",
                                [
                                    html.P("La ionización es la expulsión de un electrón de un átomo, creando un electrón libre y un ion."),
                                    html.P("Los Rayos X transportan suficiente energía para producir ionización."),
                                ],
                                "03",
                            ),
                            _tarjeta(
                                "Aplicaciones médicas",
                                [
                                    html.P("Se utilizan para obtener imágenes del interior del cuerpo."),
                                    html.P("Entre las aplicaciones están la radiografía de proyección y la tomografía computarizada (TC)."),
                                ],
                                "04",
                            ),
                        ],
                        className="teoria-grid",
                    ),
                ],
                style={"marginBottom": "30px"},
            ),

            # APOYO VISUAL (ESPECTRO E IONIZACIÓN)
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                "02 · UBICACIÓN EN EL ESPECTRO",
                                style={
                                    "fontSize": "10px",
                                    "fontWeight": "700",
                                    "letterSpacing": "1.3px",
                                    "color": GLOBAL_THEME["accent_cyan"],
                                    "marginBottom": "8px",
                                },
                            ),
                            html.H3(
                                "¿Dónde se encuentran los Rayos X?",
                                style={
                                    "margin": "0 0 10px 0",
                                    "fontSize": "20px",
                                    "color": GLOBAL_THEME["text"],
                                },
                            ),
                            html.P(
                                "Los Rayos X forman parte del espectro electromagnético. "
                                "Se encuentran entre la radiación ultravioleta y los rayos gamma, "
                                "en una región de longitudes de onda muy cortas y frecuencias elevadas.",
                                style={
                                    "margin": "0 0 14px 0",
                                    "fontSize": "13px",
                                    "lineHeight": "1.65",
                                    "color": GLOBAL_THEME["text_muted"],
                                },
                            ),
                            _imagen(
                                "espectro_electromagnetico.jpg",
                                "Espectro electromagnético y región de Rayos X",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "01",
                                                style={
                                                    "fontWeight": "800",
                                                    "color": GLOBAL_THEME["bg"],
                                                    "backgroundColor": GLOBAL_THEME["accent_cyan"],
                                                    "borderRadius": "8px",
                                                    "padding": "5px 8px",
                                                    "fontSize": "10px",
                                                },
                                            ),
                                            html.Span(
                                                "Mayor frecuencia → mayor energía",
                                                style={
                                                    "fontWeight": "700",
                                                    "color": GLOBAL_THEME["text"],
                                                    "fontSize": "12px",
                                                },
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                            "gap": "9px",
                                            "marginBottom": "7px",
                                        },
                                    ),
                                    html.P(
                                        "En el espectro, al disminuir la longitud de onda "
                                        "aumentan la frecuencia y la energía de la radiación.",
                                        style={
                                            "margin": "0",
                                            "fontSize": "12px",
                                            "lineHeight": "1.55",
                                            "color": GLOBAL_THEME["text_muted"],
                                        },
                                    ),
                                ],
                                style={
                                    "marginTop": "12px",
                                    "padding": "12px 13px",
                                    "backgroundColor": GLOBAL_THEME["bg"],
                                    "borderRadius": "11px",
                                    "border": f"1px solid {GLOBAL_THEME['card_border']}",
                                },
                            ),
                        ],
                        style={
                            "flex": "1 1 52%",
                            "minWidth": "300px",
                            "padding": "22px",
                            "boxSizing": "border-box",
                            "backgroundColor": GLOBAL_THEME["card"],
                            "border": f"1px solid {GLOBAL_THEME['card_border']}",
                            "borderRadius": "16px",
                        },
                    ),
                    html.Div(
                        [
                            html.Div(
                                "03 · IONIZACIÓN",
                                style={
                                    "fontSize": "10px",
                                    "fontWeight": "700",
                                    "letterSpacing": "1.3px",
                                    "color": GLOBAL_THEME["accent_cyan"],
                                    "marginBottom": "8px",
                                },
                            ),
                            html.H3(
                                "¿Por qué son ionizantes?",
                                style={
                                    "margin": "0 0 10px 0",
                                    "fontSize": "20px",
                                    "color": GLOBAL_THEME["text"],
                                },
                            ),
                            html.P(
                                "Una radiación es ionizante cuando tiene suficiente energía "
                                "para arrancar un electrón de un átomo. En este proceso se "
                                "forma un electrón libre y el átomo que perdió el electrón queda ionizado.",
                                style={
                                    "margin": "0 0 14px 0",
                                    "fontSize": "13px",
                                    "lineHeight": "1.65",
                                    "color": GLOBAL_THEME["text_muted"],
                                },
                            ),
                            _imagen(
                                "radiacion_ionizante.jpg",
                                "Representación de la radiación ionizante",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "02",
                                                style={
                                                    "fontWeight": "800",
                                                    "color": GLOBAL_THEME["bg"],
                                                    "backgroundColor": GLOBAL_THEME["accent_cyan"],
                                                    "borderRadius": "8px",
                                                    "padding": "5px 8px",
                                                    "fontSize": "10px",
                                                },
                                            ),
                                            html.Span(
                                                "Fotón de Rayos X → átomo → ionización",
                                                style={
                                                    "fontWeight": "700",
                                                    "color": GLOBAL_THEME["text"],
                                                    "fontSize": "12px",
                                                },
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                            "gap": "9px",
                                            "marginBottom": "7px",
                                        },
                                    ),
                                    html.P(
                                        "El fotón transfiere energía al átomo y puede expulsar "
                                        "un electrón. Por eso los Rayos X deben utilizarse con protección radiológica.",
                                        style={
                                            "margin": "0",
                                            "fontSize": "12px",
                                            "lineHeight": "1.55",
                                            "color": GLOBAL_THEME["text_muted"],
                                        },
                                    ),
                                ],
                                style={
                                    "marginTop": "12px",
                                    "padding": "12px 13px",
                                    "backgroundColor": GLOBAL_THEME["bg"],
                                    "borderRadius": "11px",
                                    "border": f"1px solid {GLOBAL_THEME['card_border']}",
                                },
                            ),
                        ],
                        style={
                            "flex": "1 1 42%",
                            "minWidth": "280px",
                            "padding": "22px",
                            "boxSizing": "border-box",
                            "backgroundColor": GLOBAL_THEME["card"],
                            "border": f"1px solid {GLOBAL_THEME['card_border']}",
                            "borderRadius": "16px",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "gap": "16px",
                    "marginBottom": "30px",
                },
            ),

            # DATOS RÁPIDOS
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("0,01–10 nm", className="teoria-indicator-value"),
                            html.Span("longitud de onda aproximada", className="teoria-indicator-label"),
                        ],
                        className="teoria-indicator",
                    ),
                    html.Div(
                        [
                            html.Span("3 × 10¹⁶–3 × 10¹⁹ Hz", className="teoria-indicator-value"),
                            html.Span("frecuencia aproximada", className="teoria-indicator-label"),
                        ],
                        className="teoria-indicator",
                    ),
                    html.Div(
                        [
                            html.Span("100 eV–100 keV", className="teoria-indicator-value"),
                            html.Span("rango de energía indicado", className="teoria-indicator-label"),
                        ],
                        className="teoria-indicator",
                    ),
                ],
                className="teoria-indicators",
            ),
        ],
        className="teoria-section",
        style={"paddingBottom": "20px"},
    )


# ============================================================
# SECCIÓN 2 — PRODUCCIÓN DE RAYOS X
# ============================================================

def seccion_produccion():
    return html.Div(
        [
            html.H2([html.I(className="fa-solid fa-bolt", style={"marginRight": "10px"}), "Producción de Rayos X"], className="teoria-section-title"),
            html.P(
                "El tubo de Rayos X produce radiación al acelerar electrones "
                "desde el cátodo hacia el ánodo mediante una diferencia de "
                "potencial elevada. Al llegar al objetivo, los electrones "
                "transfieren energía y se producen Rayos X.",
                className="teoria-intro",
            ),
            _flujo(
                [
                    "Cátodo ",
                    "Emisión de electrones",
                    "Aceleración",
                    "Ánodo",
                    "Interacción con el blanco",
                    "Producción de Rayos X",
                ]
            ),
            html.Div(
                [
                    _tarjeta("Cátodo", [html.P("Es el terminal negativo del tubo."), html.P("Contiene un filamento de tungsteno. Cuando circula corriente, el filamento se calienta y libera electrones mediante emisión termoiónica.")], "fa-solid fa-minus"),
                    _tarjeta("Ánodo y blanco", [html.P("El ánodo es el terminal positivo."), html.P("Los electrones acelerados chocan con el objetivo o blanco del ánodo.")], "fa-solid fa-plus"),
                    _tarjeta("Bremsstrahlung", [html.P("Se produce cuando un electrón energético interactúa con el núcleo y se desacelera."), html.P("La pérdida de energía cinética se transforma en un fotón de Rayos X.")], "fa-solid fa-burst"),
                    _tarjeta("Radiación característica", [html.P("Se produce cuando un electrón incidente expulsa un electrón de una capa interna del átomo."), html.P("Cuando otro electrón ocupa la vacante, se emite un fotón con una energía característica.")], "fa-solid fa-atom"),
                ],
                className="teoria-grid",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H3("¿Qué ocurre dentro del tubo?", style={"margin": "0 0 9px 0", "fontSize": "20px", "color": GLOBAL_THEME["text"]}),
                            html.P("El esquema resume el recorrido de los electrones: se liberan en el cátodo, se aceleran por la diferencia de potencial y llegan al blanco del ánodo. Allí su interacción con el material transforma parte de su energía en radiación de Rayos X.", style={"margin": "0", "fontSize": "13px", "lineHeight": "1.65", "color": GLOBAL_THEME["text_muted"]}),
                        ],
                        style={"padding": "15px 17px", "marginBottom": "12px", "backgroundColor": GLOBAL_THEME["card"], "border": f"1px solid {GLOBAL_THEME['card_border']}", "borderRadius": "12px"},
                    ),
                    _imagen("produccion_rx.jpg", "Producción de Rayos X"),
                    html.P("En la imagen, identifica el sentido del movimiento de los electrones y relaciona cada etapa con el proceso descrito en las tarjetas anteriores.", style={"margin": "10px 4px 0 4px", "fontSize": "12px", "lineHeight": "1.55", "textAlign": "center", "color": GLOBAL_THEME["text_muted"]}),
                ],
                className="teoria-image-single",
            ),
            html.Div(
                [
                    html.Div([html.Span("Bremsstrahlung", className="teoria-formula-symbol"), html.Span("→", className="teoria-formula-arrow"), html.Span("espectro continuo", className="teoria-formula-text")], className="teoria-formula-card"),
                    html.Div([html.Span("Característica", className="teoria-formula-symbol"), html.Span("→", className="teoria-formula-arrow"), html.Span("energías específicas", className="teoria-formula-text")], className="teoria-formula-card"),
                ],
                className="teoria-formulas",
            ),
        ],
        className="teoria-section",
    )


# ============================================================
# SECCIÓN 3 — TUBO DE RAYOS X
# ============================================================

def seccion_tubo():
    return html.Div(
        [
            html.H2([html.I(className="fa-solid fa-microscope", style={"marginRight": "10px"}), "Tubo de Rayos X"], className="teoria-section-title"),
            html.P("El tubo de Rayos X contiene los elementos necesarios para producir radiación mediante la aceleración de electrones desde el cátodo hacia el ánodo.", className="teoria-intro"),
            html.Div(
                [
                    _tarjeta("Cátodo", [html.P("Es el electrodo negativo."), html.P("Contiene el filamento que libera electrones por emisión termoiónica.")], "fa-solid fa-minus"),
                    _tarjeta("Ánodo", [html.P("Es el electrodo positivo."), html.P("Recibe los electrones acelerados y contiene el blanco donde se producen los Rayos X.")], "fa-solid fa-plus"),
                    _tarjeta("Blanco", [html.P("Es la zona del ánodo donde impactan los electrones."), html.P("La interacción produce Rayos X y una gran cantidad de calor.")], "fa-solid fa-bullseye"),
                    _tarjeta("Vacío", [html.P("El interior del tubo se mantiene al vacío."), html.P("Esto permite que los electrones se desplacen desde el cátodo hacia el ánodo sin colisiones con moléculas de aire.")], "⭕"),
                    _tarjeta("Ventana", [html.P("Es la zona por donde sale el haz útil de Rayos X."), html.P("Permite la salida de la radiación producida en el interior del tubo.")], "fa-solid fa-table-cells-large"),
                    _tarjeta("Ánodo rotatorio", [html.P("El ánodo gira para evitar que el área objetivo se sobrecaliente."), html.P("El material indica aproximadamente 3200–3600 rpm para muchos tubos.")], "fa-solid fa-arrows-rotate"),
                ],
                className="teoria-grid",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H3("¿Cómo leer el esquema del tubo?", style={"margin": "0 0 9px 0", "fontSize": "20px", "color": GLOBAL_THEME["text"]}),
                            html.P("El dibujo permite ubicar los componentes que participan en la producción del haz. El cátodo contiene el filamento; el ánodo incorpora el disco o blanco; el vacío facilita el desplazamiento de los electrones y la ventana permite la salida del haz útil.", style={"margin": "0", "fontSize": "13px", "lineHeight": "1.65", "color": GLOBAL_THEME["text_muted"]}),
                        ],
                        style={"padding": "15px 17px", "marginBottom": "12px", "backgroundColor": GLOBAL_THEME["card"], "border": f"1px solid {GLOBAL_THEME['card_border']}", "borderRadius": "12px"},
                    ),
                    _imagen("tubo_rx.jpg", "Esquema del tubo de Rayos X"),
                    html.Div(
                        [
                            html.Div("CÁTODO", style={"fontWeight": "800", "color": GLOBAL_THEME["accent_cyan"], "fontSize": "11px"}),
                            html.P("Filamento → emisión termoiónica de electrones.", style={"margin": "4px 0 0 0", "fontSize": "12px", "color": GLOBAL_THEME["text_muted"]}),
                            html.Div("ÁNODO", style={"marginTop": "9px", "fontWeight": "800", "color": GLOBAL_THEME["accent_cyan"], "fontSize": "11px"}),
                            html.P("Blanco → interacción de los electrones y producción de Rayos X.", style={"margin": "4px 0 0 0", "fontSize": "12px", "color": GLOBAL_THEME["text_muted"]}),
                        ],
                        style={"marginTop": "12px", "padding": "12px 14px", "backgroundColor": GLOBAL_THEME["bg"], "border": f"1px solid {GLOBAL_THEME['card_border']}", "borderRadius": "11px"},
                    ),
                ],
                className="teoria-image-single",
            ),
            html.Div(
                [
                    html.Div([html.Span("≈ 1 %", className="teoria-indicator-value"), html.Span("de la energía depositada se convierte en Rayos X", className="teoria-indicator-label")], className="teoria-indicator"),
                    html.Div([html.Span("≈ 99 %", className="teoria-indicator-value"), html.Span("se convierte en calor", className="teoria-indicator-label")], className="teoria-indicator"),
                ],
                className="teoria-indicators",
            ),
        ],
        className="teoria-section",
    )


# ============================================================
# SECCIÓN 4 — PARÁMETROS
# ============================================================

def seccion_parametros():
    return html.Div(
        [
            html.H2([html.I(className="fa-solid fa-sliders", style={"marginRight": "10px"}), "Parámetros de exposición"], className="teoria-section-title"),
            html.P("Los parámetros contemplados para esta sección son kVp, mA, tiempo y mAs. Controlan las condiciones de funcionamiento del tubo y la exposición.", className="teoria-intro"),
            html.Div(
                [
                    _tarjeta("kVp — Kilovoltaje pico", [html.P("Es el kilovoltaje pico aplicado entre el ánodo y el cátodo."), html.P("El voltaje del tubo determina la energía máxima de los fotones de Rayos X."), html.P("Ejemplo indicado en las diapositivas: 100 kVp → energía máxima de 100 keV.")], "fa-solid fa-bolt"),
                    _tarjeta("mA — Corriente del tubo", [html.P("La corriente del tubo se expresa en mA."), html.P("La corriente del filamento controla la corriente del tubo al controlar el número de electrones liberados.")], "fa-solid fa-battery-half"),
                    _tarjeta("Tiempo", [html.P("La exposición global depende de la duración durante la cual se aplica el voltaje del tubo."), html.P("El tiempo puede ser controlado mediante un temporizador o un control automático de exposición (AEC).")], "⏱️"),
                    _tarjeta("mAs", [html.P("Representa la combinación de corriente del tubo y tiempo de exposición."), html.P("Se calcula mediante la relación:"), html.P("mAs = mA × s")], "fa-solid fa-ruler-combined"),
                ],
                className="teoria-grid",
            ),
            html.Div(
                [
                    html.Div([html.Span("kVp", className="teoria-formula-symbol"), html.Span("→", className="teoria-formula-arrow"), html.Span("energía máxima del fotón", className="teoria-formula-text")], className="teoria-formula-card"),
                    html.Div([html.Span("mA", className="teoria-formula-symbol"), html.Span("×", className="teoria-formula-arrow"), html.Span("s", className="teoria-formula-symbol"), html.Span("=", className="teoria-formula-arrow"), html.Span("mAs", className="teoria-formula-symbol")], className="teoria-formula-card"),
                ],
                className="teoria-formulas",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H3([html.I(className="fa-solid fa-lightbulb", style={"marginRight": "10px"}), "Ejemplo interactivo"], style={"margin": "0 0 10px 0", "fontSize": "24px", "fontWeight": "800", "color": GLOBAL_THEME["text"]}),
                            html.P("Modifica los valores para observar cómo cambia el producto corriente × tiempo.", style={"margin": "0", "fontSize": "15px", "lineHeight": "1.6", "color": GLOBAL_THEME["text_muted"]}),
                        ],
                        style={"marginBottom": "22px"},
                    ),
                    html.Div(
                        [
                            # CORRIENTE
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Div("Corriente (mA)", style={"fontSize": "18px", "fontWeight": "700", "color": GLOBAL_THEME["text"]}),
                                                    html.Div("Rango típico en radiografía: 50 – 400 mA", style={"fontSize": "12px", "color": GLOBAL_THEME["text_muted"], "marginTop": "5px"}),
                                                ],
                                                style={"flex": "1"},
                                            ),
                                            html.Div(
                                                [
                                                    html.Span("100", id="teoria-ma-output", style={"display": "flex", "alignItems": "center", "justifyContent": "center", "minWidth": "78px", "height": "58px", "padding": "0 10px", "boxSizing": "border-box", "backgroundColor": GLOBAL_THEME["bg"], "color": GLOBAL_THEME["accent_cyan"], "border": f"1px solid {GLOBAL_THEME['accent_cyan']}", "borderRadius": "9px", "fontSize": "22px", "fontWeight": "800"}),
                                                ],
                                                style={"marginLeft": "15px"},
                                            ),
                                        ],
                                        style={"display": "flex", "alignItems": "center", "marginBottom": "13px"},
                                    ),
                                    dcc.Slider(
                                        id="teoria-ma-slider",
                                        min=50,
                                        max=400,
                                        step=10,
                                        value=100,
                                        marks={v: {"label": str(v), "style": {"color": GLOBAL_THEME["text_muted"], "fontWeight": "600"}} for v in [50, 100, 200, 300, 400]},
                                    ),
                                    html.Div("mA", style={"marginTop": "10px", "textAlign": "right", "fontSize": "12px", "fontWeight": "700", "color": GLOBAL_THEME["text_muted"]}),
                                ],
                                style={"flex": "1", "minWidth": "0", "padding": "20px 18px 15px 18px", "backgroundColor": GLOBAL_THEME["card"], "border": f"1px solid {GLOBAL_THEME['card_border']}", "borderRadius": "14px", "boxSizing": "border-box"},
                            ),
                            # TIEMPO
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Div("Tiempo (s)", style={"fontSize": "18px", "fontWeight": "700", "color": GLOBAL_THEME["text"]}),
                                                    html.Div("Rango típico en radiografía: 0.01 – 2 s", style={"fontSize": "12px", "color": GLOBAL_THEME["text_muted"], "marginTop": "5px"}),
                                                ],
                                                style={"flex": "1"},
                                            ),
                                            html.Div(
                                                [
                                                    html.Span("0.1", id="teoria-tiempo-output", style={"display": "flex", "alignItems": "center", "justifyContent": "center", "minWidth": "78px", "height": "58px", "padding": "0 10px", "boxSizing": "border-box", "backgroundColor": GLOBAL_THEME["bg"], "color": GLOBAL_THEME["accent_cyan"], "border": f"1px solid {GLOBAL_THEME['accent_cyan']}", "borderRadius": "9px", "fontSize": "22px", "fontWeight": "800"}),
                                                ],
                                                style={"marginLeft": "15px"},
                                            ),
                                        ],
                                        style={"display": "flex", "alignItems": "center", "marginBottom": "13px"},
                                    ),
                                    dcc.Slider(
                                        id="teoria-tiempo-slider",
                                        min=0.01,
                                        max=2,
                                        step=0.01,
                                        value=0.1,
                                        marks={v: {"label": str(v), "style": {"color": GLOBAL_THEME["text_muted"], "fontWeight": "600"}} for v in [0.01, 0.5, 1, 2]},
                                    ),
                                    html.Div("s", style={"marginTop": "10px", "textAlign": "right", "fontSize": "12px", "fontWeight": "700", "color": GLOBAL_THEME["text_muted"]}),
                                ],
                                style={"flex": "1", "minWidth": "0", "padding": "20px 18px 15px 18px", "backgroundColor": GLOBAL_THEME["card"], "border": f"1px solid {GLOBAL_THEME['card_border']}", "borderRadius": "14px", "boxSizing": "border-box"},
                            ),
                        ],
                        style={"display": "flex", "gap": "20px", "width": "100%", "marginBottom": "22px"},
                    ),
                    # RESULTADO
                    html.Div(
                        [
                            html.Span("mAs = ", style={"fontSize": "25px", "fontWeight": "700", "color": GLOBAL_THEME["text_muted"]}),
                            html.Span("10.00", id="teoria-mas-output", style={"fontSize": "32px", "fontWeight": "900", "color": GLOBAL_THEME["accent_cyan"]}),
                        ],
                        style={"width": "100%", "minHeight": "94px", "display": "flex", "alignItems": "center", "justifyContent": "center", "boxSizing": "border-box", "backgroundColor": GLOBAL_THEME["bg"], "border": f"1px solid {GLOBAL_THEME['accent_cyan']}", "borderRadius": "14px"},
                    ),
                ],
                className="teoria-interactive",
                style={"width": "100%", "maxWidth": "100%", "padding": "28px 28px 26px 28px", "boxSizing": "border-box", "backgroundColor": GLOBAL_THEME["card"], "border": f"1px solid {GLOBAL_THEME['card_border']}", "borderRadius": "18px", "color": GLOBAL_THEME["text"], "marginTop": "28px"},
            ),
        ],
        className="teoria-section",
    )


# ============================================================
# SECCIÓN 5 — FILTRACIÓN
# ============================================================

def seccion_filtracion():
    return html.Div(
        [
            html.H2([html.I(className="fa-solid fa-shield-halved", style={"marginRight": "10px"}), "Filtración"], className="teoria-section-title"),
            html.P("La filtración es el proceso de absorber fotones de Rayos X de baja energía antes de que entren al paciente. Estos fotones serían absorbidos casi por completo y contribuirían a la dosis sin aportar información útil a la imagen.", className="teoria-intro"),
            _flujo(["HAZ PRODUCIDO", "FILTRACIÓN", "ELIMINACIÓN DE FOTONES DE BAJA ENERGÍA", "HAZ ÚTIL"]),
            html.Div(
                [
                    _tarjeta("¿Qué elimina?", [html.P("La filtración elimina principalmente fotones de baja energía."), html.P("Estos fotones tienen poca capacidad de penetración y pueden aumentar la dosis sin contribuir significativamente a la imagen.")], "fa-solid fa-shield-halved"),
                    _tarjeta("Material filtrante", [html.P("El material utilizado para la filtración absorbe preferentemente los fotones de menor energía."), html.P("El resultado es un haz más penetrante.")], "fa-solid fa-cube"),
                    _tarjeta("Endurecimiento del haz", [html.P("Al eliminar los fotones de baja energía, aumenta la energía media del haz."), html.P("Este fenómeno se denomina endurecimiento del haz.")], "fa-solid fa-arrow-trend-up"),
                ],
                className="teoria-grid",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H3("¿Qué está mostrando el esquema?", style={"margin": "0 0 9px 0", "fontSize": "20px", "color": GLOBAL_THEME["text"]}),
                            html.P("El filtro se coloca en la trayectoria del haz para absorber preferentemente los fotones de menor energía. Después de atravesar el material filtrante, el haz contiene una proporción mayor de fotones de energía más alta.", style={"margin": "0", "fontSize": "13px", "lineHeight": "1.65", "color": GLOBAL_THEME["text_muted"]}),
                        ],
                        style={"padding": "15px 17px", "marginBottom": "12px", "backgroundColor": GLOBAL_THEME["card"], "border": f"1px solid {GLOBAL_THEME['card_border']}", "borderRadius": "12px"},
                    ),
                    _imagen("filtracion.jpg", "Esquema de filtración de Rayos X"),
                    html.Div(
                        [
                            html.Span("HAZ INICIAL", style={"fontWeight": "800", "color": GLOBAL_THEME["text_muted"], "fontSize": "11px"}),
                            html.Span("  →  ", style={"color": GLOBAL_THEME["accent_cyan"], "fontWeight": "800"}),
                            html.Span("FILTRO", style={"fontWeight": "800", "color": GLOBAL_THEME["text_muted"], "fontSize": "11px"}),
                            html.Span("  →  ", style={"color": GLOBAL_THEME["accent_cyan"], "fontWeight": "800"}),
                            html.Span("HAZ MÁS PENETRANTE", style={"fontWeight": "800", "color": GLOBAL_THEME["text_muted"], "fontSize": "11px"}),
                        ],
                        style={"marginTop": "12px", "padding": "12px", "backgroundColor": GLOBAL_THEME["bg"], "border": f"1px solid {GLOBAL_THEME['card_border']}", "borderRadius": "11px", "textAlign": "center", "lineHeight": "1.6"},
                    ),
                ],
                className="teoria-image-single",
            ),
        ],
        className="teoria-section",
    )


# ============================================================
# SECCIÓN 6 — COLIMACIÓN
# ============================================================

def seccion_colimacion():
    return html.Div(
        [
            html.H2([html.I(className="fa-solid fa-bullseye", style={"marginRight": "10px"}), "Colimación"], className="teoria-section-title"),
            html.P("Los tubos de Rayos X generan radiación en muchas direcciones. La restricción del haz limita el campo que será irradiado, evitando exponer partes del paciente que no necesitan ser fotografiadas y ayudando a reducir los efectos de la dispersión Compton.", className="teoria-intro"),
            _flujo(["HAZ AMPLIO", "COLIMADOR", "CAMPO LIMITADO"]),
            html.Div(
                [
                    _tarjeta("Diafragmas", [html.P("Son piezas planas de plomo con una abertura centrada en el haz."), html.P("Son simples y económicos, pero producen una geometría fija.")], "⬛"),
                    _tarjeta("Conos o cilindros", [html.P("Son limitadores de geometría fija."), html.P("Pueden presentar un desempeño algo mejor que los diafragmas.")], "fa-solid fa-caret-down"),
                    _tarjeta("Colimadores", [html.P("Son más flexibles y se utilizan en casi todos los sistemas de proyección de Rayos X."), html.P("Poseen diafragmas variables formados por piezas móviles de plomo.")], "fa-solid fa-bullseye"),
                ],
                className="teoria-grid",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H3("¿Qué hace el colimador?", style={"margin": "0 0 9px 0", "fontSize": "20px", "color": GLOBAL_THEME["text"]}),
                            html.P("El colimador restringe el tamaño y la forma del campo irradiado. En el esquema puedes observar cómo el haz primario se limita antes de llegar al objeto, mientras que la radiación dispersa puede aparecer después de la interacción con el objeto.", style={"margin": "0", "fontSize": "13px", "lineHeight": "1.65", "color": GLOBAL_THEME["text_muted"]}),
                        ],
                        style={"padding": "15px 17px", "marginBottom": "12px", "backgroundColor": GLOBAL_THEME["card"], "border": f"1px solid {GLOBAL_THEME['card_border']}", "borderRadius": "12px"},
                    ),
                    _imagen("colimacion.png", "Esquema de colimación del haz de Rayos X"),
                    html.Div(
                        [
                            html.Div("Cómo interpretarlo", style={"fontWeight": "800", "color": GLOBAL_THEME["accent_cyan"], "fontSize": "12px", "marginBottom": "5px"}),
                            html.P("Fuente → colimador → haz primario limitado → objeto. La restricción del campo ayuda a evitar irradiar regiones que no forman parte del área de interés.", style={"margin": "0", "fontSize": "12px", "lineHeight": "1.55", "color": GLOBAL_THEME["text_muted"]}),
                        ],
                        style={"marginTop": "12px", "padding": "12px 14px", "backgroundColor": GLOBAL_THEME["bg"], "border": f"1px solid {GLOBAL_THEME['card_border']}", "borderRadius": "11px"},
                    ),
                ],
                className="teoria-image-single",
            ),
            html.Div(
                [
                    html.H3("¿Por qué es importante?"),
                    html.P("La restricción del haz reduce la exposición de zonas que no forman parte del campo de imagen y ayuda a reducir los efectos perjudiciales de la dispersión."),
                ],
                className="teoria-highlight",
            ),
        ],
        className="teoria-section",
    )


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def mostrar_teoria():
    """
    Construye la sección completa de Teoría y Física de Rayos X.
    """
    return html.Div(
        [
            # HERO
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("FUNDAMENTOS · RADIOLOGÍA", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "2px", "color": GLOBAL_THEME["accent_cyan"], "marginBottom": "14px"}),
                            html.H1("Fundamentos de Rayos X", style={"margin": "0", "fontSize": "42px", "lineHeight": "1.1", "fontWeight": "700", "color": GLOBAL_THEME["text"]}),
                            html.P("Comprende la física detrás de los Rayos X, su producción y los principios que permiten transformar la radiación en una imagen médica.", style={"margin": "16px 0 0 0", "maxWidth": "680px", "fontSize": "15px", "lineHeight": "1.7", "color": GLOBAL_THEME["text_muted"]}),
                            html.Div(style={"width": "70px", "height": "3px", "backgroundColor": GLOBAL_THEME["accent_cyan"], "borderRadius": "3px", "marginTop": "24px"}),
                        ],
                        style={"position": "relative", "zIndex": "2"},
                    ),
                    html.Img(src="/assets/teoria/huesitos1.svg", style={"position": "absolute", "right": "55px", "top": "50%", "transform": "translateY(-50%)", "width": "150px", "height": "auto", "pointerEvents": "none"}),
                ],
                className="rx-hero-card",
                style={
                    "position": "relative", "overflow": "hidden",
                    "background": f"linear-gradient(135deg, {GLOBAL_THEME['card']} 0%, {GLOBAL_THEME['bg']} 100%)",
                    "border": f"1px solid {GLOBAL_THEME['card_border']}", "borderRadius": "18px",
                    "padding": "42px 46px", "marginBottom": "28px", "minHeight": "220px",
                    "boxSizing": "border-box", "display": "flex", "alignItems": "center",
                    "boxShadow": "0 12px 30px rgba(0, 0, 0, 0.18)",
                },
            ),

            # PESTAÑAS
            dcc.Tabs(
                id="teoria-tabs",
                value="fundamentos",
                style={"borderBottom": f"1px solid {GLOBAL_THEME['card_border']}", "marginBottom": "20px"},
                children=[
                    dcc.Tab(label="Fundamentos", value="fundamentos", style={"backgroundColor": GLOBAL_THEME["card"], "border": f"1px solid {GLOBAL_THEME['card_border']}", "color": GLOBAL_THEME["text_muted"], "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px"}, selected_style={"backgroundColor": GLOBAL_THEME["accent_cyan"], "border": f"1px solid {GLOBAL_THEME['accent_cyan']}", "color": GLOBAL_THEME["bg"], "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px", "fontWeight": "bold"}, children=seccion_fundamentos()),
                    dcc.Tab(label="Producción", value="produccion", style={"backgroundColor": GLOBAL_THEME["card"], "border": f"1px solid {GLOBAL_THEME['card_border']}", "color": GLOBAL_THEME["text_muted"], "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px"}, selected_style={"backgroundColor": GLOBAL_THEME["accent_cyan"], "border": f"1px solid {GLOBAL_THEME['accent_cyan']}", "color": GLOBAL_THEME["bg"], "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px", "fontWeight": "bold"}, children=seccion_produccion()),
                    dcc.Tab(label="Tubo", value="tubo", style={"backgroundColor": GLOBAL_THEME["card"], "border": f"1px solid {GLOBAL_THEME['card_border']}", "color": GLOBAL_THEME["text_muted"], "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px"}, selected_style={"backgroundColor": GLOBAL_THEME["accent_cyan"], "border": f"1px solid {GLOBAL_THEME['accent_cyan']}", "color": GLOBAL_THEME["bg"], "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px", "fontWeight": "bold"}, children=seccion_tubo()),
                    dcc.Tab(label="Parámetros", value="parametros", style={"backgroundColor": GLOBAL_THEME["card"], "border": f"1px solid {GLOBAL_THEME['card_border']}", "color": GLOBAL_THEME["text_muted"], "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px"}, selected_style={"backgroundColor": GLOBAL_THEME["accent_cyan"], "border": f"1px solid {GLOBAL_THEME['accent_cyan']}", "color": GLOBAL_THEME["bg"], "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px", "fontWeight": "bold"}, children=seccion_parametros()),
                    dcc.Tab(label="Filtración", value="filtracion", style={"backgroundColor": GLOBAL_THEME["card"], "border": f"1px solid {GLOBAL_THEME['card_border']}", "color": GLOBAL_THEME["text_muted"], "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px"}, selected_style={"backgroundColor": GLOBAL_THEME["accent_cyan"], "border": f"1px solid {GLOBAL_THEME['accent_cyan']}", "color": GLOBAL_THEME["bg"], "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px", "fontWeight": "bold"}, children=seccion_filtracion()),
                    dcc.Tab(label="Colimación", value="colimacion", style={"backgroundColor": GLOBAL_THEME["card"], "border": f"1px solid {GLOBAL_THEME['card_border']}", "color": GLOBAL_THEME["text_muted"], "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px"}, selected_style={"backgroundColor": GLOBAL_THEME["accent_cyan"], "border": f"1px solid {GLOBAL_THEME['accent_cyan']}", "color": GLOBAL_THEME["bg"], "padding": "10px 15px", "borderRadius": "8px 8px 0 0", "marginRight": "5px", "fontWeight": "bold"}, children=seccion_colimacion()),
                ],
            ),
        ],
        className="teoria-container",
    )

# ============================================================
# CALLBACKS DEL MÓDULO
# ============================================================

def registrar_callbacks(app):
    """
    Actualiza el valor de mAs a partir de corriente (mA)
    y tiempo de exposición (s).
    """

    @app.callback(
        Output("teoria-mas-output", "children"),
        Input("teoria-ma-slider", "value"),
        Input("teoria-tiempo-slider", "value"),
    )
    def actualizar_mas(mA, tiempo):
        if mA is None or tiempo is None:
            return "0.00"
        return f"{float(mA) * float(tiempo):.2f}"