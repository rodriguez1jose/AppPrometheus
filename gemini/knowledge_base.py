"""Base de conocimiento local para el asistente CT-SIM.

El índice se construye a partir del libro base y de las diapositivas
incluidas en assets/. La aplicación NO necesita subir los documentos completos
cada vez que el estudiante hace una pregunta: recupera primero fragmentos
relevantes y solo esos fragmentos se incorporan al prompt de Gemini.
"""

import json
import os
import re
import unicodedata

BASE_DIR = os.path.dirname(__file__)
INDEX_PATH = os.path.join(BASE_DIR, "knowledge_base.json")

STOPWORDS = {
    "a", "al", "algo", "ante", "con", "como", "cual", "cuando", "de",
    "del", "desde", "donde", "el", "ella", "ellas", "ellos", "en", "es",
    "esa", "ese", "eso", "esta", "este", "esto", "hay", "la", "las", "lo",
    "los", "me", "mi", "mis", "muy", "no", "para", "por", "que", "se",
    "segun", "si", "sin", "sobre", "su", "sus", "te", "un", "una", "uno",
    "y", "o", "u", "qué", "que", "es", "son", "ser", "del", "los", "las",
    "un", "una", "unos", "unas", "tambien", "también", "puede", "pueden",
}

ALIASES = {
    "histograma": {"histogram", "histograms"},
    "histogramas": {"histogram", "histograms"},
    "reconstruccion": {"reconstruction", "reconstruct", "reconstructed"},
    "retroproyeccion": {"backprojection", "backprojection", "back-projection"},
    "proyeccion": {"projection", "projections"},
    "proyecciones": {"projection", "projections"},
    "atenuacion": {"attenuation", "attenuations"},
    "sinograma": {"sinogram", "sinograms"},
    "tomografia": {"tomography", "computed tomography", "ct"},
    "tomografia computarizada": {"computed tomography", "ct"},
    "numero ct": {"ct numbers", "ct number", "hounsfield", "hounsfield units", "hu"},
    "hounsfield": {"hounsfield", "hounsfield units", "ct number", "ct numbers", "hu"},
    "unidades hounsfield": {"hounsfield", "hounsfield units", "ct number", "ct numbers", "hu"},
    "radon": {"radon", "radon transform"},
    "ruido": {"noise", "noisy"},
    "resolucion": {"resolution", "spatial resolution", "temporal resolution"},
    "filtro": {"filter", "filtered", "filtering"},
    "filtros": {"filter", "filtered", "filtering"},
}


def _normalize(text):
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text


def _tokens(text):
    normalized = _normalize(text)
    words = re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)?", normalized)
    return [w for w in words if len(w) > 1 and w not in STOPWORDS]


def _expanded_tokens(query):
    base = set(_tokens(query))
    normalized_query = _normalize(query)
    for key, aliases in ALIASES.items():
        if _normalize(key) in normalized_query:
            base.update(_tokens(" ".join(aliases)))
    return base


def cargar_base():
    if not os.path.exists(INDEX_PATH):
        return []
    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("records", [])
    except Exception:
        return []


_RECORDS = cargar_base()


def detectar_fuente(pregunta, fuente="todas"):
    """Determina la fuente solicitada por el usuario.

    Si el selector ya tiene una fuente concreta, se respeta.
    Si está en 'todas', se detectan expresiones como 'según el libro'.
    """
    if fuente in {"libro", "diapositivas"}:
        return fuente

    q = _normalize(pregunta)
    if any(x in q for x in [
        "segun el libro", "segun libro", "libro base", "libro principal",
        "prince", "links", "segun medical imaging"
    ]):
        return "libro"

    if any(x in q for x in [
        "segun las diapositivas", "segun diapositivas", "las diapositivas",
        "diapositivas del ingeniero", "ppt", "slides"
    ]):
        return "diapositivas"

    return "todas"


def buscar(pregunta, fuente="todas", limite=5):
    """Recupera los fragmentos más relevantes mediante búsqueda léxica.

    No genera contenido: únicamente selecciona fragmentos existentes en la
    base documental local.
    """
    if not pregunta or not _RECORDS:
        return []

    fuente_real = detectar_fuente(pregunta, fuente)
    candidatos = [
        r for r in _RECORDS
        if fuente_real == "todas" or r.get("source") == fuente_real
    ]

    query_tokens = _expanded_tokens(pregunta)
    if not query_tokens:
        return []

    scored = []
    for record in candidatos:
        text_norm = _normalize(record.get("text", ""))
        title_norm = _normalize(record.get("source_name", ""))
        location_norm = _normalize(record.get("location", ""))

        text_tokens = set(_tokens(record.get("text", "")))
        score = 0.0
        matched = 0

        for token in query_tokens:
            if token in text_tokens:
                score += 2.0
                matched += 1
            elif token in text_norm:
                score += 0.8
            if token in title_norm:
                score += 0.4
            if token in location_norm:
                score += 0.2

        # Bonus para coincidencia de frases importantes.
        qnorm = _normalize(pregunta)
        phrase_pairs = [
            ("transformada de radon", ["transformada de radon", "radon transform"]),
            ("tomografia computarizada", ["tomografia computarizada", "computed tomography"]),
            ("computed tomography", ["computed tomography", "tomografia computarizada"]),
            ("ct numbers", ["ct numbers", "ct number", "numero ct"]),
            ("retroproyeccion filtrada", ["retroproyeccion filtrada", "filtered backprojection"]),
            ("filtered backprojection", ["filtered backprojection", "retroproyeccion filtrada"]),
            ("histograma", ["histograma", "histogram"]),
            ("histogram", ["histogram", "histograma"]),
        ]
        for query_phrase, text_phrases in phrase_pairs:
            if _normalize(query_phrase) in qnorm:
                if any(_normalize(tp) in text_norm for tp in text_phrases):
                    score += 4.0

        if matched:
            scored.append((score, matched, record))

    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [r for _, _, r in scored[:limite]]


def contexto_para_gemini(pregunta, fuente="todas", limite=5):
    """Construye el contexto documental interno para Gemini.

    Los metadatos se incluyen para que el modelo pueda distinguir el libro de
    las diapositivas, pero el widget no los muestra como una sección aparte.
    """
    resultados = buscar(pregunta, fuente=fuente, limite=limite)
    fuente_real = detectar_fuente(pregunta, fuente)

    if not resultados:
        return "", fuente_real, []

    partes = []
    for i, r in enumerate(resultados, 1):
        partes.append(
            f"[Fragmento {i}]\n"
            f"Fuente interna: {r.get('source_name')}\n"
            f"Ubicación: {r.get('location')}\n"
            f"Contenido:\n{r.get('text')}"
        )

    return "\n\n".join(partes), fuente_real, resultados
