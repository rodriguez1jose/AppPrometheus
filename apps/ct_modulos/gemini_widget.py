#gemini_widget.py - ct
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from gemini.asistente import preguntar
from services.gemini_service import gemini_service


# ============================================================
# BURBUJA FLOTANTE DE GEMINI - CT-SIM
# ============================================================

def crear_gemini_widget():

    return html.Div(
        [

            # ------------------------------------------------
            # BOTÓN / BURBUJA FLOTANTE
            # ------------------------------------------------

            html.Button(
                html.I(className="fa-solid fa-wand-magic-sparkles"),
                id="gemini-boton",
                className="gemini-boton",
                title="Abrir asistente Gemini",
            ),

            # ------------------------------------------------
            # VENTANA DEL CHAT
            # ------------------------------------------------

            html.Div(
                [

                    # =================================================
                    # CABECERA
                    # =================================================

                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        html.I(className="fa-solid fa-wand-magic-sparkles"),
                                        className="gemini-logo",
                                    ),

                                    html.Div(
                                        [
                                            html.Div(
                                                "Gemini",
                                                className="gemini-titulo",
                                            ),

                                            html.Div(
                                                "Asistente CT-SIM",
                                                className="gemini-subtitulo",
                                            ),
                                        ]
                                    ),
                                ],
                                className="gemini-header-left",
                            ),

                            html.Button(
                                "×",
                                id="gemini-cerrar",
                                className="gemini-cerrar",
                                title="Cerrar",
                            ),
                        ],
                        className="gemini-header",
                    ),

                    # =================================================
                    # ÁREA DE CONVERSACIÓN
                    # =================================================

                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        html.I(className="fa-solid fa-wand-magic-sparkles"),
                                        className="gemini-avatar",
                                    ),

                                    html.Div(
                                        [
                                            html.Div(
                                                "Hola",
                                                className="gemini-mensaje-titulo",
                                            ),

                                            html.Div(
                                                [
                                                    "Soy el asistente de CT-SIM. "
                                                    "Puedo ayudarte con tomografía, "
                                                    "procesamiento de imágenes, "
                                                    "histogramas, reconstrucción y "
                                                    "los conceptos del proyecto. "
                                                    "También puedo consultar el libro base "
                                                    "y las diapositivas incluidas en Recursos."
                                                ],
                                                className="gemini-mensaje-texto",
                                            ),
                                        ]
                                    ),
                                ],
                                className="gemini-mensaje",
                            )
                        ],
                        id="gemini-conversacion",
                        className="gemini-conversacion",
                    ),

                    # =================================================
                    # SELECTOR DE FUENTE
                    # =================================================

                    html.Div(
                        [
                            html.Label(
                                "Material para consultar",
                                className="gemini-fuente-label",
                            ),

                            dcc.Dropdown(
                                id="gemini-fuente",
                                options=[
                                    {
                                        "label": "Todas las fuentes",
                                        "value": "todas",
                                    },
                                    {
                                        "label": "Libro base",
                                        "value": "libro",
                                    },
                                    {
                                        "label": "Diapositivas",
                                        "value": "diapositivas",
                                    },
                                ],
                                value="todas",
                                clearable=False,
                                searchable=False,
                                className="gemini-fuente-dropdown",
                                style={
                                    "fontSize": "13px",
                                    "color": "#111827",
                                    "marginBottom": "8px",
                                },
                            ),
                        ],
                        className="gemini-fuente-area",
                    ),

                    html.Div(
                        [
                            html.Button(
                                [
                                    html.I(className="fa-solid fa-graduation-cap", style={"marginRight": "6px", "color": "#f59e0b"}),
                                    "Comprobar Entendimiento (Defensa Socrática)",
                                ],
                                id="gemini-btn-socratico",
                                className="gemini-socratico-btn",
                                title="Iniciar una pregunta de defensa de laboratorio",
                                style={
                                    "background": "rgba(245, 158, 11, 0.12)",
                                    "border": "1px solid rgba(245, 158, 11, 0.35)",
                                    "color": "#f59e0b",
                                    "fontSize": "11px",
                                    "fontWeight": "700",
                                    "borderRadius": "8px",
                                    "padding": "6px 12px",
                                    "cursor": "pointer",
                                    "width": "100%",
                                    "marginBottom": "8px",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                },
                            ),
                        ],
                        style={"padding": "0 14px"},
                    ),

                    # =================================================
                    # CAJA DE ESCRITURA
                    # =================================================

                    html.Div(
                        [
                            dcc.Textarea(
                                id="gemini-input",
                                placeholder="Escribe tu pregunta o responde la defensa socrática...",
                                className="gemini-input",
                                rows=2,
                            ),

                            html.Button(
                                html.I(className="fa-solid fa-paper-plane"),
                                id="gemini-enviar",
                                className="gemini-enviar",
                                title="Enviar pregunta",
                            ),
                        ],
                        className="gemini-input-area",
                    ),

                    dcc.Store(id="gemini-modo-socratico", data=False),

                ],
                id="gemini-panel",
                className="gemini-panel oculto",
            ),
        ],
        id="gemini-widget",
        className="gemini-container",
    )


