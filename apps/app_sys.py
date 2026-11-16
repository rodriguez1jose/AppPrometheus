# ============================================================
# apps/app_sys.py — Señales y Sistemas
# ============================================================
import os
import io
import re
import json
import base64
import random
import datetime
import traceback

import numpy as np
_trapz = getattr(np, 'trapezoid', None) or np.trapz

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import signal

from dash import dcc, html, Input, Output, State, ALL, callback_context, no_update
from dash.exceptions import PreventUpdate

from config import ESTUDIANTES_CSV
from services.gemini_service import gemini_service

# ---- SYMPY ----
_SYMPY_OK = True
try:
    import sympy as sp
except ImportError:
    _SYMPY_OK = False

# ---- CONFIG (tema y estilos compartidos) ----
from config import (
    THEME,
    STYLE_CONTAINER,
    STYLE_HEADER,
    STYLE_CARD,
    STYLE_CALLOUT,
    STYLE_SECTION_TITLE,
    STYLE_LABEL,
    STYLE_GRAPH_DESC,
    STYLE_MINI_BUTTON,
    STYLE_MINI_BUTTON_ALT,
    STYLE_MINI_BUTTON_GREEN,
    STYLE_MINI_BUTTON_AMBER,
    STYLE_ERROR_BOX,
    STYLE_CONTROL_CARD,
    STYLE_CONTROL_INPUT,
    STYLE_SIDEBAR,
    STYLE_CONTENT_AREA,
    STYLE_EDU_CARD,
    STYLE_EDU_PAGE_HEADER,
    STYLE_PILL,
    STYLE_MODAL_OVERLAY_HIDDEN,
    STYLE_MODAL_OVERLAY_VISIBLE,
    STYLE_MODAL_BOX,
    STYLE_QUIZ_CARD,
    STYLE_OPTION_BUTTON,
    STYLE_OPTION_SELECTED,
    STYLE_ADVANCED_HEADER_BTN,
    STYLE_ADVANCED_PANEL_HIDDEN,
    STYLE_ADVANCED_PANEL_VISIBLE,
    STYLE_MARGIN_PILL_OK,
    STYLE_MARGIN_PILL_BAD,
)

# ---- GEMINI (Unificado a través de services.gemini_service) ----
# Utiliza gemini_service para la generación inteligente de quizzes y actividades


# ═══════════════════════════════════════════════════════════════════════════════
# BLOQUE 3 — UTILIDADES COMUNES
# ═══════════════════════════════════════════════════════════════════════════════

def empty_fig(title=""):
    """Figura vacía con estilo consistente."""
    fig = go.Figure()
    fig.update_layout(
        title=title, template='plotly_dark',
        plot_bgcolor=THEME['card'], paper_bgcolor=THEME['card'],
        height=300
    )
    return fig


def parse_user_signal(expr_str, t_array):
    """Parsea una expresión matemática y la evalúa sobre t_array."""
    if not expr_str or not expr_str.strip():
        return None, "Ingresa una expresión para x(t)."

    if not _SYMPY_OK:
        return None, "Falta sympy. Instala con: pip install sympy"

    try:
        expr_str = expr_str.strip()
        expr_str = expr_str.replace('^', '**')
        expr_str = re.sub(r'\bsen\b', 'sin', expr_str)

        t_sym = sp.symbols('t', real=True)
        local_dict = {
            't': t_sym,
            'pi': sp.pi,
            'e': sp.E,
            'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
            'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan,
            'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh,
            'exp': sp.exp, 'log': sp.log, 'sqrt': sp.sqrt,
            'abs': sp.Abs, 'sign': sp.sign,
            'heaviside': sp.Heaviside,
        }

        expr = sp.sympify(expr_str, locals=local_dict)
        f = sp.lambdify(t_sym, expr, modules=['numpy'])

        with np.errstate(all='ignore'):
            x_vals = f(t_array)

        x_vals = np.asarray(x_vals, dtype=float)
        if x_vals.ndim == 0:
            x_vals = np.full_like(t_array, float(x_vals), dtype=float)
        x_vals = np.nan_to_num(x_vals, nan=0.0, posinf=0.0, neginf=0.0)

        return x_vals, None

    except Exception as e:
        return None, f"Error al interpretar la expresión: {e}"


def make_slider_marks(marks_dict):
    """Formatea las marcas de un dcc.Slider con el estilo del tema."""
    return {
        k: {'label': v, 'style': {'color': '#94a3b8', 'fontSize': '11px'}}
        for k, v in marks_dict.items()
    }


def _modal_body(paragraphs):
    """Envuelve párrafos para el modal del glosario."""
    return html.Div([
        html.P(p, style={'fontSize': '14.5px', 'lineHeight': '1.6',
                         'color': '#e2e8f0', 'marginBottom': '10px'})
        for p in paragraphs
    ])


GLOSSARY = {
    'fourier_periodica': {
        'title': 'Función Periódica',
        'body': _modal_body([
            "Una función x(t) es periódica con período T si x(t) = x(t + T) para todo t. El período fundamental T₀ es el menor valor positivo de T que cumple esta condición.",
            "La frecuencia fundamental se define como f₀ = 1/T₀ (en Hz) o ω₀ = 2π/T₀ (en rad/s).",
            "Ejemplos: cos(ωt), ondas cuadradas, triangulares, dientes de sierra, trenes de impulsos.",
        ])
    },
    'fourier_exponencial': {
        'title': 'Exponencial Compleja',
        'body': _modal_body([
            "Una exponencial compleja tiene la forma e^(jθ) = cos(θ) + j·sin(θ) (fórmula de Euler).",
            "En la serie de Fourier, cada armónico se escribe como Cₖ e^(jkω₀t), donde Cₖ es un número complejo que codifica amplitud y fase, y kω₀ es la frecuencia del armónico.",
            "La suma de exponenciales complejas conjugadas (k y -k) da como resultado una sinusoide real: C₋ₖ e^(-jkω₀t) + Cₖ e^(jkω₀t) = 2|Cₖ| cos(kω₀t + θₖ).",
        ])
    },
    'fourier_espectro': {
        'title': 'Espectro de Frecuencia',
        'body': _modal_body([
            "El espectro de frecuencia es una representación gráfica de las amplitudes (|Cₖ|) y fases (∠Cₖ) de cada armónico de una señal periódica.",
            "Para señales periódicas, el espectro es discreto (líneas verticales en frecuencias kω₀), a diferencia de las señales no periódicas, cuyo espectro es continuo.",
            "El espectro de magnitud muestra cuánta energía hay en cada frecuencia; el espectro de fase muestra el desfase de cada componente.",
        ])
    },
    'gibbs': {
        'title': 'Fenómeno de Gibbs',
        'body': _modal_body([
            "El fenómeno de Gibbs es el sobreimpulso que aparece en la serie de Fourier truncada cerca de una discontinuidad de la señal.",
            "A medida que se añaden más armónicos (N → ∞), el ancho de los sobreimpulsos disminuye, pero su amplitud no desaparece: se estabiliza en aproximadamente el 9% de la altura del salto.",
            "Es un efecto matemático inevitable de aproximar funciones discontinuas mediante sumas finitas de funciones continuas (senoides).",
        ])
    },
    'fourier_filter': {
        'title': 'Filtrado de Fourier',
        'body': _modal_body([
            "El filtrado de Fourier es una técnica de procesamiento de señales que modifica el contenido frecuencial de una señal. Funciona en 3 pasos: (1) se aplica la Transformada de Fourier para pasar del dominio del tiempo al dominio de la frecuencia, (2) se multiplica por una función de filtro H(f) que atenúa o amplifica ciertas frecuencias, y (3) se aplica la Transformada Inversa de Fourier para volver al dominio temporal.",
            "La ventaja principal es que permite eliminar ruido o interferencias de manera selectiva, siempre que estas ocupen un rango de frecuencias distinto al de la señal útil. Por ejemplo, si la señal se concentra en bajas frecuencias y el ruido en altas, un filtro pasa-bajos elimina el ruido sin afectar la señal.",
            "Las aplicaciones típicas incluyen: eliminación de ruido de la red eléctrica (50/60 Hz) en señales ECG, suavizado de señales espectroscópicas, y separación de componentes en señales biomédicas multicomponente.",
            "Un aspecto importante es el compromiso entre la selectividad del filtro y la distorsión de la señal: filtros muy agresivos pueden introducir artefactos como el rizado (ringing) descrito por el fenómeno de Gibbs.",
        ])
    },
}


def term(text, key):
    """Botón de término clickeable que abre el modal de 'aprender más'."""
    return html.Button(
        text,
        id={'type': 'sys-term-link', 'term': key},
        n_clicks=0,
        className='term-link'
    )


def edu_card(title, icon, children):
    """Tarjeta educativa con ícono y contenido."""
    if isinstance(icon, str) and icon.startswith('fa-'):
        icon_element = html.I(className=icon, style={'fontSize': '20px', 'color': '#38bdf8'})
    else:
        icon_element = html.Span(icon, style={'fontSize': '22px'})

    return html.Div(className='edu-card', style=STYLE_EDU_CARD, children=[
        html.Div(
            style={'display': 'flex', 'alignItems': 'center', 'gap': '10px',
                   'marginBottom': '14px'},
            children=[
                icon_element,
                html.H3(title, style={'margin': '0', 'fontSize': '19px',
                                       'fontWeight': '700', 'color': '#f8fafc'})
            ]
        ),
        html.Div(children)
    ])


def page_header(pill_text, title, subtitle):
    """Encabezado de página educativa."""
    return html.Div(style=STYLE_EDU_PAGE_HEADER, children=[
        html.Span(pill_text, style=STYLE_PILL),
        html.H1(title, style={'margin': '12px 0 6px 0', 'fontSize': '34px',
                              'color': '#ffffff', 'fontWeight': '800'}),
        html.P(subtitle, style={'margin': '0', 'fontSize': '15px',
                                'color': '#cbd5e1', 'maxWidth': '780px',
                                'lineHeight': '1.5'}),
    ])


def next_section_link(href, label):
    """Botón de navegación al siguiente tema."""
    return html.Div(style={'marginTop': '10px', 'marginBottom': '30px'}, children=[
        dcc.Link(f"Siguiente: {label} →", href=href, className='nav-cta-btn')
    ])


# ═══════════════════════════════════════════════════════════════════════════════
# BLOQUE 4 — FOURIER (funciones de dominio + página + callbacks)
# ═══════════════════════════════════════════════════════════════════════════════

def generate_square_wave(t, T0, V=1.0):
    phase = (t / T0) % 1.0
    return np.where(phase < 0.5, V, -V)


def generate_triangle_wave(t, T0, V=1.0):
    phase = (t / T0) % 1.0
    return V * (4 * np.abs(phase - 0.5) - 1)


def generate_sawtooth_wave(t, T0, V=1.0):
    phase = (t / T0) % 1.0
    return V * (2 * phase - 1)


def generate_impulse_train(t, T0, V=1.0):
    phase = (t / T0) % 1.0
    return np.where(phase < 0.05, V / 0.05, 0.0)


def fourier_coefficients_square(T0, V=1.0, N=50):
    coeffs = {}
    for k in range(-N, N + 1):
        if k == 0:
            coeffs[k] = 0.0
        elif k % 2 == 1:
            coeffs[k] = -1j * 2 * V / (k * np.pi)
        else:
            coeffs[k] = 0.0
    return coeffs


def fourier_coefficients_triangle(T0, V=1.0, N=50):
    coeffs = {}
    for k in range(-N, N + 1):
        if k == 0:
            coeffs[k] = 0.0
        elif k % 2 == 1:
            coeffs[k] = -2 * V / ((k * np.pi) ** 2)
        else:
            coeffs[k] = 0.0
    return coeffs


def fourier_coefficients_sawtooth(T0, V=1.0, N=50):
    coeffs = {}
    for k in range(-N, N + 1):
        if k == 0:
            coeffs[k] = 0.0
        else:
            coeffs[k] = 1j * V / (k * np.pi)
    return coeffs


def reconstruct_signal_from_coeffs(t, coeffs, T0):
    w0 = 2 * np.pi / T0
    x_approx = np.zeros_like(t, dtype=complex)
    for k, Ck in coeffs.items():
        x_approx += Ck * np.exp(1j * k * w0 * t)
    return np.real(x_approx)


def compute_spectrum(coeffs):
    ks = sorted(coeffs.keys())
    freqs = np.array(ks)
    mags = np.array([np.abs(coeffs[k]) for k in ks])
    phases = np.array([np.angle(coeffs[k], deg=True) for k in ks])
    return freqs, mags, phases


def compute_mse(x_original, x_approx):
    return float(np.mean((x_original - x_approx) ** 2))


def compute_energy(coeffs):
    return float(sum(np.abs(Ck) ** 2 for Ck in coeffs.values()))


def compute_fourier_coeffs_numeric(x_array, t_array, T0, N=50):
    w0 = 2 * np.pi / T0
    coeffs = {}
    mask = (t_array >= 0) & (t_array < T0)
    t_period = t_array[mask]
    x_period = x_array[mask]

    if len(t_period) < 2:
        t_period = t_array
        x_period = x_array

    for k in range(-N, N + 1):
        integrand = x_period * np.exp(-1j * k * w0 * t_period)
        Ck = _trapz(integrand, t_period) / T0
        coeffs[k] = complex(Ck)

    return coeffs


def compute_coeffs_table(coeffs, max_rows=15, theme_mode='dark'):
    is_light = (theme_mode == 'light')
    ks = sorted(coeffs.keys())
    nonzero = [(k, coeffs[k]) for k in ks if abs(coeffs[k]) > 1e-9]
    sorted_by_mag = sorted(nonzero, key=lambda x: -abs(x[1]))[:max_rows * 2]
    sorted_by_mag = sorted(sorted_by_mag, key=lambda x: x[0])

    row_text = '#0f172a' if is_light else '#e2e8f0'
    mag_color = '#0284c7' if is_light else '#38bdf8'
    phase_color = '#d97706' if is_light else '#f59e0b'
    border_c = '#e2e8f0' if is_light else '#334155'
    header_bg = '#f1f5f9' if is_light else '#0d1424'

    rows = []
    for k, Ck in sorted_by_mag:
        mag = abs(Ck)
        phase = np.angle(Ck, deg=True)
        rows.append(html.Tr([
            html.Td(f"k = {k}", style={'padding': '6px 10px', 'color': row_text,
                                        'fontFamily': 'monospace', 'fontSize': '12.5px',
                                        'borderBottom': f"1px solid {border_c}"}),
            html.Td(f"{mag:.5f}", style={'padding': '6px 10px', 'color': mag_color,
                                          'fontFamily': 'monospace', 'fontSize': '12.5px',
                                          'textAlign': 'right',
                                          'borderBottom': f"1px solid {border_c}"}),
            html.Td(f"{phase:+.2f}°", style={'padding': '6px 10px', 'color': phase_color,
                                              'fontFamily': 'monospace', 'fontSize': '12.5px',
                                              'textAlign': 'right',
                                              'borderBottom': f"1px solid {border_c}"}),
        ]))

    return html.Div(className='edu-subcard', style={
        'backgroundColor': '#ffffff' if is_light else '#111827',
        'padding': '16px', 'borderRadius': '12px',
        'border': f"1px solid {border_c}",
        'boxShadow': '0 2px 8px rgba(0,0,0,0.04)' if is_light else 'none'
    }, children=[
        html.H5(
            [html.I(className="fa-solid fa-clipboard-list", style={'marginRight': '8px', 'color': mag_color}),
             "Coeficientes más significativos"],
            style={'color': '#0f172a' if is_light else '#f8fafc', 'marginBottom': '10px', 'fontSize': '15px', 'fontWeight': '700'}
        ),
        html.Div(style={'maxHeight': '300px', 'overflowY': 'auto',
                        'border': f"1px solid {border_c}", 'borderRadius': '8px'},
                 children=[
            html.Table(className='edu-table', style={'width': '100%', 'borderCollapse': 'collapse'},
                       children=[
                html.Thead(html.Tr([
                    html.Th("Armónico", style={'padding': '8px 10px', 'color': mag_color,
                                                'textAlign': 'left', 'fontSize': '12px',
                                                'borderBottom': f"1px solid {border_c}",
                                                'backgroundColor': header_bg}),
                    html.Th("|Cₖ|", style={'padding': '8px 10px', 'color': mag_color,
                                            'textAlign': 'right', 'fontSize': '12px',
                                            'borderBottom': f"1px solid {border_c}",
                                            'backgroundColor': header_bg}),
                    html.Th("∠Cₖ", style={'padding': '8px 10px', 'color': mag_color,
                                           'textAlign': 'right', 'fontSize': '12px',
                                           'borderBottom': f"1px solid {border_c}",
                                           'backgroundColor': header_bg}),
                ])),
                html.Tbody(rows),
            ])
        ])
    ])


def export_fourier_to_csv(t, x_original, x_approx, coeffs):
    buf = io.StringIO()
    buf.write("tiempo,senal_original,senal_aproximada,error\n")
    for i in range(len(t)):
        buf.write(f"{t[i]:.6f},{x_original[i]:.6f},{x_approx[i]:.6f},{x_original[i]-x_approx[i]:.6f}\n")
    buf.write("\n# Coeficientes de Fourier\n")
    buf.write("k,|Ck|,fase_deg\n")
    for k in sorted(coeffs.keys()):
        Ck = coeffs[k]
        buf.write(f"{k},{abs(Ck):.6f},{np.angle(Ck, deg=True):.4f}\n")
    return buf.getvalue()


