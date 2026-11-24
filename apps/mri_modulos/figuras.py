"""
apps/mri_modulos/figuras.py
===========================
Generación de gráficos Plotly con el tema oscuro de Prometeo.
Fondo #0a0f1d / #111827, tipografía Inter y acentos cyan, púrpura y ámbar.
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import THEME

FONDO = "rgba(0,0,0,0)"
PANEL = THEME["card"]
REJILLA = "rgba(148,163,184,0.12)"
TEXTO = THEME["text"]
TENUE = THEME["text_muted"]
ACENTO = THEME["accent_cyan"]
PURPURA = THEME["accent_purple"]
AMBAR = THEME["accent_amber"]
VERDE = THEME["accent_emerald"]
FUENTE = '"Inter", "Segoe UI", -apple-system, sans-serif'


def estilo(fig, alto=None, margen=None, leyenda=True):
    fig.update_layout(
        paper_bgcolor=FONDO,
        plot_bgcolor=FONDO,
        font=dict(family=FUENTE, color=TEXTO, size=12),
        margin=margen or dict(l=50, r=16, t=36, b=38),
        hoverlabel=dict(bgcolor="#0f172a", bordercolor="#334155", font=dict(family=FUENTE, color="#f8fafc")),
        showlegend=leyenda,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11), orientation="h", yanchor="bottom", y=1.02, x=0),
        uirevision="fija",
    )
    if alto:
        fig.update_layout(height=alto)
    fig.update_xaxes(gridcolor=REJILLA, zerolinecolor=REJILLA, linecolor="#1e293b", tickfont=dict(family=FUENTE, size=10, color=TENUE))
    fig.update_yaxes(gridcolor=REJILLA, zerolinecolor=REJILLA, linecolor="#1e293b", tickfont=dict(family=FUENTE, size=10, color=TENUE))
    for a in fig.layout.annotations or []:
        a.font = dict(family=FUENTE, color=TEXTO, size=13)
    return fig


def vacia(mensaje="Sin datos disponibles", alto=420):
    fig = go.Figure()
    fig.add_annotation(
        text=mensaje, x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False,
        font=dict(size=14, color=TENUE, family=FUENTE)
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return estilo(fig, alto, leyenda=False)


def _heat(img, escala="gray", zmin=0, zmax=1, nombre="", mostrar_escala=False):
    return go.Heatmap(
        z=img, colorscale=escala, zmin=zmin, zmax=zmax, showscale=mostrar_escala, name=nombre,
        hovertemplate="x: %{x}<br>y: %{y}<br>I: %{z:.3f}<extra></extra>",
        colorbar=dict(thickness=10, len=0.8, outlinewidth=0, tickfont=dict(size=10, color=TEXTO))
    )


def _ejes_imagen(fig, filas_cols, aspecto=1.0, zoom=1.0, forma=None):
    for (r, c, n) in filas_cols:
        sufijo = "" if n == 1 else str(n)
        fig.update_xaxes(visible=False, constrain="domain", row=r, col=c)
        fig.update_yaxes(visible=False, autorange="reversed", scaleanchor=f"x{sufijo}", scaleratio=aspecto,
                         constrain="domain", row=r, col=c)


def imagen(img, titulo="", escala="gray", aspecto=1.0, alto=460, zmin=0, zmax=1, mostrar_escala=False):
    fig = go.Figure(_heat(img, escala, zmin, zmax, mostrar_escala=mostrar_escala))
    fig.update_xaxes(visible=False, constrain="domain")
    fig.update_yaxes(visible=False, autorange="reversed", scaleanchor="x", scaleratio=aspecto, constrain="domain")
    fig.update_layout(title=dict(text=titulo, x=0.01, font=dict(size=13, color=TEXTO)))
    return estilo(fig, alto, leyenda=False)


def comparacion(original, procesada, t1="Original", t2="Procesada", aspecto=1.0, alto=420, escala2="gray"):
    fig = make_subplots(rows=1, cols=2, subplot_titles=(t1, t2), horizontal_spacing=0.02)
    fig.add_trace(_heat(original, "gray"), 1, 1)
    fig.add_trace(_heat(procesada, escala2), 1, 2)
    _ejes_imagen(fig, [(1, 1, 1), (1, 2, 2)], aspecto)
    return estilo(fig, alto, leyenda=False, margen=dict(l=4, r=4, t=44, b=4))


def cuadruple(imgs, titulos, aspecto=1.0, escalas=("gray", "gray", "gray", "gray"), alto=340):
    fig = make_subplots(rows=1, cols=4, subplot_titles=titulos, horizontal_spacing=0.015)
    for i, (img, esc) in enumerate(zip(imgs, escalas), 1):
        fig.add_trace(_heat(img, esc), 1, i)
    _ejes_imagen(fig, [(1, 1, 1), (1, 2, 2), (1, 3, 3), (1, 4, 4)], aspecto)
    return estilo(fig, alto, leyenda=False, margen=dict(l=4, r=4, t=44, b=4))


def bloch_3d(M, titulo="Vector de magnetización (marco rotatorio)", alto=460):
    fig = go.Figure()
    u, v = np.mgrid[0:2 * np.pi:28j, 0:np.pi:14j]
    xs, ys, zs = np.cos(u) * np.sin(v), np.sin(u) * np.sin(v), np.cos(v)
    fig.add_trace(go.Surface(x=xs, y=ys, z=zs, opacity=0.06, showscale=False,
                             colorscale=[[0, "#334155"], [1, "#334155"]], hoverinfo="skip"))
    
    for eje, col, lab in (((1.25, 0, 0), "#f87171", "x'"), ((0, 1.25, 0), "#34d399", "y'"), ((0, 0, 1.25), PURPURA, "z (B₀)")):
        fig.add_trace(go.Scatter3d(x=[0, eje[0]], y=[0, eje[1]], z=[0, eje[2]], mode="lines+text", text=["", lab],
                                   line=dict(color=col, width=4), textfont=dict(color=col, size=13), hoverinfo="skip",
                                   showlegend=False))
    n = len(M)
    fig.add_trace(go.Scatter3d(x=M[:, 0], y=M[:, 1], z=M[:, 2], mode="lines",
                               line=dict(color=np.linspace(0, 1, n), colorscale="Plasma", width=5),
                               name="Trayectoria de M", hoverinfo="skip"))
    f = M[-1]
    fig.add_trace(go.Scatter3d(x=[0, f[0]], y=[0, f[1]], z=[0, f[2]], mode="lines", line=dict(color=ACENTO, width=9),
                               name="M(t final)"))
    fig.add_trace(go.Cone(x=[f[0]], y=[f[1]], z=[f[2]], u=[f[0] * 0.25], v=[f[1] * 0.25], w=[f[2] * 0.25],
                          colorscale=[[0, ACENTO], [1, ACENTO]], showscale=False, sizemode="absolute", sizeref=0.18))
    eje = dict(range=[-1.3, 1.3], showbackground=False, gridcolor=REJILLA, zerolinecolor=REJILLA, showticklabels=False, title="")
    fig.update_layout(scene=dict(xaxis=eje, yaxis=eje, zaxis=eje, aspectmode="cube",
                                 camera=dict(eye=dict(x=1.5, y=1.3, z=0.9))),
                      title=dict(text=titulo, x=0.01, font=dict(size=13, color=TEXTO)))
    return estilo(fig, alto, leyenda=False, margen=dict(l=0, r=0, t=34, b=0))


def series(t, ys: dict, titulo="", xlab="t [ms]", ylab="", alto=280, lineas_v=None, rango_y=None):
    fig = go.Figure()
    for nombre, (y, color) in ys.items():
        fig.add_trace(go.Scatter(x=t, y=y, name=nombre, line=dict(color=color, width=2.2)))
    for (x, txt, col) in (lineas_v or []):
        fig.add_vline(x=x, line=dict(color=col, width=1.4, dash="dash"), annotation_text=txt,
                      annotation_font=dict(color=col, size=11), annotation_position="top")
    fig.update_xaxes(
        title=dict(text=xlab, font=dict(family=FUENTE, size=11, color=TEXTO)),
        showticklabels=True,
        tickfont=dict(family=FUENTE, size=10, color=TENUE),
        showgrid=True,
        gridcolor=REJILLA,
        zeroline=True,
        zerolinecolor=REJILLA,
    )
    fig.update_yaxes(
        title=dict(text=ylab, font=dict(family=FUENTE, size=11, color=TEXTO)),
        showticklabels=True,
        tickfont=dict(family=FUENTE, size=10, color=TENUE),
        showgrid=True,
        gridcolor=REJILLA,
        zeroline=True,
        zerolinecolor=REJILLA,
    )
    if rango_y:
        fig.update_yaxes(range=rango_y)
    fig.update_layout(title=dict(text=titulo, x=0.01, font=dict(size=12, color=TEXTO)))
    return estilo(fig, alto, margen=dict(l=54, r=18, t=36, b=42))


def barras(nombres, valores, colores, titulo="", alto=240, ylab=""):
    fig = go.Figure(go.Bar(x=nombres, y=valores, marker_color=colores, text=[f"{v:.2f}" for v in valores],
                           textposition="outside", textfont=dict(size=11, color=TEXTO)))
    fig.update_xaxes(
        showticklabels=True,
        tickfont=dict(family=FUENTE, size=11, color=TEXTO),
        showgrid=False,
    )
    fig.update_yaxes(
        title=dict(text=ylab, font=dict(family=FUENTE, size=11, color=TEXTO)),
        showticklabels=True,
        tickfont=dict(family=FUENTE, size=10, color=TENUE),
        showgrid=True,
        gridcolor=REJILLA,
        range=[0, max(max(valores) * 1.25, 0.05)],
    )
    fig.update_layout(title=dict(text=titulo, x=0.01, font=dict(size=12, color=TEXTO)))
    return estilo(fig, alto, leyenda=False, margen=dict(l=52, r=16, t=36, b=36))


def _rgba(hexcol, a):
    h = hexcol.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})"


def diagrama_secuencia(canales, notas, fin, titulo="Diagrama de la secuencia", alto=440):
    nombres = ["RF", "Gss", "Gpe", "Gro", "Señal"]
    etiquetas = {"RF": "RF", "Gss": "G corte (z)", "Gpe": "G fase (y)", "Gro": "G lectura (x)", "Señal": "Señal / ADC"}
    colores = {"RF": "#ec4899", "Gss": PURPURA, "Gpe": VERDE, "Gro": AMBAR, "Señal": ACENTO}
    fig = make_subplots(rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.03)
    for i, n in enumerate(nombres, 1):
        fig.add_trace(go.Scatter(x=[0, fin], y=[0, 0], line=dict(color="#334155", width=1), hoverinfo="skip"), i, 1)
        for (t, y) in canales.get(n, []):
            extra = dict(fill="tozeroy", fillcolor=_rgba(colores[n], 0.18)) if n != "Señal" else {}
            fig.add_trace(go.Scatter(x=t, y=y, line=dict(color=colores[n], width=1.8), hoverinfo="skip", **extra), i, 1)
        fig.update_yaxes(title_text=etiquetas[n], title_font=dict(size=10, color=colores[n]), showticklabels=False,
                         range=[-1.15, 1.25], showgrid=False, zeroline=False, row=i, col=1)
    for (t, canal, txt) in notas:
        fila = nombres.index(canal) + 1
        fig.add_annotation(x=t, y=1.15, text=txt, showarrow=False, font=dict(size=11, color="#f8fafc"), row=fila, col=1)
    fig.update_xaxes(title_text="tiempo [ms]", row=5, col=1)
    fig.update_xaxes(showgrid=False)
    fig.update_layout(title=dict(text=titulo, x=0.01, font=dict(size=13, color=TEXTO)))
    return estilo(fig, alto, leyenda=False, margen=dict(l=10, r=10, t=36, b=10))


def polar_fases(fotos: dict, alto=280):
    fig = make_subplots(rows=1, cols=len(fotos), specs=[[{"type": "polar"}] * len(fotos)],
                        subplot_titles=[f"t = {t:g} ms" for t in fotos])
    for i, (t, fases) in enumerate(fotos.items(), 1):
        th = np.degrees(fases[::4])
        fig.add_trace(go.Scatterpolar(r=np.ones_like(th), theta=th, mode="markers",
                                      marker=dict(size=5, color=th, colorscale="Turbo"), hoverinfo="skip"), 1, i)
        neto = np.abs(np.mean(np.exp(1j * fases)))
        ang = np.degrees(np.angle(np.mean(np.exp(1j * fases))))
        fig.add_trace(go.Scatterpolar(r=[0, neto], theta=[ang, ang], mode="lines", line=dict(color=ACENTO, width=4),
                                      hoverinfo="skip"), 1, i)
    pol = dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=False, range=[0, 1.1]),
               angularaxis=dict(showticklabels=False, gridcolor=REJILLA, linecolor="#334155"))
    fig.update_layout(**{f"polar{'' if i == 1 else i}": pol for i in range(1, len(fotos) + 1)})
    return estilo(fig, alto, leyenda=False, margen=dict(l=10, r=10, t=36, b=10))

