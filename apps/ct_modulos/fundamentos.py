from dash import html, dcc
import dash_bootstrap_components as dbc

NEGRO='#111827'; MORADO='#8B5CF6'; CIAN='#22D3EE'; BLANCO='#F9FAFB'; GRIS='#9CA3AF'


def p(txt):
    return html.P(txt, style={'color':'#D1D5DB','fontSize':'15px','lineHeight':'1.75','marginBottom':'12px'})

def idea(txt):
    return html.Div([html.Strong([html.I(className="fa-solid fa-brain", style={"marginRight": "8px"}), 'Concepto clave'],style={'color':CIAN}),html.P(txt,style={'color':BLANCO,'margin':'7px 0','lineHeight':'1.6'})],className="ct-idea-box",style={'background':'rgba(34,211,238,.08)','border':'1px solid rgba(34,211,238,.25)','borderRadius':'10px','padding':'14px 16px','marginTop':'15px'})
def flujo_tc():
    etapas = [
        ("01", "Rayos X"),
        ("02", "Mediciones"),
        ("03", "Proyecciones"),
        ("04", "Sinograma"),
        ("05", "Reconstrucción"),
        ("06", "Imagen"),
    ]

    return html.Div(
        [

            html.P(
                "Haz clic en cada etapa para explorar cómo se forma una imagen de TC.",
                style={
                    "color": "#AEBBD0",
                    "fontSize": "15px",
                    "marginBottom": "18px",
                }
            ),

            html.Div(
                [
                    html.Div(
                        [
                            html.Button(
                                [
                                    html.Span(
                                        numero,
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                            "justifyContent": "center",
                                            "width": "32px",
                                            "height": "32px",
                                            "borderRadius": "50%",
                                            "background": "#26354A",
                                            "color": "#FFFFFF",
                                            "fontWeight": "800",
                                            "fontSize": "12px",
                                            "margin": "0 auto 8px",
                                        },
                                    ),

                                    html.Span(
                                        nombre,
                                        style={
                                            "display": "block",
                                            "fontSize": "13px",
                                            "fontWeight": "700",
                                            "color": "#E5E7EB",
                                        },
                                    ),
                                ],

                                id=f"tc-step-{i+1}",

                                n_clicks=0,

                                style={
                                    "width": "100%",
                                    "minHeight": "78px",
                                    "background": "#101A2B",
                                    "border": "1px solid #273449",
                                    "borderRadius": "12px",
                                    "padding": "10px 6px",
                                    "cursor": "pointer",
                                },
                            )
                        ],

                        style={
                            "flex": "1",
                            "minWidth": "0",
                        },
                    )

                    for i, (numero, nombre) in enumerate(etapas)
                ],

                style={
                    "display": "flex",
                    "gap": "10px",
                    "alignItems": "center",
                    "width": "100%",
                },
            ),

            html.Div(
                [
                    html.Div(
                        "01",
                        id="tc-current-number",
                        style={
                            "width": "42px",
                            "height": "42px",
                            "borderRadius": "50%",
                            "background": CIAN,
                            "color": "#07111F",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "fontWeight": "800",
                            "fontSize": "14px",
                            "flexShrink": "0",
                        },
                    ),

                    html.Div(
                        [
                            html.H4(
                                "Rayos X",
                                id="tc-step-title",
                                style={
                                    "color": CIAN,
                                    "fontSize": "19px",
                                    "fontWeight": "700",
                                    "margin": "0 0 5px",
                                },
                            ),

                            html.P(
                                "La fuente genera rayos X que atraviesan el objeto.",
                                id="tc-step-text",
                                style={
                                    "color": "#D1D5DB",
                                    "fontSize": "14px",
                                    "lineHeight": "1.5",
                                    "margin": "0",
                                },
                            ),
                        ]
                    ),
                ],

                className="ct-flujo-step-box",
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "14px",
                    "background": "#101D2D",
                    "border": "1px solid #273449",
                    "borderRadius": "12px",
                    "padding": "15px 18px",
                    "marginTop": "14px",
                },
            ),
        ]
    )

def formula(txt):
    return html.Div(txt,className="ct-formula-box",style={'background':'#0B1220','border':'1px solid #334155','borderRadius':'10px','padding':'15px','fontFamily':'monospace','color':'#E5E7EB','overflowX':'auto','margin':'12px 0'})

def card(title,content,accent=MORADO):
    return html.Div([html.Div(style={'width':'4px','borderRadius':'4px','background':accent,'marginRight':'15px'}),html.Div([html.H4(title,style={'color':BLANCO,'fontSize':'19px','fontWeight':'700','marginBottom':'12px'}),content],style={'flex':'1'})],className="ct-fundamento-card",style={'display':'flex','background':'#151D2E','border':'1px solid #273449','borderRadius':'14px','padding':'20px','marginBottom':'16px','boxShadow':'0 5px 18px rgba(0,0,0,.18)'})
def comparison_card(title, subtitle, image, description, color):

    return html.Div(
        [
            html.H3(
                title,
                style={
                    'color': color,
                    'fontSize': '20px',
                    'fontWeight': '700',
                    'marginBottom': '5px'
                }
            ),

            html.P(
                subtitle,
                style={
                    'color': '#B8C4D9',
                    'fontSize': '14px',
                    'marginBottom': '12px'
                }
            ),

            # CONTENEDOR DE LA IMAGEN
            html.Div(
                [
                    html.Img(
                        src=f'/assets/{image}',
                        style={
                            'width': '100%',
                            'height': '100%',
                            'objectFit': 'contain',
                            'objectPosition': 'center',
                            'display': 'block'
                        }
                    )
                ],
                style={
                    'width': '100%',
                    'height': '210px',
                    'background': '#0B1220',
                    'borderRadius': '10px',
                    'overflow': 'hidden',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'marginBottom': '10px'
                }
            ),

            html.Div(
                description,
                style={
                    'background': '#102A40',
                    'color': '#D1D5DB',
                    'padding': '10px 12px',
                    'borderRadius': '9px',
                    'fontSize': '14px',
                    'lineHeight': '1.4'
                }
            )
        ],
        className="ct-comparison-card",
        style={
            'flex': '1',
            'background': '#101A2B',
            'border': '1px solid #273449',
            'borderRadius': '12px',
            'padding': '16px',
            'minWidth': '0',
            'overflow': 'hidden',
            'alignSelf': 'flex-start'
        }
    )

def process_card(number, title, image, description):

    return html.Div(
        [
            html.Div(
                str(number),
                style={
                    'width': '38px',
                    'height': '38px',
                    'borderRadius': '50%',
                    'background': CIAN,
                    'color': '#07111F',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'fontWeight': '800',
                    'fontSize': '17px',
                    'marginBottom': '10px'
                }
            ),

            html.H4(
                title,
                style={
                    'color': BLANCO,
                    'fontSize': '17px',
                    'fontWeight': '700',
                    'marginBottom': '10px'
                }
            ),

            html.Div(
                [
                    html.Img(
                        src=f'/assets/{image}',
                        style={
                            'width': '100%',
                            'height': '100%',
                            'objectFit': 'contain',
                            'objectPosition': 'center',
                            'display': 'block'
                        }
                    )
                ],
                style={
                    'width': '100%',
                    'height': '135px',
                    'background': '#0B1220',
                    'borderRadius': '8px',
                    'overflow': 'hidden',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'marginBottom': '12px'
                }
            ),

            html.P(
                description,
                style={
                    'color': '#B8C4D9',
                    'fontSize': '13px',
                    'lineHeight': '1.45',
                    'margin': '0'
                }
            )
        ],
        className="ct-process-card",
        style={
            'flex': '1',
            'minWidth': '0',
            'background': '#101A2B',
            'border': '1px solid #273449',
            'borderRadius': '12px',
            'padding': '14px',
            'overflow': 'hidden'
        }
    )
def section(num,title,subtitle):
    return html.Div([html.Div(num,style={'minWidth':'42px','height':'42px','borderRadius':'12px','background':MORADO,'color':BLANCO,'display':'flex','alignItems':'center','justifyContent':'center','fontWeight':'700','fontSize':'18px','marginRight':'14px'}),html.Div([html.H2(title,style={'margin':'0','color':BLANCO,'fontSize':'26px','fontWeight':'700'}),html.P(subtitle,style={'margin':'4px 0','color':GRIS,'fontSize':'14px'})])],className="ct-section-header",style={'display':'flex','alignItems':'center','marginBottom':'20px','paddingTop':'10px'})

def step(n,title,desc):
    return html.Div([html.Div(str(n),style={'width':'34px','height':'34px','minWidth':'34px','borderRadius':'50%','background':CIAN,'color':NEGRO,'fontWeight':'800','display':'flex','alignItems':'center','justifyContent':'center'}),html.Div([html.H5(title,style={'color':BLANCO,'margin':'0 0 4px','fontWeight':'700'}),html.P(desc,style={'color':GRIS,'margin':'0','lineHeight':'1.5','fontSize':'14px'})],style={'marginLeft':'13px'})],className="ct-step-item",style={'display':'flex','marginBottom':'16px'})
def block1():
    return [
        section(
            '01',
            '¿Qué es la Tomografía Computarizada?',
            'Fundamento físico y matemático de la formación de imágenes'
        ),

        card(
            'De la radiografía a la TC',

            html.Div(
                [

                    html.P(
                        [
                            'En una ',
                            html.Strong(
                                'radiografía convencional',
                                style={'color': CIAN}
                            ),
                            ', las estructuras anatómicas se proyectan unas '
                            'sobre otras en una imagen bidimensional. '
                            'La tomografía computarizada obtiene información '
                            'de una sección mediante múltiples mediciones '
                            'realizadas desde diferentes direcciones.'
                        ],
                        style={
                            'color':'#E5E7EB',
                            'fontSize':'16px',
                            'lineHeight':'1.6'
                        }
                    ),


                    html.P(
                        'El sistema mide la transmisión de rayos X a través '
                        'del objeto. Estas mediciones se organizan como '
                        'proyecciones y posteriormente se utilizan para '
                        'reconstruir la sección estudiada.',

                        style={
                            'color':'#E5E7EB',
                            'fontSize':'16px',
                            'lineHeight':'1.6'
                        }
                    ),


                    html.Div(
                        [

                            comparison_card(
                                'Radiografía convencional',
                                'Una sola proyección 2D',
                                'radiografia_convencional.png',
                                'Las estructuras anatómicas se superponen en una imagen bidimensional.',
                                CIAN
                            ),


                            comparison_card(
                                'Tomografía Computarizada (TC)',
                                'Múltiples proyecciones y reconstrucción de cortes',
                                'tc_proyecciones.png',
                                'Se adquieren múltiples proyecciones desde diferentes ángulos para reconstruir un corte.',
                                MORADO
                            )

                        ],

                        style={
                            'display':'flex',
                            'gap':'20px',
                            'marginTop':'20px'
                        }
                    )

                ]
            )
        ),

        card(
            'Concepto clave',
            flujo_tc()
        ),
        card(
            'Proceso general',

            html.Div(
                [
                    html.P(
                        'La formación de una imagen de TC sigue una secuencia de pasos, desde la adquisición de datos hasta la reconstrucción de la imagen.',
                        style={
                            'color': '#B8C4D9',
                            'fontSize': '15px',
                            'marginBottom': '18px'
                        }
                    ),

                    html.Div(
                        [
                            process_card(
                                1,
                                'Adquisición',
                                'proceso_adquisicion.png',
                                'La fuente y los detectores realizan mediciones desde distintas posiciones.'
                            ),

                            process_card(
                                2,
                                'Proyecciones',
                                'proceso_proyecciones.png',
                                'Las mediciones representan la atenuación de los rayos X desde diferentes ángulos.'
                            ),

                            process_card(
                                3,
                                'Sinograma',
                                'proceso_sinograma.png',
                                'Las proyecciones se organizan según posición y ángulo.'
                            ),

                            process_card(
                                4,
                                'Filtrado',
                                'proceso_filtrado.png',
                                'En FBP las proyecciones se procesan mediante un filtro.'
                            ),

                            process_card(
                                5,
                                'Reconstrucción',
                                'proceso_reconstruccion.png',
                                'Las contribuciones de muchas direcciones se combinan para formar la sección.'
                            )
                        ],
                        style={
                            'display': 'flex',
                            'gap': '12px',
                            'width': '100%'
                        }
                    )
                ]
            )
        )
    ]