def compute_convergence_curve(x_original, t, T0, N_max=50):
    Ns = list(range(1, N_max + 1, max(1, N_max // 25)))
    mses = []
    energies = []

    all_coeffs = compute_fourier_coeffs_numeric(x_original, t, T0, N=N_max)
    total_energy = sum(abs(all_coeffs[k]) ** 2 for k in all_coeffs)

    for N in Ns:
        sub_coeffs = {k: all_coeffs[k] for k in all_coeffs if abs(k) <= N}
        x_approx = reconstruct_signal_from_coeffs(t, sub_coeffs, T0)
        mse = compute_mse(x_original, x_approx)
        mses.append(mse)
        partial_energy = sum(abs(sub_coeffs[k]) ** 2 for k in sub_coeffs)
        energies.append(partial_energy)

    return Ns, mses, energies, total_energy


def page_fourier():
    """Página de Series de Fourier (contenido educativo + laboratorio)."""
    return html.Div(style=STYLE_CONTAINER, children=[
        page_header(
            "SERIES DE FOURIER",
            "Descomposición Espectral de Señales Periódicas",
            "Toda señal periódica puede expresarse como suma infinita de exponenciales complejas "
            "(o senoides) armónicamente relacionadas. Esta es la base del análisis espectral en ingeniería."
        ),

        # ===== PANEL 1: INTRODUCCIÓN =====
        edu_card("¿Qué es una Serie de Fourier?", "fa-solid fa-bullseye", [
            html.P([
                "Una ", term("función periódica", "fourier_periodica"),
                " x(t) con período fundamental T₀ puede descomponerse como una suma infinita de ",
                term("exponenciales complejas", "fourier_exponencial"),
                " cuyas frecuencias son múltiplos enteros de la frecuencia fundamental ω₀ = 2π/T₀."
            ], style={'color': THEME['text'], 'fontSize': '15px', 'lineHeight': '1.7'}),

            html.Div(style=STYLE_CALLOUT, children=[
                html.Strong("Idea central: "),
                "cualquier señal periódica, por complicada que sea, se construye sumando senoides simples."
            ]),

            html.P([
                "Existen tres formas equivalentes de escribir la serie:"
            ], style={'color': THEME['text_muted'], 'fontSize': '14px', 'marginTop': '12px'}),

            html.Table(className='edu-table', style={
                'width': '100%', 'borderCollapse': 'collapse', 'marginTop': '14px',
                'borderRadius': '10px', 'overflow': 'hidden',
                'border': f"1px solid {THEME['card_border']}"
            }, children=[
                html.Thead(html.Tr([
                    html.Th("Forma", style={'padding': '14px 18px', 'textAlign': 'left', 'fontSize': '14px', 'fontWeight': '700', 'letterSpacing': '0.5px'}),
                    html.Th("Ecuación", style={'padding': '14px 18px', 'textAlign': 'left', 'fontSize': '14px', 'fontWeight': '700', 'letterSpacing': '0.5px'}),
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td("Exponencial", style={'padding': '18px 18px', 'fontSize': '15px', 'fontWeight': '600', 'verticalAlign': 'middle'}),
                        html.Td(
                            html.Div(
                                r"$$x(t) = \sum_{k=-\infty}^{\infty} C_k \, e^{jk\omega_0 t}$$",
                                className='math-formula-callout',
                                style={'fontSize': '24px', 'fontWeight': '700', 'verticalAlign': 'middle', 'lineHeight': '1.8'}
                            ),
                            style={'padding': '18px 18px', 'verticalAlign': 'middle'}
                        ),
                    ]),
                    html.Tr([
                        html.Td("Trigonométrica combinada", style={'padding': '18px 18px', 'fontSize': '15px', 'fontWeight': '600', 'verticalAlign': 'middle'}),
                        html.Td(
                            html.Div(
                                r"$$x(t) = C_0 + \sum_{k=1}^{\infty} 2|C_k| \cos(k\omega_0 t + \theta_k)$$",
                                className='math-formula-callout',
                                style={'fontSize': '24px', 'fontWeight': '700', 'verticalAlign': 'middle', 'lineHeight': '1.8'}
                            ),
                            style={'padding': '18px 18px', 'verticalAlign': 'middle'}
                        ),
                    ]),
                    html.Tr([
                        html.Td("Trigonométrica", style={'padding': '18px 18px', 'fontSize': '15px', 'fontWeight': '600', 'verticalAlign': 'middle'}),
                        html.Td(
                            html.Div(
                                r"$$x(t) = A_0 + \sum_{k=1}^{\infty} \left(A_k \cos k\omega_0 t + B_k \sin k\omega_0 t\right)$$",
                                className='math-formula-callout',
                                style={'fontSize': '24px', 'fontWeight': '700', 'verticalAlign': 'middle', 'lineHeight': '1.8'}
                            ),
                            style={'padding': '18px 18px', 'verticalAlign': 'middle'}
                        ),
                    ]),
                ])
            ]),

            html.Div(className='edu-image-container', children=[
                html.Img(src='/assets/fourier_intro.png', className='edu-image',
                         style={'maxHeight': '200px', 'objectFit': 'contain'})
            ]),
            html.Div("Función periódica con período fundamental T₀", className='img-caption'),
        ]),

        # ===== PANEL 2: COEFICIENTES =====
        edu_card("Coeficientes de Fourier", "fa-solid fa-ruler-combined", [
            html.P([
                "Los coeficientes Cₖ se calculan mediante la integral de proyección sobre cada exponencial compleja:"
            ], style={'color': THEME['text'], 'fontSize': '15px', 'lineHeight': '1.7'}),

            html.Div(className='edu-formula-box', style={
                'padding': '16px', 'borderRadius': '10px',
                'border': f"1px solid {THEME['card_border']}", 'textAlign': 'center', 'margin': '12px 0'
            }, children=[
                html.Div(r"$$C_k = \frac{1}{T_0} \int_{T_0} x(t) \, e^{-jk\omega_0 t} \, dt$$",
                    className='math-formula-callout',
                    style={'fontSize': '28px', 'fontWeight': '700',
                           'textAlign': 'center', 'padding': '16px', 'lineHeight': '2'})
            ]),

            html.Ul(style={'color': THEME['text'], 'fontSize': '15px', 'lineHeight': '2.2', 'paddingLeft': '22px', 'marginTop': '14px'}, children=[
                html.Li([
                    html.Span(r"$C_0$", style={'color': THEME['accent_amber'], 'fontWeight': '700'}),
                    " = valor promedio (componente DC) de la señal."
                ]),
                html.Li([
                    html.Span(r"$C_k$", style={'color': THEME['accent_cyan'], 'fontWeight': '700'}),
                    " = amplitud y fase del k-ésimo armónico."
                ]),
                html.Li([
                    html.Span(r"$C_{-k} = C_k^*$", style={'color': THEME['accent_emerald'], 'fontWeight': '700'}),
                    " (conjugado) porque ",
                    html.Span(r"$x(t)$", style={'color': THEME['text']}),
                    " es real."
                ]),
                html.Li([
                    html.Span(r"$2C_k = A_k - jB_k$", style={'color': THEME['accent_purple'], 'fontWeight': '700'}),
                    " relación con la forma trigonométrica."
                ]),
            ]),

            html.Div(style=STYLE_CALLOUT, children=[
                html.Strong("Interpretación física: "),
                "Cₖ mide cuánta energía tiene la señal en la frecuencia kω₀."
            ]),
        ]),

        # ===== PANEL 3: ESPECTRO =====
        edu_card("Espectro de Frecuencia", "fa-solid fa-chart-bar", [
            html.P([
                "El ", term("espectro de frecuencia", "fourier_espectro"),
                " muestra las amplitudes ",
                html.Span(r"$|C_k|$", style={'color': THEME['accent_cyan'], 'fontWeight': '700'}),
                " y fases ",
                html.Span(r"$\angle C_k$", style={'color': THEME['accent_amber'], 'fontWeight': '700'}),
                " de cada armónico como líneas verticales en las frecuencias ",
                html.Span(r"$k\omega_0$", style={'color': THEME['text'], 'fontWeight': '700'}),
                ". Es discreto porque la señal es periódica."
            ], style={'color': THEME['text'], 'fontSize': '15px', 'lineHeight': '1.9'}),

            html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '14px', 'marginTop': '12px'}, children=[
                html.Div(className='edu-subcard', style={'padding': '14px', 'borderRadius': '10px', 'border': f"1px solid {THEME['card_border']}"}, children=[
                    html.H5("Espectro de Magnitud", style={'color': THEME['accent_cyan'], 'marginBottom': '8px'}),
                    html.P([
                        html.Span(r"$|C_k|$", style={'color': THEME['accent_cyan'], 'fontWeight': '700'}),
                        " vs ",
                        html.Span(r"$k\omega_0$", style={'color': THEME['text'], 'fontWeight': '700'}),
                        ". Muestra cuánta energía hay en cada armónico."
                    ], style={'color': THEME['text_muted'], 'fontSize': '13.5px', 'lineHeight': '1.8'}),
                ]),
                html.Div(className='edu-subcard', style={'padding': '14px', 'borderRadius': '10px', 'border': f"1px solid {THEME['card_border']}"}, children=[
                    html.H5("Espectro de Fase", style={'color': THEME['accent_amber'], 'marginBottom': '8px'}),
                    html.P([
                        html.Span(r"$\angle C_k$", style={'color': THEME['accent_amber'], 'fontWeight': '700'}),
                        " vs ",
                        html.Span(r"$k\omega_0$", style={'color': THEME['text'], 'fontWeight': '700'}),
                        ". Muestra el desfase de cada armónico."
                    ], style={'color': THEME['text_muted'], 'fontSize': '13.5px', 'lineHeight': '1.8'}),
                ]),
            ]),

            html.Div(style=STYLE_CALLOUT, children=[
                html.Strong("Decaimiento de armónicos: "),
                "si ",
                html.Span(r"$x(t)$", style={'color': THEME['text'], 'fontWeight': '700'}),
                " tiene una discontinuidad, ",
                html.Span(r"$|C_k| \sim 1/k$", style={'color': THEME['accent_cyan'], 'fontWeight': '700'}),
                ". Si es continua pero con derivada discontinua, ",
                html.Span(r"$|C_k| \sim 1/k^2$", style={'color': THEME['accent_cyan'], 'fontWeight': '700'}),
                ". ¡Más suave la señal, más rápido decae su espectro!"
            ]),

            html.Div(className='edu-image-container', children=[
                html.Img(src='/assets/fourier_spectrum.gif', className='edu-image',
                         style={'maxHeight': '300px', 'objectFit': 'contain'})
            ]),
            html.Div("Espectro de magnitud y fase de una onda cuadrada", className='img-caption'),
        ]),

        # ===== PANEL 4: PROPIEDADES =====
        edu_card("Propiedades y Fenómeno de Gibbs", "fa-solid fa-bolt", [
            html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '14px'}, children=[
                html.Div(className='edu-subcard', style={'padding': '16px', 'borderRadius': '10px', 'border': f"1px solid {THEME['card_border']}"}, children=[
                    html.H5("Linealidad", style={'color': THEME['accent_cyan'], 'marginBottom': '12px'}),
                    html.Div(
                        r"Si $x(t) \leftrightarrow C_k$ y $y(t) \leftrightarrow D_k$, entonces $a\,x(t) + b\,y(t) \leftrightarrow a\,C_k + b\,D_k$.",
                        style={'color': THEME['text'], 'fontSize': '15px', 'lineHeight': '2'}
                    ),
                ]),
                html.Div(className='edu-subcard', style={'padding': '16px', 'borderRadius': '10px', 'border': f"1px solid {THEME['card_border']}"}, children=[
                    html.H5("Transformación de amplitud", style={'color': THEME['accent_emerald'], 'marginBottom': '12px'}),
                    html.Div(
                        r"$y(t) = A\,x(t) + B \;\Rightarrow\; C_{0y} = A\,C_{0x} + B,\;\; C_{ky} = A\,C_{kx}\;(k\neq 0)$",
                        style={'color': THEME['text'], 'fontSize': '15px', 'lineHeight': '2'}
                    ),
                ]),
                html.Div(className='edu-subcard', style={'padding': '16px', 'borderRadius': '10px', 'border': f"1px solid {THEME['card_border']}"}, children=[
                    html.H5("Desplazamiento temporal", style={'color': THEME['accent_purple'], 'marginBottom': '12px'}),
                    html.Div(
                        r"$y(t) = x(t - t_0) \;\Rightarrow\; C_{ky} = C_{kx}\,e^{-jk\omega_0 t_0}$",
                        style={'color': THEME['text'], 'fontSize': '15px', 'lineHeight': '2'}
                    ),
                ]),
                html.Div(className='edu-subcard', style={'padding': '16px', 'borderRadius': '10px', 'border': f"1px solid {THEME['card_border']}"}, children=[
                    html.H5("Inversión temporal", style={'color': THEME['accent_amber'], 'marginBottom': '12px'}),
                    html.Div(
                        r"$y(t) = x(-t) \;\Rightarrow\; C_{ky} = C_{kx}^*$ (conjugado)",
                        style={'color': THEME['text'], 'fontSize': '15px', 'lineHeight': '2'}
                    ),
                ]),
            ]),

            html.Div(style={'marginTop': '16px'}, children=[
                html.H5("Fenómeno de Gibbs", style={'color': THEME['accent_red'], 'marginBottom': '8px'}),
                html.P([
                    "Cerca de una discontinuidad, la serie truncada presenta sobreimpulsos que ",
                    html.Strong("no desaparecen al aumentar ", style={'color': THEME['accent_red']}),
                    html.Span(r"$N$", style={'color': THEME['accent_red'], 'fontWeight': '700'}),
                    ", sino que se acercan al ",
                    html.Span(r"$9\%$", style={'color': THEME['accent_red'], 'fontWeight': '700'}),
                    " de la altura del salto. El ancho de estos sobreimpulsos sí disminuye."
                ], style={'color': THEME['text'], 'fontSize': '14.5px', 'lineHeight': '1.9'}),
            ]),

            html.Div(className='edu-image-container', children=[
                html.Img(src='/assets/gibbs_phenomenon.png', className='edu-image',
                         style={'maxHeight': '280px', 'objectFit': 'contain'})
            ]),
            html.Div("Fenómeno de Gibbs: sobreimpulso cerca de discontinuidades", className='img-caption'),
        ]),

        # ===== PANEL 5: SIMULACIÓN =====
        html.Div(style=STYLE_EDU_CARD, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '10px', 'marginBottom': '14px'}, children=[
                html.I(className="fa-solid fa-flask", style={'fontSize': '22px', 'color': THEME['accent_cyan']}),
                html.H3("Laboratorio Interactivo de Series de Fourier",
                        style={'margin': '0', 'fontSize': '19px', 'fontWeight': '700', 'color': THEME['text']})
            ]),

            html.P([
                "Escribe tu propia señal x(t) o elige una predefinida, ajusta el número de armónicos ",
                "y explora cómo la serie truncada reconstruye la señal original."
            ], style={'color': THEME['text_muted'], 'fontSize': '14px', 'marginBottom': '18px'}),

            # ===== BLOQUE 1: DEFINICIÓN DE LA SEÑAL =====
            html.Div(className='edu-subcard', style={
                'padding': '18px', 'borderRadius': '12px',
                'border': f"1px solid {THEME['card_border']}", 'marginBottom': '18px'
            }, children=[
                html.H5(
                    [
                        html.I(className="fa-solid fa-1", style={'marginRight': '8px', 'color': THEME['accent_cyan']}),
                        "Define tu señal x(t)"
                    ],
                    style={'color': THEME['accent_cyan'], 'marginBottom': '12px', 'fontSize': '15px'}
                ),

                html.Label("Modo de señal:", style=STYLE_LABEL),
                dcc.RadioItems(
                    id='sys-fourier-signal-mode',
                    options=[
                        {'label': '  Predefinida', 'value': 'predefined'},
                        {'label': '  Personalizada (escribe tu función)', 'value': 'custom'},
                    ],
                    value='predefined',
                    inline=True,
                    labelStyle={'marginRight': '20px', 'color': THEME['text'], 'fontSize': '14px', 'cursor': 'pointer'}
                ),

                # --- Subpanel: Predefinida ---
                html.Div(id='sys-fourier-predefined-panel', children=[
                    html.Label("Tipo de Señal:", style=STYLE_LABEL),
                    dcc.Dropdown(
                        id='sys-fourier-signal-type',
                        options=[
                            {'label': 'Onda Cuadrada', 'value': 'square'},
                            {'label': 'Onda Triangular', 'value': 'triangle'},
                            {'label': 'Diente de Sierra', 'value': 'sawtooth'},
                            {'label': 'Tren de Impulsos', 'value': 'impulse'},
                        ],
                        value='square', clearable=False
                    ),
                ]),

                # --- Subpanel: Personalizada ---
                html.Div(id='sys-fourier-custom-panel', style={'display': 'none'}, children=[
                    html.Label("Función x(t):", style=STYLE_LABEL),
                    dcc.Input(
                        id='sys-fourier-custom-fn',
                        type='text',
                        value='2*sin(2*pi*t) + 0.5*cos(6*pi*t)',
                        placeholder='Ej: sin(2*pi*t) + 0.3*cos(6*pi*t)',
                        style={
                            'width': '100%', 'padding': '12px 14px',
                            'backgroundColor': THEME['bg_secondary'], 'border': f"1px solid {THEME['card_border']}",
                            'borderRadius': '8px', 'color': THEME['text'],
                            'fontFamily': '"Fira Code", "Consolas", monospace',
                            'fontSize': '14px', 'boxSizing': 'border-box'
                        }
                    ),
                    html.Div("Funciones disponibles: sin, cos, tan, exp, log, sqrt, abs, pi, e, heaviside",
                             style={'color': THEME['text_muted'], 'fontSize': '11.5px',
                                    'marginTop': '6px', 'fontStyle': 'italic'}),

                    html.Div(style={'display': 'flex', 'gap': '8px', 'marginTop': '10px'}, children=[
                        html.Button([
                            html.I(className="fa-solid fa-eye", style={'marginRight': '6px'}),
                            "Mostrar x(t)"
                        ], id='sys-btn-mostrar-fn', n_clicks=0, style=STYLE_MINI_BUTTON_GREEN),
                        html.Button([
                    html.I(className="fa-solid fa-rotate-left", style={'marginRight': '6px'}),
                         "Reset"
], id='sys-btn-reset-fn', n_clicks=0, style=STYLE_MINI_BUTTON_ALT),
                    ]),
                    html.Div(id='sys-fourier-fn-status', style={'marginTop': '8px', 'fontSize': '13px'}),
                ]),
            ]),

            # ===== BLOQUE 2: PARÁMETROS =====
            html.Div(className='edu-subcard', style={
                'padding': '18px', 'borderRadius': '12px',
                'border': f"1px solid {THEME['card_border']}", 'marginBottom': '18px'
            }, children=[
                html.H5(
                    [html.I(className="fa-solid fa-2", style={'marginRight': '8px', 'color': THEME['accent_cyan']}),
                        "Parámetros de la Serie"],
                    style={'color': THEME['accent_cyan'], 'marginBottom': '12px', 'fontSize': '15px'}
                ),
                html.Div(style={'display': 'flex', 'gap': '18px', 'flexWrap': 'wrap'}, children=[
                    html.Div(style={'flex': '1', 'minWidth': '220px'}, children=[
                        html.Label("Número de Armónicos (N):", style=STYLE_LABEL),
                        dcc.Slider(id='sys-fourier-n-harmonics', min=1, max=50, step=1, value=5,
                                   marks=make_slider_marks({1: '1', 10: '10', 25: '25', 50: '50'})),
                    ]),
                    html.Div(style={'flex': '1', 'minWidth': '220px'}, children=[
                        html.Label("Período T₀ (unidades arbitrarias):", style=STYLE_LABEL),
                        dcc.Slider(id='sys-fourier-T0', min=0.5, max=5, step=0.5, value=2,
                                   marks=make_slider_marks({0.5: '0.5', 2: '2', 5: '5'})),
                    ]),
                    html.Div(style={'flex': '1', 'minWidth': '220px'}, children=[
                        html.Label("Períodos a mostrar:", style=STYLE_LABEL),
                        dcc.Slider(id='sys-fourier-periods-view', min=1, max=5, step=1, value=3,
                                   marks=make_slider_marks({1: '1', 3: '3', 5: '5'})),
                    ]),
                    html.Div(style={'flex': '1', 'minWidth': '220px'}, children=[
                        html.Label("Escala del espectro:", style=STYLE_LABEL),
                        dcc.RadioItems(
                            id='sys-fourier-spectrum-scale',
                            options=[
                                {'label': ' Lineal', 'value': 'linear'},
                                {'label': ' dB', 'value': 'db'},
                            ],
                            value='linear', inline=True,
                            labelStyle={'marginRight': '14px', 'color': THEME['text'],
                                         'fontSize': '13px', 'cursor': 'pointer'}
                        ),
                    ]),
                ]),
            ]),

            # ===== BLOQUE 3: BOTÓN PRINCIPAL =====
            html.Div(style={'display': 'flex', 'justifyContent': 'center', 'gap': '12px',
                             'marginBottom': '20px', 'flexWrap': 'wrap'}, children=[
                html.Button([
                    html.I(className="fa-solid fa-play", style={'marginRight': '8px'}),
                    "Ejecutar Simulación"], id='sys-btn-simular-fourier', n_clicks=0,
                        className='nav-cta-btn',
                        style={'background': 'linear-gradient(135deg, #8b5cf6, #a78bfa)',
                               'padding': '14px 32px', 'fontSize': '16px'}),
                html.Button([
                    html.I(className="fa-solid fa-download", style={'marginRight': '8px'}),
                    "Exportar CSV"], id='sys-btn-exportar-fourier', n_clicks=0,
                        className='nav-cta-btn',
                        style={'background': 'linear-gradient(135deg, #065f46, #059669)',
                               'padding': '14px 32px', 'fontSize': '16px'}),
                dcc.Download(id='sys-download-fourier-csv'),
            ]),

            # ===== BLOQUE 4: GRÁFICOS PRINCIPALES =====
            html.Div(style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap'}, children=[
                html.Div(style={'flex': '1', 'minWidth': '340px'}, children=[
                    dcc.Graph(id='sys-fourier-graph-approx', config={'displayModeBar': False}),
                ]),
                html.Div(style={'flex': '1', 'minWidth': '340px'}, children=[
                    dcc.Graph(id='sys-fourier-graph-comparison', config={'displayModeBar': False}),
                ]),
            ]),

            html.Div(style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap', 'marginTop': '16px'}, children=[
                html.Div(style={'flex': '1', 'minWidth': '340px'}, children=[
                    dcc.Graph(id='sys-fourier-graph-error', config={'displayModeBar': False}),
                ]),
                html.Div(style={'flex': '1', 'minWidth': '340px'}, children=[
                    dcc.Graph(id='sys-fourier-graph-convergence', config={'displayModeBar': False}),
                ]),
            ]),

            html.Div(style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap', 'marginTop': '16px'}, children=[
                html.Div(style={'flex': '1', 'minWidth': '340px'}, children=[
                    dcc.Graph(id='sys-fourier-graph-spectrum-mag', config={'displayModeBar': False}),
                ]),
                html.Div(style={'flex': '1', 'minWidth': '340px'}, children=[
                    dcc.Graph(id='sys-fourier-graph-spectrum-phase', config={'displayModeBar': False}),
                ]),
            ]),

            # ===== BLOQUE 5: MÉTRICAS Y TABLA =====
            html.Div(style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap', 'marginTop': '20px'}, children=[
                html.Div(style={'flex': '1', 'minWidth': '320px'}, children=[
                    html.Div(id='sys-fourier-metrics-panel'),
                ]),
                html.Div(style={'flex': '1', 'minWidth': '320px'}, children=[
                    html.Div(id='sys-fourier-coeffs-table'),
                ]),
            ]),
        ]),

        # ===== PANEL 6: APLICACIÓN LTI =====
        edu_card("Aplicación: Respuesta de Sistemas LTI", "fa-solid fa-wrench", [
            html.P([
                "Si una señal periódica ",
                html.Span(r"$x(t)$", style={'color': THEME['text'], 'fontWeight': '700'}),
                " con coeficientes ",
                html.Span(r"$C_{kx}$", style={'color': THEME['accent_cyan'], 'fontWeight': '700'}),
                " entra a un sistema LTI con función de transferencia ",
                html.Span(r"$H(s)$", style={'color': THEME['accent_emerald'], 'fontWeight': '700'}),
                ", la salida en estado estacionario tiene coeficientes:"
            ], style={'color': THEME['text'], 'fontSize': '15px', 'lineHeight': '1.9'}),

            html.Div(className='edu-formula-box', style={
                'padding': '16px', 'borderRadius': '10px',
                'border': f"1px solid {THEME['card_border']}", 'textAlign': 'center', 'margin': '12px 0'
            }, children=[
                html.Div(r"$$C_{ky} = H(jk\omega_0) \cdot C_{kx}$$",
                    className='math-formula-callout',
                    style={'fontSize': '28px', 'fontWeight': '700',
                           'textAlign': 'center', 'padding': '16px', 'lineHeight': '2'})
            ]),

            html.P([
                "Esto significa que el sistema ",
                html.Strong("filtra cada armónico por separado", style={'color': THEME['accent_emerald']}),
                ": atenúa unos y amplifica otros según ",
                html.Span(r"$|H(j\omega)|$", style={'color': THEME['accent_emerald'], 'fontWeight': '700'}),
                ". Por eso una onda cuadrada filtrada pasa-bajas se convierte en una senoide (el primer armónico domina)."
            ], style={'color': THEME['text'], 'fontSize': '14.5px', 'lineHeight': '1.9'}),

            html.Div(style=STYLE_CALLOUT, children=[
                html.Strong("Ejemplo clásico: "),
                "un circuito RL con ",
                html.Span(r"$H(s) = \frac{1}{s+1}$", style={'color': THEME['accent_emerald'], 'fontWeight': '700'}),
                " convierte una onda cuadrada de entrada en una señal casi senoidal, porque atenúa los armónicos ",
                html.Span(r"$3\omega_0, 5\omega_0, \dots$", style={'color': THEME['text'], 'fontWeight': '700'}),
                " mucho más que el fundamental ",
                html.Span(r"$\omega_0$", style={'color': THEME['text'], 'fontWeight': '700'}),
                "."
            ]),

            html.Div(style={'marginTop': '14px'}, children=[
                dcc.Link("Ir al simulador de Control PID →", href='/sys/control', className='nav-cta-btn')
            ]),
        ]),
        next_section_link('/sys/convolucion', 'Convolución'),
        dcc.Store(id='sys-store-fourier-data', data={}),
    ])
# ═══════════════════════════════════════════════════════════════════════════════
# BLOQUE 5 — CONVOLUCIÓN (funciones de dominio + página)
# ═══════════════════════════════════════════════════════════════════════════════
PRESET_CONVOLUTIONS = {
    'rect_rect': {
        'name': 'Pulso rectangular ⊛ Pulso rectangular',
        'x_expr': 'heaviside(t) - heaviside(t - 2)',
        'h_expr': 'heaviside(t) - heaviside(t - 1)',
        't_range': (-1, 5),
        'description': 'Convolución de dos pulsos → trapecio.'
    },
    'exp_rect': {
        'name': 'Exponencial ⊛ Pulso rectangular',
        'x_expr': 'exp(-t)*heaviside(t)',
        'h_expr': 'heaviside(t) - heaviside(t - 2)',
        't_range': (-1, 6),
        'description': 'Respuesta de un filtro RC a un pulso.'
    },
    'gauss_gauss': {
        'name': 'Gaussiana ⊛ Gaussiana',
        'x_expr': 'exp(-t**2)',
        'h_expr': 'exp(-t**2)',
        't_range': (-5, 5),
        'description': 'Convolución de gaussianas → otra gaussiana más ancha.'
    },
    'sinc_rect': {
        'name': 'Sinc ⊛ Pulso (filtro ideal)',
        'x_expr': 'sin(pi*t)/(pi*t + 1e-10)',
        'h_expr': 'heaviside(t + 1) - heaviside(t - 1)',
        't_range': (-8, 8),
        'description': 'Filtro pasa-bajos ideal (sinc) sobre pulso.'
    },
    'step_exp': {
        'name': 'Escalón ⊛ Exponencial decreciente',
        'x_expr': 'heaviside(t)',
        'h_expr': 'exp(-2*t)*heaviside(t)',
        't_range': (-1, 6),
        'description': 'Respuesta de sistema RC a escalón unitario.'
    },
}


