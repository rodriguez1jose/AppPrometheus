"""
apps/mri_modulos/fantoma.py
===================================================
FANTOMA DIGITAL DE CABEZA PARA RESONANCIA MAGNÉTICA
===================================================
Adaptado para Prometeo. Genera modelos anatómicos y sintetiza
imágenes de MRI con ecuaciones de señal reales (SE, GRE, IR, FLAIR, STIR, DWI).
"""

from __future__ import annotations

import os
from functools import lru_cache
import numpy as np
import scipy.ndimage as ndi

TEJIDOS = {
    0:  dict(nombre="Aire / fondo",          pd=0.00, t1=1.0,   t2=1.0,   t2s=1.0,  adc=0.0,  t1c=1.0),
    1:  dict(nombre="LCR",                   pd=1.00, t1=4000., t2=2000., t2s=1500., adc=3.0, t1c=4000.),
    2:  dict(nombre="Sustancia gris",        pd=0.82, t1=1000., t2=100.,  t2s=70.,  adc=0.80, t1c=950.),
    3:  dict(nombre="Sustancia blanca",      pd=0.70, t1=650.,  t2=80.,   t2s=60.,  adc=0.70, t1c=630.),
    4:  dict(nombre="Grasa",                 pd=0.90, t1=260.,  t2=80.,   t2s=60.,  adc=0.02, t1c=260.),
    5:  dict(nombre="Músculo / piel",        pd=0.75, t1=900.,  t2=45.,   t2s=30.,  adc=1.40, t1c=700.),
    6:  dict(nombre="Hueso cortical",        pd=0.04, t1=1000., t2=1.5,   t2s=1.0,  adc=0.0,  t1c=1000.),
    7:  dict(nombre="Médula ósea (diploe)",  pd=0.85, t1=320.,  t2=70.,   t2s=40.,  adc=0.30, t1c=300.),
    8:  dict(nombre="Humor vítreo",          pd=1.00, t1=3800., t2=1800., t2s=1200., adc=2.8, t1c=3800.),
    9:  dict(nombre="Núcleos grises",        pd=0.80, t1=900.,  t2=90.,   t2s=55.,  adc=0.75, t1c=880.),
    10: dict(nombre="Edema vasogénico",      pd=0.90, t1=1150., t2=190.,  t2s=120., adc=1.60, t1c=1100.),
    11: dict(nombre="Tumor (realce)",        pd=0.86, t1=1200., t2=140.,  t2s=90.,  adc=0.60, t1c=380.),
    12: dict(nombre="Necrosis",              pd=0.95, t1=2500., t2=600.,  t2s=400., adc=2.40, t1c=2500.),
    13: dict(nombre="Placa desmielinizante", pd=0.86, t1=1050., t2=170.,  t2s=100., adc=1.10, t1c=1000.),
    14: dict(nombre="Infarto agudo",         pd=0.88, t1=900.,  t2=115.,  t2s=80.,  adc=0.35, t1c=900.),
    15: dict(nombre="Vasos (flujo)",         pd=0.10, t1=1400., t2=180.,  t2s=50.,  adc=0.0,  t1c=300.),
}

ESCENARIOS = {
    "sano":    "Cerebro normal",
    "tumor":   "Glioma de alto grado (sintético)",
    "em":      "Esclerosis múltiple (sintético)",
    "ictus":   "Ictus isquémico agudo (sintético)",
    "atrofia": "Atrofia / hidrocefalia ex-vacuo (sintético)",
}

SECUENCIAS = {
    "T1":    dict(tipo="SE",  TR=500.,  TE=12.,  desc="T1 Spin Echo"),
    "T1C":   dict(tipo="SE",  TR=500.,  TE=12.,  desc="T1 post-gadolinio", contraste=True),
    "T2":    dict(tipo="SE",  TR=4000., TE=100., desc="T2 Spin Echo"),
    "PD":    dict(tipo="SE",  TR=3000., TE=15.,  desc="Densidad protónica"),
    "FLAIR": dict(tipo="IR",  TR=9000., TE=120., TI=2400., desc="T2-FLAIR"),
    "STIR":  dict(tipo="IR",  TR=4000., TE=40.,  TI=160.,  desc="STIR"),
    "GRE":   dict(tipo="GRE", TR=30.,   TE=20.,  alpha=20., desc="T2* Gradient Echo"),
    "DWI":   dict(tipo="DWI", TR=5000., TE=90.,  b=1000.,  desc="Difusión b=1000"),
    "ADC":   dict(tipo="ADC", desc="Mapa ADC"),
}

