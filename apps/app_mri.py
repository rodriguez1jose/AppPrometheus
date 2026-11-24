# apps/app_mri.py
# =============================================================================
# PROMETEO — Módulo de Resonancia Magnética (MRI)
# =============================================================================
# Expone exclusivamente:
#   - layout(pathname=None): Retorna la interfaz con 7 tabs interactivos.
#   - register_callbacks(app): Registra todos los callbacks en la app principal.
# Prefijo único obligatorio: 'mri-' en todos los componentes.
# =============================================================================

from __future__ import annotations
from functools import lru_cache

import numpy as np
from dash import dcc, html, Input, Output, State, ctx, no_update, ALL
from dash.exceptions import PreventUpdate

from config import (
    THEME,
    STYLE_CONTAINER,
    STYLE_CARD,
    STYLE_CALLOUT,
    STYLE_SECTION_TITLE,
    STYLE_LABEL,
    STYLE_GRAPH_DESC,
)
from services.gemini_service import gemini_service
from .mri_modulos import fantoma as F
from .mri_modulos import simulador_fisico as S
from .mri_modulos import figuras as FG
from .mri_modulos.preguntas_quiz import PREGUNTAS, CATEGORIAS

# -----------------------------------------------------------------------------
# ESTILOS LOCALES ARMONIZADOS
# -----------------------------------------------------------------------------
STYLE_TAB_DEFAULT = {
    "backgroundColor": THEME["card"],
    "color": THEME["text_muted"],
    "border": f"1px solid {THEME['card_border']}",
    "padding": "12px 18px",
    "fontWeight": "600",
    "borderRadius": "8px 8px 0 0",
    "fontSize": "14px",
}

STYLE_TAB_SELECTED = {
    "backgroundColor": "#1e293b",
    "color": THEME["accent_purple"],
    "borderTop": f"3px solid {THEME['accent_purple']}",
    "borderLeft": f"1px solid {THEME['card_border']}",
    "borderRight": f"1px solid {THEME['card_border']}",
    "borderBottom": "none",
    "fontWeight": "700",
    "padding": "12px 18px",
    "borderRadius": "8px 8px 0 0",
    "fontSize": "14px",
}

STYLE_BTN_ACCENT = {
    "backgroundColor": THEME["accent_purple"],
    "color": "#ffffff",
    "border": "none",
    "borderRadius": "8px",
    "padding": "8px 16px",
    "fontWeight": "600",
    "cursor": "pointer",
    "transition": "opacity 0.2s",
}

STYLE_BTN_SECONDARY = {
    "backgroundColor": "#1e293b",
    "color": THEME["text"],
    "border": f"1px solid {THEME['card_border']}",
    "borderRadius": "8px",
    "padding": "6px 14px",
    "fontWeight": "500",
    "cursor": "pointer",
    "marginRight": "6px",
    "marginBottom": "6px",
}

STYLE_KPI = {
    "backgroundColor": "#0a0f1d",
    "border": f"1px solid {THEME['card_border']}",
    "borderRadius": "10px",
    "padding": "10px 14px",
    "marginBottom": "10px",
}

STYLE_CALC_INPUT = {
    "width": "100%",
    "backgroundColor": "#0a0f1d",
    "color": "#ffffff",
    "border": f"1px solid {THEME['card_border']}",
    "borderRadius": "8px",
    "padding": "8px 12px",
    "fontSize": "14px",
    "marginBottom": "10px",
    "boxSizing": "border-box",
}


# -----------------------------------------------------------------------------
# PASOS DE FÍSICA GUIADA (9 PASOS DE RESONA)
# -----------------------------------------------------------------------------
PASOS_FISICA = [
    {
        "t": "1. El Equipo: Superconductividad y Campo B₀",
        "img": "/assets/img/d_escaner.png",
        "img_extra": "/assets/img/esr/componentes_iman.jpg",
        "extra_titulo": "Arquitectura Interna del Imán y Criostato de Helio Líquido",
        "txt": (
            "Un resonador es un electroimán gigantesco: bobinas superconductoras de niobio-titanio "
            "enfriadas con **helio líquido a −269 °C (4 K)** generan un campo magnético principal $B_0$ "
            "de 1,5 o 3 tesla (≈ 30 000–60 000 veces el campo magnético terrestre) permanentemente activo.\n\n"
            "Concéntricamente aloja las **bobinas de homogeneización (*shim*)**, las **bobinas de gradiente** "
            "(que generan los impulsos auditivos característicos al conmutar) y la **bobina de radiofrecuencia (RF)**."
        ),
    },
    {
        "t": "2. Protones de Hidrógeno: Espines Biológicos",
        "img": "/assets/img/d_espines.png",
        "img_extra": "/assets/img/esr/bobinas_recepcion.jpg",
        "extra_titulo": "Arreglo de Bobinas de Recepción Anatómicas Multicanal",
        "txt": (
            "El cuerpo humano está compuesto mayoritariamente por agua y grasa, ricas en núcleos de hidrógeno (¹H). "
            "Cada protón posee **momento angular intrínseco (espín)** y momento dipolar magnético $\\vec{\\mu}$.\n\n"
            "En ausencia de campo externo se orientan al azar. Dentro de $B_0$ adoptan estados cuánticos de energía: "
            "**paralelo** (menor energía) o **antiparalelo** (mayor energía). El exceso térmico de Boltzmann a 1,5 T "
            "es de unos **5 protones por cada millón**, suficiente para crear la **magnetización neta macroscópica $M_0$**."
        ),
    },
    {
        "t": "3. Fenómeno de Precesión y Ecuación de Larmor",
        "img": "/assets/img/d_precesion.png",
        "img_extra": "/assets/img/d_bloch.png",
        "extra_titulo": "Marco Rotatorio y Frecuencia Angular de Resonancia",
        "txt": (
            "Bajo el momento de torsión ejercido por $B_0$, los espines precesan alrededor del eje longitudinal $z$ "
            "a la **frecuencia de Larmor**:\n\n"
            "$$\\omega_0 = \\gamma B_0 \\quad \\Longrightarrow \\quad f_0 = \\frac{\\gamma}{2\\pi} B_0 = 42{,}577\\ \\text{MHz/T} \\times B_0$$\n\n"
            "A **1,5 T** la frecuencia es **63,87 MHz** y a **3,0 T** es **127,74 MHz** (espectro de ondas de radio VHF)."
        ),
    },
    {
        "t": "4. Excitación por Radiofrecuencia (Pulso B₁)",
        "img": "/assets/img/d_excitacion.png",
        "img_extra": "/assets/img/d_inversion.png",
        "extra_titulo": "Pulsos de Radiofrecuencia e Inversión Angular de Fase",
        "txt": (
            "Para perturbar el equilibrio se emite un campo oscilante $B_1(t)$ exactamente a la frecuencia de Larmor "
            "(resonancia). Los espines absorben energía y entran en **coherencia de fase**.\n\n"
            "El vector $\\vec{M}$ se inclina un ángulo $\\alpha = \\gamma \\int B_1(t) dt$. Un pulso de **90°** abate "
            "toda la magnetización hacia el plano transversal $(x', y')$, transformando $M_z$ en $M_{xy}$."
        ),
    },
    {
        "t": "5. Detección de Señal: La FID (Free Induction Decay)",
        "img": "/assets/img/d_fid.png",
        "img_extra": "/assets/img/esr/curvas_te_tr.jpg",
        "extra_titulo": "Decaimiento Temporal de Señal Inducida en la Bobina",
        "txt": (
            "La magnetización transversal $M_{xy}$ rota en el plano transversal a la frecuencia de Larmor. Por la **Ley de "
            "Inducción de Faraday**, el flujo magnético oscilante induce microvoltios en la bobina receptora: es la señal **FID**.\n\n"
            "La señal decae rápidamente a medida que los espines pierden coherencia de fase entre sí."
        ),
    },
    {
        "t": "6. Relajación Longitudinal T₁ y Transversal T₂",
        "img": "/assets/img/d_relajacion.png",
        "img_extra": "/assets/img/esr/curvas_te_tr.jpg",
        "extra_titulo": "Cinética Biofísica de Recuperación T1 vs Decaimiento T2",
        "txt": (
            "Tras la excitación ocurren dos procesos biofísicos simultáneos e independientes:\n\n"
            "- **Relajación T₁ (espín-red):** Recuperación longitudinal de $M_z(t) = M_0(1 - e^{-t/T_1})$. "
            "La grasa recupera rápido (T₁ ≈ 260 ms); el LCR es lento (T₁ ≈ 4000 ms).\n"
            "- **Relajación T₂ (espín-espín):** Decaimiento transversal $M_{xy}(t) = M_0 e^{-t/T_2}$ por interacción molecular irreversible.\n"
            "- **Decaimiento T₂*:** Pérdida acelerada por inhomogeneidades de campo: $\\frac{1}{T_2^*} = \\frac{1}{T_2} + \\frac{1}{T_2'}$."
        ),
    },
    {
        "t": "7. Codificación Espacial mediante Gradientes",
        "img": "/assets/img/d_gradientes.png",
        "img_extra": "/assets/img/esr/seleccion_corte.jpg",
        "extra_titulo": "Selección de Rebanada y Gradientes Ortogonales (Gz, Gy, Gx)",
        "txt": (
            "Para localizar el origen espacial de la señal se superponen campos lineales magnéticos (gradientes):\n\n"
            "1. **Selección de corte ($G_z$):** Excitación sintonizada a un plano anatómico específico.\n"
            "2. **Codificación de fase ($G_y$):** Desfase lineal de espines dependiente de su coordenada en $y$.\n"
            "3. **Codificación de frecuencia ($G_x$):** Muestreo en lectura donde cada columna emite a una frecuencia única."
        ),
    },
    {
        "t": "8. Espacio K y Reconstrucción por Transformada de Fourier",
        "img": "/assets/img/d_espacio_k.png",
        "img_extra": "/assets/img/esr/espacio_k_real.jpg",
        "extra_titulo": "Matriz Raw Data Digitalizada en Frecuencias Espaciales",
        "txt": (
            "Las muestras digitalizadas se ordenan en una matriz bidimensional de frecuencias espaciales: el **Espacio K**.\n\n"
            "- Las frecuencias bajas en el **centro** contienen la mayor parte de la energía y determinan el **contraste y la SNR**.\n"
            "- Las frecuencias altas en la **periferia** codifican la **resolución espacial y los bordes finos**.\n\n"
            "La imagen anatómica se reconstruye aplicando la **Transformada Inversa de Fourier 2D (iFFT2)**."
        ),
    },
    {
        "t": "9. Contraste Tisular y Patología",
        "img": "/assets/img/d_contrastes.png",
        "img_extra": "/assets/img/d_patologias.png",
        "extra_titulo": "Espectro Clínico Patológico y Discriminación Tisular",
        "txt": (
            "Ajustando los tiempos de adquisición se discrimina patología cerebral:\n\n"
            "- **T₁:** Anatomía pura, grasa brillante, corteza cerebral bien definida.\n"
            "- **T₂:** Líquido brillante; edema y lesiones hiperintensas.\n"
            "- **FLAIR:** Supresión selectiva de la señal del LCR para desenmascarar placas periventriculares.\n"
            "- **Difusión (DWI):** Diagnóstico precoz del ictus isquémico por restricción citotóxica del agua."
        ),
    },
]


# =============================================================================
# LAYOUT PRINCIPAL DEL MÓDULO MRI
# =============================================================================
def layout(pathname: str | None = None):
    return html.Div(
        [
            # Header del Módulo
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                "MÓDULO DE IMAGENOLOGÍA MÉDICA",
                                style={
                                    "backgroundColor": "rgba(168, 85, 247, 0.15)",
                                    "color": THEME["accent_purple"],
                                    "padding": "4px 12px",
                                    "borderRadius": "20px",
                                    "fontSize": "11px",
                                    "fontWeight": "700",
                                    "letterSpacing": "1px",
                                    "border": f"1px solid rgba(168, 85, 247, 0.3)",
                                },
                            ),
                            html.H1(
                                "Resonancia Magnética (MRI)",
                                style={
                                    "color": "#ffffff",
                                    "fontSize": "30px",
                                    "fontWeight": "800",
                                    "margin": "10px 0 4px 0",
                                },
                            ),
                            html.Div(
                                "Física cuántica y clásica, espacio K, secuencias de pulsos, contraste tisular y simulación interactiva.",
                                style={"color": THEME["text_muted"], "fontSize": "14px"},
                            ),
                        ]
                    ),
                ],
                style={"marginBottom": "20px"},
            ),

            # Pestañas Principales (7 Tabs)
            dcc.Tabs(
                id="mri-tabs-principal",
                value="mri-tab-inicio",
                style={"marginBottom": "20px"},
                children=[
                    dcc.Tab(label="Inicio", value="mri-tab-inicio", style=STYLE_TAB_DEFAULT, selected_style=STYLE_TAB_SELECTED),
                    dcc.Tab(label="Física", value="mri-tab-fisica", style=STYLE_TAB_DEFAULT, selected_style=STYLE_TAB_SELECTED),
                    dcc.Tab(label="Secuencias", value="mri-tab-secuencias", style=STYLE_TAB_DEFAULT, selected_style=STYLE_TAB_SELECTED),
                    dcc.Tab(label="Espacio K", value="mri-tab-kspace", style=STYLE_TAB_DEFAULT, selected_style=STYLE_TAB_SELECTED),
                    dcc.Tab(label="Contraste", value="mri-tab-contraste", style=STYLE_TAB_DEFAULT, selected_style=STYLE_TAB_SELECTED),
                    dcc.Tab(label="Simulador", value="mri-tab-simulador", style=STYLE_TAB_DEFAULT, selected_style=STYLE_TAB_SELECTED),
                    dcc.Tab(label="Actividades & IA", value="mri-tab-actividades", style=STYLE_TAB_DEFAULT, selected_style=STYLE_TAB_SELECTED),
                ],
            ),

            # Contenedor dinámico del Tab activo
            html.Div(id="mri-tab-content"),

            # Store de estado para persistencia interna
            dcc.Store(id="mri-quiz-idx", data=0),
            dcc.Store(id="mri-quiz-puntaje", data={"aciertos": 0, "respondidas": 0}),
            dcc.Store(id="mri-fisica-paso-actual", data=0),
        ]
    )


