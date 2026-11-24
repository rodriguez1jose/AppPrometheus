# apps/imaging/casos.py
# =============================================================================
# PROMETEO — Módulo de Casos Clínicos Interactivos (Problem-Based Learning)
# =============================================================================
from __future__ import annotations

import numpy as np
from dash import dcc, html, Input, Output, State, ctx, no_update
from dash.exceptions import PreventUpdate

from config import THEME, STYLE_CARD, STYLE_SECTION_TITLE, STYLE_LABEL, STYLE_CONTAINER
from services.gemini_service import gemini_service
from apps.mri_modulos import fantoma as F
from apps.mri_modulos import figuras as FG

# =============================================================================
# DEFINICIÓN DE CASOS CLÍNICOS EDUCATIVOS
# =============================================================================
CASOS = {
    "ictus": {
        "titulo": "Caso 1: Déficit Neurológico Súbito (Sospecha de Ictus Isquémico)",
        "escenario": "ictus",
        "edad_sexo": "Hombre de 64 años",
        "tiempo_evolucion": "90 minutos (Ventana terapéutica aguda)",
        "motivo": "Paresia súbita braquio-crural derecha y afasia motora mientras desayunaba.",
        "pregunta_clinica": "¿Qué secuencia permite diagnosticar la isquemia en fase hiperaguda (restricción a la difusión de agua)?",
        "secuencias_disponibles": ["DWI", "ADC", "T2", "FLAIR", "T1"],
        "secuencia_recomendada": "DWI",
        "hallazgo_clave": (
            "En la secuencia DWI (Difusión) se observa un área hiperintensa focal fronto-parietal izquierda con caída "
            "correspondiente en el mapa ADC (restricción por edema citotóxico intracelular). El mismatch DWI-FLAIR positivo "
            "confirma que la lesión tiene menos de 4.5 horas de evolución, haciendo al paciente candidato a trombólisis o trombectomía."
        ),
        "pregunta_evaluacion": "¿Cuál es la causa biofísica de la hiperintensidad observada en la secuencia DWI en el tejido isquémico?",
        "opciones": [
            "Rotura de la barrera hematoencefálica con extravasación de contraste",
            "Falla de las bombas Na+/K+ ATPasa con edema citotóxico y restricción del movimiento browniano del agua",
            "Aumento masivo del tiempo de relajación T1 por pérdida de mielina",
            "Disminución de la susceptibilidad magnética por exceso de oxihemoglobina"
        ],
        "respuesta_correcta": 1,
        "explicacion": "Al fallar el aporte de oxígeno y glucosa, las bombas dependientes de ATP fallan; el agua se acumula dentro de las neuronas (edema citotóxico), reduciendo el espacio extracelular y restringiendo la difusión molecular libre del agua (hiperintensidad en DWI y baja señal en ADC)."
    },
    "tumor": {
        "titulo": "Caso 2: Cefalea Matutina y Crisis Epiléptica (Masa Cerebral)",
        "escenario": "tumor",
        "edad_sexo": "Mujer de 48 años",
        "tiempo_evolucion": "3 semanas de evolución progresiva",
        "motivo": "Cefalea progresiva más intensa al despertar, náuseas matutinas y primera crisis convulsiva focal.",
        "pregunta_clinica": "¿Qué combinación de secuencias permite distinguir el tumor sólido infiltrante del edema vasogénico periférico?",
        "secuencias_disponibles": ["T1C", "T1", "T2", "FLAIR"],
        "secuencia_recomendada": "T1C",
        "hallazgo_clave": (
            "En T1 post-contraste (T1C) se aprecia un realce anular irregular que marca la pared tumoral activa con rotura de barrera "
            "hematoencefálica y centro necrótico. En T2-FLAIR se evidencia el halo hiperintenso periférico correspondiente al edema "
            "vasogénico extracelular con efecto de masa sobre los ventrículos."
        ),
        "pregunta_evaluacion": "¿Por qué el tumor realza intensamente en la secuencia T1 tras administrar el agente de contraste a base de Gadolinio?",
        "opciones": [
            "Porque el Gadolinio disminuye drásticamente el tiempo de relajación T1 de los protones adyacentes",
            "Porque el Gadolinio bloquea los gradientes de selección de corte",
            "Porque el tumor absorbe fotones por efecto Compton intensificado",
            "Porque el Gadolinio alarga el tiempo T2 haciendo que brille en eco de espín"
        ],
        "respuesta_correcta": 0,
        "explicacion": "El Gadolinio es una sustancia paramagnética que acelera la relajación longitudinal de los protones de agua cercanos, acortando su T1 y generando una señal brillante (hiperintensa) en imágenes ponderadas en T1."
    },
    "em": {
        "titulo": "Caso 3: Visión Borrosa y Parestesias (Sospecha de Esclerosis Múltiple)",
        "escenario": "em",
        "edad_sexo": "Mujer de 28 años",
        "tiempo_evolucion": "Episodio actual de 5 días de evolución",
        "motivo": "Disminución de agudeza visual en ojo izquierdo y debilidad transitoria en extremidades inferiores.",
        "pregunta_clinica": "¿Qué secuencia es el estándar de oro para detectar placas desmielinizantes periventriculares sin interferencia del LCR?",
        "secuencias_disponibles": ["FLAIR", "T2", "STIR", "T1"],
        "secuencia_recomendada": "FLAIR",
        "hallazgo_clave": (
            "La secuencia T2-FLAIR atenúa la señal brillante del líquido cefalorraquídeo ventricular mediante un pulso de inversión "
            "(TI ≈ 2400 ms), permitiendo visualizar con alto contraste las placas hiperintensas periventriculares perpendiculares "
            "al eje ventricular (Dedos de Dawson), características de desmielinización inflamatoria."
        ),
        "pregunta_evaluacion": "¿Cuál es la función del Tiempo de Inversión (TI) en la secuencia T2-FLAIR para este diagnóstico?",
        "opciones": [
            "Maximizar la atenuación de rayos X en el hueso craneal",
            "Hacer coincidir el tiempo de muestreo con el paso por cero (nulling) de la magnetización longitudinal del LCR",
            "Aumentar el ángulo de Ernst para adquirir cortes ultra-rápidos",
            "Inducir resonancia en los átomos de fósforo de la mielina"
        ],
        "respuesta_correcta": 1,
        "explicacion": "En FLAIR (Fluid Attenuated Inversion Recovery), el TI se ajusta exactamente al tiempo en que la curva de recuperación T1 del LCR cruza el valor cero ($TI = T1 \\ln 2$), anulando su señal para que las lesiones adyacentes a los ventrículos resalten."
    },
    "atrofia": {
        "titulo": "Caso 4: Deterioro Cognitivo y Pérdida de Memoria (Neurodegeneración)",
        "escenario": "atrofia",
        "edad_sexo": "Hombre de 76 años",
        "tiempo_evolucion": "18 meses de evolución insidiosa",
        "motivo": "Pérdida progresiva de memoria a corto plazo, desorientación espacial y dificultad en actividades complejas.",
        "pregunta_clinica": "¿Qué hallazgo volumétrico en las secuencias ponderadas en T1 y T2 orienta a pérdida de masa cortical?",
        "secuencias_disponibles": ["T1", "T2", "FLAIR", "PD"],
        "secuencia_recomendada": "T1",
        "hallazgo_clave": (
            "En la secuencia T1 y T2 se observa un marcado ensanchamiento de los surcos corticales, adelgazamiento de las circunvoluciones "
            "fronto-temporales y aumento compensatorio del volumen de los ventrículos laterales (hidrocefalia ex-vacuo por pérdida de parénquima cerebral)."
        ),
        "pregunta_evaluacion": "¿Qué diferencia una hidrocefalia ex-vacuo de una hidrocefalia comunicante obstructiva en imagenología?",
        "opciones": [
            "En la hidrocefalia ex-vacuo la dilatación ventricular es secundaria a la pérdida de tejido cerebral, sin hipertensión intracraneal",
            "En la hidrocefalia ex-vacuo el LCR tiene tiempo T1 muy corto similar a la grasa",
            "En la obstructiva los surcos cerebrales están muy ensanchados y profundos",
            "No hay diferencias radiológicas entre ambas entidades"
        ],
        "respuesta_correcta": 0,
        "explicacion": "La hidrocefalia ex-vacuo es un fenómeno pasivo: el espacio que deja la pérdida de sustancia blanca y gris es ocupado por líquido cefalorraquídeo sin que exista un bloqueo dinámico de su circulación."
    }
}