FORMA = (160, 192, 144)   # (x, y, z)
VOXEL_MM = 1.2


def _rejilla(forma=FORMA, voxel=VOXEL_MM):
    nx, ny, nz = forma
    x = (np.arange(nx, dtype=np.float32) - nx / 2) * voxel
    y = (np.arange(ny, dtype=np.float32) - ny / 2) * voxel
    z = (np.arange(nz, dtype=np.float32) - nz / 2 + 14) * voxel
    return x[:, None, None], y[None, :, None], z[None, None, :]


def _elipsoide(X, Y, Z, c, r):
    return ((X - c[0]) / r[0]) ** 2 + ((Y - c[1]) / r[1]) ** 2 + ((Z - c[2]) / r[2]) ** 2 <= 1.0


def _capsula(X, Y, Z, p0, p1, radio):
    p0 = np.asarray(p0, np.float32)
    p1 = np.asarray(p1, np.float32)
    d = p1 - p0
    L2 = float(d @ d) + 1e-6
    t = ((X - p0[0]) * d[0] + (Y - p0[1]) * d[1] + (Z - p0[2]) * d[2]) / L2
    t = np.clip(t, 0, 1)
    dx = X - (p0[0] + t * d[0])
    dy = Y - (p0[1] + t * d[1])
    dz = Z - (p0[2] + t * d[2])
    return dx * dx + dy * dy + dz * dz <= radio * radio


def _ruido_suave(forma, sigma, semilla):
    rng = np.random.default_rng(semilla)
    n = ndi.gaussian_filter(rng.standard_normal(forma).astype(np.float32), sigma)
    return n / (n.std() + 1e-8)