# -----------------------------------------------------------------------------
# TAB 1: INICIO
# -----------------------------------------------------------------------------
def render_tab_inicio():
    tarjetas_info = [
        ("fa-solid fa-atom", "Física Nuclear", "Espín nuclear, frecuencia de Larmor, magnetización macroscópica y relajación T1/T2."),
        ("fa-solid fa-clock", "Secuencias de Pulsos", "Spin Echo, Gradient Echo, Inversion Recovery, secuencias ultrarrápidas EPI y difusión."),
        ("fa-solid fa-globe", "Espacio K y Fourier", "Codificación espacial 2D, filtrado en frecuencia, artefactos clínicos y reconstrucción iFFT2."),
        ("fa-solid fa-palette", "Contraste Tisular", "Sustancia blanca, gris, LCR y lesiones cerebrales sintetizadas con fantoma digital en tiempo real."),
        ("fa-solid fa-magnet", "Simulador 3D de Bloch", "Ecuaciones diferenciales del vector de magnetización, dephasing de isocromatas y calculadoras."),
        ("fa-solid fa-robot", "Tutor IA y Evaluación", "Quiz interactivo categorizado y tutor inteligente con Gemini para resolver dudas formativas."),
    ]
    return html.Div(
        [
            html.Div(
                style={**STYLE_CARD, "marginBottom": "20px"},
                children=[
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2("Bienvenido al Módulo de Resonancia Magnética", style=STYLE_SECTION_TITLE),
                                    html.P(
                                        "La Resonancia Magnética (RM) es la modalidad de imagen médica diagnóstica de mayor resolución de contraste tisular. "
                                        "A diferencia de los Rayos X y la Tomografía Computarizada, no utiliza radiación ionizante, sino la interacción entre "
                                        "potentes campos magnéticos estáticos, pulsos de radiofrecuencia en resonancia con los núcleos de hidrógeno y gradientes espaciales.",
                                        style={"color": THEME["text"], "fontSize": "15px", "lineHeight": "1.6"},
                                    ),
                                    html.Div(
                                        style=STYLE_CALLOUT,
                                        children=[
                                            html.Strong("Objetivo de Aprendizaje: "),
                                            "Dominar desde los fundamentos cuánticos del protón y la precesión de Larmor, hasta la formación de imagen en el espacio K "
                                            "y la interpretación cuantitativa del contraste patológico cerebral.",
                                        ],
                                    ),
                                ],
                                style={"flex": "1 1 500px"},
                            ),
                            html.Div(
                                html.Img(
                                    src="/assets/img/hero_cerebro.png",
                                    style={
                                        "maxWidth": "100%",
                                        "maxHeight": "240px",
                                        "objectFit": "cover",
                                        "borderRadius": "12px",
                                        "border": f"1px solid {THEME['card_border']}",
                                        "boxShadow": "0 6px 18px rgba(0,0,0,0.35)",
                                    },
                                ),
                                style={"flex": "1 1 380px", "textAlign": "center"},
                            ),
                        ],
                        style={"display": "flex", "gap": "24px", "alignItems": "center", "flexWrap": "wrap"},
                    ),
                ],
            ),
            html.Div(
                [
                    html.Div(
                        style={**STYLE_CARD, "flex": "1", "minWidth": "280px"},
                        children=[
                            html.H3([html.I(className=icon, style={"marginRight": "8px"}), t], style={"fontSize": "17px", "color": THEME["accent_purple"], "marginBottom": "6px"}),
                            html.P(d, style={"color": THEME["text_muted"], "fontSize": "13px", "margin": "0"}),
                        ],
                    )
                    for icon, t, d in tarjetas_info
                ],
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))", "gap": "16px"},
            ),
        ]
    )


# -----------------------------------------------------------------------------
# TAB 2: FÍSICA
# -----------------------------------------------------------------------------
def render_tab_fisica(paso_idx: int = 0):
    total = len(PASOS_FISICA)
    idx = max(0, min(paso_idx, total - 1))
    paso = PASOS_FISICA[idx]

    img_extra_elem = None
    if paso.get("img_extra"):
        img_extra_elem = html.Div(
            [
                html.Div(
                    [
                        html.I(className="fa-solid fa-microscope", style={"marginRight": "8px", "color": THEME["accent_cyan"]}),
                        paso.get("extra_titulo", "Referencia Visual Complementaria"),
                    ],
                    style={"color": THEME["accent_cyan"], "fontSize": "13px", "fontWeight": "700", "margin": "14px 0 6px 0"},
                ),
                html.Img(
                    src=paso["img_extra"],
                    style={
                        "maxWidth": "100%",
                        "maxHeight": "240px",
                        "objectFit": "contain",
                        "borderRadius": "10px",
                        "border": f"1px solid {THEME['card_border']}",
                        "backgroundColor": "#0a0f1d",
                        "boxShadow": "0 4px 12px rgba(0,0,0,0.3)",
                    },
                ),
            ],
            style={"marginTop": "10px", "textAlign": "center"},
        )

    return html.Div(
        [
            html.Div(
                style=STYLE_CARD,
                children=[
                    html.Div(
                        [
                            html.H2(paso["t"], style={**STYLE_SECTION_TITLE, "borderBottom": "none", "margin": "0"}),
                            html.Div(
                                f"Paso {idx + 1} de {total}",
                                style={"color": THEME["accent_purple"], "fontWeight": "700", "fontSize": "14px"},
                            ),
                        ],
                        style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "16px"},
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Img(
                                        src=paso["img"],
                                        style={
                                            "width": "100%",
                                            "maxWidth": "720px",
                                            "maxHeight": "480px",
                                            "objectFit": "contain",
                                            "borderRadius": "12px",
                                            "border": f"1px solid {THEME['card_border']}",
                                            "backgroundColor": "#0a0f1d",
                                            "boxShadow": "0 6px 18px rgba(0,0,0,0.35)",
                                        },
                                    ),
                                    img_extra_elem,
                                ],
                                style={"flex": "1 1 540px", "textAlign": "center"},
                            ),
                            html.Div(
                                [
                                    dcc.Markdown(paso["txt"], mathjax=True, style={"color": THEME["text"], "fontSize": "15px", "lineHeight": "1.75"}),
                                ],
                                style={"flex": "1 1 380px"},
                            ),
                        ],
                        style={"display": "flex", "gap": "28px", "flexWrap": "wrap", "alignItems": "flex-start"},
                    ),
                    html.Hr(style={"borderColor": THEME["card_border"], "margin": "20px 0"}),
                    html.Div(
                        [
                            html.Button(
                                "← Anterior",
                                id="mri-btn-paso-prev",
                                style={**STYLE_BTN_SECONDARY, "opacity": 0.5 if idx == 0 else 1.0},
                                disabled=idx == 0,
                            ),
                            html.Div(
                                [
                                    html.Button(
                                        f"{i + 1}",
                                        id={"type": "mri-btn-paso-directo", "index": i},
                                        style={
                                            **STYLE_BTN_SECONDARY,
                                            "backgroundColor": THEME["accent_purple"] if i == idx else "#1e293b",
                                            "color": "#ffffff" if i == idx else THEME["text_muted"],
                                            "fontWeight": "700" if i == idx else "500",
                                            "padding": "6px 12px",
                                        },
                                    )
                                    for i in range(total)
                                ],
                                style={"display": "flex", "gap": "4px", "flexWrap": "wrap"},
                            ),
                            html.Button(
                                "Siguiente →",
                                id="mri-btn-paso-next",
                                style={**STYLE_BTN_ACCENT, "opacity": 0.5 if idx == total - 1 else 1.0},
                                disabled=idx == total - 1,
                            ),
                        ],
                        style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "flexWrap": "wrap", "gap": "10px"},
                    ),
                ],
            ),
        ]
    )


# -----------------------------------------------------------------------------
# TAB 3: SECUENCIAS
# -----------------------------------------------------------------------------
def render_tab_secuencias():
    return html.Div(
        [
            html.Div(
                [
                    # Columna de controles
                    html.Div(
                        style={**STYLE_CARD, "flex": "1", "maxWidth": "340px"},
                        children=[
                            html.H3("Tipo de Secuencia", style=STYLE_SECTION_TITLE),
                            dcc.Dropdown(
                                id="mri-sq-tipo",
                                options=[
                                    {"label": "Spin Echo (SE)", "value": "SE"},
                                    {"label": "Gradient Echo (GRE)", "value": "GRE"},
                                    {"label": "Inversion Recovery (IR)", "value": "IR"},
                                    {"label": "Echo Planar Imaging (EPI)", "value": "EPI"},
                                    {"label": "Difusión (DWI)", "value": "DWI"},
                                ],
                                value="SE",
                                clearable=False,
                                style={"color": "#000000"},
                            ),

                            html.Label("Tiempo de Eco (TE) [ms]:", style=STYLE_LABEL),
                            html.Div(id="mri-sq-te-txt", style={"color": THEME["accent_cyan"], "fontWeight": "700"}),
                            dcc.Slider(
                                id="mri-sq-te", min=10, max=100, step=2, value=30,
                                marks={10: "10", 30: "30", 50: "50", 75: "75", 100: "100"},
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),

                            html.Label("Tiempo de Repetición (TR) [ms]:", style=STYLE_LABEL),
                            html.Div(id="mri-sq-tr-txt", style={"color": THEME["accent_cyan"], "fontWeight": "700"}),
                            dcc.Slider(
                                id="mri-sq-tr", min=50, max=500, step=25, value=150,
                                marks={50: "50", 150: "150", 300: "300", 500: "500"},
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),

                            html.Label("Tiempo de Inversión (TI) [ms] (sólo IR):", style=STYLE_LABEL),
                            html.Div(id="mri-sq-ti-txt", style={"color": THEME["accent_cyan"], "fontWeight": "700"}),
                            dcc.Slider(
                                id="mri-sq-ti", min=10, max=100, step=5, value=40,
                                marks={10: "10", 40: "40", 70: "70", 100: "100"},
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),

                            html.Label("Tren de Ecos (ETL) (sólo EPI):", style=STYLE_LABEL),
                            html.Div(id="mri-sq-etl-txt", style={"color": THEME["accent_cyan"], "fontWeight": "700"}),
                            dcc.Slider(
                                id="mri-sq-etl", min=4, max=16, step=2, value=8,
                                marks={4: "4", 8: "8", 12: "12", 16: "16"},
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),
                        ],
                    ),

                    # Columna de visualización del cronograma
                    html.Div(
                        style={**STYLE_CARD, "flex": "2"},
                        children=[
                            html.H3("Cronograma Multi-Canal de Pulsos y Gradientes", style=STYLE_SECTION_TITLE),
                            dcc.Loading(dcc.Graph(id="mri-sq-fig", style={"height": "420px"}), type="dot", color=THEME["accent_purple"]),
                            html.Div(id="mri-sq-texto", style={"marginTop": "14px"}),
                        ],
                    ),
                ],
                style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
            ),

            # Material Visual de Apoyo: Diagrama de Secuencias
            html.Div(
                style={**STYLE_CARD, "marginTop": "20px"},
                children=[
                    html.H3(
                        [
                            html.I(className="fa-solid fa-wave-square", style={"marginRight": "8px", "color": THEME["accent_cyan"]}),
                            "Fundamento Visual: Diagrama de Secuencia Spin Echo Canónica",
                        ],
                        style=STYLE_SECTION_TITLE,
                    ),
                    html.Div(
                        [
                            html.Div(
                                html.Img(
                                    src="/assets/img/d_secuencia_se.png",
                                    style={
                                        "width": "100%",
                                        "maxWidth": "720px",
                                        "maxHeight": "440px",
                                        "objectFit": "contain",
                                        "borderRadius": "12px",
                                        "border": f"1px solid {THEME['card_border']}",
                                        "backgroundColor": "#0a0f1d",
                                        "boxShadow": "0 6px 18px rgba(0,0,0,0.35)",
                                    },
                                ),
                                style={"flex": "1 1 520px", "textAlign": "center"},
                            ),
                            html.Div(
                                [
                                    html.H4("Estructura de Pulsos y Gradientes Físicos", style={"color": THEME["accent_cyan"], "marginBottom": "10px", "fontSize": "16px"}),
                                    dcc.Markdown(
                                        "1. **Canal RF:** Pulso de excitación de 90° que abate la magnetización hacia el plano transversal, seguido de un pulso de reenfocado de 180° a $t = TE/2$ para invertir el desfase de los espines.\n"
                                        "2. **Gradiente de Selección de Corte ($G_z$):** Conmutado simultáneamente con los pulsos de RF para delimitar la rebanada anatómica activa junto con un gradiente de refase.\n"
                                        "3. **Gradiente de Codificación de Fase ($G_y$):** Se aplica un escalón distinto en cada ciclo TR para desplazar el muestreo a lo largo de las filas $k_y$.\n"
                                        "4. **Gradiente de Frecuencia/Lectura ($G_x$):** Inicialmente desfasa los espines y luego adquiere la señal mientras los espines se reenfocan en el centro del eco a $t = TE$.\n"
                                        "5. **Canal de Señal:** Detección sincrónica del eco simétrico en la bobina receptora.",
                                        style={"color": THEME["text"], "fontSize": "14px", "lineHeight": "1.75"},
                                    ),
                                ],
                                style={"flex": "1 1 380px"},
                            ),
                        ],
                        style={"display": "flex", "gap": "28px", "alignItems": "center", "flexWrap": "wrap"},
                    ),
                ],
            ),
        ]
    )


