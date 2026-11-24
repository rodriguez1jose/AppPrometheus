"""
apps/mri_modulos/simulador_fisico.py
====================================
SIMULADOR FÍSICO DE RESONANCIA MAGNÉTICA
========================================
- Ecuaciones de Bloch para un vector y conjunto de isocromatas (T2*, SE, GRE).
- Curvas de relajación T1/T2 y diferenciación tisular.
- Dominio de espacio K: FFT2/iFFT2, muestreos, artefactos y filtrado.
- Diagramas temporales de secuencias de pulso (SE, GRE, IR, EPI, DWI).
- Calculadoras de física de RM.
"""

from __future__ import annotations

import numpy as np

GAMMA_BAR = 42.577478  # MHz/T
GAMMA = 2 * np.pi * GAMMA_BAR * 1e6  # rad/s/T
HBAR = 1.054571817e-34
KB = 1.380649e-23
EPS = 1e-8


# ---------------------------------------------------------------------------
# 1. BLOCH Y ROTACIONES
# ---------------------------------------------------------------------------

def _rot_x(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, s], [0, -s, c]])


def _rot_y(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]])


def _rot_z(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])


def bloch_vector(T1=800., T2=80., flip=90., df=5.0, duracion=None, n=600, pasos_excitacion=40):
    """
    Simula un único vector M en el marco rotatorio (optimizado con preasignación).
    df: desplazamiento de frecuencia respecto a la resonancia [Hz].
    Devuelve t [ms], M (n,3).
    """
    if duracion is None:
        duracion = max(3 * T1, 5 * T2)
    M = np.array([0.0, 0.0, 1.0], dtype=np.float64)
    tray = np.empty((pasos_excitacion, 3), dtype=np.float64)
    paso = np.deg2rad(flip) / pasos_excitacion
    Rx = _rot_x(paso)
    for i in range(pasos_excitacion):
        M = Rx @ M
        tray[i] = M
    t_exc = np.linspace(-1.0, 0.0, pasos_excitacion)
    t = np.linspace(0, duracion, n)
    dt = t[1] - t[0]
    out = np.empty((n, 3), dtype=np.float64)
    Rz = _rot_z(2 * np.pi * df * dt * 1e-3)
    E1, E2 = np.exp(-dt / T1), np.exp(-dt / T2)
    for i in range(n):
        out[i] = M
        M = Rz @ M
        M = np.array([M[0] * E2, M[1] * E2, 1.0 + (M[2] - 1.0) * E1])
    return np.concatenate([t_exc, t]), np.vstack([tray, out])


def bloch_isocromatas(T1=800., T2=80., T2p=25., TE=60., secuencia="SE", n_spins=200,
                      n_t=500, semilla=0):
    """
    Conjunto de isocromatas con distribución lorentziana de frecuencias (T2').
    secuencia: 'FID', 'SE' (90-180) o 'GRE'.
    """
    rng = np.random.default_rng(semilla)
    gamma_hz = 1.0 / (np.pi * T2p * 1e-3)
    df = gamma_hz / 2 * np.tan(np.pi * (rng.random(n_spins) - 0.5))
    df = np.clip(df, -40 * gamma_hz, 40 * gamma_hz)
    T = 2.2 * TE if secuencia != "FID" else 6 * T2p
    t = np.linspace(0, T, n_t)
    fases = 2 * np.pi * df[None, :] * t[:, None] * 1e-3
    if secuencia == "SE":
        tau = TE / 2
        post = t > tau
        fases[post] = -fases[np.searchsorted(t, tau)] + 2 * np.pi * df[None, :] * (t[post, None] - tau) * 1e-3
    elif secuencia == "GRE":
        desfase_grad = 2.5 * np.sin(2 * np.pi * t / TE * 1.5)
        fases = fases + desfase_grad[:, None] * (np.linspace(-1, 1, n_spins)[None, :] * 8.0)
    
    # Magnetización transversal de cada espín
    dec_t2 = np.exp(-t / T2)[:, None]
    mxy_ind = dec_t2 * np.exp(1j * fases)
    mxy = np.abs(np.mean(mxy_ind, axis=1))
    mz = 1 - np.exp(-t / T1)
    
    instantes = [0, TE / 4, TE / 2, 3 * TE / 4, TE] if secuencia != "FID" else [0, T2p / 2, T2p, 2 * T2p, 4 * T2p]
    fotos = {}
    for ti in instantes:
        i = int(np.argmin(np.abs(t - ti)))
        fotos[round(float(t[i]), 1)] = np.angle(mxy_ind[i])
    return t, mxy, mz, fotos