def generar_etiquetas(escenario: str = "sano", semilla: int = 7) -> np.ndarray:
    X, Y, Z = _rejilla()
    forma = FORMA
    atrofia = escenario == "atrofia"

    pert = _ruido_suave(forma, 10, semilla) * 1.5
    cabeza = _elipsoide(X, Y, Z, (0, 0, 0), (74, 96, 90))
    cuello = ((X / 52) ** 2 + ((Y + 10) / 58) ** 2 <= 1) & (Z < -40)
    cara = _elipsoide(X, Y, Z, (0, 30, -45), (60, 70, 40))
    cabeza = ndi.binary_closing(cabeza | cuello | cara, iterations=2)
    d_cab = ndi.distance_transform_edt(cabeza, sampling=VOXEL_MM).astype(np.float32) + pert

    lab = np.zeros(forma, np.uint8)
    lab[cabeza] = 5
    lab[cabeza & (d_cab > 1.5)] = 4
    lab[cabeza & (d_cab > 5.5)] = 6
    lab[cabeza & (d_cab > 7.5)] = 7
    lab[cabeza & (d_cab > 10.0)] = 6
    lab[cabeza & (d_cab > 11.5)] = 1

    X2, Y2 = X[:, :, 0], Y[:, :, 0]
    ax_ = np.abs(X2)
    temporal = 1 / (1 + np.exp(-(ax_ - 26) / 3.0)) * np.exp(-((Y2 - 2) / 30.0) ** 4)
    frontal = 1 / (1 + np.exp(-(Y2 - 38) / 5.0))
    zbase2 = -22.0 - 14.0 * temporal + 8.0 * frontal
    zbase = ndi.gaussian_filter(zbase2.astype(np.float32), 3)[..., None]
    bajo_base = (Z < zbase) & (d_cab > 11.5)
    lab[bajo_base & (lab == 1)] = 5
    hueso_base = (Z < zbase) & (Z > zbase - 3.5) & (d_cab > 10)
    lab[hueso_base] = 6

    lab[_elipsoide(X, Y, Z, (0, 22, zbase.mean() - 14), (16, 13, 9))] = 0
    lab[_elipsoide(X, Y, Z, (0, 30, -62), (14, 18, 10)) & cabeza] = 0
    for zc in np.arange(-48, -100, -14):
        lab[_elipsoide(X, Y, Z, (0, -22, zc), (11, 10, 5.5))] = 7
        lab[_elipsoide(X, Y, Z, (0, -22, zc), (11.8, 10.8, 6.2)) & (lab != 7)] = 6
    lab[_elipsoide(X, Y, Z, (0, 8, -78), (24, 30, 14)) & cabeza] = 5

    cerebro = (d_cab > (14.5 if atrofia else 13.0)) & (Z >= zbase + 1)
    cerebro &= ~_elipsoide(X, Y, Z, (0, -52, -34), (54, 34, 26))
    d_cer = ndi.distance_transform_edt(cerebro, sampling=VOXEL_MM).astype(np.float32)

    N = _ruido_suave(forma, 2.9, semilla + 1)
    ancho_surco = 0.24 if atrofia else 0.12
    surcos = cerebro & (np.abs(N) < ancho_surco) & (d_cer < 17)
    fisura = cerebro & (np.abs(X) < (2.2 if atrofia else 1.3)) & (Z > 20) & (d_cer < 45)
    silvio = cerebro & (np.abs(np.abs(X) - 52 + 0.15 * Z) < 1.5) & (Z > -18) & (Z < 12) & (Y > -20) & (Y < 35)
    lcr_cortical = surcos | fisura | silvio
    parenquima = cerebro & ~lcr_cortical
    d_lcr = ndi.distance_transform_edt(parenquima, sampling=VOXEL_MM).astype(np.float32)
    grosor = 3.3 + 0.5 * _ruido_suave(forma, 6, semilla + 2)
    lab[cerebro] = 1
    lab[parenquima] = 3
    lab[parenquima & (d_lcr < grosor)] = 2

    for s in (-1, 1):
        lab[_elipsoide(X, Y, Z, (s * 11, -8, 4), (8, 13, 8))] = 9
        lab[_elipsoide(X, Y, Z, (s * 24, 6, 2), (5, 15, 9))] = 9
        lab[_elipsoide(X, Y, Z, (s * 16, 19, 11), (5, 8, 7))] = 9

    k = 1.75 if atrofia else 1.0
    vent = np.zeros(forma, bool)
    for s in (-1, 1):
        puntos = [(s * 12, 26, 9), (s * 13, 6, 16), (s * 15, -14, 16), (s * 22, -32, 10), (s * 20, -50, 4)]
        radios = [5.0, 4.4, 4.0, 5.6, 3.0]
        for p0, p1, r in zip(puntos[:-1], puntos[1:], radios):
            vent |= _capsula(X, Y, Z, p0, p1, r * k)
        vent |= _capsula(X, Y, Z, (s * 22, -32, 10), (s * 30, -12, -8), 3.2 * k)
        vent |= _capsula(X, Y, Z, (s * 30, -12, -8), (s * 32, 8, -14), 2.5 * k)
    vent &= ~(np.abs(X) < 1.2)
    vent |= (np.abs(X) < 2.2 * k) & (Y > -12) & (Y < 14) & (Z > -8) & (Z < 6)
    vent |= _elipsoide(X, Y, Z, (0, -38, -30), (4 * k, 4, 6))
    lab[vent] = 1

    cereb = _elipsoide(X, Y, Z, (0, -52, -34), (50, 30, 22)) & (d_cab > 12)
    d_cb = ndi.distance_transform_edt(cereb, sampling=VOXEL_MM).astype(np.float32)
    folia = np.abs(_ruido_suave(forma, 1.6, semilla + 3)) > 0.35
    lab[cereb] = 3
    lab[cereb & ((d_cb < 3) | (folia & (d_cb < 14)))] = 2
    lab[cereb & ((d_cb < 0.9) | (np.abs(X) < 0.9) & (Z > -25))] = 1
    tronco = _capsula(X, Y, Z, (0, -18, -6), (0, -28, -80), 12)
    lab[tronco & (d_cab > 11)] = 3
    lab[_capsula(X, Y, Z, (0, -18, -6), (0, -28, -80), 15) & ~tronco & (d_cab > 11) & (Z < -10)] = 1
    lab[_elipsoide(X, Y, Z, (0, -38, -30), (4 * k, 4, 6))] = 1

    for s in (-1, 1):
        orb = _elipsoide(X, Y, Z, (s * 31, 70, -26), (17, 20, 15))
        lab[orb & cabeza] = 4
        lab[_elipsoide(X, Y, Z, (s * 31, 76, -26), (11.5, 11.5, 11.5))] = 8
        lab[_capsula(X, Y, Z, (s * 31, 66, -26), (s * 12, 40, -20), 2.0)] = 3
    lab[_elipsoide(X, Y, Z, (0, 66, -46), (14, 20, 16))] = 0
    lab[_elipsoide(X, Y, Z, (0, 56, 8), (8, 9, 12)) & cabeza & (d_cab > 3) & (d_cab < 15)] = 0
    for s in (-1, 1):
        lab[_capsula(X, Y, Z, (s * 16, 18, -30), (s * 18, 22, -60), 2.6)] = 15
    lab[_capsula(X, Y, Z, (0, -86, 40), (0, -60, -20), 2.2) & (lab == 1)] = 15

    rng = np.random.default_rng(semilla + 99)
    if escenario == "tumor":
        lab = _efecto_masa(lab, centro=(34, 14, 22), fuerza=7.0)
        c = (34, 14, 22)
        r = np.sqrt((X - c[0]) ** 2 + ((Y - c[1]) / 1.1) ** 2 + ((Z - c[2]) / 0.95) ** 2)
        rr = r + 2.0 * _ruido_suave(forma, 3, semilla + 5)
        cerebral = np.isin(lab, (2, 3, 9))
        lab[cerebral & (rr < 26) & (lab == 3)] = 10
        lab[cerebral & (rr < 21)] = 10
        lab[np.isin(lab, (2, 3, 9, 10, 1)) & (rr < 13)] = 11
        lab[rr < 8] = 12
    elif escenario == "em":
        n = 0
        while n < 16:
            s = rng.choice((-1, 1))
            p = (s * rng.uniform(14, 30), rng.uniform(-40, 30), rng.uniform(4, 30))
            a = rng.uniform(2.0, 4.8)
            elip = _elipsoide(X, Y, Z, p, (a, a * 1.1, a * 1.8))
            if (lab[elip] == 3).mean() > 0.6:
                lab[elip & np.isin(lab, (2, 3))] = 13
                n += 1
        for _ in range(3):
            s = rng.choice((-1, 1))
            p = (s * rng.uniform(40, 55), rng.uniform(-30, 30), rng.uniform(20, 45))
            lab[_elipsoide(X, Y, Z, p, (2.5, 2.5, 3)) & np.isin(lab, (2, 3))] = 13
    elif escenario == "ictus":
        borde = _ruido_suave(forma, 5, semilla + 7) * 6.0
        r_t = np.sqrt((X + 62) ** 2 + ((Y - 2) / 1.25) ** 2 + ((Z - 8) / 1.15) ** 2) + borde
        cuna = (r_t < 36) & (X < -14)
        lab[cuna & np.isin(lab, (2, 3, 9))] = 14

    return lab