# -----------------------------------------------------------------------------
# TAB 4: K-SPACE
# -----------------------------------------------------------------------------
def render_tab_kspace():
    return html.Div(
        [
            html.Div(
                [
                    # Panel de Control
                    html.Div(
                        style={**STYLE_CARD, "flex": "1", "maxWidth": "340px"},
                        children=[
                            html.H3("Operación en Espacio K", style=STYLE_SECTION_TITLE),
                            dcc.RadioItems(
                                id="mri-k-modo-op",
                                options=[
                                    {"label": " Filtro Frecuencial", "value": "filtro"},
                                    {"label": " Muestreo Acelerado", "value": "muestreo"},
                                    {"label": " Artefactos Clínicos", "value": "artefacto"},
                                ],
                                value="filtro",
                                labelStyle={"display": "block", "marginBottom": "8px", "color": THEME["text"]},
                            ),
                            html.Hr(style={"borderColor": THEME["card_border"]}),

                            # Subpanel Filtros
                            html.Div(
                                id="mri-k-panel-filtro",
                                children=[
                                    html.Label("Tipo de Filtro:", style=STYLE_LABEL),
                                    dcc.Dropdown(
                                        id="mri-k-filtro",
                                        options=[{"label": a, "value": b} for a, b in S.FILTROS_K],
                                        value="paso_bajo",
                                        clearable=False,
                                        style={"color": "#000000"},
                                    ),
                                    html.Label("Familia Matemática:", style=STYLE_LABEL),
                                    dcc.Dropdown(
                                        id="mri-k-familia",
                                        options=[
                                            {"label": "Gaussiano (suave sin ripple)", "value": "gaussiano"},
                                            {"label": "Butterworth (corte ajustable)", "value": "butterworth"},
                                            {"label": "Ideal (genera anillado Gibbs)", "value": "ideal"},
                                        ],
                                        value="gaussiano",
                                        clearable=False,
                                        style={"color": "#000000"},
                                    ),
                                    html.Label("Frecuencia de Corte D₀ (%):", style=STYLE_LABEL),
                                    dcc.Slider(
                                        id="mri-k-d0", min=2, max=80, step=2, value=20,
                                        marks={2: "2%", 20: "20%", 40: "40%", 60: "60%", 80: "80%"},
                                        tooltip={"placement": "bottom", "always_visible": False},
                                    ),
                                    html.Label("Ganancia High-Boost:", style=STYLE_LABEL),
                                    dcc.Slider(
                                        id="mri-k-g", min=1.0, max=3.0, step=0.1, value=1.5,
                                        marks={1.0: "1.0", 1.5: "1.5", 2.0: "2.0", 2.5: "2.5", 3.0: "3.0"},
                                        tooltip={"placement": "bottom", "always_visible": False},
                                    ),
                                ],
                            ),

                            # Subpanel Muestreo
                            html.Div(
                                id="mri-k-panel-muestreo",
                                style={"display": "none"},
                                children=[
                                    html.Label("Patrón de Adquisición:", style=STYLE_LABEL),
                                    dcc.Dropdown(
                                        id="mri-k-modo",
                                        options=[
                                            {"label": "Sólo el Centro (bajas frec)", "value": "centro"},
                                            {"label": "Sólo la Periferia (altas frec)", "value": "periferia"},
                                            {"label": "Submuestreo en Fase (factor R)", "value": "submuestreo"},
                                            {"label": "Fourier Parcial (Half-Scan)", "value": "parcial"},
                                            {"label": "Trayectoria Radial", "value": "radial"},
                                            {"label": "Trayectoria Espiral", "value": "espiral"},
                                            {"label": "Aleatorio (Compressed Sensing)", "value": "aleatorio"},
                                        ],
                                        value="centro",
                                        clearable=False,
                                        style={"color": "#000000"},
                                    ),
                                    html.Label("Fracción / Factor R:", style=STYLE_LABEL),
                                    dcc.Slider(
                                        id="mri-k-par", min=0.1, max=0.8, step=0.05, value=0.3,
                                        marks={0.1: "10%", 0.3: "30%", 0.5: "50%", 0.8: "80%"},
                                        tooltip={"placement": "bottom", "always_visible": False},
                                    ),
                                ],
                            ),

                            # Subpanel Artefactos
                            html.Div(
                                id="mri-k-panel-artefacto",
                                style={"display": "none"},
                                children=[
                                    html.Label("Artefacto Clínico:", style=STYLE_LABEL),
                                    dcc.Dropdown(
                                        id="mri-k-art",
                                        options=[
                                            {"label": "Movimiento del Paciente (Ghosting)", "value": "movimiento"},
                                            {"label": "Espiga de RF / Spike (Herringbone)", "value": "spike"},
                                            {"label": "Ruido Térmico de Bobina", "value": "ruido"},
                                            {"label": "Truncamiento de Matriz (Gibbs)", "value": "truncamiento"},
                                            {"label": "Aliasing / Plegamiento FOV", "value": "aliasing"},
                                        ],
                                        value="movimiento",
                                        clearable=False,
                                        style={"color": "#000000"},
                                    ),
                                    html.Label("Severidad del Artefacto:", style=STYLE_LABEL),
                                    dcc.Slider(
                                        id="mri-k-sev", min=0.1, max=1.0, step=0.05, value=0.4,
                                        marks={0.1: "Bajo", 0.4: "Medio", 0.7: "Alto", 1.0: "Máx"},
                                        tooltip={"placement": "bottom", "always_visible": False},
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # Panel de Gráficos (Altura optimizada a 480px)
                    html.Div(
                        style={**STYLE_CARD, "flex": "2"},
                        children=[
                            html.H3("Laboratorio de Espacio K: Entrada → Dominio K → Reconstrucción iFFT2", style=STYLE_SECTION_TITLE),
                            dcc.Loading(dcc.Graph(id="mri-k-fig", style={"height": "480px"}), type="dot", color=THEME["accent_cyan"]),
                            html.Div(id="mri-k-explica", style={"marginTop": "16px"}),
                        ],
                    ),
                ],
                style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
            ),

            # Material Visual de Apoyo: Filtrado en Espacio K
            html.Div(
                style={**STYLE_CARD, "marginTop": "20px"},
                children=[
                    html.H3(
                        [
                            html.I(className="fa-solid fa-chart-area", style={"marginRight": "8px", "color": THEME["accent_purple"]}),
                            "Fundamento Visual: Filtrado en Frecuencia y Distribución Espectral",
                        ],
                        style=STYLE_SECTION_TITLE,
                    ),
                    html.Div(
                        [
                            html.Div(
                                html.Img(
                                    src="/assets/img/d_filtros_frecuencia.png",
                                    style={
                                        "width": "100%",
                                        "maxWidth": "740px",
                                        "maxHeight": "440px",
                                        "objectFit": "contain",
                                        "borderRadius": "12px",
                                        "border": f"1px solid {THEME['card_border']}",
                                        "backgroundColor": "#0a0f1d",
                                        "boxShadow": "0 6px 18px rgba(0,0,0,0.35)",
                                    },
                                ),
                                style={"flex": "1 1 520px", "textAlign": "center"},
                            ),
                            html.Div(
                                [
                                    html.H4("Distribución de Información Frecuencial", style={"color": THEME["accent_purple"], "marginBottom": "10px", "fontSize": "16px"}),
                                    dcc.Markdown(
                                        "- **Centro del Espacio K ($k_x \\approx 0, k_y \\approx 0$):** Contiene las frecuencias espaciales bajas con la mayor potencia espectral. Determina la **relación señal/ruido (SNR)** y el **contraste tisular** general.\n"
                                        "- **Periferia del Espacio K:** Contiene las frecuencias espaciales altas. Codifica las transiciones bruscas de intensidad, definiendo los **bordes anatómicos** y la **resolución espacial** neta.\n"
                                        "- **Filtro Paso Bajo:** Preserva el centro y atenúa la periferia, suavizando la imagen a costa de perder nitidez (anillado de Gibbs en filtros ideales).\n"
                                        "- **Filtro Paso Alto:** Elimina el centro y resalta los contornos anatómicos sin contraste de fondo.\n"
                                        "- **Aceleración (K-Space Submuestreado):** Saltar líneas en fase reduce el tiempo de escaneo pero induce aliasing si no se reconstruye mediante técnicas paralelas (SENSE, GRAPPA).",
                                        style={"color": THEME["text"], "fontSize": "14px", "lineHeight": "1.75"},
                                    ),
                                ],
                                style={"flex": "1 1 380px"},
                            ),
                        ],
                        style={"display": "flex", "gap": "28px", "alignItems": "center", "flexWrap": "wrap"},
                    ),
                ],
            ),
        ]
    )


# -----------------------------------------------------------------------------
# TAB 5: CONTRASTE
# -----------------------------------------------------------------------------
def render_tab_contraste():
    return html.Div(
        [
            html.Div(
                [
                    # Parámetros
                    html.Div(
                        style={**STYLE_CARD, "flex": "1", "maxWidth": "340px"},
                        children=[
                            html.H3("Fantoma y Secuencia", style=STYLE_SECTION_TITLE),
                            html.Label("Escenario Patológico:", style=STYLE_LABEL),
                            dcc.Dropdown(
                                id="mri-sc-esc",
                                options=[{"label": v, "value": k} for k, v in F.ESCENARIOS.items()],
                                value="sano",
                                clearable=False,
                                style={"color": "#000000"},
                            ),

                            html.Label("Tipo de Secuencia:", style=STYLE_LABEL),
                            dcc.RadioItems(
                                id="mri-sc-tipo",
                                options=[
                                    {"label": " Spin Echo", "value": "SE"},
                                    {"label": " Gradient Echo", "value": "GRE"},
                                    {"label": " Inversion Recovery", "value": "IR"},
                                ],
                                value="SE",
                                inline=True,
                                style={"color": THEME["text"], "marginBottom": "10px"},
                            ),

                            html.Label("Presets Rápidos:", style=STYLE_LABEL),
                            html.Div(
                                [
                                    html.Button("T1", id="mri-pre-t1", style=STYLE_BTN_SECONDARY),
                                    html.Button("T2", id="mri-pre-t2", style=STYLE_BTN_SECONDARY),
                                    html.Button("DP", id="mri-pre-dp", style=STYLE_BTN_SECONDARY),
                                    html.Button("FLAIR", id="mri-pre-flair", style=STYLE_BTN_SECONDARY),
                                    html.Button("STIR", id="mri-pre-stir", style=STYLE_BTN_SECONDARY),
                                    html.Button("GRE", id="mri-pre-gre", style=STYLE_BTN_SECONDARY),
                                ],
                                style={"display": "flex", "flexWrap": "wrap", "gap": "4px"},
                            ),

                            html.Label("Tiempo de Repetición (TR) [ms]:", style=STYLE_LABEL),
                            html.Div(id="mri-sc-tr-txt", style={"color": THEME["accent_purple"], "fontWeight": "700"}),
                            dcc.Slider(
                                id="mri-sc-tr", min=50, max=5000, step=50, value=500,
                                marks={50: "50", 1000: "1k", 2500: "2.5k", 5000: "5k"},
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),

                            html.Label("Tiempo de Eco (TE) [ms]:", style=STYLE_LABEL),
                            html.Div(id="mri-sc-te-txt", style={"color": THEME["accent_purple"], "fontWeight": "700"}),
                            dcc.Slider(
                                id="mri-sc-te", min=2, max=200, step=2, value=15,
                                marks={2: "2", 50: "50", 100: "100", 150: "150", 200: "200"},
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),

                            html.Label("Tiempo de Inversión (TI) [ms] (sólo IR):", style=STYLE_LABEL),
                            html.Div(id="mri-sc-ti-txt", style={"color": THEME["accent_purple"], "fontWeight": "700"}),
                            dcc.Slider(
                                id="mri-sc-ti", min=50, max=3000, step=50, value=2400,
                                marks={50: "50", 1000: "1k", 2000: "2k", 3000: "3k"},
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),

                            html.Label("Ángulo α [°] (sólo GRE):", style=STYLE_LABEL),
                            html.Div(id="mri-sc-a-txt", style={"color": THEME["accent_purple"], "fontWeight": "700"}),
                            dcc.Slider(
                                id="mri-sc-a", min=5, max=90, step=5, value=30,
                                marks={5: "5°", 30: "30°", 60: "60°", 90: "90°"},
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),

                            html.Label("Campo B₀:", style=STYLE_LABEL),
                            dcc.RadioItems(
                                id="mri-sc-b0",
                                options=[{"label": " 1.5 Tesla", "value": 1.5}, {"label": " 3.0 Tesla", "value": 3.0}],
                                value=1.5,
                                inline=True,
                                style={"color": THEME["text"]},
                            ),
                        ],
                    ),

                    # Imágenes y Curvas (Imagen ampliada a 460px de alto)
                    html.Div(
                        style={"flex": "2", "display": "flex", "flexDirection": "column", "gap": "20px"},
                        children=[
                            html.Div(
                                style=STYLE_CARD,
                                children=[
                                    html.H3("Corte Axial Sintetizado en Tiempo Real", style=STYLE_SECTION_TITLE),
                                    dcc.Loading(dcc.Graph(id="mri-sc-img", style={"height": "460px"}), type="dot", color=THEME["accent_purple"]),
                                ],
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        style={**STYLE_CARD, "flex": "1"},
                                        children=[
                                            html.H4("Curvas T1 / T2", style=STYLE_SECTION_TITLE),
                                            dcc.Graph(id="mri-sc-curvas", style={"height": "250px"}),
                                        ],
                                    ),
                                    html.Div(
                                        style={**STYLE_CARD, "flex": "1"},
                                        children=[
                                            html.H4("Intensidad por Tejido", style=STYLE_SECTION_TITLE),
                                            dcc.Graph(id="mri-sc-barras", style={"height": "250px"}),
                                        ],
                                    ),
                                ],
                                style={"display": "flex", "gap": "16px", "flexWrap": "wrap"},
                            ),
                            html.Div(id="mri-sc-texto", style=STYLE_CARD),
                        ],
                    ),
                ],
                style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
            ),

            # Material Visual de Apoyo: Ponderaciones Clínicas T1, T2 y DP
            html.Div(
                style={**STYLE_CARD, "marginTop": "20px"},
                children=[
                    html.H3(
                        [
                            html.I(className="fa-solid fa-palette", style={"marginRight": "8px", "color": THEME["accent_cyan"]}),
                            "Fundamento Visual: Matriz de Ponderación Tisular (T1, T2, DP y FLAIR)",
                        ],
                        style=STYLE_SECTION_TITLE,
                    ),
                    html.Div(
                        [
                            html.Div(
                                html.Img(
                                    src="/assets/img/d_contrastes.png",
                                    style={
                                        "width": "100%",
                                        "maxWidth": "780px",
                                        "maxHeight": "400px",
                                        "objectFit": "contain",
                                        "borderRadius": "12px",
                                        "border": f"1px solid {THEME['card_border']}",
                                        "backgroundColor": "#0a0f1d",
                                        "boxShadow": "0 6px 18px rgba(0,0,0,0.35)",
                                    },
                                ),
                                style={"flex": "1 1 540px", "textAlign": "center"},
                            ),
                            html.Div(
                                [
                                    html.H4("Reglas Clínicas del Contraste de Imagen", style={"color": THEME["accent_cyan"], "marginBottom": "10px", "fontSize": "16px"}),
                                    dcc.Markdown(
                                        "- **Ponderación T1 (TR corto ~500 ms, TE corto ~15 ms):** Resalta la rapidez con que los tejidos recuperan su magnetización longitudinal. Grasa hiperintensa (brillante); LCR hipointenso (oscuro). Ideal para anatomía.\n"
                                        "- **Ponderación T2 (TR largo ~4000 ms, TE largo ~100 ms):** Permite el decaimiento transversal de los tejidos. Sustancias con agua libre (LCR, edema tumoral, inflamación) brillan intensamente.\n"
                                        "- **Densidad Protónica DP (TR largo, TE corto):** Minimiza tanto las diferencias T1 como T2, reflejando principalmente la concentración local de protones hidrogenados.\n"
                                        "- **FLAIR (Inversión-Recuperación con TI ≈ 2400 ms):** Aplica un pulso inversor de 180° que pasa por el punto nulo del LCR al momento del pulso de 90°, anulando el brillo del líquido para revelar lesiones periventriculares.",
                                        style={"color": THEME["text"], "fontSize": "14px", "lineHeight": "1.75"},
                                    ),
                                ],
                                style={"flex": "1 1 380px"},
                            ),
                        ],
                        style={"display": "flex", "gap": "28px", "alignItems": "center", "flexWrap": "wrap"},
                    ),
                ],
            ),
        ]
    )


# -----------------------------------------------------------------------------
# TAB 6: SIMULADOR
# -----------------------------------------------------------------------------
def render_tab_simulador():
    return html.Div(
        [
            dcc.Tabs(
                id="mri-sim-subtabs",
                value="mri-subtab-bloch",
                style={"marginBottom": "16px"},
                children=[
                    dcc.Tab(label="Precesión y Excitación (Bloch 3D)", value="mri-subtab-bloch", style=STYLE_TAB_DEFAULT, selected_style=STYLE_TAB_SELECTED),
                    dcc.Tab(label="Isocromatas y Ecos (FID / SE / GRE)", value="mri-subtab-ecos", style=STYLE_TAB_DEFAULT, selected_style=STYLE_TAB_SELECTED),
                    dcc.Tab(label="Calculadoras de Física de RM", value="mri-subtab-calculadoras", style=STYLE_TAB_DEFAULT, selected_style=STYLE_TAB_SELECTED),
                ],
            ),
            html.Div(id="mri-sim-subtab-content", children=render_subtab_bloch()),
        ]
    )


# Subtab A: Bloch
def render_subtab_bloch():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        style={**STYLE_CARD, "flex": "1", "maxWidth": "320px"},
                        children=[
                            html.H3("Parámetros Físicos", style=STYLE_SECTION_TITLE),
                            html.Label("Campo B₀ [T]:", style=STYLE_LABEL),
                            html.Div(id="mri-sb-b0-txt", style={"color": THEME["accent_cyan"], "fontWeight": "700"}),
                            dcc.Slider(
                                id="mri-sb-b0", min=0.5, max=7.0, step=0.1, value=1.5,
                                marks={0.5: "0.5", 1.5: "1.5", 3.0: "3.0", 5.0: "5.0", 7.0: "7.0"},
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),

                            html.Label("Ángulo Flip α [°]:", style=STYLE_LABEL),
                            html.Div(id="mri-sb-alfa-txt", style={"color": THEME["accent_cyan"], "fontWeight": "700"}),
                            dcc.Slider(
                                id="mri-sb-alfa", min=10, max=180, step=10, value=90,
                                marks={10: "10°", 45: "45°", 90: "90°", 135: "135°", 180: "180°"},
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),

                            html.Label("T1 [ms] (Longitudinal):", style=STYLE_LABEL),
                            html.Div(id="mri-sb-t1-txt", style={"color": THEME["accent_cyan"], "fontWeight": "700"}),
                            dcc.Slider(
                                id="mri-sb-t1", min=100, max=3000, step=100, value=800,
                                marks={100: "100", 800: "800", 1500: "1.5k", 2200: "2.2k", 3000: "3k"},
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),

                            html.Label("T2 [ms] (Transversal):", style=STYLE_LABEL),
                            html.Div(id="mri-sb-t2-txt", style={"color": THEME["accent_cyan"], "fontWeight": "700"}),
                            dcc.Slider(
                                id="mri-sb-t2", min=20, max=500, step=10, value=90,
                                marks={20: "20", 90: "90", 200: "200", 350: "350", 500: "500"},
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),

                            html.Label("Desajuste Δf [Hz]:", style=STYLE_LABEL),
                            html.Div(id="mri-sb-df-txt", style={"color": THEME["accent_cyan"], "fontWeight": "700"}),
                            dcc.Slider(
                                id="mri-sb-df", min=0, max=20, step=1, value=5,
                                marks={0: "0", 5: "5", 10: "10", 15: "15", 20: "20"},
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),

                            html.Div(id="mri-sb-kpis", style={"marginTop": "16px"}),
                        ],
                    ),
                    html.Div(
                        style={"flex": "2", "display": "flex", "flexDirection": "column", "gap": "16px"},
                        children=[
                            html.Div(
                                style=STYLE_CARD,
                                children=[
                                    html.H3("Vector de Magnetización M(t) en Marco Rotatorio (3D)", style=STYLE_SECTION_TITLE),
                                    dcc.Loading(dcc.Graph(id="mri-sb-3d", style={"height": "400px"}), type="dot", color=THEME["accent_cyan"]),
                                ],
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        style={**STYLE_CARD, "flex": "1"},
                                        children=[
                                            html.H4("Componentes de M(t)", style=STYLE_SECTION_TITLE),
                                            dcc.Graph(id="mri-sb-comp", style={"height": "250px"}),
                                        ],
                                    ),
                                    html.Div(
                                        style={**STYLE_CARD, "flex": "1"},
                                        children=[
                                            html.H4("Señal FID Detectada", style=STYLE_SECTION_TITLE),
                                            dcc.Graph(id="mri-sb-fid", style={"height": "250px"}),
                                        ],
                                    ),
                                ],
                                style={"display": "flex", "gap": "16px", "flexWrap": "wrap"},
                            ),
                        ],
                    ),
                ],
                style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
            ),

            # Material Visual de Apoyo: Ecuaciones de Bloch
            html.Div(
                style={**STYLE_CARD, "marginTop": "20px"},
                children=[
                    html.H3(
                        [
                            html.I(className="fa-solid fa-compass", style={"marginRight": "8px", "color": THEME["accent_cyan"]}),
                            "Fundamento Visual: Ecuaciones de Bloch y Marco Rotatorio",
                        ],
                        style=STYLE_SECTION_TITLE,
                    ),
                    html.Div(
                        [
                            html.Div(
                                html.Img(
                                    src="/assets/img/d_bloch.png",
                                    style={
                                        "width": "100%",
                                        "maxWidth": "740px",
                                        "maxHeight": "400px",
                                        "objectFit": "contain",
                                        "borderRadius": "12px",
                                        "border": f"1px solid {THEME['card_border']}",
                                        "backgroundColor": "#0a0f1d",
                                        "boxShadow": "0 6px 18px rgba(0,0,0,0.35)",
                                    },
                                ),
                                style={"flex": "1 1 520px", "textAlign": "center"},
                            ),
                            html.Div(
                                [
                                    html.H4("Dinámica Clásica del Vector de Magnetización", style={"color": THEME["accent_purple"], "marginBottom": "10px", "fontSize": "16px"}),
                                    dcc.Markdown(
                                        "Las ecuaciones fenomenológicas propuestas por Felix Bloch describen la trayectoria del vector macroscópico $\\vec{M}(t)$:\n\n"
                                        "$$\\frac{d\\vec{M}}{dt} = \\gamma (\\vec{M} \\times \\vec{B}) - \\frac{M_x \\hat{i} + M_y \\hat{j}}{T_2} - \\frac{(M_z - M_0)\\hat{k}}{T_1}$$\n\n"
                                        "En el **marco de referencia rotatorio** a la frecuencia de Larmor $\\omega_0$, el campo magnético estático $B_0$ se anula efectivamente. Un pulso de RF oscilante $B_1$ se percibe estacionario, inclinando la magnetización neta en un ángulo $\\alpha = \\gamma B_1 \\tau$. Al cesar el pulso, la magnetización transversal decae con $T_2$ y la componente longitudinal se recupera hacia el equilibrio $M_0$ con constante temporal $T_1$.",
                                        mathjax=True,
                                        style={"color": THEME["text"], "fontSize": "14px", "lineHeight": "1.75"},
                                    ),
                                ],
                                style={"flex": "1 1 380px"},
                            ),
                        ],
                        style={"display": "flex", "gap": "28px", "alignItems": "center", "flexWrap": "wrap"},
                    ),
                ],
            ),
        ]
    )


