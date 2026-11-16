# apps/ct_modulos/interfaz.py
# ============================================================
# Interfaz principal del módulo de Tomografía Computarizada (CT)
# Adaptada para integrarse en Prometeo
# ============================================================
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from config import THEME as GLOBAL_THEME

# Importamos los módulos del CT
from .fundamentos import layout_fundamentos
from .procesamiento import procesamiento_layout, registrar_callbacks_procesamiento
from .recursos import layout_recursos
from .gemini_widget import crear_gemini_widget, registrar_gemini_callbacks
from .simulador import simulador_layout, registrar_callbacks_simulador

# ============================================================
# PALETA CT (Alineada con THEME de Prometeo)
# ============================================================
BG = GLOBAL_THEME["bg"]
PANEL = GLOBAL_THEME["card"]
BORDER = GLOBAL_THEME["card_border"]
CYAN = GLOBAL_THEME["accent_cyan"]
PURPLE = GLOBAL_THEME["accent_purple"]
WHITE = GLOBAL_THEME["text"]
MUTED = GLOBAL_THEME["text_muted"]

# ============================================================
# COMPONENTES REUTILIZABLES
# ============================================================
def nav_item(icon, text, href, active=False):
    return dbc.NavLink(
        [html.Span(icon, className="nav-icon"), html.Span(text)],
        href=href,
        active=active,
        className="ct-nav-link",
    )

def info_card(number, title, text, icon):
    return html.Div(
        [
            html.Div([html.Div(number, className="card-number"), html.Div(icon, className="card-icon")], className="card-top"),
            html.H4(title, className="card-title"),
            html.P(text, className="card-text"),
        ],
        className="info-card",
    )

def section_header(kicker, title, text):
    return html.Div(
        [
            html.Div(kicker.upper(), className="section-kicker"),
            html.H2(title, className="section-title"),
            html.P(text, className="section-description"),
        ],
        className="section-header",
    )

# ============================================================
# BARRA LATERAL
# ============================================================
def crear_sidebar_ct(active_path="/imaging/ct"):
    active_path = active_path.rstrip("/") if active_path else "/imaging/ct"
    return html.Div(
        [
            html.Div(
                [
                    html.Div(html.I(className="fa-solid fa-circle-dot"), className="brand-symbol"),
                    html.Div([html.Div("CT-SIM", className="brand-name"), html.Div("CT RESEARCH LAB", className="brand-subtitle")]),
                ],
                className="brand",
            ),
            # --- BOTÓN VOLVER A IMAGENOLOGÍA (IGUAL A RAYOS X) ---
            dcc.Link(
                html.Div(
                    [
                        html.I(className="fa-solid fa-arrow-left", style={"marginRight": "12px", "fontSize": "14px"}),
                        html.Span("Volver a Imagenología", style={"fontSize": "13px", "fontWeight": "500"}),
                    ],
                    className="ct-back-link",
                    style={"marginBottom": "16px"}
                ),
                href="/imaging",
                style={"textDecoration": "none", "display": "block", "width": "100%"}
            ),
            html.Div("NAVEGACIÓN", className="nav-label"),
            dbc.Nav(
                [
                    nav_item(html.I(className="fa-solid fa-house"), "Inicio", "/imaging/ct", active=(active_path in ("/imaging/ct", "/imaging/ct/"))),
                    nav_item(html.I(className="fa-solid fa-book-bookmark"), "Fundamentos", "/imaging/ct/teoria", active=(active_path == "/imaging/ct/teoria")),
                    nav_item(html.I(className="fa-solid fa-circle-nodes"), "Simulador CT", "/imaging/ct/simulador", active=(active_path == "/imaging/ct/simulador")),
                    nav_item(html.I(className="fa-solid fa-sliders"), "Procesamiento", "/imaging/ct/procesamiento", active=(active_path == "/imaging/ct/procesamiento")),
                    nav_item(html.I(className="fa-solid fa-folder-open"), "Recursos", "/imaging/ct/recursos", active=(active_path == "/imaging/ct/recursos")),
                ],
                vertical=True,
                className="ct-nav",
            ),
            html.Div(className="sidebar-spacer"),
            html.Div(
                [
                    html.Div("PROYECTO ACADÉMICO", className="status-label"),
                    html.Div([html.Span(className="status-dot"), html.Span("Sistema preparado")], className="system-status"),
                ],
                className="sidebar-status",
            ),
        ],
        className="sidebar",
    )

