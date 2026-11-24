# app.py
# =============================================================================
# PROMETEO — Plataforma Educativa Interactiva
# Punto de Entrada y Router Maestro (Single Source of Truth)
# =============================================================================
import dash
from dash import dcc, html, Input, Output

# Configuración global y estilos
from config import FULL_CSS, THEME

# Vistas principales desacopladas
from apps.home import home_layout
from apps.imaging.hub import imaging_hub_layout, modalidad_wrapper

# Módulos de aplicación
from apps import app_sys, app_mri, app_ct, app_rx, app_docente
from apps.imaging import casos


# =============================================================================
# INICIALIZACIÓN DE LA APLICACIÓN DASH
# =============================================================================
app = dash.Dash(
    __name__,
    title="Prometeo - Plataforma Educativa",
    suppress_callback_exceptions=True,
)

server = app.server  # Exponer servidor WSGI para producción


# =============================================================================
# PLANTILLA HTML MAESTRA (MathJax 3 + Font Awesome 6 + Fuentes + CSS Global)
# =============================================================================
app.index_string = f"""
<!DOCTYPE html>
<html lang="es">
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}

        <!-- Font Awesome 6.5 -->
        <link
            rel="stylesheet"
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"
            referrerpolicy="no-referrer"
        />

        <!-- Fuentes Google (Inter + Fira Code) -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link
            href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500;600&display=swap"
            rel="stylesheet"
        >

        <!-- Configuración e inicialización de MathJax 3 -->
        <script>
            window.MathJax = {{
                tex: {{
                    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
                    processEscapes: true,
                    processEnvironments: true
                }},
                options: {{
                    skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
                }},
                startup: {{
                    pageReady: function() {{
                        return MathJax.startup.defaultPageReady();
                    }}
                }}
            }};
        </script>
        <script
            id="MathJax-script"
            async
            src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
        </script>

        <!-- CSS Maestro Unificado -->
        <style>{FULL_CSS}</style>
    </head>
    <body style="margin: 0; padding: 0; background-color: #0a0f1d; color: #f8fafc;">
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
"""


# =============================================================================
# CONTENEDOR GLOBAL (ÚNICO dcc.Location + Store de Tema)
# =============================================================================
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="theme-store", data="dark", storage_type="local"),
        html.Div(id="theme-dummy-output", style={"display": "none"}),
        html.Div(id="mathjax-dummy-output", style={"display": "none"}),
        html.Div(id="page-content"),
    ],
    id="main-app-container",
    style={"minHeight": "100vh", "backgroundColor": THEME["bg"]},
)


# =============================================================================
# CLIENTSIDE CALLBACKS: CONMUTACIÓN DE TEMA (CLARO / OSCURO) Y MATHJAX
# =============================================================================
app.clientside_callback(
    """
    function(n_clicks, current_theme) {
        if (!n_clicks) {
            return window.dash_clientside.no_update;
        }
        return (current_theme === 'light') ? 'dark' : 'light';
    }
    """,
    Output("theme-store", "data"),
    Input("theme-toggle-btn", "n_clicks"),
    dash.State("theme-store", "data"),
    prevent_initial_call=True,
)

app.clientside_callback(
    """
    function(theme, pathname) {
        var current = theme || 'dark';
        document.body.classList.remove('dark-theme', 'light-theme');
        document.body.classList.add(current + '-theme');

        setTimeout(function() {
            var icon = document.getElementById('theme-toggle-icon');
            var text = document.getElementById('theme-toggle-text');
            if (icon) {
                icon.className = (current === 'light') ? 'fa-solid fa-moon' : 'fa-solid fa-sun';
            }
            if (text) {
                text.innerText = (current === 'light') ? 'Modo Oscuro' : 'Modo Claro';
            }
        }, 40);
        return window.dash_clientside.no_update;
    }
    """,
    Output("theme-dummy-output", "children"),
    Input("theme-store", "data"),
    Input("url", "pathname"),
)

app.clientside_callback(
    """
    function(children, pathname) {
        function triggerMathJax() {
            if (!window.MathJax) return;
            var el = document.getElementById('page-content') || document.body;
            if (window.MathJax.startup && window.MathJax.startup.promise) {
                window.MathJax.startup.promise = window.MathJax.startup.promise.then(function() {
                    if (window.MathJax.typesetClear) {
                        try { window.MathJax.typesetClear([el]); } catch(e) {}
                    }
                    return window.MathJax.typesetPromise([el]);
                }).catch(function(err) {
                    console.warn('MathJax typeset exception:', err);
                });
            } else if (window.MathJax.typesetPromise) {
                if (window.MathJax.typesetClear) {
                    try { window.MathJax.typesetClear([el]); } catch(e) {}
                }
                window.MathJax.typesetPromise([el]).catch(function(err) {
                    console.warn('MathJax typeset exception:', err);
                });
            }
        }
        // Ejecución escalonada para asegurar que el DOM de React está completamente montado
        setTimeout(triggerMathJax, 50);
        setTimeout(triggerMathJax, 200);
        setTimeout(triggerMathJax, 500);
        setTimeout(triggerMathJax, 1000);
        return window.dash_clientside.no_update;
    }
    """,
    Output("mathjax-dummy-output", "children"),
    Input("page-content", "children"),
    Input("url", "pathname"),
    prevent_initial_call=False,
)


# =============================================================================
# ROUTER PRINCIPAL
# =============================================================================
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def render_page(pathname: str):
    """
    Controlador central de navegación. El navegador y el historial de URLs
    son la única fuente de verdad para la renderización de páginas.
    """
    if not pathname or pathname in ("/", ""):
        return home_layout()

    # 1. Rama: Señales y Sistemas (/sys y subrutas)
    if pathname == "/sys" or pathname.startswith("/sys/"):
        return app_sys.layout(pathname)

    # 2. Hub de Imagenología Médica (/imaging)
    if pathname in ("/imaging", "/imaging/"):
        return imaging_hub_layout()

    # 3. Modalidad: Resonancia Magnética (/imaging/mri)
    if pathname.startswith("/imaging/mri"):
        return modalidad_wrapper(
            app_mri.layout(pathname),
            "Resonancia Magnética (MRI)",
            THEME["accent_purple"],
        )

    # 4. Modalidad: Tomografía Computarizada (/imaging/ct y subrutas)
    if pathname.startswith("/imaging/ct"):
        return app_ct.layout(pathname)

    # 5. Modalidad: Rayos X (/imaging/rx y subrutas)
    if pathname.startswith("/imaging/rx"):
        return app_rx.layout(pathname)

    # 6. Modalidad: Casos Clínicos Interactivos (/imaging/casos)
    if pathname.startswith("/imaging/casos"):
        return modalidad_wrapper(
            casos.casos_layout(),
            "Casos Clínicos Interactivos",
            "#10b981",
        )

    # 7. Panel Docente (/docente)
    if pathname == "/docente" or pathname.startswith("/docente/"):
        return app_docente.layout()

    # Fallback predeterminado: Home
    return home_layout()


# =============================================================================
# REGISTRO DE CALLBACKS MODULARES
# =============================================================================
app_sys.register_callbacks(app)
app_mri.register_callbacks(app)
app_ct.register_callbacks(app)
app_rx.register_callbacks(app)
casos.register_callbacks(app)
app_docente.register_callbacks(app)


# =============================================================================
# ARRANQUE DE LA APLICACIÓN
# =============================================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