def compute_convolution_numeric(x, h, t):
    dt = float(t[1] - t[0])
    y_full = signal.convolve(x, h, mode='full') * dt
    t_conv_full = np.linspace(2 * t[0], 2 * t[-1], len(y_full))
    mask = (t_conv_full >= t[0]) & (t_conv_full <= t[-1])
    return t_conv_full[mask].astype(float), y_full[mask].astype(float)


def compute_convolution_animated(x, h, t, n_frames=60):
    t_min, t_max = float(t[0]), float(t[-1])
    frames = []
    t_samples = np.linspace(t_min, t_max, int(n_frames))

    for tk in t_samples:
        tk_f = float(tk)
        tau_shifted = tk_f - t
        h_shifted = np.interp(tau_shifted, t, h, left=0.0, right=0.0)
        product = x * h_shifted
        y_val = float(_trapz(product, t))
        frames.append({
            'tk': tk_f,
            'h_shifted': [float(v) for v in h_shifted],
            'product': [float(v) for v in product],
            'y_val': y_val
        })
    return frames, [float(v) for v in t_samples]


def build_conv_animation_figure(frame, t, x, tk, y_conv, t_conv):
    h_shifted = np.array(frame['h_shifted'])
    product = np.array(frame['product'])
    y_val = frame['y_val']
    tk = frame['tk']

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        subplot_titles=(
            f"x(τ)  y  h(t−τ)  [t = {tk:.2f}]",
            "Producto x(τ)·h(t−τ)  =  área → y(t)",
            "y(t) acumulada"
        ),
        vertical_spacing=0.12, row_heights=[0.35, 0.35, 0.30]
    )

    fig.add_trace(go.Scatter(
        x=t, y=x, mode='lines', name='x(τ)',
        line=dict(color='#38bdf8', width=2.5)
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=t, y=h_shifted, mode='lines', name='h(t−τ)',
        line=dict(color='#a855f7', width=2.5)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=t, y=product, mode='lines', name='producto',
        line=dict(color='#f59e0b', width=2.5),
        fill='tozeroy', fillcolor='rgba(245,158,11,0.25)'
    ), row=2, col=1)

    mask = t_conv <= tk
    if np.any(mask):
        fig.add_trace(go.Scatter(
            x=t_conv[mask], y=y_conv[mask], mode='lines',
            name='y(t)', line=dict(color='#10b981', width=2.5),
            fill='tozeroy', fillcolor='rgba(16,185,129,0.15)'
        ), row=3, col=1)
    fig.add_trace(go.Scatter(
        x=[tk], y=[y_val], mode='markers',
        marker=dict(color='#ef4444', size=12, symbol='circle',
                    line=dict(color='#ffffff', width=1.5)),
        name=f'y={y_val:.4f}'
    ), row=3, col=1)

    fig.update_layout(
        height=580, showlegend=False,
        template='plotly_dark', plot_bgcolor=THEME['card'],
        paper_bgcolor=THEME['card'],
        margin=dict(l=50, r=20, t=40, b=30)
    )
    fig.update_xaxes(title_text="τ (tiempo)", row=3, col=1)
    fig.update_xaxes(range=[float(t[0]), float(t[-1])], row=1, col=1)
    fig.update_xaxes(range=[float(t[0]), float(t[-1])], row=2, col=1)
    fig.update_xaxes(range=[float(t_conv[0]), float(t_conv[-1])], row=3, col=1)
    return fig


def page_convolucion():
    return html.Div(style=STYLE_CONTAINER, children=[
        page_header(
            "CONVOLUCIÓN",
            "La Operación Fundamental de los Sistemas LTI",
            "La convolución describe cómo un sistema LTI transforma una señal de entrada. "
            "y(t) = x(t) * h(t) = ∫ x(τ)·h(t−τ) dτ"
        ),

        edu_card("¿Qué es la Convolución?", "fa-solid fa-infinity", [
            html.P([
                "La convolución combina dos señales para producir una tercera. En sistemas LTI, "
                "si conoces la ", html.Strong("respuesta al impulso h(t)"),
                ", puedes predecir la salida para CUALQUIER entrada."
            ], style={'color': '#e2e8f0', 'fontSize': '15px', 'lineHeight': '1.9'}),

            html.Div(style={
                'background': '#0d1424', 'padding': '20px', 'borderRadius': '10px',
                'border': '1px solid #334155', 'textAlign': 'center', 'margin': '14px 0'
            }, children=[
                html.Div(r"$$y(t) = x(t) * h(t) = \int_{-\infty}^{\infty} x(\tau)\, h(t - \tau)\, d\tau$$",
                         style={'color': '#38bdf8', 'fontSize': '26px', 'fontWeight': '700', 'lineHeight': '2'}),
                html.Div(r"$$y[n] = x[n] * h[n] = \sum_{k=-\infty}^{\infty} x[k]\, h[n - k]$$",
                         style={'color': '#a855f7', 'fontSize': '24px', 'fontWeight': '700', 'lineHeight': '2', 'marginTop': '8px'}),
            ]),

            html.Div(style=STYLE_CALLOUT, children=[
                html.Strong("Interpretación gráfica (los 4 pasos): "),
                html.Ol([
                    html.Li([html.Strong("Reflejar: "), "obtener h(−τ)."]),
                    html.Li([html.Strong("Desplazar: "), "obtener h(t−τ) para cada t."]),
                    html.Li([html.Strong("Multiplicar: "), "x(τ)·h(t−τ) punto a punto."]),
                    html.Li([html.Strong("Integrar: "), "el área bajo el producto = y(t)."]),
                ], style={'marginTop': '8px', 'paddingLeft': '22px'})
            ]),
        ]),

        html.Div(style=STYLE_EDU_CARD, children=[
            html.H3([
                html.I(className="fa-solid fa-film", style={'marginRight': '10px', 'color': '#38bdf8'}),"Laboratorio Visual de Convolución"], style={'color': '#f8fafc', 'marginBottom': '16px'}),

            html.Div(style={
                'background': '#0d1424', 'padding': '18px', 'borderRadius': '12px',
                'border': '1px solid #334155', 'marginBottom': '18px'
            }, children=[
                html.H5("1. Elige un ejemplo o define tus señales",
                        style={'color': '#38bdf8', 'marginBottom': '12px'}),

                html.Label("Ejemplos rápidos:", style=STYLE_LABEL),
                html.Div(style={'display': 'flex', 'gap': '8px', 'flexWrap': 'wrap',
                                'marginBottom': '10px'}, children=[
                    html.Button([
                        html.I(className="fa-solid fa-square",
                            style={'marginRight': '8px', 'color': '#ffffff'}),
                        "Rect ⊛ Rect"
                    ], id='sys-conv-ex-rect', n_clicks=0,
                    style={**STYLE_MINI_BUTTON, 'background': 'linear-gradient(135deg, #1e40af, #3b82f6)'}),

                    html.Button([
                        html.I(className="fa-solid fa-arrow-trend-down",
                            style={'marginRight': '8px', 'color': '#ffffff'}),
                        "Exp ⊛ Rect"
                    ], id='sys-conv-ex-exp', n_clicks=0,
                    style={**STYLE_MINI_BUTTON, 'background': 'linear-gradient(135deg, #065f46, #059669)'}),

                    html.Button([
                        html.I(className="fa-solid fa-bell",
                            style={'marginRight': '8px', 'color': '#ffffff'}),
                        "Gauss ⊛ Gauss"
                    ], id='sys-conv-ex-gauss', n_clicks=0,
                    style={**STYLE_MINI_BUTTON, 'background': 'linear-gradient(135deg, #6d28d9, #8b5cf6)'}),

                    html.Button([
                        html.I(className="fa-solid fa-water",
                            style={'marginRight': '8px', 'color': '#ffffff'}),
                        "Sinc ⊛ Rect"
                    ], id='sys-conv-ex-sinc', n_clicks=0,
                    style={**STYLE_MINI_BUTTON, 'background': 'linear-gradient(135deg, #9d174d, #db2777)'}),

                    html.Button([
                        html.I(className="fa-solid fa-stairs",
                            style={'marginRight': '8px', 'color': '#ffffff'}),
                        "Escalón ⊛ Exp"
                    ], id='sys-conv-ex-step', n_clicks=0,
                    style={**STYLE_MINI_BUTTON, 'background': 'linear-gradient(135deg, #b45309, #d97706)'}),
                ]),

                html.Label("Ejemplo predefinido:", style=STYLE_LABEL),
                dcc.Dropdown(
                    id='sys-conv-preset',
                    options=[{'label': v['name'], 'value': k} for k, v in PRESET_CONVOLUTIONS.items()],
                    value='rect_rect', clearable=False
                ),

                html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr',
                                'gap': '14px', 'marginTop': '14px'}, children=[
                    html.Div([
                        html.Label("x(t) =", style=STYLE_LABEL),
                        dcc.Input(id='sys-conv-x-expr', type='text',
                                  value='heaviside(t) - heaviside(t - 2)',
                                  style=STYLE_CONTROL_INPUT),
                    ]),
                    html.Div([
                        html.Label("h(t) =", style=STYLE_LABEL),
                        dcc.Input(id='sys-conv-h-expr', type='text',
                                  value='heaviside(t) - heaviside(t - 1)',
                                  style=STYLE_CONTROL_INPUT),
                    ]),
                ]),
                html.Div(id='sys-conv-error', style={'marginTop': '8px'}),
            ]),

            html.Div(style={'display': 'flex', 'gap': '14px', 'flexWrap': 'wrap'}, children=[
                html.Div(style={'flex': '1', 'minWidth': '220px'}, children=[
                    html.Label("Duración de simulación (s):", style=STYLE_LABEL),
                    dcc.Slider(id='sys-conv-tmax', min=2, max=20, step=0.5, value=6,
                               marks=make_slider_marks({2: '2', 10: '10', 20: '20'})),
                ]),
                html.Div(style={'flex': '1', 'minWidth': '220px'}, children=[
                    html.Label("Número de frames:", style=STYLE_LABEL),
                    dcc.Slider(id='sys-conv-frames', min=20, max=120, step=10, value=60,
                               marks=make_slider_marks({20: '20', 60: '60', 120: '120'})),
                ]),
            ]),

            html.Div(style={'display': 'flex', 'justifyContent': 'center', 'gap': '12px',
                            'marginTop': '16px', 'marginBottom': '16px'}, children=[
                html.Button([html.I(className="fa-solid fa-play", style={'marginRight': '8px'}),
                             "Calcular Convolución"],
                            id='sys-btn-conv-run', n_clicks=0, className='nav-cta-btn',
                            style={'background': 'linear-gradient(135deg, #8b5cf6, #a78bfa)',
                                   'padding': '14px 32px', 'fontSize': '16px'}),
            ]),

            html.Div(style={'display': 'flex', 'justifyContent': 'center', 'gap': '10px',
                            'marginBottom': '12px'}, children=[
                html.Button([html.I(className="fa-solid fa-play", style={'marginRight': '6px'}), "Play"], id='sys-btn-conv-play', n_clicks=0, style=STYLE_MINI_BUTTON_GREEN),
                html.Button([html.I(className="fa-solid fa-pause", style={'marginRight': '6px'}), "Pause"], id='sys-btn-conv-pause', n_clicks=0, style=STYLE_MINI_BUTTON_AMBER),
                html.Button([html.I(className="fa-solid fa-backward-step", style={'marginRight': '6px'}), "Reset"], 
            id='sys-btn-conv-reset', n_clicks=0, style=STYLE_MINI_BUTTON_ALT),
                html.Span(id='sys-conv-frame-indicator',
                          style={'color': '#94a3b8', 'alignSelf': 'center', 'fontSize': '13px'}),
            ]),
            dcc.Interval(id='sys-conv-anim-interval', interval=250, n_intervals=0, disabled=True),

            dcc.Loading(
                type="circle",
                color="#38bdf8",
                children=[
                    dcc.Graph(id='sys-conv-graph-anim', config={'displayModeBar': False}),
                ]
            ),

            dcc.Graph(id='sys-conv-graph-result', config={'displayModeBar': False}),

            dcc.Store(id='sys-conv-frames-store', data={}),
            dcc.Store(id='sys-conv-current-frame', data=0),
            dcc.Store(id='sys-conv-playing', data=False),
        ]),

        edu_card("Propiedades de la Convolución", "fa-solid fa-list-check", [
            html.Table(style={'width': '100%', 'borderCollapse': 'collapse'}, children=[
                html.Thead(html.Tr([
                    html.Th("Propiedad", style={'padding': '10px', 'color': '#38bdf8',
                                                'textAlign': 'left', 'borderBottom': '2px solid #334155'}),
                    html.Th("Fórmula", style={'padding': '10px', 'color': '#38bdf8',
                                              'textAlign': 'left', 'borderBottom': '2px solid #334155'}),
                ])),
                html.Tbody([
                    html.Tr([html.Td("Conmutativa", style={'padding': '10px', 'color': '#e2e8f0'}),
                             html.Td("x * h = h * x", style={'padding': '10px', 'color': '#fcd34d', 'fontFamily': 'monospace'})]),
                    html.Tr([html.Td("Asociativa", style={'padding': '10px', 'color': '#e2e8f0'}),
                             html.Td("(x * h₁) * h₂ = x * (h₁ * h₂)", style={'padding': '10px', 'color': '#fcd34d', 'fontFamily': 'monospace'})]),
                    html.Tr([html.Td("Distributiva", style={'padding': '10px', 'color': '#e2e8f0'}),
                             html.Td("x * (h₁ + h₂) = x*h₁ + x*h₂", style={'padding': '10px', 'color': '#fcd34d', 'fontFamily': 'monospace'})]),
                    html.Tr([html.Td("Identidad", style={'padding': '10px', 'color': '#e2e8f0'}),
                             html.Td("x * δ = x", style={'padding': '10px', 'color': '#fcd34d', 'fontFamily': 'monospace'})]),
                    html.Tr([html.Td("Teorema de convolución", style={'padding': '10px', 'color': '#e2e8f0'}),
                             html.Td("F{x * h} = F{x} · F{h}", style={'padding': '10px', 'color': '#fcd34d', 'fontFamily': 'monospace'})]),
                ])
            ]),
        ]),

        next_section_link('/sys/fourier-tf', 'Transformada de Fourier'),
    ])


# ═══════════════════════════════════════════════════════════════════════════════
# BLOQUE 6 — TRANSFORMADA DE FOURIER
# ═══════════════════════════════════════════════════════════════════════════════
def estimate_bandwidth(freqs, mag):
    """Ancho de banda a -3 dB (solo frecuencias positivas)."""
    if len(mag) == 0 or np.max(mag) < 1e-12:
        return 0.0
    mask_pos = freqs >= 0
    f_pos = freqs[mask_pos]
    m_pos = mag[mask_pos]
    if len(m_pos) < 2:
        return 0.0
    peak = np.max(m_pos)
    if peak < 1e-12:
        return 0.0
    threshold = peak / np.sqrt(2)
    above = np.where(m_pos >= threshold)[0]
    if len(above) < 2:
        return 0.0
    return float(f_pos[above[-1]] - f_pos[above[0]])


def page_transformada_fourier():
    return html.Div(style=STYLE_CONTAINER, children=[
        page_header(
            "TRANSFORMADA DE FOURIER",
            "Análisis Espectral de Señales No Periódicas",
            "Generalización de la Serie de Fourier para señales no periódicas: el espectro se vuelve continuo."
        ),

        edu_card("De la Serie a la Transformada", "fa-solid fa-arrow-right-arrow-left", [
            html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr',
                            'gap': '14px'}, children=[
                html.Div(style={'background': '#0d1424', 'padding': '16px',
                                'borderRadius': '10px', 'border': '1px solid #334155'}, children=[
                    html.H5("Serie (periódica)", style={'color': '#38bdf8'}),
                    html.Div(r"$$x(t) = \sum_{k} C_k e^{jk\omega_0 t}$$",
                             style={'color': '#fcd34d', 'fontSize': '20px', 'textAlign': 'center'}),
                    html.P("Espectro discreto", style={'color': '#94a3b8', 'fontSize': '13px',
                                                       'textAlign': 'center'}),
                ]),
                html.Div(style={'background': '#0d1424', 'padding': '16px',
                                'borderRadius': '10px', 'border': '1px solid #334155'}, children=[
                    html.H5("Transformada (no periódica)", style={'color': '#10b981'}),
                    html.Div(r"$$X(j\omega) = \int_{-\infty}^{\infty} x(t) e^{-j\omega t} dt$$",
                             style={'color': '#fcd34d', 'fontSize': '20px', 'textAlign': 'center'}),
                    html.P("Espectro continuo", style={'color': '#94a3b8', 'fontSize': '13px',
                                                       'textAlign': 'center'}),
                ]),
            ]),
        ]),

        html.Div(style=STYLE_EDU_CARD, children=[
            html.H3([
                html.I(className="fa-solid fa-flask",
                       style={'marginRight': '10px', 'color': '#38bdf8'}),
                "Laboratorio de Transformada de Fourier"
            ], style={'color': '#f8fafc', 'display': 'flex', 'alignItems': 'center',
                      'margin': '0 0 16px 0'}),

            html.Label("Elige un ejemplo o escribe tu propia señal:", style=STYLE_LABEL),

            html.Div(style={'display': 'flex', 'gap': '8px', 'flexWrap': 'wrap',
                            'marginBottom': '14px'}, children=[
                html.Button([
                    html.I(className="fa-solid fa-arrow-trend-down",
                           style={'marginRight': '8px', 'color': '#ffffff'}),
                    "Pulso exponencial"
                ], id='sys-tf-ex-1', n_clicks=0,
                   style={**STYLE_MINI_BUTTON, 'background': 'linear-gradient(135deg, #1e40af, #3b82f6)'}),

                html.Button([
                    html.I(className="fa-solid fa-square",
                           style={'marginRight': '8px', 'color': '#ffffff'}),
                    "Pulso rectangular"
                ], id='sys-tf-ex-2', n_clicks=0,
                   style={**STYLE_MINI_BUTTON, 'background': 'linear-gradient(135deg, #6d28d9, #8b5cf6)'}),

                html.Button([
                    html.I(className="fa-solid fa-bell",
                           style={'marginRight': '8px', 'color': '#ffffff'}),
                    "Gaussiana"
                ], id='sys-tf-ex-3', n_clicks=0,
                   style={**STYLE_MINI_BUTTON, 'background': 'linear-gradient(135deg, #065f46, #059669)'}),

                html.Button([
                    html.I(className="fa-solid fa-wave-square",
                           style={'marginRight': '8px', 'color': '#ffffff'}),
                    "Senoide pura"
                ], id='sys-tf-ex-4', n_clicks=0,
                   style={**STYLE_MINI_BUTTON, 'background': 'linear-gradient(135deg, #b45309, #d97706)'}),

                html.Button([
                    html.I(className="fa-solid fa-water",
                           style={'marginRight': '8px', 'color': '#ffffff'}),
                    "Sinc (pasa-bajos)"
                ], id='sys-tf-ex-5', n_clicks=0,
                   style={**STYLE_MINI_BUTTON, 'background': 'linear-gradient(135deg, #9d174d, #db2777)'}),
            ]),

            html.Div(style={'display': 'flex', 'gap': '14px', 'flexWrap': 'wrap'}, children=[
                html.Div(style={'flex': '2', 'minWidth': '280px'}, children=[
                    html.Label("x(t) =", style=STYLE_LABEL),
                    dcc.Input(id='sys-tf-x-expr', type='text', value='exp(-t)*heaviside(t)',
                              placeholder='Ej: exp(-t)*heaviside(t)  ó  sin(2*pi*t)',
                              style=STYLE_CONTROL_INPUT),
                    html.Div([
                        html.I(className="fa-solid fa-lightbulb",
                               style={'marginRight': '6px', 'color': '#f59e0b',
                                      'fontSize': '11px'}),
                        "Puedes usar: sin, cos, exp, sqrt, abs, heaviside, pi, t"
                    ], style={'color': '#64748b', 'fontSize': '11.5px',
                              'marginTop': '6px', 'fontStyle': 'italic',
                              'display': 'flex', 'alignItems': 'center'}),
                ]),
                html.Div(style={'flex': '1', 'minWidth': '160px'}, children=[
                    html.Label("Rango t:", style=STYLE_LABEL),
                    dcc.Slider(id='sys-tf-trange', min=2, max=20, step=1, value=10),
                ]),
                html.Div(style={'flex': '1', 'minWidth': '160px'}, children=[
                    html.Label("Escala:", style=STYLE_LABEL),
                    dcc.Dropdown(id='sys-tf-scale', options=[
                        {'label': 'Lineal', 'value': 'linear'},
                        {'label': 'dB', 'value': 'db'},
                    ], value='linear', clearable=False),
                ]),
            ]),

            html.Div(style={'display': 'flex', 'justifyContent': 'center', 'gap': '12px',
                            'marginTop': '16px'}, children=[
                html.Button([
                    html.I(className="fa-solid fa-play", style={'marginRight': '8px'}),
                    "Calcular TF"
                ],
                    id='sys-btn-tf-run', n_clicks=0, className='nav-cta-btn',
                    style={'background': 'linear-gradient(135deg, #8b5cf6, #a78bfa)',
                           'padding': '14px 32px', 'fontSize': '16px'}),
            ]),

            html.Div(style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap',
                            'marginTop': '16px'}, children=[
                html.Div(style={'flex': '1', 'minWidth': '340px'}, children=[
                    dcc.Graph(id='sys-tf-graph-time', config={'displayModeBar': False}),
                ]),
                html.Div(style={'flex': '1', 'minWidth': '340px'}, children=[
                    dcc.Graph(id='sys-tf-graph-mag', config={'displayModeBar': False}),
                ]),
            ]),
            html.Div(style={'marginTop': '16px'}, children=[
                dcc.Graph(id='sys-tf-graph-phase', config={'displayModeBar': False}),
            ]),
            html.Div(id='sys-tf-props-panel', style={'marginTop': '16px'}),
        ]),

        next_section_link('/sys/muestreo', 'Muestreo y Aliasing'),
    ])