# ============================================================
# CALLBACKS
# ============================================================

def registrar_gemini_callbacks(app):

    # ========================================================
    # ABRIR / CERRAR CHAT
    # ========================================================

    @app.callback(
        Output("gemini-panel", "className"),
        Input("gemini-boton", "n_clicks"),
        Input("gemini-cerrar", "n_clicks"),
        State("gemini-panel", "className"),
        prevent_initial_call=True,
    )
    def alternar_gemini(abrir, cerrar, clase_actual):

        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate

        disparador = ctx.triggered[0]["prop_id"].split(".")[0]

        if disparador == "gemini-boton":

            if not clase_actual:
                clase_actual = "gemini-panel oculto"

            if "oculto" in clase_actual:
                return "gemini-panel"

            return "gemini-panel oculto"

        if disparador == "gemini-cerrar":
            return "gemini-panel oculto"

        raise PreventUpdate


    # ========================================================
    # ENVIAR PREGUNTA O DEFENDER SOCRÁTICAMENTE
    # ========================================================

    @app.callback(
        Output("gemini-conversacion", "children"),
        Output("gemini-input", "value"),
        Output("gemini-modo-socratico", "data"),

        Input("gemini-enviar", "n_clicks"),
        Input("gemini-btn-socratico", "n_clicks"),

        State("gemini-input", "value"),
        State("gemini-conversacion", "children"),
        State("gemini-fuente", "value"),
        State("gemini-modo-socratico", "data"),

        prevent_initial_call=True,
    )
    def gestionar_interaccion_gemini(
        n_enviar,
        n_socratico,
        pregunta,
        conversacion,
        fuente,
        en_modo_socratico,
    ):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        disparador = ctx.triggered[0]["prop_id"].split(".")[0]
        if conversacion is None:
            conversacion = []

        # ----------------------------------------------------
        # 1. Caso: Disparar Reto Socrático
        # ----------------------------------------------------
        if disparador == "gemini-btn-socratico":
            reto = gemini_service.generar_reto_socratico("Tomografía Computarizada")
            mensaje_reto = html.Div(
                [
                    html.Div(
                        [
                            html.I(className="fa-solid fa-graduation-cap", style={"color": "#f59e0b"}),
                            html.Span(" Defensa Socrática", style={"fontWeight": "700", "marginLeft": "6px", "color": "#f59e0b"}),
                        ],
                        className="gemini-avatar",
                        style={"background": "rgba(245,158,11,0.15)", "width": "auto", "padding": "4px 10px", "borderRadius": "12px"}
                    ),
                    html.Div(
                        [
                            html.Div("Evaluador de Laboratorio", className="gemini-mensaje-titulo", style={"color": "#f59e0b"}),
                            html.Div(reto, className="gemini-mensaje-texto"),
                        ]
                    ),
                ],
                className="gemini-mensaje",
                style={"border": "1px solid rgba(245,158,11,0.3)", "borderRadius": "10px", "padding": "10px", "background": "rgba(245,158,11,0.05)"}
            )
            return conversacion + [mensaje_reto], "", True

        # ----------------------------------------------------
        # 2. Caso: Enviar Respuesta o Pregunta Normal
        # ----------------------------------------------------
        if not pregunta or not pregunta.strip():
            raise PreventUpdate

        pregunta = pregunta.strip()
        if not fuente:
            fuente = "todas"

        mensaje_usuario = html.Div(
            [
                html.Div("Tú", className="gemini-mensaje-usuario-titulo"),
                html.Div(pregunta, className="gemini-mensaje-usuario"),
            ],
            className="gemini-mensaje-usuario-contenedor",
        )

        try:
            if en_modo_socratico:
                respuesta = gemini_service.evaluar_defensa_socratica(pregunta, "Tomografía Computarizada")
            else:
                respuesta = preguntar(pregunta, fuente=fuente)
                if not respuesta:
                    respuesta = "No se recibió una respuesta de Gemini. Intenta nuevamente."
        except Exception as error:
            respuesta = f"[ERROR] No se pudo obtener respuesta de Gemini.\n\nDetalle: {error}"

        mensaje_gemini = html.Div(
            [
                html.Div(
                    html.I(className="fa-solid fa-graduation-cap" if en_modo_socratico else "fa-solid fa-wand-magic-sparkles"),
                    className="gemini-avatar",
                ),
                html.Div(
                    [
                        html.Div("Evaluador Socrático" if en_modo_socratico else "Gemini", className="gemini-mensaje-titulo"),
                        html.Div(respuesta, className="gemini-mensaje-texto"),
                    ]
                ),
            ],
            className="gemini-mensaje",
        )

        return conversacion + [mensaje_usuario, mensaje_gemini], "", False
