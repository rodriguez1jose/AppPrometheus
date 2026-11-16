# config.py
# =============================================================================
# PROMETEO — Configuración Global, Sistema de Diseño y Rutas Maestras
# =============================================================================
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# 1. RUTAS MAESTRAS DEL SISTEMA
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
RESULTADOS_DIR = BASE_DIR / "resultados"

# Asegurar directorios esenciales
RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
ESTUDIANTES_CSV = RESULTADOS_DIR / "resultados_estudiantes.csv"

# Rutas de datos por modalidad (con compatibilidad retroactiva durante migración)
RX_DATA_DIR = DATA_DIR / "rx"
RX_DATASET_DIR = RX_DATA_DIR / "dataset"
RX_LIBROS_DIR = RX_DATA_DIR / "libros"
RX_IMAGENES_DIR = RX_DATA_DIR / "imagenes"

def get_rx_imagenes_dir() -> Path:
    """Devuelve la ruta oficial de imágenes de Rayos X (originales y procesadas)."""
    if RX_IMAGENES_DIR.exists():
        return RX_IMAGENES_DIR
    old_dir = BASE_DIR / "imagenes_rx"
    if old_dir.exists():
        return old_dir
    RX_IMAGENES_DIR.mkdir(parents=True, exist_ok=True)
    return RX_IMAGENES_DIR

def get_rx_libros_dir() -> Path:
    """Devuelve la carpeta con la bibliografía de Rayos X en PDF."""
    if RX_LIBROS_DIR.exists():
        return RX_LIBROS_DIR
    old_dir = BASE_DIR / "libros_rx"
    if old_dir.exists():
        return old_dir
    RX_LIBROS_DIR.mkdir(parents=True, exist_ok=True)
    return RX_LIBROS_DIR

def get_rx_dataset_dir() -> Path:
    """Devuelve la carpeta con los textos base de Rayos X."""
    if RX_DATASET_DIR.exists():
        return RX_DATASET_DIR
    old_dir = BASE_DIR / "dataset_rx"
    if old_dir.exists():
        return old_dir
    RX_DATASET_DIR.mkdir(parents=True, exist_ok=True)
    return RX_DATASET_DIR


# ─────────────────────────────────────────────────────────────────────────────
# 2. TOKENS DE DISEÑO Y PALETA UNIFICADA (TEMA OSCURO PROMETEO + CIAN)
# ─────────────────────────────────────────────────────────────────────────────
THEME = {
    # Fondos
    'bg': '#0f172a',            # Fondo principal azul noche profundo
    'bg_secondary': '#1e293b',  # Fondo secundario para barras o bloques
    'card': '#1e293b',          # Color de tarjetas (Slate Navy)
    'card_border': '#334155',   # Borde de tarjetas
    'border': '#334155',        # Alias genérico para bordes

    # Tipografía
    'text': '#f8fafc',          # Texto principal de alta legibilidad
    'text_muted': '#cbd5e1',    # Texto secundario claro
    'text_secondary': '#cbd5e1',# Alias secundario
    'card_text': '#f8fafc',
    'card_text_secondary': '#cbd5e1',
    'sidebar_text': '#f8fafc',
    'sidebar_muted': '#94a3b8',

    # Acentos de Marca y Modalidades
    'accent_cyan': '#38bdf8',   # Acento Primario Prometeo y SyS
    'accent_teal': '#06b6d4',
    'accent_emerald': '#10b981',# Éxito / Operación correcta
    'accent_amber': '#f59e0b',  # Ámbar para Rx / Advertencias
    'accent_purple': '#a855f7', # Púrpura para MRI e IA
    'accent_red': '#ef4444',    # Errores

    # Compatibilidad con módulos heredados de Rayos X
    'green': '#38bdf8',         # Armonizado a Cyan
    'green_light': '#7dd3fc',
    'pink': '#38bdf8',          # Armonizado a Cyan para sustituir el rosa antiguo
    'pink_light': '#7dd3fc',
    'mauve': '#38bdf8',
}

# Paleta Clara (Light Mode) en alto contraste
THEME_LIGHT = {
    # Fondos
    'bg': '#f8fafc',            # Fondo claro
    'bg_secondary': '#f1f5f9',  # Fondo secundario
    'card': '#ffffff',          # Fondo de tarjetas blanco puro
    'card_border': '#e2e8f0',   # Borde sutil
    'border': '#e2e8f0',

    # Tipografía
    'text': '#0f172a',          # Texto oscuro principal
    'text_muted': '#475569',    # Texto secundario
    'text_secondary': '#64748b',
    'card_text': '#0f172a',
    'card_text_secondary': '#475569',
    'sidebar_text': '#0f172a',
    'sidebar_muted': '#64748b',

    # Acentos con contraste adaptado para fondo claro
    'accent_cyan': '#0284c7',
    'accent_teal': '#0d9488',
    'accent_emerald': '#059669',
    'accent_amber': '#d97706',
    'accent_purple': '#9333ea',
    'accent_red': '#dc2626',

    # Compatibilidad
    'green': '#0284c7',
    'green_light': '#38bdf8',
    'pink': '#0284c7',
    'pink_light': '#38bdf8',
    'mauve': '#0284c7',
}


def get_theme(mode: str = "dark") -> dict:
    """Devuelve el diccionario de colores correspondiente al modo ('dark' o 'light')."""
    return THEME_LIGHT if mode == "light" else THEME


# ─────────────────────────────────────────────────────────────────────────────
# 3. ESTILOS BASE COMPARTIDOS (COMPONENTES UI)
# ─────────────────────────────────────────────────────────────────────────────

STYLE_CONTAINER = {
    'fontFamily': '"Inter", "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif',
    'backgroundColor': THEME['bg'],
    'minHeight': '100vh',
    'padding': '20px 35px',
    'color': THEME['text'],
    'boxSizing': 'border-box',
}

STYLE_HEADER = {
    'background': 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0369a1 100%)',
    'padding': '26px 32px',
    'borderRadius': '16px',
    'border': f"1px solid {THEME['card_border']}",
    'boxShadow': '0 10px 25px -5px rgba(0, 0, 0, 0.5)',
    'marginBottom': '24px',
}

STYLE_CARD = {
    'backgroundColor': THEME['card'],
    'borderRadius': '14px',
    'padding': '22px',
    'border': f"1px solid {THEME['card_border']}",
    'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.3)',
    'marginBottom': '20px',
}