# ═══════════════════════════════════════════════════════════════════════════════
# BLOQUE 7 — MUESTREO Y ALIASING
# ═══════════════════════════════════════════════════════════════════════════════
def page_muestreo():
    return html.Div(style=STYLE_CONTAINER, children=[
        page_header(
            "MUESTREO Y ALIASING",
            "Teorema de Nyquist-Shannon",
            "Cómo muestrear señales continuas sin perder información."
        ),

        edu_card("Teorema de Nyquist-Shannon", "fa-solid fa-wave-square", [
            html.P([
                "Para reconstruir sin error una señal de ancho de banda ",
                html.Span("B", style={'color': '#38bdf8', 'fontWeight': '700'}),
                " (Hz), la frecuencia de muestreo debe cumplir:"
            ], style={'color': '#e2e8f0', 'fontSize': '15px'}),

            html.Div(style={'textAlign': 'center', 'padding': '16px',
                            'background': '#0d1424', 'borderRadius': '10px',
                            'border': '1px solid #334155', 'margin': '12px 0'}, children=[
                html.Div(r"$$f_s > 2B$$",
                         style={'color': '#fcd34d', 'fontSize': '28px', 'fontWeight': '700'}),
            ]),

            html.Div(style=STYLE_CALLOUT, children=[
                html.Strong("Aliasing: "),
                "si f_s < 2B, las frecuencias altas se 'pliegan' y aparecen como frecuencias falsas bajas."
            ]),
        ]),

        html.Div(style=STYLE_EDU_CARD, children=[
            html.H3([html.I(className="fa-solid fa-microscope", style={'marginRight': '10px', 'color': '#38bdf8'}),
                "Simulador de Muestreo y Aliasing"
            ], style={'color': '#f8fafc'}),

            html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr 1fr',
                            'gap': '14px', 'marginTop': '14px'}, children=[
                html.Div([
                    html.Label("Frecuencia de la señal (Hz):", style=STYLE_LABEL),
                    dcc.Slider(id='sys-samp-f-signal', min=1, max=20, step=0.5, value=5,
                               marks=make_slider_marks({1: '1', 10: '10', 20: '20'})),
                ]),
                html.Div([
                    html.Label("Frecuencia de muestreo fs (Hz):", style=STYLE_LABEL),
                    dcc.Slider(id='sys-samp-f-samp', min=1, max=50, step=0.5, value=20,
                               marks=make_slider_marks({1: '1', 20: '20', 50: '50'})),
                ]),
                html.Div([
                    html.Label("Tipo de señal:", style=STYLE_LABEL),
                    dcc.Dropdown(id='sys-samp-tipo', options=[
                        {'label': 'Seno', 'value': 'sin'},
                        {'label': 'Suma de senos', 'value': 'multitone'},
                        {'label': 'Chirp', 'value': 'chirp'},
                    ], value='sin', clearable=False),
                ]),
            ]),

            dcc.Graph(id='sys-samp-graph', config={'displayModeBar': False}),
            html.Div(id='sys-samp-alias-info', style={'marginTop': '12px'}),
        ]),

        next_section_link('/sys/control', 'Control de Señales'),
    ])


# ═══════════════════════════════════════════════════════════════════════════════
# BLOQUE 8 — CONTROL DE SEÑALES
# ═══════════════════════════════════════════════════════════════════════════════
def parse_transfer_function(tf_str):
    result = {'num': None, 'den': None, 'delay': 0.0, 'sys': None,
              'tf_str': tf_str, 'error': None}

    if not tf_str or not tf_str.strip():
        result['error'] = "Ingresa una función de transferencia."
        return result

    if not _SYMPY_OK:
        result['error'] = "Falta el paquete 'sympy' (pip install sympy) para parsear la TF."
        return result

    try:
        s = sp.symbols('s')
        expr_str = tf_str.strip().replace('^', '**')

        delay = 0.0
        delay_pattern = re.compile(
            r'(?:e|exp)\s*\*\*\s*\(\s*-\s*([0-9]*\.?[0-9]+)\s*\*?\s*s\s*\)'
        )
        m = delay_pattern.search(expr_str)
        if m:
            delay = float(m.group(1))
            expr_str = delay_pattern.sub('1', expr_str)

        expr = sp.sympify(expr_str, locals={'s': s})
        expr = sp.together(sp.simplify(expr))
        numer, denom = sp.fraction(expr)

        num_poly = sp.Poly(sp.expand(numer), s)
        den_poly = sp.Poly(sp.expand(denom), s)

        num_coeffs = [float(c) for c in num_poly.all_coeffs()]
        den_coeffs = [float(c) for c in den_poly.all_coeffs()]

        if all(abs(c) < 1e-14 for c in den_coeffs):
            result['error'] = "El denominador de la función de transferencia es nulo."
            return result

        result['num'] = num_coeffs
        result['den'] = den_coeffs
        result['delay'] = delay
        result['sys'] = signal.TransferFunction(num_coeffs, den_coeffs)

    except Exception as e:
        result['error'] = f"No se pudo interpretar la función de transferencia: {e}"

    return result


def _poly_terms_str(coeffs):
    sup = {2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶'}
    n = len(coeffs)
    parts = []
    for i, c in enumerate(coeffs):
        power = n - 1 - i
        if abs(c) < 1e-10:
            continue
        sign = '-' if c < 0 else '+'
        mag = abs(c)
        if power == 0:
            body = f"{mag:.3g}"
        elif power == 1:
            body = "s" if abs(mag - 1) < 1e-9 else f"{mag:.3g}s"
        else:
            base = "s" if abs(mag - 1) < 1e-9 else f"{mag:.3g}s"
            body = base + sup.get(power, f"^{power}")
        parts.append((sign, body))
    if not parts:
        return "0"
    out = ("-" if parts[0][0] == '-' else "") + parts[0][1]
    for sign, body in parts[1:]:
        out += f" {sign} {body}"
    return out


def format_tf_display(num, den, delay=0.0, tf_str=""):
    if num is None or den is None:
        return html.Div([
            html.Span("Sin función de transferencia válida cargada.", style={'color': '#94a3b8', 'fontSize': '13px'})
        ])

    num_str = _poly_terms_str(num)
    den_str = _poly_terms_str(den)
    delay_str = f" · e^(-{delay:g}s)" if delay and abs(delay) > 1e-12 else ""

    return html.Div(style={'textAlign': 'center', 'padding': '10px 6px'}, children=[
        html.Div(f"G(s){delay_str} =", style={'color': '#94a3b8', 'fontSize': '12.5px', 'marginBottom': '6px'}),
        html.Div(num_str, style={
            'color': '#38bdf8', 'fontSize': '18px', 'fontWeight': '700',
            'fontFamily': '"Fira Code", "Consolas", monospace',
            'paddingBottom': '6px', 'borderBottom': '2px solid #475569',
            'display': 'inline-block', 'minWidth': '140px'
        }),
        html.Div(den_str, style={
            'color': '#e2e8f0', 'fontSize': '18px', 'fontWeight': '700',
            'fontFamily': '"Fira Code", "Consolas", monospace',
            'paddingTop': '6px', 'display': 'block'
        }),
    ])


def build_closed_loop(num_g, den_g, kp, ki, kd):
    num_c = [kd, kp, ki]
    den_c = [1.0, 0.0]
    num_l = np.polymul(num_c, num_g)
    den_l = np.polymul(den_c, den_g)
    den_cl = np.polyadd(den_l, num_l)
    num_cl = num_l
    return num_cl, den_cl


def _apply_delay(t, y, delay):
    if not delay or delay <= 0 or len(t) < 2:
        return y
    dt = t[1] - t[0]
    shift = int(round(delay / dt))
    if shift <= 0:
        return y
    shifted = np.zeros_like(y)
    if shift < len(y):
        shifted[shift:] = y[:len(y) - shift]
    return shifted


def _build_input(t, input_type, amplitude, omega=2.0):
    if input_type == 'ramp':
        return amplitude * t
    elif input_type == 'sine':
        return amplitude * np.sin(omega * t)
    elif input_type == 'impulse':
        u = np.zeros_like(t)
        u[0] = amplitude / (t[1] - t[0]) if len(t) > 1 else amplitude
        return u
    return np.ones_like(t) * amplitude


def simulate_tf_response(num, den, t, input_type='step', amplitude=1.0, delay=0.0):
    try:
        sys_ = signal.TransferFunction(num, den)
        if input_type == 'step':
            _, y = signal.step(sys_, T=t)
            y = y * amplitude
        elif input_type == 'impulse':
            _, y = signal.impulse(sys_, T=t)
            y = y * amplitude
        else:
            u = _build_input(t, input_type, amplitude)
            _, y, _ = signal.lsim(sys_, U=u, T=t)
        y = np.nan_to_num(y, nan=0.0, posinf=1e6, neginf=-1e6)
        y = np.clip(y, -1e6, 1e6)
        y = _apply_delay(t, y, delay)
        return y
    except Exception:
        return np.zeros_like(t)


def analyze_control_metrics(y, t, setpoint=1.0):
    metrics = {}
    sp_ = setpoint if abs(setpoint) > 1e-9 else 1.0

    settle_threshold = 0.05 * abs(sp_)
    within = np.abs(y - sp_) <= settle_threshold
    settle_time = t[-1]
    for i in range(len(within) - 1, -1, -1):
        if not within[i]:
            settle_time = t[min(i + 1, len(t) - 1)]
            break
        settle_time = t[0]
    metrics['settle_time'] = float(settle_time)

    max_val = np.max(y) if len(y) else 0.0
    metrics['overshoot'] = float(max(0.0, (max_val - sp_) / sp_ * 100)) if sp_ != 0 else 0.0

    metrics['steady_state_error'] = float(abs(sp_ - y[-1]) / abs(sp_) * 100) if len(y) and sp_ != 0 else 0.0

    y10, y90 = 0.1 * sp_, 0.9 * sp_
    idx10 = np.where(y >= y10)[0] if sp_ > 0 else np.where(y <= y10)[0]
    idx90 = np.where(y >= y90)[0] if sp_ > 0 else np.where(y <= y90)[0]
    if len(idx10) and len(idx90):
        metrics['rise_time'] = float(t[idx90[0]] - t[idx10[0]])
    else:
        metrics['rise_time'] = 0.0

    return metrics


_PLOTLY_KW = dict(template="plotly_dark", plot_bgcolor=THEME['card'], paper_bgcolor=THEME['card'])


def plot_time_response(t, y_open, y_closed, setpoint, input_type, tf_active_str="1/(τs + 1)"):
    labels = {'step': 'Escalón', 'ramp': 'Rampa', 'sine': 'Senoidal', 'impulse': 'Impulso'}
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=y_open, mode='lines', name='Planta sin control (TF)',
                              line=dict(color='#64748b', width=2, dash='dot')))
    fig.add_trace(go.Scatter(x=t, y=y_closed, mode='lines', name='Planta con control PID',
                              line=dict(color='#38bdf8', width=2.5)))
    if input_type in ('step', 'ramp'):
        ref = np.ones_like(t) * setpoint if input_type == 'step' else setpoint * t
        fig.add_trace(go.Scatter(x=t, y=ref, mode='lines', name='Setpoint / Referencia',
                                  line=dict(color='#f59e0b', width=2, dash='dash')))
    fig.update_layout(
        title=(
            f"<b>Respuesta Temporal</b> — Entrada: {labels.get(input_type, 'Escalón')}<br>"
            f"<span style='font-size:12px;color:#94a3b8;font-weight:500'>Planta: G(s) = {tf_active_str}</span>"
        ),
        xaxis_title="Tiempo (s)", yaxis_title="Amplitud",
        height=380, margin=dict(l=45, r=20, t=70, b=35),
        legend=dict(orientation='h', yanchor='top', y=-0.12, xanchor='center', x=0.5),
        dragmode='pan', **_PLOTLY_KW
    )
    fig.update_xaxes(rangeslider_visible=False)
    return fig


def plot_control_signal(t, u):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=u, mode='lines', name='u(t)', line=dict(color='#a855f7', width=2)))
    fig.update_layout(
        title="<b>Señal de Control u(t)</b>", xaxis_title="Tiempo (s)", yaxis_title="u(t)",
        height=220, margin=dict(l=45, r=20, t=40, b=35), **_PLOTLY_KW
    )
    return fig


def plot_poles_zeros(num_g, den_g):
    try:
        z, p, _ = signal.tf2zpk(num_g, den_g)
    except Exception:
        z, p = np.array([]), np.array([])

    fig = go.Figure()

    max_re = max(1.0, np.max(np.abs(np.real(p))) if len(p) else 1.0, np.max(np.abs(np.real(z))) if len(z) else 1.0)
    max_im = max(1.0, np.max(np.abs(np.imag(p))) if len(p) else 1.0, np.max(np.abs(np.imag(z))) if len(z) else 1.0)
    max_re *= 1.4
    max_im *= 1.4

    fig.add_shape(type='rect', x0=-max_re, x1=0, y0=-max_im, y1=max_im,
                  fillcolor='rgba(16,185,129,0.08)', line=dict(width=0), layer='below')
    fig.add_vline(x=0, line_color='#475569', line_width=1)
    fig.add_hline(y=0, line_color='#475569', line_width=1)

    if len(p):
        fig.add_trace(go.Scatter(x=np.real(p), y=np.imag(p), mode='markers', name='Polos',
                                  marker=dict(symbol='x', size=13, color='#ef4444', line=dict(width=2))))
    if len(z):
        fig.add_trace(go.Scatter(x=np.real(z), y=np.imag(z), mode='markers', name='Ceros',
                                  marker=dict(symbol='circle-open', size=13, color='#38bdf8', line=dict(width=2))))

    fig.update_layout(
        title="<b>Plano S — Polos (x) y Ceros (o)</b>",
        xaxis_title="Re(s)", yaxis_title="Im(s)",
        height=380, margin=dict(l=45, r=20, t=45, b=35),
        xaxis=dict(range=[-max_re, max_re], zeroline=False),
        yaxis=dict(range=[-max_im, max_im], zeroline=False, scaleanchor='x', scaleratio=1),
        **_PLOTLY_KW
    )
    return fig


def plot_bode(num_g, den_g):
    try:
        sys_ = signal.TransferFunction(num_g, den_g)
        w, mag, phase = signal.bode(sys_, n=500)
    except Exception:
        w, mag, phase = np.logspace(-2, 2, 500), np.zeros(500), np.zeros(500)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                         subplot_titles=("<b>Magnitud</b>", "<b>Fase</b>"), vertical_spacing=0.12)
    fig.add_trace(go.Scatter(x=w, y=mag, mode='lines', line=dict(color='#38bdf8', width=2), name='Magnitud'), row=1, col=1)
    fig.add_hline(y=0, line_dash='dot', line_color='#64748b', row=1, col=1)
    fig.add_trace(go.Scatter(x=w, y=phase, mode='lines', line=dict(color='#f59e0b', width=2), name='Fase'), row=2, col=1)
    fig.add_hline(y=-180, line_dash='dot', line_color='#64748b', row=2, col=1)

    fig.update_xaxes(type='log', title_text='Frecuencia ω (rad/s)', row=2, col=1)
    fig.update_yaxes(title_text='Magnitud (dB)', row=1, col=1)
    fig.update_yaxes(title_text='Fase (°)', row=2, col=1)
    fig.update_layout(height=430, margin=dict(l=50, r=20, t=45, b=40), showlegend=False, **_PLOTLY_KW)
    return fig


def plot_root_locus(num_g, den_g, k_max=200.0, n_points=400):
    den_g = np.array(den_g, dtype=float)
    num_g = np.array(num_g, dtype=float)

    ks = np.concatenate([[0.0], np.logspace(-3, np.log10(k_max), n_points)])
    all_re, all_im, all_k = [], [], []

    for k in ks:
        char_poly = np.polyadd(den_g, k * num_g)
        roots = np.roots(char_poly)
        all_re.extend(np.real(roots))
        all_im.extend(np.imag(roots))
        all_k.extend([k] * len(roots))

    fig = go.Figure()
    fig.add_vline(x=0, line_color='#475569', line_width=1)
    fig.add_hline(y=0, line_color='#475569', line_width=1)
    fig.add_trace(go.Scatter(
        x=all_re, y=all_im, mode='markers',
        marker=dict(size=4, color=all_k, colorscale='Viridis', showscale=True,
                    colorbar=dict(title='K')),
        name='Lugar de las raíces'
    ))
    try:
        z0, p0, _ = signal.tf2zpk(num_g, den_g)
        fig.add_trace(go.Scatter(x=np.real(p0), y=np.imag(p0), mode='markers', name='Polos (K=0)',
                                  marker=dict(symbol='x', size=12, color='#ef4444')))
        fig.add_trace(go.Scatter(x=np.real(z0), y=np.imag(z0), mode='markers', name='Ceros',
                                  marker=dict(symbol='circle-open', size=12, color='#38bdf8')))
    except Exception:
        pass

    fig.update_layout(
        title="<b>Lugar de las Raíces (Root Locus)</b> — variando ganancia K de G(s)",
        xaxis_title="Re(s)", yaxis_title="Im(s)",
        height=430, margin=dict(l=45, r=20, t=45, b=35), **_PLOTLY_KW
    )
    return fig


def plot_nyquist(num_g, den_g):
    w = np.logspace(-3, 4, 3000)
    s_jw = 1j * w
    L = np.polyval(num_g, s_jw) / np.polyval(den_g, s_jw)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.real(L), y=np.imag(L), mode='lines', name='ω > 0',
                              line=dict(color='#38bdf8', width=2)))
    fig.add_trace(go.Scatter(x=np.real(L), y=-np.imag(L), mode='lines', name='ω < 0',
                              line=dict(color='#38bdf8', width=1.5, dash='dot')))
    fig.add_trace(go.Scatter(x=[-1], y=[0], mode='markers', name='Punto crítico (-1, 0)',
                              marker=dict(symbol='x', size=13, color='#ef4444')))
    fig.update_layout(
        title="<b>Diagrama de Nyquist</b>",
        xaxis_title="Re(L(jω))", yaxis_title="Im(L(jω))",
        height=430, margin=dict(l=45, r=20, t=45, b=35), **_PLOTLY_KW
    )
    return fig


def compute_stability_margins(num_g, den_g):
    try:
        sys_ = signal.TransferFunction(num_g, den_g)
        w, mag_db, phase = signal.bode(sys_, n=4000)
        mag_lin = 10 ** (mag_db / 20.0)

        phase_margin, w_gc = None, None
        sign_change = np.where(np.diff(np.sign(mag_db)))[0]
        if len(sign_change):
            i = sign_change[0]
            w_gc = w[i]
            ph = np.interp(0.0, [mag_db[i], mag_db[i + 1]], [phase[i], phase[i + 1]])
            phase_margin = 180.0 + ph

        gain_margin_db, w_pc = None, None
        sign_change2 = np.where(np.diff(np.sign(phase + 180.0)))[0]
        if len(sign_change2):
            i = sign_change2[0]
            w_pc = w[i]
            m = np.interp(-180.0, [phase[i], phase[i + 1]], [mag_db[i], mag_db[i + 1]])
            gain_margin_db = -m

        return {
            'phase_margin': phase_margin, 'w_gc': w_gc,
            'gain_margin_db': gain_margin_db, 'w_pc': w_pc,
        }
    except Exception:
        return {'phase_margin': None, 'w_gc': None, 'gain_margin_db': None, 'w_pc': None}


def build_stability_panel(margins, poles):
    unstable = any(np.real(p) > 1e-9 for p in poles) if len(poles) else False
    stability_pill = html.Span("INESTABLE" if unstable else "ESTABLE",
                                style=STYLE_MARGIN_PILL_BAD if unstable else STYLE_MARGIN_PILL_OK)

    def fmt(v, unit=""):
        return f"{v:.2f}{unit}" if v is not None else "N/D"

    pm = margins.get('phase_margin')
    gm = margins.get('gain_margin_db')
    pm_pill = STYLE_MARGIN_PILL_OK if (pm is not None and pm > 0) else STYLE_MARGIN_PILL_BAD
    gm_pill = STYLE_MARGIN_PILL_OK if (gm is not None and gm > 0) else STYLE_MARGIN_PILL_BAD

    return html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '14px', 'alignItems': 'center'}, children=[
        html.Div(["Estabilidad (polos en lazo abierto): ", stability_pill]),
        html.Div(["Margen de Fase: ", html.Span(fmt(pm, "°"), style=pm_pill),
                  html.Span(f"  (en ω={fmt(margins.get('w_gc'))} rad/s)" if margins.get('w_gc') else "",
                             style={'color': '#64748b', 'fontSize': '11px'})]),
        html.Div(["Margen de Ganancia: ", html.Span(fmt(gm, " dB"), style=gm_pill),
                  html.Span(f"  (en ω={fmt(margins.get('w_pc'))} rad/s)" if margins.get('w_pc') else "",
                             style={'color': '#64748b', 'fontSize': '11px'})]),
    ])


def export_to_csv(t, y_open, y_closed, u):
    buf = io.StringIO()
    buf.write("tiempo_s,planta_sin_control,planta_con_control,senal_control_u\n")
    for i in range(len(t)):
        buf.write(f"{t[i]:.6f},{y_open[i]:.6f},{y_closed[i]:.6f},{u[i]:.6f}\n")
    return buf.getvalue()


DEFAULT_TF = "1/(s^2 + 0.6*s + 1)"