def block2():
    return [
            # ====================================================
            # ENCABEZADO
            # ====================================================
            html.Div(
                [
                    html.Div(
                        "02",
                        style={
                            "width": "54px",
                            "height": "54px",
                            "borderRadius": "14px",
                            "background": MORADO,
                            "color": BLANCO,
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "fontSize": "17px",
                            "fontWeight": "800",
                            "flexShrink": "0",
                        },
                    ),

                    html.Div(
                        [
                            html.H2(
                                "Atenuación y proyecciones",
                                style={
                                    "color": BLANCO,
                                    "fontSize": "28px",
                                    "fontWeight": "800",
                                    "margin": "0",
                                },
                            ),

                            html.P(
                                "La información que recibe el sistema de TC",
                                style={
                                    "color": "#AEBBD0",
                                    "fontSize": "15px",
                                    "margin": "4px 0 0",
                                },
                            ),
                        ]
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "14px",
                    "marginBottom": "22px",
                },
            ),

            # ====================================================
            # TARJETA DE ATENUACIÓN
            # ====================================================

            html.Div(
                [
                    # Título
                    html.Div(
                        [
                            html.Div(
                                style={
                                    "width": "4px",
                                    "height": "32px",
                                    "borderRadius": "4px",
                                    "background": MORADO,
                                    "flexShrink": "0",
                                }
                            ),

                            html.Div(
                                [
                                    html.H3(
                                        "Atenuación de rayos X",
                                        style={
                                            "color": BLANCO,
                                            "fontSize": "21px",
                                            "fontWeight": "750",
                                            "margin": "0 0 6px",
                                        },
                                    ),

                                    html.P(
                                        "¿Qué ocurre cuando el haz atraviesa un objeto?",
                                        style={
                                            "color": "#AEBBD0",
                                            "fontSize": "14px",
                                            "margin": "0",
                                        },
                                    ),
                                ]
                            ),
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "12px",
                            "marginBottom": "20px",
                        },
                    ),

                    # =================================================
                    # EXPLICACIÓN BREVE
                    # =================================================

                    html.P(
                        [
                            "Cuando un haz de rayos X atraviesa un objeto, "
                            "su intensidad disminuye por la interacción de "
                            "los fotones con la materia."
                        ],
                        style={
                            "color": "#D1D5DB",
                            "fontSize": "15px",
                            "lineHeight": "1.6",
                            "margin": "0 0 20px",
                        },
                    ),

                    # =================================================
                    # DIAGRAMA VISUAL
                    # =================================================

                    html.Div(
                        [
                            # Intensidad inicial
                            html.Div(
                                [
                                    html.Div(
                                        "I₀",
                                        style={
                                            "fontSize": "27px",
                                            "fontWeight": "800",
                                            "color": CIAN,
                                            "marginBottom": "4px",
                                        },
                                    ),

                                    html.Div(
                                        "Intensidad inicial",
                                        style={
                                            "fontSize": "11px",
                                            "color": "#94A3B8",
                                        },
                                    ),
                                ],
                                style={
                                    "textAlign": "center",
                                    "minWidth": "95px",
                                },
                            ),

                            # Flecha 1
                            html.Div(
                                "→ → →",
                                style={
                                    "color": CIAN,
                                    "fontSize": "20px",
                                    "fontWeight": "800",
                                    "letterSpacing": "2px",
                                },
                            ),

                            # Objeto
                            html.Div(
                                [
                                    html.Div(
                                        "OBJETO",
                                        style={
                                            "color": BLANCO,
                                            "fontSize": "13px",
                                            "fontWeight": "800",
                                            "marginBottom": "5px",
                                        },
                                    ),

                                    html.Div(
                                        "ATENUACIÓN",
                                        style={
                                            "color": "#A78BFA",
                                            "fontSize": "10px",
                                            "fontWeight": "700",
                                            "letterSpacing": "0.7px",
                                        },
                                    ),
                                ],
                                style={
                                    "minWidth": "150px",
                                    "padding": "16px 20px",
                                    "textAlign": "center",
                                    "background": "#18243A",
                                    "border": "1px solid #3B4A63",
                                    "borderRadius": "12px",
                                    "boxShadow": "inset 0 0 20px rgba(139,92,246,.08)",
                                },
                            ),

                            # Flecha 2
                            html.Div(
                                "→ → →",
                                style={
                                    "color": CIAN,
                                    "fontSize": "20px",
                                    "fontWeight": "800",
                                    "letterSpacing": "2px",
                                },
                            ),

                            # Intensidad final
                            html.Div(
                                [
                                    html.Div(
                                        "I < I₀",
                                        style={
                                            "fontSize": "27px",
                                            "fontWeight": "800",
                                            "color": CIAN,
                                            "marginBottom": "4px",
                                        },
                                    ),

                                    html.Div(
                                        "Intensidad detectada",
                                        style={
                                            "fontSize": "11px",
                                            "color": "#94A3B8",
                                        },
                                    ),
                                ],
                                style={
                                    "textAlign": "center",
                                    "minWidth": "110px",
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "gap": "18px",
                            "background": "#0B1220",
                            "border": "1px solid #273449",
                            "borderRadius": "12px",
                            "padding": "22px 15px",
                            "marginBottom": "20px",
                            "overflow": "hidden",
                        },
                    ),

                    # =================================================
                    # SEGUNDA EXPLICACIÓN
                    # =================================================

                    html.Div(
                        [
                            html.Div(
                                "MEDICIÓN",
                                style={
                                    "color": CIAN,
                                    "fontSize": "11px",
                                    "fontWeight": "800",
                                    "letterSpacing": "1px",
                                    "marginBottom": "6px",
                                },
                            ),

                            html.P(
                                "La medición se relaciona con la atenuación "
                                "a lo largo de la trayectoria. Al repetir "
                                "la medición desde diferentes direcciones "
                                "se obtiene información para reconstruir "
                                "una sección.",
                                style={
                                    "color": "#D1D5DB",
                                    "fontSize": "14px",
                                    "lineHeight": "1.55",
                                    "margin": "0",
                                },
                            ),
                        ],
                        style={
                            "background": "#101D2D",
                            "border": "1px solid #273449",
                            "borderRadius": "10px",
                            "padding": "14px 16px",
                            "marginBottom": "16px",
                        },
                    ),

                    # =================================================
                    # ECUACIÓN
                    # =================================================

                    html.Div(
                        [
                            html.Div(
                                "PROYECCIÓN",
                                style={
                                    "color": "#A78BFA",
                                    "fontSize": "10px",
                                    "fontWeight": "800",
                                    "letterSpacing": "1px",
                                    "marginBottom": "8px",
                                },
                            ),

                            html.Div(
                                "P(θ,s) = ∫ f(x,y) · δ(x cosθ + y sinθ − s) dx dy",
                                style={
                                    "color": BLANCO,
                                    "fontSize": "16px",
                                    "fontFamily": "monospace",
                                    "fontWeight": "600",
                                    "textAlign": "center",
                                    "padding": "12px",
                                    "overflowX": "auto",
                                },
                            ),
                        ],
                        style={
                            "background": "#080F1D",
                            "border": "1px solid #273449",
                            "borderRadius": "10px",
                            "padding": "12px 16px",
                            "marginBottom": "16px",
                        },
                    ),

                    # ==============================================
                    # CONCEPTO CLAVE
                    # =================================================

                    html.Div(
                        [
                            html.Div(
                                html.I(className="fa-solid fa-lightbulb", style={"color": "#facc15"}),
                                style={
                                    "fontSize": "21px",
                                    "marginRight": "10px",
                                },
                            ),

                            html.Div(
                                [
                                    html.Div(
                                        "CONCEPTO CLAVE",
                                        style={
                                            "color": CIAN,
                                            "fontSize": "11px",
                                            "fontWeight": "800",
                                            "letterSpacing": "0.8px",
                                            "marginBottom": "4px",
                                        },
                                    ),

                                    html.Div(
                                        "Una proyección no es una imagen completa: "
                                        "es información del objeto observada desde "
                                        "una determinada dirección.",
                                        style={
                                            "color": "#E5E7EB",
                                            "fontSize": "13px",
                                            "lineHeight": "1.5",
                                        },
                                    ),
                                ]
                            ),
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "background": "rgba(34, 211, 238, 0.07)",
                            "border": "1px solid rgba(34, 211, 238, 0.25)",
                            "borderRadius": "10px",
                            "padding": "13px 15px",
                        },
                    ),
                ],
                className="ct-fundamento-card",
                style={
                    "background": "#101A2B",
                    "border": "1px solid #273449",
                    "borderRadius": "14px",
                    "padding": "24px",
                    "marginBottom": "20px",
                },
            ),
        ]

def block3():

    return [

        # =====================================================
        # ENCABEZADO
        # =====================================================

        html.Div(
            [
                html.Div(
                    "03",
                    style={
                        "width": "54px",
                        "height": "54px",
                        "borderRadius": "14px",
                        "background": MORADO,
                        "color": BLANCO,
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "fontSize": "17px",
                        "fontWeight": "800",
                        "flexShrink": "0",
                    },
                ),

                html.Div(
                    [
                        html.H2(
                            "Transformada de Radon",
                            style={
                                "color": BLANCO,
                                "fontSize": "28px",
                                "fontWeight": "800",
                                "margin": "0",
                            },
                        ),

                        html.P(
                            "La relación matemática entre el objeto y sus proyecciones",
                            style={
                                "color": "#AEBBD0",
                                "fontSize": "15px",
                                "margin": "4px 0 0",
                            },
                        ),
                    ]
                ),
            ],
            style={
                "display": "flex",
                "alignItems": "center",
                "gap": "14px",
                "marginBottom": "22px",
            },
        ),

        # =====================================================
        # TARJETA PRINCIPAL
        # =====================================================

        html.Div(
            [

                # -------------------------------------------------
                # TÍTULO
                # -------------------------------------------------

                html.Div(
                    [
                        html.Div(
                            style={
                                "width": "4px",
                                "height": "32px",
                                "borderRadius": "4px",
                                "background": MORADO,
                                "flexShrink": "0",
                            }
                        ),

                        html.Div(
                            [
                                html.H3(
                                    "¿Qué hace la transformada de Radon?",
                                    style={
                                        "color": BLANCO,
                                        "fontSize": "21px",
                                        "fontWeight": "750",
                                        "margin": "0 0 6px",
                                    },
                                ),

                                html.P(
                                    "De un objeto 2D a un conjunto de proyecciones 1D",
                                    style={
                                        "color": "#AEBBD0",
                                        "fontSize": "14px",
                                        "margin": "0",
                                    },
                                ),
                            ]
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "12px",
                        "marginBottom": "18px",
                    },
                ),

                # -------------------------------------------------
                # EXPLICACIÓN
                # -------------------------------------------------

                html.P(
                    "La transformada de Radon describe integrales de línea "
                    "de una función. En tomografía permite representar "
                    "matemáticamente las mediciones obtenidas a lo largo "
                    "de diferentes trayectorias.",
                    style={
                        "color": "#D1D5DB",
                        "fontSize": "15px",
                        "lineHeight": "1.6",
                        "margin": "0 0 10px",
                    },
                ),

                html.P(
                    "Para cada ángulo θ se obtiene una proyección. "
                    "Al cambiar el ángulo se generan nuevas proyecciones "
                    "y el conjunto contiene la información necesaria "
                    "para la reconstrucción.",
                    style={
                        "color": "#D1D5DB",
                        "fontSize": "15px",
                        "lineHeight": "1.6",
                        "margin": "0 0 20px",
                    },
                ),

                # =================================================
                # DIAGRAMA VISUAL PRINCIPAL
                # =================================================

                html.Div(
                    [

                        # OBJETO 2D
                        html.Div(
                            [
                                html.Div(
                                    "OBJETO 2D",
                                    style={
                                        "color": CIAN,
                                        "fontSize": "11px",
                                        "fontWeight": "800",
                                        "letterSpacing": "1px",
                                        "marginBottom": "12px",
                                    },
                                ),

                                html.Div(
                                    [
                                        html.Div(
                                            "● ●",
                                            style={
                                                "color": "#A78BFA",
                                                "fontSize": "18px",
                                                "lineHeight": "0.8",
                                            },
                                        ),
                                        html.Div(
                                            "● ● ●",
                                            style={
                                                "color": "#C4B5FD",
                                                "fontSize": "18px",
                                                "lineHeight": "0.8",
                                            },
                                        ),
                                        html.Div(
                                            "● ●",
                                            style={
                                                "color": "#A78BFA",
                                                "fontSize": "18px",
                                                "lineHeight": "0.8",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "gap": "4px",
                                        "width": "120px",
                                        "height": "120px",
                                        "background": "#18243A",
                                        "border": "1px solid #3B4A63",
                                        "borderRadius": "14px",
                                        "boxShadow": "inset 0 0 25px rgba(139,92,246,.10)",
                                    },
                                ),
                            ],
                            style={
                                "flex": "1",
                                "display": "flex",
                                "flexDirection": "column",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "minWidth": "0",
                            },
                        ),

                        # FLECHA
                        html.Div(
                            "→",
                            style={
                                "color": CIAN,
                                "fontSize": "30px",
                                "fontWeight": "800",
                            },
                        ),

                        # RADON
                        html.Div(
                            [
                                html.Div(
                                    "TRANSFORMADA",
                                    className="ct-radon-tag",
                                    style={
                                        "color": "#A78BFA",
                                        "fontSize": "10px",
                                        "fontWeight": "800",
                                        "letterSpacing": "1px",
                                        "marginBottom": "8px",
                                    },
                                ),

                                html.Div(
                                    "RADON",
                                    className="ct-radon-title",
                                    style={
                                        "color": "#ffffff",
                                        "fontSize": "20px",
                                        "fontWeight": "800",
                                        "marginBottom": "6px",
                                    },
                                ),

                                html.Div(
                                    "R{f}(θ,s)",
                                    className="ct-radon-formula",
                                    style={
                                        "color": CIAN,
                                        "fontSize": "16px",
                                        "fontFamily": "monospace",
                                        "fontWeight": "700",
                                    },
                                ),
                            ],
                            className="ct-radon-box",
                            style={
                                "flex": "1",
                                "minWidth": "150px",
                                "padding": "22px 15px",
                                "textAlign": "center",
                                "background": "#151F31",
                                "border": "1px solid #3B4A63",
                                "borderRadius": "14px",
                            },
                        ),

                        # FLECHA
                        html.Div(
                            "→",
                            style={
                                "color": CIAN,
                                "fontSize": "30px",
                                "fontWeight": "800",
                            },
                        ),

                        # PROYECCIONES
                        html.Div(
                            [
                                html.Div(
                                    "PROYECCIONES 1D",
                                    style={
                                        "color": CIAN,
                                        "fontSize": "11px",
                                        "fontWeight": "800",
                                        "letterSpacing": "1px",
                                        "marginBottom": "12px",
                                    },
                                ),

                                html.Div(
                                    [
                                        html.Div(
                                            "θ₁  ─────────",
                                            style={
                                                "color": "#E5E7EB",
                                                "fontSize": "12px",
                                                "fontFamily": "monospace",
                                            },
                                        ),

                                        html.Div(
                                            "θ₂  ─────────",
                                            style={
                                                "color": "#A78BFA",
                                                "fontSize": "12px",
                                                "fontFamily": "monospace",
                                            },
                                        ),

                                        html.Div(
                                            "θ₃  ─────────",
                                            style={
                                                "color": "#E5E7EB",
                                                "fontSize": "12px",
                                                "fontFamily": "monospace",
                                            },
                                        ),

                                        html.Div(
                                            "⋮",
                                            style={
                                                "color": CIAN,
                                                "fontSize": "17px",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "gap": "6px",
                                    },
                                ),
                            ],
                            style={
                                "flex": "1",
                                "minWidth": "0",
                                "padding": "15px",
                                "background": "#101A2B",
                                "border": "1px solid #273449",
                                "borderRadius": "14px",
                                "textAlign": "center",
                            },
                        ),

                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "gap": "15px",
                        "background": "#0B1220",
                        "border": "1px solid #273449",
                        "borderRadius": "14px",
                        "padding": "22px",
                        "marginBottom": "20px",
                        "overflow": "hidden",
                    },
                ),

                # =================================================
                # ÁNGULOS
                # =================================================

                html.Div(
                    [
                        html.Div(
                            "CAMBIO DE ÁNGULO",
                            style={
                                "color": CIAN,
                                "fontSize": "10px",
                                "fontWeight": "800",
                                "letterSpacing": "1px",
                                "marginBottom": "10px",
                            },
                        ),

                        html.Div(
                            [
                                html.Div(
                                    "θ₁",
                                    style={
                                        "width": "48px",
                                        "height": "48px",
                                        "borderRadius": "50%",
                                        "background": "#18243A",
                                        "border": "1px solid #3B4A63",
                                        "color": BLANCO,
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "fontWeight": "800",
                                    },
                                ),

                                html.Div(
                                    "→",
                                    style={
                                        "color": CIAN,
                                        "fontSize": "20px",
                                    },
                                ),

                                html.Div(
                                    "θ₂",
                                    style={
                                        "width": "48px",
                                        "height": "48px",
                                        "borderRadius": "50%",
                                        "background": "#8B5CF6",
                                        "color": BLANCO,
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "fontWeight": "800",
                                        "boxShadow": "0 5px 15px rgba(139,92,246,.25)",
                                    },
                                ),

                                html.Div(
                                    "→",
                                    style={
                                        "color": CIAN,
                                        "fontSize": "20px",
                                    },
                                ),

                                html.Div(
                                    "θ₃",
                                    style={
                                        "width": "48px",
                                        "height": "48px",
                                        "borderRadius": "50%",
                                        "background": "#18243A",
                                        "border": "1px solid #3B4A63",
                                        "color": BLANCO,
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "fontWeight": "800",
                                    },
                                ),

                                html.Div(
                                    "→",
                                    style={
                                        "color": CIAN,
                                        "fontSize": "20px",
                                    },
                                ),

                                html.Div(
                                    "θₙ",
                                    style={
                                        "width": "48px",
                                        "height": "48px",
                                        "borderRadius": "50%",
                                        "background": "#18243A",
                                        "border": "1px solid #3B4A63",
                                        "color": BLANCO,
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "fontWeight": "800",
                                    },
                                ),
                            ],
                            style={
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "gap": "12px",
                            },
                        ),

                        html.P(
                            "Cada ángulo aporta una nueva proyección del objeto.",
                            style={
                                "color": "#94A3B8",
                                "fontSize": "12px",
                                "textAlign": "center",
                                "margin": "10px 0 0",
                            },
                        ),
                    ],
                    style={
                        "background": "#101D2D",
                        "border": "1px solid #273449",
                        "borderRadius": "12px",
                        "padding": "15px",
                        "marginBottom": "18px",
                        "textAlign": "center",
                    },
                ),

                # =================================================
                # ECUACIÓN
                # =================================================

                html.Div(
                    [
                        html.Div(
                            "DEFINICIÓN MATEMÁTICA",
                            style={
                                "color": "#A78BFA",
                                "fontSize": "10px",
                                "fontWeight": "800",
                                "letterSpacing": "1px",
                                "marginBottom": "8px",
                            },
                        ),

                        html.Div(
                            "R{f}(θ,s) = ∫∫ f(x,y) δ(x cosθ + y sinθ − s) dx dy",
                            style={
                                "color": BLANCO,
                                "fontSize": "16px",
                                "fontFamily": "monospace",
                                "fontWeight": "600",
                                "textAlign": "center",
                                "padding": "10px",
                                "overflowX": "auto",
                            },
                        ),
                    ],
                    style={
                        "background": "#080F1D",
                        "border": "1px solid #273449",
                        "borderRadius": "10px",
                        "padding": "12px 16px",
                        "marginBottom": "16px",
                    },
                ),

                # =================================================
                # CONCEPTO CLAVE
                # =================================================

                html.Div(
                    [
                        html.Div(
                            html.I(className="fa-solid fa-lightbulb", style={"color": "#facc15"}),
                            style={
                                "fontSize": "21px",
                                "marginRight": "10px",
                            },
                        ),

                        html.Div(
                            [
                                html.Div(
                                    "CONCEPTO CLAVE",
                                    style={
                                        "color": CIAN,
                                        "fontSize": "11px",
                                        "fontWeight": "800",
                                        "letterSpacing": "0.8px",
                                        "marginBottom": "4px",
                                    },
                                ),

                                html.Div(
                                    "Radon transforma una imagen 2D en un conjunto "
                                    "de proyecciones 1D tomadas desde diferentes ángulos.",
                                    style={
                                        "color": "#E5E7EB",
                                        "fontSize": "13px",
                                        "lineHeight": "1.5",
                                    },
                                ),
                            ]
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "background": "rgba(34, 211, 238, 0.07)",
                        "border": "1px solid rgba(34, 211, 238, 0.25)",
                        "borderRadius": "10px",
                        "padding": "13px 15px",
                    },
                ),

            ],
            className="ct-fundamento-card",
            style={
                "background": "#101A2B",
                "border": "1px solid #273449",
                "borderRadius": "14px",
                "padding": "24px",
                "marginBottom": "20px",
            },
        ),
    ]

def block4():

    return [

        # =====================================================
        # ENCABEZADO
        # =====================================================

        section(
            '04',
            'Sinograma',
            'Representación visual de las proyecciones'
        ),

        # =====================================================
        # ¿QUÉ ES UN SINOGRAMA?
        # =====================================================

        card(
            '¿Qué es un sinograma?',

            html.Div(
                [

                    p(
                        'El sinograma es una representación gráfica de las '
                        'proyecciones obtenidas durante la adquisición '
                        'tomográfica. La información se organiza según la '
                        'posición del detector y el ángulo.'
                    ),

                    p(
                        'El conjunto de proyecciones contiene los datos '
                        'necesarios para realizar posteriormente la '
                        'reconstrucción.'
                    ),

                    # =================================================
                    # SECUENCIA VISUAL DEL SINOGRAMA
                    # =================================================

                    html.Div(
                        [

                            # =============================================
                            # 01. ADQUISICIÓN
                            # =============================================

                            html.Div(
                                [
                                    html.Div(
                                        "01 · ADQUISICIÓN",
                                        style={
                                            "color": CIAN,
                                            "fontSize": "12px",
                                            "fontWeight": "800",
                                            "letterSpacing": "1px",
                                            "marginBottom": "10px",
                                        },
                                    ),

                                    html.Img(
                                        src="/assets/adquisicion_diagrama.png",
                                        style={
                                            "width": "100%",
                                            "height": "220px",
                                            "objectFit": "contain",
                                            "display": "block",
                                        },
                                    ),

                                    html.P(
                                        "El sistema obtiene mediciones del objeto "
                                        "desde diferentes ángulos.",
                                        style={
                                            "color": "#AEBBD0",
                                            "fontSize": "13px",
                                            "lineHeight": "1.5",
                                            "margin": "8px 0 0",
                                        },
                                    ),
                                ],
                                style={
                                    "flex": "1",
                                    "minWidth": "0",
                                    "background": "#0B1220",
                                    "border": "1px solid #273449",
                                    "borderRadius": "12px",
                                    "padding": "14px",
                                },
                            ),

                            # FLECHA
                            html.Div(
                                "→",
                                style={
                                    "color": CIAN,
                                    "fontSize": "32px",
                                    "fontWeight": "800",
                                    "alignSelf": "center",
                                },
                            ),

                            # =============================================
                            # 02. PROYECCIONES
                            # =============================================

                            html.Div(
                                [
                                    html.Div(
                                        "02 · PROYECCIONES",
                                        style={
                                            "color": MORADO,
                                            "fontSize": "12px",
                                            "fontWeight": "800",
                                            "letterSpacing": "1px",
                                            "marginBottom": "10px",
                                        },
                                    ),

                                    html.Img(
                                        src="/assets/proyecciones_vistas.png",
                                        style={
                                            "width": "100%",
                                            "height": "220px",
                                            "objectFit": "contain",
                                            "display": "block",
                                        },
                                    ),

                                    html.P(
                                        "Cada ángulo produce una nueva proyección "
                                        "del objeto.",
                                        style={
                                            "color": "#AEBBD0",
                                            "fontSize": "13px",
                                            "lineHeight": "1.5",
                                            "margin": "8px 0 0",
                                        },
                                    ),
                                ],
                                style={
                                    "flex": "1",
                                    "minWidth": "0",
                                    "background": "#0B1220",
                                    "border": "1px solid #273449",
                                    "borderRadius": "12px",
                                    "padding": "14px",
                                },
                            ),

                            # FLECHA
                            html.Div(
                                "→",
                                style={
                                    "color": CIAN,
                                    "fontSize": "32px",
                                    "fontWeight": "800",
                                    "alignSelf": "center",
                                },
                            ),

                            # =============================================
                            # 03. SINOGRAMA
                            # =============================================

                            html.Div(
                                [
                                    html.Div(
                                        "03 · SINOGRAMA",
                                        style={
                                            "color": CIAN,
                                            "fontSize": "12px",
                                            "fontWeight": "800",
                                            "letterSpacing": "1px",
                                            "marginBottom": "10px",
                                        },
                                    ),

                                    html.Img(
                                        src="/assets/sinograma.png",
                                        style={
                                            "width": "100%",
                                            "height": "220px",
                                            "objectFit": "contain",
                                            "display": "block",
                                        },
                                    ),

                                    html.P(
                                        "Las proyecciones organizadas según el ángulo "
                                        "y la posición del detector forman el sinograma.",
                                        style={
                                            "color": "#AEBBD0",
                                            "fontSize": "13px",
                                            "lineHeight": "1.5",
                                            "margin": "8px 0 0",
                                        },
                                    ),
                                ],
                                style={
                                    "flex": "1",
                                    "minWidth": "0",
                                    "background": "#0B1220",
                                    "border": "1px solid #273449",
                                    "borderRadius": "12px",
                                    "padding": "14px",
                                },
                            ),

                        ],
                        className="ct-fundamento-card",
                        style={
                            "display": "flex",
                            "alignItems": "stretch",
                            "gap": "12px",
                            "width": "100%",
                            "background": "#080F1D",
                            "border": "1px solid #273449",
                            "borderRadius": "14px",
                            "padding": "16px",
                            "marginTop": "18px",
                            "marginBottom": "18px",
                            "boxSizing": "border-box",
                        },
                    ),
                    # =================================================
                    # ¿CÓMO SE LEEN LAS ESTRUCTURAS?
                    # =================================================

                    html.Div(
                        [

                            html.Div(
                                "¿CÓMO SE LEEN LAS ESTRUCTURAS DEL SINOGRAMA?",
                                style={
                                    "color": CIAN,
                                    "fontSize": "12px",
                                    "fontWeight": "800",
                                    "letterSpacing": "1px",
                                    "marginBottom": "10px",
                                },
                            ),

                            html.P(
                                "Las diferentes estructuras del objeto producen patrones característicos en el sinograma.",
                                style={
                                    "color": "#D1D5DB",
                                    "fontSize": "14px",
                                    "marginBottom": "18px",
                                },
                            ),


                            html.Div(
                                [

                                    # =====================
                                    # PUNTO
                                    # =====================

                                    html.Div(
                                        [
                                            html.Div(
                                                "PUNTO",
                                                style={
                                                    "color": MORADO,
                                                    "fontSize": "14px",
                                                    "fontWeight": "800",
                                                    "textAlign": "center",
                                                    "marginBottom": "12px",
                                                },
                                            ),

                                            html.Img(
                                                src="/assets/punto_sinograma.png",
                                                style={
                                                    "width": "100%",
                                                    "height": "170px",
                                                    "objectFit": "contain",
                                                    "objectPosition": "center",
                                                    "display": "block",
                                                },
                                            ),

                                            html.Div(
                                                "Trayectoria sinusoidal",
                                                style={
                                                    "color": CIAN,
                                                    "fontWeight": "800",
                                                    "fontSize": "14px",
                                                    "textAlign": "center",
                                                    "marginTop": "12px",
                                                },
                                            ),

                                            html.P(
                                                "Un punto genera una curva sinusoidal cuando cambia el ángulo de adquisición.",
                                                style={
                                                    "color": "#AEBBD0",
                                                    "fontSize": "12px",
                                                    "lineHeight": "1.5",
                                                    "textAlign": "center",
                                                },
                                            ),

                                        ],

                                        style={
                                            "background": "#0B1220",
                                            "border": "1px solid #273449",
                                            "borderRadius": "12px",
                                            "padding": "18px",
                                        },
                                    ),



                                    # =====================
                                    # LÍNEA
                                    # =====================

                                    html.Div(
                                        [
                                            html.Div(
                                                "LÍNEA",
                                                style={
                                                    "color": CIAN,
                                                    "fontSize": "14px",
                                                    "fontWeight": "800",
                                                    "textAlign": "center",
                                                    "marginBottom": "12px",
                                                },
                                            ),

                                            html.Img(
                                                src="/assets/linea_sinograma.png",
                                                style={
                                                    "width": "100%",
                                                    "height": "170px",
                                                    "objectFit": "contain",
                                                    "objectPosition": "center",
                                                    "display": "block",
                                                },
                                            ),

                                            html.Div(
                                                "Banda característica",
                                                style={
                                                    "color": CIAN,
                                                    "fontWeight": "800",
                                                    "fontSize": "14px",
                                                    "textAlign": "center",
                                                    "marginTop": "12px",
                                                },
                                            ),

                                            html.P(
                                                "Una estructura lineal produce una banda aproximadamente horizontal.",
                                                style={
                                                    "color": "#AEBBD0",
                                                    "fontSize": "12px",
                                                    "lineHeight": "1.5",
                                                    "textAlign": "center",
                                                },
                                            ),

                                        ],

                                        style={
                                            "background": "#0B1220",
                                            "border": "1px solid #273449",
                                            "borderRadius": "12px",
                                            "padding": "18px",
                                        },
                                    ),



                                    # =====================
                                    # CÍRCULO
                                    # =====================

                                    html.Div(
                                        [
                                            html.Div(
                                                "CÍRCULO",
                                                style={
                                                    "color": MORADO,
                                                    "fontSize": "14px",
                                                    "fontWeight": "800",
                                                    "textAlign": "center",
                                                    "marginBottom": "12px",
                                                },
                                            ),

                                            html.Img(
                                                src="/assets/circulo_sinograma.png",
                                                style={
                                                    "width": "100%",
                                                    "height": "170px",
                                                    "objectFit": "contain",
                                                    "objectPosition": "center",
                                                    "display": "block",
                                                },
                                            ),

                                            html.Div(
                                                "Familia de curvas",
                                                style={
                                                    "color": CIAN,
                                                    "fontWeight": "800",
                                                    "fontSize": "14px",
                                                    "textAlign": "center",
                                                    "marginTop": "12px",
                                                },
                                            ),

                                            html.P(
                                                "Un círculo genera múltiples trayectorias sinusoidales.",
                                                style={
                                                    "color": "#AEBBD0",
                                                    "fontSize": "12px",
                                                    "lineHeight": "1.5",
                                                    "textAlign": "center",
                                                },
                                            ),

                                        ],

                                        style={
                                            "background": "#0B1220",
                                            "border": "1px solid #273449",
                                            "borderRadius": "12px",
                                            "padding": "18px",
                                        },
                                    ),

                                ],

                                style={
                                    "display": "grid",
                                    "gridTemplateColumns": "repeat(3, 1fr)",
                                    "gap": "18px",
                                    "width": "100%",
                                },
                            ),

                        ],
                        className="ct-fundamento-card",
                        style={
                            "background": "#101A2B",
                            "border": "1px solid #273449",
                            "borderRadius": "14px",
                            "padding": "18px",
                            "marginBottom": "20px",
                        },
                    ),
                    # =================================================
                    # CONCEPTO CLAVE
                    # =================================================

                    html.Div(
                        [
                            html.Div(
                                html.I(className="fa-solid fa-lightbulb", style={"color": "#facc15"}),
                                style={
                                    'fontSize': '21px',
                                    'marginRight': '10px'
                                }
                            ),

                            html.Div(
                                [
                                    html.Div(
                                        'CONCEPTO CLAVE',
                                        style={
                                            'color': CIAN,
                                            'fontSize': '11px',
                                            'fontWeight': '800',
                                            'letterSpacing': '0.8px',
                                            'marginBottom': '4px'
                                        }
                                    ),

                                    html.Div(
                                        'El sinograma no es la imagen anatómica '
                                        'reconstruida; es una representación de '
                                        'los datos de proyección.',
                                        className="ct-callout-text",
                                        style={
                                            'color': '#E5E7EB',
                                            'fontSize': '13px',
                                            'lineHeight': '1.5'
                                        }
                                    )
                                ]
                            )
                        ],
                        className="ct-info-callout",
                        style={
                            'display': 'flex',
                            'alignItems': 'center',
                            'background': 'rgba(34, 211, 238, 0.07)',
                            'border': '1px solid rgba(34, 211, 238, 0.25)',
                            'borderRadius': '10px',
                            'padding': '13px 15px'
                        }
                    )

                ]
            )
        ),

               # =====================================================
        # DEL OBJETO AL SINOGRAMA
        # =====================================================

        card(
            'Del objeto al sinograma',

            html.Div(
                [

                    html.P(
                        'El sinograma aparece cuando las mediciones obtenidas '
                        'durante la adquisición se organizan de acuerdo con '
                        'el ángulo y la posición del detector.',
                        style={
                            'color': '#D1D5DB',
                            'fontSize': '15px',
                            'lineHeight': '1.6',
                            'margin': '0 0 20px'
                        }
                    ),

                    # -------------------------------------------------
                    # TRES ETAPAS VISUALES
                    # -------------------------------------------------

                    html.Div(
                        [

                            # ==============================
                            # 01 ADQUISICIÓN
                            # ==============================

                            html.Div(
                                [

                                    html.Div(
                                        '01 · ADQUISICIÓN',
                                        style={
                                            'color': CIAN,
                                            'fontSize': '11px',
                                            'fontWeight': '800',
                                            'letterSpacing': '0.8px',
                                            'marginBottom': '10px'
                                        }
                                    ),

                                    html.Div(
                                        [
                                            html.Img(
                                                src='/assets/proceso_adquisicion.png',
                                                style={
                                                    'width': '100%',
                                                    'height': '170px',
                                                    'objectFit': 'contain',
                                                    'display': 'block'
                                                }
                                            )
                                        ],
                                        style={
                                            'height': '190px',
                                            'background': '#0B1220',
                                            'borderRadius': '10px',
                                            'display': 'flex',
                                            'alignItems': 'center',
                                            'justifyContent': 'center',
                                            'overflow': 'hidden'
                                        }
                                    ),

                                    html.P(
                                        'Se obtienen mediciones del objeto '
                                        'desde diferentes posiciones.',
                                        style={
                                            'color': '#AEBBD0',
                                            'fontSize': '12px',
                                            'lineHeight': '1.5',
                                            'margin': '10px 0 0'
                                        }
                                    )

                                ],
                                style={
                                    'flex': '1',
                                    'minWidth': '0',
                                    'background': '#101A2B',
                                    'border': '1px solid #273449',
                                    'borderRadius': '12px',
                                    'padding': '14px'
                                }
                            ),

                            # ==============================
                            # FLECHA
                            # ==============================

                            html.Div(
                                '→',
                                style={
                                    'color': CIAN,
                                    'fontSize': '30px',
                                    'fontWeight': '800',
                                    'alignSelf': 'center'
                                }
                            ),

                            # ==============================
                            # 02 PROYECCIONES
                            # ==============================

                            html.Div(
                                [

                                    html.Div(
                                        '02 · PROYECCIONES',
                                        style={
                                            'color': MORADO,
                                            'fontSize': '11px',
                                            'fontWeight': '800',
                                            'letterSpacing': '0.8px',
                                            'marginBottom': '10px'
                                        }
                                    ),

                                    html.Div(
                                        [
                                            html.Img(
                                                src='/assets/proceso_proyecciones.png',
                                                style={
                                                    'width': '100%',
                                                    'height': '170px',
                                                    'objectFit': 'contain',
                                                    'display': 'block'
                                                }
                                            )
                                        ],
                                        style={
                                            'height': '190px',
                                            'background': '#0B1220',
                                            'borderRadius': '10px',
                                            'display': 'flex',
                                            'alignItems': 'center',
                                            'justifyContent': 'center',
                                            'overflow': 'hidden'
                                        }
                                    ),

                                    html.P(
                                        'Cada ángulo produce una nueva '
                                        'proyección del objeto.',
                                        style={
                                            'color': '#AEBBD0',
                                            'fontSize': '12px',
                                            'lineHeight': '1.5',
                                            'margin': '10px 0 0'
                                        }
                                    )

                                ],
                                style={
                                    'flex': '1',
                                    'minWidth': '0',
                                    'background': '#101A2B',
                                    'border': '1px solid #273449',
                                    'borderRadius': '12px',
                                    'padding': '14px'
                                }
                            ),

                            # ==============================
                            # FLECHA
                            # ==============================

                            html.Div(
                                '→',
                                style={
                                    'color': CIAN,
                                    'fontSize': '30px',
                                    'fontWeight': '800',
                                    'alignSelf': 'center'
                                }
                            ),

                            # ==============================
                            # 03 SINOGRAMA
                            # ==============================

                            html.Div(
                                [

                                    html.Div(
                                        '03 · SINOGRAMA',
                                        style={
                                            'color': CIAN,
                                            'fontSize': '11px',
                                            'fontWeight': '800',
                                            'letterSpacing': '0.8px',
                                            'marginBottom': '10px'
                                        }
                                    ),

                                    html.Div(
                                        [
                                            html.Img(
                                                src='/assets/proceso_sinograma.png',
                                                style={
                                                    'width': '100%',
                                                    'height': '170px',
                                                    'objectFit': 'contain',
                                                    'display': 'block'
                                                }
                                            )
                                        ],
                                        style={
                                            'height': '190px',
                                            'background': '#0B1220',
                                            'borderRadius': '10px',
                                            'display': 'flex',
                                            'alignItems': 'center',
                                            'justifyContent': 'center',
                                            'overflow': 'hidden'
                                        }
                                    ),

                                    html.P(
                                        'Las proyecciones organizadas forman '
                                        'el patrón del sinograma.',
                                        style={
                                            'color': '#AEBBD0',
                                            'fontSize': '12px',
                                            'lineHeight': '1.5',
                                            'margin': '10px 0 0'
                                        }
                                    )

                                ],
                                style={
                                    'flex': '1',
                                    'minWidth': '0',
                                    'background': '#101A2B',
                                    'border': '1px solid #273449',
                                    'borderRadius': '12px',
                                    'padding': '14px'
                                }
                            )

                        ],
                        style={
                            'display': 'flex',
                            'alignItems': 'stretch',
                            'gap': '12px',
                            'width': '100%'
                        }
                    ),

                    # -------------------------------------------------
                    # MENSAJE INFERIOR
                    # -------------------------------------------------

                    html.Div(
                        [
                            html.Div(
                                '03',
                                style={
                                    'width': '38px',
                                    'height': '38px',
                                    'borderRadius': '50%',
                                    'background': MORADO,
                                    'color': BLANCO,
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'justifyContent': 'center',
                                    'fontWeight': '800',
                                    'fontSize': '12px',
                                    'flexShrink': '0'
                                }
                            ),

                            html.Div(
                                [
                                    html.Div(
                                        'RESULTADO',
                                        style={
                                            'color': CIAN,
                                            'fontSize': '10px',
                                            'fontWeight': '800',
                                            'letterSpacing': '1px',
                                            'marginBottom': '3px'
                                        }
                                    ),

                                    html.Div(
                                        'El sinograma reúne la información '
                                        'de todas las proyecciones y sirve '
                                        'como entrada para la reconstrucción.',
                                        style={
                                            'color': '#E5E7EB',
                                            'fontSize': '13px',
                                            'lineHeight': '1.5'
                                        }
                                    )
                                ]
                            )
                        ],
                        style={
                            'display': 'flex',
                            'alignItems': 'center',
                            'gap': '12px',
                            'background': 'rgba(139, 92, 246, 0.08)',
                            'border': '1px solid rgba(139, 92, 246, 0.25)',
                            'borderRadius': '10px',
                            'padding': '13px 15px',
                            'marginTop': '18px'
                        }
                    )

                ]
            )
        ),

    ]

    
def block5():

    return [

        section(
            '05',
            'Retroproyección',
            'Cómo se distribuyen las proyecciones sobre la imagen'
        ),

        # =====================================================
        # 01. RETROPROYECCIÓN SIMPLE
        # =====================================================

        html.Div(
            [
                # ENCABEZADO
                html.Div(
                    [
                        html.Div(
                            "01",
                            style={
                                "width": "42px",
                                "height": "42px",
                                "borderRadius": "50%",
                                "background": MORADO,
                                "color": BLANCO,
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "fontWeight": "800",
                                "fontSize": "15px",
                                "flexShrink": "0",
                            },
                        ),

                        html.Div(
                            [
                                html.H3(
                                    "Retroproyección simple",
                                    style={
                                        "color": BLANCO,
                                        "fontSize": "21px",
                                        "fontWeight": "800",
                                        "margin": "0 0 4px",
                                    },
                                ),

                                html.P(
                                    "Distribuir cada medición nuevamente "
                                    "sobre la trayectoria de donde provino.",
                                    style={
                                        "color": "#94A3B8",
                                        "fontSize": "13px",
                                        "margin": "0",
                                    },
                                ),
                            ]
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "12px",
                        "marginBottom": "16px",
                    },
                ),

                # EXPLICACIÓN
                html.P(
                    "Una sola proyección no permite reconstruir completamente "
                    "el objeto. Cada valor de la proyección se distribuye "
                    "nuevamente sobre la línea correspondiente.",
                    style={
                        "color": "#D1D5DB",
                        "fontSize": "14px",
                        "lineHeight": "1.55",
                        "margin": "0 0 16px",
                    },
                ),

                # =================================================
                # TRES ETAPAS VISUALES
                # =================================================

                html.Div(
                    [

                        # -------------------------
                        # PROYECCIÓN
                        # -------------------------

                        html.Div(
                            [
                                html.Div(
                                    "PROYECCIÓN",
                                    style={
                                        "color": CIAN,
                                        "fontSize": "12px",
                                        "fontWeight": "800",
                                        "letterSpacing": "0.8px",
                                        "textAlign": "center",
                                        "marginBottom": "8px",
                                    },
                                ),

                                html.Img(
                                    src="/assets/rp_proyeccion.png",
                                    style={
                                        "width": "100%",
                                        "height": "190px",
                                        "objectFit": "contain",
                                        "objectPosition": "center",
                                        "display": "block",
                                    },
                                ),

                                html.P(
                                    "Una medición desde un determinado ángulo.",
                                    style={
                                        "color": "#94A3B8",
                                        "fontSize": "12px",
                                        "lineHeight": "1.4",
                                        "textAlign": "center",
                                        "margin": "6px 0 0",
                                    },
                                ),
                            ],
                            style={
                                "flex": "1",
                                "minWidth": "0",
                                "background": "#0B1220",
                                "border": "1px solid #273449",
                                "borderRadius": "12px",
                                "padding": "12px",
                            },
                        ),

                        # FLECHA
                        html.Div(
                            "→",
                            style={
                                "color": CIAN,
                                "fontSize": "30px",
                                "fontWeight": "800",
                                "alignSelf": "center",
                                "flexShrink": "0",
                            },
                        ),

                        # -------------------------
                        # RETROPROYECCIÓN
                        # -------------------------

                        html.Div(
                            [
                                html.Div(
                                    "RETROPROYECCIÓN",
                                    style={
                                        "color": MORADO,
                                        "fontSize": "12px",
                                        "fontWeight": "800",
                                        "letterSpacing": "0.8px",
                                        "textAlign": "center",
                                        "marginBottom": "8px",
                                    },
                                ),

                                html.Img(
                                    src="/assets/rp_retroproyeccion.png",
                                    style={
                                        "width": "100%",
                                        "height": "190px",
                                        "objectFit": "contain",
                                        "objectPosition": "center",
                                        "display": "block",
                                    },
                                ),

                                html.P(
                                    "La medición se distribuye sobre su línea.",
                                    style={
                                        "color": "#94A3B8",
                                        "fontSize": "12px",
                                        "lineHeight": "1.4",
                                        "textAlign": "center",
                                        "margin": "6px 0 0",
                                    },
                                ),
                            ],
                            style={
                                "flex": "1",
                                "minWidth": "0",
                                "background": "#0B1220",
                                "border": "1px solid #273449",
                                "borderRadius": "12px",
                                "padding": "12px",
                            },
                        ),

                        # FLECHA
                        html.Div(
                            "→",
                            style={
                                "color": CIAN,
                                "fontSize": "30px",
                                "fontWeight": "800",
                                "alignSelf": "center",
                                "flexShrink": "0",
                            },
                        ),

                        # -------------------------
                        # MUCHAS PROYECCIONES
                        # -------------------------

                        html.Div(
                            [
                                html.Div(
                                    "MUCHAS PROYECCIONES",
                                    style={
                                        "color": CIAN,
                                        "fontSize": "12px",
                                        "fontWeight": "800",
                                        "letterSpacing": "0.8px",
                                        "textAlign": "center",
                                        "marginBottom": "8px",
                                    },
                                ),

                                html.Img(
                                    src="/assets/rp_muchas_proyecciones.png",
                                    style={
                                        "width": "100%",
                                        "height": "190px",
                                        "objectFit": "contain",
                                        "objectPosition": "center",
                                        "display": "block",
                                    },
                                ),

                                html.P(
                                    "La suma de direcciones genera una estimación.",
                                    style={
                                        "color": "#94A3B8",
                                        "fontSize": "12px",
                                        "lineHeight": "1.4",
                                        "textAlign": "center",
                                        "margin": "6px 0 0",
                                    },
                                ),
                            ],
                            style={
                                "flex": "1",
                                "minWidth": "0",
                                "background": "#0B1220",
                                "border": "1px solid #273449",
                                "borderRadius": "12px",
                                "padding": "12px",
                            },
                        ),

                    ],
                    style={
                        "display": "flex",
                        "alignItems": "stretch",
                        "gap": "10px",
                        "width": "100%",
                    },
                ),

                # =================================================
                # ECUACIÓN
                # =================================================

                html.Div(
                    [
                        html.Div(
                            "RETROPROYECCIÓN SIMPLE",
                            style={
                                "color": CIAN,
                                "fontSize": "11px",
                                "fontWeight": "800",
                                "letterSpacing": "1px",
                                "marginBottom": "8px",
                                "textAlign": "center",
                            },
                        ),

                        html.Div(
                            "f̂(x,y) ≈ Δθ Σ q(x cosθₖ + y sinθₖ, θₖ)",
                            style={
                                "color": BLANCO,
                                "fontSize": "20px",
                                "fontWeight": "700",
                                "fontFamily": "monospace",
                                "textAlign": "center",
                                "lineHeight": "1.5",
                            },
                        ),
                    ],

                    style={
                        "background": "#080F1D",
                        "border": "1px solid rgba(34,211,238,.30)",
                        "borderRadius": "10px",
                        "padding": "16px 20px",
                        "marginTop": "14px",
                        "width": "100%",
                        "boxSizing": "border-box",
                    },
                ),

                # CONCEPTO CLAVE
                html.Div(
                    [
                        html.Span(
                            html.I(className="fa-solid fa-lightbulb", style={"color": "#facc15"}),
                            style={
                                "fontSize": "20px",
                                "marginRight": "10px",
                            },
                        ),

                        html.Span(
                            "Retroproyectar significa llevar cada medición "
                            "nuevamente hacia las líneas del objeto que la originaron.",
                            style={
                                "color": "#E5E7EB",
                                "fontSize": "13px",
                                "lineHeight": "1.5",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "background": "rgba(139,92,246,.08)",
                        "border": "1px solid rgba(139,92,246,.35)",
                        "borderRadius": "10px",
                        "padding": "12px 15px",
                        "marginTop": "12px",
                    },
                ),

            ],
            className="ct-fundamento-card",
            style={
                "background": "#101A2B",
                "border": "1px solid #273449",
                "borderRadius": "14px",
                "padding": "20px",
                "marginBottom": "18px",
                "boxSizing": "border-box",
            },
        ),


        # =====================================================
        # 02. ¿POR QUÉ APARECE EL DESENFOQUE?
        # =====================================================

        html.Div(
            [
                # ENCABEZADO
                html.Div(
                    [
                        html.Div(
                            "02",
                            style={
                                "width": "42px",
                                "height": "42px",
                                "borderRadius": "50%",
                                "background": CIAN,
                                "color": "#07111F",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "fontWeight": "800",
                                "fontSize": "15px",
                                "flexShrink": "0",
                            },
                        ),

                        html.Div(
                            [
                                html.H3(
                                    "¿Por qué aparece el desenfoque?",
                                    style={
                                        "color": BLANCO,
                                        "fontSize": "21px",
                                        "fontWeight": "800",
                                        "margin": "0 0 4px",
                                    },
                                ),

                                html.P(
                                    "La limitación de la retroproyección simple.",
                                    style={
                                        "color": "#94A3B8",
                                        "fontSize": "13px",
                                        "margin": "0",
                                    },
                                ),
                            ]
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "12px",
                        "marginBottom": "14px",
                    },
                ),

                html.P(
                    "Cada proyección distribuye información sobre una línea. "
                    "Cuando se superponen muchas proyecciones, la información "
                    "se extiende alrededor de las estructuras originales.",
                    style={
                        "color": "#D1D5DB",
                        "fontSize": "14px",
                        "lineHeight": "1.55",
                        "margin": "0 0 16px",
                    },
                ),

                # DOS IMÁGENES INDIVIDUALES
                html.Div(
                    [

                        html.Div(
                            [
                                html.Div(
                                    "UNA PROYECCIÓN",
                                    style={
                                        "color": MORADO,
                                        "fontSize": "12px",
                                        "fontWeight": "800",
                                        "letterSpacing": "0.8px",
                                        "textAlign": "center",
                                        "marginBottom": "8px",
                                    },
                                ),

                                html.Img(
                                    src="/assets/rp_una_proyeccion.png",
                                    style={
                                        "width": "100%",
                                        "height": "290px",
                                        "objectFit": "contain",
                                        "objectPosition": "center",
                                        "display": "block",
                                    },
                                ),

                                html.P(
                                    
                                    style={
                                        "color": "#AEBBD0",
                                        "fontSize": "12px",
                                        "lineHeight": "1.45",
                                        "textAlign": "center",
                                        "margin": "6px 0 0",
                                    },
                                ),
                            ],
                            style={
                                "flex": "1",
                                "minWidth": "0",
                                "background": "#0B1220",
                                "border": "1px solid #273449",
                                "borderRadius": "12px",
                                "padding": "14px",
                            },
                        ),

                        html.Div(
                            [
                                html.Div(
                                    "MUCHAS PROYECCIONES",
                                    style={
                                        "color": CIAN,
                                        "fontSize": "12px",
                                        "fontWeight": "800",
                                        "letterSpacing": "0.8px",
                                        "textAlign": "center",
                                        "marginBottom": "8px",
                                    },
                                ),

                                html.Img(
                                    src="/assets/rp_muchas_lineas_halo.png",
                                    style={
                                        "width": "100%",
                                        "height": "295px",
                                        "objectFit": "contain",
                                        "objectPosition": "center",
                                        "display": "block",
                                    },
                                ),

                                html.P(
                                    style={
                                        "color": "#AEBBD0",
                                        "fontSize": "12px",
                                        "lineHeight": "1.45",
                                        "textAlign": "center",
                                        "margin": "4px 0 0",
                                    },
                                ),
                            ],
                            style={
                                "flex": "1",
                                "minWidth": "0",
                                "background": "#0B1220",
                                "border": "1px solid #273449",
                                "borderRadius": "12px",
                                "padding": "10px",
                            },
                        ),

                    ],
                    style={
                        "display": "flex",
                        "gap": "14px",
                        "width": "100%",
                    },
                ),

                # SOLUCIÓN
                html.Div(
                    [
                        html.Span(
                            "→",
                            style={
                                "color": CIAN,
                                "fontSize": "24px",
                                "fontWeight": "800",
                                "marginRight": "10px",
                            },
                        ),

                        html.Div(
                            [
                                html.Div(
                                    "SOLUCIÓN: FILTRADO + RETROPROYECCIÓN",
                                    style={
                                        "color": CIAN,
                                        "fontSize": "12px",
                                        "fontWeight": "800",
                                        "letterSpacing": "0.8px",
                                    },
                                ),

                                html.Div(
                                    "La retroproyección filtrada (FBP) aplica "
                                    "un filtro antes de distribuir las proyecciones.",
                                    style={
                                        "color": "#E5E7EB",
                                        "fontSize": "13px",
                                        "marginTop": "4px",
                                    },
                                ),
                            ]
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "background": "rgba(34,211,238,.07)",
                        "border": "1px solid rgba(34,211,238,.25)",
                        "borderRadius": "10px",
                        "padding": "12px 15px",
                        "marginTop": "14px",
                    },
                ),

            ],
            className="ct-fundamento-card",
            style={
                "background": "#101A2B",
                "border": "1px solid #273449",
                "borderRadius": "14px",
                "padding": "20px",
                "marginBottom": "20px",
                "boxSizing": "border-box",
            },
        ),
    ]
    
def block6():

    return [

        section(
            '06',
            'Retroproyección filtrada (FBP)',
            'Filtered Back Projection'
        ),

        # =====================================================
        # 01. ¿QUÉ ES FBP?
        # =====================================================

        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            "01",
                            style={
                                "width": "42px",
                                "height": "42px",
                                "borderRadius": "50%",
                                "background": MORADO,
                                "color": BLANCO,
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "fontWeight": "800",
                                "fontSize": "15px",
                                "flexShrink": "0",
                            },
                        ),

                        html.Div(
                            [
                                html.H3(
                                    "¿Qué es FBP?",
                                    style={
                                        "color": BLANCO,
                                        "fontSize": "21px",
                                        "fontWeight": "800",
                                        "margin": "0 0 4px",
                                    },
                                ),

                                html.P(
                                    "Filtered Back Projection",
                                    style={
                                        "color": "#94A3B8",
                                        "fontSize": "13px",
                                        "margin": "0",
                                    },
                                ),
                            ]
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "12px",
                        "marginBottom": "15px",
                    },
                ),

                html.P(
                    "La retroproyección filtrada combina dos operaciones: "
                    "primero se filtran las proyecciones y después se "
                    "retroproyectan sobre la imagen.",
                    style={
                        "color": "#D1D5DB",
                        "fontSize": "14px",
                        "lineHeight": "1.55",
                        "margin": "0 0 8px",
                    },
                ),

                html.P(
                    "El filtrado busca compensar el desenfoque introducido "
                    "por la retroproyección simple.",
                    style={
                        "color": "#AEBBD0",
                        "fontSize": "13px",
                        "lineHeight": "1.5",
                        "margin": "0",
                    },
                ),

                # CONCEPTO CLAVE
                html.Div(
                    [
                        html.Span(
                            html.I(className="fa-solid fa-lightbulb", style={"color": "#facc15"}),
                            style={
                                "fontSize": "20px",
                                "marginRight": "10px",
                            },
                        ),

                        html.Div(
                            [
                                html.Div(
                                    "CONCEPTO CLAVE",
                                    style={
                                        "color": CIAN,
                                        "fontSize": "11px",
                                        "fontWeight": "800",
                                        "letterSpacing": "0.8px",
                                        "marginBottom": "4px",
                                    },
                                ),

                                html.Div(
                                    "FBP = Filtrar las proyecciones + "
                                    "Retroproyectarlas + Acumularlas.",
                                    style={
                                        "color": "#E5E7EB",
                                        "fontSize": "14px",
                                    },
                                ),
                            ]
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "background": "rgba(34,211,238,.07)",
                        "border": "1px solid rgba(34,211,238,.25)",
                        "borderRadius": "10px",
                        "padding": "12px 15px",
                        "marginTop": "14px",
                    },
                ),
            ],
            className="ct-fundamento-card",
            style={
                "background": "#101A2B",
                "border": "1px solid #273449",
                "borderRadius": "14px",
                "padding": "20px",
                "marginBottom": "18px",
                "boxSizing": "border-box",
            },
        ),

        # =====================================================
        # 02. ETAPAS DE FBP
        # =====================================================

        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            "02",
                            style={
                                "width": "42px",
                                "height": "42px",
                                "borderRadius": "50%",
                                "background": CIAN,
                                "color": "#07111F",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "fontWeight": "800",
                                "fontSize": "15px",
                                "flexShrink": "0",
                            },
                        ),

                        html.Div(
                            [
                                html.H3(
                                    "Etapas de FBP",
                                    style={
                                        "color": BLANCO,
                                        "fontSize": "21px",
                                        "fontWeight": "800",
                                        "margin": "0",
                                    },
                                ),

                                html.P(
                                    "Del conjunto de proyecciones a la imagen reconstruida",
                                    style={
                                        "color": "#94A3B8",
                                        "fontSize": "13px",
                                        "margin": "3px 0 0",
                                    },
                                ),
                            ]
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "12px",
                        "marginBottom": "16px",
                    },
                ),

                # =================================================
                # FLUJO PRINCIPAL
                # =================================================

                html.Div(
                    [
                        # FILTRADO
                        html.Div(
                            [
                                html.Div(
                                    "01",
                                    style={
                                        "width": "30px",
                                        "height": "30px",
                                        "borderRadius": "50%",
                                        "background": MORADO,
                                        "color": BLANCO,
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "fontWeight": "800",
                                        "fontSize": "12px",
                                        "margin": "0 auto 7px",
                                    },
                                ),

                                html.Div(
                                    "FILTRADO",
                                    style={
                                        "color": MORADO,
                                        "fontSize": "12px",
                                        "fontWeight": "800",
                                        "textAlign": "center",
                                        "letterSpacing": "0.7px",
                                        "marginBottom": "7px",
                                    },
                                ),

                                html.Img(
                                    src="/assets/fbp_filtrado.png",
                                    style={
                                        "width": "100%",
                                        "height": "180px",
                                        "objectFit": "contain",
                                        "objectPosition": "center",
                                        "display": "block",
                                    },
                                ),

                                html.P(
                                    "Se aplica un filtro a cada proyección "
                                    "para compensar el desenfoque.",
                                    style={
                                        "color": "#AEBBD0",
                                        "fontSize": "12px",
                                        "lineHeight": "1.4",
                                        "textAlign": "center",
                                        "margin": "5px 0 0",
                                    },
                                ),
                            ],
                            style={
                                "flex": "1",
                                "minWidth": "0",
                                "background": "#0B1220",
                                "border": "1px solid #273449",
                                "borderRadius": "12px",
                                "padding": "12px",
                                "boxSizing": "border-box",
                            },
                        ),

                        # FLECHA
                        html.Div(
                            "→",
                            style={
                                "color": CIAN,
                                "fontSize": "28px",
                                "fontWeight": "800",
                                "alignSelf": "center",
                                "flexShrink": "0",
                            },
                        ),

                        # RETROPROYECCIÓN
                        html.Div(
                            [
                                html.Div(
                                    "02",
                                    style={
                                        "width": "30px",
                                        "height": "30px",
                                        "borderRadius": "50%",
                                        "background": CIAN,
                                        "color": "#07111F",
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "fontWeight": "800",
                                        "fontSize": "12px",
                                        "margin": "0 auto 7px",
                                    },
                                ),

                                html.Div(
                                    "RETROPROYECCIÓN",
                                    style={
                                        "color": CIAN,
                                        "fontSize": "12px",
                                        "fontWeight": "800",
                                        "textAlign": "center",
                                        "letterSpacing": "0.7px",
                                        "marginBottom": "7px",
                                    },
                                ),

                                html.Img(
                                    src="/assets/fbp_retroproyeccion.png",
                                    style={
                                        "width": "100%",
                                        "height": "180px",
                                        "objectFit": "contain",
                                        "objectPosition": "center",
                                        "display": "block",
                                    },
                                ),

                                html.P(
                                    "La proyección filtrada se distribuye "
                                    "sobre sus líneas originales.",
                                    style={
                                        "color": "#AEBBD0",
                                        "fontSize": "12px",
                                        "lineHeight": "1.4",
                                        "textAlign": "center",
                                        "margin": "5px 0 0",
                                    },
                                ),
                            ],
                            style={
                                "flex": "1",
                                "minWidth": "0",
                                "background": "#0B1220",
                                "border": "1px solid #273449",
                                "borderRadius": "12px",
                                "padding": "12px",
                                "boxSizing": "border-box",
                            },
                        ),

                        # FLECHA
                        html.Div(
                            "→",
                            style={
                                "color": CIAN,
                                "fontSize": "28px",
                                "fontWeight": "800",
                                "alignSelf": "center",
                                "flexShrink": "0",
                            },
                        ),

                        # IMAGEN RECONSTRUIDA
                        html.Div(
                            [
                                html.Div(
                                    "03",
                                    style={
                                        "width": "30px",
                                        "height": "30px",
                                        "borderRadius": "50%",
                                        "background": MORADO,
                                        "color": BLANCO,
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "fontWeight": "800",
                                        "fontSize": "12px",
                                        "margin": "0 auto 7px",
                                    },
                                ),

                                html.Div(
                                    "RECONSTRUCCIÓN",
                                    style={
                                        "color": MORADO,
                                        "fontSize": "12px",
                                        "fontWeight": "800",
                                        "textAlign": "center",
                                        "letterSpacing": "0.7px",
                                        "marginBottom": "7px",
                                    },
                                ),

                                html.Img(
                                    src="/assets/fbp_reconstruccion.png",
                                    style={
                                        "width": "100%",
                                        "height": "180px",
                                        "objectFit": "contain",
                                        "objectPosition": "center",
                                        "display": "block",
                                    },
                                ),

                                html.P(
                                    "Las contribuciones se acumulan para "
                                    "obtener la sección reconstruida.",
                                    style={
                                        "color": "#AEBBD0",
                                        "fontSize": "12px",
                                        "lineHeight": "1.4",
                                        "textAlign": "center",
                                        "margin": "5px 0 0",
                                    },
                                ),
                            ],
                            style={
                                "flex": "1",
                                "minWidth": "0",
                                "background": "#0B1220",
                                "border": "1px solid #273449",
                                "borderRadius": "12px",
                                "padding": "12px",
                                "boxSizing": "border-box",
                            },
                        ),

                    ],
                    style={
                        "display": "flex",
                        "alignItems": "stretch",
                        "gap": "9px",
                        "width": "100%",
                    },
                ),

                # =================================================
                # RESUMEN DEL PROCESO
                # =================================================

                html.Div(
                    [
                        html.Div(
                            "PROYECCIONES",
                            style={
                                "color": CIAN,
                                "fontSize": "11px",
                                "fontWeight": "800",
                            },
                        ),

                        html.Div(
                            "→",
                            style={
                                "color": "#64748B",
                                "fontSize": "18px",
                            },
                        ),

                        html.Div(
                            "FILTRADO",
                            style={
                                "color": MORADO,
                                "fontSize": "11px",
                                "fontWeight": "800",
                            },
                        ),

                        html.Div(
                            "→",
                            style={
                                "color": "#64748B",
                                "fontSize": "18px",
                            },
                        ),

                        html.Div(
                            "RETROPROYECCIÓN",
                            style={
                                "color": CIAN,
                                "fontSize": "11px",
                                "fontWeight": "800",
                            },
                        ),

                        html.Div(
                            "→",
                            style={
                                "color": "#64748B",
                                "fontSize": "18px",
                            },
                        ),

                        html.Div(
                            "IMAGEN RECONSTRUIDA",
                            style={
                                "color": MORADO,
                                "fontSize": "11px",
                                "fontWeight": "800",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "gap": "10px",
                        "background": "#080F1D",
                        "border": "1px solid #273449",
                        "borderRadius": "10px",
                        "padding": "10px",
                        "marginTop": "14px",
                    },
                ),

            ],
            className="ct-fundamento-card",
            style={
                "background": "#101A2B",
                "border": "1px solid #273449",
                "borderRadius": "14px",
                "padding": "20px",
                "marginBottom": "18px",
                "boxSizing": "border-box",
            },
        ),

        # =====================================================
        # 03. EJEMPLO NUMÉRICO DEL MATERIAL
        # =====================================================

        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            "03",
                            style={
                                "width": "42px",
                                "height": "42px",
                                "borderRadius": "50%",
                                "background": MORADO,
                                "color": BLANCO,
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "fontWeight": "800",
                                "fontSize": "15px",
                                "flexShrink": "0",
                            },
                        ),

                        html.Div(
                            [
                                html.H3(
                                    "Ejemplo computacional",
                                    style={
                                        "color": BLANCO,
                                        "fontSize": "21px",
                                        "fontWeight": "800",
                                        "margin": "0 0 3px",
                                    },
                                ),

                                html.P(
                                    "Configuración utilizada en el proyecto",
                                    style={
                                        "color": "#94A3B8",
                                        "fontSize": "13px",
                                        "margin": "0",
                                    },
                                ),
                            ]
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "12px",
                        "marginBottom": "14px",
                    },
                ),

                # DATOS
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    "FANTOMA",
                                    style={
                                        "color": CIAN,
                                        "fontSize": "10px",
                                        "fontWeight": "800",
                                    },
                                ),
                                html.Div(
                                    "Shepp–Logan",
                                    style={
                                        "color": BLANCO,
                                        "fontSize": "15px",
                                        "fontWeight": "700",
                                        "marginTop": "3px",
                                    },
                                ),
                            ],
                            style={
                                "background": "#0B1220",
                                "border": "1px solid #273449",
                                "borderRadius": "10px",
                                "padding": "11px",
                            },
                        ),

                        html.Div(
                            [
                                html.Div(
                                    "TAMAÑO",
                                    style={
                                        "color": CIAN,
                                        "fontSize": "10px",
                                        "fontWeight": "800",
                                    },
                                ),
                                html.Div(
                                    "160 × 160 px",
                                    style={
                                        "color": BLANCO,
                                        "fontSize": "15px",
                                        "fontWeight": "700",
                                        "marginTop": "3px",
                                    },
                                ),
                            ],
                            style={
                                "background": "#0B1220",
                                "border": "1px solid #273449",
                                "borderRadius": "10px",
                                "padding": "11px",
                            },
                        ),

                        html.Div(
                            [
                                html.Div(
                                    "VISTAS",
                                    style={
                                        "color": CIAN,
                                        "fontSize": "10px",
                                        "fontWeight": "800",
                                    },
                                ),
                                html.Div(
                                    "180",
                                    style={
                                        "color": BLANCO,
                                        "fontSize": "15px",
                                        "fontWeight": "700",
                                        "marginTop": "3px",
                                    },
                                ),
                            ],
                            style={
                                "background": "#0B1220",
                                "border": "1px solid #273449",
                                "borderRadius": "10px",
                                "padding": "11px",
                            },
                        ),

                        html.Div(
                            [
                                html.Div(
                                    "GEOMETRÍA",
                                    style={
                                        "color": CIAN,
                                        "fontSize": "10px",
                                        "fontWeight": "800",
                                    },
                                ),
                                html.Div(
                                    "Paralela",
                                    style={
                                        "color": BLANCO,
                                        "fontSize": "15px",
                                        "fontWeight": "700",
                                        "marginTop": "3px",
                                    },
                                ),
                            ],
                            style={
                                "background": "#0B1220",
                                "border": "1px solid #273449",
                                "borderRadius": "10px",
                                "padding": "11px",
                            },
                        ),
                    ],
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(4, 1fr)",
                        "gap": "10px",
                    },
                ),

                html.Div(
                    "La demostración utiliza radon e iradon de scikit-image "
                    "con interpolación lineal. También puede incorporarse "
                    "ruido gaussiano al sinograma.",
                    style={
                        "color": "#AEBBD0",
                        "fontSize": "13px",
                        "lineHeight": "1.5",
                        "marginTop": "12px",
                    },
                ),

                html.Div(
                    [
                        html.Span(
                            "ℹ",
                            style={
                                "width": "24px",
                                "height": "24px",
                                "borderRadius": "50%",
                                "background": CIAN,
                                "color": "#07111F",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "fontWeight": "800",
                                "marginRight": "10px",
                                "flexShrink": "0",
                            },
                        ),

                        html.Span(
                            "Es una demostración computacional del proceso "
                            "de reconstrucción; no representa un protocolo "
                            "clínico de dosis.",
                            style={
                                "color": "#D1D5DB",
                                "fontSize": "12px",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "background": "rgba(34,211,238,.06)",
                        "border": "1px solid rgba(34,211,238,.20)",
                        "borderRadius": "10px",
                        "padding": "10px 12px",
                        "marginTop": "12px",
                    },
                ),

            ],
            className="ct-fundamento-card",
            style={
                "background": "#101A2B",
                "border": "1px solid #273449",
                "borderRadius": "14px",
                "padding": "20px",
                "marginBottom": "20px",
                "boxSizing": "border-box",
            },
        ),
    ]

def block7():

    return [

        section(
            '07',
            'Filtros de reconstrucción',
            'Control de las frecuencias espaciales durante FBP'
        ),

        # =====================================================
        # INTRODUCCIÓN
        # =====================================================

        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            "01",
                            style={
                                "width": "42px",
                                "height": "42px",
                                "borderRadius": "50%",
                                "background": MORADO,
                                "color": BLANCO,
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "fontWeight": "800",
                                "fontSize": "15px",
                                "flexShrink": "0",
                            },
                        ),

                        html.Div(
                            [
                                html.H3(
                                    "¿Por qué necesitamos filtros?",
                                    style={
                                        "color": BLANCO,
                                        "fontSize": "21px",
                                        "fontWeight": "800",
                                        "margin": "0 0 4px",
                                    },
                                ),

                                html.P(
                                    "Controlar el equilibrio entre detalle y ruido",
                                    style={
                                        "color": "#94A3B8",
                                        "fontSize": "13px",
                                        "margin": "0",
                                    },
                                ),
                            ]
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "12px",
                        "marginBottom": "14px",
                    },
                ),

                html.P(
                    "Durante la reconstrucción FBP, el filtro modifica las "
                    "frecuencias espaciales de las proyecciones antes de "
                    "realizar la retroproyección.",
                    style={
                        "color": "#D1D5DB",
                        "fontSize": "14px",
                        "lineHeight": "1.55",
                        "margin": "0",
                    },
                ),

                html.Div(
                    [
                        html.Span(
                            html.I(className="fa-solid fa-lightbulb", style={"color": "#facc15"}),
                            style={
                                "fontSize": "20px",
                                "marginRight": "10px",
                            },
                        ),

                        html.Span(
                            "Cambiar el filtro modifica el compromiso entre "
                            "resolución, suavizado y sensibilidad al ruido.",
                            style={
                                "color": "#E5E7EB",
                                "fontSize": "13px",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "background": "rgba(34,211,238,.07)",
                        "border": "1px solid rgba(34,211,238,.25)",
                        "borderRadius": "10px",
                        "padding": "12px 15px",
                        "marginTop": "14px",
                    },
                ),
            ],
            className="ct-fundamento-card",
            style={
                "background": "#101A2B",
                "border": "1px solid #273449",
                "borderRadius": "14px",
                "padding": "20px",
                "marginBottom": "18px",
                "boxSizing": "border-box",
            },
        ),

        # =====================================================
        # COMPARACIÓN DE FILTROS
        # =====================================================

        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            "02",
                            style={
                                "width": "42px",
                                "height": "42px",
                                "borderRadius": "50%",
                                "background": CIAN,
                                "color": "#07111F",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "fontWeight": "800",
                                "fontSize": "15px",
                                "flexShrink": "0",
                            },
                        ),

                        html.Div(
                            [
                                html.H3(
                                    "Comparación de filtros",
                                    style={
                                        "color": BLANCO,
                                        "fontSize": "21px",
                                        "fontWeight": "800",
                                        "margin": "0 0 3px",
                                    },
                                ),

                                html.P(
                                    "Cada filtro modifica de manera diferente "
                                    "las frecuencias espaciales.",
                                    style={
                                        "color": "#94A3B8",
                                        "fontSize": "13px",
                                        "margin": "0",
                                    },
                                ),
                            ]
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "12px",
                        "marginBottom": "16px",
                    },
                ),

                html.Div(
                    [

                        # =================================================
                        # RAMPE
                        # =================================================

                        html.Div(
                            [
                                html.Div(
                                    "FILTRO RAMPE",
                                    style={
                                        "color": MORADO,
                                        "fontSize": "12px",
                                        "fontWeight": "800",
                                        "letterSpacing": "0.8px",
                                        "textAlign": "center",
                                        "marginBottom": "3px",
                                    },
                                ),

                                html.Img(
                                    src="/assets/filtro_rampe.png",
                                    style={
                                        "width": "100%",
                                        "height": "auto",
                                        "display": "block",
                                        "margin": "0",
                                        "padding": "0",
                                    },
                                ),

                                html.H4(
                                    "Mayor énfasis en altas frecuencias",
                                    style={
                                        "color": BLANCO,
                                        "fontSize": "14px",
                                        "textAlign": "center",
                                        "margin": "4px 0 3px",
                                    },
                                ),

                                html.P(
                                    "Ayuda a recuperar detalle, pero puede "
                                    "hacer más visible el ruido.",
                                    style={
                                        "color": "#AEBBD0",
                                        "fontSize": "12px",
                                        "lineHeight": "1.45",
                                        "textAlign": "center",
                                        "margin": "0",
                                    },
                                ),
                            ],
                            style={
                                "flex": "1",
                                "minWidth": "0",
                                "background": "#0B1220",
                                "border": "1px solid #273449",
                                "borderRadius": "12px",
                                "padding": "8px 12px 12px",
                                "boxSizing": "border-box",
                            },
                        ),

                        # =================================================
                        # HAMMING
                        # =================================================

                        html.Div(
                            [
                                html.Div(
                                    "FILTRO HAMMING",
                                    style={
                                        "color": CIAN,
                                        "fontSize": "12px",
                                        "fontWeight": "800",
                                        "letterSpacing": "0.8px",
                                        "textAlign": "center",
                                        "marginBottom": "3px",
                                    },
                                ),

                                html.Img(
                                    src="/assets/filtro_hamming.png",
                                    style={
                                        "width": "100%",
                                        "height": "auto",
                                        "display": "block",
                                        "margin": "0",
                                        "padding": "0",
                                    },
                                ),

                                html.H4(
                                    "Suaviza las altas frecuencias",
                                    style={
                                        "color": BLANCO,
                                        "fontSize": "14px",
                                        "textAlign": "center",
                                        "margin": "4px 0 3px",
                                    },
                                ),

                                html.P(
                                    "Reduce determinadas componentes de alta "
                                    "frecuencia y suaviza la respuesta.",
                                    style={
                                        "color": "#AEBBD0",
                                        "fontSize": "12px",
                                        "lineHeight": "1.45",
                                        "textAlign": "center",
                                        "margin": "0",
                                    },
                                ),
                            ],
                            style={
                                "flex": "1",
                                "minWidth": "0",
                                "background": "#0B1220",
                                "border": "1px solid #273449",
                                "borderRadius": "12px",
                                "padding": "8px 12px 12px",
                                "boxSizing": "border-box",
                            },
                        ),

                        # =================================================
                        # COSENO
                        # =================================================

                        html.Div(
                            [
                                html.Div(
                                    "FILTRO COSENO",
                                    style={
                                        "color": MORADO,
                                        "fontSize": "12px",
                                        "fontWeight": "800",
                                        "letterSpacing": "0.8px",
                                        "textAlign": "center",
                                        "marginBottom": "3px",
                                    },
                                ),

                                html.Img(
                                    src="/assets/filtro_coseno.png",
                                    style={
                                        "width": "100%",
                                        "height": "auto",
                                        "display": "block",
                                        "margin": "0",
                                        "padding": "0",
                                    },
                                ),

                                html.H4(
                                    "Respuesta suavizada",
                                    style={
                                        "color": BLANCO,
                                        "fontSize": "14px",
                                        "textAlign": "center",
                                        "margin": "4px 0 3px",
                                    },
                                ),

                                html.P(
                                    "Modifica la respuesta de frecuencia mediante "
                                    "una ventana cosenoidal.",
                                    style={
                                        "color": "#AEBBD0",
                                        "fontSize": "12px",
                                        "lineHeight": "1.45",
                                        "textAlign": "center",
                                        "margin": "0",
                                    },
                                ),
                            ],
                            style={
                                "flex": "1",
                                "minWidth": "0",
                                "background": "#0B1220",
                                "border": "1px solid #273449",
                                "borderRadius": "12px",
                                "padding": "8px 12px 12px",
                                "boxSizing": "border-box",
                            },
                        ),

                    ],
                    style={
                        "display": "flex",
                        "alignItems": "stretch",
                        "gap": "12px",
                        "width": "100%",
                    },
                ),
            ],
            className="ct-fundamento-card",
            style={
                "background": "#101A2B",
                "border": "1px solid #273449",
                "borderRadius": "14px",
                "padding": "20px",
                "marginBottom": "8px",
                "boxSizing": "border-box",
            },
        ),

        # =====================================================
        # IDEA FINAL
        # =====================================================

        html.Div(
            [
                html.Div(
                    "03",
                    style={
                        "width": "38px",
                        "height": "38px",
                        "borderRadius": "50%",
                        "background": MORADO,
                        "color": BLANCO,
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "fontWeight": "800",
                        "fontSize": "13px",
                        "flexShrink": "0",
                    },
                ),

                html.Div(
                    [
                        html.Div(
                            "COMPROMISO ENTRE DETALLE Y RUIDO",
                            style={
                                "color": CIAN,
                                "fontSize": "11px",
                                "fontWeight": "800",
                                "letterSpacing": "0.8px",
                                "marginBottom": "4px",
                            },
                        ),

                        html.Div(
                            "Los filtros permiten estudiar cómo cambia "
                            "la imagen reconstruida al modificar las "
                            "frecuencias espaciales.",
                            className="ct-callout-text",
                            style={
                                "color": "#E5E7EB",
                                "fontSize": "13px",
                                "lineHeight": "1.5",
                            },
                        ),
                    ],
                ),
            ],
            className="ct-info-callout",
            style={
                "display": "flex",
                "alignItems": "center",
                "gap": "12px",
                "background": "rgba(139,92,246,.08)",
                "border": "1px solid rgba(139,92,246,.30)",
                "borderRadius": "12px",
                "padding": "13px 16px",
                "marginBottom": "20px",
            },
        ),
    ]


