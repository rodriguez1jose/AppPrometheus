#app_rx.py
from dash import dcc, html, Input, Output, State, no_update, callback_context, ALL
from config import THEME
from .rx_modulos.interfaz import crear_inicio, detectar_tipo_consulta, crear_sidebar
from .rx_modulos.teoria_rx import mostrar_teoria, registrar_callbacks as registrar_teoria
from .rx_modulos.formacion_imagen import mostrar_formacion
from .rx_modulos.procesamiento import mostrar_procesamiento, registrar_callbacks as registrar_procesamiento
from .rx_modulos.analisis import mostrar_analisis, registrar_callbacks as registrar_analisis
from .rx_modulos.actividades import mostrar_actividades, registrar_callbacks as registrar_actividades
from .rx_modulos.gemini_rx import mostrar_gemini, generar_respuesta_rapida
from .rx_modulos.imagenes_rx import generar_imagen_rx
from .rx_modulos.videos_rx import generar_videos_rx
from .rx_modulos.visuales_rx import generar_visual_rx


def crear_asistente_flotante():
    return html.Div(
        [
            html.Button(
                [
                    html.I(className="fa-solid fa-wand-magic-sparkles", style={"fontSize": "18px", "marginRight": "8px"}),
                    "ASISTENTE IA",
                ],
                id="rx-boton-asistente-ia",
                n_clicks=0,
                style={
                    "position": "fixed", "right": "24px", "bottom": "22px", "zIndex": "1001",
                    "backgroundColor": THEME["accent_purple"], "color": THEME["text"],
                    "border": f"1px solid {THEME['accent_purple']}", "borderRadius": "24px",
                    "padding": "13px 20px", "fontSize": "12px", "fontWeight": "700",
                    "letterSpacing": "1px", "cursor": "pointer", "boxShadow": "0 8px 24px rgba(0,0,0,0.28)",
                },
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(html.I(className="fa-solid fa-wand-magic-sparkles"), style={"fontSize": "18px", "color": THEME["accent_purple"], "marginRight": "10px"}),
                                    html.Div(
                                        [
                                            html.Div("ASISTENTE IA", style={"fontSize": "12px", "fontWeight": "700", "letterSpacing": "1px", "color": THEME["text"]}),
                                            html.Div("Rayos X · Tutor académico", style={"fontSize": "9px", "color": THEME["text_muted"], "marginTop": "3px"}),
                                        ]
                                    ),
                                ],
                                style={"display": "flex", "alignItems": "center"},
                            ),
                            html.Button(
                                html.I(className="fa-solid fa-xmark"),
                                id="rx-cerrar-asistente-ia",
                                n_clicks=0,
                                style={"background": "transparent", "border": "none", "color": THEME["text_muted"], "fontSize": "18px", "cursor": "pointer", "lineHeight": "1"},
                            ),
                        ],
                        style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "padding": "15px 16px", "borderBottom": f"1px solid {THEME['card_border']}"},
                    ),
                    html.Div(
                        id="rx-historial-visible-gemini-flotante",
                        children=html.Div(
                            "Hola, soy tu asistente de IA para Rayos X. ¿Qué quieres aprender?",
                            style={"backgroundColor": THEME["bg"], "color": THEME["text"], "borderRadius": "10px", "padding": "11px 12px", "fontSize": "12px", "lineHeight": "1.5"},
                        ),
                        style={"flex": "1", "overflowY": "auto", "padding": "14px", "display": "flex", "flexDirection": "column", "gap": "9px"},
                    ),
                    html.Div(
                        [
                            dcc.Textarea(
                                id="rx-input-pregunta-gemini-flotante",
                                placeholder="Escribe tu pregunta...",
                                style={"width": "100%", "height": "58px", "resize": "none", "boxSizing": "border-box", "backgroundColor": THEME["bg"], "color": THEME["text"], "border": f"1px solid {THEME['card_border']}", "borderRadius": "9px", "padding": "9px 10px", "fontSize": "12px"},
                            ),
                            html.Button(
                                "Preguntar →",
                                id="rx-btn-consultar-gemini-flotante",
                                n_clicks=0,
                                style={"width": "100%", "marginTop": "8px", "backgroundColor": THEME["accent_purple"], "color": THEME["text"], "border": "none", "borderRadius": "8px", "padding": "10px", "fontSize": "12px", "fontWeight": "700", "letterSpacing": "0.8px", "cursor": "pointer"},
                            ),
                        ],
                        style={"padding": "12px 14px 14px 14px", "borderTop": f"1px solid {THEME['card_border']}"},
                    ),
                    dcc.Store(id="rx-historial-gemini-flotante", data=[]),
                ],
                id="rx-ventana-asistente-ia",
                style={
                    "display": "none", "position": "fixed", "right": "24px", "bottom": "76px", "width": "360px", "height": "470px", "zIndex": "1000",
                    "backgroundColor": THEME["card"], "border": f"1px solid {THEME['card_border']}", "borderRadius": "15px", "boxShadow": "0 18px 50px rgba(0,0,0,0.38)", "overflow": "hidden", "flexDirection": "column",
                },
            ),
        ]
    )