STYLE_CALLOUT = {
    'background': 'linear-gradient(90deg, rgba(56, 189, 248, 0.12) 0%, rgba(15, 23, 42, 0.6) 100%)',
    'borderLeft': f"4px solid {THEME['accent_cyan']}",
    'padding': '14px 18px',
    'borderRadius': '8px',
    'fontSize': '15px',
    'color': '#e0f2fe',
    'lineHeight': '1.5',
    'marginBottom': '16px',
}

STYLE_SECTION_TITLE = {
    'fontSize': '20px',
    'fontWeight': '700',
    'color': THEME['text'],
    'borderBottom': f"1px solid {THEME['card_border']}",
    'paddingBottom': '8px',
    'marginTop': '0px',
    'marginBottom': '14px',
}

STYLE_LABEL = {
    'fontWeight': '600',
    'fontSize': '15px',
    'color': THEME['text_muted'],
    'marginTop': '14px',
    'marginBottom': '6px',
    'display': 'block',
}

STYLE_GRAPH_DESC = {
    'color': THEME['text_muted'],
    'fontSize': '14px',
    'lineHeight': '1.5',
    'marginTop': '10px',
    'paddingTop': '10px',
    'borderTop': f"1px solid {THEME['card_border']}",
}

STYLE_MINI_BUTTON = {
    'background': 'linear-gradient(135deg, #0369a1, #0284c7)',
    'color': '#ffffff',
    'border': 'none',
    'padding': '7px 14px',
    'borderRadius': '8px',
    'fontWeight': '700',
    'fontSize': '12px',
    'cursor': 'pointer',
}
STYLE_MINI_BUTTON_ALT = {**STYLE_MINI_BUTTON, 'background': 'linear-gradient(135deg, #8b5cf6, #a78bfa)'}
STYLE_MINI_BUTTON_GREEN = {**STYLE_MINI_BUTTON, 'background': 'linear-gradient(135deg, #065f46, #059669)'}
STYLE_MINI_BUTTON_AMBER = {**STYLE_MINI_BUTTON, 'background': 'linear-gradient(135deg, #b45309, #d97706)'}

STYLE_ERROR_BOX = {
    'backgroundColor': 'rgba(239,68,68,0.12)',
    'border': '1px solid rgba(239,68,68,0.4)',
    'borderRadius': '8px',
    'padding': '8px 12px',
    'color': '#fca5a5',
    'fontSize': '12.5px',
    'marginTop': '8px',
}

STYLE_CONTROL_CARD = {
    'backgroundColor': THEME['card'],
    'borderRadius': '16px',
    'padding': '20px 22px',
    'border': f"1px solid {THEME['card_border']}",
    'boxShadow': '0 4px 14px rgba(0, 0, 0, 0.35)',
    'marginBottom': '18px',
}

STYLE_CONTROL_INPUT = {
    'width': '100%',
    'padding': '9px 12px',
    'backgroundColor': THEME['bg_secondary'],
    'border': f"1px solid {THEME['card_border']}",
    'borderRadius': '8px',
    'color': THEME['text'],
    'fontSize': '14px',
    'fontFamily': '"Fira Code", "Consolas", monospace',
    'boxSizing': 'border-box',
}

STYLE_SIDEBAR = {
    'width': '270px',
    'minWidth': '270px',
    'backgroundColor': THEME['bg_secondary'],
    'borderRight': f"1px solid {THEME['card_border']}",
    'padding': '28px 18px',
    'position': 'sticky',
    'top': '0',
    'height': '100vh',
    'overflowY': 'auto',
    'boxSizing': 'border-box',
    'fontFamily': '"Inter", "Segoe UI", -apple-system, sans-serif',
}

STYLE_CONTENT_AREA = {
    'flex': '1',
    'minWidth': '0',
    'backgroundColor': THEME['bg'],
    'fontFamily': '"Inter", "Segoe UI", -apple-system, sans-serif',
}

STYLE_EDU_CARD = {
    'backgroundColor': THEME['card'],
    'borderRadius': '16px',
    'padding': '26px 28px',
    'border': f"1px solid {THEME['card_border']}",
    'boxShadow': '0 4px 14px rgba(0, 0, 0, 0.35)',
    'marginBottom': '22px',
}

STYLE_EDU_PAGE_HEADER = {
    'background': 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0369a1 100%)',
    'padding': '30px 34px',
    'borderRadius': '16px',
    'border': f"1px solid {THEME['card_border']}",
    'boxShadow': '0 10px 25px -5px rgba(0, 0, 0, 0.5)',
    'marginBottom': '26px',
}

STYLE_PILL = {
    'backgroundColor': 'rgba(56, 189, 248, 0.2)',
    'color': THEME['accent_cyan'],
    'padding': '4px 12px',
    'borderRadius': '20px',
    'fontSize': '11px',
    'fontWeight': '700',
    'border': '1px solid rgba(56,189,248,0.4)',
    'letterSpacing': '0.5px',
}

STYLE_MODAL_OVERLAY_HIDDEN = {'display': 'none'}
STYLE_MODAL_OVERLAY_VISIBLE = {
    'display': 'flex',
    'position': 'fixed',
    'top': '0', 'left': '0', 'width': '100%', 'height': '100%',
    'backgroundColor': 'rgba(2,6,15,0.78)',
    'zIndex': '9998',
    'alignItems': 'center',
    'justifyContent': 'center',
}

STYLE_MODAL_BOX = {
    'backgroundColor': THEME['card'],
    'border': f"1px solid {THEME['card_border']}",
    'borderTop': f"3px solid {THEME['accent_cyan']}",
    'borderRadius': '16px',
    'padding': '26px 30px',
    'maxWidth': '580px',
    'width': '90%',
    'maxHeight': '80vh',
    'overflowY': 'auto',
    'boxShadow': '0 20px 50px rgba(0,0,0,0.6)',
    'fontFamily': '"Inter", "Segoe UI", -apple-system, sans-serif',
}

# Estilos de Quizzes y Actividades
STYLE_QUIZ_CARD = {
    'backgroundColor': THEME['card'],
    'borderRadius': '16px',
    'padding': '24px 28px',
    'border': f"1px solid {THEME['card_border']}",
    'boxShadow': '0 4px 14px rgba(0, 0, 0, 0.35)',
    'marginBottom': '18px',
}