def _efecto_masa(lab, centro, fuerza):
    X, Y, Z = _rejilla()
    dx, dy, dz = X - centro[0], Y - centro[1], Z - centro[2]
    r = np.sqrt(dx ** 2 + dy ** 2 + dz ** 2) + 1e-3
    desplaz = fuerza * np.exp(-((r - 10) / 30.0) ** 2)
    ix = np.arange(lab.shape[0])[:, None, None] - desplaz * dx / r / VOXEL_MM
    iy = np.arange(lab.shape[1])[None, :, None] - desplaz * dy / r / VOXEL_MM
    iz = np.arange(lab.shape[2])[None, None, :] - desplaz * dz / r / VOXEL_MM
    ix, iy, iz = np.broadcast_arrays(ix, iy, iz)
    cerebral = np.isin(lab, (1, 2, 3, 9))
    nuevo = ndi.map_coordinates(lab, [ix, iy, iz], order=0, mode="nearest")
    return np.where(cerebral & np.isin(nuevo, (1, 2, 3, 9)), nuevo, lab).astype(np.uint8)


def mapas_parametricos(lab: np.ndarray, contraste: bool = False) -> dict:
    n = max(TEJIDOS) + 1
    tabla = {k: np.zeros(n, np.float32) for k in ("pd", "t1", "t2", "t2s", "adc")}
    for i, p in TEJIDOS.items():
        tabla["pd"][i] = p["pd"]
        tabla["t1"][i] = p["t1c"] if contraste else p["t1"]
        tabla["t2"][i] = p["t2"]
        tabla["t2s"][i] = p["t2s"]
        tabla["adc"][i] = p["adc"]
    return {k: v[lab] for k, v in tabla.items()}


def senal_spin_echo(pd, t1, t2, TR, TE):
    return pd * (1 - np.exp(-TR / t1)) * np.exp(-TE / t2)