def renderizar_respuesta(respuesta):
    if isinstance(respuesta, dict):
        if respuesta.get("tipo") == "imagen":
            return html.Img(src=respuesta.get("contenido"), style={"width": "100%", "maxWidth": "700px", "borderRadius": "10px", "marginTop": "10px"})
        if respuesta.get("tipo") == "texto":
            return respuesta.get("contenido", "")
    return respuesta


def layout(pathname="/imaging/rx"):
    ruta = pathname.rstrip("/") if pathname else "/imaging/rx"
    if not ruta.startswith("/imaging/rx"):
        ruta = "/imaging/rx"
        
    routes = {
        "/imaging/rx": crear_inicio,
        "/imaging/rx/fundamentos": mostrar_teoria,
        "/imaging/rx/produccion": mostrar_teoria,
        "/imaging/rx/formacion": mostrar_formacion,
        "/imaging/rx/detectores": mostrar_formacion,
        "/imaging/rx/procesamiento": mostrar_procesamiento,
        "/imaging/rx/analisis": mostrar_analisis,
        "/imaging/rx/gemini": mostrar_gemini,
        "/imaging/rx/actividades": mostrar_actividades,
    }
    vista_fn = routes.get(ruta, crear_inicio)
    contenido = vista_fn()

    return html.Div(
        [
            crear_sidebar(pathname=ruta),
            
            # Contenido de la subpágina actual
            html.Div(
                contenido,
                id="rx-pagina-actual",
                style={"flex": "1", "minWidth": "0", "padding": "0"}
            ),
            
            html.Div(id="rx-asistente-flotante-contenedor", children=crear_asistente_flotante()),
            dcc.Store(id="rx-contexto-gemini", data=None),
            dcc.Store(id="rx-histograma-contexto", data=None),
        ],
        style={"display": "flex", "backgroundColor": THEME["bg"], "minHeight": "100vh"}
    )