STYLE_OPTION_BUTTON = {
    'backgroundColor': THEME['card'],
    'border': f"1px solid {THEME['card_border']}",
    'borderRadius': '10px',
    'padding': '12px 18px',
    'color': THEME['text'],
    'cursor': 'pointer',
    'width': '100%',
    'textAlign': 'left',
    'fontSize': '14px',
    'transition': 'all 0.2s ease',
}

STYLE_OPTION_SELECTED = {
    'backgroundColor': THEME['card'],
    'border': f"2px solid {THEME['accent_cyan']}",
    'borderRadius': '10px',
    'padding': '12px 18px',
    'color': THEME['accent_cyan'],
    'cursor': 'pointer',
    'width': '100%',
    'textAlign': 'left',
    'fontSize': '14px',
    'boxShadow': '0 0 15px rgba(56, 189, 248, 0.15)',
}

STYLE_ADVANCED_HEADER_BTN = {
    'width': '100%',
    'background': 'linear-gradient(90deg, #1e293b 0%, #0f172a 100%)',
    'border': f"1px solid {THEME['card_border']}",
    'borderRadius': '10px',
    'padding': '14px 18px',
    'color': THEME['text'],
    'fontWeight': '700',
    'fontSize': '15px',
    'cursor': 'pointer',
    'display': 'flex',
    'justifyContent': 'space-between',
    'alignItems': 'center',
}

STYLE_ADVANCED_PANEL_HIDDEN = {'display': 'none'}
STYLE_ADVANCED_PANEL_VISIBLE = {
    'display': 'block',
    'marginTop': '12px',
    'padding': '18px',
    'backgroundColor': THEME['card'],
    'border': f"1px solid {THEME['card_border']}",
    'borderRadius': '12px',
}

STYLE_MARGIN_PILL_OK = {
    'backgroundColor': 'rgba(16,185,129,0.15)', 'color': '#10b981',
    'padding': '4px 10px', 'borderRadius': '8px', 'fontWeight': '700', 'fontSize': '12px'
}
STYLE_MARGIN_PILL_BAD = {
    'backgroundColor': 'rgba(239,68,68,0.15)', 'color': '#f87171',
    'padding': '4px 10px', 'borderRadius': '8px', 'fontWeight': '700', 'fontSize': '12px'
}


# ─────────────────────────────────────────────────────────────────────────────
# 4. CSS OSCURO GLOBAL Y SANEAMIENTO DE ESTILOS
# ─────────────────────────────────────────────────────────────────────────────

DARK_CSS = """
/* Reset y tipografía global uniforme */
html, body, #react-entry-point, .dash-app-content {
    font-family: "Inter", "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif !important;
    background-color: #0a0f1d !important;
    color: #f8fafc !important;
}

/* Neutralización de sobreescrituras heredadas en títulos y párrafos */
h1, h2, h3, h4, h5, h6,
.teoria-section-title, .teoria-card-title, .teoria-visual-title {
    font-family: "Inter", "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: #f8fafc !important;
}

.teoria-intro, .teoria-card-body p, .teoria-highlight p, .teoria-formula-text, .teoria-visual-text p {
    color: #cbd5e1 !important;
}

/* Dropdowns oscuros de Dash */
.dash-dropdown,
.dash-dropdown .Select-control,
.Select-control,
div[class*="control"] {
    background-color: #1e293b !important;
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    color: #ffffff !important;
}

.dash-dropdown .Select-value-label,
.Select-value-label,
.Select-placeholder,
div[class*="singleValue"],
div[class*="placeholder"],
div[class*="ValueContainer"] * {
    color: #ffffff !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}

.Select-menu-outer,
.Select-menu,
.Select-menu-outer > div,
.Select-menu > div,
div[class*="menu"],
div[class*="MenuList"] {
    background-color: #1e293b !important;
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.7) !important;
    z-index: 99999 !important;
}

.Select-input,
.Select-input > input,
div[class*="Input"],
div[class*="Input"] input,
div[class*="search"],
div[class*="search"] input {
    background-color: #0f172a !important;
    background: #0f172a !important;
    color: #ffffff !important;
    border: 1px solid #334155 !important;
    border-radius: 6px !important;
}

.VirtualizedSelectOption,
.VirtualizedSelectOption *,
.Select-option,
.Select-option *,
div[class*="option"],
div[class*="option"] *,
.Select-menu-outer div:not(.is-selected):not(.is-focused):not([class*="-is-selected"]):not([class*="-is-focused"]),
.Select-menu-outer span,
.Select-menu div,
.Select-menu span {
    background-color: #1e293b !important;
    background: #1e293b !important;
    color: #ffffff !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}

.VirtualizedSelectFocusedOption,
.VirtualizedSelectFocusedOption *,
.Select-option.is-selected,
.Select-option.is-selected *,
.Select-option.is-focused,
.Select-option.is-focused *,
.VirtualizedSelectOption.is-selected,
.VirtualizedSelectOption.is-selected *,
div[class*="-is-selected"],
div[class*="-is-selected"] *,
div[class*="-is-focused"],
div[class*="-is-focused"] * {
    background-color: #1e293b !important;
    background: #1e293b !important;
    color: #38bdf8 !important;
    font-weight: 700 !important;
}

.Select-arrow {
    border-color: #94a3b8 transparent transparent !important;
}

/* Sliders interactivos */
.rc-slider-mark-text {
    color: #94a3b8 !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    background: transparent !important;
}

.rc-slider-mark-text-active {
    color: #38bdf8 !important;
    font-weight: 700 !important;
}

.rc-slider-rail {
    background-color: #334155 !important;
    height: 6px !important;
}

.rc-slider-track {
    background-color: #38bdf8 !important;
    height: 6px !important;
}

.rc-slider-handle {
    border: 2px solid #7dd3fc !important;
    background-color: #0284c7 !important;
    width: 16px !important;
    height: 16px !important;
    margin-top: -5px !important;
}

input[type="number"],
.dash-input,
div[class*="number-input"],
.rc-slider-tooltip-inner {
    background-color: #1e293b !important;
    color: #38bdf8 !important;
    border: 1px solid #475569 !important;
    border-radius: 6px !important;
    font-weight: 800 !important;
    font-size: 13.5px !important;
    text-align: center !important;
    padding: 4px 8px !important;
}

.edu-image {
    width: 100%;
    border-radius: 10px;
    margin: 8px 0 12px 0;
    border: 1px solid #334155;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
.edu-image-container {
    display: flex;
    justify-content: center;
    margin: 10px 0 6px 0;
}
.img-caption {
    color: #94a3b8;
    font-size: 12px;
    text-align: center;
    margin-top: 4px;
    font-style: italic;
}
"""