# Subtab B: Ecos
def render_subtab_ecos():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        style={**STYLE_CARD, "flex": "1", "maxWidth": "320px"},
                        children=[
                            html.H3("Experimento de Ecos", style=STYLE_SECTION_TITLE),
                            dcc.RadioItems(
                                id="mri-se-tipo",
                                options=[
                                    {"label": " FID Libre", "value": "FID"},
                                    {"label": " Spin Echo (90°-180°)", "value": "SE"},
                                    {"label": " Gradient Echo (GRE)", "value": "GRE"},
                                ],
                                value="SE",
                                style={"color": THEME["text"], "marginBottom": "12px"},
                            ),
                            html.Label("T2 Verdadero [ms]:", style=STYLE_LABEL),
                            dcc.Slider(
                                id="mri-se-t2", min=20, max=300, step=10, value=100,
                                marks={20: "20", 100: "100", 200: "200", 300: "300"},
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),
                            html.Label("T2' (Inhomogeneidad) [ms]:", style=STYLE_LABEL),
                            dcc.Slider(
                                id="mri-se-t2p", min=5, max=80, step=5, value=20,
                                marks={5: "5", 20: "20", 50: "50", 80: "80"},
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),
                            html.Label("Tiempo de Eco (TE) [ms]:", style=STYLE_LABEL),
                            dcc.Slider(
                                id="mri-se-te", min=20, max=150, step=5, value=60,
                                marks={20: "20", 60: "60", 100: "100", 150: "150"},
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),
                            html.Div(id="mri-se-kpis", style={"marginTop": "14px"}),
                        ],
                    ),
                    html.Div(
                        style={"flex": "2", "display": "flex", "flexDirection": "column", "gap": "16px"},
                        children=[
                            html.Div(
                                style=STYLE_CARD,
                                children=[
                                    html.H3("Evolución de la Magnetización Transversal Neta", style=STYLE_SECTION_TITLE),
                                    dcc.Graph(id="mri-se-curva", style={"height": "280px"}),
                                ],
                            ),
                            html.Div(
                                style=STYLE_CARD,
                                children=[
                                    html.H3("Isocromatas de Espines: Desfase y Reenfocado Polar", style=STYLE_SECTION_TITLE),
                                    dcc.Graph(id="mri-se-polar", style={"height": "260px"}),
                                ],
                            ),
                        ],
                    ),
                ],
                style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
            ),

            # Material Visual de Apoyo: Desfase FID y Reenfocado Spin Echo
            html.Div(
                style={**STYLE_CARD, "marginTop": "20px"},
                children=[
                    html.H3(
                        [
                            html.I(className="fa-solid fa-rotate", style={"marginRight": "8px", "color": THEME["accent_purple"]}),
                            "Fundamento Visual: Caída Libre (FID) y Reenfocado por Pulso de 180°",
                        ],
                        style=STYLE_SECTION_TITLE,
                    ),
                    html.Div(
                        [
                            html.Div(
                                html.Img(
                                    src="/assets/img/d_fid.png",
                                    style={
                                        "width": "100%",
                                        "maxWidth": "740px",
                                        "maxHeight": "380px",
                                        "objectFit": "contain",
                                        "borderRadius": "12px",
                                        "border": f"1px solid {THEME['card_border']}",
                                        "backgroundColor": "#0a0f1d",
                                        "boxShadow": "0 6px 18px rgba(0,0,0,0.35)",
                                    },
                                ),
                                style={"flex": "1 1 520px", "textAlign": "center"},
                            ),
                            html.Div(
                                [
                                    html.H4("Isocromatas y Señal Transversal Neta", style={"color": THEME["accent_cyan"], "marginBottom": "10px", "fontSize": "16px"}),
                                    dcc.Markdown(
                                        "- **Decaimiento FID ($T_2^*$):** Tras el pulso inicial de 90°, las pequeñas heterogeneidades locales del campo magnético hacen que distintos grupos de protones (isocromatas) precesen a frecuencias levemente distintas, provocando un rápido abanico de desfase angular con constante $T_2^*$.\n"
                                        "- **Pulso Reenfocador de 180°:** A $t = TE/2$, se emite un pulso de 180° que 'da la vuelta' a las isocromatas en el plano transversal (análogo a una carrera donde los corredores más rápidos ahora deben volver desde atrás).\n"
                                        "- **Formación del Eco de Espín:** A $t = TE$, todas las isocromatas recuperan exactamente la coherencia de fase, generando una señal de eco medible cuya amplitud depende únicamente del decaimiento biológico molecular irreversible $T_2$.",
                                        style={"color": THEME["text"], "fontSize": "14px", "lineHeight": "1.75"},
                                    ),
                                ],
                                style={"flex": "1 1 380px"},
                            ),
                        ],
                        style={"display": "flex", "gap": "28px", "alignItems": "center", "flexWrap": "wrap"},
                    ),
                ],
            ),
        ]
    )