# ---------------------------------------------------------------------------
# 2. RELAJACIÓN Y TEJIDOS
# ---------------------------------------------------------------------------

TEJIDOS_REF = {
    "Grasa": (260, 80, 0.9, "#f59e0b"),
    "Sustancia blanca": (650, 80, 0.70, "#e2e8f0"),
    "Sustancia gris": (1000, 100, 0.82, "#94a3b8"),
    "LCR": (4000, 2000, 1.0, "#38bdf8"),
    "Músculo": (900, 45, 0.75, "#ef4444"),
    "Edema / lesión": (1150, 190, 0.9, "#a855f7"),
}


def escalar_t1(t1_15, B0):
    return t1_15 * (B0 / 1.5) ** (1 / 3)


def curvas_relajacion(B0=1.5, tmax_t1=5000, tmax_t2=500):
    t1 = np.linspace(0, tmax_t1, 300)
    t2 = np.linspace(0, tmax_t2, 300)
    out = {}
    for n, (T1, T2, pd, col) in TEJIDOS_REF.items():
        T1b = escalar_t1(T1, B0) if n != "LCR" else T1
        out[n] = dict(mz=pd * (1 - np.exp(-t1 / T1b)), mxy=pd * np.exp(-t2 / T2), color=col, T1=T1b, T2=T2)
    return t1, t2, out


def senal_tejidos(secuencia, TR, TE, TI=None, alpha=90, B0=1.5):
    res = {}
    for n, (T1, T2, pd, col) in TEJIDOS_REF.items():
        T1b = escalar_t1(T1, B0) if n != "LCR" else T1
        if secuencia == "GRE":
            a = np.deg2rad(alpha)
            E1 = np.exp(-TR / T1b)
            s = pd * np.sin(a) * (1 - E1) / (1 - np.cos(a) * E1) * np.exp(-TE / (0.7 * T2))
        elif secuencia == "IR":
            s = pd * abs(1 - 2 * np.exp(-TI / T1b) + np.exp(-TR / T1b)) * np.exp(-TE / T2)
        else:
            s = pd * (1 - np.exp(-TR / T1b)) * np.exp(-TE / T2)
        res[n] = (float(s), col)
    return res


# ---------------------------------------------------------------------------
# 3. ESPACIO K Y TRANSFORMADA DE FOURIER 2D
# ---------------------------------------------------------------------------

def a_kspace(img):
    return np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(img)))


def desde_kspace(k):
    return np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(k)))


def log_mag(k):
    m = np.log1p(np.abs(k))
    return (m / (m.max() + 1e-8)).astype(np.float32)