def page_control():
    return html.Div(style=STYLE_CONTAINER, children=[
        page_header(
            "CONTROL DE SEÑALES",
            "Diseño de Controladores (PID) y Análisis de Sistemas",
            "Herramienta tipo MATLAB: ajusta parámetros PID, define funciones de transferencia reales "
            "(scipy.signal) y analiza estabilidad, polos/ceros, Bode, Root Locus y Nyquist."
        ),

        html.Div(style={'display': 'flex', 'gap': '16px', 'marginBottom': '18px', 'flexWrap': 'wrap'}, children=[

            html.Div(style={'flex': '3', 'minWidth': '250px'}, children=[
                html.Div(style=STYLE_CONTROL_CARD, children=[
                    html.H4("Parámetros de Control", style=STYLE_SECTION_TITLE),

                    html.Label("Kp (Ganancia Proporcional):", style=STYLE_LABEL),
                    dcc.Slider(id='sys-slider-kp', min=0, max=10, step=0.1, value=1.0,
                               marks=make_slider_marks({0: '0', 5: '5', 10: '10'})),

                    html.Label("Ki (Ganancia Integral):", style=STYLE_LABEL),
                    dcc.Slider(id='sys-slider-ki', min=0, max=5, step=0.1, value=0.0,
                               marks=make_slider_marks({0: '0', 2.5: '2.5', 5: '5'})),

                    html.Label("Kd (Ganancia Derivativa):", style=STYLE_LABEL),
                    dcc.Slider(id='sys-slider-kd', min=0, max=2, step=0.05, value=0.0,
                               marks=make_slider_marks({0: '0', 1: '1', 2: '2'})),

                    html.Label("Setpoint:", style=STYLE_LABEL),
                    dcc.Slider(id='sys-slider-setpoint', min=0.1, max=5, step=0.1, value=1.0,
                               marks=make_slider_marks({0.1: '0.1', 2.5: '2.5', 5: '5'})),

                    html.Label("Constante de tiempo τ (solo si no hay TF activa):", style=STYLE_LABEL),
                    dcc.Slider(id='sys-slider-tau', min=0.1, max=5, step=0.1, value=1.0,
                               marks=make_slider_marks({0.1: '0.1', 2.5: '2.5', 5: '5'})),

                    html.Div(style={'marginTop': '12px'}, children=[
                        html.Label("Presets rápidos:", style=STYLE_LABEL),
                        html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '6px'}, children=[
                            html.Button("P", id='sys-preset-p', n_clicks=0, style=STYLE_MINI_BUTTON_GREEN),
                            html.Button("PI", id='sys-preset-pi', n_clicks=0, style=STYLE_MINI_BUTTON),
                            html.Button("PID", id='sys-preset-pid', n_clicks=0, style=STYLE_MINI_BUTTON_ALT),
                            html.Button("Agresivo", id='sys-preset-aggressive', n_clicks=0, style=STYLE_MINI_BUTTON_AMBER),
                        ])
                    ]),
                ])
            ]),

            html.Div(style={'flex': '4.5', 'minWidth': '340px'}, children=[
                html.Div(style=STYLE_CONTROL_CARD, children=[
                    html.H4("Función de Transferencia G(s)", style=STYLE_SECTION_TITLE),

                    dcc.Input(
                        id='sys-input-transfer-function',
                        type='text',
                        value=DEFAULT_TF,
                        placeholder='Ej: 1/(s**2 + 0.5*s + 1)  ó  (s+1)/(s**2+0.3*s+1)',
                        style=STYLE_CONTROL_INPUT
                    ),

                    html.Div(style={'display': 'flex', 'gap': '8px', 'marginTop': '8px'}, children=[
                        html.Button([html.I(className="fa-solid fa-chart-column", style={'marginRight': '6px'}), "Mostrar"], 
                            id='sys-btn-mostrar-tf', n_clicks=0, style=STYLE_MINI_BUTTON_GREEN),
                        html.Button([html.I(className="fa-solid fa-play", style={'marginRight': '6px'}), "Aplicar PID"], 
                            id='sys-btn-aplicar-pid', n_clicks=0, style=STYLE_MINI_BUTTON),
                    html.Button([html.I(className="fa-solid fa-rotate-left", style={'marginRight': '6px'}), "Reset"], 
            id='sys-btn-reset-tf', n_clicks=0, style=STYLE_MINI_BUTTON_ALT),
                    ]),

                    html.Div(id='sys-tf-parse-error'),

                    html.Div(id='sys-display-tf-formula', style={'marginTop': '10px'}),

                    html.Div(style={
                        'marginTop': '14px', 'paddingTop': '12px',
                        'borderTop': '1px dashed #334155'
                    }, children=[
                        html.Div([
                            html.I(className="fa-solid fa-sitemap",
                                style={'marginRight': '8px', 'color': '#a855f7'}),
                            html.Span("Lazo abierto L(s) = C(s)·G(s)",
                                    style={'color': '#a855f7', 'fontWeight': '700', 'fontSize': '13px'})
                        ], style={'marginBottom': '8px'}),
                        html.Div(id='sys-display-lazo-abierto'),
                    ]),

                    dcc.Graph(id='sys-graph-poles-zeros', config={'displayModeBar': False}, style={'marginTop': '6px'}),
                ])
            ]),
            html.Div(style={'flex': '2.5', 'minWidth': '230px'}, children=[
                html.Div(style=STYLE_CONTROL_CARD, children=[
                    html.H4("Métricas de Rendimiento", style=STYLE_SECTION_TITLE),
                    html.Div(id='sys-control-metrics'),

                    html.Hr(style={'borderColor': '#374151', 'margin': '14px 0'}),
                    html.H4("Análisis de Estabilidad", style={**STYLE_SECTION_TITLE, 'fontSize': '16px'}),
                    html.Div(id='sys-control-stability-panel'),

                    html.Hr(style={'borderColor': '#374151', 'margin': '14px 0'}),
                    html.Label("Tipo de Entrada:", style=STYLE_LABEL),
                    dcc.Dropdown(
                        id='sys-dropdown-input-type', clearable=False, value='step',
                        options=[
                            {'label': 'Escalón', 'value': 'step'},
                            {'label': 'Rampa', 'value': 'ramp'},
                            {'label': 'Senoidal', 'value': 'sine'},
                            {'label': 'Impulso', 'value': 'impulse'},
                        ]
                    ),
                ])
            ]),
        ]),

        html.Div(style=STYLE_CONTROL_CARD, children=[
            html.Button(
                id='sys-btn-toggle-advanced', n_clicks=0, style=STYLE_ADVANCED_HEADER_BTN,
                children=[ html.Span([
                    html.I(className="fa-solid fa-screwdriver-wrench", style={'marginRight': '8px'}),
                    "Herramientas Avanzadas (Bode · Root Locus · Nyquist · Exportar)"
                ]),
                html.I(className="fa-solid fa-chevron-down", id='sys-advanced-toggle-arrow')
                ]
            ),
            html.Div(id='sys-advanced-tools-panel', style=STYLE_ADVANCED_PANEL_HIDDEN, children=[
                html.Div(style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap'}, children=[
                    html.Div(style={'flex': '1', 'minWidth': '360px'}, children=[dcc.Graph(id='sys-graph-bode', config={'displayModeBar': False})]),
                    html.Div(style={'flex': '1', 'minWidth': '360px'}, children=[dcc.Graph(id='sys-graph-root-locus', config={'displayModeBar': False})]),
                ]),
                html.Div(style={'marginTop': '10px'}, children=[dcc.Graph(id='sys-graph-nyquist', config={'displayModeBar': False})]),
                html.Div(style={'marginTop': '14px', 'display': 'flex', 'alignItems': 'center', 'gap': '12px'}, children=[
                    html.Button([html.I(className="fa-solid fa-file-csv", style={'marginRight': '6px'}), "Exportar Datos (CSV)"], 
                        id='sys-btn-export-csv', n_clicks=0, style=STYLE_MINI_BUTTON_GREEN),
                    dcc.Download(id='sys-download-control-csv'),
                ]),
            ]),
        ]),

        html.Div(style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap'}, children=[
            html.Div(style={'flex': '6', 'minWidth': '360px'}, children=[
                html.Div(style=STYLE_CONTROL_CARD, children=[
                    dcc.Graph(id='sys-graph-control-response'),
                    html.Div("Respuesta temporal: setpoint (naranja), planta sin control (gris punteado) "
                              "y planta con control PID (cian). Usa scroll/arrastre para zoom y pan.",
                              style=STYLE_GRAPH_DESC)
                ])
            ]),
        ]),

        html.Div(style=STYLE_CONTROL_CARD, children=[
            dcc.Graph(id='sys-graph-control-signal'),
            html.Div("Señal de control u(t) generada por el controlador PID.", style=STYLE_GRAPH_DESC)
        ]),

        dcc.Store(id='sys-store-control-tf', data={}),
        dcc.Store(id='sys-store-control-sim', data={}),
        dcc.Store(id='sys-store-advanced-open', data=False),

        next_section_link('/sys/actividades', 'Actividades'),
    ])

# ═══════════════════════════════════════════════════════════════════════════════
# BLOQUE 9 — ACTIVIDADES (Gemini + página + callbacks)
# ═══════════════════════════════════════════════════════════════════════════════
def generar_preguntas_con_gemini(tema="señales y sistemas", cantidad=5):
    """Genera preguntas de opción múltiple usando Gemini API."""
    try:
        if not gemini_service.is_available:
            return generar_preguntas_fallback(cantidad)
        prompt = f"""
        Eres un experto en Señales y Sistemas (Signals and Systems) y educación en ingeniería.
        Tu tarea es generar {cantidad} preguntas de opción múltiple para estudiantes universitarios.
        Las preguntas deben basarse en los siguientes conceptos clave:

        **CONCEPTOS FUNDAMENTALES (de un curso de Señales y Sistemas):**
        1. Series de Fourier: coeficientes, espectro de magnitud y fase, propiedades
        2. Fenómeno de Gibbs y convergencia de series de Fourier
        3. Transformada de Fourier y su relación con la serie
        4. Sistemas LTI: convolución, respuesta al impulso, función de transferencia
        5. Transformada de Laplace: polos, ceros, región de convergencia
        6. Estabilidad de sistemas: criterio de Routh-Hurwitz, ubicación de polos
        7. Controladores PID: acciones proporcional, integral y derivativa
        8. Diagramas de Bode: margen de ganancia y margen de fase
        9. Lugar de las raíces (Root Locus)
        10. Diagrama de Nyquist y criterio de estabilidad
        11. Respuesta temporal: tiempo de subida, tiempo de establecimiento, overshoot
        12. Teorema de Parseval y energía de señales
        13. Muestreo y teorema de Nyquist-Shannon
        14. Filtros: pasa-bajos, pasa-altos, pasa-banda

        **INSTRUCCIONES PARA LAS PREGUNTAS:**
        1. Cada pregunta debe ser clara, educativa y relevante para ingeniería
        2. Incluir 4 opciones (A, B, C, D) con una sola correcta
        3. Las opciones incorrectas deben ser plausibles pero claramente erróneas
        4. Incluir preguntas que conecten la teoría con aplicaciones prácticas
        5. Variar la dificultad: algunas fáciles, otras más desafiantes

        **FORMATO DE SALIDA (JSON):**
        [
            {{
                "pregunta": "¿Qué representa el coeficiente C₀ en la serie de Fourier de una señal periódica?",
                "opciones": {{
                    "A": "El valor promedio (componente DC) de la señal",
                    "B": "La frecuencia fundamental de la señal",
                    "C": "La potencia total de la señal",
                    "D": "El desfase inicial de la señal"
                }},
                "correcta": "A"
            }}
        ]

        **IMPORTANTE:**
        - Devuelve SOLO el JSON, sin texto adicional
        - Asegúrate de que las preguntas sean precisas y estén bien redactadas
        - Incluye al menos 1 pregunta sobre Series de Fourier y 1 sobre Control PID
        """

        preguntas = gemini_service.generar_json(prompt)
        if isinstance(preguntas, list) and len(preguntas) > 0:
            return preguntas
        return generar_preguntas_fallback(cantidad)

    except Exception as e:
        print(f"[SyS] [AVISO] Error Gemini: {e}. Usando preguntas de respaldo.")
        return generar_preguntas_fallback(cantidad)


def generar_preguntas_fallback(cantidad=5):
    """Preguntas predefinidas de Signals & Systems como respaldo."""
    banco_preguntas = [
        {
            "pregunta": "¿Qué representa el coeficiente C₀ en la serie de Fourier de una señal periódica?",
            "opciones": {
                "A": "El valor promedio (componente DC) de la señal",
                "B": "La frecuencia fundamental",
                "C": "La potencia total",
                "D": "El desfase inicial"
            },
            "correcta": "A"
        },
        {
            "pregunta": "¿Cómo decae la magnitud de los coeficientes de Fourier |Cₖ| para una onda cuadrada?",
            "opciones": {
                "A": "Proporcional a 1/k",
                "B": "Proporcional a 1/k²",
                "C": "Exponencialmente",
                "D": "No decae"
            },
            "correcta": "A"
        },
        {
            "pregunta": "¿Qué establece el fenómeno de Gibbs?",
            "opciones": {
                "A": "Aparece un sobreimpulso cerca de discontinuidades que no desaparece al aumentar N",
                "B": "La serie de Fourier siempre converge uniformemente",
                "C": "Los coeficientes decaen exponencialmente",
                "D": "La energía se conserva"
            },
            "correcta": "A"
        },
        {
            "pregunta": "¿Qué efecto tiene aumentar la ganancia integral Ki en un PID?",
            "opciones": {
                "A": "Elimina el error en estado estacionario pero puede aumentar el overshoot",
                "B": "Reduce el tiempo de subida",
                "C": "Aumenta la estabilidad del sistema",
                "D": "No tiene efecto en el error"
            },
            "correcta": "A"
        },
        {
            "pregunta": "¿Qué mide el margen de fase de un sistema en lazo abierto?",
            "opciones": {
                "A": "Cuánto se puede aumentar el desfase antes de volver el sistema inestable",
                "B": "La ganancia máxima del sistema",
                "C": "La frecuencia de resonancia",
                "D": "El error en estado estacionario"
            },
            "correcta": "A"
        },
        {
            "pregunta": "¿Qué representa el lugar de las raíces (Root Locus)?",
            "opciones": {
                "A": "La trayectoria de los polos del lazo cerrado al variar la ganancia K",
                "B": "La respuesta temporal del sistema",
                "C": "La ganancia del controlador",
                "D": "La frecuencia de muestreo"
            },
            "correcta": "A"
        },
        {
            "pregunta": "¿Cuál es la condición para que un sistema LTI sea estable?",
            "opciones": {
                "A": "Todos los polos deben estar en el semiplano izquierdo del plano s",
                "B": "Todos los ceros deben estar en el semiplano izquierdo",
                "C": "La ganancia debe ser mayor que 1",
                "D": "El sistema debe tener al menos un polo en el origen"
            },
            "correcta": "A"
        },
        {
            "pregunta": "¿Qué establece el teorema de Parseval?",
            "opciones": {
                "A": "La energía de la señal es igual a la suma de las energías de sus armónicos",
                "B": "La transformada de Fourier es invertible",
                "C": "La convolución en tiempo es producto en frecuencia",
                "D": "La señal debe ser periódica"
            },
            "correcta": "A"
        },
        {
            "pregunta": "¿Qué relación existe entre la transformada de Fourier y la serie de Fourier?",
            "opciones": {
                "A": "La serie de Fourier es un caso particular de la transformada para señales periódicas",
                "B": "Son completamente independientes",
                "C": "La transformada solo aplica a señales periódicas",
                "D": "La serie solo aplica a señales no periódicas"
            },
            "correcta": "A"
        },
        {
            "pregunta": "En un diagrama de Bode, ¿qué indica el margen de ganancia?",
            "opciones": {
                "A": "Cuánto se puede aumentar la ganancia antes de la inestabilidad",
                "B": "La frecuencia de cruce de fase",
                "C": "El ancho de banda",
                "D": "El tiempo de establecimiento"
            },
            "correcta": "A"
        },
    ]

    seleccionadas = random.sample(banco_preguntas, min(cantidad, len(banco_preguntas)))
    return seleccionadas


def page_actividades():
    return html.Div(style=STYLE_CONTAINER, children=[
        page_header(
            "ACTIVIDADES INTERACTIVAS",
            "Prueba de conocimientos de Señales y Sistemas",
            "Responde las preguntas y recibe tu retroalimentación."
        ),

        html.Div(style={'display': 'flex', 'gap': '15px', 'marginBottom': '20px', 'flexWrap': 'wrap'}, children=[
            html.Button(
                [html.I(className="fa-solid fa-arrows-rotate", style={'marginRight': '8px'}), "Generar Nuevas Preguntas"],
                id='sys-btn-generar-preguntas',
                n_clicks=0,
                className='nav-cta-btn',
                style={'background': 'linear-gradient(135deg, #0369a1, #0284c7)'}
            ),
            html.Button(
                [html.I(className="fa-solid fa-paper-plane", style={'marginRight': '8px'}), "Enviar Resultados"],
                id='sys-btn-enviar-resultados',
                n_clicks=0,
                className='nav-cta-btn',
                style={'background': 'linear-gradient(135deg, #065f46, #059669)'}
            ),
        ]),

        # ===== INFORMACIÓN DEL ESTUDIANTE =====
        html.Div(style=STYLE_QUIZ_CARD, children=[
            html.H4("Datos del Estudiante", style={'color': '#f8fafc', 'marginBottom': '12px', 'fontSize': '16px'}),
            html.Div(style={'display': 'flex', 'gap': '15px', 'flexWrap': 'wrap'}, children=[
                html.Div(style={'flex': '1', 'minWidth': '200px'}, children=[
                    html.Label("Nombre completo:", style={'color': '#94a3b8', 'fontSize': '13px', 'display': 'block', 'marginBottom': '4px'}),
                    dcc.Input(
                        id='sys-input-nombre-estudiante',
                        type='text',
                        placeholder='Ingresa tu nombre',
                        style={
                            'width': '100%',
                            'padding': '10px 14px',
                            'backgroundColor': '#1e293b',
                            'border': '1px solid #334155',
                            'borderRadius': '8px',
                            'color': '#ffffff',
                            'fontSize': '14px'
                        }
                    )
                ]),
                html.Div(style={'flex': '1', 'minWidth': '200px'}, children=[
                    html.Label("Correo electrónico:", style={'color': '#94a3b8', 'fontSize': '13px', 'display': 'block', 'marginBottom': '4px'}),
                    dcc.Input(
                        id='sys-input-correo-estudiante',
                        type='email',
                        placeholder='ejemplo@universidad.edu',
                        style={
                            'width': '100%',
                            'padding': '10px 14px',
                            'backgroundColor': '#1e293b',
                            'border': '1px solid #334155',
                            'borderRadius': '8px',
                            'color': '#ffffff',
                            'fontSize': '14px'
                        }
                    )
                ]),
            ]),
        ]),

        # ===== CONTENEDOR DE PREGUNTAS =====
        html.Div(id='sys-container-preguntas', children=[
            html.Div(style=STYLE_QUIZ_CARD, children=[
                html.P("Presiona 'Generar Nuevas Preguntas' para comenzar.",
                       style={'color': '#94a3b8', 'textAlign': 'center', 'fontSize': '16px'})
            ])
        ]),

        # ===== ÁREA DE TAREAS CON SUBIDA DE ARCHIVOS =====
        html.Div(style=STYLE_QUIZ_CARD, children=[
            html.H4([
                html.I(className="fa-solid fa-cloud-arrow-up", style={'marginRight': '8px', 'color': '#38bdf8'}),"Subir Tarea"
            ], style={'color': '#f8fafc', 'marginBottom': '12px', 'fontSize': '16px'}),
            html.P("Sube tu tarea en formato PDF, Word, o imagen. El archivo se guardará en la carpeta de tareas.",
                   style={'color': '#94a3b8', 'fontSize': '13px', 'marginBottom': '12px'}),

            html.Div(style={'display': 'flex', 'gap': '15px', 'flexWrap': 'wrap'}, children=[
                html.Div(style={'flex': '1', 'minWidth': '200px'}, children=[
                    html.Label("Nombre completo:", style={'color': '#94a3b8', 'fontSize': '13px', 'display': 'block', 'marginBottom': '4px'}),
                    dcc.Input(
                        id='sys-input-nombre-tarea',
                        type='text',
                        placeholder='Tu nombre completo',
                        style={
                            'width': '100%',
                            'padding': '10px 14px',
                            'backgroundColor': '#1e293b',
                            'border': '1px solid #334155',
                            'borderRadius': '8px',
                            'color': '#ffffff',
                            'fontSize': '14px'
                        }
                    )
                ]),
                html.Div(style={'flex': '1', 'minWidth': '200px'}, children=[
                    html.Label("Asignatura / Curso:", style={'color': '#94a3b8', 'fontSize': '13px', 'display': 'block', 'marginBottom': '4px'}),
                    dcc.Input(
                        id='sys-input-curso-tarea',
                        type='text',
                        placeholder='Ej: Señales y Sistemas',
                        style={
                            'width': '100%',
                            'padding': '10px 14px',
                            'backgroundColor': '#1e293b',
                            'border': '1px solid #334155',
                            'borderRadius': '8px',
                            'color': '#ffffff',
                            'fontSize': '14px'
                        }
                    )
                ]),
            ]),

            html.Div(style={'display': 'flex', 'gap': '15px', 'flexWrap': 'wrap', 'marginTop': '12px'}, children=[
                html.Div(style={'flex': '2', 'minWidth': '250px'}, children=[
                    html.Label("Descripción de la tarea:", style={'color': '#94a3b8', 'fontSize': '13px', 'display': 'block', 'marginBottom': '4px'}),
                    dcc.Textarea(
                        id='sys-textarea-tarea-descripcion',
                        placeholder='Describe brevemente tu tarea...',
                        style={
                            'width': '100%',
                            'minHeight': '80px',
                            'padding': '12px 14px',
                            'backgroundColor': '#1e293b',
                            'border': '1px solid #334155',
                            'borderRadius': '8px',
                            'color': '#e2e8f0',
                            'fontSize': '14px',
                            'resize': 'vertical'
                        }
                    )
                ]),

                html.Div(style={'flex': '1', 'minWidth': '200px'}, children=[
                    html.Label("Archivo de la tarea:", style={'color': '#94a3b8', 'fontSize': '13px', 'display': 'block', 'marginBottom': '4px'}),
                    dcc.Upload(
                        id='sys-upload-tarea-archivo',
                        children=html.Div([
                            html.I(className="fa-solid fa-cloud-arrow-up", style={'fontSize': '24px', 'color': '#38bdf8', 'display': 'block', 'marginBottom': '6px'}),
                            html.Div([
                                html.I(className="fa-solid fa-paperclip", style={'marginRight': '6px'}),"Arrastra o ",
                            html.Span("haz clic para subir", style={'color': '#38bdf8', 'textDecoration': 'underline'})," tu archivo"
                ])
                        ], style={
                            'border': '2px dashed #334155',
                            'borderRadius': '8px',
                            'padding': '24px 20px',
                            'textAlign': 'center',
                            'color': '#94a3b8',
                            'fontSize': '13px',
                            'cursor': 'pointer',
                            'height': '100%',
                            'minHeight': '80px',
                            'display': 'flex',
                            'flexDirection': 'column',
                            'alignItems': 'center',
                            'justifyContent': 'center'
                        }),
                        multiple=False
                    ),
                    html.Div(id='sys-upload-tarea-info', style={'color': '#38bdf8', 'fontSize': '12px', 'marginTop': '6px'})
                ]),
            ]),

            html.Div(style={'marginTop': '16px', 'display': 'flex', 'gap': '12px', 'flexWrap': 'wrap', 'alignItems': 'center'}, children=[
                html.Button(
                    [html.I(className="fa-solid fa-paper-plane", style={'marginRight': '8px'}), "Enviar Tarea"],
                    id='sys-btn-enviar-tarea',
                    n_clicks=0,
                    className='nav-cta-btn',
                    style={'background': 'linear-gradient(135deg, #8b5cf6, #a78bfa)'}
                ),
                html.Div(id='sys-mensaje-tarea-estado', style={'color': '#10b981', 'fontSize': '14px', 'fontWeight': '600'})
            ]),

            html.Hr(style={'borderColor': '#374151', 'margin': '18px 0 12px 0'}),
            html.Div([
                html.Span([
                    html.I(className="fa-solid fa-folder-open", style={'marginRight': '6px'}),"Tareas enviadas recientemente: "
                ], style={'color': '#94a3b8', 'fontSize': '13px'}),
                html.Span(id='sys-contador-tareas', style={'color': '#38bdf8', 'fontSize': '13px', 'fontWeight': '700'})
            ]),
        ]),

                # ===== MODAL DE RESULTADOS =====
        html.Div(id='sys-modal-resultados', style=STYLE_MODAL_OVERLAY_HIDDEN, children=[
            html.Div(style=STYLE_MODAL_BOX, children=[
                html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'flex-start', 'marginBottom': '14px'}, children=[
                    html.H3(
                        [html.I(className="fa-solid fa-chart-simple", style={'marginRight': '8px'}), "Resultados del Quiz"], 
                        style={'margin': '0', 'color': '#f8fafc', 'fontSize': '20px', 'fontWeight': '800'}
                    ),
                    html.Button(html.I(className="fa-solid fa-xmark"), id='sys-btn-cerrar-resultados', n_clicks=0, className='modal-close-btn')
                ]),
                html.Div(id='sys-modal-resultados-body')
            ])
        ]),

        # ===== STORE PARA GUARDAR ESTADO =====
        dcc.Store(id='sys-store-preguntas', data=[]),
        dcc.Store(id='sys-store-respuestas', data={}),
        dcc.Store(id='sys-store-resultados', data={}),
    ])