def block8():

    return [

        section(
            '08',
            'Geometría de haz de abanico',
            'Del modelo paralelo hacia una geometría de TC'
        ),

        # =========================================================
        # 01 — ¿QUÉ CAMBIA?
        # =========================================================

        card(
            '¿Qué cambia?',
            html.Div(
                [

                    p(
                        'En una geometría de haz de abanico, los rayos divergen '
                        'desde una misma fuente. Por ello, la posición de la '
                        'fuente, el ángulo de cada rayo y la geometría del '
                        'detector deben considerarse durante la reconstrucción.'
                    ),

                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        'FUENTE',
                                        style={
                                            'color': CIAN,
                                            'fontSize': '12px',
                                            'fontWeight': '800',
                                            'letterSpacing': '0.8px',
                                            'marginBottom': '8px',
                                            'textAlign': 'center'
                                        }
                                    ),

                                    html.Div(
                                        '●',
                                        style={
                                            'fontSize': '30px',
                                            'color': MORADO,
                                            'textAlign': 'center'
                                        }
                                    )
                                ],
                                style={
                                    'width': '100%',
                                    'textAlign': 'center'
                                }
                            ),

                            html.Div(
                                [
                                    html.Div(
                                        '↘  →  →  →  →',
                                        style={
                                            'color': CIAN,
                                            'fontSize': '23px',
                                            'letterSpacing': '5px'
                                        }
                                    ),
                                    html.Div(
                                        '↗  →  →  →  →',
                                        style={
                                            'color': CIAN,
                                            'fontSize': '23px',
                                            'letterSpacing': '5px'
                                        }
                                    ),
                                    html.Div(
                                        '→  →  →  →  →',
                                        style={
                                            'color': CIAN,
                                            'fontSize': '23px',
                                            'letterSpacing': '5px'
                                        }
                                    )
                                ],
                                style={
                                    'width': '100%',
                                    'textAlign': 'center',
                                    'lineHeight': '1.35'
                                }
                            ),

                            html.Div(
                                [
                                    html.Div(
                                        'OBJETO',
                                        style={
                                            'color': BLANCO,
                                            'fontSize': '14px',
                                            'fontWeight': '800',
                                            'textAlign': 'center'
                                        }
                                    ),

                                    html.Div(
                                        '◯',
                                        style={
                                            'fontSize': '48px',
                                            'color': '#A78BFA',
                                            'textAlign': 'center'
                                        }
                                    )
                                ],
                                style={
                                    'width': '100%',
                                    'textAlign': 'center'
                                }
                            ),

                            html.Div(
                                [
                                    html.Div(
                                        'DETECTOR',
                                        style={
                                            'color': CIAN,
                                            'fontSize': '12px',
                                            'fontWeight': '800',
                                            'letterSpacing': '0.8px',
                                            'marginBottom': '8px',
                                            'textAlign': 'center'
                                        }
                                    ),

                                    html.Div(
                                        '▮ ▮ ▮ ▮ ▮ ▮',
                                        style={
                                            'color': '#CBD5E1',
                                            'fontSize': '22px',
                                            'letterSpacing': '3px',
                                            'textAlign': 'center'
                                        }
                                    )
                                ],
                                style={
                                    'width': '100px',
                                    'flexShrink': '0'
                                }
                            )

                        ],
                        style={
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'gap': '35px',
                            'width': '100%',
                            'maxWidth': '1050px',
                            'margin': '0 auto',
                            'background': '#0B1220',
                            'border': '1px solid #273449',
                            'borderRadius': '12px',
                            'padding': '22px 30px',
                            'boxSizing': 'border-box',
                            'overflow': 'hidden'
                        }
                    ),

                    html.Div(
                        [
                            html.Div(
                                'HAZ DE ABANICO',
                                style={
                                    'color': MORADO,
                                    'fontSize': '12px',
                                    'fontWeight': '800',
                                    'letterSpacing': '0.8px'
                                }
                            ),

                            html.Div(
                                'Los rayos salen de una fuente común y forman diferentes ángulos.',
                                className="ct-callout-text",
                                style={
                                    'color': '#D1D5DB',
                                    'fontSize': '13px'
                                }
                            )
                        ],
                        className="ct-info-callout",
                        style={
                            'display': 'flex',
                            'alignItems': 'center',
                            'gap': '14px',
                            'background': 'rgba(139,92,246,.08)',
                            'border': '1px solid rgba(139,92,246,.25)',
                            'borderRadius': '10px',
                            'padding': '11px 14px',
                            'marginTop': '12px'
                        }
                    )

                ]
            )
        ),

        # =========================================================
        # 02 — CONFIGURACIONES DE MUESTREO
        # =========================================================

        card(
            'Configuraciones de muestreo',
            html.Div(
                [

                    html.P(
                        'La geometría del detector determina cómo se distribuyen '
                        'las mediciones dentro del haz de abanico.',
                        style={
                            'color': '#AEBBD0',
                            'fontSize': '14px',
                            'marginBottom': '15px'
                        }
                    ),

                    html.Div(
                        [

                            # -----------------------------------------
                            # RAYOS EQUIANGULARES
                            # -----------------------------------------

                            html.Div(
                                [
                                    html.Div(
                                        '01',
                                        style={
                                            'width': '36px',
                                            'height': '36px',
                                            'borderRadius': '50%',
                                            'background': MORADO,
                                            'color': BLANCO,
                                            'display': 'flex',
                                            'alignItems': 'center',
                                            'justifyContent': 'center',
                                            'fontWeight': '800',
                                            'margin': '0 auto 9px'
                                        }
                                    ),

                                    html.H4(
                                        'Rayos equiangulares',
                                        style={
                                            'color': BLANCO,
                                            'fontSize': '15px',
                                            'textAlign': 'center',
                                            'margin': '0 0 8px'
                                        }
                                    ),

                                    html.Div(
                                        [
                                            '↘',
                                            ' → ',
                                            '→ ',
                                            '→ ',
                                            '↗'
                                        ],
                                        style={
                                            'color': CIAN,
                                            'fontSize': '22px',
                                            'textAlign': 'center',
                                            'letterSpacing': '4px',
                                            'marginBottom': '8px'
                                        }
                                    ),

                                    html.P(
                                        'Separación angular constante entre rayos.',
                                        style={
                                            'color': '#AEBBD0',
                                            'fontSize': '12px',
                                            'lineHeight': '1.45',
                                            'textAlign': 'center',
                                            'margin': '0'
                                        }
                                    )
                                ],
                                style={
                                    'flex': '1',
                                    'minWidth': '0',
                                    'background': '#0B1220',
                                    'border': '1px solid #273449',
                                    'borderRadius': '12px',
                                    'padding': '15px',
                                    'boxSizing': 'border-box'
                                }
                            ),

                            # -----------------------------------------
                            # DETECTOR RECTILÍNEO
                            # -----------------------------------------

                            html.Div(
                                [
                                    html.Div(
                                        '02',
                                        style={
                                            'width': '36px',
                                            'height': '36px',
                                            'borderRadius': '50%',
                                            'background': CIAN,
                                            'color': '#07111F',
                                            'display': 'flex',
                                            'alignItems': 'center',
                                            'justifyContent': 'center',
                                            'fontWeight': '800',
                                            'margin': '0 auto 9px'
                                        }
                                    ),

                                    html.H4(
                                        'Detector rectilíneo',
                                        style={
                                            'color': BLANCO,
                                            'fontSize': '15px',
                                            'textAlign': 'center',
                                            'margin': '0 0 8px'
                                        }
                                    ),

                                    html.Div(
                                        '▮  ▮  ▮  ▮  ▮  ▮',
                                        style={
                                            'color': CIAN,
                                            'fontSize': '18px',
                                            'textAlign': 'center',
                                            'letterSpacing': '3px',
                                            'marginBottom': '8px'
                                        }
                                    ),

                                    html.P(
                                        'Elementos con separación lineal constante.',
                                        style={
                                            'color': '#AEBBD0',
                                            'fontSize': '12px',
                                            'lineHeight': '1.45',
                                            'textAlign': 'center',
                                            'margin': '0'
                                        }
                                    )
                                ],
                                style={
                                    'flex': '1',
                                    'minWidth': '0',
                                    'background': '#0B1220',
                                    'border': '1px solid #273449',
                                    'borderRadius': '12px',
                                    'padding': '15px',
                                    'boxSizing': 'border-box'
                                }
                            ),

                            # -----------------------------------------
                            # DETECTOR EN ARCO
                            # -----------------------------------------

                            html.Div(
                                [
                                    html.Div(
                                        '03',
                                        style={
                                            'width': '36px',
                                            'height': '36px',
                                            'borderRadius': '50%',
                                            'background': MORADO,
                                            'color': BLANCO,
                                            'display': 'flex',
                                            'alignItems': 'center',
                                            'justifyContent': 'center',
                                            'fontWeight': '800',
                                            'margin': '0 auto 9px'
                                        }
                                    ),

                                    html.H4(
                                        'Detector en arco',
                                        style={
                                            'color': BLANCO,
                                            'fontSize': '15px',
                                            'textAlign': 'center',
                                            'margin': '0 0 8px'
                                        }
                                    ),

                                    html.Div(
                                        '⌒  ⌒  ⌒',
                                        style={
                                            'color': CIAN,
                                            'fontSize': '25px',
                                            'textAlign': 'center',
                                            'marginBottom': '8px'
                                        }
                                    ),

                                    html.P(
                                        'Elementos separados angularmente alrededor de la fuente.',
                                        style={
                                            'color': '#AEBBD0',
                                            'fontSize': '12px',
                                            'lineHeight': '1.45',
                                            'textAlign': 'center',
                                            'margin': '0'
                                        }
                                    )
                                ],
                                style={
                                    'flex': '1',
                                    'minWidth': '0',
                                    'background': '#0B1220',
                                    'border': '1px solid #273449',
                                    'borderRadius': '12px',
                                    'padding': '15px',
                                    'boxSizing': 'border-box'
                                }
                            )

                        ],
                        style={
                            'display': 'flex',
                            'gap': '12px',
                            'alignItems': 'stretch',
                            'width': '100%'
                        }
                    ),

                    html.Div(
                        [
                            html.Span(
                                html.I(className="fa-solid fa-lightbulb", style={"color": "#facc15"}),
                                style={
                                    'fontSize': '20px',
                                    'marginRight': '9px'
                                }
                            ),

                            html.Span(
                                'La geometría utilizada determina cómo deben interpretarse las mediciones.',
                                className="ct-callout-text",
                                style={
                                    'color': '#E5E7EB',
                                    'fontSize': '13px'
                                }
                            )
                        ],
                        className="ct-info-callout",
                        style={
                            'display': 'flex',
                            'alignItems': 'center',
                            'background': 'rgba(34,211,238,.07)',
                            'border': '1px solid rgba(34,211,238,.22)',
                            'borderRadius': '10px',
                            'padding': '11px 14px',
                            'marginTop': '14px'
                        }
                    )

                ]
            )
        ),

        # =========================================================
        # 03 — REBINNING
        # =========================================================

        card(
            'Rebinning',
            html.Div(
                [

                    p(
                        'Una estrategia consiste en reorganizar las mediciones '
                        'del haz de abanico para aproximarlas a una representación '
                        'de rayos paralelos. Este proceso se conoce como rebinning '
                        'y requiere interpolación.'
                    ),

                    html.Div(
                        [

                            html.Div(
                                [
                                    html.Div(
                                        'HAZ DE ABANICO',
                                        style={
                                            'color': MORADO,
                                            'fontSize': '11px',
                                            'fontWeight': '800',
                                            'letterSpacing': '0.8px',
                                            'marginBottom': '7px',
                                            'textAlign': 'center'
                                        }
                                    ),

                                    html.Div(
                                        '↘  →  →  →\n→  →  →  →\n↗  →  →  →',
                                        style={
                                            'whiteSpace': 'pre-line',
                                            'color': CIAN,
                                            'fontSize': '20px',
                                            'lineHeight': '1.25',
                                            'textAlign': 'center'
                                        }
                                    )
                                ],
                                style={
                                    'flex': '1',
                                    'background': '#0B1220',
                                    'borderRadius': '10px',
                                    'padding': '15px'
                                }
                            ),

                            html.Div(
                                '→',
                                style={
                                    'color': CIAN,
                                    'fontSize': '30px',
                                    'fontWeight': '800'
                                }
                            ),

                            html.Div(
                                [
                                    html.Div(
                                        'INTERPOLACIÓN',
                                        style={
                                            'color': CIAN,
                                            'fontSize': '11px',
                                            'fontWeight': '800',
                                            'letterSpacing': '0.8px',
                                            'marginBottom': '7px',
                                            'textAlign': 'center'
                                        }
                                    ),

                                    html.Div(
                                        '↕  ↕  ↕',
                                        style={
                                            'color': MORADO,
                                            'fontSize': '27px',
                                            'textAlign': 'center',
                                            'marginTop': '10px'
                                        }
                                    ),

                                    html.Div(
                                        'Reorganización de las mediciones',
                                        style={
                                            'color': '#AEBBD0',
                                            'fontSize': '12px',
                                            'textAlign': 'center'
                                        }
                                    )
                                ],
                                style={
                                    'flex': '1',
                                    'background': '#0B1220',
                                    'borderRadius': '10px',
                                    'padding': '15px'
                                }
                            ),

                            html.Div(
                                '→',
                                style={
                                    'color': CIAN,
                                    'fontSize': '30px',
                                    'fontWeight': '800'
                                }
                            ),

                            html.Div(
                                [
                                    html.Div(
                                        'RAYOS PARALELOS',
                                        style={
                                            'color': MORADO,
                                            'fontSize': '11px',
                                            'fontWeight': '800',
                                            'letterSpacing': '0.8px',
                                            'marginBottom': '7px',
                                            'textAlign': 'center'
                                        }
                                    ),

                                    html.Div(
                                        '→  →  →  →\n→  →  →  →\n→  →  →  →',
                                        style={
                                            'whiteSpace': 'pre-line',
                                            'color': CIAN,
                                            'fontSize': '20px',
                                            'lineHeight': '1.25',
                                            'textAlign': 'center'
                                        }
                                    )
                                ],
                                style={
                                    'flex': '1',
                                    'background': '#0B1220',
                                    'borderRadius': '10px',
                                    'padding': '15px'
                                }
                            )

                        ],
                        style={
                            'display': 'flex',
                            'alignItems': 'center',
                            'gap': '12px',
                            'marginTop': '15px'
                        }
                    ),

                    html.Div(
                        [
                            html.Div(
                                'CONCEPTO CLAVE',
                                style={
                                    'color': CIAN,
                                    'fontSize': '11px',
                                    'fontWeight': '800',
                                    'letterSpacing': '0.8px',
                                    'marginBottom': '4px'
                                }
                            ),

                            html.Div(
                                'El rebinning reorganiza las mediciones para facilitar su representación y procesamiento.',
                                className="ct-callout-text",
                                style={
                                    'color': '#E5E7EB',
                                    'fontSize': '13px',
                                    'lineHeight': '1.5'
                                }
                            )
                        ],
                        className="ct-info-callout",
                        style={
                            'background': 'rgba(34,211,238,.07)',
                            'border': '1px solid rgba(34,211,238,.25)',
                            'borderRadius': '10px',
                            'padding': '12px 15px',
                            'marginTop': '14px'
                        }
                    )

                ]
            )
        )
    ]
