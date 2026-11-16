"""Regenera gemini/knowledge_base.json usando los documentos de assets/.

Ejecutar desde la carpeta del proyecto con:
    py gemini/generar_base_conocimiento.py

Se usa solo cuando se reemplaza o actualiza el PDF o el PPTX.
"""

import json
import os
import re
import sys

try:
    import fitz
except ImportError:
    fitz = None

try:
    from pptx import Presentation
except ImportError:
    Presentation = None

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(PROJECT_DIR, "assets")
OUT = os.path.join(PROJECT_DIR, "gemini", "knowledge_base.json")

records = []

pdf_path = os.path.join(ASSETS, "Medical_Imaging_Signals_and_Systems.pdf")
if fitz is not None and os.path.exists(pdf_path):
    doc = fitz.open(pdf_path)
    for page_no, page in enumerate(doc, 1):
        text = re.sub(r"\s+", " ", page.get_text("text") or "").strip()
        if text:
            records.append({
                "id": f"book_p{page_no}",
                "source": "libro",
                "source_name": "Medical Imaging Signals and Systems — Prince & Links, 2nd ed.",
                "location": f"Página PDF {page_no}",
                "page": page_no,
                "text": text,
            })

ppt_path = os.path.join(ASSETS, "Tomografia_Computarizada.pptx")
if Presentation is not None and os.path.exists(ppt_path):
    prs = Presentation(ppt_path)
    for slide_no, slide in enumerate(prs.slides, 1):
        parts = []
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text and shape.text.strip():
                parts.append(shape.text.strip())
        text = re.sub(r"\s+", " ", "\n".join(parts)).strip()
        if text:
            records.append({
                "id": f"slides_s{slide_no}",
                "source": "diapositivas",
                "source_name": "Tomografía Computarizada — diapositivas del proyecto",
                "location": f"Diapositiva {slide_no}",
                "slide": slide_no,
                "text": text,
            })

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"version": 1, "records": records}, f, ensure_ascii=False)

print(f"Base de conocimiento generada: {len(records)} fragmentos")
print(OUT)