# Subtab C: Calculadoras
def render_subtab_calculadoras():
    return html.Div(
        [
            # Banner introductorio explicativo
            html.Div(
                style={**STYLE_CARD, "marginBottom": "20px"},
                children=[
                    html.H3(
                        [
                            html.I(className="fa-solid fa-calculator", style={"marginRight": "8px", "color": THEME["accent_cyan"]}),
                            "Calculadoras Físicas y Cuantitativas de Resonancia Magnética",
                        ],
                        style=STYLE_SECTION_TITLE,
                    ),
                    html.P(
                        "Esta suite interactiva permite calcular con rigor biofísico los parámetros que gobiernan la adquisición en RM: "
                        "desde la frecuencia de resonancia nuclear y polarización cuántica de Boltzmann, hasta el espesor geométrico de corte, "
                        "el tiempo total de escaneo y el ángulo de Ernst para máxima relación señal/ruido en secuencias rápidas.",
                        style={"color": THEME["text"], "fontSize": "14px", "lineHeight": "1.6", "margin": "0"},
                    ),
                ],
            ),

            html.Div(
                [
                    # Calculadora 1: Larmor
                    html.Div(
                        style={**STYLE_CARD, "flex": "1", "minWidth": "320px"},
                        children=[
                            html.H4(
                                [
                                    html.I(className="fa-solid fa-atom", style={"marginRight": "8px", "color": THEME["accent_cyan"]}),
                                    "1. Frecuencia de Larmor y Polarización",
                                ],
                                style=STYLE_SECTION_TITLE,
                            ),
                            html.Div(
                                dcc.Markdown("$$f_0 = \\frac{\\gamma}{2\\pi} B_0 = 42.577\\text{ MHz/T} \\times B_0$$", mathjax=True),
                                style={"textAlign": "center", "marginBottom": "12px", "color": THEME["accent_cyan"]},
                            ),
                            html.Label("Presets Clínicos de Campo B₀:", style=STYLE_LABEL),
                            html.Div(
                                [
                                    html.Button("0.55 T (Bajo)", id="mri-pre-b0-055", style=STYLE_BTN_SECONDARY),
                                    html.Button("1.5 T (Clínico)", id="mri-pre-b0-15", style=STYLE_BTN_SECONDARY),
                                    html.Button("3.0 T (Avanzado)", id="mri-pre-b0-30", style=STYLE_BTN_SECONDARY),
                                    html.Button("7.0 T (Ultra)", id="mri-pre-b0-70", style=STYLE_BTN_SECONDARY),
                                ],
                                style={"display": "flex", "gap": "6px", "flexWrap": "wrap", "marginBottom": "12px"},
                            ),
                            html.Label("Campo Magnético Principal B₀ [Tesla]:", style=STYLE_LABEL),
                            dcc.Input(id="mri-cl-b0", type="number", value=1.5, min=0.1, max=11.7, step=0.1, style=STYLE_CALC_INPUT),
                            html.Div(id="mri-cl-out1", style={"marginTop": "14px"}),
                        ],
                    ),

                    # Calculadora 2: Selección de Corte
                    html.Div(
                        style={**STYLE_CARD, "flex": "1", "minWidth": "320px"},
                        children=[
                            html.H4(
                                [
                                    html.I(className="fa-solid fa-layer-group", style={"marginRight": "8px", "color": THEME["accent_purple"]}),
                                    "2. Selección de Corte y Espesor (Δz)",
                                ],
                                style=STYLE_SECTION_TITLE,
                            ),
                            html.Div(
                                dcc.Markdown("$$\\Delta z = \\frac{\\text{BW}_{\\text{RF}}}{\\frac{\\gamma}{2\\pi} \\cdot G_z} = \\frac{\\text{BW [Hz]}}{42.577 \\times G_z\\text{ [mT/m]}}$$", mathjax=True),
                                style={"textAlign": "center", "marginBottom": "12px", "color": THEME["accent_purple"]},
                            ),
                            html.Label("Presets de Espesor Anatómico:", style=STYLE_LABEL),
                            html.Div(
                                [
                                    html.Button("Fino (1.4 mm)", id="mri-pre-corte-fino", style=STYLE_BTN_SECONDARY),
                                    html.Button("Estándar (2.8 mm)", id="mri-pre-corte-estandar", style=STYLE_BTN_SECONDARY),
                                    html.Button("Grueso (5.6 mm)", id="mri-pre-corte-grueso", style=STYLE_BTN_SECONDARY),
                                ],
                                style={"display": "flex", "gap": "6px", "flexWrap": "wrap", "marginBottom": "12px"},
                            ),
                            html.Label("Ancho de Banda del Pulso RF [Hz]:", style=STYLE_LABEL),
                            dcc.Input(id="mri-cl-bw", type="number", value=1200, min=100, max=10000, step=50, style=STYLE_CALC_INPUT),
                            html.Label("Gradiente de Selección Gz [mT/m]:", style=STYLE_LABEL),
                            dcc.Input(id="mri-cl-g", type="number", value=10.0, min=0.5, max=80.0, step=0.5, style=STYLE_CALC_INPUT),
                            html.Div(id="mri-cl-out2", style={"marginTop": "14px"}),
                        ],
                    ),

                    # Calculadora 3: Tiempo de Adquisición
                    html.Div(
                        style={**STYLE_CARD, "flex": "1", "minWidth": "320px"},
                        children=[
                            html.H4(
                                [
                                    html.I(className="fa-solid fa-stopwatch", style={"marginRight": "8px", "color": THEME["accent_cyan"]}),
                                    "3. Tiempo Total de Adquisición (T_scan)",
                                ],
                                style=STYLE_SECTION_TITLE,
                            ),
                            html.Div(
                                dcc.Markdown("$$T_{\\text{scan}} = \\frac{TR \\times N_y \\times \\text{NEX}}{\\text{ETL}}$$", mathjax=True),
                                style={"textAlign": "center", "marginBottom": "12px", "color": THEME["accent_cyan"]},
                            ),
                            html.Label("Presets de Protocolo Clínico:", style=STYLE_LABEL),
                            html.Div(
                                [
                                    html.Button("SE Clásica", id="mri-pre-t-se", style=STYLE_BTN_SECONDARY),
                                    html.Button("Turbo SE (TSE)", id="mri-pre-t-tse", style=STYLE_BTN_SECONDARY),
                                    html.Button("EPI Rápida", id="mri-pre-t-epi", style=STYLE_BTN_SECONDARY),
                                ],
                                style={"display": "flex", "gap": "6px", "flexWrap": "wrap", "marginBottom": "12px"},
                            ),
                            html.Label("Tiempo de Repetición TR [ms]:", style=STYLE_LABEL),
                            dcc.Input(id="mri-cl-tr", type="number", value=500, min=10, max=10000, step=50, style=STYLE_CALC_INPUT),
                            html.Label("Líneas de Matriz en Fase (Ny):", style=STYLE_LABEL),
                            dcc.Input(id="mri-cl-ny", type="number", value=256, min=32, max=1024, step=32, style=STYLE_CALC_INPUT),
                            html.Label("Promedios de Señal (NEX / NSA):", style=STYLE_LABEL),
                            dcc.Input(id="mri-cl-nex", type="number", value=1, min=1, max=16, step=1, style=STYLE_CALC_INPUT),
                            html.Label("Factor Turbo / Tren de Ecos (ETL):", style=STYLE_LABEL),
                            dcc.Input(id="mri-cl-etl", type="number", value=1, min=1, max=64, step=1, style=STYLE_CALC_INPUT),
                            html.Div(id="mri-cl-out3", style={"marginTop": "14px"}),
                        ],
                    ),

                    # Calculadora 4: Ángulo de Ernst
                    html.Div(
                        style={**STYLE_CARD, "flex": "1", "minWidth": "320px"},
                        children=[
                            html.H4(
                                [
                                    html.I(className="fa-solid fa-bolt", style={"marginRight": "8px", "color": THEME["accent_amber"]}),
                                    "4. Ángulo Óptimo de Ernst (GRE)",
                                ],
                                style=STYLE_SECTION_TITLE,
                            ),
                            html.Div(
                                dcc.Markdown("$$\\alpha_E = \\arccos\\left(e^{-TR / T_1}\\right)$$", mathjax=True),
                                style={"textAlign": "center", "marginBottom": "12px", "color": THEME["accent_amber"]},
                            ),
                            html.Label("Presets por Tejido Cerebral:", style=STYLE_LABEL),
                            html.Div(
                                [
                                    html.Button("Grasa (260 ms)", id="mri-pre-e-grasa", style=STYLE_BTN_SECONDARY),
                                    html.Button("Sust. Blanca (800 ms)", id="mri-pre-e-sb", style=STYLE_BTN_SECONDARY),
                                    html.Button("Sust. Gris (1100 ms)", id="mri-pre-e-sg", style=STYLE_BTN_SECONDARY),
                                    html.Button("LCR (4000 ms)", id="mri-pre-e-lcr", style=STYLE_BTN_SECONDARY),
                                ],
                                style={"display": "flex", "gap": "6px", "flexWrap": "wrap", "marginBottom": "12px"},
                            ),
                            html.Label("Tiempo T1 del Tejido [ms]:", style=STYLE_LABEL),
                            dcc.Input(id="mri-cl-t1", type="number", value=800, min=50, max=4000, step=50, style=STYLE_CALC_INPUT),
                            html.Label("Tiempo de Repetición TR [ms]:", style=STYLE_LABEL),
                            dcc.Input(id="mri-cl-tr2", type="number", value=30, min=2, max=500, step=2, style=STYLE_CALC_INPUT),
                            html.Div(id="mri-cl-out4", style={"marginTop": "14px"}),
                        ],
                    ),
                ],
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))", "gap": "20px"},
            ),
        ]
    )