# =============================================================================
# LAYOUT DE LA VISTA DE CASOS CLÍNICOS
# =============================================================================
def casos_layout():
    primer_caso = "ictus"
    c_info = CASOS[primer_caso]

    return html.Div(
        [
            # Header del módulo
            html.Div(
                [
                    html.Div(
                        [
                            html.I(className="fa-solid fa-user-doctor", style={"fontSize": "26px", "color": "#10b981", "marginRight": "12px"}),
                            html.Span("APRENDIZAJE BASADO EN PROBLEMAS", style={"fontSize": "12px", "letterSpacing": "2px", "fontWeight": "700", "color": "#10b981"}),
                        ],
                        style={"display": "flex", "alignItems": "center", "marginBottom": "8px"},
                    ),
                    html.H1("Casos Clínicos y Retos Diagnósticos", style={"fontSize": "28px", "fontWeight": "800", "color": THEME["text"], "margin": "0 0 8px 0"}),
                    html.P(
                        "Analiza viñetas médicas reales, selecciona las secuencias diagnósticas adecuadas y correlaciona la biofísica con la patología.",
                        style={"color": THEME["text_muted"], "fontSize": "15px", "margin": "0"},
                    ),
                ],
                style={"background": "linear-gradient(135deg, rgba(16,185,129,0.12) 0%, rgba(56,189,248,0.06) 100%)", "padding": "24px 28px", "borderRadius": "16px", "border": f"1px solid {THEME['card_border']}", "marginBottom": "24px"},
            ),

            # Selector de casos clínicos
            html.Div(
                [
                    html.Label("Selecciona un Escenario Clínico:", style={"fontWeight": "700", "color": THEME["text"], "marginBottom": "10px", "display": "block"}),
                    dcc.Dropdown(
                        id="casos-selector-caso",
                        options=[
                            {"label": v["titulo"], "value": k}
                            for k, v in CASOS.items()
                        ],
                        value=primer_caso,
                        clearable=False,
                        style={"color": "#0f172a", "fontWeight": "600"},
                    ),
                ],
                style={**STYLE_CARD, "padding": "18px 24px", "marginBottom": "20px"},
            ),

            # Grid de 2 columnas: [Viñeta y Preguntas] vs [Visor de Imagen]
            html.Div(
                [
                    # Columna Izquierda: Viñeta y Evaluación
                    html.Div(
                        [
                            # Tarjeta Viñeta
                            html.Div(
                                [
                                    html.H3("Ficha del Paciente", style=STYLE_SECTION_TITLE),
                                    html.Div(id="casos-ficha-paciente", children=_render_ficha(c_info)),
                                ],
                                style={**STYLE_CARD, "padding": "22px", "marginBottom": "20px"},
                            ),

                            # Selector de secuencia
                            html.Div(
                                [
                                    html.Label("Secuencia Diagnóstica a Evaluar:", style=STYLE_LABEL),
                                    dcc.RadioItems(
                                        id="casos-selector-secuencia",
                                        options=[{"label": f" {s}", "value": s} for s in c_info["secuencias_disponibles"]],
                                        value=c_info["secuencia_recomendada"],
                                        inline=True,
                                        style={"color": THEME["text"], "display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "14px"},
                                    ),
                                    html.Button(
                                        [html.I(className="fa-solid fa-eye", style={"marginRight": "8px"}), "Revelar Hallazgo Radiológico Clave"],
                                        id="casos-btn-revelar-hallazgo",
                                        n_clicks=0,
                                        style={"background": "rgba(56,189,248,0.12)", "border": f"1px solid {THEME['accent_cyan']}", "color": THEME["accent_cyan"], "padding": "8px 14px", "borderRadius": "8px", "fontWeight": "600", "cursor": "pointer", "fontSize": "13px"},
                                    ),
                                    html.Div(id="casos-box-hallazgo", style={"display": "none", "marginTop": "14px"}),
                                ],
                                style={**STYLE_CARD, "padding": "22px", "marginBottom": "20px"},
                            ),

                            # Pregunta de Razonamiento Clínico
                            html.Div(
                                [
                                    html.H3("Desafío de Comprensión", style=STYLE_SECTION_TITLE),
                                    html.Div(id="casos-pregunta-texto", children=c_info["pregunta_evaluacion"], style={"color": THEME["text"], "fontWeight": "600", "marginBottom": "14px", "fontSize": "14px"}),
                                    dcc.RadioItems(
                                        id="casos-opciones-respuesta",
                                        options=[{"label": f" {op}", "value": i} for i, op in enumerate(c_info["opciones"])],
                                        style={"color": THEME["text"], "display": "flex", "flexDirection": "column", "gap": "10px", "fontSize": "13px"},
                                    ),
                                    html.Button(
                                        [html.I(className="fa-solid fa-check", style={"marginRight": "8px"}), "Verificar Respuesta"],
                                        id="casos-btn-verificar-quiz",
                                        n_clicks=0,
                                        style={"marginTop": "16px", "background": "#10b981", "border": "none", "color": "#ffffff", "padding": "9px 18px", "borderRadius": "8px", "fontWeight": "700", "cursor": "pointer"},
                                    ),
                                    html.Div(id="casos-resultado-quiz", style={"marginTop": "14px"}),
                                ],
                                style={**STYLE_CARD, "padding": "22px"},
                            ),
                        ],
                        style={"flex": "1", "minWidth": "320px"},
                    ),

                    # Columna Derecha: Visor de Imagen Diagnóstica
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H3("Exploración Axial de Neuroimagen", style={**STYLE_SECTION_TITLE, "margin": "0"}),
                                            html.Span(id="casos-badge-secuencia", children=c_info["secuencia_recomendada"], style={"background": "rgba(16,185,129,0.18)", "color": "#10b981", "padding": "4px 10px", "borderRadius": "12px", "fontSize": "12px", "fontWeight": "700"}),
                                        ],
                                        style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "12px"},
                                    ),
                                    dcc.Graph(id="casos-grafico-imagen", style={"height": "420px"}),
                                    html.Div(
                                        "Interactúa con la imagen: usa zoom y pan para inspeccionar los surcos, ventrículos o zonas focales de lesión.",
                                        style={"fontSize": "12px", "color": THEME["text_muted"], "textAlign": "center", "marginTop": "8px"},
                                    ),
                                ],
                                style={**STYLE_CARD, "padding": "20px"},
                            ),

                            # Botón de consulta clínica con Gemini
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.I(className="fa-solid fa-wand-magic-sparkles", style={"color": THEME["accent_cyan"], "marginRight": "8px"}),
                                            html.Span("Tutor Clínico Gemini", style={"fontWeight": "700", "color": THEME["text"]}),
                                        ],
                                        style={"marginBottom": "8px"},
                                    ),
                                    html.P("¿Tienes dudas sobre los criterios diagnósticos o la fisiopatología de este caso?", style={"fontSize": "12px", "color": THEME["text_muted"], "margin": "0 0 10px 0"}),
                                    dcc.Input(id="casos-input-gemini", placeholder="Ej.: ¿Qué ventana de tiempo existe para la trombólisis en este paciente?", style={"width": "100%", "padding": "8px 12px", "borderRadius": "8px", "border": f"1px solid {THEME['card_border']}", "background": "rgba(255,255,255,0.05)", "color": THEME["text"], "marginBottom": "10px", "boxSizing": "border-box"}),
                                    html.Button([html.I(className="fa-solid fa-paper-plane", style={"marginRight": "6px"}), "Consultar al Tutor Clínico"], id="casos-btn-gemini", n_clicks=0, style={"background": "rgba(56,189,248,0.15)", "border": f"1px solid {THEME['accent_cyan']}", "color": THEME["accent_cyan"], "padding": "7px 14px", "borderRadius": "8px", "fontWeight": "600", "cursor": "pointer", "fontSize": "12px"}),
                                    html.Div(id="casos-respuesta-gemini", style={"marginTop": "12px", "fontSize": "13px", "lineHeight": "1.6"}),
                                ],
                                style={**STYLE_CARD, "padding": "20px", "marginTop": "20px"},
                            ),
                        ],
                        style={"flex": "1.1", "minWidth": "340px"},
                    ),
                ],
                style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
            ),
        ],
        style={"marginTop": "8px"},
    )