# ============================================================
# PÁGINAS (Portada y placeholder)
# ============================================================
def layout_inicio():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("LABORATORIO DE IMAGENOLOGÍA", className="hero-kicker"),
                            html.H1(["Tomografía", html.Br(), html.Span("Computarizada", className="gradient-text")], className="hero-title"),
                            html.P("CT-SIM es un entorno educativo para explorar la formación, adquisición, reconstrucción y procesamiento de imágenes de tomografía computarizada.", className="hero-text"),
                            html.Div(
                                [
                                    dbc.Button("EXPLORAR FUNDAMENTOS  →", href="/imaging/ct/teoria", className="btn-primary-ct"),
                                    dbc.Button("ABRIR SIMULADOR", href="/imaging/ct/simulador", color="secondary", className="btn-secondary-ct"),
                                ],
                                className="hero-buttons",
                            ),
                        ],
                        className="hero-copy",
                    ),
                    html.Div(
                        [
                            # Nota: Asegúrate de que Tomografo_hero.png esté en la carpeta /assets/
                            html.Img(src="/assets/Tomografo_hero.png", className="tomografo-img"),
                            html.Div([html.Span(className="live-dot"), " SIMULACIÓN EDUCATIVA"], className="live-badge"),
                        ],
                        className="hero-visual",
                    ),
                ],
                className="hero",
            ),
            html.Div(
                [
                    info_card("01", "Fundamentos", "Principios físicos, atenuación, HU, ventanas, componentes y formación de la imagen.", html.I(className="fa-solid fa-book-bookmark")),
                    info_card("02", "Adquisición", "Proyecciones, sinograma y conceptos esenciales de reconstrucción tomográfica.", html.I(className="fa-solid fa-circle-nodes")),
                    info_card("03", "Procesamiento", "Histogramas, CDF, contraste, gamma, filtros y técnicas de mejora de imagen.", html.I(className="fa-solid fa-sliders")),
                    info_card("04", "Inteligencia Artificial", "Herramientas de análisis educativo con Gemini y contexto calculado por Python.", html.I(className="fa-solid fa-wand-magic-sparkles")),
                ],
                className="feature-grid",
            ),
        ],
        className="page",
    )

def placeholder_page(title, subtitle):
    return html.Div(
        [
            section_header("Módulo", title, subtitle),
            html.Div(
                [
                    html.Div("EN CONSTRUCCIÓN", className="module-tag"),
                    html.H3(title, className="module-title"),
                    html.P("Esta sección se conectará con el código correspondiente durante la integración.", className="module-text"),
                ],
                className="empty-module",
            ),
        ],
        className="page",
    )

# ============================================================
# LAYOUT PÚBLICO Y CALLBACKS
# ============================================================
def render_page_ct(pathname):
    """Mapea la subruta de CT al componente correspondiente."""
    if pathname in (None, "", "/imaging/ct", "/imaging/ct/"):
        return layout_inicio()
    if pathname == "/imaging/ct/teoria":
        return layout_fundamentos()
    if pathname == "/imaging/ct/procesamiento":
        return procesamiento_layout()
    if pathname == "/imaging/ct/recursos":
        return layout_recursos()
    if pathname == "/imaging/ct/simulador":
        return simulador_layout()
    return placeholder_page("Página no encontrada", "La ruta solicitada no existe.")


def crear_layout_ct(pathname="/imaging/ct"):
    """Layout principal que Prometeo importa, renderizado directamente por pathname."""
    contenido = render_page_ct(pathname)
    return html.Div(
        [
            crear_sidebar_ct(active_path=pathname),
            html.Main(contenido, id="ct-page-content", className="content"),
            crear_gemini_widget(),
        ],
        className="ct-container",
    )


def registrar_callbacks_ct(app):
    """Registra todos los callbacks del módulo CT (procesamiento, Gemini y simulador)."""
    # ---- Callbacks de procesamiento ----
    registrar_callbacks_procesamiento(app)

    # ---- Callbacks de Gemini (Abrir/Cerrar chat y enviar pregunta) ----
    registrar_gemini_callbacks(app)

    # ---- Callbacks del simulador ----
    registrar_callbacks_simulador(app)