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


# -----------------------------------------------------------------------------
# PASOS DE FÍSICA GUIADA (9 PASOS DE RESONA)
# -----------------------------------------------------------------------------
PASOS_FISICA = [
    {
        "t": "1. El Equipo: Superconductividad y Campo B₀",
        "img": "/assets/img/d_escaner.png",
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
        "txt": (
            "La magnetización transversal $M_{xy}$ rota en el plano transversal a la frecuencia de Larmor. Por la **Ley de "
            "Inducción de Faraday**, el flujo magnético oscilante induce microvoltios en la bobina receptora: es la señal **FID**.\n\n"
            "La señal decae rápidamente a medida que los espines pierden coherencia de fase entre sí."
        ),
    },
    {
        "t": "6. Relajación Longitudinal T₁ y Transversal T₂",
        "img": "/assets/img/d_relajacion.png",
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
                style=STYLE_CARD,
                children=[
                    html.H2("Bienvenido al Módulo de Resonancia Magnética", style=STYLE_SECTION_TITLE),
                    html.P(
                        "La Resonancia Magnética (RM) es la modalidad de imagen médica diagnóstica de mayor resolución de contraste tisular. "
                        "A diferencia de los Rayos X y la Tomografía Computarizada, no utiliza radiación ionizante, sino la interacción entre "
                        "potentes campos magnéticos estáticos, pulsos de radiofrecuencia en resonancia con los núcleos de hidrógeno y gradientes espaciales.",
                        style={"color": THEME["text"], "fontSize": "15px", "lineHeight": "1.6"},
                    ),
                    html.Div(style=STYLE_CALLOUT, children=[
                        html.Strong("Objetivo de Aprendizaje: "),
                        "Dominar desde los fundamentos cuánticos del protón y la precesión de Larmor, hasta la formación de imagen en el espacio K "
                        "y la interpretación cuantitativa del contraste patológico cerebral."
                    ]),
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
                                            "maxWidth": "100%",
                                            "borderRadius": "12px",
                                            "border": f"1px solid {THEME['card_border']}",
                                            "backgroundColor": "#0a0f1d",
                                        },
                                    ),
                                ],
                                style={"flex": "1", "maxWidth": "440px", "textAlign": "center"},
                            ),
                            html.Div(
                                [
                                    dcc.Markdown(paso["txt"], mathjax=True, style={"color": THEME["text"], "fontSize": "14px", "lineHeight": "1.7"}),
                                ],
                                style={"flex": "1.3"},
                            ),
                        ],
                        style={"display": "flex", "gap": "24px", "flexWrap": "wrap", "alignItems": "center"},
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
                            dcc.Slider(id="mri-sq-te", min=10, max=100, step=2, value=30),

                            html.Label("Tiempo de Repetición (TR) [ms]:", style=STYLE_LABEL),
                            html.Div(id="mri-sq-tr-txt", style={"color": THEME["accent_cyan"], "fontWeight": "700"}),
                            dcc.Slider(id="mri-sq-tr", min=50, max=500, step=25, value=150),

                            html.Label("Tiempo de Inversión (TI) [ms] (sólo IR):", style=STYLE_LABEL),
                            html.Div(id="mri-sq-ti-txt", style={"color": THEME["accent_cyan"], "fontWeight": "700"}),
                            dcc.Slider(id="mri-sq-ti", min=10, max=100, step=5, value=40),

                            html.Label("Tren de Ecos (ETL) (sólo EPI):", style=STYLE_LABEL),
                            html.Div(id="mri-sq-etl-txt", style={"color": THEME["accent_cyan"], "fontWeight": "700"}),
                            dcc.Slider(id="mri-sq-etl", min=4, max=16, step=2, value=8),
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
            )
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
                                    dcc.Slider(id="mri-k-d0", min=2, max=80, step=2, value=20),
                                    html.Label("Ganancia High-Boost:", style=STYLE_LABEL),
                                    dcc.Slider(id="mri-k-g", min=1.0, max=3.0, step=0.1, value=1.5),
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
                                    dcc.Slider(id="mri-k-par", min=0.1, max=0.8, step=0.05, value=0.3),
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
                                    dcc.Slider(id="mri-k-sev", min=0.1, max=1.0, step=0.05, value=0.4),
                                ],
                            ),
                        ],
                    ),

                    # Panel de Gráficos
                    html.Div(
                        style={**STYLE_CARD, "flex": "2"},
                        children=[
                            html.H3("Laboratorio de Espacio K: Entrada → Dominio K → Reconstrucción iFFT2", style=STYLE_SECTION_TITLE),
                            dcc.Loading(dcc.Graph(id="mri-k-fig", style={"height": "360px"}), type="dot", color=THEME["accent_cyan"]),
                            html.Div(id="mri-k-explica", style={"marginTop": "16px"}),
                        ],
                    ),
                ],
                style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
            )
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
                            dcc.Slider(id="mri-sc-tr", min=50, max=5000, step=50, value=500),

                            html.Label("Tiempo de Eco (TE) [ms]:", style=STYLE_LABEL),
                            html.Div(id="mri-sc-te-txt", style={"color": THEME["accent_purple"], "fontWeight": "700"}),
                            dcc.Slider(id="mri-sc-te", min=2, max=200, step=2, value=15),

                            html.Label("Tiempo de Inversión (TI) [ms] (sólo IR):", style=STYLE_LABEL),
                            html.Div(id="mri-sc-ti-txt", style={"color": THEME["accent_purple"], "fontWeight": "700"}),
                            dcc.Slider(id="mri-sc-ti", min=50, max=3000, step=50, value=2400),

                            html.Label("Ángulo α [°] (sólo GRE):", style=STYLE_LABEL),
                            html.Div(id="mri-sc-a-txt", style={"color": THEME["accent_purple"], "fontWeight": "700"}),
                            dcc.Slider(id="mri-sc-a", min=5, max=90, step=5, value=30),

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

                    # Imágenes y Curvas
                    html.Div(
                        style={"flex": "2", "display": "flex", "flexDirection": "column", "gap": "20px"},
                        children=[
                            html.Div(
                                style=STYLE_CARD,
                                children=[
                                    html.H3("Corte Axial Sintetizado en Tiempo Real", style=STYLE_SECTION_TITLE),
                                    dcc.Loading(dcc.Graph(id="mri-sc-img", style={"height": "360px"}), type="dot", color=THEME["accent_purple"]),
                                ],
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        style={**STYLE_CARD, "flex": "1"},
                                        children=[
                                            html.H4("Curvas T1 / T2", style=STYLE_SECTION_TITLE),
                                            dcc.Graph(id="mri-sc-curvas", style={"height": "220px"}),
                                        ],
                                    ),
                                    html.Div(
                                        style={**STYLE_CARD, "flex": "1"},
                                        children=[
                                            html.H4("Intensidad por Tejido", style=STYLE_SECTION_TITLE),
                                            dcc.Graph(id="mri-sc-barras", style={"height": "220px"}),
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
            )
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
            html.Div(id="mri-sim-subtab-content"),
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
                            dcc.Slider(id="mri-sb-b0", min=0.5, max=7.0, step=0.1, value=1.5),

                            html.Label("Ángulo Flip α [°]:", style=STYLE_LABEL),
                            html.Div(id="mri-sb-alfa-txt", style={"color": THEME["accent_cyan"], "fontWeight": "700"}),
                            dcc.Slider(id="mri-sb-alfa", min=10, max=180, step=10, value=90),

                            html.Label("T1 [ms] (Longitudinal):", style=STYLE_LABEL),
                            html.Div(id="mri-sb-t1-txt", style={"color": THEME["accent_cyan"], "fontWeight": "700"}),
                            dcc.Slider(id="mri-sb-t1", min=100, max=3000, step=100, value=800),

                            html.Label("T2 [ms] (Transversal):", style=STYLE_LABEL),
                            html.Div(id="mri-sb-t2-txt", style={"color": THEME["accent_cyan"], "fontWeight": "700"}),
                            dcc.Slider(id="mri-sb-t2", min=20, max=500, step=10, value=90),

                            html.Label("Desajuste Δf [Hz]:", style=STYLE_LABEL),
                            html.Div(id="mri-sb-df-txt", style={"color": THEME["accent_cyan"], "fontWeight": "700"}),
                            dcc.Slider(id="mri-sb-df", min=0, max=20, step=1, value=5),

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
                                            dcc.Graph(id="mri-sb-comp", style={"height": "220px"}),
                                        ],
                                    ),
                                    html.Div(
                                        style={**STYLE_CARD, "flex": "1"},
                                        children=[
                                            html.H4("Señal FID Detectada", style=STYLE_SECTION_TITLE),
                                            dcc.Graph(id="mri-sb-fid", style={"height": "220px"}),
                                        ],
                                    ),
                                ],
                                style={"display": "flex", "gap": "16px", "flexWrap": "wrap"},
                            ),
                        ],
                    ),
                ],
                style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
            )
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
                            dcc.Slider(id="mri-se-t2", min=20, max=300, step=10, value=100),
                            html.Label("T2' (Inhomogeneidad) [ms]:", style=STYLE_LABEL),
                            dcc.Slider(id="mri-se-t2p", min=5, max=80, step=5, value=20),
                            html.Label("Tiempo de Eco (TE) [ms]:", style=STYLE_LABEL),
                            dcc.Slider(id="mri-se-te", min=20, max=150, step=5, value=60),
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
                                    dcc.Graph(id="mri-se-curva", style={"height": "260px"}),
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
            )
        ]
    )