def block9():

    conceptos = [
        ('01', 'Atenuación',
         'Disminución de la intensidad de los rayos X al atravesar materia.',
         'La atenuación describe cómo el haz pierde intensidad debido a su interacción con la materia.'),

        ('02', 'Proyección',
         'Información de atenuación medida a lo largo de una dirección.',
         'Una proyección reúne la información obtenida desde una determinada dirección durante la adquisición.'),

        ('03', 'Radon',
         'Relación matemática entre el objeto y sus proyecciones.',
         'La transformada de Radon representa matemáticamente las integrales de línea obtenidas desde diferentes ángulos.'),

        ('04', 'Sinograma',
         'Representación de las proyecciones según posición y ángulo.',
         'El sinograma organiza las mediciones de las proyecciones y permite visualizar cómo cambian al variar el ángulo.'),

        ('05', 'Retroproyección',
         'Distribución de las proyecciones sobre sus líneas originales.',
         'La retroproyección lleva nuevamente cada medición hacia las trayectorias de donde provino para formar una estimación de la imagen.'),

        ('06', 'FBP',
         'Filtrado de las proyecciones seguido de retroproyección.',
         'La retroproyección filtrada combina el filtrado de las proyecciones con su posterior distribución sobre la imagen.'),

        ('07', 'Filtro Rampe',
         'Filtro que enfatiza componentes de alta frecuencia.',
         'El filtro Rampe ayuda a recuperar detalles y cambios rápidos de intensidad, aunque puede hacer más visible el ruido.'),

        ('08', 'Haz de abanico',
         'Geometría donde los rayos divergen desde una fuente.',
         'En esta geometría los rayos parten de una fuente común y forman diferentes ángulos antes de llegar al detector.'),

        ('09', 'Shepp–Logan',
         'Fantoma utilizado para demostrar reconstrucción.',
         'El fantoma de Shepp–Logan permite estudiar y visualizar procesos de reconstrucción tomográfica de forma controlada.'),

        ('10', 'RMSE',
         'Raíz del error cuadrático medio frente a una referencia.',
         'El RMSE permite cuantificar la diferencia entre una imagen reconstruida y una imagen de referencia.')
    ]


    # =========================================================
    # TARJETAS DE CONCEPTOS
    # =========================================================

    tarjetas = []

    for numero, titulo, resumen, detalle in conceptos:

        tarjetas.append(
            html.Button(
                [
                    html.Div(
                        numero,
                        style={
                            'width': '34px',
                            'height': '34px',
                            'borderRadius': '50%',
                            'background': '#263750',
                            'color': '#FFFFFF',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'fontWeight': '800',
                            'fontSize': '12px',
                            'flexShrink': '0'
                        }
                    ),

                    html.Div(
                        [
                            html.Div(
                                titulo,
                                style={
                                    'color': BLANCO,
                                    'fontSize': '15px',
                                    'fontWeight': '700',
                                    'textAlign': 'left'
                                }
                            ),

                            html.Div(
                                resumen,
                                style={
                                    'color': '#AEBBD0',
                                    'fontSize': '12px',
                                    'lineHeight': '1.35',
                                    'textAlign': 'left',
                                    'marginTop': '3px'
                                }
                            )
                        ],
                        style={
                            'flex': '1',
                            'minWidth': '0'
                        }
                    )
                ],

                id=f'concepto-{numero}',

                n_clicks=0,

                className="ct-concept-btn",

                style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'gap': '11px',
                    'width': '100%',
                    'minHeight': '72px',
                    'background': '#101A2B',
                    'border': '1px solid #273449',
                    'borderRadius': '12px',
                    'padding': '10px 12px',
                    'cursor': 'pointer',
                    'boxSizing': 'border-box',
                    'textAlign': 'left'
                }
            )
        )


    return [

        # =====================================================
        # TÍTULO
        # =====================================================

        section(
            '09',
            'Conceptos clave',
            'Resumen interactivo para estudiar'
        ),


        # =====================================================
        # CONTENEDOR PRINCIPAL
        # =====================================================
        html.Div(
            [

                # -------------------------------------------------
                # COLUMNA DE CONCEPTOS
                # -------------------------------------------------

                html.Div(
                    [
                        html.H3(
                            'Explora los conceptos',
                            style={
                                'color': BLANCO,
                                'fontSize': '20px',
                                'fontWeight': '700',
                                'marginBottom': '6px'
                            }
                        ),

                        html.P(
                            'Selecciona un concepto para ver su explicación.',
                            style={
                                'color': '#AEBBD0',
                                'fontSize': '14px',
                                'marginBottom': '16px'
                            }
                        ),

                        html.Div(
                            tarjetas,
                            style={
                                'display': 'grid',
                                'gridTemplateColumns':
                                    'repeat(2, minmax(0, 1fr))',
                                'gap': '10px'
                            }
                        )
                    ],

                    className="ct-fundamento-card",
                    style={
                        'flex': '1.35',
                        'minWidth': '0',
                        'background': '#101A2B',
                        'border': '1px solid #273449',
                        'borderRadius': '14px',
                        'padding': '20px'
                    }
                ),

                html.Div(
                    [
                # -------------------------------------------------
                # PANEL INTERACTIVO
                # -------------------------------------------------

                        html.Div(
                            '01',
                            id='concepto-numero',
                            style={
                                'width': '48px',
                                'height': '48px',
                                'borderRadius': '50%',
                                'background': CIAN,
                                'color': '#07111F',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'fontWeight': '800',
                                'fontSize': '15px',
                                'marginBottom': '14px'
                            }
                        ),
                        
                        html.Div(
                            [
                                html.Img(
                                    id='concepto-imagen',
                                    src='/assets/proceso_adquisicion.png',
                                    style={
                                        'width': '100%',
                                        'height': '320px',
                                        'objectFit': 'contain',
                                        'display': 'block',
                                        'borderRadius': '12px',
                                        'margin': 'auto'
                                    }
                                )
                            ],
                            className="ct-subcard",
                            style={
                                'width': '100%',
                                'minHeight': '340px',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'background': '#101A2B',
                                'border': '1px solid #273449',
                                'borderRadius': '14px',
                                'padding': '10px',
                                'boxSizing': 'border-box',
                                'marginBottom': '18px'
                            }
                        ),
                        html.H2(
                            'Atenuación',
                            id='concepto-titulo',
                            style={
                                'color': CIAN,
                                'fontSize': '25px',
                                'fontWeight': '800',
                                'margin': '0 0 10px'
                            }
                        ),

                        html.Div(
                            'Disminución de la intensidad de los rayos X al atravesar materia.',
                            id='concepto-resumen',
                            style={
                                'color': BLANCO,
                                'fontSize': '16px',
                                'fontWeight': '600',
                                'lineHeight': '1.5',
                                'marginBottom': '18px'
                            }
                        ),

                        html.Div(
                            [
                                html.Div(
                                    '¿QUÉ SIGNIFICA?',
                                    style={
                                        'color': MORADO,
                                        'fontSize': '11px',
                                        'fontWeight': '800',
                                        'letterSpacing': '1px',
                                        'marginBottom': '7px'
                                    }
                                ),

                                html.P(
                                    'La atenuación describe cómo el haz pierde intensidad debido a su interacción con la materia.',
                                    id='concepto-detalle',
                                    style={
                                        'color': '#D1D5DB',
                                        'fontSize': '14px',
                                        'lineHeight': '1.6',
                                        'margin': '0'
                                    }
                                ),

                                html.Div(
                                    [
                                        html.Div(
                                            'APLICACIÓN EN TC',
                                            style={
                                                'color': CIAN,
                                                'fontSize': '11px',
                                                'fontWeight': '800',
                                                'letterSpacing': '1px',
                                                'marginBottom': '6px'
                                            }
                                        ),

                                        html.P(
                                            'En TC, las diferencias de atenuación permiten obtener información sobre las estructuras atravesadas por los rayos X.',
                                            id='concepto-aplicacion',
                                            style={
                                                'color': '#D1D5DB',
                                                'fontSize': '13px',
                                                'lineHeight': '1.55',
                                                'margin': '0'
                                            }
                                        )
                                    ],
                                    style={
                                        'background': 'rgba(34, 211, 238, 0.06)',
                                        'border': '1px solid rgba(34, 211, 238, 0.20)',
                                        'borderRadius': '10px',
                                        'padding': '13px',
                                        'marginTop': '12px'
                                    }
                                ),
                            ],

                            className="ct-subcard",
                            style={
                                'background': '#0B1220',
                                'border': '1px solid #273449',
                                'borderRadius': '11px',
                                'padding': '15px'
                            }
                        ),

                        html.Div(
                            [
                                html.Span(
                                    html.I(className="fa-solid fa-lightbulb", style={"color": "#facc15"}),
                                    style={
                                        'fontSize': '20px',
                                        'marginRight': '8px'
                                    }
                                ),

                                html.Span(
                                    'Haz clic en otro concepto para continuar.',
                                    style={
                                        'color': '#AEBBD0',
                                        'fontSize': '12px'
                                    }
                                )
                            ],

                            style={
                                'display': 'flex',
                                'alignItems': 'center',
                                'marginTop': '15px'
                            }
                        )
                    ],

                    className="ct-fundamento-card",
                    style={
                        'flex': '0.85',
                        'minWidth': '0',
                        'background': '#151D2E',
                        'border': '1px solid #273449',
                        'borderRadius': '14px',
                        'padding': '22px',
                        'alignSelf': 'stretch'
                    }
                )
            ],
            style={
                'display': 'flex',
                'gap': '16px',
                'alignItems': 'stretch',
                'width': '100%',
                'marginBottom': '20px'
            }
        ),
                # =========================================================
        # IDEA CENTRAL INTERACTIVA
        # =========================================================

        html.Div(
            [
                html.Div(
                    [
                        html.Span(
                            html.I(className="fa-solid fa-microscope", style={"color": CIAN}),
                            style={
                                'fontSize': '25px',
                                'marginRight': '12px'
                            }
                        ),

                        html.Div(
                            [
                                html.Div(
                                    'LA IDEA CENTRAL DE TODA LA TC',
                                    style={
                                        'color': CIAN,
                                        'fontSize': '12px',
                                        'fontWeight': '800',
                                        'letterSpacing': '0.8px',
                                        'marginBottom': '7px'
                                    }
                                ),

                                html.P(
                                    'Explora el proceso completo de formación de una imagen de TC.',
                                    style={
                                        'color': '#AEBBD0',
                                        'fontSize': '13px',
                                        'margin': '0'
                                    }
                                )
                            ]
                        )
                    ],
                    style={
                        'display': 'flex',
                        'alignItems': 'center',
                        'marginBottom': '18px'
                    }
                ),

                # -------------------------------------------------
                # ETAPAS
                # -------------------------------------------------

                html.Div(
                    [
                        html.Button(
                            [
                                html.Div(
                                    '01',
                                    style={
                                        'fontSize': '12px',
                                        'fontWeight': '800',
                                        'color': '#07111F',
                                        'background': CIAN,
                                        'width': '30px',
                                        'height': '30px',
                                        'borderRadius': '50%',
                                        'display': 'flex',
                                        'alignItems': 'center',
                                        'justifyContent': 'center',
                                        'margin': '0 auto 7px'
                                    }
                                ),
                                html.Div(
                                    'MEDIR',
                                    style={
                                        'color': BLANCO,
                                        'fontSize': '12px',
                                        'fontWeight': '800'
                                    }
                                )
                            ],
                            id='idea-tc-01',
                            n_clicks=0,
                            className="ct-concept-btn",
                            style={
                                'flex': '1',
                                'background': '#101A2B',
                                'border': '1px solid #273449',
                                'borderRadius': '11px',
                                'padding': '10px 6px',
                                'cursor': 'pointer'
                            }
                        ),

                        html.Button(
                            [
                                html.Div(
                                    '02',
                                    style={
                                        'fontSize': '12px',
                                        'fontWeight': '800',
                                        'color': '#07111F',
                                        'background': CIAN,
                                        'width': '30px',
                                        'height': '30px',
                                        'borderRadius': '50%',
                                        'display': 'flex',
                                        'alignItems': 'center',
                                        'justifyContent': 'center',
                                        'margin': '0 auto 7px'
                                    }
                                ),
                                html.Div(
                                    'ORGANIZAR',
                                    style={
                                        'color': BLANCO,
                                        'fontSize': '12px',
                                        'fontWeight': '800'
                                    }
                                )
                            ],
                            id='idea-tc-02',
                            n_clicks=0,
                            className="ct-concept-btn",
                            style={
                                'flex': '1',
                                'background': '#101A2B',
                                'border': '1px solid #273449',
                                'borderRadius': '11px',
                                'padding': '10px 6px',
                                'cursor': 'pointer'
                            }
                        ),

                        html.Button(
                            [
                                html.Div(
                                    '03',
                                    style={
                                        'fontSize': '12px',
                                        'fontWeight': '800',
                                        'color': '#07111F',
                                        'background': CIAN,
                                        'width': '30px',
                                        'height': '30px',
                                        'borderRadius': '50%',
                                        'display': 'flex',
                                        'alignItems': 'center',
                                        'justifyContent': 'center',
                                        'margin': '0 auto 7px'
                                    }
                                ),
                                html.Div(
                                    'FILTRAR',
                                    style={
                                        'color': BLANCO,
                                        'fontSize': '12px',
                                        'fontWeight': '800'
                                    }
                                )
                            ],
                            id='idea-tc-03',
                            n_clicks=0,
                            className="ct-concept-btn",
                            style={
                                'flex': '1',
                                'background': '#101A2B',
                                'border': '1px solid #273449',
                                'borderRadius': '11px',
                                'padding': '10px 6px',
                                'cursor': 'pointer'
                            }
                        ),

                        html.Button(
                            [
                                html.Div(
                                    '04',
                                    style={
                                        'fontSize': '12px',
                                        'fontWeight': '800',
                                        'color': '#07111F',
                                        'background': CIAN,
                                        'width': '30px',
                                        'height': '30px',
                                        'borderRadius': '50%',
                                        'display': 'flex',
                                        'alignItems': 'center',
                                        'justifyContent': 'center',
                                        'margin': '0 auto 7px'
                                    }
                                ),
                                html.Div(
                                    'RETROPROYECTAR',
                                    style={
                                        'color': BLANCO,
                                        'fontSize': '11px',
                                        'fontWeight': '800'
                                    }
                                )
                            ],
                            id='idea-tc-04',
                            n_clicks=0,
                            className="ct-concept-btn",
                            style={
                                'flex': '1',
                                'background': '#101A2B',
                                'border': '1px solid #273449',
                                'borderRadius': '11px',
                                'padding': '10px 6px',
                                'cursor': 'pointer'
                            }
                        ),

                        html.Button(
                            [
                                html.Div(
                                    '05',
                                    style={
                                        'fontSize': '12px',
                                        'fontWeight': '800',
                                        'color': '#07111F',
                                        'background': CIAN,
                                        'width': '30px',
                                        'height': '30px',
                                        'borderRadius': '50%',
                                        'display': 'flex',
                                        'alignItems': 'center',
                                        'justifyContent': 'center',
                                        'margin': '0 auto 7px'
                                    }
                                ),
                                html.Div(
                                    'RECONSTRUIR',
                                    style={
                                        'color': BLANCO,
                                        'fontSize': '11px',
                                        'fontWeight': '800'
                                    }
                                )
                            ],
                            id='idea-tc-05',
                            n_clicks=0,
                            className="ct-concept-btn",
                            style={
                                'flex': '1',
                                'background': '#101A2B',
                                'border': '1px solid #273449',
                                'borderRadius': '11px',
                                'padding': '10px 6px',
                                'cursor': 'pointer'
                            }
                        )
                    ],
                    style={
                        'display': 'flex',
                        'gap': '8px',
                        'width': '100%'
                    }
                ),

                # -------------------------------------------------
                # EXPLICACIÓN
                # -------------------------------------------------

                html.Div(
                    [
                        html.Div(
                            '01',
                            id='idea-tc-numero',
                            style={
                                'width': '38px',
                                'height': '38px',
                                'borderRadius': '50%',
                                'background': CIAN,
                                'color': '#07111F',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'fontWeight': '800',
                                'fontSize': '13px',
                                'flexShrink': '0'
                            }
                        ),

                        html.Div(
                            [
                                html.H4(
                                    'Medir desde muchas direcciones',
                                    id='idea-tc-titulo',
                                    style={
                                        'color': CIAN,
                                        'fontSize': '17px',
                                        'fontWeight': '800',
                                        'margin': '0 0 5px'
                                    }
                                ),

                                html.P(
                                    'La TC obtiene mediciones de atenuación desde diferentes direcciones alrededor del objeto.',
                                    id='idea-tc-texto',
                                    style={
                                        'color': '#D1D5DB',
                                        'fontSize': '13px',
                                        'lineHeight': '1.5',
                                        'margin': '0'
                                    }
                                )
                            ]
                        )
                    ],
                    className="ct-subcard",
                    style={
                        'display': 'flex',
                        'alignItems': 'center',
                        'gap': '12px',
                        'background': '#101D2D',
                        'border': '1px solid #273449',
                        'borderRadius': '11px',
                        'padding': '13px 15px',
                        'marginTop': '12px'
                    }
                )
            ],
            className="ct-fundamento-card",
            style={
                'background': '#17152B',
                'border': f'1px solid {MORADO}',
                'borderRadius': '14px',
                'padding': '18px 20px',
                'marginBottom': '20px'
            }
        )
    ]