def senal_gradient_echo(pd, t1, t2s, TR, TE, alpha_deg):
    a = np.deg2rad(alpha_deg)
    E1 = np.exp(-TR / t1)
    return pd * np.sin(a) * (1 - E1) / (1 - np.cos(a) * E1) * np.exp(-TE / t2s)


def senal_inversion_recovery(pd, t1, t2, TR, TE, TI):
    return pd * np.abs(1 - 2 * np.exp(-TI / t1) + np.exp(-TR / t1)) * np.exp(-TE / t2)


def senal_difusion(pd, t1, t2, adc, TR, TE, b):
    return senal_spin_echo(pd, t1, t2, TR, TE) * np.exp(-b * adc * 1e-3)


def sintetizar(mapas: dict, secuencia: str = "T1", params: dict | None = None,
               ruido: float = 0.012, sesgo: float = 0.08, semilla: int = 3) -> np.ndarray:
    p = dict(SECUENCIAS.get(secuencia, SECUENCIAS["T1"]))
    if params:
        p.update(params)
    pd, t1, t2, t2s, adc = (mapas[k] for k in ("pd", "t1", "t2", "t2s", "adc"))
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        t = p["tipo"]
        if t == "SE":
            s = senal_spin_echo(pd, t1, t2, p["TR"], p["TE"])
        elif t == "GRE":
            s = senal_gradient_echo(pd, t1, t2s, p["TR"], p["TE"], p.get("alpha", 30))
        elif t == "IR":
            s = senal_inversion_recovery(pd, t1, t2, p["TR"], p["TE"], p["TI"])
        elif t == "DWI":
            s = senal_difusion(pd, t1, t2, adc, p["TR"], p["TE"], p.get("b", 1000))
        elif t == "ADC":
            s = adc / 3.2 * (pd > 0.05)
        else:
            s = pd
    s = np.nan_to_num(s).astype(np.float32)
    s = ndi.gaussian_filter(s, 0.55)
    escala = np.percentile(s[s > 0], 99.5) if np.any(s > 0) else 1.0
    s /= (escala + 1e-8)
    rng = np.random.default_rng(semilla)
    if sesgo > 0:
        campo = 1 + sesgo * _ruido_suave(s.shape if s.ndim == 3 else s.shape, 25, semilla + 11).clip(-2, 2)
        s *= campo
    if ruido > 0:
        n1 = rng.normal(0, ruido, s.shape).astype(np.float32)
        n2 = rng.normal(0, ruido, s.shape).astype(np.float32)
        s = np.sqrt((s + n1) ** 2 + n2 ** 2)
    return s.astype(np.float32)


_CACHE_LAB: dict = {}


def etiquetas_cache(escenario: str = "sano") -> np.ndarray:
    if escenario in _CACHE_LAB:
        return _CACHE_LAB[escenario]
    
    # Intento 1: Directorio local en appPrometheo/data/mri
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ruta1 = os.path.join(base_dir, "data", "mri", f"etiquetas_{escenario}.npz")
    
    lab = None
    for r in [ruta1]:
        if os.path.exists(r):
            try:
                npz = np.load(r)
                if "lab" in npz:
                    lab = npz["lab"]
                elif "arr_0" in npz:
                    lab = npz["arr_0"]
                if lab is not None and lab.shape == FORMA:
                    break
                lab = None
            except Exception:
                lab = None

    if lab is None:
        lab = generar_etiquetas(escenario)
        try:
            os.makedirs(os.path.dirname(ruta1), exist_ok=True)
            np.savez_compressed(ruta1, lab=lab)
        except Exception:
            pass

    _CACHE_LAB[escenario] = lab
    return lab


@lru_cache(maxsize=16)
def _corte_axial_parametros_cached(escenario="sano", z_idx=None):
    lab = etiquetas_cache(escenario)
    if z_idx is None:
        z_idx = int(lab.shape[2] * 0.47)
    lab2 = np.rot90(lab[:, :, z_idx])
    return lab2, mapas_parametricos(lab2)


def corte_axial_parametros(escenario="sano", z_idx=None):
    lab2, mapas = _corte_axial_parametros_cached(escenario, z_idx)
    return lab2.copy(), {k: v.copy() for k, v in mapas.items()}


def volumen_ejemplo(escenario="sano", secuencia="T1") -> np.ndarray:
    lab = etiquetas_cache(escenario)
    mapas = mapas_parametricos(lab, contraste=SECUENCIAS.get(secuencia, {}).get("contraste", False))
    return sintetizar(mapas, secuencia)