# ═══════════════════════════════════════════════════════════════════════════════
# BLOQUE 10 — INICIO + NAVEGACIÓN (sidebar + modal)
# ═══════════════════════════════════════════════════════════════════════════════
def page_inicio():
    return html.Div(style=STYLE_CONTAINER, children=[
        page_header(
            "SIGNALS AND SYSTEMS",
            "Procesamiento de Señales y Sistemas",
            "Un recorrido interactivo por el análisis de Fourier, el diseño de controladores PID y el análisis de sistemas lineales."
        ),

        html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(260px, 1fr))', 'gap': '18px'}, children=[
            edu_card("Series de Fourier", "fa-solid fa-chart-bar", [
                html.P("Descomposición espectral de señales periódicas: coeficientes, espectro, fenómeno de Gibbs.",
                       style={'color': '#cbd5e1', 'fontSize': '14px'}),
                dcc.Link("Explorar →", href='/sys/fourier',
                        style={'color': THEME['accent_cyan'], 'fontWeight': '700', 'fontSize': '13px', 'textDecoration': 'none'})
            ]),
            edu_card("Control de Señales", "fa-solid fa-sliders", [
                html.P("Diseño de controladores PID, funciones de transferencia, Bode, Root Locus y Nyquist.",
                       style={'color': '#cbd5e1', 'fontSize': '14px'}),
                dcc.Link("Explorar →", href='/sys/control',
                        style={'color': THEME['accent_cyan'], 'fontWeight': '700', 'fontSize': '13px', 'textDecoration': 'none'})
            ]),
        ]),
    ])


NAV_ITEMS = [
    ('fa-solid fa-arrow-left', 'Volver a Prometeo', '/'),
    ('fa-solid fa-house', 'Inicio SyS', '/sys'),
    ('fa-solid fa-chart-line', 'Series de Fourier', '/sys/fourier'),
    ('fa-solid fa-arrows-left-right', 'Convolución', '/sys/convolucion'),
    ('fa-solid fa-wave-square', 'Transformada Fourier', '/sys/fourier-tf'),
    ('fa-solid fa-signal', 'Muestreo & Aliasing', '/sys/muestreo'),
    ('fa-solid fa-sliders-h', 'Control de Señales', '/sys/control'),
    ('fa-solid fa-pencil', 'Actividades', '/sys/actividades'),
]


def build_sidebar():
    links = [
        dcc.Link(
            html.Div([
                html.I(
                    className=icon,
                    style={'marginRight': '12px', 'fontSize': '15px', 'width': '20px', 'textAlign': 'center', 'color': '#38bdf8'}
                ),
                html.Span(label, style={'fontSize': '13.5px', 'fontWeight': '600'})
            ], className='sidebar-link'),
            href=href, style={'textDecoration': 'none'}
        )
        for icon, label, href in NAV_ITEMS
    ]
    return html.Div(style=STYLE_SIDEBAR, children=[
        html.Div(style={'marginBottom': '28px', 'paddingLeft': '4px'}, children=[
            html.Div(
                html.I(className="fa-solid fa-infinity", style={'fontSize': '28px', 'color': '#38bdf8'}),
                style={'marginBottom': '4px'}
            ),
            html.Div("SyS", style={'fontSize': '18px', 'fontWeight': '800', 'color': '#ffffff', 'marginTop': '4px'}),
            html.Div("Signals and Systems", style={'fontSize': '11px', 'color': THEME['text_muted'], 'marginTop': '2px'})
        ]),
        html.Div(links, style={'display': 'flex', 'flexDirection': 'column'}),
        html.Div(style={'marginTop': '30px', 'paddingTop': '16px', 'borderTop': f"1px solid {THEME['card_border']}"}, children=[
            html.Div("Procesamiento de Señales", style={'fontSize': '10.5px', 'color': THEME['text_muted']}),
            html.Div("Fourier · Control · Sistemas", style={'fontSize': '13px', 'color': '#38bdf8', 'fontWeight': '700'})
        ])
    ])


modal = html.Div(id='sys-modal-overlay', style=STYLE_MODAL_OVERLAY_HIDDEN, children=[
    html.Div(style=STYLE_MODAL_BOX, children=[
        html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'flex-start', 'marginBottom': '14px'}, children=[
            html.H3(id='sys-modal-title', style={'margin': '0', 'color': '#f8fafc', 'fontSize': '20px', 'fontWeight': '800', 'paddingRight': '20px'}),
            html.Button(html.I(className="fa-solid fa-xmark"), id='sys-modal-close', n_clicks=0, className='modal-close-btn')
        ]),
        html.Div(id='sys-modal-body')
    ])
])


# ═══════════════════════════════════════════════════════════════════════════════
# BLOQUE 11 — LAYOUT Y REGISTRO DE CALLBACKS
# ═══════════════════════════════════════════════════════════════════════════════

def layout(pathname="/sys"):
    """Layout completo de la app Señales y Sistemas."""
    routes = {
        '/sys/fourier': page_fourier,
        '/sys/convolucion': page_convolucion,
        '/sys/fourier-tf': page_transformada_fourier,
        '/sys/muestreo': page_muestreo,
        '/sys/control': page_control,
        '/sys/actividades': page_actividades,
    }
    page_fn = routes.get(pathname, page_inicio)

    return html.Div(
        [
            build_sidebar(),
            html.Div(page_fn(), style=STYLE_CONTENT_AREA),
            modal,
        ],
        style={
            'display': 'flex',
            'minHeight': '100vh',
            'backgroundColor': THEME['bg'],
            'fontFamily': '"Inter", "Segoe UI", -apple-system, sans-serif',
        },
    )


def register_callbacks(app):
    """Registra todos los callbacks de la app SyS en la app global."""

    # -------------------------------------------------------------------------
    # 1. ROUTER INTERNO DE SyS
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # 1. (Router interno eliminado — lo maneja app.py con app_sys.layout)
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # 2. MODAL DEL GLOSARIO
    # -------------------------------------------------------------------------
    @app.callback(
        Output('sys-modal-overlay', 'style'),
        Output('sys-modal-title', 'children'),
        Output('sys-modal-body', 'children'),
        Input({'type': 'sys-term-link', 'term': ALL}, 'n_clicks'),
        Input('sys-modal-close', 'n_clicks'),
        prevent_initial_call=True
    )
    def toggle_modal(term_clicks, close_clicks):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id == 'sys-modal-close':
            return STYLE_MODAL_OVERLAY_HIDDEN, no_update, no_update

        try:
            parsed = json.loads(trigger_id)
            term_key = parsed.get('term')
        except (ValueError, AttributeError):
            raise PreventUpdate

        if not any(term_clicks):
            raise PreventUpdate

        entry = GLOSSARY.get(term_key)
        if not entry:
            raise PreventUpdate

        return STYLE_MODAL_OVERLAY_VISIBLE, entry['title'], entry['body']

    # -------------------------------------------------------------------------
    # 3. REGISTRO DE LOS 6 SUBMÓDULOS DE CALLBACKS
    # -------------------------------------------------------------------------
    _register_fourier_callbacks(app)
    _register_activities_callbacks(app)
    _register_control_callbacks(app)
    _register_convolucion_callbacks(app)
    _register_tf_callbacks(app)
    _register_muestreo_callbacks(app)


# ═══════════════════════════════════════════════════════════════════════════════
# SUBMÓDULOS DE CALLBACKS (envueltos, no a nivel de módulo)
# ═══════════════════════════════════════════════════════════════════════════════

def _register_fourier_callbacks(app):

    @app.callback(
        [Output('sys-fourier-predefined-panel', 'style'),
         Output('sys-fourier-custom-panel', 'style')],
        [Input('sys-fourier-signal-mode', 'value')],
        prevent_initial_call=True
    )
    def toggle_signal_mode(mode):
        if mode == 'custom':
            return {'display': 'none'}, {'display': 'block'}
        return {'display': 'block'}, {'display': 'none'}

    @app.callback(
        Output('sys-fourier-fn-status', 'children'),
        [Input('sys-btn-mostrar-fn', 'n_clicks'),
         Input('sys-btn-reset-fn', 'n_clicks')],
        [State('sys-fourier-custom-fn', 'value')],
        prevent_initial_call=True
    )
    def mostrar_fn_custom(n_mostrar, n_reset, fn_str):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger == 'sys-btn-reset-fn':
            fn_str = '2*sin(2*pi*t) + 0.5*cos(6*pi*t)'

        t_test = np.linspace(0, 4, 100)
        x_test, err = parse_user_signal(fn_str, t_test)
        if err:
            return html.Div([html.I(className="fa-solid fa-triangle-exclamation", style={"marginRight": "8px"}), err], style=STYLE_ERROR_BOX)
        return html.Div([
            html.Span([html.I(className="fa-solid fa-circle-check", style={"marginRight": "8px"}), "Expresión válida. x(t) = "], style={'color': '#10b981'}),
            html.Code(fn_str, style={'color': '#38bdf8', 'fontFamily': 'monospace',
                                      'fontSize': '13px'})
        ])

    @app.callback(
        [Output('sys-fourier-graph-approx', 'figure'),
         Output('sys-fourier-graph-comparison', 'figure'),
         Output('sys-fourier-graph-error', 'figure'),
         Output('sys-fourier-graph-convergence', 'figure'),
         Output('sys-fourier-graph-spectrum-mag', 'figure'),
         Output('sys-fourier-graph-spectrum-phase', 'figure'),
         Output('sys-fourier-metrics-panel', 'children'),
         Output('sys-fourier-coeffs-table', 'children'),
         Output('sys-store-fourier-data', 'data')],
        [Input('sys-btn-simular-fourier', 'n_clicks')],
        [State('sys-fourier-signal-mode', 'value'),
         State('sys-fourier-signal-type', 'value'),
         State('sys-fourier-custom-fn', 'value'),
         State('sys-fourier-n-harmonics', 'value'),
         State('sys-fourier-T0', 'value'),
         State('sys-fourier-periods-view', 'value'),
         State('sys-fourier-spectrum-scale', 'value'),
         State('theme-store', 'data')],
        prevent_initial_call=True
    )
    def simular_fourier(n_clicks, mode, signal_type, custom_fn, N, T0, n_periods, spec_scale, theme_mode='dark'):
        try:
            return _simular_fourier_impl(n_clicks, mode, signal_type, custom_fn, N, T0, n_periods, spec_scale, theme_mode=theme_mode)
        except Exception as e:
            print("=" * 70)
            print("[SyS] ERROR EN simular_fourier:")
            traceback.print_exc()
            print("=" * 70)
            is_light = (theme_mode == 'light')
            bg = "#ffffff" if is_light else THEME['card']
            fig_error = go.Figure()
            fig_error.update_layout(
                title=f"<b>Error:</b> {str(e)[:100]}",
                template="plotly_white" if is_light else "plotly_dark",
                plot_bgcolor=bg, paper_bgcolor=bg,
                font=dict(color="#0f172a" if is_light else "#f8fafc")
            )
            empty = go.Figure()
            empty.update_layout(template="plotly_white" if is_light else "plotly_dark",
                                plot_bgcolor=bg, paper_bgcolor=bg)
            return (fig_error, empty, empty, empty, empty, empty,
                html.Div(f"Error: {str(e)}",
                         style={'color': '#ef4444', 'padding': '12px'}),
                html.Div(""),
                {})

    @app.callback(
        Output('sys-download-fourier-csv', 'data'),
        [Input('sys-btn-exportar-fourier', 'n_clicks')],
        [State('sys-store-fourier-data', 'data')],
        prevent_initial_call=True
    )
    def exportar_fourier_csv(n_clicks, store_data):
        if not n_clicks or not store_data:
            raise PreventUpdate

        try:
            t = np.array(store_data['t'])
            x_orig = np.array(store_data['x_original'])
            x_approx = np.array(store_data['x_approx'])

            coeffs = {}
            for i, k in enumerate(store_data['coeffs_keys']):
                coeffs[k] = complex(store_data['coeffs_vals_real'][i],
                                    store_data['coeffs_vals_imag'][i])

            csv_text = export_fourier_to_csv(t, x_orig, x_approx, coeffs)
            return dict(content=csv_text, filename="fourier_simulacion.csv")
        except Exception:
            buf = io.StringIO()
            buf.write("tiempo,senal_original,senal_aproximada\n")
            for i in range(len(store_data['t'])):
                buf.write(f"{store_data['t'][i]:.6f},"
                          f"{store_data['x_original'][i]:.6f},"
                          f"{store_data['x_approx'][i]:.6f}\n")
            return dict(content=buf.getvalue(), filename="fourier_simulacion.csv")


def _simular_fourier_impl(n_clicks, mode, signal_type, custom_fn, N, T0, n_periods, spec_scale, theme_mode='dark'):
    """Implementación de la simulación de Fourier (llamada desde el callback)."""
    is_light = (theme_mode == 'light')
    template = "plotly_white" if is_light else "plotly_dark"
    plot_bg = "#ffffff" if is_light else THEME['card']
    paper_bg = "#ffffff" if is_light else THEME['card']
    font_color = "#0f172a" if is_light else "#f8fafc"
    cyan_line = "#0284c7" if is_light else "#38bdf8"
    amber_color = "#d97706" if is_light else "#f59e0b"
    emerald_color = "#059669" if is_light else "#10b981"
    border_c = "#e2e8f0" if is_light else "#334155"
    text_muted_c = "#64748b" if is_light else "#94a3b8"

    t = np.linspace(0, n_periods * T0, 2000)

    if mode == 'custom':
        x_original, err = parse_user_signal(custom_fn, t)
        if err:
            x_original = np.zeros_like(t)
            signal_name = "Expresión inválida"
        else:
            signal_name = f"x(t) = {custom_fn[:40]}..." if len(custom_fn) > 40 else f"x(t) = {custom_fn}"
        coeffs = compute_fourier_coeffs_numeric(x_original, t, T0, N=N)
    else:
        if signal_type == 'square':
            x_original = generate_square_wave(t, T0, V=1.0)
            coeffs = fourier_coefficients_square(T0, V=1.0, N=N)
            signal_name = "Onda Cuadrada"
        elif signal_type == 'triangle':
            x_original = generate_triangle_wave(t, T0, V=1.0)
            coeffs = fourier_coefficients_triangle(T0, V=1.0, N=N)
            signal_name = "Onda Triangular"
        elif signal_type == 'sawtooth':
            x_original = generate_sawtooth_wave(t, T0, V=1.0)
            coeffs = fourier_coefficients_sawtooth(T0, V=1.0, N=N)
            signal_name = "Diente de Sierra"
        else:
            x_original = generate_impulse_train(t, T0, V=1.0)
            coeffs = fourier_coefficients_square(T0, V=1.0, N=N)
            signal_name = "Tren de Impulsos"

    x_approx = reconstruct_signal_from_coeffs(t, coeffs, T0)
    error = x_original - x_approx
    mse = compute_mse(x_original, x_approx)
    rmse = float(np.sqrt(mse))
    max_err = float(np.max(np.abs(error))) if len(error) > 0 else 0.0
    freqs, mags, phases = compute_spectrum(coeffs)

    energy_total = compute_energy(coeffs)
    dt = t[1] - t[0]
    energy_signal = float(_trapz(x_original ** 2, t) / T0) if T0 > 0 else 0.0
    pct_energy = (energy_total / energy_signal * 100) if energy_signal > 0 else 0.0

    # ===== GRÁFICO 1: Aproximación =====
    fig_approx = go.Figure()
    fig_approx.add_trace(go.Scatter(x=t, y=x_original, mode='lines', name='x(t) original',
                                     line=dict(color='#64748b', width=2, dash='dot')))
    fig_approx.add_trace(go.Scatter(x=t, y=x_approx, mode='lines', name=f'xₙ(t) N={N}',
                                     line=dict(color=cyan_line, width=2.5)))
    fig_approx.update_layout(
        title=f"<b>{signal_name}</b> — Aproximación con N={N}",
        xaxis_title="Tiempo (s)", yaxis_title="Amplitud",
        height=340, template=template, plot_bgcolor=plot_bg, paper_bgcolor=paper_bg,
        font=dict(color=font_color),
        margin=dict(l=45, r=20, t=50, b=35),
        legend=dict(orientation='h', yanchor='top', y=-0.18, xanchor='center', x=0.5)
    )

    # ===== GRÁFICO 2: Comparación =====
    fig_comp = make_subplots(rows=2, cols=1, shared_xaxes=True,
                              subplot_titles=("Original", f"Reconstrucción N={N}"),
                              vertical_spacing=0.15)
    fig_comp.add_trace(go.Scatter(x=t, y=x_original, mode='lines',
                                   line=dict(color=emerald_color, width=2), name='Original'),
                        row=1, col=1)
    fig_comp.add_trace(go.Scatter(x=t, y=x_approx, mode='lines',
                                   line=dict(color=cyan_line, width=2), name=f'N={N}'),
                        row=2, col=1)
    fig_comp.update_xaxes(title_text="Tiempo (s)", row=2, col=1)
    fig_comp.update_layout(height=340, template=template,
                            plot_bgcolor=plot_bg, paper_bgcolor=paper_bg,
                            font=dict(color=font_color),
                            showlegend=False, margin=dict(l=45, r=20, t=50, b=35))

    # ===== GRÁFICO 3: Error =====
    fig_error = go.Figure()
    fig_error.add_trace(go.Scatter(x=t, y=error, mode='lines', name='e(t)',
                                    line=dict(color='#ef4444', width=2)))
    fig_error.add_hline(y=0, line_dash='dash', line_color='#64748b')
    fig_error.update_layout(
        title=f"<b>Error de Aproximación</b> — MSE = {mse:.5f}",
        xaxis_title="Tiempo (s)", yaxis_title="e(t)",
        height=320, template=template, plot_bgcolor=plot_bg, paper_bgcolor=paper_bg,
        font=dict(color=font_color),
        margin=dict(l=45, r=20, t=50, b=35)
    )

    # ===== GRÁFICO 4: Convergencia =====
    try:
        Ns, mses, energies, total_e = compute_convergence_curve(x_original, t, T0, N_max=min(50, N * 2 + 5))
        fig_conv = make_subplots(specs=[[{"secondary_y": True}]])
        fig_conv.add_trace(go.Scatter(x=Ns, y=mses, mode='lines+markers',
                                       name='MSE(N)',
                                       line=dict(color='#ef4444', width=2),
                                       marker=dict(size=5)),
                            secondary_y=False)
        if total_e > 0:
            pct_e = [100 * e / total_e for e in energies]
            fig_conv.add_trace(go.Scatter(x=Ns, y=pct_e, mode='lines+markers',
                                           name='Energía capturada (%)',
                                           line=dict(color=emerald_color, width=2),
                                           marker=dict(size=5)),
                                secondary_y=True)
        fig_conv.update_xaxes(title_text="N (armónicos)")
        fig_conv.update_yaxes(title_text="MSE", secondary_y=False, color='#ef4444')
        fig_conv.update_yaxes(title_text="% Energía (Parseval)", secondary_y=True, color=emerald_color)
        fig_conv.update_layout(
            title="<b>Convergencia de la Serie Truncada</b>",
            height=320, template=template, plot_bgcolor=plot_bg, paper_bgcolor=paper_bg,
            font=dict(color=font_color),
            margin=dict(l=45, r=55, t=50, b=35),
            legend=dict(orientation='h', yanchor='top', y=-0.18, xanchor='center', x=0.5)
        )
    except Exception:
        fig_conv = go.Figure()
        fig_conv.update_layout(title="<b>Convergencia</b> — No disponible",
                                height=320, template=template,
                                plot_bgcolor=plot_bg, paper_bgcolor=paper_bg,
                                font=dict(color=font_color))

    # ===== GRÁFICO 5: Espectro de magnitud =====
    if spec_scale == 'db':
        mags_plot = 20 * np.log10(np.maximum(mags, 1e-12))
        y_title = "Magnitud (dB)"
    else:
        mags_plot = mags.copy()
        y_title = "|Cₖ|"

    fig_mag = go.Figure()
    fig_mag.add_trace(go.Bar(
        x=freqs, y=mags_plot, name='|Cₖ|',
        marker_color=cyan_line,
        marker_line=dict(color='#0284c7' if is_light else '#0ea5e9', width=1)
    ))
    fig_mag.update_layout(
        title="<b>Espectro de Magnitud</b>",
        xaxis_title="Armónico k", yaxis_title=y_title,
        height=320, template=template, plot_bgcolor=plot_bg, paper_bgcolor=paper_bg,
        font=dict(color=font_color),
        margin=dict(l=45, r=20, t=50, b=35)
    )

    # ===== GRÁFICO 6: Espectro de fase =====
    fig_phase = go.Figure()
    fig_phase.add_trace(go.Bar(
        x=freqs, y=phases, name='∠Cₖ',
        marker_color=amber_color,
        marker_line=dict(color='#b45309' if is_light else '#d97706', width=1)
    ))
    fig_phase.update_layout(
        title="<b>Espectro de Fase</b>",
        xaxis_title="Armónico k", yaxis_title="Fase (°)",
        height=320, template=template, plot_bgcolor=plot_bg, paper_bgcolor=paper_bg,
        font=dict(color=font_color),
        margin=dict(l=45, r=20, t=50, b=35)
    )

    # ===== MÉTRICAS =====
    num_armonicos_activos = sum(1 for k in coeffs if abs(coeffs[k]) > 1e-9)
    energia = compute_energy(coeffs)

    metrics_html = html.Div(className='edu-subcard', style={
        'backgroundColor': '#ffffff' if is_light else '#1e293b', 'padding': '16px', 'borderRadius': '10px',
        'border': f"1px solid {border_c}", 'display': 'flex', 'gap': '20px', 'flexWrap': 'wrap',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.04)' if is_light else 'none'
    }, children=[
        html.Div([
            html.Div("Señal", style={'color': text_muted_c, 'fontSize': '11px'}),
            html.Div(signal_name, style={'color': cyan_line, 'fontWeight': '700', 'fontSize': '13px'})
        ]),
        html.Div([
            html.Div("Armónicos activos", style={'color': text_muted_c, 'fontSize': '11px'}),
            html.Div(f"{num_armonicos_activos}", style={'color': emerald_color, 'fontWeight': '700', 'fontSize': '13px'})
        ]),
        html.Div([
            html.Div("MSE", style={'color': text_muted_c, 'fontSize': '11px'}),
            html.Div(f"{mse:.5f}", style={'color': '#dc2626' if is_light else '#ef4444', 'fontWeight': '700', 'fontSize': '13px'})
        ]),
        html.Div([
            html.Div("RMSE", style={'color': text_muted_c, 'fontSize': '11px'}),
            html.Div(f"{rmse:.5f}", style={'color': '#dc2626' if is_light else '#ef4444', 'fontWeight': '700', 'fontSize': '13px'})
        ]),
        html.Div([
            html.Div("Error máx.", style={'color': text_muted_c, 'fontSize': '11px'}),
            html.Div(f"{max_err:.4f}", style={'color': amber_color, 'fontWeight': '700', 'fontSize': '13px'})
        ]),
        html.Div([
            html.Div("Energía (Parseval)", style={'color': text_muted_c, 'fontSize': '11px'}),
            html.Div(f"{energia:.4f}", style={'color': amber_color, 'fontWeight': '700', 'fontSize': '13px'})
        ]),
        html.Div([
            html.Div("% Energía capturada", style={'color': text_muted_c, 'fontSize': '11px'}),
            html.Div(f"{pct_energy:.1f}%", style={'color': emerald_color, 'fontWeight': '700', 'fontSize': '13px'})
        ]),
    ])

    coeffs_table = compute_coeffs_table(coeffs, max_rows=15, theme_mode=theme_mode)

    store_data = {
        't': t.tolist(),
        'x_original': x_original.tolist(),
        'x_approx': x_approx.tolist(),
        'coeffs_keys': list(coeffs.keys()),
        'coeffs_vals_real': [float(np.real(coeffs[k])) for k in coeffs.keys()],
        'coeffs_vals_imag': [float(np.imag(coeffs[k])) for k in coeffs.keys()],
        'signal_name': signal_name,
    }

    return (fig_approx, fig_comp, fig_error, fig_conv, fig_mag, fig_phase,
            metrics_html, coeffs_table, store_data)


