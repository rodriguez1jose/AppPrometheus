#gemini_widget.py - ct
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from gemini.asistente import preguntar


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

                    # =================================================
                    # CAJA DE ESCRITURA
                    # =================================================

                    html.Div(
                        [
                            dcc.Textarea(
                                id="gemini-input",
                                placeholder="Escribe tu pregunta... Ej.: Según el libro base, ¿qué es la reconstrucción?",
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
    # ENVIAR PREGUNTA
    # ========================================================

    @app.callback(
        Output("gemini-conversacion", "children"),
        Output("gemini-input", "value"),

        Input("gemini-enviar", "n_clicks"),

        State("gemini-input", "value"),
        State("gemini-conversacion", "children"),
        State("gemini-fuente", "value"),

        prevent_initial_call=True,
    )
    def enviar_pregunta(
        n_clicks,
        pregunta,
        conversacion,
        fuente,
    ):

        # ----------------------------------------------------
        # Validar pregunta
        # ----------------------------------------------------

        if not pregunta or not pregunta.strip():
            raise PreventUpdate

        pregunta = pregunta.strip()

        if not fuente:
            fuente = "todas"

        # ----------------------------------------------------
        # Si no existe conversación, crear lista
        # ----------------------------------------------------

        if conversacion is None:
            conversacion = []

        # ----------------------------------------------------
        # Mensaje del estudiante
        # ----------------------------------------------------

        mensaje_usuario = html.Div(
            [
                html.Div(
                    "Tú",
                    className="gemini-mensaje-usuario-titulo",
                ),

                html.Div(
                    pregunta,
                    className="gemini-mensaje-usuario",
                ),
            ],
            className="gemini-mensaje-usuario-contenedor",
        )

        # ----------------------------------------------------
        # Consultar Gemini con recuperación documental
        # ----------------------------------------------------

        try:
            respuesta = preguntar(
                pregunta,
                fuente=fuente,
            )

            if not respuesta:
                respuesta = (
                    "No se recibió una respuesta de Gemini. "
                    "Intenta nuevamente."
                )

        except Exception as error:

            respuesta = (
                "[ERROR] No se pudo obtener una respuesta de Gemini.\n\n"
                f"Detalle: {error}"
            )

        # ----------------------------------------------------
        # Mensaje de Gemini
        # ----------------------------------------------------

        mensaje_gemini = html.Div(
            [
                html.Div(
                    html.I(className="fa-solid fa-wand-magic-sparkles"),
                    className="gemini-avatar",
                ),

                html.Div(
                    [
                        html.Div(
                            "Gemini",
                            className="gemini-mensaje-titulo",
                        ),

                        html.Div(
                            respuesta,
                            className="gemini-mensaje-texto",
                        ),
                    ]
                ),
            ],
            className="gemini-mensaje",
        )

        # ----------------------------------------------------
        # Agregar ambos mensajes al historial
        # ----------------------------------------------------

        nueva_conversacion = conversacion + [
            mensaje_usuario,
            mensaje_gemini,
        ]

        return nueva_conversacion, ""