def block10():
    """Extensión matemática del proceso de TC, basada principalmente en las diapositivas base."""
    return [
        section(
            '10',
            'Formulación matemática del proceso',
            'De la atenuación y las proyecciones hasta la reconstrucción'
        ),

        card(
            '1. Atenuación: de I₀ a la medición tomográfica',
            html.Div([
                p('Las diapositivas presentan como medida fundamental de la TC la atenuación de los rayos X a lo largo de una línea entre la fuente y el detector. La intensidad disminuye al atravesar materia y la información de esa pérdida de intensidad se utiliza para obtener las integrales de línea del coeficiente de atenuación.'),
                formula('I = I₀ · exp(−∫ μ(x,y) ds)'),
                p('I₀ representa la intensidad incidente, I la intensidad medida por el detector y μ(x,y) el coeficiente de atenuación lineal. La integral recorre la trayectoria del rayo. En el simulador educativo esta física no se modela con un tubo y detectores reales; se utiliza como fundamento conceptual para pasar de un objeto a sus proyecciones.'),
                formula('p = −ln(I/I₀) = ∫ μ(x,y) ds'),
                p('Esta forma muestra el paso conceptual que conecta la medición de intensidades con una integral de línea. A partir de muchas de estas mediciones se construyen las proyecciones utilizadas para la reconstrucción.'),
                formula('CT = 1000 · (μ_t − μ_agua) / μ_agua   [HU]'),
                p('La definición de número CT en unidades Hounsfield permite expresar el coeficiente de atenuación de un tejido de forma relativa al agua. Esta relación pertenece al fundamento físico de la TC; nuestra simulación principal no genera HU clínicos porque trabaja con imágenes normalizadas.'),
                idea('La medición de TC no es todavía una imagen: es información integrada a lo largo de una trayectoria. Se necesitan muchas trayectorias y ángulos para reconstruir la distribución espacial.'),
            ])
        ),

        card(
            '2. Proyección y transformada de Radon',
            html.Div([
                p('Para una geometría de rayos paralelos, una proyección corresponde a una colección de integrales de línea tomadas con un ángulo θ. Las diapositivas relacionan directamente esta definición con la transformada de Radon 2-D.'),
                formula('p(s,θ) = ∫ f(x,y) · δ(x cosθ + y sinθ − s) dx dy'),
                html.P('Aquí p(s,θ) representa la proyección, s la posición sobre el detector y θ el ángulo de adquisición. La función f(x,y) representa el objeto o distribución que queremos reconstruir.', style={'color':'#D1D5DB','fontSize':'15px','lineHeight':'1.65','marginBottom':'12px'}),
                formula('R{f}(s,θ) = p(s,θ)'),
                html.Div([
                    html.Div([html.Strong('En nuestro simulador', style={'color':CIAN}), html.P('esta etapa se implementa mediante `radon(...)`, generando proyecciones para los ángulos seleccionados.', style={'color':'#D1D5DB','margin':'5px 0','lineHeight':'1.55'})], style={'flex':'1'}),
                    html.Div([html.Strong('Idea matemática', style={'color':'#C4B5FD'}), html.P('Radon transforma una imagen 2-D en un conjunto de proyecciones 1-D; su inversa permite recuperar la imagen.', style={'color':'#D1D5DB','margin':'5px 0','lineHeight':'1.55'})], style={'flex':'1'}),
                ], className="ct-subcard", style={'display':'flex','gap':'14px','background':'#0B1220','border':'1px solid #273449','borderRadius':'10px','padding':'14px'}),
            ])
        ),

        card(
            '3. El sinograma como representación de los datos',
            html.Div([
                html.Div([
                    html.Div([
                        html.H4('¿Qué representa?', style={'color':CIAN,'margin':'0 0 7px','fontSize':'18px'}),
                        p('El sinograma es una representación de la transformada de Radon. Una dimensión corresponde a la posición del detector y la otra al ángulo. Por eso cada fila o columna representa una proyección dependiendo de la convención utilizada.'),
                        formula('S(s,θ) = p(s,θ) = R{f(x,y)}'),
                    ], style={'flex':'1'}),
                    html.Div([
                        html.Img(src='/assets/sinograma_tc.png', className="ct-subcard", style={'width':'100%','height':'240px','objectFit':'contain','background':'#0B1220','borderRadius':'10px'}),
                        html.P('En el simulador, el sinograma permite ver cómo cambia la información de las proyecciones al rotar el objeto.', style={'color':'#AEBBD0','fontSize':'13px','lineHeight':'1.5','margin':'8px 0 0'}),
                    ], style={'flex':'1'}),
                ], style={'display':'flex','gap':'18px','alignItems':'center'}),
                idea('Un sinograma no es la imagen anatómica. Es una representación de los datos de proyección que posteriormente deben procesarse para reconstruir el corte.'),
            ])
        ),

        card(
            '4. Retroproyección: por qué aparece el desenfoque',
            html.Div([
                p('Las diapositivas muestran que una sola proyección no determina de forma única el objeto. En la retroproyección, cada valor medido se distribuye nuevamente sobre la línea de la que provino. Al sumar muchas retroproyecciones obtenemos una estimación de la imagen, pero aparece borrosidad.'),
                formula('b(x,y) = ∫ p(x cosθ + y sinθ, θ) dθ'),
                html.Div([
                    html.Div([html.Img(src='/assets/retroproyeccion_desenfoque.png', style={'width':'100%','height':'190px','objectFit':'contain'}), html.P('Retroproyección simple: las contribuciones se distribuyen y producen desenfoque.', style={'color':'#AEBBD0','fontSize':'13px','lineHeight':'1.4','margin':'5px 0'})], className="ct-subcard", style={'flex':'1','background':'#0B1220','borderRadius':'10px','padding':'10px'}),
                    html.Div([html.Img(src='/assets/fbp_filtrado.png', style={'width':'100%','height':'190px','objectFit':'contain'}), html.P('Antes de retroproyectar en FBP, las proyecciones se filtran para compensar ese efecto.', style={'color':'#AEBBD0','fontSize':'13px','lineHeight':'1.4','margin':'5px 0'})], className="ct-subcard", style={'flex':'1','background':'#0B1220','borderRadius':'10px','padding':'10px'}),
                ], style={'display':'flex','gap':'14px','marginTop':'15px'}),
            ])
        ),

        card(
            '5. FBP: filtrado + retroproyección + suma',
            html.Div([
                p('Las diapositivas describen la retroproyección filtrada como un procedimiento de tres pasos: filtrar las proyecciones, retroproyectarlas y sumar las contribuciones. El filtro de rampa aparece en el dominio de frecuencia y compensa el efecto de la retroproyección.'),
                formula('H_Ramp(ω) = |ω|'),
                formula('F₁{pθ}(ω) = F₂{f}(ω cosθ, ω sinθ)   ← Teorema del corte de proyección'),
                formula('f(x,y) ≈ ∫ q(x cosθ + y sinθ, θ) dθ,    q = p * h'),
                html.Div([
                    step(1, 'Filtrar', 'Cada proyección se transforma y se pondera mediante el filtro elegido.'),
                    step(2, 'Retroproyectar', 'La proyección filtrada se distribuye sobre la trayectoria correspondiente.'),
                    step(3, 'Sumar', 'Se acumulan las contribuciones de todas las proyecciones para formar la reconstrucción.'),
                ], className="ct-subcard", style={'background':'#0B1220','border':'1px solid #273449','borderRadius':'10px','padding':'15px'}),
                idea('En nuestro código, `reconstruir_fbp()` utiliza la reconstrucción inversa de Radon de scikit-image y permite seleccionar Ramp, Hamming o Cosine.'),
            ])
        ),
    ]


