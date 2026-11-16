# services/gemini_service.py
# =============================================================================
# PROMETEO — Cliente Unificado de Inteligencia Artificial (Google Gemini)
# =============================================================================
# Utiliza el SDK moderno 'google-genai' (>= 1.0.0).
# Todas las modalidades (SyS, CT, Rx, MRI) deben consumir exclusivamente este
# servicio centralizado para texto, análisis multimodal y generación visual.
# =============================================================================

import os
import re
import json
import base64
from pathlib import Path
from typing import Optional, Dict, Any, Union, List

from dotenv import load_dotenv

# Carga de variables de entorno (.env)
load_dotenv()

# Intentar importar el SDK moderno de google-genai
_GENAI_AVAILABLE = False
try:
    from google import genai
    from google.genai import types as genai_types
    _GENAI_AVAILABLE = True
except ImportError:
    genai = None
    genai_types = None


class GeminiService:
    """
    Servicio Singleton para interactuar con la API de Google Gemini.
    Garantiza una única instancia del cliente en toda la aplicación.
    """

    def __init__(self):
        self._client = None
        self._api_key: str = ""
        self._cache: Dict[str, str] = {}
        self._cache_max_items: int = 150
        self._initialized = False

        # Modelos configurados (con valores predeterminados estables)
        self.model_text = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash").strip()
        self.model_image_analysis = os.getenv("GEMINI_IMAGE_ANALYSIS_MODEL", "gemini-2.5-flash").strip()
        self.model_image_generation = os.getenv("GEMINI_IMAGE_MODEL", "imagen-3.0-generate-002").strip()

        self._init_client()

    def _init_client(self):
        """Inicializa el cliente de forma segura sin romper la app si falta la clave."""
        self._api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not _GENAI_AVAILABLE:
            print("[GeminiService] ADVERTENCIA: El paquete 'google-genai' no está disponible.")
            self._client = None
            return

        if not self._api_key:
            print("[GeminiService] AVISO: GEMINI_API_KEY no encontrada en .env. Se usarán respuestas locales/fallback.")
            self._client = None
            return

        try:
            self._client = genai.Client(api_key=self._api_key)
            self._initialized = True
            print(f"[GeminiService] Conectado exitosamente (Modelo texto: {self.model_text}).")
        except Exception as e:
            print(f"[GeminiService] Error al inicializar cliente Gemini: {e}")
            self._client = None

    @property
    def is_available(self) -> bool:
        """Devuelve True si el cliente está listo para recibir consultas."""
        return self._client is not None

    def reload_key(self, new_key: Optional[str] = None):
        """Permite recargar la API Key dinámicamente si se actualiza el .env."""
        if new_key:
            os.environ["GEMINI_API_KEY"] = new_key
        self._init_client()

    # ─────────────────────────────────────────────────────────────────────────
    # CACHÉ EN MEMORIA
    # ─────────────────────────────────────────────────────────────────────────
    def _get_cache(self, key: str) -> Optional[str]:
        return self._cache.get(key.strip().lower())

    def _set_cache(self, key: str, value: str):
        if len(self._cache) >= self._cache_max_items:
            # Eliminar la mitad más antigua
            keys_to_remove = list(self._cache.keys())[:25]
            for k in keys_to_remove:
                self._cache.pop(k, None)
        self._cache[key.strip().lower()] = value

    # ─────────────────────────────────────────────────────────────────────────
    # GESTIÓN CENTRALIZADA DE ERRORES
    # ─────────────────────────────────────────────────────────────────────────
    def _formatear_error(self, error: Exception, contexto: str = "Gemini") -> str:
        mensaje = str(error)
        codigo = getattr(error, "code", None)

        if codigo == 429 or "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje:
            return (
                "[AVISO] Límite de solicitudes alcanzado en la API de Gemini.\n\n"
                "Por favor espera unos instantes antes de enviar una nueva consulta."
            )

        if codigo in (401, 403) or any(x in mensaje for x in ("401", "403", "API_KEY_INVALID", "PERMISSION_DENIED")):
            return (
                "[ERROR] Error de autenticación con Gemini.\n\n"
                "La clave GEMINI_API_KEY configurada en .env no fue aceptada o no tiene cuota asignada."
            )

        return f"[ERROR] Error en el asistente ({contexto}):\n{mensaje}"

    # ─────────────────────────────────────────────────────────────────────────
    # CONSULTA DE TEXTO
    # ─────────────────────────────────────────────────────────────────────────
    def generar_texto(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        usar_cache: bool = True,
    ) -> str:
        """
        Envía un prompt de texto a Gemini y retorna la respuesta como cadena.
        """
        if not prompt or not prompt.strip():
            return ""

        cache_key = f"{prompt}_{system_instruction or ''}"
        if usar_cache:
            en_cache = self._get_cache(cache_key)
            if en_cache:
                return en_cache

        if not self.is_available:
            return "El asistente de IA no está configurado (falta GEMINI_API_KEY en .env)."

        target_model = model or self.model_text
        try:
            config = None
            if system_instruction or temperature is not None:
                config = genai_types.GenerateContentConfig(
                    temperature=temperature,
                    system_instruction=system_instruction,
                )

            response = self._client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=config,
            )
            texto_resp = response.text or ""

            if usar_cache and texto_resp:
                self._set_cache(cache_key, texto_resp)

            return texto_resp

        except Exception as error:
            return self._formatear_error(error, contexto="Texto")

    # ─────────────────────────────────────────────────────────────────────────
    # ANÁLISIS MULTIMODAL (IMAGEN + TEXTO)
    # ─────────────────────────────────────────────────────────────────────────
    def analizar_imagen(
        self,
        imagen: Union[str, Path, bytes],
        prompt: str,
        contexto: str = "",
        mime_type: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        """
        Analiza una imagen médica (ruta, Path o bytes) combinada con una pregunta
        y contexto técnico de procesamiento.
        """
        if not self.is_available:
            return "El asistente de IA no está configurado (falta GEMINI_API_KEY en .env)."

        target_model = model or self.model_image_analysis

        try:
            # Obtención de bytes y mime_type
            if isinstance(imagen, (str, Path)):
                ruta_str = str(imagen)
                if not os.path.exists(ruta_str):
                    return f"[ERROR] La imagen no existe en la ruta: {ruta_str}"

                ext = os.path.splitext(ruta_str)[1].lower()
                mimes = {
                    ".png": "image/png",
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".webp": "image/webp",
                    ".bmp": "image/bmp",
                    ".gif": "image/gif",
                }
                detected_mime = mimes.get(ext, "image/png")
                with open(ruta_str, "rb") as f:
                    datos_bytes = f.read()
            elif isinstance(imagen, bytes):
                datos_bytes = imagen
                detected_mime = mime_type or "image/png"
            else:
                return "[ERROR] Tipo de entrada de imagen no soportado."

            part = genai_types.Part.from_bytes(
                data=datos_bytes,
                mime_type=detected_mime,
            )

            prompt_completo = prompt
            if contexto:
                prompt_completo = (
                    f"{prompt}\n\n"
                    f"================================\n"
                    f"CONTEXTO DE PROCESAMIENTO TÉCNICO\n"
                    f"================================\n"
                    f"{contexto}"
                )

            response = self._client.models.generate_content(
                model=target_model,
                contents=[part, prompt_completo],
            )
            return response.text or ""

        except Exception as error:
            return self._formatear_error(error, contexto="Análisis de Imagen")

    # ─────────────────────────────────────────────────────────────────────────
    # GENERACIÓN ESTRUCTURADA (JSON / QUIZZES / DIAGRAMAS)
    # ─────────────────────────────────────────────────────────────────────────
    def generar_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Optional[Union[Dict, List]]:
        """
        Solicita a Gemini una respuesta en formato JSON estructurado y la parsea.
        Ideal para quizzes automáticos (SyS) y mapas conceptuales (Rx).
        """
        instruccion = (system_instruction or "") + "\nResponde EXCLUSIVAMENTE con un JSON válido sin texto adicional."
        texto = self.generar_texto(prompt, system_instruction=instruccion, model=model, temperature=0.2, usar_cache=False)

        if not texto or texto.startswith("[ERROR]") or texto.startswith("[AVISO]"):
            return None

        # Limpiar bloques de código markdown tipo ```json ... ```
        limpio = texto.strip()
        if "```" in limpio:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", limpio)
            if match:
                limpio = match.group(1).strip()

        try:
            return json.loads(limpio)
        except Exception as e:
            print(f"[GeminiService] Error decodificando JSON generado: {e}\nTexto recibido:\n{texto[:200]}")
            return None

    # ─────────────────────────────────────────────────────────────────────────
    # GENERACIÓN DE IMÁGENES
    # ─────────────────────────────────────────────────────────────────────────
    def generar_imagen(
        self,
        prompt: str,
        ruta_salida: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Genera una imagen usando el modelo de generación de imágenes de Gemini.
        """
        if not self.is_available:
            return {"ok": False, "mensaje": "Cliente Gemini no disponible.", "ruta": None}

        try:
            response = self._client.models.generate_content(
                model=self.model_image_generation,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )

            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "inline_data") and part.inline_data:
                        datos = part.inline_data.data
                        if ruta_salida:
                            os.makedirs(os.path.dirname(os.path.abspath(ruta_salida)), exist_ok=True)
                            with open(ruta_salida, "wb") as f:
                                f.write(datos)
                        return {
                            "ok": True,
                            "mensaje": "Imagen generada con éxito.",
                            "bytes": datos,
                            "ruta": ruta_salida,
                        }

            return {"ok": False, "mensaje": "Gemini no devolvió ninguna imagen.", "ruta": None}

        except Exception as error:
            return {
                "ok": False,
                "mensaje": self._formatear_error(error, contexto="Generación de Imagen"),
                "ruta": None,
            }


# Instancia global compartida (Singleton)
gemini_service = GeminiService()