# -----------------------------------------------------------------------------
# TAB 7: ACTIVIDADES & IA
# -----------------------------------------------------------------------------
def render_tab_actividades():
    return html.Div(
        [
            html.Div(
                [
                    # Columna Izquierda: Quiz Interactivo
                    html.Div(
                        style={**STYLE_CARD, "flex": "1.4"},
                        children=[
                            html.Div(
                                [
                                    html.H3([html.I(className="fa-solid fa-pen-to-square", style={"marginRight": "8px"}), "Autoevaluación Interactiva"], style={**STYLE_SECTION_TITLE, "borderBottom": "none", "margin": "0"}),
                                    html.Div(id="mri-quiz-badge-score", style={"color": THEME["accent_purple"], "fontWeight": "700"}),
                                ],
                                style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "14px"},
                            ),
                            html.Label("Filtrar por Categoría:", style=STYLE_LABEL),
                            dcc.Dropdown(
                                id="mri-quiz-categoria",
                                options=[{"label": c, "value": c} for c in CATEGORIAS],
                                value="Todas",
                                clearable=False,
                                style={"color": "#000000", "marginBottom": "14px"},
                            ),

                            # Caja de Pregunta
                            html.Div(id="mri-quiz-pregunta-box"),

                            html.Div(
                                [
                                    html.Button("Comprobar Respuesta", id="mri-quiz-btn-responder", style=STYLE_BTN_ACCENT),
                                    html.Button("Siguiente Pregunta →", id="mri-quiz-btn-siguiente", style=STYLE_BTN_SECONDARY),
                                ],
                                style={"display": "flex", "gap": "10px", "marginTop": "16px"},
                            ),
                            html.Div(id="mri-quiz-feedback", style={"marginTop": "16px"}),
                        ],
                    ),

                    # Columna Derecha: Tutor Inteligente Gemini
                    html.Div(
                        style={**STYLE_CARD, "flex": "1"},
                        children=[
                            html.H3([html.I(className="fa-solid fa-robot", style={"marginRight": "8px"}), "Tutor Pedagógico con IA"], style=STYLE_SECTION_TITLE),
                            html.P(
                                "Consulta cualquier duda conceptual sobre física de RM, artefactos, matemáticas de Fourier o diagnóstico:",
                                style={"color": THEME["text_muted"], "fontSize": "13px"},
                            ),
                            dcc.Textarea(
                                id="mri-ia-prompt",
                                placeholder="Ej: ¿Por qué en secuencias FLAIR el LCR se anula con un TI largo de 2400 ms?",
                                style={
                                    "width": "100%",
                                    "height": "90px",
                                    "backgroundColor": "#0a0f1d",
                                    "color": THEME["text"],
                                    "border": f"1px solid {THEME['card_border']}",
                                    "borderRadius": "8px",
                                    "padding": "10px",
                                    "boxSizing": "border-box",
                                    "fontSize": "13px",
                                },
                            ),
                            html.Button("Consultar al Tutor IA →", id="mri-ia-btn-consultar", style={**STYLE_BTN_ACCENT, "marginTop": "10px", "width": "100%"}),
                            dcc.Loading(
                                html.Div(id="mri-ia-respuesta", style={"marginTop": "16px"}),
                                type="dot",
                                color=THEME["accent_purple"],
                            ),
                        ],
                    ),
                ],
                style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
            )
        ]
    )


# =============================================================================
# HELPER DE LECTURA BASE DE DATOS
# =============================================================================
@lru_cache(maxsize=4)
def _get_baseline_mri_orig():
    lab2, mapas = F.corte_axial_parametros("sano")
    return F.sintetizar(mapas, "T1", ruido=0.005)


