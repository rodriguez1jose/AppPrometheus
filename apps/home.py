# apps/home.py
# =============================================================================
# PROMETEO — Carátula Principal (Home)
# =============================================================================
from dash import dcc, html
from config import THEME, STYLE_CONTAINER, STYLE_CARD


def home_layout():
    """Retorna la vista principal con los dos módulos raíz: SyS e Imagenología."""
    return html.Div(
        [
            # Barra superior con Switch de Tema
            html.Div(
                [
                    html.Button(
                        [
                            html.I(id="theme-toggle-icon", className="fa-solid fa-moon", style={"marginRight": "8px"}),
                            html.Span(id="theme-toggle-text", children="Modo Claro"),
                        ],
                        id="theme-toggle-btn",
                        n_clicks=0,
                        style={
                            "background": "rgba(255, 255, 255, 0.08)",
                            "border": f"1px solid {THEME['border']}",
                            "color": THEME["text"],
                            "padding": "8px 16px",
                            "borderRadius": "20px",
                            "cursor": "pointer",
                            "fontWeight": "600",
                            "fontSize": "13px",
                            "display": "inline-flex",
                            "alignItems": "center",
                            "transition": "all 0.2s ease",
                        },
                    )
                ],
                style={
                    "display": "flex",
                    "justifyContent": "flex-end",
                    "padding": "16px 24px 0 0",
                    "width": "100%",
                    "boxSizing": "border-box",
                },
            ),

            # Hero: Ícono + Título de la plataforma
            html.Div(
                [
                    html.I(
                        className="fa-solid fa-fire",
                        style={
                            "fontSize": "56px",
                            "background": "linear-gradient(135deg, #38bdf8 0%, #a855f7 50%, #f59e0b 100%)",
                            "-webkit-background-clip": "text",
                            "-webkit-text-fill-color": "transparent",
                            "marginBottom": "16px",
                        },
                    ),
                    html.H1(
                        "PROMETEO",
                        style={
                            "fontSize": "64px",
                            "fontWeight": "800",
                            "letterSpacing": "6px",
                            "margin": "0",
                            "background": "linear-gradient(135deg, #38bdf8 0%, #a855f7 50%, #f59e0b 100%)",
                            "-webkit-background-clip": "text",
                            "-webkit-text-fill-color": "transparent",
                            "backgroundClip": "text",
                        },
                    ),
                    html.P(
                        "Plataforma Educativa Interactiva",
                        style={
                            "color": THEME["text"],
                            "fontSize": "20px",
                            "marginTop": "16px",
                            "marginBottom": "6px",
                            "fontWeight": "300",
                        },
                    ),
                    html.P(
                        "Señales, Sistemas y Diagnóstico por Imágenes",
                        style={
                            "color": THEME["text_muted"],
                            "fontSize": "15px",
                            "margin": "0",
                        },
                    ),
                ],
                style={
                    "textAlign": "center",
                    "padding": "80px 20px 50px 20px",
                },
            ),

            # Grid de 2 tarjetas maestras
            html.Div(
                [
                    # --- Tarjeta Señales y Sistemas ---
                    dcc.Link(
                        html.Div(
                            [
                                html.Div(
                                    html.I(
                                        className="fa-solid fa-chart-line",
                                        style={
                                            "fontSize": "42px",
                                            "color": THEME["accent_cyan"],
                                        },
                                    ),
                                    style={
                                        "width": "80px",
                                        "height": "80px",
                                        "borderRadius": "20px",
                                        "background": "rgba(56, 189, 248, 0.12)",
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "marginBottom": "20px",
                                    },
                                ),
                                html.H2(
                                    "Señales y Sistemas",
                                    style={
                                        "fontSize": "24px",
                                        "fontWeight": "700",
                                        "color": THEME["text"],
                                        "margin": "0 0 10px 0",
                                    },
                                ),
                                html.P(
                                    "Series de Fourier, convolución, transformada, muestreo y control de sistemas.",
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
                                **STYLE_CARD,
                                "padding": "36px 30px",
                                "cursor": "pointer",
                                "transition": "transform 0.2s ease, box-shadow 0.2s ease",
                            },
                        ),
                        href="/sys",
                        style={"textDecoration": "none"},
                    ),

                    # --- Tarjeta Imagenología ---
                    dcc.Link(
                        html.Div(
                            [
                                html.Div(
                                    html.I(
                                        className="fa-solid fa-hospital",
                                        style={
                                            "fontSize": "42px",
                                            "color": THEME["accent_purple"],
                                        },
                                    ),
                                    style={
                                        "width": "80px",
                                        "height": "80px",
                                        "borderRadius": "20px",
                                        "background": "rgba(168, 85, 247, 0.12)",
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "marginBottom": "20px",
                                    },
                                ),
                                html.H2(
                                    "Imagenología",
                                    style={
                                        "fontSize": "24px",
                                        "fontWeight": "700",
                                        "color": THEME["text"],
                                        "margin": "0 0 10px 0",
                                    },
                                ),
                                html.P(
                                    "Tomografía computarizada, resonancia magnética y rayos X: física, contraste y diagnóstico.",
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
                                **STYLE_CARD,
                                "padding": "36px 30px",
                                "cursor": "pointer",
                                "transition": "transform 0.2s ease, box-shadow 0.2s ease",
                            },
                        ),
                        href="/imaging",
                        style={"textDecoration": "none"},
                    ),
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))",
                    "gap": "28px",
                    "maxWidth": "900px",
                    "margin": "0 auto",
                    "padding": "0 20px 60px 20px",
                },
            ),

            # Footer
            html.Div(
                "© Prometeo - Plataforma Educativa",
                style={
                    "textAlign": "center",
                    "color": THEME["text_muted"],
                    "fontSize": "13px",
                    "padding": "20px",
                    "borderTop": f"1px solid {THEME['card_border']}",
                    "marginTop": "auto",
                },
            ),
        ],
        style={
            **STYLE_CONTAINER,
            "minHeight": "100vh",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "space-between",
        },
    )