def register_callbacks(app):
    registrar_teoria(app)
    registrar_procesamiento(app)
    registrar_analisis(app)
    registrar_actividades(app)

    # 1. Callback del Asistente (Abrir/Cerrar)
    @app.callback(
        Output("rx-ventana-asistente-ia", "style"),
        Input("rx-boton-asistente-ia", "n_clicks"),
        Input("rx-cerrar-asistente-ia", "n_clicks"),
        prevent_initial_call=True,
    )
    def alternar_asistente(abrir, cerrar):
        if not callback_context.triggered:
            return no_update
        disparador = callback_context.triggered[0]["prop_id"].split(".")[0]
        if disparador == "rx-boton-asistente-ia":
            return {
                "display": "flex", "position": "fixed", "right": "24px", "bottom": "76px",
                "width": "360px", "height": "470px", "zIndex": "1000",
                "backgroundColor": THEME["card"], "border": f"1px solid {THEME['card_border']}",
                "borderRadius": "15px", "boxShadow": "0 18px 50px rgba(0,0,0,0.38)",
                "overflow": "hidden", "flexDirection": "column",
            }
        return {"display": "none"}

    # 4. Callback del Asistente (Consultar)
    @app.callback(
        Output("rx-historial-visible-gemini-flotante", "children"),
        Output("rx-historial-gemini-flotante", "data"),
        Input("rx-btn-consultar-gemini-flotante", "n_clicks"),
        State("rx-input-pregunta-gemini-flotante", "value"),
        State("rx-historial-gemini-flotante", "data"),
        State("rx-contexto-gemini", "data"),
        prevent_initial_call=True,
    )
    def consultar_asistente_flotante(n_clicks, pregunta, historial, contexto_rx):
        if not pregunta or not pregunta.strip():
            return no_update, no_update
        if historial is None:
            historial = []
        
        pregunta = pregunta.strip()
        tipo = detectar_tipo_consulta(pregunta)
        
        if tipo == "imagen":
            respuesta = generar_imagen_rx(pregunta, historial)
            if respuesta.get("ok"):
                respuesta_historial = {"tipo": "imagen", "contenido": "data:image/png;base64," + respuesta["imagen"]}
                respuesta_ui = html.Img(src=respuesta_historial["contenido"], style={"width": "100%", "maxWidth": "700px", "borderRadius": "10px", "marginTop": "10px"})
            else:
                respuesta_historial = {"tipo": "texto", "contenido": respuesta.get("error", "Error generando imagen.")}
                respuesta_ui = respuesta_historial["contenido"]
                
        elif tipo == "video":
            respuesta = generar_videos_rx(pregunta, historial)
            if respuesta.get("ok"):
                links = [html.A(enlace["titulo"], href=enlace["url"], target="_blank", style={"display": "block", "color": THEME["accent_cyan"], "marginBottom": "5px"}) for enlace in respuesta["enlaces"]]
                respuesta_historial = {"tipo": "texto", "contenido": "Aquí tienes algunos videos recomendados:"}
                respuesta_ui = html.Div([html.P("Aquí tienes algunos videos recomendados:"), *links])
            else:
                respuesta_historial = {"tipo": "texto", "contenido": respuesta.get("mensaje", "Error.")}
                respuesta_ui = respuesta_historial["contenido"]
                
        elif tipo == "visual":
            resultado_visual = generar_visual_rx(pregunta, historial)
            if resultado_visual.get("ok"):
                respuesta_historial = {"tipo": "imagen", "contenido": "data:image/png;base64," + resultado_visual["imagen"]}
                respuesta_ui = html.Img(src=respuesta_historial["contenido"], style={"width": "100%", "maxWidth": "700px", "borderRadius": "10px", "marginTop": "10px"})
            else:
                respuesta_historial = {"tipo": "texto", "contenido": resultado_visual.get("error", "Error.")}
                respuesta_ui = respuesta_historial["contenido"]
        else:
            respuesta = generar_respuesta_rapida(pregunta)
            respuesta_historial = {"tipo": "texto", "contenido": str(respuesta)}
            respuesta_ui = str(respuesta)

        nuevo_historial = historial + [{"pregunta": pregunta, "respuesta": respuesta_historial}]
        
        mensajes = []
        for mensaje in nuevo_historial:
            mensajes.append(
                html.Div(
                    [
                        html.Div("Tú", style={"fontSize": "9px", "fontWeight": "700", "color": THEME["accent_purple"], "marginBottom": "4px"}),
                        html.Div(mensaje["pregunta"], style={"fontSize": "12px", "lineHeight": "1.45", "color": THEME["text"], "marginBottom": "8px"}),
                        html.Div("ASISTENTE IA", style={"fontSize": "9px", "fontWeight": "700", "color": THEME["accent_cyan"], "marginBottom": "4px"}),
                        html.Div(renderizar_respuesta(mensaje["respuesta"]), style={"fontSize": "12px", "lineHeight": "1.5", "color": THEME["text"], "whiteSpace": "pre-wrap"}),
                    ],
                    style={"backgroundColor": THEME["bg"], "borderRadius": "10px", "padding": "10px 11px", "borderLeft": f"3px solid {THEME['accent_purple']}"},
                )
            )
        return mensajes, nuevo_historial