# =============================================================================
# REGISTRO DE CALLBACKS MODULARES
# =============================================================================
def register_callbacks(app):

    # 1. Router del Tab Principal
    @app.callback(
        Output("mri-tab-content", "children"),
        Input("mri-tabs-principal", "value"),
    )
    def cambiar_tab_principal(tab_seleccionado):
        if tab_seleccionado == "mri-tab-fisica":
            return render_tab_fisica(0)
        elif tab_seleccionado == "mri-tab-secuencias":
            return render_tab_secuencias()
        elif tab_seleccionado == "mri-tab-kspace":
            return render_tab_kspace()
        elif tab_seleccionado == "mri-tab-contraste":
            return render_tab_contraste()
        elif tab_seleccionado == "mri-tab-simulador":
            return render_tab_simulador()
        elif tab_seleccionado == "mri-tab-actividades":
            return render_tab_actividades()
        return render_tab_inicio()

    # 2. Navegación en Física (Paso a Paso)
    @app.callback(
        Output("mri-tab-content", "children", allow_duplicate=True),
        Output("mri-fisica-paso-actual", "data"),
        Input("mri-btn-paso-prev", "n_clicks"),
        Input("mri-btn-paso-next", "n_clicks"),
        Input({"type": "mri-btn-paso-directo", "index": ALL}, "n_clicks"),
        State("mri-fisica-paso-actual", "data"),
        prevent_initial_call=True,
    )
    def navegar_fisica(n_prev, n_next, clicks_directos, paso_actual):
        trig = ctx.triggered_id
        if trig == "mri-btn-paso-prev":
            paso_actual = max(0, paso_actual - 1)
        elif trig == "mri-btn-paso-next":
            paso_actual = min(len(PASOS_FISICA) - 1, paso_actual + 1)
        elif isinstance(trig, dict) and trig.get("type") == "mri-btn-paso-directo":
            paso_actual = trig.get("index", 0)
        return render_tab_fisica(paso_actual), paso_actual

    # 3. Callbacks de Secuencias de Pulso
    @app.callback(
        Output("mri-sq-fig", "figure"),
        Output("mri-sq-texto", "children"),
        Output("mri-sq-te-txt", "children"),
        Output("mri-sq-tr-txt", "children"),
        Output("mri-sq-ti-txt", "children"),
        Output("mri-sq-etl-txt", "children"),
        Input("mri-sq-tipo", "value"),
        Input("mri-sq-te", "value"),
        Input("mri-sq-tr", "value"),
        Input("mri-sq-ti", "value"),
        Input("mri-sq-etl", "value"),
    )
    def actualizar_secuencias(tipo, TE, TR, TI, etl):
        TE = min(TE, TR)
        canales, notas, fin = S.diagrama_secuencia(tipo=tipo, TE=float(TE), TR=float(TR), TI=float(TI), etl=int(etl))
        fig = FG.diagrama_secuencia(canales, notas, fin, titulo=f"Secuencia {tipo} (TR={TR} ms, TE={TE} ms)")

        explicaciones = {
            "SE": "Secuencia Spin Echo tradicional: Pulso de 90° seguido de un pulso refocalizador de 180° a TE/2 para eliminar inhomogeneidades estáticas (T2').",
            "GRE": "Secuencia Gradient Echo: Pulso de excitación con ángulo α < 90° y gradiente bipolar de lectura. Muy veloz, sensible a susceptibilidad T2*.",
            "IR": "Inversion Recovery: Pulso preparatorio de 180° a tiempo TI para anular un tejido específico según su T1 (p. ej. LCR en FLAIR, grasa en STIR).",
            "EPI": "Echo Planar Imaging: Un solo disparo de RF seguido de oscilación veloz de gradientes de lectura para llenar todo el espacio K en milisegundos.",
            "DWI": "Difusión: Secuencia Spin Echo potenciada con gradientes de Stejskal-Tanner para medir el movimiento browniano microscópico de las moléculas de agua.",
        }
        texto = html.Div(explicaciones.get(tipo, ""), style={"color": THEME["text_muted"], "fontSize": "13px"})
        return fig, texto, f"{TE} ms", f"{TR} ms", f"{TI} ms", f"{etl} ecos"

    # 4. Callbacks de Espacio K
    @app.callback(
        Output("mri-k-panel-filtro", "style"),
        Output("mri-k-panel-muestreo", "style"),
        Output("mri-k-panel-artefacto", "style"),
        Input("mri-k-modo-op", "value"),
    )
    def conmutar_paneles_kspace(modo_op):
        s_filtro = {"display": "block"} if modo_op == "filtro" else {"display": "none"}
        s_muestreo = {"display": "block"} if modo_op == "muestreo" else {"display": "none"}
        s_artefacto = {"display": "block"} if modo_op == "artefacto" else {"display": "none"}
        return s_filtro, s_muestreo, s_artefacto

    @app.callback(
        Output("mri-k-fig", "figure"),
        Output("mri-k-explica", "children"),
        Input("mri-k-modo-op", "value"),
        Input("mri-k-filtro", "value"),
        Input("mri-k-familia", "value"),
        Input("mri-k-d0", "value"),
        Input("mri-k-g", "value"),
        Input("mri-k-modo", "value"),
        Input("mri-k-par", "value"),
        Input("mri-k-art", "value"),
        Input("mri-k-sev", "value"),
    )
    def procesar_kspace(modo_op, filtro, familia, d0, g, modo, par, art, sev):
        img_orig = _get_baseline_mri_orig().copy()

        if modo_op == "filtro":
            H = S.mascara_filtro_k(img_orig.shape, tipo=filtro, familia=familia, frac=d0 / 100.0, ganancia=g)
            rec, k_log = S.filtrar_en_k(img_orig, H)
            titulos = ("1. Imagen Original", "2. Filtro H(kx,ky)", "3. Espacio K Filtrado", "4. Reconstrucción")
            fig = FG.cuadruple([img_orig, H, k_log, rec], titulos)
            expl = html.Div(f"Filtro '{filtro}' ({familia}) con D₀ = {d0}% del radio espectral.", style=STYLE_GRAPH_DESC)
        elif modo_op == "muestreo":
            rec, k_log, mask = S.reconstruir(img_orig, modo=modo, p={"radio": par, "R": int(max(2, 1 / par)), "fraccion": par})
            titulos = ("1. Original", "2. Máscara de Muestreo", "3. Espacio K Submuestreado", "4. Reconstrucción")
            fig = FG.cuadruple([img_orig, mask, k_log, rec], titulos)
            expl = html.Div(f"Patrón de muestreo '{modo}'. Las líneas omitidas alteran el campo de visión o la SNR.", style=STYLE_GRAPH_DESC)
        else:
            rec, k_log, mask = S.reconstruir(img_orig, artefacto=art, pa={"severidad": sev, "amplitud": sev * 5.0, "nivel": sev * 0.01})
            titulos = ("1. Original", "2. Máscara de Adquisición", "3. Espacio K Afectado", "4. Imagen con Artefacto")
            fig = FG.cuadruple([img_orig, mask, k_log, rec], titulos)
            expl = html.Div(f"Artefacto clínico '{art}' simulado con severidad {sev:.2f}.", style=STYLE_GRAPH_DESC)

        return fig, expl

    # 5. Callbacks de Contraste y Fantoma
    PRESETS_CONTRASTE = {
        "mri-pre-t1": ("SE", 500, 15, 2400, 30),
        "mri-pre-t2": ("SE", 4000, 100, 2400, 30),
        "mri-pre-dp": ("SE", 3000, 15, 2400, 30),
        "mri-pre-flair": ("IR", 9000, 120, 2400, 30),
        "mri-pre-stir": ("IR", 4000, 40, 160, 30),
        "mri-pre-gre": ("GRE", 400, 25, 2400, 20),
    }

    @app.callback(
        Output("mri-sc-tipo", "value"),
        Output("mri-sc-tr", "value"),
        Output("mri-sc-te", "value"),
        Output("mri-sc-ti", "value"),
        Output("mri-sc-a", "value"),
        [Input(k, "n_clicks") for k in PRESETS_CONTRASTE],
        prevent_initial_call=True,
    )
    def aplicar_presets_contraste(*_):
        trig = ctx.triggered_id
        if trig in PRESETS_CONTRASTE:
            return PRESETS_CONTRASTE[trig]
        raise PreventUpdate

    @app.callback(
        Output("mri-sc-img", "figure"),
        Output("mri-sc-curvas", "figure"),
        Output("mri-sc-barras", "figure"),
        Output("mri-sc-texto", "children"),
        Output("mri-sc-tr-txt", "children"),
        Output("mri-sc-te-txt", "children"),
        Output("mri-sc-ti-txt", "children"),
        Output("mri-sc-a-txt", "children"),
        Input("mri-sc-esc", "value"),
        Input("mri-sc-tipo", "value"),
        Input("mri-sc-tr", "value"),
        Input("mri-sc-te", "value"),
        Input("mri-sc-ti", "value"),
        Input("mri-sc-a", "value"),
        Input("mri-sc-b0", "value"),
    )
    def actualizar_contraste(esc, tipo, TR, TE, TI, alfa, b0):
        TE = min(TE, TR)
        lab, mapas = F.corte_axial_parametros(esc)
        params = {"tipo": tipo, "TR": float(TR), "TE": float(TE), "TI": float(TI), "alpha": float(alfa)}
        img = F.sintetizar(mapas, params=params)
        fig_img = FG.imagen(img, titulo=f"Fantoma Axial ({F.ESCENARIOS.get(esc, esc)})")

        t1, t2, curvas = S.curvas_relajacion(B0=b0, tmax_t1=max(TR * 1.2, 2000), tmax_t2=max(TE * 2.5, 300))
        ys_curvas = {k: (v["mz"] if tipo != "T2" else v["mxy"], v["color"]) for k, v in curvas.items()}
        fig_curvas = FG.series(t1 if tipo != "T2" else t2, ys_curvas, titulo="Relajación Tisular", xlab="Tiempo [ms]", ylab="Magnetización M(t)/M0")

        res_tej = S.senal_tejidos(tipo, float(TR), float(TE), float(TI), float(alfa), float(b0))
        nombres = list(res_tej.keys())
        valores = [res_tej[k][0] for k in nombres]
        colores = [res_tej[k][1] for k in nombres]
        fig_barras = FG.barras(nombres, valores, colores, titulo="Intensidad de Señal por Tejido", ylab="Señal relativa")

        desc = (
            f"Parámetros activos: {tipo} con TR = {TR} ms, TE = {TE} ms a {b0} T. "
            f"El contraste relativo se define en el instante TE sobre la magnetización recuperada durante TR."
        )
        return fig_img, fig_curvas, fig_barras, desc, f"{TR} ms", f"{TE} ms", f"{TI} ms", f"{alfa}°"

    # 6. Callbacks del Simulador
    @app.callback(
        Output("mri-sim-subtab-content", "children"),
        Input("mri-sim-subtabs", "value"),
    )
    def cambiar_subtab_simulador(subtab):
        if subtab == "mri-subtab-ecos":
            return render_subtab_ecos()
        elif subtab == "mri-subtab-calculadoras":
            return render_subtab_calculadoras()
        return render_subtab_bloch()

    @app.callback(
        Output("mri-sb-3d", "figure"),
        Output("mri-sb-comp", "figure"),
        Output("mri-sb-fid", "figure"),
        Output("mri-sb-kpis", "children"),
        Output("mri-sb-b0-txt", "children"),
        Output("mri-sb-alfa-txt", "children"),
        Output("mri-sb-t1-txt", "children"),
        Output("mri-sb-t2-txt", "children"),
        Output("mri-sb-df-txt", "children"),
        Input("mri-sb-b0", "value"),
        Input("mri-sb-alfa", "value"),
        Input("mri-sb-t1", "value"),
        Input("mri-sb-t2", "value"),
        Input("mri-sb-df", "value"),
    )
    def actualizar_bloch(b0, alfa, t1, t2, df):
        t2 = min(t2, t1)
        t, M = S.bloch_vector(T1=float(t1), T2=float(t2), flip=float(alfa), df=float(df), n=400)
        fig_3d = FG.bloch_3d(M[::2])
        post = t >= 0
        tt, MM = t[post], M[post]

        ys_comp = {
            "Mx'": (MM[:, 0], "#f87171"),
            "My'": (MM[:, 1], "#34d399"),
            "Mz": (MM[:, 2], THEME["accent_purple"]),
            "|Mxy|": (np.hypot(MM[:, 0], MM[:, 1]), THEME["accent_cyan"]),
        }
        fig_comp = FG.series(tt, ys_comp, titulo="Componentes de M(t)", xlab="Tiempo [ms]", ylab="Componente Vectorial")

        ys_fid = {
            "Señal FID (My')": (MM[:, 1], THEME["accent_cyan"]),
            "Envolvente e^(-t/T2)": (np.sin(np.deg2rad(alfa)) * np.exp(-tt / t2), THEME["accent_amber"]),
        }
        fig_fid = FG.series(tt, ys_fid, titulo="Señal Detectada en Bobina", xlab="Tiempo [ms]", ylab="Voltaje Inducido (u.a.)")

        f0 = S.larmor_mhz(b0)
        exceso = S.exceso_spins_ppm(b0)
        kpis = html.Div(
            [
                html.Div([html.Small("Frecuencia Larmor: ", style={"color": THEME["text_muted"]}), html.Strong(f"{f0:.2f} MHz", style={"color": THEME["accent_cyan"]})], style=STYLE_KPI),
                html.Div([html.Small("Exceso de Espines: ", style={"color": THEME["text_muted"]}), html.Strong(f"{exceso:.1f} ppm", style={"color": THEME["accent_purple"]})], style=STYLE_KPI),
            ]
        )
        return fig_3d, fig_comp, fig_fid, kpis, f"{b0:.1f} T", f"{alfa}°", f"{t1} ms", f"{t2} ms", f"{df} Hz"

    @app.callback(
        Output("mri-se-curva", "figure"),
        Output("mri-se-polar", "figure"),
        Output("mri-se-kpis", "children"),
        Input("mri-se-tipo", "value"),
        Input("mri-se-t2", "value"),
        Input("mri-se-t2p", "value"),
        Input("mri-se-te", "value"),
    )
    def actualizar_ecos(tipo, t2, t2p, te):
        t, mxy, mz, fotos = S.bloch_isocromatas(T1=800.0, T2=float(t2), T2p=float(t2p), TE=float(te), secuencia=tipo)
        fig_curva = FG.series(t, {"|Mxy|": (mxy, THEME["accent_cyan"]), "Mz": (mz, THEME["accent_purple"])}, titulo="Magnetización Transversal Neta", xlab="Tiempo [ms]", ylab="|Mxy| / M0")
        fig_polar = FG.polar_fases(fotos)
        t2s = 1.0 / (1.0 / t2 + 1.0 / t2p)
        kpi = html.Div(
            [
                html.Div([html.Small("T2* Estimado: ", style={"color": THEME["text_muted"]}), html.Strong(f"{t2s:.1f} ms", style={"color": THEME["accent_amber"]})], style=STYLE_KPI),
            ]
        )
        return fig_curva, fig_polar, kpi

    # Callbacks de Presets para Calculadoras
    @app.callback(
        Output("mri-cl-b0", "value"),
        Input("mri-pre-b0-055", "n_clicks"),
        Input("mri-pre-b0-15", "n_clicks"),
        Input("mri-pre-b0-30", "n_clicks"),
        Input("mri-pre-b0-70", "n_clicks"),
        prevent_initial_call=True,
    )
    def aplicar_preset_b0(*_):
        trig = ctx.triggered_id
        if trig == "mri-pre-b0-055": return 0.55
        if trig == "mri-pre-b0-15": return 1.5
        if trig == "mri-pre-b0-30": return 3.0
        if trig == "mri-pre-b0-70": return 7.0
        raise PreventUpdate

    @app.callback(
        Output("mri-cl-bw", "value"),
        Output("mri-cl-g", "value"),
        Input("mri-pre-corte-fino", "n_clicks"),
        Input("mri-pre-corte-estandar", "n_clicks"),
        Input("mri-pre-corte-grueso", "n_clicks"),
        prevent_initial_call=True,
    )
    def aplicar_preset_corte(*_):
        trig = ctx.triggered_id
        if trig == "mri-pre-corte-fino": return 1200, 20.0
        if trig == "mri-pre-corte-estandar": return 1200, 10.0
        if trig == "mri-pre-corte-grueso": return 1200, 5.0
        raise PreventUpdate

    @app.callback(
        Output("mri-cl-tr", "value"),
        Output("mri-cl-ny", "value"),
        Output("mri-cl-nex", "value"),
        Output("mri-cl-etl", "value"),
        Input("mri-pre-t-se", "n_clicks"),
        Input("mri-pre-t-tse", "n_clicks"),
        Input("mri-pre-t-epi", "n_clicks"),
        prevent_initial_call=True,
    )
    def aplicar_preset_tiempo(*_):
        trig = ctx.triggered_id
        if trig == "mri-pre-t-se": return 500, 256, 1, 1
        if trig == "mri-pre-t-tse": return 3500, 256, 1, 16
        if trig == "mri-pre-t-epi": return 2000, 128, 1, 64
        raise PreventUpdate

    @app.callback(
        Output("mri-cl-t1", "value"),
        Input("mri-pre-e-grasa", "n_clicks"),
        Input("mri-pre-e-sb", "n_clicks"),
        Input("mri-pre-e-sg", "n_clicks"),
        Input("mri-pre-e-lcr", "n_clicks"),
        prevent_initial_call=True,
    )
    def aplicar_preset_ernst(*_):
        trig = ctx.triggered_id
        if trig == "mri-pre-e-grasa": return 260
        if trig == "mri-pre-e-sb": return 800
        if trig == "mri-pre-e-sg": return 1100
        if trig == "mri-pre-e-lcr": return 4000
        raise PreventUpdate

    # Callbacks de Calculadoras Enriquecidas
    @app.callback(Output("mri-cl-out1", "children"), Input("mri-cl-b0", "value"))
    def calc_larmor(b0):
        if not b0 or b0 <= 0:
            return html.Div("Ingresa un valor de campo magnético válido.", style={"color": THEME["accent_amber"]})
        b0 = float(b0)
        f0 = S.larmor_mhz(b0)
        exceso = S.exceso_spins_ppm(b0)
        banda = "VHF baja" if f0 < 100 else ("VHF alta" if f0 < 300 else "UHF")
        
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Small("Frecuencia de Larmor (f₀)", style={"color": THEME["text_muted"], "fontSize": "11px", "display": "block"}),
                                html.Strong(f"{f0:.2f} MHz", style={"color": THEME["accent_cyan"], "fontSize": "22px", "fontWeight": "800"}),
                                html.Small(f"Banda espectral: {banda}", style={"color": THEME["text_muted"], "fontSize": "11px", "display": "block", "marginTop": "2px"}),
                            ],
                            style={"backgroundColor": "#0a0f1d", "padding": "10px", "borderRadius": "8px", "flex": "1", "border": f"1px solid {THEME['card_border']}"},
                        ),
                        html.Div(
                            [
                                html.Small("Exceso Polarizado (Boltzmann)", style={"color": THEME["text_muted"], "fontSize": "11px", "display": "block"}),
                                html.Strong(f"{exceso:.1f} ppm", style={"color": THEME["accent_purple"], "fontSize": "22px", "fontWeight": "800"}),
                                html.Small("Protones en paralelo por millón", style={"color": THEME["text_muted"], "fontSize": "11px", "display": "block", "marginTop": "2px"}),
                            ],
                            style={"backgroundColor": "#0a0f1d", "padding": "10px", "borderRadius": "8px", "flex": "1", "border": f"1px solid {THEME['card_border']}"},
                        ),
                    ],
                    style={"display": "flex", "gap": "10px", "marginBottom": "12px", "flexWrap": "wrap"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.I(className="fa-solid fa-circle-info", style={"marginRight": "6px", "color": THEME["accent_cyan"]}),
                                html.Strong("Interpretación Biofísica: "),
                                f"A {b0:.2f} T, los protones de hidrógeno precesan a {f0:.2f} millones de vueltas por segundo. Solo {exceso:.1f} de cada 1 000 000 de núcleos adoptan el estado paralelo de baja energía para crear la magnetización macroscópica neta M₀.",
                            ],
                            style={"color": THEME["text"], "fontSize": "12.5px", "lineHeight": "1.5", "marginBottom": "6px"},
                        ),
                        html.Div(
                            [
                                html.I(className="fa-solid fa-lightbulb", style={"marginRight": "6px", "color": THEME["accent_amber"]}),
                                html.Strong("Regla de Oro: "),
                                "La magnetización macroscópica M₀ y la relación señal/ruido (SNR) aumentan de forma lineal con B₀.",
                            ],
                            style={"color": THEME["text_muted"], "fontSize": "12px", "lineHeight": "1.4"},
                        ),
                    ],
                    style={"backgroundColor": "rgba(56, 189, 248, 0.06)", "padding": "10px", "borderRadius": "8px", "border": "1px solid rgba(56, 189, 248, 0.2)"},
                ),
            ]
        )

    @app.callback(Output("mri-cl-out2", "children"), Input("mri-cl-bw", "value"), Input("mri-cl-g", "value"))
    def calc_corte(bw, g):
        if not bw or not g or g <= 0:
            return html.Div("Ingresa valores positivos de ancho de banda y gradiente.", style={"color": THEME["accent_amber"]})
        bw = float(bw)
        g = float(g)
        dz = S.grosor_corte_mm(bw, g)
        
        tipo_corte = "Corte Fino" if dz < 2.0 else ("Corte Estándar" if dz <= 4.0 else "Corte Grueso")
        color_badge = THEME["accent_purple"] if dz < 2.0 else (THEME["accent_cyan"] if dz <= 4.0 else THEME["accent_amber"])
        
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Small("Espesor de Corte Físico (Δz)", style={"color": THEME["text_muted"], "fontSize": "11px", "display": "block"}),
                                html.Strong(f"{dz:.2f} mm", style={"color": color_badge, "fontSize": "22px", "fontWeight": "800"}),
                                html.Small(f"Categoría: {tipo_corte}", style={"color": color_badge, "fontSize": "11px", "display": "block", "marginTop": "2px", "fontWeight": "600"}),
                            ],
                            style={"backgroundColor": "#0a0f1d", "padding": "10px", "borderRadius": "8px", "flex": "1", "border": f"1px solid {THEME['card_border']}"},
                        ),
                        html.Div(
                            [
                                html.Small("Pendiente Espacial", style={"color": THEME["text_muted"], "fontSize": "11px", "display": "block"}),
                                html.Strong(f"{42.577 * g:.1f} Hz/mm", style={"color": THEME["text"], "fontSize": "18px", "fontWeight": "700"}),
                                html.Small("Dispersión por milímetro", style={"color": THEME["text_muted"], "fontSize": "11px", "display": "block", "marginTop": "2px"}),
                            ],
                            style={"backgroundColor": "#0a0f1d", "padding": "10px", "borderRadius": "8px", "flex": "1", "border": f"1px solid {THEME['card_border']}"},
                        ),
                    ],
                    style={"display": "flex", "gap": "10px", "marginBottom": "12px", "flexWrap": "wrap"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.I(className="fa-solid fa-circle-info", style={"marginRight": "6px", "color": THEME["accent_purple"]}),
                                html.Strong("Compromiso Diagnóstico: "),
                                "Cortes finos (< 2 mm) disminuyen el efecto de volumen parcial en estructuras diminutas (hipocampo, oído interno), pero reducen la SNR. Cortes gruesos aportan mayor señal pero pierden detalle espacial.",
                            ],
                            style={"color": THEME["text"], "fontSize": "12.5px", "lineHeight": "1.5", "marginBottom": "6px"},
                        ),
                        html.Div(
                            [
                                html.I(className="fa-solid fa-lightbulb", style={"marginRight": "6px", "color": THEME["accent_amber"]}),
                                html.Strong("Regla de Oro: "),
                                "Para adelgazar el corte debes aumentar la potencia del gradiente Gz o estrechar el ancho de banda del pulso RF.",
                            ],
                            style={"color": THEME["text_muted"], "fontSize": "12px", "lineHeight": "1.4"},
                        ),
                    ],
                    style={"backgroundColor": "rgba(168, 85, 247, 0.06)", "padding": "10px", "borderRadius": "8px", "border": "1px solid rgba(168, 85, 247, 0.2)"},
                ),
            ]
        )

    @app.callback(Output("mri-cl-out3", "children"), Input("mri-cl-tr", "value"), Input("mri-cl-ny", "value"), Input("mri-cl-nex", "value"), Input("mri-cl-etl", "value"))
    def calc_tiempo(tr, ny, nex, etl):
        if not tr or not ny:
            return html.Div("Ingresa TR y número de líneas de fase.", style={"color": THEME["accent_amber"]})
        tr = float(tr)
        ny = int(ny)
        nex = max(1, int(nex or 1))
        etl = max(1, int(etl or 1))
        
        t_sec = S.tiempo_adquisicion_s(tr, ny, nex, etl)
        mins, segs = divmod(int(t_sec), 60)
        
        if t_sec < 45:
            calidad_t = "Ultrarrápido (apnea / funcional / pediátrico)"
            color_t = THEME["accent_emerald"]
        elif t_sec <= 240:
            calidad_t = "Estándar clínico (duración y confort óptimos)"
            color_t = THEME["accent_cyan"]
        else:
            calidad_t = "Secuencia larga (riesgo de movimiento del paciente)"
            color_t = THEME["accent_amber"]
            
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Small("Tiempo Total de Escaneo (T_scan)", style={"color": THEME["text_muted"], "fontSize": "11px", "display": "block"}),
                                html.Strong(f"{mins} min {segs:02d} s", style={"color": color_t, "fontSize": "22px", "fontWeight": "800"}),
                                html.Small(f"{t_sec:.1f} segundos netos", style={"color": THEME["text_muted"], "fontSize": "11px", "display": "block", "marginTop": "2px"}),
                            ],
                            style={"backgroundColor": "#0a0f1d", "padding": "10px", "borderRadius": "8px", "flex": "1", "border": f"1px solid {THEME['card_border']}"},
                        ),
                        html.Div(
                            [
                                html.Small("Aceleración por ETL", style={"color": THEME["text_muted"], "fontSize": "11px", "display": "block"}),
                                html.Strong(f"{etl}x", style={"color": THEME["accent_purple"], "fontSize": "22px", "fontWeight": "800"}),
                                html.Small(f"Sin ETL tardaría {(t_sec * etl)/60:.1f} min", style={"color": THEME["text_muted"], "fontSize": "11px", "display": "block", "marginTop": "2px"}),
                            ],
                            style={"backgroundColor": "#0a0f1d", "padding": "10px", "borderRadius": "8px", "flex": "1", "border": f"1px solid {THEME['card_border']}"},
                        ),
                    ],
                    style={"display": "flex", "gap": "10px", "marginBottom": "12px", "flexWrap": "wrap"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.I(className="fa-solid fa-clock", style={"marginRight": "6px", "color": color_t}),
                                html.Strong("Evaluación Operativa: "),
                                f"{calidad_t}. El escaneo llena una matriz de {ny} pasos de fase con {nex} promedio(s).",
                            ],
                            style={"color": THEME["text"], "fontSize": "12.5px", "lineHeight": "1.5", "marginBottom": "6px"},
                        ),
                        html.Div(
                            [
                                html.I(className="fa-solid fa-lightbulb", style={"marginRight": "6px", "color": THEME["accent_amber"]}),
                                html.Strong("Regla de Oro: "),
                                "Duplicar el número de promedios (NEX) duplica el tiempo de escaneo pero solo mejora la SNR en un factor √2 (41%).",
                            ],
                            style={"color": THEME["text_muted"], "fontSize": "12px", "lineHeight": "1.4"},
                        ),
                    ],
                    style={"backgroundColor": "rgba(16, 185, 129, 0.06)", "padding": "10px", "borderRadius": "8px", "border": "1px solid rgba(16, 185, 129, 0.2)"},
                ),
            ]
        )

    @app.callback(Output("mri-cl-out4", "children"), Input("mri-cl-t1", "value"), Input("mri-cl-tr2", "value"))
    def calc_ernst(t1, tr):
        if not t1 or not tr or t1 <= 0 or tr <= 0:
            return html.Div("Ingresa valores positivos de T1 y TR.", style={"color": THEME["accent_amber"]})
        t1 = float(t1)
        tr = float(tr)
        ernst = S.angulo_ernst(tr, t1)
        
        E1 = np.exp(-tr / t1)
        rad_e = np.deg2rad(ernst)
        sen_ernst = np.sin(rad_e) * (1.0 - E1) / (1.0 - np.cos(rad_e) * E1)
        sen_90 = 1.0 * (1.0 - E1)
        mejora = (sen_ernst / max(1e-5, sen_90) - 1.0) * 100.0
        
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Small("Ángulo Óptimo de Ernst (α_E)", style={"color": THEME["text_muted"], "fontSize": "11px", "display": "block"}),
                                html.Strong(f"{ernst:.1f}°", style={"color": THEME["accent_amber"], "fontSize": "22px", "fontWeight": "800"}),
                                html.Small(f"Para TR = {tr:.0f} ms y T1 = {t1:.0f} ms", style={"color": THEME["text_muted"], "fontSize": "11px", "display": "block", "marginTop": "2px"}),
                            ],
                            style={"backgroundColor": "#0a0f1d", "padding": "10px", "borderRadius": "8px", "flex": "1", "border": f"1px solid {THEME['card_border']}"},
                        ),
                        html.Div(
                            [
                                html.Small("Ganancia vs Pulso de 90°", style={"color": THEME["text_muted"], "fontSize": "11px", "display": "block"}),
                                html.Strong(f"+{mejora:.0f}% señal", style={"color": THEME["accent_emerald"], "fontSize": "22px", "fontWeight": "800"}),
                                html.Small("En estado estacionario", style={"color": THEME["text_muted"], "fontSize": "11px", "display": "block", "marginTop": "2px"}),
                            ],
                            style={"backgroundColor": "#0a0f1d", "padding": "10px", "borderRadius": "8px", "flex": "1", "border": f"1px solid {THEME['card_border']}"},
                        ),
                    ],
                    style={"display": "flex", "gap": "10px", "marginBottom": "12px", "flexWrap": "wrap"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.I(className="fa-solid fa-circle-info", style={"marginRight": "6px", "color": THEME["accent_amber"]}),
                                html.Strong("Por qué no usar 90°: "),
                                f"Cuando el TR ({tr:.0f} ms) es mucho menor que el T1 ({t1:.0f} ms), un pulso de 90° destruiría la magnetización longitudinal sin darle tiempo a recuperarse, saturando el tejido. Con {ernst:.1f}° obtienes la máxima señal transversal en estado estacionario.",
                            ],
                            style={"color": THEME["text"], "fontSize": "12.5px", "lineHeight": "1.5", "marginBottom": "6px"},
                        ),
                        html.Div(
                            [
                                html.I(className="fa-solid fa-lightbulb", style={"marginRight": "6px", "color": THEME["accent_cyan"]}),
                                html.Strong("Regla de Oro: "),
                                "Cuanto más corto sea el TR, menor debe ser el ángulo de inclinación α para evitar la saturación del tejido.",
                            ],
                            style={"color": THEME["text_muted"], "fontSize": "12px", "lineHeight": "1.4"},
                        ),
                    ],
                    style={"backgroundColor": "rgba(245, 158, 11, 0.06)", "padding": "10px", "borderRadius": "8px", "border": "1px solid rgba(245, 158, 11, 0.2)"},
                ),
            ]
        )

    # 7. Callbacks de Actividades & Quiz
    @app.callback(
        Output("mri-quiz-pregunta-box", "children"),
        Output("mri-quiz-feedback", "children"),
        Output("mri-quiz-badge-score", "children"),
        Input("mri-quiz-idx", "data"),
        Input("mri-quiz-categoria", "value"),
        State("mri-quiz-puntaje", "data"),
    )
    def render_pregunta_quiz(idx, categoria, puntaje):
        preguntas_filtradas = PREGUNTAS if categoria == "Todas" else [p for p in PREGUNTAS if p[4] == categoria]
        if not preguntas_filtradas:
            return html.Div("No hay preguntas en esta categoría."), "", ""
        
        idx = idx % len(preguntas_filtradas)
        enunciado, opciones, correcta, expl, cat = preguntas_filtradas[idx]

        card = html.Div(
            [
                html.Div(f"Pregunta {idx + 1} de {len(preguntas_filtradas)} · Categoría: {cat}", style={"color": THEME["accent_purple"], "fontSize": "12px", "fontWeight": "700", "marginBottom": "8px"}),
                html.H4(enunciado, style={"color": "#ffffff", "fontSize": "16px", "marginBottom": "14px"}),
                dcc.RadioItems(
                    id="mri-quiz-opciones",
                    options=[{"label": f" {op}", "value": i} for i, op in enumerate(opciones)],
                    labelStyle={"display": "block", "marginBottom": "10px", "color": THEME["text"], "cursor": "pointer"},
                ),
            ]
        )
        score_text = f"Aciertos: {puntaje.get('aciertos', 0)} / {puntaje.get('respondidas', 0)}"
        return card, "", score_text

    @app.callback(
        Output("mri-quiz-feedback", "children", allow_duplicate=True),
        Output("mri-quiz-puntaje", "data"),
        Output("mri-quiz-badge-score", "children", allow_duplicate=True),
        Input("mri-quiz-btn-responder", "n_clicks"),
        State("mri-quiz-opciones", "value"),
        State("mri-quiz-idx", "data"),
        State("mri-quiz-categoria", "value"),
        State("mri-quiz-puntaje", "data"),
        prevent_initial_call=True,
    )
    def responder_quiz(n_clicks, opcion_elegida, idx, categoria, puntaje):
        if opcion_elegida is None:
            return html.Div([html.I(className="fa-solid fa-triangle-exclamation", style={"marginRight": "8px"}), "Selecciona una opción antes de comprobar."], style={"color": THEME["accent_amber"]}), puntaje, no_update
        
        preguntas_filtradas = PREGUNTAS if categoria == "Todas" else [p for p in PREGUNTAS if p[4] == categoria]
        idx = idx % len(preguntas_filtradas)
        enunciado, opciones, correcta, expl, cat = preguntas_filtradas[idx]

        es_correcta = (opcion_elegida == correcta)
        puntaje["respondidas"] = puntaje.get("respondidas", 0) + 1
        if es_correcta:
            puntaje["aciertos"] = puntaje.get("aciertos", 0) + 1

        color = THEME["accent_emerald"] if es_correcta else "#ef4444"
        if es_correcta:
            icono_badge = [html.I(className="fa-solid fa-circle-check", style={"marginRight": "8px"}), " ¡Correcto!"]
        else:
            icono_badge = [html.I(className="fa-solid fa-circle-xmark", style={"marginRight": "8px"}), f" Incorrecto. La opción correcta era: '{opciones[correcta]}'."]

        feedback = html.Div(
            [
                html.Div(icono_badge, style={"fontWeight": "700", "color": color, "fontSize": "15px", "marginBottom": "6px"}),
                html.Div(expl, style={"color": THEME["text"], "fontSize": "13px", "lineHeight": "1.5"}),
            ],
            style={"backgroundColor": "#0a0f1d", "padding": "12px", "borderRadius": "8px", "border": f"1px solid {color}"},
        )
        score_text = f"Aciertos: {puntaje['aciertos']} / {puntaje['respondidas']}"
        return feedback, puntaje, score_text

    @app.callback(
        Output("mri-quiz-idx", "data"),
        Input("mri-quiz-btn-siguiente", "n_clicks"),
        State("mri-quiz-idx", "data"),
        prevent_initial_call=True,
    )
    def siguiente_pregunta(n_clicks, idx):
        return idx + 1

    # Callback Tutor IA con Gemini
    @app.callback(
        Output("mri-ia-respuesta", "children"),
        Input("mri-ia-btn-consultar", "n_clicks"),
        State("mri-ia-prompt", "value"),
        prevent_initial_call=True,
    )
    def consultar_tutor_ia(n_clicks, prompt):
        if not prompt or not prompt.strip():
            return html.Div("Por favor escribe una consulta para el Tutor de RM.", style={"color": THEME["accent_amber"]})
        
        system_instruction = (
            "Eres un profesor universitario y tutor pedagógico de Resonancia Magnética (MRI) e Imagenología Médica. "
            "Responde con rigor biofísico, claridad didáctica y concisión. Usa fórmulas matemáticas y ejemplos formativos si corresponde."
        )
        try:
            texto_respuesta = gemini_service.generar_texto(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.3,
            )
            return html.Div(
                [
                    html.Div([html.I(className="fa-solid fa-wand-magic-sparkles", style={"marginRight": "8px"}), "Respuesta del Tutor IA:"], style={"color": THEME["accent_purple"], "fontWeight": "700", "marginBottom": "6px"}),
                    dcc.Markdown(texto_respuesta, mathjax=True, style={"fontSize": "13px", "lineHeight": "1.6", "color": THEME["text"]}),
                ],
                style={"backgroundColor": "#0a0f1d", "padding": "14px", "borderRadius": "10px", "border": f"1px solid {THEME['card_border']}"},
            )
        except Exception as e:
            return html.Div(f"Error al consultar al Tutor IA: {e}", style={"color": "#ef4444", "fontSize": "12px"})
