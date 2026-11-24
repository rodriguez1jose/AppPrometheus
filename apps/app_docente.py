# apps/app_docente.py
# =============================================================================
# PROMETEO — Panel del Docente: Métricas de Dificultad y Comprensión Colectiva
# Acceso Restringido para Plantel Docente:
#   Usuario: Calderon_Humberto
#   Contraseña: HC2026
# =============================================================================
from __future__ import annotations

import os
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, State, no_update
from dash.exceptions import PreventUpdate

from config import THEME, STYLE_CARD, STYLE_SECTION_TITLE, STYLE_LABEL, STYLE_CONTAINER, ESTUDIANTES_CSV
from services.gemini_service import gemini_service

# Credenciales autorizadas para el docente
DOCENTE_USER = "Calderon_Humberto"
DOCENTE_PASS = "HC2026"


def _cargar_datos_estudiantes() -> pd.DataFrame:
    """
    Carga exclusivamente los datos reales de estudiantes desde resultados_estudiantes.csv.
    Si el archivo no existe o está vacío (plataforma sin entregas aún), retorna un DataFrame vacío.
    """
    columnas = ["nombre", "fecha", "actividad", "modulo", "puntaje"]
    if os.path.exists(ESTUDIANTES_CSV):
        try:
            df = pd.read_csv(ESTUDIANTES_CSV)
            if not df.empty and "nombre" in df.columns and "puntaje" in df.columns:
                if "modulo" not in df.columns:
                    df["modulo"] = "Rayos X"
                return df
        except Exception:
            pass
    return pd.DataFrame(columns=columnas)


