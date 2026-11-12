"""Configuración e invocación del modelo de IA (Google Gemini) para evaluar CVs."""

import logging
import os

from google import genai
from pydantic import ValidationError

from models.cv_model import AnalisisCV
from prompts.cv_prompts import crear_sistema_prompts

logger = logging.getLogger(__name__)

MODELO_PREDETERMINADO = "gemini-3.8-flash"


class EvaluacionError(Exception):
    """Excepción controlada cuando falla la comunicación o validación del modelo."""


def obtener_modelo_configurado() -> str:
    """Devuelve el identificador del modelo Gemini configurado en el entorno."""
    return os.getenv("GEMINI_MODEL", MODELO_PREDETERMINADO).strip() or MODELO_PREDETERMINADO


def crear_evaluador_cv() -> genai.Client:
    """Inicializa y devuelve el cliente oficial de Google Gemini.

    Verifica explícitamente que ``GEMINI_API_KEY`` esté definida en el entorno.

    Returns:
        Instancia configurada de ``genai.Client``.

    Raises:
        EvaluacionError: Si no se encuentra la clave ``GEMINI_API_KEY``.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise EvaluacionError(
            "No se encontró la variable de entorno GEMINI_API_KEY. "
            "Configúrala en tu terminal antes de iniciar Streamlit "
            "(por ejemplo: $env:GEMINI_API_KEY = 'tu_clave')."
        )
    return genai.Client(api_key=api_key)


def _formatear_error_api(exc: Exception) -> str:
    """Traduce errores comunes de la API a mensajes claros en español."""
    texto = str(exc)
    texto_lower = texto.lower()

    if "api_key_invalid" in texto_lower or "api key not valid" in texto_lower or "401" in texto_lower or "403" in texto_lower:
        return (
            "La clave GEMINI_API_KEY no es válida o no tiene permisos. "
            "Verifica tu clave en Google AI Studio (https://aistudio.google.com/apikey)."
        )
    if "429" in texto_lower or "quota" in texto_lower or "resource_exhausted" in texto_lower:
        return (
            "Se alcanzó el límite de cuota o velocidad de la API de Gemini (HTTP 429). "
            "Espera unos segundos y vuelve a intentarlo, o revisa tu cuota en Google AI Studio."
        )
    if "404" in texto_lower or "not found" in texto_lower:
        modelo = obtener_modelo_configurado()
        return (
            f"El modelo '{modelo}' no está disponible o no fue encontrado. "
            f"Verifica la variable GEMINI_MODEL (por defecto '{MODELO_PREDETERMINADO}')."
        )
    return f"No se pudo completar la evaluación con Gemini: {texto}"


def evaluar_candidato(texto_cv: str, descripcion_puesto: str) -> AnalisisCV:
    """Evalúa un CV frente a la descripción del puesto usando salida estructurada.

    Utiliza la API de Interactions de ``google-genai`` con ``AnalisisCV`` como
    esquema JSON de respuesta, garantizando que el resultado cumpla con el
    modelo Pydantic.

    Args:
        texto_cv: Texto extraído del PDF del candidato.
        descripcion_puesto: Requisitos y descripción del puesto.

    Returns:
        Instancia validada de ``AnalisisCV``.

    Raises:
        EvaluacionError: Si falta la clave de API, falla la llamada a Gemini o
            la respuesta no cumple con el esquema esperado.
    """
    cliente = crear_evaluador_cv()
    modelo = obtener_modelo_configurado()
    sistema, mensaje_usuario = crear_sistema_prompts(texto_cv, descripcion_puesto)

    try:
        interaction = cliente.interactions.create(
            model=modelo,
            system_instruction=sistema,
            input=mensaje_usuario,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": AnalisisCV.model_json_schema(),
            },
            generation_config={
                "thinking_level": "low",
            },
            store=False,
        )

        texto_respuesta = (interaction.output_text or "").strip()
        if not texto_respuesta:
            raise EvaluacionError(
                "El modelo devolvió una respuesta vacía. Intenta nuevamente."
            )

        return AnalisisCV.model_validate_json(texto_respuesta)

    except EvaluacionError:
        raise
    except ValidationError as exc:
        logger.exception("Error validando la respuesta JSON del modelo contra AnalisisCV")
        raise EvaluacionError(
            "La respuesta del modelo no cumplió con el formato estructurado esperado."
        ) from exc
    except Exception as exc:
        logger.exception("Error durante la invocación a la API de Gemini")
        raise EvaluacionError(_formatear_error_api(exc)) from exc