def _register_activities_callbacks(app):

    # 1. GENERAR PREGUNTAS
    @app.callback(
        [Output('sys-store-preguntas', 'data'),
         Output('sys-store-respuestas', 'data'),
         Output('sys-container-preguntas', 'children'),
         Output('sys-modal-resultados', 'style')],
        [Input('sys-btn-generar-preguntas', 'n_clicks')],
        prevent_initial_call=True
    )
    def generar_preguntas(n_clicks):
        if not n_clicks:
            raise PreventUpdate

        preguntas = generar_preguntas_con_gemini(cantidad=5)
        if not preguntas:
            preguntas = generar_preguntas_fallback(5)

        children = []
        for idx, p in enumerate(preguntas):
            p['indice'] = idx
            opciones_html = []
            letras = ['A', 'B', 'C', 'D']
            for letra in letras:
                if letra in p['opciones']:
                    opciones_html.append(
                        html.Div(
                            html.Button(
                                f"{letra}. {p['opciones'][letra]}",
                                id={'type': 'sys-opcion-respuesta', 'indice': idx, 'letra': letra},
                                n_clicks=0,
                                style=STYLE_OPTION_BUTTON
                            ),
                            style={'marginBottom': '8px'}
                        )
                    )

            children.append(
                html.Div(style=STYLE_QUIZ_CARD, children=[
                    html.H4(
                        f"Pregunta {idx+1}: {p['pregunta']}",
                        style={'color': '#f8fafc', 'fontSize': '16px', 'marginBottom': '12px'}
                    ),
                    html.Div(opciones_html),
                    html.Div(
                        id={'type': 'sys-feedback-pregunta', 'indice': idx},
                        style={'marginTop': '10px', 'fontSize': '13px', 'color': '#94a3b8'}
                    )
                ])
            )

        children.append(
            html.Div(style={'display': 'flex', 'justifyContent': 'center', 'marginTop': '15px'}, children=[
                html.Button(
                    [html.I(className="fa-solid fa-circle-check", style={"marginRight": "8px"}), "Verificar Respuestas"],
                    id='sys-btn-verificar-respuestas',
                    n_clicks=0,
                    className='nav-cta-btn',
                    style={'background': 'linear-gradient(135deg, #065f46, #059669)'}
                )
            ])
        )

        return preguntas, {}, children, STYLE_MODAL_OVERLAY_HIDDEN

    # 2. SELECCIONAR OPCIÓN
        # 2. SELECCIONAR OPCIÓN
    @app.callback(
        [Output({'type': 'sys-opcion-respuesta', 'indice': ALL, 'letra': ALL}, 'style', allow_duplicate=True),
         Output('sys-store-respuestas', 'data', allow_duplicate=True)],
        [Input({'type': 'sys-opcion-respuesta', 'indice': ALL, 'letra': ALL}, 'n_clicks')],
        [State({'type': 'sys-opcion-respuesta', 'indice': ALL, 'letra': ALL}, 'id'),
         State('sys-store-respuestas', 'data')],
        prevent_initial_call=True
    )
    def seleccionar_opcion(n_clicks_list, id_list, respuestas_actuales):
        ctx = callback_context
        if not ctx.triggered or not any(n_clicks_list):
            raise PreventUpdate

        respuestas = dict(respuestas_actuales) if respuestas_actuales else {}
        trigger = ctx.triggered[0]
        trigger_id = json.loads(trigger['prop_id'].split('.')[0])
        idx_seleccionado = trigger_id['indice']
        letra_seleccionada = trigger_id['letra']

        respuestas[str(idx_seleccionado)] = letra_seleccionada

        nuevos_estilos = []
        for id_item in id_list:
            item_idx_str = str(id_item['indice'])
            if item_idx_str in respuestas and respuestas[item_idx_str] == id_item['letra']:
                nuevos_estilos.append(STYLE_OPTION_SELECTED)
            else:
                nuevos_estilos.append(STYLE_OPTION_BUTTON)

        return nuevos_estilos, respuestas

    # 3. VERIFICAR O ENVIAR RESULTADOS
    @app.callback(
        [Output('sys-modal-resultados', 'style', allow_duplicate=True),
         Output('sys-modal-resultados-body', 'children')],
        [Input('sys-btn-verificar-respuestas', 'n_clicks'),
         Input('sys-btn-enviar-resultados', 'n_clicks'),
         Input('sys-btn-cerrar-resultados', 'n_clicks')],
        [State('sys-store-preguntas', 'data'),
         State('sys-store-respuestas', 'data'),
         State('sys-input-nombre-estudiante', 'value'),
         State('sys-input-correo-estudiante', 'value')],
        prevent_initial_call=True
    )
    def verificar_o_enviar(verificar_clicks, enviar_clicks, cerrar_clicks, preguntas, respuestas, nombre, correo):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id == 'sys-btn-cerrar-resultados':
            return STYLE_MODAL_OVERLAY_HIDDEN, no_update

        if not preguntas:
            return STYLE_MODAL_OVERLAY_VISIBLE, html.P([html.I(className="fa-solid fa-triangle-exclamation", style={"marginRight": "8px"}), "Primero debes generar las preguntas."], style={'color': '#f87171', 'fontWeight': 'bold'})

        respuestas = respuestas or {}
        total = len(preguntas)

        if len(respuestas) < total:
            faltantes = total - len(respuestas)
            return STYLE_MODAL_OVERLAY_VISIBLE, html.P(
                [
                    html.I(className="fa-solid fa-triangle-exclamation", style={"marginRight": "8px"}),
                    f"Has respondido {len(respuestas)} de {total} preguntas. Te faltan {faltantes} por responder.",
                ],
                style={'color': '#f59e0b', 'fontSize': '15px', 'lineHeight': '1.6'}
            )

        if trigger_id == 'sys-btn-enviar-resultados' and (not nombre or not correo):
            return STYLE_MODAL_OVERLAY_VISIBLE, html.P(
                [html.I(className="fa-solid fa-triangle-exclamation", style={"marginRight": "8px"}), "Completa tu Nombre y Correo antes de enviar los resultados."],
                style={'color': '#f87171', 'fontSize': '15px', 'fontWeight': 'bold'}
            )

        correctas = 0
        for idx, p in enumerate(preguntas):
            if respuestas.get(str(idx)) == p.get('correcta'):
                correctas += 1

        porcentaje = round((correctas / total) * 100, 1)

        reporte = html.Div([
            html.P([html.I(className="fa-solid fa-user", style={"marginRight": "8px"}), f"Estudiante: {nombre or 'No especificado'}"], style={'color': '#e2e8f0', 'fontSize': '15px'}),
            html.P([html.I(className="fa-solid fa-envelope", style={"marginRight": "8px"}), f"Correo: {correo or 'No especificado'}"], style={'color': '#e2e8f0', 'fontSize': '15px'}),
            html.Hr(style={'borderColor': '#334155', 'margin': '12px 0'}),
            html.P([html.I(className="fa-solid fa-pen-to-square", style={"marginRight": "8px"}), f"Preguntas respondidas: {total} de {total}"], style={'color': '#e2e8f0', 'fontSize': '15px'}),
            html.P([html.I(className="fa-solid fa-circle-check", style={"marginRight": "8px"}), f"Correctas: {correctas}"], style={'color': '#10b981', 'fontSize': '18px', 'fontWeight': 'bold'}),
            html.P([html.I(className="fa-solid fa-circle-xmark", style={"marginRight": "8px"}), f"Incorrectas: {total - correctas}"], style={'color': '#f87171', 'fontSize': '18px', 'fontWeight': 'bold'}),
            html.P([html.I(className="fa-solid fa-bullseye", style={"marginRight": "8px"}), f"Calificación: {porcentaje}%"], style={'color': '#38bdf8', 'fontSize': '20px', 'fontWeight': 'bold'}),
            html.Hr(style={'borderColor': '#334155', 'margin': '12px 0'}),
            html.P([html.I(className="fa-solid fa-book", style={"marginRight": "8px"}), "Revisa los temas para reforzar conceptos."], style={'color': '#94a3b8', 'fontSize': '14px'}),
        ])

        if trigger_id == 'sys-btn-enviar-resultados':
            try:
                with open(ESTUDIANTES_CSV, 'a', encoding='utf-8') as f:
                    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"{timestamp},{nombre.strip()},{correo.strip()},{correctas},{total},{porcentaje}\n")
                reporte.children.append(
                    html.P([html.I(className="fa-solid fa-circle-check", style={"marginRight": "8px"}), "Resultados guardados."], style={'color': '#10b981', 'fontSize': '14px', 'marginTop': '10px'})
                )
            except Exception as e:
                reporte.children.append(
                    html.P([html.I(className="fa-solid fa-circle-xmark", style={"marginRight": "8px"}), f"Error al guardar: {str(e)}"], style={'color': '#f87171', 'fontSize': '14px', 'marginTop': '10px'})
                )

        return STYLE_MODAL_OVERLAY_VISIBLE, reporte

    # 4. MOSTRAR INFO DEL ARCHIVO
    @app.callback(
        Output('sys-upload-tarea-info', 'children'),
        Input('sys-upload-tarea-archivo', 'contents'),
        State('sys-upload-tarea-archivo', 'filename'),
        prevent_initial_call=True
    )
    def mostrar_info_archivo(contents, filename):
        if contents is None:
            return ""
        size_bytes = len(contents)
        if size_bytes < 1024:
            size_str = f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            size_str = f"{size_bytes / 1024:.1f} KB"
        else:
            size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
        return html.Span([html.I(className="fa-solid fa-circle-check", style={"marginRight": "8px"}), f"Archivo seleccionado: {filename} ({size_str})"])

    # 5. GUARDAR TAREA CON ARCHIVO
    @app.callback(
        [Output('sys-mensaje-tarea-estado', 'children'),
         Output('sys-contador-tareas', 'children', allow_duplicate=True)],
        [Input('sys-btn-enviar-tarea', 'n_clicks')],
        [State('sys-upload-tarea-archivo', 'contents'),
         State('sys-upload-tarea-archivo', 'filename'),
         State('sys-input-nombre-tarea', 'value'),
         State('sys-input-curso-tarea', 'value'),
         State('sys-textarea-tarea-descripcion', 'value')],
        prevent_initial_call=True
    )
    def guardar_tarea_con_archivo(n_clicks, contents, filename, nombre, curso, descripcion):
        if n_clicks == 0:
            raise PreventUpdate

        if not nombre or not nombre.strip():
            return html.Span([html.I(className="fa-solid fa-triangle-exclamation", style={"marginRight": "8px"}), "Ingresa tu nombre completo."]), no_update
        if not contents:
            return html.Span([html.I(className="fa-solid fa-triangle-exclamation", style={"marginRight": "8px"}), "Selecciona un archivo."]), no_update
        if not descripcion or not descripcion.strip():
            return html.Span([html.I(className="fa-solid fa-triangle-exclamation", style={"marginRight": "8px"}), "Escribe una descripción."]), no_update

        try:
            carpeta_tareas = "tareas_subidas"
            if not os.path.exists(carpeta_tareas):
                os.makedirs(carpeta_tareas)

            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_limpio = nombre.strip().replace(' ', '_')
            extension = filename.split('.')[-1] if '.' in filename else 'pdf'
            nombre_archivo = f"{timestamp}_{nombre_limpio}.{extension}"
            ruta_completa = os.path.join(carpeta_tareas, nombre_archivo)

            content_type, content_string = contents.split(',')
            with open(ruta_completa, 'wb') as f:
                f.write(base64.b64decode(content_string))

            with open('tareas_estudiantes.txt', 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*70}\n")
                f.write(f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Estudiante: {nombre}\n")
                f.write(f"Curso: {curso or 'No especificado'}\n")
                f.write(f"Archivo: {nombre_archivo}\n")
                f.write(f"Descripción:\n{descripcion}\n")
                f.write(f"{'='*70}\n")

            try:
                with open('tareas_estudiantes.txt', 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    num_tareas = contenido.count('='*70)
            except Exception:
                num_tareas = 0

            return html.Span([html.I(className="fa-solid fa-circle-check", style={"marginRight": "8px"}), f"¡Tarea enviada! Archivo: {nombre_archivo}"]), f"{num_tareas} tareas"

        except Exception as e:
            return html.Span([html.I(className="fa-solid fa-circle-xmark", style={"marginRight": "8px"}), f"Error: {str(e)}"]), no_update

    # 6. CERRAR MODAL AL CAMBIAR DE PÁGINA
    @app.callback(
        Output('sys-modal-resultados', 'style', allow_duplicate=True),
        Input('url', 'pathname'),
        prevent_initial_call=True
    )
    def cerrar_modal_al_cambiar_pagina(pathname):
        return STYLE_MODAL_OVERLAY_HIDDEN

    # 7. CONTADOR DE TAREAS
    @app.callback(
        Output('sys-contador-tareas', 'children'),
        Input('sys-btn-enviar-tarea', 'n_clicks'),
        prevent_initial_call=True
    )
    def actualizar_contador_tareas(n_clicks):
        try:
            with open('tareas_estudiantes.txt', 'r', encoding='utf-8') as f:
                contenido = f.read()
                num_tareas = contenido.count('=' * 70)
            return f"{num_tareas} tareas"
        except Exception:
            return "0 tareas"


def _register_control_callbacks(app):

    # 7.1 Mostrar TF
    @app.callback(
        [Output('sys-display-tf-formula', 'children'),
         Output('sys-graph-poles-zeros', 'figure'),
         Output('sys-tf-parse-error', 'children'),
         Output('sys-store-control-tf', 'data')],
        [Input('sys-btn-mostrar-tf', 'n_clicks'),
         Input('sys-btn-reset-tf', 'n_clicks')],
        [State('sys-input-transfer-function', 'value')],
        prevent_initial_call=True
    )
    def mostrar_tf(n_clicks_mostrar, n_clicks_reset, tf_str):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id == 'sys-btn-reset-tf':
            tf_str = DEFAULT_TF

        if not tf_str or not tf_str.strip():
            error_box = html.Div([html.I(className="fa-solid fa-triangle-exclamation", style={"marginRight": "8px"}), "Ingresa una función de transferencia."], style=STYLE_ERROR_BOX)
            return error_box, plot_poles_zeros([1.0], [1.0, 1.0]), "", {}

        parsed = parse_transfer_function(tf_str)

        if parsed['error']:
            error_box = html.Div([html.I(className="fa-solid fa-triangle-exclamation", style={"marginRight": "8px"}), parsed['error']], style=STYLE_ERROR_BOX)
            return error_box, plot_poles_zeros([1.0], [1.0, 1.0]), "", {}

        tf_data = {
            'num': parsed['num'],
            'den': parsed['den'],
            'delay': parsed.get('delay', 0.0),
            'tf_str': parsed.get('tf_str', tf_str)
        }

        fig_pz = plot_poles_zeros(parsed['num'], parsed['den'])
        formula = format_tf_display(parsed['num'], parsed['den'], parsed.get('delay', 0.0))

        return formula, fig_pz, "", tf_data

    # 7.2 Aplicar PID y actualizar gráficas
    @app.callback(
        [Output('sys-graph-control-response', 'figure'),
         Output('sys-graph-control-signal', 'figure'),
         Output('sys-control-metrics', 'children'),
         Output('sys-control-stability-panel', 'children'),
         Output('sys-slider-kp', 'value'),
         Output('sys-slider-ki', 'value'),
         Output('sys-slider-kd', 'value'),
         Output('sys-store-control-sim', 'data'),
         Output('sys-display-lazo-abierto', 'children')],
        [Input('sys-slider-kp', 'value'),
         Input('sys-slider-ki', 'value'),
         Input('sys-slider-kd', 'value'),
         Input('sys-slider-setpoint', 'value'),
         Input('sys-slider-tau', 'value'),
         Input('sys-dropdown-input-type', 'value'),
         Input('sys-preset-p', 'n_clicks'),
         Input('sys-preset-pi', 'n_clicks'),
         Input('sys-preset-pid', 'n_clicks'),
         Input('sys-preset-aggressive', 'n_clicks'),
         Input('sys-btn-aplicar-pid', 'n_clicks')],
        [State('sys-store-control-tf', 'data'),
         State('sys-input-transfer-function', 'value')],
        prevent_initial_call= True
    )
    def update_control_response(kp, ki, kd, setpoint, tau, input_type, p_click, pi_click, pid_click, agg_click, aplicar_pid, tf_data, tf_input_str):

        if tf_input_str and tf_input_str.strip():
            parsed_now = parse_transfer_function(tf_input_str)
            if not parsed_now['error']:
                tf_data = {
                    'num': parsed_now['num'],
                    'den': parsed_now['den'],
                    'delay': parsed_now.get('delay', 0.0),
                    'tf_str': tf_input_str
                }

        ctx = callback_context
        trigger = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

        if trigger == 'sys-preset-p':
            kp, ki, kd = 2.0, 0.0, 0.0
        elif trigger == 'sys-preset-pi':
            kp, ki, kd = 2.0, 0.5, 0.0
        elif trigger == 'sys-preset-pid':
            kp, ki, kd = 3.0, 1.0, 0.5
        elif trigger == 'sys-preset-aggressive':
            kp, ki, kd = 6.0, 2.5, 1.0

        kp = kp or 0.0
        ki = ki or 0.0
        kd = kd or 0.0
        setpoint = setpoint or 1.0
        tau = tau or 1.0

        if tf_data and tf_data.get('num') is not None and tf_data.get('den') is not None:
            num_g = tf_data['num']
            den_g = tf_data['den']
            delay = tf_data.get('delay', 0.0)
            tf_active_str = tf_data.get('tf_str', f"1/({tau:.2f}s + 1)")
        else:
            num_g = [1.0]
            den_g = [tau, 1.0]
            delay = 0.0
            tf_active_str = f"1/({tau:.2f}s + 1)"

        t = np.linspace(0, 15, 600)

        y_open = simulate_tf_response(num_g, den_g, t, input_type, setpoint, delay)
        num_cl, den_cl = build_closed_loop(num_g, den_g, kp, ki, kd)
        y_closed = simulate_tf_response(num_cl, den_cl, t, input_type, setpoint, delay)

        if input_type == 'step':
            ref = np.ones_like(t) * setpoint
        elif input_type == 'ramp':
            ref = setpoint * t
        elif input_type == 'sine':
            ref = setpoint * np.sin(2.0 * t)
        else:
            ref = np.zeros_like(t)

        e = ref - y_closed
        dt = t[1] - t[0]
        integral_e = np.cumsum(e) * dt
        deriv_e = np.gradient(e, dt)
        u = kp * e + ki * integral_e + kd * deriv_e
        u = np.nan_to_num(u, nan=0.0, posinf=1e6, neginf=-1e6)
        u = np.clip(u, -1e6, 1e6)

        fig_response = plot_time_response(t, y_open, y_closed, setpoint, input_type, tf_active_str)
        fig_signal = plot_control_signal(t, u)

        metrics = analyze_control_metrics(y_closed, t, setpoint if input_type == 'step' else 1.0)
        metrics_html = html.Div(style={'fontSize': '13px'}, children=[
            html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '4px'},
                    children=[html.Span("T. Establecimiento:", style={'color': '#94a3b8'}),
                            html.Span(f"{metrics['settle_time']:.2f} s", style={'color': '#38bdf8', 'fontWeight': '700'})]),
            html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '4px'},
                    children=[html.Span("Overshoot:", style={'color': '#94a3b8'}),
                            html.Span(f"{metrics['overshoot']:.1f} %", style={'color': '#38bdf8', 'fontWeight': '700'})]),
            html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '4px'},
                    children=[html.Span("Error E.E.:", style={'color': '#94a3b8'}),
                            html.Span(f"{metrics['steady_state_error']:.1f} %", style={'color': '#38bdf8', 'fontWeight': '700'})]),
            html.Div(style={'display': 'flex', 'justifyContent': 'space-between'},
                    children=[html.Span("T. Subida:", style={'color': '#94a3b8'}),
                            html.Span(f"{metrics['rise_time']:.2f} s", style={'color': '#38bdf8', 'fontWeight': '700'})]),
        ])

        margins = compute_stability_margins(num_g, den_g)
        try:
            _, poles_open, _ = signal.tf2zpk(num_g, den_g)
        except Exception:
            poles_open = []
        stability_html = build_stability_panel(margins, poles_open)

        sim_store = {
            't': t.tolist(),
            'y_open': y_open.tolist(),
            'y_closed': y_closed.tolist(),
            'u': u.tolist()
        }

        num_c = [kd, kp, ki]
        den_c = [1.0, 0.0]

        num_L = np.polymul(num_c, num_g)
        den_L = np.polymul(den_c, den_g)

        lazo_abierto_html = format_tf_display(
            num_L.tolist(), den_L.tolist(), delay=delay,
            tf_str=f"L(s)"
        )

        return (fig_response, fig_signal, metrics_html, stability_html,
                kp, ki, kd, sim_store, lazo_abierto_html)

    # 7.3 Herramientas avanzadas
    @app.callback(
        [Output('sys-graph-bode', 'figure'),
         Output('sys-graph-root-locus', 'figure'),
         Output('sys-graph-nyquist', 'figure')],
        [Input('sys-advanced-tools-panel', 'style'),
         Input('sys-store-control-tf', 'data')],
        prevent_initial_call=True
    )
    def update_advanced_tools(panel_style, tf_data):
        if not panel_style or panel_style.get('display') == 'none':
            raise PreventUpdate

        if tf_data and tf_data.get('num') is not None and tf_data.get('den') is not None:
            num_g, den_g = tf_data['num'], tf_data['den']
        else:
            num_g, den_g = [1.0], [1.0, 1.0]

        return plot_bode(num_g, den_g), plot_root_locus(num_g, den_g), plot_nyquist(num_g, den_g)

    # 7.4 Toggle avanzado
    @app.callback(
        [Output('sys-advanced-tools-panel', 'style'),
         Output('sys-advanced-toggle-arrow', 'children'),
         Output('sys-store-advanced-open', 'data')],
        [Input('sys-btn-toggle-advanced', 'n_clicks')],
        [State('sys-store-advanced-open', 'data')],
        prevent_initial_call=True
    )
    def toggle_advanced_tools(n_clicks, is_open):
        new_state = not is_open
        style = STYLE_ADVANCED_PANEL_VISIBLE if new_state else STYLE_ADVANCED_PANEL_HIDDEN
        arrow = html.I(className="fa-solid fa-chevron-up" if new_state else "fa-solid fa-chevron-down")
        return style, arrow, new_state

    # 7.5 Exportar CSV
    @app.callback(
        Output('sys-download-control-csv', 'data'),
        Input('sys-btn-export-csv', 'n_clicks'),
        State('sys-store-control-sim', 'data'),
        prevent_initial_call=True
    )
    def download_csv(n_clicks, sim_data):
        if not n_clicks or not sim_data:
            raise PreventUpdate
        csv_text = export_to_csv(
            np.array(sim_data['t']), np.array(sim_data['y_open']),
            np.array(sim_data['y_closed']), np.array(sim_data['u'])
        )
        return dict(content=csv_text, filename="respuesta_control.csv")

    # 7.6 Inicializar store-control-tf con la TF por defecto
    @app.callback(
        Output('sys-store-control-tf', 'data', allow_duplicate=True),
        Input('url', 'pathname'),
        prevent_initial_call=True
    )
    def init_default_tf(pathname):
        if pathname == '/sys/control':
            parsed = parse_transfer_function(DEFAULT_TF)
            if not parsed['error']:
                return {
                    'num': parsed['num'],
                    'den': parsed['den'],
                    'delay': parsed.get('delay', 0.0),
                    'tf_str': DEFAULT_TF
                }
        raise PreventUpdate


