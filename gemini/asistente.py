from .gemini_api import (
    preguntar_gemini,
    preguntar_gemini_imagen
)

from .prompts import SYSTEM_PROMPT, VALIDACION_DE_MODALIDAD
from .knowledge_base import contexto_para_gemini


def _construir_prompt(pregunta, fuente="todas"):
    contexto, fuente_real, resultados = contexto_para_gemini(
        pregunta,
        fuente=fuente,
        limite=5,
    )

    prompt = SYSTEM_PROMPT + "\n\n"

    prompt += """
MODO DE RESPUESTA CON MATERIAL ACADÉMICO

El proyecto dispone de una base documental local formada por:
- el libro base Medical Imaging Signals and Systems, de Prince y Links, 2.ª edición;
- las diapositivas de Tomografía Computarizada incluidas en Recursos.

Cuando exista material recuperado debajo de este mensaje:
1. Úsalo como fuente principal para responder.
2. No atribuyas al libro o a las diapositivas una definición, dato o afirmación que
   no esté respaldada por el material recuperado.
3. Si el estudiante dice "según el libro" o selecciona "Libro base", utiliza solamente
   los fragmentos del libro recuperados. Si el material no contiene la respuesta,
   dilo claramente en vez de inventarla.
4. Si el estudiante dice "según las diapositivas" o selecciona "Diapositivas", utiliza
   solamente los fragmentos de las diapositivas recuperados.
5. Si la pregunta no especifica una fuente, puedes integrar los materiales recuperados
   y explicarlos de forma didáctica. Si los documentos no cubren el punto, puedes
   complementar con conocimiento general, dejando claro que es una explicación
   complementaria y no atribuyéndola a los documentos.
6. No reproduzcas largos fragmentos textuales del material. Resume y explica con tus
   propias palabras.
7. No muestres al estudiante una sección técnica de "fuentes" o metadatos. Puedes
   decir de manera natural "según el libro" o "según las diapositivas" cuando sea útil.

"""

    if fuente_real == "libro":
        prompt += "Fuente solicitada: LIBRO BASE.\n\n"
    elif fuente_real == "diapositivas":
        prompt += "Fuente solicitada: DIAPOSITIVAS.\n\n"
    else:
        prompt += "Fuente solicitada: TODAS LAS FUENTES DISPONIBLES.\n\n"

    if contexto:
        prompt += "MATERIAL ACADÉMICO RECUPERADO:\n\n"
        prompt += contexto
        prompt += "\n\nFIN DEL MATERIAL RECUPERADO.\n\n"
    else:
        prompt += (
            "No se encontró un fragmento documental suficientemente relevante para "
            "esta pregunta. No atribuyas información al libro ni a las diapositivas.\n\n"
        )

    prompt += f"Pregunta del estudiante:\n\n{pregunta}"
    return prompt


# ==========================================
# Preguntas de texto con base documental
# ==========================================

def preguntar(pregunta, fuente="todas"):
    prompt = _construir_prompt(pregunta, fuente=fuente)
    return preguntar_gemini(prompt)


# ==========================================
# Análisis de imagen + datos de procesamiento
# ==========================================

def analizar_imagen_tc(
        ruta_imagen,
        pregunta,
        contexto="",
        fuente="todas"
):

    prompt = _construir_prompt(pregunta, fuente=fuente)
    prompt += "\n\n" + VALIDACION_DE_MODALIDAD

    if contexto:
        prompt += f"\n\nCONTEXTO DEL PROCESAMIENTO DE LA IMAGEN:\n{contexto}"

    return preguntar_gemini_imagen(
        ruta_imagen,
        prompt,
        contexto
    )