EXTRA_CSS = """
.sidebar-link {
    display: flex;
    align-items: center;
    padding: 11px 14px;
    border-radius: 10px;
    color: #cbd5e1;
    text-decoration: none;
    transition: all 0.15s ease;
    margin-bottom: 3px;
}
.sidebar-link:hover {
    background-color: rgba(56, 189, 248, 0.12);
    color: #38bdf8;
}
.sidebar-link i {
    color: #38bdf8 !important;
    transition: color 0.15s ease;
}
.sidebar-link:hover i {
    color: #7dd3fc !important;
}

.term-link {
    color: #38bdf8;
    background: none;
    border: none;
    border-bottom: 1px dashed #38bdf8;
    padding: 0 1px;
    font: inherit;
    font-weight: 700;
    cursor: pointer;
    transition: color 0.15s ease;
}
.term-link:hover {
    color: #f59e0b;
    border-bottom-color: #f59e0b;
}

.edu-card:hover {
    box-shadow: 0 8px 22px rgba(0, 0, 0, 0.5);
    transition: box-shadow 0.2s ease;
}

.modal-close-btn {
    background: rgba(148,163,184,0.15);
    border: none;
    color: #cbd5e1;
    width: 30px;
    height: 30px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 15px;
}
.modal-close-btn:hover {
    background: rgba(239,68,68,0.25);
    color: #f87171;
}

.nav-cta-btn {
    background: linear-gradient(135deg, #0369a1, #0284c7);
    color: #ffffff;
    border: none;
    padding: 12px 22px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 14px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
}
.nav-cta-btn:hover {
    background: linear-gradient(135deg, #0284c7, #38bdf8);
}

/* Scrollbars sobrios */
::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-track { background: #0a0f1d !important; }
::-webkit-scrollbar-thumb { background: #334155 !important; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #475569 !important; }

mjx-container { color: inherit !important; }
mjx-container[display="true"] {
    margin: 0.5em 0 !important;
    text-align: center !important;
}
mjx-container svg { vertical-align: middle !important; }

/* Tarjetas de carátula */
.home-card {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    cursor: pointer;
}
.home-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6);
}
"""

