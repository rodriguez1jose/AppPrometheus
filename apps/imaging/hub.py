# apps/imaging/hub.py
# =============================================================================
# PROMETEO — Hub de Imagenología Médica (CT | MRI | Rx)
# =============================================================================
from dash import dcc, html
from config import THEME, STYLE_CONTAINER


def _hex_to_rgb(hex_color: str) -> str:
    """Convierte '#38bdf8' → '56, 189, 248' para usar en rgba()."""
    h = hex_color.lstrip("#")
    return f"{int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)}"


def _imaging_card(icon: str, title: str, subtitle: str, description: str, color: str, href: str):
    """Componente reutilizable para cada tarjeta de modalidad en el hub."""
    return dcc.Link(
        html.Div(
            [
                html.Div(
                    html.I(
                        className=icon,
                        style={"fontSize": "38px", "color": color},
                    ),
                    style={
                        "width": "72px",
                        "height": "72px",
                        "borderRadius": "18px",
                        "background": f"rgba({_hex_to_rgb(color)}, 0.12)",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "marginBottom": "18px",
                    },
                ),
                html.H2(
                    title,
                    style={
                        "fontSize": "26px",
                        "fontWeight": "700",
                        "color": THEME["text"],
                        "margin": "0 0 4px 0",
                    },
                ),
                html.Div(
                    subtitle,
                    style={
                        "color": color,
                        "fontSize": "13px",
                        "fontWeight": "600",
                        "letterSpacing": "1px",
                        "marginBottom": "12px",
                        "textTransform": "uppercase",
                    },
                ),
                html.P(
                    description,
                    style={
                        "color": THEME["text_muted"],
                        "fontSize": "14px",
                        "lineHeight": "1.6",
                        "margin": "0",
                    },
                ),
            ],
            className="home-card",
            style={
                "background": "linear-gradient(145deg, #1e293b 0%, #0f172a 100%)",
                "border": f"1px solid {THEME['card_border']}",
                "boxShadow": "0 4px 12px rgba(0,0,0,0.3)",
                "borderRadius": "16px",
                "padding": "30px",
                "cursor": "pointer",
                "transition": "transform 0.2s ease, box-shadow 0.2s ease",
                "height": "100%",
                "boxSizing": "border-box",
            },
        ),
        href=href,
        style={"textDecoration": "none"},
    )


def imaging_hub_layout():
    """Carátula de Imagenología: 3 tarjetas que redirigen a /imaging/{ct|mri|rx}."""
    return html.Div(
        [
            dcc.Link(
                html.Div(
                    [
                        html.I(className="fa-solid fa-arrow-left", style={"marginRight": "8px", "fontSize": "13px"}),
                        "Volver a Prometeo",
                    ],
                    style={
                        "display": "inline-flex",
                        "alignItems": "center",
                        "color": THEME["text_muted"],
                        "fontSize": "13px",
                        "fontWeight": "500",
                        "padding": "8px 14px",
                        "borderRadius": "8px",
                        "border": f"1px solid {THEME['card_border']}",
                        "transition": "all 0.2s ease",
                        "cursor": "pointer",
                        "marginBottom": "20px",
                    },
                ),
                href="/",
                style={"textDecoration": "none"},
            ),

            # Header
            html.Div(
                [
                    html.Div(
                        [
                            html.I(
                                className="fa-solid fa-hospital",
                                style={
                                    "fontSize": "22px",
                                    "color": THEME["accent_purple"],
                                    "marginRight": "10px",
                                },
                            ),
                            html.Span(
                                "IMAGENOLOGÍA MÉDICA",
                                style={
                                    "fontSize": "12px",
                                    "letterSpacing": "3px",
                                    "fontWeight": "600",
                                    "color": THEME["accent_purple"],
                                },
                            ),
                        ],
                        style={"marginBottom": "10px"},
                    ),
                    html.H1(
                        "Diagnóstico por Imágenes",
                        style={
                            "fontSize": "32px",
                            "fontWeight": "700",
                            "color": THEME["text"],
                            "margin": "0 0 8px 0",
                        },
                    ),
                    html.P(
                        "Elige una modalidad para explorar sus principios físicos y simulaciones interactivas.",
                        style={
                            "color": THEME["text_muted"],
                            "fontSize": "15px",
                            "margin": "0",
                        },
                    ),
                ],
                style={
                    "background": "linear-gradient(135deg, rgba(168,85,247,0.15) 0%, rgba(56,189,248,0.08) 100%)",
                    "borderRadius": "16px",
                    "padding": "32px",
                    "marginBottom": "28px",
                    "border": f"1px solid {THEME['card_border']}",
                },
            ),

            # Grid de 3 tarjetas
            html.Div(
                [
                    _imaging_card(
                        icon="fa-solid fa-x-ray",
                        title="CT",
                        subtitle="Tomografía Computarizada",
                        description="Atenuación de rayos X, escala Hounsfield, transformadas y ventanas de visualización.",
                        color=THEME["accent_cyan"],
                        href="/imaging/ct",
                    ),
                    _imaging_card(
                        icon="fa-solid fa-magnet",
                        title="MRI",
                        subtitle="Resonancia Magnética",
                        description="Relajación T1/T2, espacio k, secuencias y contraste tisular.",
                        color=THEME["accent_purple"],
                        href="/imaging/mri",
                    ),
                    _imaging_card(
                        icon="fa-solid fa-bone",
                        title="Rx",
                        subtitle="Radiografía",
                        description="Proyección de rayos X, interacción con la materia, densidades y análisis radiográfico.",
                        color=THEME["accent_amber"],
                        href="/imaging/rx",
                    ),
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))",
                    "gap": "24px",
                },
            ),
        ],
        style=STYLE_CONTAINER,
    )


def modalidad_wrapper(app_content, titulo: str, color: str):
    """
    Envuelve el layout de una modalidad (CT, MRI) con un header común y botón 'Volver a Imagenología'.
    """
    return html.Div(
        [
            # Botón volver
            dcc.Link(
                html.Div(
                    [
                        html.I(
                            className="fa-solid fa-arrow-left",
                            style={"marginRight": "8px", "fontSize": "13px"},
                        ),
                        "Volver a Imagenología",
                    ],
                    style={
                        "display": "inline-flex",
                        "alignItems": "center",
                        "color": THEME["text_muted"],
                        "fontSize": "13px",
                        "fontWeight": "500",
                        "padding": "8px 14px",
                        "borderRadius": "8px",
                        "border": f"1px solid {THEME['card_border']}",
                        "transition": "all 0.2s ease",
                        "cursor": "pointer",
                    },
                ),
                href="/imaging",
                style={"textDecoration": "none"},
            ),

            # Título de la modalidad
            html.Div(
                [
                    html.H1(
                        titulo,
                        style={
                            "fontSize": "30px",
                            "fontWeight": "700",
                            "color": THEME["text"],
                            "margin": "20px 0 6px 0",
                        },
                    ),
                    html.Div(
                        style={
                            "height": "3px",
                            "width": "60px",
                            "background": color,
                            "borderRadius": "2px",
                            "marginBottom": "24px",
                        },
                    ),
                ]
            ),

            # Contenido específico de la modalidad
            html.Div(app_content),
        ],
        style=STYLE_CONTAINER,
    )