def block11():
    """Conecta los fundamentos con el módulo de procesamiento que existe en CT-SIM."""
    return [
        section(
            '11',
            'Del sinograma a la imagen procesada',
            'Cómo se relacionan la reconstrucción y el procesamiento de imágenes de nuestro proyecto'
        ),

        card(
            'Reconstrucción tomográfica vs. procesamiento de imagen',
            html.Div([
                html.Div([
                    html.Div([
                        html.H3('SIMULADOR TC', style={'color':MORADO,'fontSize':'20px','margin':'0 0 8px'}),
                        html.P('Su objetivo es reconstruir una imagen a partir de proyecciones.', style={'color':'#D1D5DB','lineHeight':'1.55'}),
                        html.P('Imagen → Radon → Proyecciones → Sinograma → Filtrado → FBP → Imagen reconstruida', style={'color':'#AEBBD0','fontFamily':'monospace','fontSize':'13px','lineHeight':'1.6'}),
                    ], className="ct-subcard", style={'flex':'1','background':'#101A2B','border':'1px solid #273449','borderRadius':'10px','padding':'15px'}),
                    html.Div([
                        html.H3('PROCESAMIENTO', style={'color':CIAN,'fontSize':'20px','margin':'0 0 8px'}),
                        html.P('Su objetivo es modificar, mejorar o analizar una imagen que ya existe.', style={'color':'#D1D5DB','lineHeight':'1.55'}),
                        html.P('Imagen → contraste → gamma → histograma → CLAHE → filtros → segmentación', style={'color':'#AEBBD0','fontFamily':'monospace','fontSize':'13px','lineHeight':'1.6'}),
                    ], className="ct-subcard", style={'flex':'1','background':'#101A2B','border':'1px solid #273449','borderRadius':'10px','padding':'15px'}),
                ], style={'display':'flex','gap':'16px'}),
                html.P('En nuestro proyecto ambos módulos están relacionados: el simulador explica cómo se obtiene/reconstruye la imagen y el módulo de procesamiento permite estudiar qué podemos hacer con esa imagen después de reconstruirla.', style={'color':'#D1D5DB','fontSize':'15px','lineHeight':'1.65','marginTop':'16px'}),
            ])
        ),

        card(
            '¿Qué hace cada filtro de reconstrucción?',
            html.Div([
                html.Div([
                    html.Div([html.H4('Ramp / Ram-Lak',style={'color':MORADO,'margin':'0 0 7px'}),formula('H(ω)=|ω|'),html.P('Es el filtro base de rampa. Da mayor peso a las altas frecuencias y ayuda a recuperar detalle, pero también puede hacer más visible el ruido.',style={'color':'#B8C4D9','lineHeight':'1.5'})], style={'flex':'1'}),
                    html.Div([html.H4('Hamming',style={'color':CIAN,'margin':'0 0 7px'}),formula('H(ω)=|ω|·W_H(ω)'),html.P('Aplica una ventana que atenúa progresivamente las componentes de frecuencia alta. El resultado tiende a ser más suavizado y menos sensible al ruido que Ramp.',style={'color':'#B8C4D9','lineHeight':'1.5'})], style={'flex':'1'}),
                    html.Div([html.H4('Cosine',style={'color':'#C4B5FD','margin':'0 0 7px'}),formula('H(ω)=|ω|·W_C(ω)'),html.P('También utiliza una ventana cosenoidal sobre la rampa, modificando la respuesta en frecuencia y proporcionando un compromiso diferente entre detalle y suavizado.',style={'color':'#B8C4D9','lineHeight':'1.5'})], style={'flex':'1'}),
                ], style={'display':'flex','gap':'14px'}),
                html.Div([
                    html.P('Comparación conceptual',style={'color':BLANCO,'fontWeight':'700','margin':'15px 0 8px'}),
                    html.P('Ramp → más detalle / más ruido potencial   |   Hamming → más suavizado / menos altas frecuencias   |   Cosine → suavizado intermedio según la ventana.',style={'color':'#AEBBD0','fontSize':'14px','lineHeight':'1.55','margin':'0'})
                ], className="ct-subcard", style={'background':'#0B1220','border':'1px solid #273449','borderRadius':'10px','padding':'12px 14px'})
            ])
        ),

        card(
            'Procesamiento posterior de la imagen',
            html.Div([
                p('Una vez obtenida la imagen reconstruida, nuestro módulo de procesamiento permite estudiar otras transformaciones que ya forman parte del proyecto. Estas operaciones no sustituyen la reconstrucción FBP: trabajan sobre la imagen después de obtenerla.'),
                html.Div([
                    process_card(1,'Contraste','proceso_filtrado.png','Modifica la separación visual entre niveles de intensidad para facilitar la observación de estructuras.'),
                    process_card(2,'Gamma','proceso_filtrado.png','Aplica una transformación no lineal de intensidad para modificar la respuesta tonal de la imagen.'),
                    process_card(3,'Histograma / CLAHE','sinograma.png','Permiten analizar y redistribuir intensidades; CLAHE trabaja de manera local para mejorar el contraste.'),
                    process_card(4,'Filtros','filtro_hamming.png','Permiten suavizar, resaltar o modificar componentes de la imagen según el objetivo del procesamiento.'),
                ], style={'display':'flex','gap':'12px'}),
                idea('La separación conceptual es clave: FBP reconstruye a partir de proyecciones; contraste, gamma, CLAHE y filtros de imagen procesan la imagen ya reconstruida.'),
            ])
        ),

        card(
            'Cómo se conecta con nuestro simulador',
            html.Div([
                formula('Imagen → Radon → Sinograma → Filtro de reconstrucción → Retroproyección → Imagen FBP → Procesamiento de imagen'),
                html.P('Esta cadena resume la relación entre los fundamentos matemáticos y los módulos implementados en CT-SIM. El estudiante puede observar los datos intermedios, cambiar parámetros y comparar cómo las decisiones de adquisición o reconstrucción afectan el resultado.', style={'color':'#D1D5DB','fontSize':'15px','lineHeight':'1.65'}),
                html.Div([
                    html.Strong('Fuentes principales utilizadas para esta ampliación', style={'color':CIAN}),
                    html.P('Diapositivas base de Tomografía Computarizada: especialmente diapositivas 5–7 (fundamento y Radon), 35–43 (atenuación, números CT, proyecciones, sinograma y retroproyección) y 57–69 (teorema del corte de proyección, FBP, filtros/ventanas y reconstrucción en tres pasos).', style={'color':'#AEBBD0','fontSize':'13px','lineHeight':'1.55','margin':'6px 0 0'})
                ], style={'background':'rgba(34,211,238,.07)','border':'1px solid rgba(34,211,238,.22)','borderRadius':'10px','padding':'13px 15px','marginTop':'14px'})
            ])
        ),
    ]

