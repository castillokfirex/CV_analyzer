"""Funciones puras de clasificación y umbrales para el ajuste del candidato."""


def obtener_evaluacion_principal(porcentaje: int) -> tuple[str, str]:
    """Clasifica el porcentaje en la escala de evaluación principal.

    Umbrales según especificación:
    - 80–100: Excelente
    - 60–79: Bueno
    - 40–59: Regular
    - 0–39: Bajo

    Args:
        porcentaje: Porcentaje de ajuste entre 0 y 100.

    Returns:
        Tupla ``(etiqueta, color_hex)`` para su presentación visual.
    """
    if porcentaje >= 80:
        return "Excelente", "#16a34a"
    if porcentaje >= 60:
        return "Bueno", "#2563eb"
    if porcentaje >= 40:
        return "Regular", "#d97706"
    return "Bajo", "#dc2626"


def obtener_recomendacion_final(porcentaje: int) -> tuple[str, str, str]:
    """Determina la recomendación final de contratación según el porcentaje.

    Umbrales según especificación:
    - 70–100: Candidato recomendado
    - 50–69: Candidato con potencial
    - 0–49: Candidato no recomendado

    Args:
        porcentaje: Porcentaje de ajuste entre 0 y 100.

    Returns:
        Tupla ``(titulo_recomendacion, detalle, nivel_alerta)`` donde
        ``nivel_alerta`` es ``"success"``, ``"warning"`` o ``"error"``.
    """
    if porcentaje >= 70:
        return (
            "Candidato recomendado",
            "El perfil cumple ampliamente con los criterios clave del puesto. "
            "Se recomienda avanzar a la fase de entrevistas técnicas.",
            "success",
        )
    if porcentaje >= 50:
        return (
            "Candidato con potencial",
            "El perfil presenta una base sólida pero tiene brechas en algunos "
            "requisitos. Se sugiere evaluar sus áreas de mejora en entrevista.",
            "warning",
        )
    return (
        "Candidato no recomendado",
        "El perfil actual no alcanza el ajuste mínimo requerido para el puesto "
        "en este proceso de selección.",
        "error",
    )