def _render_ficha(caso):
    return html.Div(
        [
            html.Div([html.Strong("Paciente: "), html.Span(caso["edad_sexo"], style={"color": THEME["accent_cyan"]})], style={"marginBottom": "6px", "fontSize": "13px"}),
            html.Div([html.Strong("Tiempo de evolución: "), html.Span(caso["tiempo_evolucion"], style={"color": THEME["accent_amber"]})], style={"marginBottom": "6px", "fontSize": "13px"}),
            html.Div([html.Strong("Motivo de consulta: "), html.Span(caso["motivo"])], style={"marginBottom": "10px", "fontSize": "13px", "lineHeight": "1.5"}),
            html.Div([html.Strong("Objetivo: "), html.Span(caso["pregunta_clinica"], style={"fontStyle": "italic", "color": THEME["text"]})], style={"fontSize": "13px", "background": "rgba(255,255,255,0.03)", "padding": "8px 12px", "borderRadius": "8px"}),
        ]
    )


# =============================================================================
# REGISTRO DE CALLBACKS
# =============================================================================
def register_callbacks(app):

    # 1. Actualizar caso seleccionado (Ficha, opciones de secuencia, pregunta)
    @app.callback(
        Output("casos-ficha-paciente", "children"),
        Output("casos-selector-secuencia", "options"),
        Output("casos-selector-secuencia", "value"),
        Output("casos-pregunta-texto", "children"),
        Output("casos-opciones-respuesta", "options"),
        Output("casos-opciones-respuesta", "value"),
        Output("casos-box-hallazgo", "style", allow_duplicate=True),
        Output("casos-resultado-quiz", "children", allow_duplicate=True),
        Output("casos-respuesta-gemini", "children", allow_duplicate=True),
        Input("casos-selector-caso", "value"),
        prevent_initial_call=True,
    )
    def cambiar_caso(caso_id):
        caso = CASOS.get(caso_id, CASOS["ictus"])
        opts_sec = [{"label": f" {s}", "value": s} for s in caso["secuencias_disponibles"]]
        opts_quiz = [{"label": f" {op}", "value": i} for i, op in enumerate(caso["opciones"])]
        return (
            _render_ficha(caso),
            opts_sec,
            caso["secuencia_recomendada"],
            caso["pregunta_evaluacion"],
            opts_quiz,
            None,
            {"display": "none"},
            "",
            "",
        )

    # 2. Renderizar imagen diagnóstica según secuencia
    @app.callback(
        Output("casos-grafico-imagen", "figure"),
        Output("casos-badge-secuencia", "children"),
        Input("casos-selector-caso", "value"),
        Input("casos-selector-secuencia", "value"),
    )
    def renderizar_imagen_caso(caso_id, secuencia):
        caso = CASOS.get(caso_id, CASOS["ictus"])
        secuencia = secuencia or caso["secuencia_recomendada"]
        lab2, mapas = F.corte_axial_parametros(caso["escenario"])
        img_sint = F.sintetizar(mapas, secuencia=secuencia, ruido=0.008)
        fig = FG.imagen(img_sint, titulo=f"Corte Axial — Secuencia {secuencia}", alto=400)
        return fig, f"Secuencia: {secuencia}"

    # 3. Revelar / Ocultar Hallazgo Clave
    @app.callback(
        Output("casos-box-hallazgo", "style", allow_duplicate=True),
        Output("casos-box-hallazgo", "children"),
        Input("casos-btn-revelar-hallazgo", "n_clicks"),
        State("casos-selector-caso", "value"),
        State("casos-box-hallazgo", "style"),
        prevent_initial_call=True,
    )
    def alternar_hallazgo(n_clicks, caso_id, estilo_actual):
        if not n_clicks:
            raise PreventUpdate
        caso = CASOS.get(caso_id, CASOS["ictus"])
        esta_oculto = estilo_actual.get("display") == "none"
        if esta_oculto:
            nuevo_estilo = {"display": "block", "background": "rgba(56,189,248,0.08)", "border": f"1px solid {THEME['accent_cyan']}", "borderRadius": "10px", "padding": "12px 16px", "marginTop": "14px"}
            contenido = [
                html.Div([html.I(className="fa-solid fa-bullseye", style={"color": THEME["accent_cyan"], "marginRight": "8px"}), html.Strong("Reporte del Radiólogo:", style={"color": THEME["accent_cyan"]})], style={"marginBottom": "6px"}),
                html.P(caso["hallazgo_clave"], style={"margin": "0", "fontSize": "13px", "lineHeight": "1.6", "color": THEME["text"]}),
            ]
            return nuevo_estilo, contenido
        return {"display": "none"}, ""

    # 4. Calificar Quiz del Caso
    @app.callback(
        Output("casos-resultado-quiz", "children", allow_duplicate=True),
        Input("casos-btn-verificar-quiz", "n_clicks"),
        State("casos-selector-caso", "value"),
        State("casos-opciones-respuesta", "value"),
        prevent_initial_call=True,
    )
    def calificar_quiz(n_clicks, caso_id, respuesta_elegida):
        if respuesta_elegida is None:
            return html.Div([html.I(className="fa-solid fa-triangle-exclamation", style={"marginRight": "8px"}), "Selecciona una opción para verificar."], style={"color": THEME["accent_amber"], "fontWeight": "600", "fontSize": "13px"})

        caso = CASOS.get(caso_id, CASOS["ictus"])
        if respuesta_elegida == caso["respuesta_correcta"]:
            return html.Div(
                [
                    html.Div([html.I(className="fa-solid fa-circle-check", style={"marginRight": "8px"}), "¡Correcto!"], style={"fontWeight": "700", "color": "#10b981", "fontSize": "14px", "marginBottom": "6px"}),
                    html.P(caso["explicacion"], style={"margin": "0", "fontSize": "13px", "color": THEME["text"], "lineHeight": "1.5"}),
                ],
                style={"background": "rgba(16,185,129,0.12)", "border": "1px solid #10b981", "borderRadius": "8px", "padding": "12px 14px"}
            )
        else:
            return html.Div(
                [
                    html.Div([html.I(className="fa-solid fa-circle-xmark", style={"marginRight": "8px"}), "Respuesta incorrecta."], style={"fontWeight": "700", "color": "#ef4444", "fontSize": "14px", "marginBottom": "6px"}),
                    html.P("Revisa nuevamente la biofísica del tejido o consulta al tutor Gemini para orientar tu razonamiento.", style={"margin": "0", "fontSize": "13px", "color": THEME["text"], "lineHeight": "1.5"}),
                ],
                style={"background": "rgba(239,68,68,0.12)", "border": "1px solid #ef4444", "borderRadius": "8px", "padding": "12px 14px"}
            )

    # 5. Consulta clínica con Gemini
    @app.callback(
        Output("casos-respuesta-gemini", "children", allow_duplicate=True),
        Input("casos-btn-gemini", "n_clicks"),
        State("casos-input-gemini", "value"),
        State("casos-selector-caso", "value"),
        prevent_initial_call=True,
    )
    def consultar_gemini_caso(n_clicks, pregunta, caso_id):
        if not pregunta or not pregunta.strip():
            raise PreventUpdate

        caso = CASOS.get(caso_id, CASOS["ictus"])
        prompt = (
            f"Actúa como un neurorradiólogo y docente clínico. Responde de forma didáctica y concisa a la pregunta del estudiante:\n"
            f"Contexto del caso: {caso['titulo']}\n"
            f"Paciente: {caso['edad_sexo']}. Motivo: {caso['motivo']}\n"
            f"Pregunta del estudiante: {pregunta}\n"
            f"Enfócate en la relación entre la imagen diagnóstica y el razonamiento clínico (máximo 120 palabras)."
        )
        resp = gemini_service.generar_texto(prompt, usar_cache=True)
        return html.Div(
            [
                html.Strong("Tutor Clínico: ", style={"color": THEME["accent_cyan"]}),
                html.Span(resp),
            ],
            style={"background": "rgba(56,189,248,0.08)", "borderRadius": "8px", "padding": "10px 14px", "border": f"1px solid {THEME['card_border']}"}
        )