_CACHED_LAYOUT_FUNDAMENTOS = None

def layout_fundamentos():
    global _CACHED_LAYOUT_FUNDAMENTOS
    if _CACHED_LAYOUT_FUNDAMENTOS is None:
        bloques = block1() + block2() + block3() + block4() + block5() + block6() + block7() + block8() + block9() + block10() + block11()
        _CACHED_LAYOUT_FUNDAMENTOS = html.Div([
            html.Div([html.Div('FUNDAMENTOS DE TC',style={'display':'inline-block','background':'rgba(139,92,246,.15)','border':'1px solid rgba(139,92,246,.45)','color':'#C4B5FD','padding':'6px 12px','borderRadius':'20px','fontSize':'12px','fontWeight':'700','letterSpacing':'1px'}),html.H1('Fundamentos de Tomografía Computarizada',style={'color':BLANCO,'fontSize':'38px','fontWeight':'800','marginBottom':'12px'}),html.P('Comprende cómo una medición de rayos X se transforma en proyecciones, sinograma y finalmente en una imagen reconstruida.',style={'color':'#CBD5E1','fontSize':'17px','lineHeight':'1.7','maxWidth':'850px'})],style={'background':'linear-gradient(135deg,#111827,#17152B,#111827)','border':f'1px solid rgba(139,92,246,.35)','borderRadius':'20px','padding':'35px','marginBottom':'30px'}),
            html.Div([
                html.H3([html.I(className='fa-solid fa-book', style={'marginRight': '8px'}), 'Contenido'], className="ct-index-title", style={'fontSize': '20px', 'fontWeight': '700', 'margin': '0 0 14px 0'}),
                html.Div([
                    dcc.Link(
                        f'{n}. {t}',
                        href=f'#fund-{n}',
                        className="ct-index-link",
                        style={'textDecoration':'none','padding':'8px 14px','borderRadius':'8px','fontSize':'13px','fontWeight':'600'}
                    ) for n,t in [(1,'Introducción'),(2,'Proyecciones'),(3,'Radon'),(4,'Sinograma'),(5,'Retroproyección'),(6,'FBP'),(7,'Filtros'),(8,'Haz de abanico'),(9,'Resumen'),(10,'Fórmulas y modelo matemático'),(11,'Procesamiento en CT-SIM')]
                ], style={'display':'flex','flexWrap':'wrap','gap':'8px'})
            ], className="ct-index-card", style={'borderRadius':'14px','padding':'18px 20px','marginBottom':'30px'}),
            *[html.Div(block, id=f'fund-{i}') for i,block in enumerate(bloques,1)]
        ], style={'background':NEGRO,'minHeight':'100vh','padding':'30px 5%','color':BLANCO,'fontFamily':'Arial,sans-serif'})
    return _CACHED_LAYOUT_FUNDAMENTOS

if __name__=='__main__':
    from dash import Dash
    app=Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout=layout_fundamentos()
    app.run(debug=False)