def _estilo_figura(fig, alto=340):
    """Aplica formato visual unificado para el panel del docente."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family='"Inter", "Segoe UI", sans-serif', color=THEME["text"], size=12),
        margin=dict(l=20, r=20, t=35, b=25),
        uirevision="fija-docente",
        height=alto,
    )
    fig.update_xaxes(gridcolor="rgba(148,163,184,0.12)", zerolinecolor="rgba(148,163,184,0.12)")
    fig.update_yaxes(gridcolor="rgba(148,163,184,0.12)", zerolinecolor="rgba(148,163,184,0.12)")
    return fig


# =============================================================================
# VISTA: FORMULARIO DE INICIO DE SESIÓN DOCENTE
# =============================================================================
def _render_login_view():
    return html.Div(
        [
            # Enlace de regreso al Home
            html.Div(
                dcc.Link(
                    [
                        html.I(className="fa-solid fa-arrow-left", style={"marginRight": "8px"}),
                        "Volver al Inicio",
                    ],
                    href="/",
                    style={
                        "color": THEME["text_muted"],
                        "textDecoration": "none",
                        "fontSize": "13px",
                        "fontWeight": "600",
                        "display": "inline-flex",
                        "alignItems": "center",
                        "padding": "6px 12px",
                        "borderRadius": "8px",
                        "background": "rgba(255, 255, 255, 0.05)",
                        "border": f"1px solid {THEME['card_border']}",
                    },
                ),
                style={"marginBottom": "24px"},
            ),

            # Tarjeta de Autenticación Central
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                html.I(
                                    className="fa-solid fa-chalkboard-user",
                                    style={"fontSize": "32px", "color": THEME["accent_amber"]},
                                ),
                                style={
                                    "width": "68px",
                                    "height": "68px",
                                    "borderRadius": "18px",
                                    "background": "rgba(245, 158, 11, 0.12)",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                    "margin": "0 auto 16px auto",
                                },
                            ),
                            html.H2(
                                "Plantel Docente",
                                style={
                                    "fontSize": "24px",
                                    "fontWeight": "800",
                                    "color": THEME["text"],
                                    "margin": "0 0 6px 0",
                                },
                            ),
                            html.P(
                                "Portal restringido para instructores y administración académica.",
                                style={
                                    "color": THEME["text_muted"],
                                    "fontSize": "13px",
                                    "margin": "0 0 24px 0",
                                },
                            ),
                        ],
                        style={"textAlign": "center"},
                    ),

                    # Campo: Usuario
                    html.Div(
                        [
                            html.Label(
                                "Usuario Institucional",
                                style={**STYLE_LABEL, "display": "block", "marginBottom": "6px"},
                            ),
                            dcc.Input(
                                id="docente-login-usuario",
                                type="text",
                                placeholder="Ingresa tu usuario institucional",
                                style={
                                    "width": "100%",
                                    "background": "rgba(255, 255, 255, 0.05)",
                                    "border": f"1px solid {THEME['card_border']}",
                                    "color": THEME["text"],
                                    "padding": "10px 14px",
                                    "borderRadius": "8px",
                                    "fontSize": "14px",
                                    "boxSizing": "border-box",
                                    "outline": "none",
                                },
                            ),
                        ],
                        style={"marginBottom": "16px"},
                    ),

                    # Campo: Contraseña
                    html.Div(
                        [
                            html.Label(
                                "Contraseña",
                                style={**STYLE_LABEL, "display": "block", "marginBottom": "6px"},
                            ),
                            dcc.Input(
                                id="docente-login-password",
                                type="password",
                                placeholder="••••••••",
                                style={
                                    "width": "100%",
                                    "background": "rgba(255, 255, 255, 0.05)",
                                    "border": f"1px solid {THEME['card_border']}",
                                    "color": THEME["text"],
                                    "padding": "10px 14px",
                                    "borderRadius": "8px",
                                    "fontSize": "14px",
                                    "boxSizing": "border-box",
                                    "outline": "none",
                                },
                            ),
                        ],
                        style={"marginBottom": "20px"},
                    ),

                    # Botón de Inicio de Sesión
                    html.Button(
                        [
                            html.I(className="fa-solid fa-arrow-right-to-bracket", style={"marginRight": "8px"}),
                            "Ingresar al Panel",
                        ],
                        id="docente-btn-login",
                        n_clicks=0,
                        style={
                            "width": "100%",
                            "background": "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
                            "color": "#ffffff",
                            "border": "none",
                            "padding": "11px",
                            "borderRadius": "8px",
                            "fontWeight": "700",
                            "fontSize": "14px",
                            "cursor": "pointer",
                            "transition": "opacity 0.2s ease",
                        },
                    ),

                    # Contenedor de Error
                    html.Div(id="docente-login-error", style={"marginTop": "14px"}),
                ],
                style={
                    **STYLE_CARD,
                    "maxWidth": "420px",
                    "margin": "40px auto 60px auto",
                    "padding": "32px 30px",
                    "border": f"1px solid {THEME['border']}",
                },
            ),
        ],
        style={"padding": "20px 0"},
    )


# =============================================================================
# VISTA: PANEL DASHBOARD DOCENTE (SOLO USUARIOS AUTENTICADOS)
# =============================================================================
def _render_dashboard_view():
    df = _cargar_datos_estudiantes()
    tiene_datos = not df.empty

    total_estudiantes = df["nombre"].nunique() if tiene_datos else 0
    total_entregas = len(df) if tiene_datos else 0
    promedio_global = f"{round(df['puntaje'].mean(), 1)} / 100" if tiene_datos else "--"

    if tiene_datos:
        resumen_modulos = df.groupby("modulo")["puntaje"].mean().to_dict()
        modulo_critico = min(resumen_modulos, key=resumen_modulos.get) if resumen_modulos else "Sin datos"
        subtitulo_critico = f"Promedio: {round(resumen_modulos.get(modulo_critico, 0), 1)} pts"
    else:
        modulo_critico = "Sin datos"
        subtitulo_critico = "Requiere entregas de la cohorte"

    return html.Div(
        [
            # Header Superior con Navegación y Sesión Docente
            html.Div(
                [
                    dcc.Link(
                        [
                            html.I(className="fa-solid fa-arrow-left", style={"marginRight": "8px"}),
                            "Volver al Inicio",
                        ],
                        href="/",
                        style={
                            "color": THEME["text_muted"],
                            "textDecoration": "none",
                            "fontSize": "13px",
                            "fontWeight": "600",
                            "display": "inline-flex",
                            "alignItems": "center",
                            "padding": "6px 12px",
                            "borderRadius": "8px",
                            "background": "rgba(255, 255, 255, 0.05)",
                            "border": f"1px solid {THEME['card_border']}",
                        },
                    ),
                    html.Div(
                        [
                            html.Span(
                                [
                                    html.I(className="fa-solid fa-user-check", style={"color": "#10b981", "marginRight": "6px"}),
                                    f"Docente: {DOCENTE_USER}",
                                ],
                                style={
                                    "color": THEME["text"],
                                    "fontSize": "13px",
                                    "fontWeight": "600",
                                    "marginRight": "14px",
                                    "background": "rgba(16, 185, 129, 0.12)",
                                    "padding": "6px 12px",
                                    "borderRadius": "8px",
                                    "border": "1px solid rgba(16, 185, 129, 0.3)",
                                },
                            ),
                            html.Button(
                                [
                                    html.I(className="fa-solid fa-right-from-bracket", style={"marginRight": "6px"}),
                                    "Cerrar Sesión",
                                ],
                                id="docente-btn-logout",
                                n_clicks=0,
                                style={
                                    "background": "rgba(239, 68, 68, 0.12)",
                                    "border": "1px solid rgba(239, 68, 68, 0.35)",
                                    "color": "#ef4444",
                                    "padding": "6px 12px",
                                    "borderRadius": "8px",
                                    "cursor": "pointer",
                                    "fontWeight": "600",
                                    "fontSize": "13px",
                                },
                            ),
                        ],
                        style={"display": "flex", "alignItems": "center"},
                    ),
                ],
                style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "20px"},
            ),

            # Título del Panel
            html.Div(
                [
                    html.Div(
                        [
                            html.I(
                                className="fa-solid fa-chalkboard-user",
                                style={"fontSize": "26px", "color": THEME["accent_amber"], "marginRight": "12px"},
                            ),
                            html.H1(
                                "Panel de Gestión y Analítica Docente",
                                style={
                                    "fontSize": "28px",
                                    "fontWeight": "800",
                                    "color": THEME["text"],
                                    "margin": "0",
                                    "display": "inline-block",
                                },
                            ),
                        ],
                        style={"display": "flex", "alignItems": "center", "marginBottom": "6px"},
                    ),
                    html.P(
                        "Métricas de dificultad en tiempo real, detección temprana de vacíos conceptuales y rendimiento de la cohorte.",
                        style={"color": THEME["text_muted"], "fontSize": "14px", "margin": "0"},
                    ),
                ],
                style={"marginBottom": "24px"},
            ),

            # Tarjetas KPI de Resumen Global
            html.Div(
                [
                    # KPI 1: Estudiantes Activos
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.I(className="fa-solid fa-users", style={"color": THEME["accent_cyan"], "fontSize": "20px"}),
                                    html.Span("Estudiantes Activos", style={"color": THEME["text_muted"], "fontSize": "12px", "fontWeight": "600", "marginLeft": "8px", "textTransform": "uppercase"}),
                                ],
                                style={"display": "flex", "alignItems": "center", "marginBottom": "10px"},
                            ),
                            html.Div(str(total_estudiantes), style={"fontSize": "32px", "fontWeight": "800", "color": THEME["text"]}),
                            html.Div("Matriculados en cohorte actual" if tiene_datos else "Sin alumnos registrados aún", style={"color": THEME["text_muted"], "fontSize": "12px", "marginTop": "4px"}),
                        ],
                        style={**STYLE_CARD, "padding": "20px 24px"},
                    ),

                    # KPI 2: Entregas Totales
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.I(className="fa-solid fa-file-circle-check", style={"color": THEME["accent_purple"], "fontSize": "20px"}),
                                    html.Span("Actividades Enviadas", style={"color": THEME["text_muted"], "fontSize": "12px", "fontWeight": "600", "marginLeft": "8px", "textTransform": "uppercase"}),
                                ],
                                style={"display": "flex", "alignItems": "center", "marginBottom": "10px"},
                            ),
                            html.Div(str(total_entregas), style={"fontSize": "32px", "fontWeight": "800", "color": THEME["text"]}),
                            html.Div("Quizzes, talleres y simulaciones" if tiene_datos else "Aún no hay entregas", style={"color": THEME["text_muted"], "fontSize": "12px", "marginTop": "4px"}),
                        ],
                        style={**STYLE_CARD, "padding": "20px 24px"},
                    ),

                    # KPI 3: Promedio Global
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.I(className="fa-solid fa-chart-line", style={"color": "#10b981", "fontSize": "20px"}),
                                    html.Span("Promedio de Curso", style={"color": THEME["text_muted"], "fontSize": "12px", "fontWeight": "600", "marginLeft": "8px", "textTransform": "uppercase"}),
                                ],
                                style={"display": "flex", "alignItems": "center", "marginBottom": "10px"},
                            ),
                            html.Div(promedio_global, style={"fontSize": "32px", "fontWeight": "800", "color": "#10b981"}),
                            html.Div("Tasa de comprensión colectiva" if tiene_datos else "Pendiente de evaluaciones", style={"color": THEME["text_muted"], "fontSize": "12px", "marginTop": "4px"}),
                        ],
                        style={**STYLE_CARD, "padding": "20px 24px"},
                    ),

                    # KPI 4: Concepto Crítico
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.I(className="fa-solid fa-triangle-exclamation", style={"color": THEME["accent_amber"], "fontSize": "20px"}),
                                    html.Span("Área Más Desafiante", style={"color": THEME["text_muted"], "fontSize": "12px", "fontWeight": "600", "marginLeft": "8px", "textTransform": "uppercase"}),
                                ],
                                style={"display": "flex", "alignItems": "center", "marginBottom": "10px"},
                            ),
                            html.Div(modulo_critico, style={"fontSize": "24px", "fontWeight": "800", "color": THEME["accent_amber"]}),
                            html.Div(subtitulo_critico, style={"color": THEME["text_muted"], "fontSize": "12px", "marginTop": "4px"}),
                        ],
                        style={**STYLE_CARD, "padding": "20px 24px"},
                    ),
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                    "gap": "18px",
                    "marginBottom": "24px",
                },
            ),

            # Sección Gráfica Analítica (Dos Columnas)
            html.Div(
                [
                    # Gráfico 1: Rendimiento por Módulo
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.I(className="fa-solid fa-chart-column", style={"color": THEME["accent_cyan"], "marginRight": "8px"}),
                                    html.Span("Tasa de Comprensión por Módulo", style={"fontWeight": "700", "fontSize": "15px", "color": THEME["text"]}),
                                ],
                                style={"marginBottom": "12px"},
                            ),
                            dcc.Graph(id="docente-grafico-modulos", config={"displayModeBar": False}),
                        ],
                        style={**STYLE_CARD, "padding": "20px"},
                    ),

                    # Gráfico 2: Distribución de Calificaciones
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.I(className="fa-solid fa-chart-area", style={"color": THEME["accent_purple"], "marginRight": "8px"}),
                                    html.Span("Distribución de Calificaciones del Curso", style={"fontWeight": "700", "fontSize": "15px", "color": THEME["text"]}),
                                ],
                                style={"marginBottom": "12px"},
                            ),
                            dcc.Graph(id="docente-grafico-distribucion", config={"displayModeBar": False}),
                        ],
                        style={**STYLE_CARD, "padding": "20px"},
                    ),
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(420px, 1fr))",
                    "gap": "20px",
                    "marginBottom": "24px",
                },
            ),

            # Asistente Pedagógico Docente (Gemini IA)
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.I(className="fa-solid fa-wand-magic-sparkles", style={"color": THEME["accent_cyan"], "fontSize": "18px", "marginRight": "10px"}),
                                    html.Span("Asistente Pedagógico IA — Recomendaciones de Refuerzo para la Clase", style={"fontWeight": "700", "fontSize": "15px", "color": THEME["text"]}),
                                ],
                                style={"display": "flex", "alignItems": "center"},
                            ),
                            html.Button(
                                [
                                    html.I(className="fa-solid fa-bolt", style={"marginRight": "8px"}),
                                    "Generar Plan de Refuerzo",
                                ],
                                id="docente-btn-generar-gemini",
                                n_clicks=0,
                                style={
                                    "background": "linear-gradient(135deg, #0284c7 0%, #38bdf8 100%)",
                                    "color": "#ffffff",
                                    "border": "none",
                                    "padding": "8px 16px",
                                    "borderRadius": "8px",
                                    "cursor": "pointer",
                                    "fontWeight": "600",
                                    "fontSize": "13px",
                                },
                            ),
                        ],
                        style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "14px"},
                    ),
                    dcc.Loading(
                        html.Div(
                            "Haz clic en 'Generar Plan de Refuerzo' para que la IA analice las calificaciones y proponga 3 estrategias didácticas y una pregunta detonante para la próxima sesión.",
                            id="docente-resumen-ia",
                            style={"color": THEME["text_muted"], "fontSize": "13.5px", "lineHeight": "1.6"},
                        ),
                        type="dot",
                        color=THEME["accent_cyan"],
                    ),
                ],
                style={
                    **STYLE_CARD,
                    "padding": "22px 26px",
                    "marginBottom": "24px",
                    "border": f"1px solid {THEME['border']}",
                },
            ),

            # Tabla de Entregas y Exportación
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.I(className="fa-solid fa-list-check", style={"color": THEME["accent_cyan"], "marginRight": "8px"}),
                                    html.Span("Registro Detallado de Entregas y Evaluaciones", style={"fontWeight": "700", "fontSize": "15px", "color": THEME["text"]}),
                                ]
                            ),
                            html.Div(
                                [
                                    dcc.Input(
                                        id="docente-filtro-nombre",
                                        type="text",
                                        placeholder="Buscar estudiante...",
                                        style={
                                            "background": "rgba(255, 255, 255, 0.05)",
                                            "border": f"1px solid {THEME['card_border']}",
                                            "color": THEME["text"],
                                            "padding": "7px 12px",
                                            "borderRadius": "6px",
                                            "fontSize": "13px",
                                            "marginRight": "10px",
                                            "outline": "none",
                                        },
                                    ),
                                    dcc.Dropdown(
                                        id="docente-filtro-modulo",
                                        options=[
                                            {"label": "Todos los Módulos", "value": "TODOS"},
                                            {"label": "Rayos X", "value": "Rayos X"},
                                            {"label": "Resonancia (MRI)", "value": "MRI"},
                                            {"label": "Tomografía (CT)", "value": "CT"},
                                            {"label": "Señales y Sistemas", "value": "Señales"},
                                            {"label": "Casos Clínicos", "value": "Casos"},
                                        ],
                                        value="TODOS",
                                        clearable=False,
                                        style={"width": "180px", "display": "inline-block", "marginRight": "10px", "fontSize": "13px"},
                                    ),
                                    html.Button(
                                        [
                                            html.I(className="fa-solid fa-file-csv", style={"marginRight": "6px"}),
                                            "Exportar CSV",
                                        ],
                                        id="docente-btn-exportar",
                                        n_clicks=0,
                                        style={
                                            "background": "rgba(16, 185, 129, 0.15)",
                                            "color": "#10b981",
                                            "border": "1px solid #10b981",
                                            "padding": "7px 14px",
                                            "borderRadius": "6px",
                                            "fontWeight": "600",
                                            "fontSize": "13px",
                                            "cursor": "pointer",
                                        },
                                    ),
                                    dcc.Download(id="docente-descargar-csv"),
                                ],
                                style={"display": "flex", "alignItems": "center"},
                            ),
                        ],
                        style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "16px", "flexWrap": "wrap", "gap": "12px"},
                    ),

                    # Contenedor dinámico de la tabla
                    html.Div(id="docente-tabla-contenedor"),
                ],
                style={**STYLE_CARD, "padding": "22px 26px", "marginBottom": "30px"},
            ),
        ],
        style={"padding": "10px 0"},
    )


# =============================================================================
# LAYOUT MAESTRO: CONTENEDOR CON STORE DE SESIÓN
# =============================================================================
def layout():
    return html.Div(
        [
            dcc.Store(id="docente-auth-store", storage_type="session", data={"autenticado": False, "usuario": None}),
            html.Div(id="docente-contenido-dinamico"),
        ],
        style={**STYLE_CONTAINER, "padding": "24px 20px 60px 20px"},
    )


# =============================================================================
# REGISTRO DE CALLBACKS
# =============================================================================
def register_callbacks(app):

    # 1. Conmutador de vista según estado de autenticación
    @app.callback(
        Output("docente-contenido-dinamico", "children"),
        Input("docente-auth-store", "data"),
    )
    def renderizar_vista(auth_data):
        if auth_data and auth_data.get("autenticado") is True:
            return _render_dashboard_view()
        return _render_login_view()

    # 2. Procesamiento de inicio de sesión
    @app.callback(
        Output("docente-auth-store", "data", allow_duplicate=True),
        Output("docente-login-error", "children"),
        Input("docente-btn-login", "n_clicks"),
        Input("docente-login-password", "n_submit"),
        State("docente-login-usuario", "value"),
        State("docente-login-password", "value"),
        prevent_initial_call=True,
    )
    def procesar_login(n_clicks, n_submit, usuario, password):
        if not n_clicks and not n_submit:
            raise PreventUpdate

        u = (usuario or "").strip()
        p = (password or "").strip()

        if u == DOCENTE_USER and p == DOCENTE_PASS:
            return {"autenticado": True, "usuario": DOCENTE_USER}, ""
        else:
            error_box = html.Div(
                [
                    html.I(className="fa-solid fa-circle-exclamation", style={"marginRight": "8px"}),
                    "Usuario o contraseña incorrectos. Verifique sus credenciales.",
                ],
                style={
                    "color": "#ef4444",
                    "background": "rgba(239, 68, 68, 0.12)",
                    "border": "1px solid #ef4444",
                    "borderRadius": "8px",
                    "padding": "10px 14px",
                    "fontSize": "13px",
                    "marginTop": "10px",
                },
            )
            return no_update, error_box

    # 3. Procesamiento de cierre de sesión
    @app.callback(
        Output("docente-auth-store", "data", allow_duplicate=True),
        Input("docente-btn-logout", "n_clicks"),
        prevent_initial_call=True,
    )
    def procesar_logout(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return {"autenticado": False, "usuario": None}

    # 4. Gráficas analíticas (Rendimiento por módulo y distribución)
    @app.callback(
        Output("docente-grafico-modulos", "figure"),
        Output("docente-grafico-distribucion", "figure"),
        Input("docente-filtro-modulo", "value"),
    )
    def actualizar_graficas(filtro):
        df = _cargar_datos_estudiantes()

        if df.empty:
            # Gráfica vacía cuando aún no hay registros
            fig_bar = go.Figure()
            fig_bar.add_annotation(
                text="No hay actividades registradas todavía.<br>Los datos se generarán conforme los estudiantes completen talleres y quizzes.",
                showarrow=False,
                font=dict(color=THEME["text_muted"], size=13),
                xref="paper", yref="paper", x=0.5, y=0.5,
            )
            _estilo_figura(fig_bar)

            fig_hist = go.Figure()
            fig_hist.add_annotation(
                text="Sin calificaciones para mostrar.<br>Esperando primeras entregas de los estudiantes.",
                showarrow=False,
                font=dict(color=THEME["text_muted"], size=13),
                xref="paper", yref="paper", x=0.5, y=0.5,
            )
            _estilo_figura(fig_hist)
            return fig_bar, fig_hist

        # Si hay datos reales registrados:
        promedios = df.groupby("modulo")["puntaje"].agg(["mean", "count"]).reset_index()
        colores_map = {
            "Rayos X": THEME["accent_amber"],
            "MRI": THEME["accent_purple"],
            "CT": THEME["accent_cyan"],
            "Señales": "#3b82f6",
            "Casos": "#10b981",
        }
        colores = [colores_map.get(m, THEME["accent_cyan"]) for m in promedios["modulo"]]

        fig_bar = go.Figure(
            go.Bar(
                x=promedios["modulo"],
                y=promedios["mean"],
                text=[f"{v:.1f}% ({c} ent.)" for v, c in zip(promedios["mean"], promedios["count"])],
                textposition="auto",
                marker=dict(color=colores, line=dict(color="rgba(255,255,255,0.15)", width=1)),
                hovertemplate="<b>Módulo:</b> %{x}<br><b>Promedio:</b> %{y:.1f}%<extra></extra>",
            )
        )
        fig_bar.add_hline(y=70, line_dash="dash", line_color="#ef4444", annotation_text="Límite Aprobación (70%)", annotation_position="bottom right")
        _estilo_figura(fig_bar)
        fig_bar.update_yaxes(range=[0, 105], title_text="Promedio (%)")

        # Histograma de distribución de calificaciones
        fig_hist = go.Figure(
            go.Histogram(
                x=df["puntaje"],
                nbinsx=10,
                marker=dict(color="rgba(168, 85, 247, 0.7)", line=dict(color="#a855f7", width=1.5)),
                hovertemplate="Rango: %{x} pts<br>Cantidad de estudiantes: %{y}<extra></extra>",
            )
        )
        _estilo_figura(fig_hist)
        fig_hist.update_xaxes(range=[40, 105], title_text="Calificación Obtenida")
        fig_hist.update_yaxes(title_text="Frecuencia (Estudiantes)")

        return fig_bar, fig_hist

    # 5. Tabla interactiva con filtros
    @app.callback(
        Output("docente-tabla-contenedor", "children"),
        Input("docente-filtro-nombre", "value"),
        Input("docente-filtro-modulo", "value"),
    )
    def renderizar_tabla(busqueda, filtro_modulo):
        df = _cargar_datos_estudiantes()

        if df.empty:
            return html.Div(
                [
                    html.I(className="fa-solid fa-folder-open", style={"fontSize": "38px", "color": THEME["text_muted"], "marginBottom": "12px"}),
                    html.H4("No hay registros de actividades o evaluaciones aún", style={"color": THEME["text"], "margin": "0 0 6px 0", "fontSize": "15px", "fontWeight": "600"}),
                    html.P("Los registros aparecerán aquí automáticamente en tiempo real a medida que los estudiantes completen talleres y quizzes en los módulos de la plataforma.", style={"color": THEME["text_muted"], "fontSize": "13px", "maxWidth": "480px", "margin": "0 auto", "lineHeight": "1.5"}),
                ],
                style={"textAlign": "center", "padding": "40px 20px"},
            )

        if filtro_modulo and filtro_modulo != "TODOS":
            df = df[df["modulo"] == filtro_modulo]
        if busqueda and busqueda.strip():
            b = busqueda.strip().lower()
            df = df[df["nombre"].str.lower().str.contains(b)]

        if df.empty:
            return html.Div(
                [
                    html.I(className="fa-solid fa-inbox", style={"fontSize": "32px", "color": THEME["text_muted"], "marginBottom": "10px"}),
                    html.P("No se encontraron registros que coincidan con la búsqueda.", style={"color": THEME["text_muted"], "fontSize": "13px"}),
                ],
                style={"textAlign": "center", "padding": "30px"},
            )

        filas = []
        for _, row in df.iterrows():
            ptje = float(row["puntaje"])
            if ptje >= 85:
                badge_bg, badge_col, badge_txt = "rgba(16,185,129,0.15)", "#10b981", "Excelente"
            elif ptje >= 70:
                badge_bg, badge_col, badge_txt = "rgba(56,189,248,0.15)", THEME["accent_cyan"], "Aprobado"
            else:
                badge_bg, badge_col, badge_txt = "rgba(239,68,68,0.15)", "#ef4444", "Refuerzo"

            filas.append(
                html.Tr(
                    [
                        html.Td(row["nombre"], style={"padding": "12px 14px", "fontWeight": "600", "color": THEME["text"]}),
                        html.Td(row["actividad"], style={"padding": "12px 14px", "color": THEME["text"]}),
                        html.Td(row["modulo"], style={"padding": "12px 14px", "color": THEME["text_muted"]}),
                        html.Td(row["fecha"], style={"padding": "12px 14px", "color": THEME["text_muted"], "fontSize": "12px"}),
                        html.Td(f"{ptje:.1f} / 100", style={"padding": "12px 14px", "fontWeight": "700", "color": THEME["text"]}),
                        html.Td(
                            html.Span(
                                badge_txt,
                                style={
                                    "background": badge_bg,
                                    "color": badge_col,
                                    "padding": "4px 10px",
                                    "borderRadius": "12px",
                                    "fontSize": "11.5px",
                                    "fontWeight": "700",
                                },
                            ),
                            style={"padding": "12px 14px"},
                        ),
                    ],
                    style={"borderBottom": f"1px solid {THEME['card_border']}"},
                )
            )

        encabezados = ["Estudiante", "Actividad / Taller", "Módulo", "Fecha", "Puntaje", "Estado"]
        return html.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th(h, style={"padding": "12px 14px", "textAlign": "left", "color": THEME["text_muted"], "fontSize": "12px", "fontWeight": "700", "textTransform": "uppercase"})
                            for h in encabezados
                        ]
                    ),
                    style={"background": "rgba(255, 255, 255, 0.03)", "borderBottom": f"1px solid {THEME['border']}"},
                ),
                html.Tbody(filas),
            ],
            style={"width": "100%", "borderCollapse": "collapse", "fontSize": "13px"},
        )

    # 6. Exportar datos a CSV
    @app.callback(
        Output("docente-descargar-csv", "data"),
        Input("docente-btn-exportar", "n_clicks"),
        prevent_initial_call=True,
    )
    def exportar_csv(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        df = _cargar_datos_estudiantes()
        return dcc.send_data_frame(df.to_csv, filename=f"reporte_notas_prometeo_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", index=False)

    # 7. Asistente Pedagógico con Gemini
    @app.callback(
        Output("docente-resumen-ia", "children"),
        Input("docente-btn-generar-gemini", "n_clicks"),
        prevent_initial_call=True,
    )
    def generar_plan_docente_ia(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        df = _cargar_datos_estudiantes()

        if df.empty:
            return html.Div(
                [
                    html.I(className="fa-solid fa-circle-info", style={"color": THEME["accent_cyan"], "marginRight": "8px"}),
                    "Actualmente no existen evaluaciones registradas en el sistema. Una vez que la cohorte comience a realizar actividades en la plataforma, podrás solicitar aquí un análisis pedagógico del desempeño y recomendaciones de refuerzo para tu clase.",
                ],
                style={"background": "rgba(56, 189, 248, 0.08)", "borderRadius": "10px", "padding": "14px 18px", "border": f"1px solid {THEME['card_border']}", "color": THEME["text"], "fontSize": "13.5px"},
            )

        promedios = df.groupby("modulo")["puntaje"].mean().to_dict()
        prompt = (
            f"Actúa como un asesor pedagógico universitario en Bioingeniería y Física Médica. "
            f"Analiza el desempeño de la cohorte actual de estudiantes en la plataforma Prometeo:\n"
            f"Promedios por módulo: {promedios}\n"
            f"El módulo con menor desempeño es '{min(promedios, key=promedios.get)}'.\n"
            f"Genera una breve recomendación didáctica para el profesor que incluya:\n"
            f"1. Diagnóstico del obstáculo conceptual principal.\n"
            f"2. Estrategia práctica de refuerzo para la próxima clase usando los simuladores interactivos.\n"
            f"3. Una pregunta detonante para abrir discusión en el aula.\n"
            f"Sé conciso, directo y estructurado (máximo 160 palabras)."
        )
        respuesta = gemini_service.generar_texto(prompt, usar_cache=True)
        return html.Div(
            [
                html.Div(
                    [
                        html.I(className="fa-solid fa-graduation-cap", style={"color": THEME["accent_cyan"], "marginRight": "8px"}),
                        html.Strong("Recomendación Didáctica de la IA:", style={"color": THEME["accent_cyan"]}),
                    ],
                    style={"marginBottom": "8px"},
                ),
                html.Div(respuesta, style={"whiteSpace": "pre-line", "color": THEME["text"]}),
            ],
            style={"background": "rgba(56, 189, 248, 0.08)", "borderRadius": "10px", "padding": "16px 20px", "border": f"1px solid {THEME['accent_cyan']}"},
        )
