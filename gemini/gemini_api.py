# gemini/gemini_api.py
# =============================================================================
# PROMETEO — Adaptador Retrocompatible hacia services.gemini_service
# =============================================================================
import os
from services.gemini_service import gemini_service

# Referencias a modelos configurados
MODEL_TEXT = gemini_service.model_text
MODEL_IMAGE_ANALYSIS = gemini_service.model_image_analysis
MODEL_IMAGE_GENERATION = gemini_service.model_image_generation

# Cliente compartido (singleton)
client = gemini_service._client


def preguntar_gemini(prompt: str) -> str:
    """Envía solamente texto a Gemini usando el servicio centralizado."""
    return gemini_service.generar_texto(prompt)


def preguntar_gemini_imagen(ruta_imagen: str, prompt: str, contexto: str = "") -> str:
    """Envía imagen + texto al modelo multimodal del servicio centralizado."""
    return gemini_service.analizar_imagen(
        imagen=ruta_imagen,
        prompt=prompt,
        contexto=contexto,
    )


def generar_imagen_gemini(
    prompt: str,
    ruta_salida: str = "gemini_generada.png",
    image_size: str = "1K",
    aspect_ratio: str = "1:1",
):
    """Genera una imagen con Gemini usando el servicio centralizado."""
    return gemini_service.generar_imagen(prompt, ruta_salida=ruta_salida)