THEME_CSS = """
/* =============================================================================
   SISTEMA DE TEMAS DINÁMICO (CLARO / OSCURO) Y DEFINICIÓN DE VARIABLES
   ============================================================================= */
:root, body, body.dark-theme {
    --color-bg: #0a0f1d;
    --color-bg-secondary: #111827;
    --color-card: #1e293b;
    --color-card-border: #334155;
    --color-border: #334155;
    --color-text: #f8fafc;
    --color-text-muted: #cbd5e1;
    --color-text-secondary: #94a3b8;
    --color-accent-cyan: #38bdf8;
    --color-accent-purple: #c084fc;
    --color-accent-amber: #f59e0b;
    --color-accent-emerald: #10b981;
    --color-accent-red: #f87171;
}

body.light-theme {
    --color-bg: #f8fafc;
    --color-bg-secondary: #f1f5f9;
    --color-card: #ffffff;
    --color-card-border: #e2e8f0;
    --color-border: #e2e8f0;
    --color-text: #0f172a;
    --color-text-muted: #475569;
    --color-text-secondary: #64748b;
    --color-accent-cyan: #0284c7;
    --color-accent-purple: #7e22ce;
    --color-accent-amber: #b45309;
    --color-accent-emerald: #059669;
    --color-accent-red: #dc2626;
}

body.dark-theme {
    background-color: #0a0f1d !important;
    color: #f8fafc !important;
}

body.light-theme {
    background-color: #f8fafc !important;
    color: #0f172a !important;
}

body.light-theme #main-app-container {
    background-color: #f8fafc !important;
    color: #0f172a !important;
}

/* =============================================================================
   ADAPTACIÓN PROFUNDA DE FONDOS OSCUROS A CLAROS (LIGHT THEME)
   ============================================================================= */
/* Fondos de nivel 1 (Página / Contenedores principales) */
body.light-theme div[style*="#0a0f1d"],
body.light-theme div[style*="rgb(10, 15, 29)"],
body.light-theme div[style*="#0f172a"],
body.light-theme div[style*="rgb(15, 23, 42)"],
body.light-theme div[style*="#111827"],
body.light-theme div[style*="rgb(17, 24, 39)"] {
    background-color: #f8fafc !important;
}

/* Fondos de nivel 2 (Tarjetas, Paneles, Sidebars, Contenedores de fórmulas y ejercicios) */
body.light-theme div[style*="#1e293b"],
body.light-theme div[style*="rgb(30, 41, 59)"],
body.light-theme div[style*="#0d1424"],
body.light-theme div[style*="rgb(13, 20, 36)"],
body.light-theme div[style*="#0d1527"],
body.light-theme div[style*="rgb(13, 21, 39)"],
body.light-theme div[style*="#151D2E"],
body.light-theme div[style*="#151d2e"],
body.light-theme div[style*="rgb(21, 29, 46)"],
body.light-theme div[style*="#162032"],
body.light-theme div[style*="rgb(22, 32, 50)"],
body.light-theme div[style*="#131d2e"],
body.light-theme div[style*="rgb(19, 29, 46)"],
body.light-theme div[style*="#17152B"],
body.light-theme div[style*="#17152b"],
body.light-theme div[style*="rgb(23, 21, 43)"],
body.light-theme div[style*="#1e1e2f"],
body.light-theme div[style*="#273449"],
body.light-theme div[style*="rgb(39, 52, 73)"],
body.light-theme div[style*="#0B1220"],
body.light-theme div[style*="#0b1220"],
body.light-theme div[style*="rgb(11, 18, 32)"],
body.light-theme div[style*="#101A2B"],
body.light-theme div[style*="#101a2b"],
body.light-theme div[style*="rgb(16, 26, 43)"],
body.light-theme div[style*="#07111F"],
body.light-theme div[style*="#07111f"],
body.light-theme div[style*="rgb(7, 17, 31)"],
body.light-theme div[style*="#18243A"],
body.light-theme div[style*="#18243a"],
body.light-theme div[style*="rgb(24, 36, 58)"],
body.light-theme div[style*="#080F1D"],
body.light-theme div[style*="#080f1d"],
body.light-theme div[style*="rgb(8, 15, 29)"],
body.light-theme div[style*="#101D2D"],
body.light-theme div[style*="#101d2d"],
body.light-theme div[style*="rgb(16, 29, 45)"],
body.light-theme div[style*="#26354A"],
body.light-theme div[style*="#26354a"],
body.light-theme div[style*="rgb(38, 53, 74)"],
body.light-theme div[style*="#121B2A"],
body.light-theme div[style*="#121b2a"],
body.light-theme div[style*="rgb(18, 27, 42)"],
body.light-theme div[style*="#101A29"],
body.light-theme div[style*="#101a29"],
body.light-theme div[style*="#102A40"],
body.light-theme div[style*="#102a40"],
body.light-theme div[style*="rgb(16, 42, 64)"],
body.light-theme div[style*="#0B1120"],
body.light-theme div[style*="#0b1120"] {
    background: #ffffff !important;
    border-color: #e2e8f0 !important;
}

/* Headers, banners y tarjetas con degradado oscuro transformados a blanco/claro */
body.light-theme div[style*="linear-gradient(135deg, #0f172a"],
body.light-theme div[style*="linear-gradient(135deg, rgb(15, 23, 42)"],
body.light-theme div[style*="linear-gradient(135deg, #111827"],
body.light-theme div[style*="linear-gradient(135deg,#111827"],
body.light-theme div[style*="linear-gradient(135deg, rgb(17, 24, 39)"],
body.light-theme div[style*="linear-gradient(145deg, #111827"],
body.light-theme div[style*="linear-gradient(145deg,#111827"],
body.light-theme div[style*="linear-gradient(145deg, rgb(17, 24, 39)"],
body.light-theme div[style*="linear-gradient(135deg, #17152B"],
body.light-theme div[style*="linear-gradient(135deg,#17152B"],
body.light-theme div[style*="linear-gradient(135deg, #101D2B"],
body.light-theme div[style*="linear-gradient(135deg,#101D2B"],
body.light-theme div[style*="linear-gradient(145deg, rgba(30,41,59"],
body.light-theme div[style*="linear-gradient(145deg,rgba(30,41,59"],
body.light-theme div[style*="linear-gradient(145deg, rgba(30, 41, 59"],
body.light-theme div[style*="linear-gradient(145deg,rgba(30, 41, 59"],
body.light-theme .rx-hero-card,
body.light-theme .rx-card,
body.light-theme .rx-control-card,
body.light-theme .rx-filter-card,
body.light-theme .info-card,
body.light-theme .theory-main-card,
body.light-theme .visual-card,
body.light-theme .learning-panel,
body.light-theme .resource-banner,
body.light-theme .empty-module,
body.light-theme .ct-fundamento-card,
body.light-theme .ct-comparison-card,
body.light-theme .ct-process-card {
    background: #ffffff !important;
    background-image: none !important;
    border-color: #e2e8f0 !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
}

/* Hero Cards en RX: texto oscuro de alto contraste */
body.light-theme .rx-hero-card h1 {
    color: #0f172a !important;
}
body.light-theme .rx-hero-card p {
    color: #475569 !important;
}
body.light-theme .rx-hero-card div[style*="letterSpacing"],
body.light-theme .rx-hero-card div[style*="letter-spacing"] {
    color: #0284c7 !important;
}

/* Tarjetas y pasos en CT */
body.light-theme .ct-flujo-step-box {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
}
body.light-theme .ct-flujo-step-box #tc-step-title {
    color: #0284c7 !important;
}
body.light-theme .ct-flujo-step-box #tc-step-text {
    color: #334155 !important;
}

body.light-theme .ct-fundamento-card h1,
body.light-theme .ct-fundamento-card h2,
body.light-theme .ct-fundamento-card h3,
body.light-theme .ct-fundamento-card h4,
body.light-theme .ct-fundamento-card h5,
body.light-theme .ct-fundamento-card h6 {
    color: #0f172a !important;
}
body.light-theme .ct-fundamento-card p {
    color: #334155 !important;
}

body.light-theme .ct-subcard {
    background: #f8fafc !important;
    background-image: none !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03) !important;
}
body.light-theme .ct-subcard h3,
body.light-theme .ct-subcard h4,
body.light-theme .ct-subcard h5 {
    color: #0f172a !important;
}
body.light-theme .ct-subcard p,
body.light-theme .ct-subcard span:not([class*="fa-"]) {
    color: #475569 !important;
}

body.light-theme .ct-concept-btn,
body.light-theme button[id^="concepto-"],
body.light-theme button[id^="idea-tc-"] {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
}
body.light-theme .ct-concept-btn:hover,
body.light-theme button[id^="concepto-"]:hover,
body.light-theme button[id^="idea-tc-"]:hover {
    background: #f1f5f9 !important;
    border-color: #0284c7 !important;
}
body.light-theme .ct-concept-btn div,
body.light-theme button[id^="concepto-"] div,
body.light-theme button[id^="idea-tc-"] div {
    color: #0f172a !important;
}
body.light-theme button[id^="concepto-"] div[style*="borderRadius: 50%"],
body.light-theme button[id^="concepto-"] div[style*="border-radius: 50%"],
body.light-theme button[id^="concepto-"] div[style*="border-radius:50%"] {
    background: #e2e8f0 !important;
    color: #0284c7 !important;
}
body.light-theme button[id^="idea-tc-"] div[style*="borderRadius: 50%"],
body.light-theme button[id^="idea-tc-"] div[style*="border-radius: 50%"],
body.light-theme button[id^="idea-tc-"] div[style*="border-radius:50%"] {
    background: #0284c7 !important;
    color: #ffffff !important;
}

body.light-theme .ct-info-callout {
    background: #f1f5f9 !important;
    border-color: #cbd5e1 !important;
}
body.light-theme .ct-callout-text,
body.light-theme .ct-info-callout .ct-callout-text,
body.light-theme .ct-info-callout p,
body.light-theme .ct-info-callout div[style*="#E5E7EB"],
body.light-theme .ct-info-callout div[style*="#D1D5DB"],
body.light-theme .ct-info-callout span[style*="#E5E7EB"] {
    color: #0f172a !important;
    font-weight: 500 !important;
}

/* Índice de contenidos en CT Fundamentos (/imaging/ct/teoria) */
body.light-theme .ct-index-card {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
}

body.dark-theme .ct-index-card,
.ct-index-card {
    background: #0f172a !important;
    border: 1px solid #273449 !important;
}

body.light-theme .ct-index-title,
body.light-theme .ct-index-card h3,
body.light-theme .ct-index-card .ct-index-title {
    color: #0f172a !important;
}

body.light-theme .ct-index-title i,
body.light-theme .ct-index-card h3 i {
    color: #0284c7 !important;
}

body.dark-theme .ct-index-title,
body.dark-theme .ct-index-card h3,
.ct-index-title {
    color: #f8fafc !important;
}

body.dark-theme .ct-index-title i,
.ct-index-title i {
    color: #38bdf8 !important;
}

/* Píldoras / Botones del menú de contenidos */
body.light-theme .ct-index-link,
body.light-theme .ct-index-card a,
body.light-theme a.ct-index-link {
    color: #0f172a !important;
    background: #f1f5f9 !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    text-decoration: none !important;
    font-weight: 600 !important;
    transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease !important;
}

body.light-theme .ct-index-link:hover,
body.light-theme .ct-index-card a:hover,
body.light-theme a.ct-index-link:hover {
    background: #e2e8f0 !important;
    border-color: #94a3b8 !important;
    color: #0f172a !important;
}

body.light-theme .ct-index-link:active,
body.light-theme .ct-index-link.active,
body.light-theme a.ct-index-link:active,
body.light-theme a.ct-index-link.active {
    background: #0284c7 !important;
    border-color: #0284c7 !important;
    color: #ffffff !important;
}

body.dark-theme .ct-index-link,
.ct-index-link {
    color: #cbd5e1 !important;
    background: #151d2e !important;
    border: 1px solid #273449 !important;
    border-radius: 8px !important;
    text-decoration: none !important;
    font-weight: 600 !important;
}

body.dark-theme .ct-index-link:hover,
.ct-index-link:hover {
    background: #1e293b !important;
    border-color: #475569 !important;
    color: #f8fafc !important;
}

body.dark-theme .ct-index-link:active,
body.dark-theme .ct-index-link.active,
.ct-index-link:active,
.ct-index-link.active {
    background: #0284c7 !important;
    border-color: #38bdf8 !important;
    color: #ffffff !important;
}

/* Caja de la Transformada de Radon en /imaging/ct/teoria */
.ct-radon-box,
body.light-theme .ct-radon-box,
body.dark-theme .ct-radon-box {
    background: #151f31 !important;
    border: 1px solid #3b4a63 !important;
}

.ct-radon-tag,
body.light-theme .ct-radon-tag,
body.dark-theme .ct-radon-tag {
    color: #c4b5fd !important;
}

.ct-radon-title,
body.light-theme .ct-radon-title,
body.dark-theme .ct-radon-title,
body.light-theme .ct-radon-box .ct-radon-title,
body.dark-theme .ct-radon-box .ct-radon-title,
body.light-theme div.ct-radon-title,
body.dark-theme div.ct-radon-title {
    color: #ffffff !important;
    font-size: 20px !important;
    font-weight: 800 !important;
    letter-spacing: 0.5px !important;
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.4) !important;
}

.ct-radon-formula,
body.light-theme .ct-radon-formula,
body.dark-theme .ct-radon-formula {
    color: #38bdf8 !important;
}

/* Switch de Tema Global (#theme-toggle-btn) */
body.dark-theme #theme-toggle-btn {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    color: #f8fafc !important;
}

body.dark-theme #theme-toggle-btn:hover {
    background: rgba(255, 255, 255, 0.15) !important;
    border-color: #38bdf8 !important;
}

body.light-theme #theme-toggle-btn {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    color: #0f172a !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
}

body.light-theme #theme-toggle-btn:hover {
    background: #f1f5f9 !important;
    border-color: #0284c7 !important;
    color: #0284c7 !important;
}

body.light-theme #theme-toggle-btn #theme-toggle-icon,
body.light-theme #theme-toggle-btn #theme-toggle-text {
    color: #0f172a !important;
}

body.light-theme #theme-toggle-btn:hover #theme-toggle-icon,
body.light-theme #theme-toggle-btn:hover #theme-toggle-text {
    color: #0284c7 !important;
}

/* Contenedores de flujo y cajas de visualización en RX y CT */
body.light-theme .rx-flow-container,
body.light-theme div[style*="padding: 16px 10px"][style*="overflow: hidden"],
body.light-theme div[style*="padding: 14px 10px"][style*="overflow: hidden"] {
    background-color: #f8fafc !important;
    border-color: #e2e8f0 !important;
}

body.light-theme .rx-flow-step,
body.light-theme .rx-image-box {
    background-color: #ffffff !important;
    border-color: #cbd5e1 !important;
    color: #0f172a !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04) !important;
}

body.light-theme .teoria-imagen,
body.light-theme div[style*="maxHeight: 330px"],
body.light-theme div[style*="max-height: 330px"] {
    background-color: #f8fafc !important;
    border-color: #e2e8f0 !important;
}

/* Callouts informativos */
body.light-theme div[style*="linear-gradient(90deg, rgba(56, 189, 248"],
body.light-theme div[style*="rgba(34,211,238,.08)"],
body.light-theme div[style*="rgba(34, 211, 238, 0.08)"] {
    background: linear-gradient(90deg, rgba(2, 132, 199, 0.08) 0%, rgba(241, 245, 249, 0.95) 100%) !important;
    color: #0369a1 !important;
    border-left-color: #0284c7 !important;
}

/* Bordes en tema claro */
body.light-theme div[style*="#334155"],
body.light-theme div[style*="rgb(51, 65, 85)"],
body.light-theme div[style*="#273449"],
body.light-theme div[style*="#1f2937"] {
    border-color: #e2e8f0 !important;
}

/* =============================================================================
   TIPOGRAFÍA Y CONTRASTE EN TEMA CLARO
   ============================================================================= */
body.light-theme h1,
body.light-theme h2,
body.light-theme h3,
body.light-theme h4,
body.light-theme h5,
body.light-theme h6 {
    color: #0f172a !important;
}

body.light-theme p,
body.light-theme label {
    color: #334155 !important;
}

/* Textos blancos / claros inline que pasan a texto oscuro */
body.light-theme [style*="#f8fafc"]:not(button):not(.nav-cta-btn):not(.btn-primary-ct):not(.ct-radon-title),
body.light-theme [style*="rgb(248, 250, 252)"]:not(button):not(.nav-cta-btn):not(.btn-primary-ct):not(.ct-radon-title),
body.light-theme [style*="#F8FAFC"]:not(button):not(.nav-cta-btn):not(.btn-primary-ct):not(.ct-radon-title),
body.light-theme [style*="#f1f5f9"]:not(button):not(.nav-cta-btn):not(.btn-primary-ct):not(.ct-radon-title),
body.light-theme [style*="rgb(241, 245, 249)"]:not(button):not(.nav-cta-btn):not(.btn-primary-ct):not(.ct-radon-title),
body.light-theme [style*="#ffffff"]:not(button):not(.nav-cta-btn):not(.btn-primary-ct):not([style*="linear-gradient"]):not(.badge):not(.ct-radon-title),
body.light-theme [style*="rgb(255, 255, 255)"]:not(button):not(.nav-cta-btn):not(.btn-primary-ct):not([style*="linear-gradient"]):not(.badge):not(.ct-radon-title),
body.light-theme [style*="#FFFFFF"]:not(button):not(.nav-cta-btn):not(.btn-primary-ct):not([style*="linear-gradient"]):not(.badge):not(.ct-radon-title),
body.light-theme [style*="#F9FAFB"]:not(button):not(.ct-radon-title),
body.light-theme [style*="#f9fafb"]:not(button):not(.ct-radon-title),
body.light-theme [style*="rgb(249, 250, 251)"]:not(button):not(.ct-radon-title),
body.light-theme [style*="#e2e8f0"]:not(button):not(.nav-cta-btn):not(.ct-radon-title),
body.light-theme [style*="rgb(226, 232, 240)"]:not(button):not(.nav-cta-btn):not(.ct-radon-title),
body.light-theme [style*="#D1D5DB"]:not(button):not(.ct-radon-title),
body.light-theme [style*="#d1d5db"]:not(button):not(.ct-radon-title),
body.light-theme [style*="rgb(209, 213, 219)"]:not(button):not(.ct-radon-title),
body.light-theme [style*="#E5E7EB"]:not(button):not(.ct-radon-title),
body.light-theme [style*="#e5e7eb"]:not(button):not(.ct-radon-title),
body.light-theme [style*="rgb(229, 231, 235)"]:not(button):not(.ct-radon-title),
body.light-theme [style*="#e0f2fe"]:not(button) {
    color: #0f172a !important;
}

/* Textos muted inline */
body.light-theme [style*="#94a3b8"],
body.light-theme [style*="#94A3B8"],
body.light-theme [style*="rgb(148, 163, 184)"],
body.light-theme [style*="#cbd5e1"],
body.light-theme [style*="#CBD5E1"],
body.light-theme [style*="rgb(203, 213, 225)"],
body.light-theme [style*="#9CA3AF"],
body.light-theme [style*="#9ca3af"],
body.light-theme [style*="rgb(156, 163, 175)"],
body.light-theme [style*="#AEBBD0"],
body.light-theme [style*="#aebbd0"],
body.light-theme [style*="rgb(174, 187, 208)"],
body.light-theme [style*="#B8C4D9"],
body.light-theme [style*="#b8c4d9"],
body.light-theme [style*="rgb(184, 196, 217)"] {
    color: #475569 !important;
}

/* Acentos de alto contraste en modo claro */
body.light-theme [style*="#38bdf8"]:not(button):not(.btn-primary-ct):not(.badge):not([style*="background"]):not([style*="linear-gradient"]),
body.light-theme [style*="#38BDF8"]:not(button):not(.btn-primary-ct):not(.badge):not([style*="background"]):not([style*="linear-gradient"]),
body.light-theme [style*="#22D3EE"]:not(button):not(.btn-primary-ct):not(.badge):not([style*="background"]):not([style*="linear-gradient"]),
body.light-theme [style*="#22d3ee"]:not(button):not(.btn-primary-ct):not(.badge):not([style*="background"]):not([style*="linear-gradient"]),
body.light-theme [style*="rgb(56, 189, 248)"]:not(button):not(.btn-primary-ct):not(.badge):not([style*="background"]),
body.light-theme [style*="rgb(34, 211, 238)"]:not(button):not(.btn-primary-ct):not(.badge):not([style*="background"]) {
    color: #0284c7 !important;
}

body.light-theme [style*="#8B5CF6"]:not(button):not(.badge):not([style*="background"]):not([style*="linear-gradient"]),
body.light-theme [style*="#8b5cf6"]:not(button):not(.badge):not([style*="background"]):not([style*="linear-gradient"]),
body.light-theme [style*="#A78BFA"]:not(button):not(.badge):not([style*="background"]):not([style*="linear-gradient"]),
body.light-theme [style*="#a78bfa"]:not(button):not(.badge):not([style*="background"]):not([style*="linear-gradient"]),
body.light-theme [style*="#C4B5FD"]:not(button):not(.badge):not([style*="background"]):not([style*="linear-gradient"]),
body.light-theme [style*="#c4b5fd"]:not(button):not(.badge):not([style*="background"]):not([style*="linear-gradient"]) {
    color: #7c3aed !important;
}

/* Pastillas y badges de RX */
body.light-theme .rx-badge-pill,
body.light-theme span[style*="borderRadius: 999px"][style*="#38bdf8"],
body.light-theme span[style*="border-radius: 999px"][style*="#38bdf8"] {
    background-color: #0284c7 !important;
    color: #ffffff !important;
}

/* Módulo CT en Tema Claro */
body.light-theme .ct-container {
    background: #f8fafc !important;
}
body.light-theme .sidebar {
    background: #ffffff !important;
    border-right-color: #e2e8f0 !important;
}
body.light-theme .content {
    background: #f8fafc !important;
}
body.light-theme .brand-name {
    color: #0f172a !important;
}
body.light-theme .ct-nav-link {
    color: #475569 !important;
}
body.light-theme .ct-nav-link:hover,
body.light-theme .ct-nav-link.active {
    background: rgba(2, 132, 199, 0.08) !important;
    color: #0284c7 !important;
    border-left-color: #0284c7 !important;
}
body.light-theme .sidebar-status {
    background: #f8fafc !important;
    border-color: #e2e8f0 !important;
}
body.light-theme .system-status {
    color: #475569 !important;
}
body.light-theme .hero-title {
    color: #0f172a !important;
}
body.light-theme .hero-text {
    color: #334155 !important;
}
body.light-theme .card-title {
    color: #0f172a !important;
}
body.light-theme .card-text {
    color: #475569 !important;
}
body.light-theme .card-icon {
    color: #0284c7 !important;
}
body.light-theme .live-badge {
    background: #ffffff !important;
    border-color: #e2e8f0 !important;
    color: #475569 !important;
}

/* Flujo TC en /imaging/ct/teoria */
body.light-theme button[id^="tc-step-"] {
    background: #ffffff !important;
    border-color: #cbd5e1 !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
}
body.light-theme button[id^="tc-step-"] span {
    color: #0f172a !important;
}
body.light-theme button[id^="tc-step-"] span[style*="borderRadius: 50%"],
body.light-theme button[id^="tc-step-"] span[style*="border-radius: 50%"],
body.light-theme button[id^="tc-step-"] span[style*="border-radius:50%"] {
    background: #e2e8f0 !important;
    color: #0f172a !important;
}
body.light-theme #tc-current-number {
    background: #0284c7 !important;
    color: #ffffff !important;
}
body.light-theme #tc-step-title {
    color: #0284c7 !important;
}
body.light-theme #tc-step-text {
    color: #334155 !important;
}

/* Tarjetas y subpaneles educativos en /sys/fourier y módulos */
.edu-subcard,
.edu-formula-box {
    transition: background-color 0.2s, border-color 0.2s;
}

body.dark-theme .edu-subcard,
body.dark-theme .edu-formula-box {
    background-color: #0d1424 !important;
    border-color: #334155 !important;
}

body.light-theme .edu-subcard,
body.light-theme .edu-formula-box {
    background-color: #ffffff !important;
    border-color: #e2e8f0 !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
}

body.light-theme .edu-table {
    background-color: #ffffff !important;
    border-color: #e2e8f0 !important;
}

body.light-theme .edu-table th {
    background-color: #f1f5f9 !important;
    color: #0284c7 !important;
    border-bottom-color: #e2e8f0 !important;
}

body.light-theme .edu-table td {
    color: #0f172a !important;
    border-bottom-color: #f1f5f9 !important;
}

/* Fórmulas destacadas */
.math-formula-callout {
    color: #fcd34d;
    transition: color 0.2s;
}

body.light-theme .math-formula-callout {
    color: #0284c7 !important;
}

body.dark-theme .math-formula-callout {
    color: #fcd34d !important;
}

/* PRESERVAR TEXTO BLANCO EN BOTONES CON FONDO OSCURO O GRADIENTE */
body.light-theme .nav-cta-btn,
body.light-theme .btn-primary-ct,
body.light-theme button[style*="linear-gradient"],
body.light-theme a[style*="linear-gradient"],
body.light-theme .btn-primary {
    color: #ffffff !important;
}

/* BOTÓN SECUNDARIO CT ("ABRIR SIMULADOR") - TEXTO OSCURO EN FONDO BLANCO */
body.light-theme .btn-secondary-ct,
body.light-theme a.btn-secondary-ct,
body.light-theme button.btn-secondary-ct,
body.light-theme .btn-secondary-ct.btn,
body.light-theme .btn-secondary-ct.btn-primary,
body.light-theme .btn-secondary-ct.btn-secondary {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    color: #0f172a !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
}

body.light-theme .btn-secondary-ct:hover,
body.light-theme a.btn-secondary-ct:hover,
body.light-theme button.btn-secondary-ct:hover,
body.light-theme .btn-secondary-ct.btn-primary:hover,
body.light-theme .btn-secondary-ct.btn-secondary:hover {
    background: #f1f5f9 !important;
    border-color: #0284c7 !important;
    color: #0284c7 !important;
}

/* =============================================================================
   MATHJAX: FORMULAS MATEMÁTICAS EN ALTO CONTRASTE
   ============================================================================= */
body.dark-theme mjx-container {
    color: #f8fafc !important;
}

body.light-theme mjx-container {
    color: #0f172a !important;
}

/* =============================================================================
   SIDEBAR, TARJETAS, DROPDOWNS E INPUTS
   ============================================================================= */
body.light-theme .sidebar-link {
    color: #475569 !important;
}

body.light-theme .sidebar-link:hover {
    background: rgba(2, 132, 199, 0.12) !important;
    color: #0284c7 !important;
}

body.light-theme .home-card {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05) !important;
}

body.light-theme .home-card:hover {
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1) !important;
}

body.light-theme input,
body.light-theme textarea {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border-color: #cbd5e1 !important;
}

body.light-theme .Select-control {
    background-color: #ffffff !important;
    border-color: #cbd5e1 !important;
}

body.light-theme .Select-value-label,
body.light-theme .Select-placeholder {
    color: #0f172a !important;
}

body.light-theme .Select-menu-outer {
    background-color: #ffffff !important;
    border-color: #cbd5e1 !important;
}

body.light-theme .Select-option {
    background-color: #ffffff !important;
    color: #0f172a !important;
}

body.light-theme .Select-option:hover,
body.light-theme .Select-option.is-focused {
    background-color: #f1f5f9 !important;
    color: #0284c7 !important;
}

/* Pestañas */
body.light-theme .tab-bar,
body.light-theme .custom-tab {
    background-color: #e2e8f0 !important;
    color: #475569 !important;
    border-color: #cbd5e1 !important;
}

body.light-theme .custom-tab--selected {
    background-color: #ffffff !important;
    color: #0284c7 !important;
    border-color: #0284c7 !important;
}

/* Modales */
body.light-theme .modal-close-btn {
    background: rgba(15, 23, 42, 0.08) !important;
    color: #0f172a !important;
}

body.light-theme .modal-close-btn:hover {
    background: rgba(220, 38, 38, 0.15) !important;
    color: #dc2626 !important;
}

/* Scrollbars */
body.light-theme ::-webkit-scrollbar-track {
    background: #f1f5f9 !important;
}

body.light-theme ::-webkit-scrollbar-thumb {
    background: #cbd5e1 !important;
}

body.light-theme ::-webkit-scrollbar-thumb:hover {
    background: #94a3b8 !important;
}
"""

FULL_CSS = DARK_CSS + EXTRA_CSS + THEME_CSS
