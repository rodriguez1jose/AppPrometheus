from dash import html
from config import THEME


def layout_recursos():

    # ============================================================
    # RECURSOS PRINCIPALES
    # ============================================================

    tarjeta_libro = html.Div(
        className="info-card",
        children=[
            html.Div(
                html.I(className="fa-solid fa-book-open", style={"color": "#FDE68A"}),
                style={
                    "fontSize": "48px",
                    "marginBottom": "12px",
                },
            ),

            html.Div(
                "LIBRO DE REFERENCIA",
                style={
                    "display": "inline-block",
                    "color": "#FDE68A",
                    "background": "rgba(250,204,21,.10)",
                    "border": "1px solid rgba(250,204,21,.35)",
                    "padding": "6px 12px",
                    "borderRadius": "20px",
                    "fontSize": "12px",
                    "fontWeight": "800",
                    "letterSpacing": "1px",
                    "marginBottom": "15px",
                },
            ),

            html.H3(
                "Medical Imaging Signals and Systems",
                style={
                    "color": "#F8FAFC",
                    "fontSize": "23px",
                    "fontWeight": "800",
                    "margin": "0 0 8px 0",
                    "lineHeight": "1.3",
                },
            ),

            html.P(
                "Jerry L. Prince & Jonathan M. Links",
                style={
                    "color": "#22D3EE",
                    "fontSize": "16px",
                    "fontWeight": "700",
                    "margin": "0 0 5px 0",
                },
            ),

            html.P(
                "2nd Edition · Pearson",
                style={
                    "color": "#94A3B8",
                    "fontSize": "14px",
                    "margin": "0 0 15px 0",
                },
            ),

            html.P(
                "Referencia principal para el estudio de señales y "
                "sistemas en imágenes médicas, con contenidos relacionados "
                "con tomografía computarizada, procesamiento de señales, "
                "transformada de Fourier y formación de imágenes.",
                style={
                    "color": "#CBD5E1",
                    "fontSize": "14px",
                    "lineHeight": "1.7",
                    "margin": "0 0 20px 0",
                },
            ),

            html.A(
                [
                    html.I(className="fa-solid fa-book-open", style={"marginRight": "8px"}),
                    "VER LIBRO",
                ],
                href="/assets/Medical_Imaging_Signals_and_Systems.pdf",
                target="_blank",
                style={
                    "display": "inline-block",
                    "background": "#8B5CF6",
                    "color": "#FFFFFF",
                    "padding": "12px 20px",
                    "borderRadius": "10px",
                    "textDecoration": "none",
                    "fontWeight": "800",
                    "fontSize": "14px",
                },
            ),
        ],

        style={
            "background": "linear-gradient(135deg, #17152B, #111827)",
            "border": "1px solid rgba(250,204,21,.35)",
            "borderRadius": "16px",
            "padding": "25px",
            "boxSizing": "border-box",
            "height": "100%",
        },
    )


    # ============================================================
    # POWERPOINT DE LA ASIGNATURA
    # ============================================================

    tarjeta_presentacion = html.Div(
        className="info-card",
        children=[
            html.Div(
                html.I(className="fa-solid fa-chart-pie", style={"color": "#67E8F9"}),
                style={
                    "fontSize": "48px",
                    "marginBottom": "12px",
                },
            ),

            html.Div(
                "MATERIAL DE LA ASIGNATURA",
                style={
                    "display": "inline-block",
                    "color": "#67E8F9",
                    "background": "rgba(34,211,238,.10)",
                    "border": "1px solid rgba(34,211,238,.35)",
                    "padding": "6px 12px",
                    "borderRadius": "20px",
                    "fontSize": "12px",
                    "fontWeight": "800",
                    "letterSpacing": "1px",
                    "marginBottom": "15px",
                },
            ),

            html.H3(
                "Tomografía Computarizada",
                style={
                    "color": "#F8FAFC",
                    "fontSize": "23px",
                    "fontWeight": "800",
                    "margin": "0 0 8px 0",
                    "lineHeight": "1.3",
                },
            ),

            html.P(
                "Ing. Humberto Calderón, PhD",
                style={
                    "color": "#22D3EE",
                    "fontSize": "16px",
                    "fontWeight": "700",
                    "margin": "0 0 5px 0",
                },
            ),

            html.P(
                "Material de la asignatura",
                style={
                    "color": "#94A3B8",
                    "fontSize": "14px",
                    "margin": "0 0 15px 0",
                },
            ),

            html.P(
                "Presentación de la asignatura con contenidos relacionados "
                "con los fundamentos de la tomografía computarizada, "
                "proyecciones, reconstrucción y procesamiento de imágenes.",
                style={
                    "color": "#CBD5E1",
                    "fontSize": "14px",
                    "lineHeight": "1.7",
                    "margin": "0 0 20px 0",
                },
            ),

            html.A(
                [
                    html.I(className="fa-solid fa-chart-pie", style={"marginRight": "8px"}),
                    "VER PRESENTACIÓN",
                ],
                href="/assets/Tomografia_Computarizada.pptx",
                target="_blank",
                style={
                    "display": "inline-block",
                    "background": "#8B5CF6",
                    "color": "#FFFFFF",
                    "padding": "12px 20px",
                    "borderRadius": "10px",
                    "textDecoration": "none",
                    "fontWeight": "800",
                    "fontSize": "14px",
                },
            ),
        ],

        style={
            "background": "linear-gradient(135deg, #101D2B, #111827)",
            "border": "1px solid rgba(34,211,238,.30)",
            "borderRadius": "16px",
            "padding": "25px",
            "boxSizing": "border-box",
            "height": "100%",
        },
    )


    # ============================================================
    # VIDEOS
    # ============================================================

    videos = [
        {
            "titulo": "Introducción a la TC • Atenuación • Proyecciones",
            "url": "https://www.youtube.com/embed/0OdNI3lSgLc",
            "relacion": "Introducción a la tomografía computarizada",
            "descripcion": (
                "Explica qué es la tomografía computarizada, "
                "cómo se obtienen las imágenes y el papel de la atenuación."
            ),
        },

        {
            "titulo": "Componentes del sistema de TC • Gantry • Detectores",
            "url": "https://www.youtube.com/embed/0GPUk0CvMdw",
            "relacion": "Componentes del sistema de TC",
            "descripcion": (
                "Presenta los principales componentes de un sistema "
                "de tomografía computarizada."
            ),
        },

        {
            "titulo": "Haz de abanico • Geometrías de adquisición • Evolución de la TC",
            "url": "https://www.youtube.com/embed/E9vLclEQRtc",
            "relacion": "Geometrías y adquisición",
            "descripcion": (
                "Explica aspectos relacionados con la adquisición "
                "de datos y la evolución de la tecnología de TC."
            ),
        },

        {
            "titulo": "Proyecciones • Retroproyección • Reconstrucción",
            "url": "https://www.youtube.com/embed/f0sxjhGHRPo",
            "relacion": "Reconstrucción tomográfica",
            "descripcion": (
                "Explica el proceso de tomografía y cómo las proyecciones "
                "permiten obtener una imagen."
            ),
        },

        {
            "titulo": "Transformada de Radon • Fourier • Reconstrucción",
            "url": "https://www.youtube.com/embed/YIvTpW3IevI",
            "relacion": "Transformada de Radon y Fourier",
            "descripcion": (
                "Introduce la relación entre las proyecciones, "
                "la transformada de Radon y el dominio de Fourier."
            ),
        },

        {
            "titulo": "FBP • Filtro Ram-Lak • Retroproyección filtrada",
            "url": "https://www.youtube.com/embed/pZ7JlXagT0w",
            "relacion": "Retroproyección filtrada",
            "descripcion": (
                "Explica el método de Filtered Backprojection (FBP) "
                "utilizado para la reconstrucción de imágenes de TC."
            ),
        },
        {
            "titulo": "X-ray tomography 103: Filtered Back-Projection",
            "url": "https://www.youtube.com/embed/JLFhG3ddgTU",
            "relacion": "Retroproyección filtrada (FBP)",
            "descripcion": (
                "Explica visualmente el método clásico de reconstrucción "
                "por retroproyección filtrada (FBP), mostrando la relación "
                "entre la retroproyección y el filtrado."
            ),
        },

        {
            "titulo": "Computed Tomography: Dual Source CT - Dual Energy",
            "url": "https://www.youtube.com/embed/08udju-MnpM",
            "relacion": "TC de doble fuente y doble energía",
            "descripcion": (
                "Presenta el funcionamiento de la tomografía computarizada "
                "de doble fuente y la adquisición mediante diferentes "
                "niveles de energía."
            ),
        },

        {
            "titulo": "Multidetector Computed Tomography",
            "url": "https://www.youtube.com/embed/1D0quq5a2GY",
            "relacion": "Tomografía computarizada multidetector (MDCT)",
            "descripcion": (
                "Introduce la tomografía computarizada multidetector y "
                "su importancia en la adquisición de múltiples cortes."
            ),
        },

        {
            "titulo": "Slip Ring en tomografía computada",
            "url": "https://www.youtube.com/embed/aIvTcw1ARLg",
            "relacion": "Slip Ring y adquisición continua",
            "descripcion": (
                "Explica el sistema Slip Ring utilizado en los equipos "
                "de tomografía computarizada para permitir la rotación "
                "continua del gantry."
            ),
        },

        {
            "titulo": "Physics: Helical / Spiral Computed Tomography",
            "url": "https://www.youtube.com/embed/7Js5NwRPQ00",
            "relacion": "TC helicoidal o espiral",
            "descripcion": (
                "Explica los fundamentos físicos de la tomografía "
                "helicoidal o espiral y su relación con la adquisición "
                "continua de datos."
            ),
        },

        {
            "titulo": "CT Scan Modes Compared: Axial vs Helical",
            "url": "https://www.youtube.com/embed/O86USkvKpZg",
            "relacion": "Comparación: TC axial vs helicoidal",
            "descripcion": (
                "Compara los modos de adquisición axial y helicoidal "
                "de la tomografía computarizada, destacando sus "
                "principales diferencias."
            ),
        },

        {
            "titulo": "Fifth Generation CT for Radiologic Technologists",
            "url": "https://www.youtube.com/embed/SMhDEgb4Eho",
            "relacion": "Evolución de los equipos de TC",
            "descripcion": (
                "Presenta características de la quinta generación "
                "de tomógrafos y su evolución dentro de la tecnología "
                "de tomografía computarizada."
            ),
        },
    ]


    tarjetas_videos = []

    for video in videos:

        tarjeta = html.Div(
            className="info-card",
            children=[
                html.Div(
                    video["relacion"],
                    style={
                        "color": "#22D3EE",
                        "fontSize": "13px",
                        "fontWeight": "800",
                        "letterSpacing": "0.5px",
                        "marginBottom": "10px",
                    },
                ),

                html.H3(
                    video["titulo"],
                    style={
                        "color": "#F8FAFC",
                        "fontSize": "19px",
                        "fontWeight": "800",
                        "margin": "0 0 15px 0",
                        "lineHeight": "1.35",
                    },
                ),

                html.Iframe(
                    src=video["url"],
                    style={
                        "width": "100%",
                        "height": "300px",
                        "border": "0",
                        "borderRadius": "12px",
                        "display": "block",
                    },
                ),

                html.P(
                    video["descripcion"],
                    style={
                        "color": "#CBD5E1",
                        "fontSize": "14px",
                        "lineHeight": "1.6",
                        "margin": "15px 0 0 0",
                    },
                ),
            ],

            style={
                "borderRadius": "16px",
                "padding": "20px",
                "boxSizing": "border-box",
            },
        )

        tarjetas_videos.append(tarjeta)


    # ============================================================
    # PÁGINA
    # ============================================================

    return html.Div(
        [
            # ----------------------------------------------------
            # ENCABEZADO
            # ----------------------------------------------------

            html.Div(
                [
                    html.Div(
                        "BIBLIOGRAFÍA Y RECURSOS",
                        style={
                            "color": "#22D3EE",
                            "fontSize": "14px",
                            "fontWeight": "800",
                            "letterSpacing": "2px",
                            "marginBottom": "8px",
                        },
                    ),

                    html.H1(
                        "Material de estudio",
                        style={
                            "color": "#F8FAFC",
                            "fontSize": "38px",
                            "fontWeight": "800",
                            "margin": "0 0 12px 0",
                        },
                    ),

                    html.P(
                        "Bibliografía, material de la asignatura y videos "
                        "para complementar el aprendizaje de Tomografía Computarizada.",
                        style={
                            "color": "#94A3B8",
                            "fontSize": "16px",
                            "lineHeight": "1.6",
                            "margin": "0",
                        },
                    ),
                ],

                style={
                    "marginBottom": "30px",
                },
            ),


            # ----------------------------------------------------
            # RECURSOS PRINCIPALES
            # ----------------------------------------------------

            html.H2(
                "Recursos principales",
                style={
                    "color": "#F8FAFC",
                    "fontSize": "24px",
                    "fontWeight": "800",
                    "margin": "0 0 20px 0",
                },
            ),

            html.Div(
                [
                    tarjeta_libro,
                    tarjeta_presentacion,
                ],

                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(2, minmax(0, 1fr))",
                    "gap": "20px",
                    "marginBottom": "40px",
                },
            ),


            # ----------------------------------------------------
            # VIDEOS
            # ----------------------------------------------------

            html.H2(
                "Videos recomendados",
                style={
                    "color": "#F8FAFC",
                    "fontSize": "24px",
                    "fontWeight": "800",
                    "margin": "0 0 20px 0",
                },
            ),

            html.Div(
                tarjetas_videos,

                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(2, minmax(0, 1fr))",
                    "gap": "20px",
                },
            ),
        ],

        style={
            "backgroundColor": THEME["bg"],
            "minHeight": "100vh",
            "padding": "40px 5%",
            "boxSizing": "border-box",
        },
    )