def mascara_kspace(forma, modo="completo", p=None):
    p = p or {}
    M, N = forma
    ky = (np.arange(M) - M // 2)[:, None]
    kx = (np.arange(N) - N // 2)[None, :]
    r = np.sqrt((ky / (M / 2)) ** 2 + (kx / (N / 2)) ** 2)
    mask = np.ones(forma, np.float32)
    if modo == "centro":
        mask = (r <= p.get("radio", 0.15)).astype(np.float32)
    elif modo == "periferia":
        mask = (r > p.get("radio", 0.15)).astype(np.float32)
    elif modo == "submuestreo":
        R = int(p.get("R", 2))
        mask = np.zeros(forma, np.float32)
        mask[::R, :] = 1
    elif modo == "parcial":
        frac = p.get("fraccion", 0.6)
        mask = np.zeros(forma, np.float32)
        mask[: int(M * frac), :] = 1
    elif modo == "radial":
        n = int(p.get("radios", 32))
        mask = np.zeros(forma, np.float32)
        t = np.linspace(-1, 1, 2 * max(M, N))
        for a in np.linspace(0, np.pi, n, endpoint=False):
            yy = np.clip(np.round(M / 2 + t * M / 2 * np.sin(a)).astype(int), 0, M - 1)
            xx = np.clip(np.round(N / 2 + t * N / 2 * np.cos(a)).astype(int), 0, N - 1)
            mask[yy, xx] = 1
    elif modo == "espiral":
        vueltas = int(p.get("vueltas", 16))
        mask = np.zeros(forma, np.float32)
        th = np.linspace(0, 2 * np.pi * vueltas, 40000)
        rr = th / th.max()
        yy = np.clip(np.round(M / 2 + rr * M / 2 * np.sin(th)).astype(int), 0, M - 1)
        xx = np.clip(np.round(N / 2 + rr * N / 2 * np.cos(th)).astype(int), 0, N - 1)
        mask[yy, xx] = 1
    elif modo == "aleatorio":
        frac = p.get("fraccion", 0.3)
        rng = np.random.default_rng(4)
        prob = np.clip(frac * 2.2 * np.exp(-(ky[:, 0] / (M / 5)) ** 2) + frac * 0.4, 0, 1)
        filas = rng.random(M) < prob
        filas[M // 2 - 6:M // 2 + 6] = True
        mask = np.repeat(filas[:, None], N, axis=1).astype(np.float32)
    return mask


def reconstruir(img, modo="completo", p=None, artefacto=None, pa=None):
    pa = pa or {}
    k = a_kspace(img.astype(np.complex64))
    M, N = k.shape
    rng = np.random.default_rng(7)
    if artefacto == "movimiento":
        frac = pa.get("severidad", 0.3)
        filas = rng.random(M) < frac
        desplaz = rng.normal(0, pa.get("amplitud", 3.0), M)
        fase = np.exp(-2j * np.pi * desplaz[:, None] * (np.arange(M) - M // 2)[:, None] / M)
        k = np.where(filas[:, None], k * fase, k)
    elif artefacto == "spike":
        ky, kx = int(M / 2 + pa.get("dy", 18)), int(N / 2 + pa.get("dx", 25))
        k[ky % M, kx % N] += np.abs(k).max() * pa.get("intensidad", 0.25)
    elif artefacto == "ruido":
        s = np.abs(k).max() * pa.get("nivel", 0.002)
        k = k + rng.normal(0, s, k.shape) + 1j * rng.normal(0, s, k.shape)
    elif artefacto == "truncamiento":
        n = int(pa.get("matriz", 48))
        m = np.zeros_like(k)
        cy, cx = M // 2, N // 2
        m[cy - n // 2:cy + n // 2, cx - n // 2:cx + n // 2] = 1
        k = k * m
    elif artefacto == "aliasing":
        R = int(pa.get("R", 2))
        k2 = np.zeros_like(k)
        k2[::R] = k[::R] * R
        k = k2
    mask = mascara_kspace(k.shape, modo, p)
    k_m = k * mask
    rec = np.abs(desde_kspace(k_m))
    rec = rec / (np.percentile(rec, 99.8) + 1e-8)
    return np.clip(rec, 0, 1).astype(np.float32), log_mag(k_m), mask


# ---------------------------------------------------------------------------
# 4. FILTRADO ESPACIAL Y FRECUENCIAL
# ---------------------------------------------------------------------------

def funcion_transferencia(forma, tipo="gaussiano", banda="paso_bajo", D0=30.0, n=2, W=10.0):
    M, N = forma
    u = np.arange(M) - M / 2
    v = np.arange(N) - N / 2
    D = np.sqrt(u[:, None] ** 2 + v[None, :] ** 2).astype(np.float32)
    D0 = max(1.0, float(D0))
    if banda in ("paso_bajo", "paso_alto"):
        if tipo == "ideal":
            H = (D <= D0).astype(np.float32)
        elif tipo == "butterworth":
            H = 1.0 / (1.0 + (D / D0) ** (2 * n))
        else:
            H = np.exp(-(D ** 2) / (2 * D0 ** 2))
        if banda == "paso_alto":
            H = 1.0 - H
    else:
        W = max(1.0, float(W))
        if tipo == "ideal":
            H = 1.0 - ((D >= D0 - W / 2) & (D <= D0 + W / 2)).astype(np.float32)
        elif tipo == "butterworth":
            H = 1.0 / (1.0 + ((D * W) / (D ** 2 - D0 ** 2 + EPS)) ** (2 * n))
        else:
            H = 1.0 - np.exp(-(((D ** 2 - D0 ** 2) / (D * W + EPS)) ** 2))
        if banda == "paso_banda":
            H = 1.0 - H
    return H.astype(np.float32)


FILTROS_K = [
    ("Paso bajo (suaviza, conserva el contraste)", "paso_bajo"),
    ("Paso alto (realza bordes y detalles)", "paso_alto"),
    ("Paso banda (texturas de un tamaño)", "paso_banda"),
    ("Rechaza banda (elimina un rango)", "rechaza_banda"),
    ("Ventana de Hamming (reduce el anillado de Gibbs)", "hamming"),
    ("Ventana de Hann (apodización)", "hann"),
    ("Realce de altas frecuencias (high-boost)", "high_boost"),
]


def mascara_filtro_k(forma, tipo="paso_bajo", familia="gaussiano", frac=0.2, ancho=0.1, orden=2, ganancia=1.5):
    M, N = forma
    radio = min(M, N) / 2
    if tipo in ("hamming", "hann"):
        def w(n):
            x = np.linspace(-1, 1, n)
            return 0.54 + 0.46 * np.cos(np.pi * x) if tipo == "hamming" else 0.5 + 0.5 * np.cos(np.pi * x)
        return np.outer(w(M), w(N)).astype(np.float32)
    if tipo == "high_boost":
        Hpa = funcion_transferencia(forma, familia, "paso_alto", max(1.0, frac * radio), orden, max(1.0, ancho * radio))
        return (1.0 + (ganancia - 1.0) * Hpa).astype(np.float32)
    return funcion_transferencia(forma, familia, tipo, max(1.0, frac * radio), orden, max(1.0, ancho * radio))


def filtrar_en_k(img, H):
    k = a_kspace(img.astype(np.complex64))
    kf = k * H
    out = np.real(desde_kspace(kf))
    if H.min() < 0.999 and H.max() <= 1.0 + 1e-6 and H[H.shape[0] // 2, H.shape[1] // 2] < 0.5:
        lo, hi = np.percentile(out, [1, 99.5])
        out = (out - lo) / (hi - lo + 1e-8)
    return np.clip(out, 0, 1).astype(np.float32), log_mag(kf)


# ---------------------------------------------------------------------------
# 5. DIAGRAMAS DE SECUENCIAS
# ---------------------------------------------------------------------------

def _sinc_pulse(t0, dur, amp, n=60):
    t = np.linspace(-dur / 2, dur / 2, n)
    y = amp * np.sinc(4 * t / dur) * np.hanning(n)
    return list(t0 + t), list(y)


def _trap(t0, dur, amp, rampa=0.6):
    return [t0, t0 + rampa, t0 + dur - rampa, t0 + dur], [0, amp, amp, 0]


def _fid(t0, amp):
    tt = np.linspace(t0, t0 + 6, 80)
    return (list(tt), list(amp * np.exp(-(tt - t0) / 1.8) * np.cos((tt - t0) * 8)))


def diagrama_secuencia(tipo="SE", TE=30., TR=100., TI=50., etl=8):
    canales = {k: [] for k in ("RF", "Gss", "Gpe", "Gro", "Señal")}
    notas = []
    t_exc = TI if tipo == "IR" else 5.0
    if tipo == "IR":
        canales["RF"].append(_sinc_pulse(2, 3, 1.0))
        notas.append((2, "RF", "180° inv."))
        canales["Gss"].append(_trap(0.5, 3, 0.6))
    canales["RF"].append(_sinc_pulse(t_exc, 3, 0.6 if tipo != "GRE" else 0.35))
    notas.append((t_exc, "RF", "90°" if tipo != "GRE" else "α"))
    canales["Gss"].append(_trap(t_exc - 1.5, 3, 0.6))
    canales["Gss"].append(_trap(t_exc + 1.6, 1.5, -0.6))
    canales["Gpe"] += [_trap(t_exc + 2, 2.5, a) for a in np.linspace(-0.7, 0.7, 7)]
    t0 = 0.0
    te = t_exc + TE
    if tipo in ("SE", "IR", "DWI"):
        t180 = t_exc + TE / 2
        canales["RF"].append(_sinc_pulse(t180, 3, 1.0))
        notas.append((t180, "RF", "180°"))
        canales["Gss"].append(_trap(t180 - 1.5, 3, 0.6))
        canales["Gro"].append(_trap(t_exc + 2, 2.5, 0.6))
        if tipo == "DWI":
            canales["Gpe"].append(_trap(t_exc + 5, TE / 2 - 9, 1.0))
            canales["Gpe"].append(_trap(t180 + 2.5, TE / 2 - 9, 1.0))
            notas.append((t_exc + 5, "Gpe", "G difusión"))
        canales["Gro"].append(_trap(te - 3, 6, 0.6))
        tt = np.linspace(te - 3, te + 3, 120)
        canales["Señal"].append((list(tt), list(np.sinc((tt - te) * 1.3) * np.cos((tt - te) * 9))))
        canales["Señal"].append(_fid(t_exc + 1.6, 0.25))
    elif tipo == "GRE":
        canales["Gro"].append(_trap(t_exc + 2, te - t_exc - 5, -0.6))
        canales["Gro"].append(_trap(te - 3, 6, 0.6))
        tt = np.linspace(te - 3, te + 3, 120)
        canales["Señal"].append((list(tt), list(np.sinc((tt - te) * 1.3) * np.cos((tt - te) * 9) * 0.8)))
        canales["Gss"].append(_trap(te + 3.5, 2, 0.8))
        notas.append((te + 4, "Gss", "spoiler"))
    elif tipo == "EPI":
        t180 = t_exc + 8
        canales["RF"].append(_sinc_pulse(t180, 3, 1.0))
        canales["Gss"].append(_trap(t180 - 1.5, 3, 0.6))
        canales["Gpe"] = [_trap(t_exc + 2, 2, -0.7)]
        t0 = t180 + 3
        sgn = 1
        for i in range(etl):
            canales["Gro"].append(_trap(t0, 4, 0.7 * sgn))
            canales["Gpe"].append(_trap(t0 + 3.6, 0.8, 0.25))
            tt = np.linspace(t0, t0 + 4, 40)
            ce = t0 + 2
            env = np.exp(-abs(i - etl / 2) / (etl / 2.5))
            canales["Señal"].append((list(tt), list(env * np.sinc((tt - ce) * 1.8) * np.cos((tt - ce) * 10))))
            t0 += 4.2
            sgn *= -1
        notas.append((t180 + 3, "Gro", "tren EPI"))
    fin = max(TR, te + 8 if tipo != "EPI" else t0 + 4)
    return canales, notas, fin


# ---------------------------------------------------------------------------
# 6. CALCULADORAS CLÍNICAS
# ---------------------------------------------------------------------------

def larmor_mhz(B0):
    return GAMMA_BAR * B0


def exceso_spins_ppm(B0, T=310.0):
    return GAMMA * HBAR * B0 / (2 * KB * T) * 1e6


def grosor_corte_mm(bw_rf_hz, G_mT_m):
    return bw_rf_hz / (GAMMA_BAR * 1e6 * G_mT_m * 1e-3) * 1e3


def tiempo_adquisicion_s(TR_ms, Ny, NEX=1, ETL=1, cortes_por_tr=1, n_paquetes=1):
    return TR_ms * 1e-3 * Ny * NEX / max(ETL, 1) * n_paquetes


def resolucion_mm(FOV_mm, N):
    return FOV_mm / N


def snr_relativa(dx, dy, dz, Ny, NEX, BW_hz, B0=1.5):
    return B0 * dx * dy * dz * np.sqrt(Ny * NEX / BW_hz)


def angulo_ernst(TR, T1):
    return float(np.degrees(np.arccos(np.exp(-TR / T1))))


def ti_nulo(T1, TR=None):
    if TR is None:
        return T1 * np.log(2)
    return T1 * (np.log(2) - np.log(1 + np.exp(-TR / T1)))


def desplazamiento_quimico_px(B0, BW_total_hz, Nx):
    df = 3.5e-6 * larmor_mhz(B0) * 1e6
    return df / (BW_total_hz / Nx), df