# Subtab C: Calculadoras
def render_subtab_calculadoras():
    return html.Div(
        [
            html.Div(
                [
                    # Calculadora 1: Larmor
                    html.Div(
                        style={**STYLE_CARD, "flex": "1", "minWidth": "280px"},
                        children=[
                            html.H4("1. Larmor y Polarización", style=STYLE_SECTION_TITLE),
                            html.Label("Campo Magnético B₀ [T]:", style=STYLE_LABEL),
                            dcc.Input(id="mri-cl-b0", type="number", value=1.5, min=0.1, max=11.7, step=0.1, style={"width": "100%", "padding": "6px"}),
                            html.Div(id="mri-cl-out1", style={"marginTop": "12px"}),
                        ],
                    ),
                    # Calculadora 2: Selección de Corte
                    html.Div(
                        style={**STYLE_CARD, "flex": "1", "minWidth": "280px"},
                        children=[
                            html.H4("2. Selección de Corte", style=STYLE_SECTION_TITLE),
                            html.Label("Ancho de Banda RF [Hz]:", style=STYLE_LABEL),
                            dcc.Input(id="mri-cl-bw", type="number", value=1200, min=100, max=10000, step=50, style={"width": "100%", "padding": "6px"}),
                            html.Label("Gradiente Gz [mT/m]:", style=STYLE_LABEL),
                            dcc.Input(id="mri-cl-g", type="number", value=10.0, min=0.5, max=80.0, step=0.5, style={"width": "100%", "padding": "6px"}),
                            html.Div(id="mri-cl-out2", style={"marginTop": "12px"}),
                        ],
                    ),
                    # Calculadora 3: Tiempo de Adquisición
                    html.Div(
                        style={**STYLE_CARD, "flex": "1", "minWidth": "280px"},
                        children=[
                            html.H4("3. Tiempo de Escaneo", style=STYLE_SECTION_TITLE),
                            html.Label("TR [ms]:", style=STYLE_LABEL),
                            dcc.Input(id="mri-cl-tr", type="number", value=500, min=10, max=10000, step=50, style={"width": "100%", "padding": "6px"}),
                            html.Label("Líneas de Fase (Ny):", style=STYLE_LABEL),
                            dcc.Input(id="mri-cl-ny", type="number", value=256, min=32, max=1024, step=32, style={"width": "100%", "padding": "6px"}),
                            html.Label("NEX (Promedios):", style=STYLE_LABEL),
                            dcc.Input(id="mri-cl-nex", type="number", value=1, min=1, max=16, step=1, style={"width": "100%", "padding": "6px"}),
                            html.Label("Factor Turbo (ETL):", style=STYLE_LABEL),
                            dcc.Input(id="mri-cl-etl", type="number", value=1, min=1, max=64, step=1, style={"width": "100%", "padding": "6px"}),
                            html.Div(id="mri-cl-out3", style={"marginTop": "12px"}),
                        ],
                    ),
                    # Calculadora 4: Ángulo de Ernst
                    html.Div(
                        style={**STYLE_CARD, "flex": "1", "minWidth": "280px"},
                        children=[
                            html.H4("4. Ángulo Óptimo de Ernst (GRE)", style=STYLE_SECTION_TITLE),
                            html.Label("T1 del Tejido [ms]:", style=STYLE_LABEL),
                            dcc.Input(id="mri-cl-t1", type="number", value=900, min=50, max=4000, step=50, style={"width": "100%", "padding": "6px"}),
                            html.Label("TR de Secuencia [ms]:", style=STYLE_LABEL),
                            dcc.Input(id="mri-cl-tr2", type="number", value=30, min=2, max=500, step=2, style={"width": "100%", "padding": "6px"}),
                            html.Div(id="mri-cl-out4", style={"marginTop": "12px"}),
                        ],
                    ),
                ],
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(260px, 1fr))", "gap": "16px"},
            )
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
        lab2, mapas = F.corte_axial_parametros("sano")
        img_orig = F.sintetizar(mapas, "T1", ruido=0.005)

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
        fig_curvas = FG.series(t1 if tipo != "T2" else t2, ys_curvas, titulo="Relajación Tisular", xlab="t [ms]")

        res_tej = S.senal_tejidos(tipo, float(TR), float(TE), float(TI), float(alfa), float(b0))
        nombres = list(res_tej.keys())
        valores = [res_tej[k][0] for k in nombres]
        colores = [res_tej[k][1] for k in nombres]
        fig_barras = FG.barras(nombres, valores, colores, titulo="Intensidad de Señal por Tejido")

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
        fig_comp = FG.series(tt, ys_comp, titulo="Componentes de M(t)")

        ys_fid = {
            "Señal FID (My')": (MM[:, 1], THEME["accent_cyan"]),
            "Envolvente e^(-t/T2)": (np.sin(np.deg2rad(alfa)) * np.exp(-tt / t2), THEME["accent_amber"]),
        }
        fig_fid = FG.series(tt, ys_fid, titulo="Señal Detectada en Bobina")

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
        fig_curva = FG.series(t, {"|Mxy|": (mxy, THEME["accent_cyan"]), "Mz": (mz, THEME["accent_purple"])}, titulo="Magnetización Transversal Neta")
        fig_polar = FG.polar_fases(fotos)
        t2s = 1.0 / (1.0 / t2 + 1.0 / t2p)
        kpi = html.Div(
            [
                html.Div([html.Small("T2* Estimado: ", style={"color": THEME["text_muted"]}), html.Strong(f"{t2s:.1f} ms", style={"color": THEME["accent_amber"]})], style=STYLE_KPI),
            ]
        )
        return fig_curva, fig_polar, kpi

    # Callbacks de Calculadoras
    @app.callback(Output("mri-cl-out1", "children"), Input("mri-cl-b0", "value"))
    def calc_larmor(b0):
        if not b0:
            return ""
        f0 = S.larmor_mhz(b0)
        exceso = S.exceso_spins_ppm(b0)
        return html.Div([html.Div(f"f₀ = {f0:.2f} MHz"), html.Div(f"Exceso = {exceso:.1f} ppm")], style={"color": THEME["accent_cyan"], "fontWeight": "600"})

    @app.callback(Output("mri-cl-out2", "children"), Input("mri-cl-bw", "value"), Input("mri-cl-g", "value"))
    def calc_corte(bw, g):
        if not bw or not g:
            return ""
        dz = S.grosor_corte_mm(bw, g)
        return html.Div(f"Grosor de Corte Δz = {dz:.2f} mm", style={"color": THEME["accent_purple"], "fontWeight": "600"})

    @app.callback(Output("mri-cl-out3", "children"), Input("mri-cl-tr", "value"), Input("mri-cl-ny", "value"), Input("mri-cl-nex", "value"), Input("mri-cl-etl", "value"))
    def calc_tiempo(tr, ny, nex, etl):
        if not tr or not ny:
            return ""
        t_sec = S.tiempo_adquisicion_s(tr, ny, nex or 1, etl or 1)
        mins, segs = divmod(int(t_sec), 60)
        return html.Div(f"Tiempo Total: {mins} min {segs} s ({t_sec:.1f} s)", style={"color": THEME["accent_cyan"], "fontWeight": "600"})

    @app.callback(Output("mri-cl-out4", "children"), Input("mri-cl-t1", "value"), Input("mri-cl-tr2", "value"))
    def calc_ernst(t1, tr):
        if not t1 or not tr:
            return ""
        ernst = S.angulo_ernst(tr, t1)
        return html.Div(f"Ángulo de Ernst α_E = {ernst:.1f}°", style={"color": THEME["accent_amber"], "fontWeight": "600"})

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