def _register_convolucion_callbacks(app):

    @app.callback(
        [Output('sys-conv-x-expr', 'value', allow_duplicate=True),
         Output('sys-conv-h-expr', 'value', allow_duplicate=True)],
        Input('sys-conv-preset', 'value'),
        prevent_initial_call=True
    )
    def update_preset_conv(preset_key):
        p = PRESET_CONVOLUTIONS.get(preset_key, PRESET_CONVOLUTIONS['rect_rect'])
        return p['x_expr'], p['h_expr']

    CONV_EXAMPLES = {
        'sys-conv-ex-rect': ('heaviside(t) - heaviside(t - 2)',
                             'heaviside(t) - heaviside(t - 1)'),
        'sys-conv-ex-exp':  ('exp(-t)*heaviside(t)',
                             'heaviside(t) - heaviside(t - 2)'),
        'sys-conv-ex-gauss': ('exp(-t**2)', 'exp(-t**2)'),
        'sys-conv-ex-sinc': ('sin(pi*t)/(pi*t + 1e-10)',
                             'heaviside(t + 1) - heaviside(t - 1)'),
        'sys-conv-ex-step': ('heaviside(t)', 'exp(-2*t)*heaviside(t)'),
    }

    @app.callback(
        [Output('sys-conv-x-expr', 'value', allow_duplicate=True),
         Output('sys-conv-h-expr', 'value', allow_duplicate=True)],
        [Input('sys-conv-ex-rect', 'n_clicks'),
         Input('sys-conv-ex-exp', 'n_clicks'),
         Input('sys-conv-ex-gauss', 'n_clicks'),
         Input('sys-conv-ex-sinc', 'n_clicks'),
         Input('sys-conv-ex-step', 'n_clicks')],
        prevent_initial_call=True
    )
    def cargar_ejemplo_conv(c1, c2, c3, c4, c5):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        trig = ctx.triggered[0]['prop_id'].split('.')[0]
        x_e, h_e = CONV_EXAMPLES.get(
            trig,
            ('heaviside(t) - heaviside(t - 2)',
             'heaviside(t) - heaviside(t - 1)')
        )
        return x_e, h_e

    @app.callback(
        [Output('sys-conv-graph-anim', 'figure'),
         Output('sys-conv-graph-result', 'figure'),
         Output('sys-conv-frames-store', 'data'),
         Output('sys-conv-current-frame', 'data'),
         Output('sys-conv-error', 'children'),
         Output('sys-conv-playing', 'data', allow_duplicate=True),
         Output('sys-conv-anim-interval', 'disabled', allow_duplicate=True),
         Output('sys-conv-frame-indicator', 'children')],
        [Input('sys-btn-conv-run', 'n_clicks')],
        [State('sys-conv-x-expr', 'value'),
         State('sys-conv-h-expr', 'value'),
         State('sys-conv-tmax', 'value'),
         State('sys-conv-frames', 'value')],
        prevent_initial_call=True
    )
    def run_convolution(n_clicks, x_expr, h_expr, tmax, n_frames):
        try:
            tmax = float(tmax) if tmax else 6.0
            n_frames = int(n_frames) if n_frames else 60

            t = np.linspace(-tmax / 2, tmax / 2, 800)

            x, err_x = parse_user_signal(x_expr, t)
            if err_x:
                return (empty_fig("Error x(t)"), empty_fig(""), {}, 0,
                        html.Div([html.I(className="fa-solid fa-triangle-exclamation", style={"marginRight": "8px"}), err_x], style=STYLE_ERROR_BOX),
                        False, True, "")

            h, err_h = parse_user_signal(h_expr, t)
            if err_h:
                return (empty_fig("Error h(t)"), empty_fig(""), {}, 0,
                        html.Div([html.I(className="fa-solid fa-triangle-exclamation", style={"marginRight": "8px"}), err_h], style=STYLE_ERROR_BOX),
                        False, True, "")

            t_conv, y_conv = compute_convolution_numeric(x, h, t)
            frames, t_samples = compute_convolution_animated(x, h, t, n_frames=n_frames)

            fig_result = make_subplots(
                rows=2, cols=2,
                subplot_titles=("x(τ)", "h(τ)", "y(t) = x * h", "Comparación"),
                vertical_spacing=0.18, horizontal_spacing=0.1
            )

            fig_result.add_trace(go.Scatter(
                x=t, y=x, mode='lines', name='x',
                line=dict(color='#38bdf8', width=2.5)), row=1, col=1)
            fig_result.add_trace(go.Scatter(
                x=t, y=h, mode='lines', name='h',
                line=dict(color='#a855f7', width=2.5)), row=1, col=2)
            fig_result.add_trace(go.Scatter(
                x=t_conv, y=y_conv, mode='lines', name='y',
                line=dict(color='#10b981', width=2.5),
                fill='tozeroy', fillcolor='rgba(16,185,129,0.15)'), row=2, col=1)
            fig_result.add_trace(go.Scatter(
                x=t, y=x, mode='lines', name='x',
                line=dict(color='#38bdf8', width=1.5, dash='dot')), row=2, col=2)
            fig_result.add_trace(go.Scatter(
                x=t, y=h, mode='lines', name='h',
                line=dict(color='#a855f7', width=1.5, dash='dot')), row=2, col=2)
            fig_result.add_trace(go.Scatter(
                x=t_conv, y=y_conv, mode='lines', name='y',
                line=dict(color='#10b981', width=2.5)), row=2, col=2)

            fig_result.update_layout(
                height=520, showlegend=False,
                template='plotly_dark', plot_bgcolor=THEME['card'],
                paper_bgcolor=THEME['card'],
                margin=dict(l=45, r=20, t=50, b=35))

            store_data = {
                'x': [float(v) for v in x],
                'h': [float(v) for v in h],
                't': [float(v) for v in t],
                't_conv': [float(v) for v in t_conv],
                'y_conv': [float(v) for v in y_conv],
                'frames': frames,
                't_samples': t_samples,
                'x_expr': str(x_expr),
                'h_expr': str(h_expr),
                'n_frames': len(frames)
            }

            fig_anim = build_conv_animation_figure(
                frames[0], t, x, t_samples[0], y_conv, t_conv)

            indicator = f"Frame 1 / {len(frames)}"

            return (fig_anim, fig_result, store_data, 0, "",
                    False, True, indicator)

        except Exception as e:
            traceback.print_exc()
            return (empty_fig(f"Error: {e}"), empty_fig(""), {}, 0,
                    html.Div([html.I(className="fa-solid fa-triangle-exclamation", style={"marginRight": "8px"}), str(e)], style=STYLE_ERROR_BOX),
                    False, True, "")

    @app.callback(
        [Output('sys-conv-anim-interval', 'disabled'),
         Output('sys-conv-playing', 'data'),
         Output('sys-conv-current-frame', 'data', allow_duplicate=True),
         Output('sys-conv-graph-anim', 'figure', allow_duplicate=True),
         Output('sys-conv-frame-indicator', 'children', allow_duplicate=True)],
        [Input('sys-btn-conv-play', 'n_clicks'),
         Input('sys-btn-conv-pause', 'n_clicks'),
         Input('sys-btn-conv-reset', 'n_clicks')],
        [State('sys-conv-frames-store', 'data'),
         State('sys-conv-current-frame', 'data')],
        prevent_initial_call=True
    )
    def control_conv_animation(play_clicks, pause_clicks, reset_clicks,
                                store, current_frame):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trig = ctx.triggered[0]['prop_id'].split('.')[0]

        if trig == 'sys-btn-conv-reset':
            if not store or 'frames' not in store:
                return True, False, 0, no_update, "Frame 1 / 0"
            frames = store['frames']
            t = np.array(store['t'])
            x = np.array(store['x'])
            t_conv = np.array(store['t_conv'])
            y_conv = np.array(store['y_conv'])
            t_samples = store['t_samples']
            fig = build_conv_animation_figure(
                frames[0], t, x, t_samples[0], y_conv, t_conv)
            return True, False, 0, fig, f"Frame 1 / {len(frames)}"

        if trig == 'sys-btn-conv-play':
            if not store or 'frames' not in store:
                raise PreventUpdate
            frames = store['frames']
            cf = int(current_frame or 0)
            if cf >= len(frames):
                cf = 0
            next_frame = (cf + 1) % len(frames)
            t = np.array(store['t'])
            x = np.array(store['x'])
            t_conv = np.array(store['t_conv'])
            y_conv = np.array(store['y_conv'])
            t_samples = store['t_samples']
            fig = build_conv_animation_figure(
                frames[next_frame], t, x, t_samples[next_frame], y_conv, t_conv)
            return False, True, next_frame, fig, f"Frame {next_frame + 1} / {len(frames)}"

        if trig == 'sys-btn-conv-pause':
            return True, False, no_update, no_update, no_update

        raise PreventUpdate

    @app.callback(
        [Output('sys-conv-current-frame', 'data', allow_duplicate=True),
         Output('sys-conv-graph-anim', 'figure', allow_duplicate=True),
         Output('sys-conv-frame-indicator', 'children', allow_duplicate=True)],
        Input('sys-conv-anim-interval', 'n_intervals'),
        [State('sys-conv-frames-store', 'data'),
         State('sys-conv-current-frame', 'data'),
         State('sys-conv-playing', 'data')],
        prevent_initial_call=True
    )
    def advance_conv_frame(n_intervals, store, current_frame, playing):
        if not playing or not store or 'frames' not in store:
            raise PreventUpdate

        frames = store['frames']
        if not frames:
            raise PreventUpdate

        cf = int(current_frame or 0)
        next_frame = (cf + 1) % len(frames)

        t = np.array(store['t'])
        x = np.array(store['x'])
        t_conv = np.array(store['t_conv'])
        y_conv = np.array(store['y_conv'])
        t_samples = store['t_samples']

        fig = build_conv_animation_figure(
            frames[next_frame], t, x, t_samples[next_frame], y_conv, t_conv)

        return next_frame, fig, f"Frame {next_frame + 1} / {len(frames)}"


def _register_tf_callbacks(app):

    TF_EXAMPLES = {
        'sys-tf-ex-1': 'exp(-t)*heaviside(t)',
        'sys-tf-ex-2': 'heaviside(t+1) - heaviside(t-1)',
        'sys-tf-ex-3': 'exp(-t**2)',
        'sys-tf-ex-4': 'cos(2*pi*t)',
        'sys-tf-ex-5': 'sin(4*t)/(4*t + 1e-10)',
    }

    @app.callback(
        Output('sys-tf-x-expr', 'value'),
        [Input('sys-tf-ex-1', 'n_clicks'),
         Input('sys-tf-ex-2', 'n_clicks'),
         Input('sys-tf-ex-3', 'n_clicks'),
         Input('sys-tf-ex-4', 'n_clicks'),
         Input('sys-tf-ex-5', 'n_clicks')],
        prevent_initial_call=True
    )
    def cargar_ejemplo_tf(c1, c2, c3, c4, c5):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        return TF_EXAMPLES.get(trigger_id, 'exp(-t)*heaviside(t)')

    @app.callback(
        [Output('sys-tf-graph-time', 'figure'),
         Output('sys-tf-graph-mag', 'figure'),
         Output('sys-tf-graph-phase', 'figure'),
         Output('sys-tf-props-panel', 'children')],
        [Input('sys-btn-tf-run', 'n_clicks')],
        [State('sys-tf-x-expr', 'value'), State('sys-tf-trange', 'value'),
         State('sys-tf-scale', 'value')],
        prevent_initial_call=True
    )
    def run_tf(n_clicks, expr, trange, scale):
        try:
            t = np.linspace(-trange, trange, 4096)
            x, err = parse_user_signal(expr, t)
            if err:
                return empty_fig("Error"), empty_fig(""), empty_fig(""), \
                       html.Div([html.I(className="fa-solid fa-triangle-exclamation", style={"marginRight": "8px"}), err], style=STYLE_ERROR_BOX)

            dt = t[1] - t[0]
            N = len(x)

            X = np.fft.fftshift(np.fft.fft(x)) * dt
            freqs = np.fft.fftshift(np.fft.fftfreq(N, d=dt)) * 2 * np.pi

            mag = np.abs(X)
            phase = np.angle(X, deg=True)

            f_max = (np.pi / dt) * 0.5
            mask = np.abs(freqs) <= f_max
            freqs_plot = freqs[mask]
            mag_plot_vals = mag[mask]
            phase_plot_vals = phase[mask]

            if scale == 'db':
                mag_plot = 20 * np.log10(np.maximum(mag_plot_vals, 1e-12))
                ylab = "|X(jω)| (dB)"
            else:
                mag_plot = mag_plot_vals
                ylab = "|X(jω)|"

            fig_t = go.Figure()
            fig_t.add_trace(go.Scatter(x=t, y=x, mode='lines',
                line=dict(color='#38bdf8', width=2.5), fill='tozeroy',
                fillcolor='rgba(56,189,248,0.15)', name='x(t)'))
            fig_t.update_layout(
                title="<b>x(t)</b>", xaxis_title="t (s)", yaxis_title="Amplitud",
                height=320, template='plotly_dark',
                plot_bgcolor=THEME['card'], paper_bgcolor=THEME['card'],
                margin=dict(l=45, r=20, t=45, b=35))

            fig_m = go.Figure()
            fig_m.add_trace(go.Scatter(x=freqs_plot, y=mag_plot, mode='lines',
                line=dict(color='#10b981', width=2.5), fill='tozeroy',
                fillcolor='rgba(16,185,129,0.15)', name='|X(jω)|'))
            fig_m.update_layout(
                title="<b>Espectro de magnitud</b>",
                xaxis_title="ω (rad/s)", yaxis_title=ylab, height=320,
                template='plotly_dark', plot_bgcolor=THEME['card'],
                paper_bgcolor=THEME['card'], margin=dict(l=45, r=20, t=45, b=35))

            fig_p = go.Figure()
            fig_p.add_trace(go.Scatter(x=freqs_plot, y=phase_plot_vals, mode='lines',
                line=dict(color='#f59e0b', width=2.5), name='∠X(jω)'))
            fig_p.update_layout(
                title="<b>Espectro de fase</b>",
                xaxis_title="ω (rad/s)", yaxis_title="Fase (°)", height=280,
                template='plotly_dark', plot_bgcolor=THEME['card'],
                paper_bgcolor=THEME['card'], margin=dict(l=45, r=20, t=45, b=35))

            e_time = _trapz(x**2, t)
            e_freq = _trapz(mag**2, freqs) / (2 * np.pi)
            bw = estimate_bandwidth(freqs, mag)

            props = html.Div(
                style={'backgroundColor': '#1e293b', 'padding': '16px',
                       'borderRadius': '10px', 'border': '1px solid #334155',
                       'display': 'flex', 'gap': '20px', 'flexWrap': 'wrap'},
                children=[
                    html.Div([
                        html.Div("Energía (tiempo)",
                                 style={'color': '#94a3b8', 'fontSize': '11px'}),
                        html.Div(f"{e_time:.5f}",
                                 style={'color': '#10b981', 'fontWeight': '700'})]),
                    html.Div([
                        html.Div("Energía (frecuencia)",
                                 style={'color': '#94a3b8', 'fontSize': '11px'}),
                        html.Div(f"{e_freq:.5f}",
                                 style={'color': '#10b981', 'fontWeight': '700'})]),
                    html.Div([
                        html.Div("Ancho de banda (-3 dB)",
                                 style={'color': '#94a3b8', 'fontSize': '11px'}),
                        html.Div(f"{bw:.3f} rad/s",
                                 style={'color': '#38bdf8', 'fontWeight': '700'})]),
                ])

            return fig_t, fig_m, fig_p, props

        except Exception as e:
            traceback.print_exc()
            return empty_fig(f"Error: {e}"), empty_fig(""), empty_fig(""), html.Div("")


def _register_muestreo_callbacks(app):
    @app.callback(
        [Output('sys-samp-graph', 'figure'),
         Output('sys-samp-alias-info', 'children')],
        [Input('sys-samp-f-signal', 'value'),
         Input('sys-samp-f-samp', 'value'),
         Input('sys-samp-tipo', 'value')],
        prevent_initial_call=True
    )
    def run_muestreo(f_sig, fs, tipo):
        if f_sig is None or fs is None or tipo is None:
            raise PreventUpdate
        try:
            T_total = 1.0
            t_cont = np.linspace(0, T_total, 5000)

            def gen_signal(t_arr):
                if tipo == 'sin':
                    return np.sin(2 * np.pi * f_sig * t_arr)
                elif tipo == 'multitone':
                    return (0.5*np.sin(2*np.pi*f_sig*t_arr) +
                            0.3*np.sin(2*np.pi*3*f_sig*t_arr) +
                            0.2*np.sin(2*np.pi*5*f_sig*t_arr))
                else:
                    return np.sin(2*np.pi*(f_sig*t_arr + 5*t_arr**2))

            x_cont = gen_signal(t_cont)
            n_samples = max(int(fs * T_total), 2)
            t_samp = np.linspace(0, T_total, n_samples)
            x_samp = gen_signal(t_samp)

            nyquist = 2 * f_sig
            aliasing = fs < nyquist
            f_alias = abs(f_sig - round(f_sig / fs) * fs) if aliasing and tipo == 'sin' else None

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=t_cont, y=x_cont, mode='lines', name='x(t)',
                line=dict(color='#38bdf8', width=2), opacity=0.6))
            fig.add_trace(go.Scatter(x=t_samp, y=x_samp, mode='markers+lines',
                name=f'Muestras (fs={fs} Hz)',
                line=dict(color='#f59e0b', width=1, dash='dot'),
                marker=dict(size=8, color='#f59e0b')))

            if aliasing and tipo == 'sin' and f_alias:
                alias_signal = np.sin(2*np.pi*f_alias*t_cont)
                fig.add_trace(go.Scatter(x=t_cont, y=alias_signal, mode='lines',
                    name=f'Alias ({f_alias:.2f} Hz)',
                    line=dict(color='#ef4444', width=2, dash='dash')))

            fig.update_layout(
                title=f"<b>Muestreo</b> — fs = {fs} Hz, Nyquist = {nyquist} Hz",
                xaxis_title="Tiempo (s)", yaxis_title="Amplitud", height=420,
                template='plotly_dark', plot_bgcolor=THEME['card'],
                paper_bgcolor=THEME['card'], margin=dict(l=45, r=20, t=50, b=35))

            if aliasing:
                info = html.Div([
                    html.Span([html.I(className="fa-solid fa-triangle-exclamation", style={"marginRight": "8px"}), "ALIASING: "], style={'color': '#ef4444', 'fontWeight': '700'}),
                    html.Span(f"fs = {fs} Hz < 2B = {nyquist} Hz. ", style={'color': '#e2e8f0'}),
                    html.Span(f"Se pliega a {f_alias:.2f} Hz. " if f_alias else "",
                              style={'color': '#f59e0b'}),
                    html.Span("Aumenta fs.", style={'color': '#e2e8f0'}),
                ], style={'padding': '12px', 'background': 'rgba(239,68,68,0.12)',
                          'borderRadius': '8px', 'border': '1px solid rgba(239,68,68,0.4)',
                          'fontSize': '14px'})
            else:
                info = html.Div([
                    html.Span([html.I(className="fa-solid fa-circle-check", style={"marginRight": "8px"}), "Sin aliasing. "], style={'color': '#10b981', 'fontWeight': '700'}),
                    html.Span(f"fs = {fs} Hz ≥ 2B = {nyquist} Hz.", style={'color': '#e2e8f0'}),
                ], style={'padding': '12px', 'background': 'rgba(16,185,129,0.12)',
                          'borderRadius': '8px', 'border': '1px solid rgba(16,185,129,0.4)',
                          'fontSize': '14px'})

            return fig, info
        except Exception as e:
            return empty_fig(str(e)), html.Div("")
        