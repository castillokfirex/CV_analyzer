"""Esquema Pydantic para la respuesta estructurada del análisis de CV."""

from pydantic import BaseModel, Field


class AnalisisCV(BaseModel):
    """Modelo de salida estructurada con la evaluación integral del candidato."""

    nombre_candidato: str = Field(
        description=(
            "Nombre completo del candidato extraído del CV. "
            "Si no aparece explícitamente, indicar 'No especificado'."
        )
    )
    experiencia_años: int = Field(
        ge=0,
        description=(
            "Años enteros de experiencia profesional relevante para el puesto "
            "(0 si no tiene experiencia relevante o es recién graduado)."
        ),
    )
    habilidades_clave: list[str] = Field(
        description=(
            "Lista de habilidades técnicas y blandas del candidato que son "
            "relevantes para el puesto (se sugieren entre 5 y 10 habilidades)."
        )
    )
    education: str = Field(
        description=(
            "Nivel educativo más alto alcanzado, titulaciones y especialización "
            "relevante del candidato. Si no figura, indicar 'No especificado'."
        )
    )
    experiencia_relevante: str = Field(
        description=(
            "Resumen conciso y objetivo de la trayectoria y logros del candidato "
            "directamente relacionados con los requisitos del puesto."
        )
    )
    fortalezas: list[str] = Field(
        description=(
            "Principales puntos fuertes del candidato frente al puesto "
            "(se sugieren entre 3 y 5 fortalezas claras y específicas)."
        )
    )
    areas_mejora: list[str] = Field(
        description=(
            "Áreas de desarrollo, brechas técnicas o requisitos del puesto "
            "que el candidato no cubre completamente (se sugieren entre 2 y 4 áreas)."
        )
    )
    porcentaje_ajuste: int = Field(
        ge=0,
        le=100,
        description=(
            "Porcentaje global de ajuste al puesto entre 0 y 100, ponderando: "
            "experiencia relevante (40%), habilidades técnicas (35%), "
            "formación y certificaciones (15%) y coherencia profesional (10%)."
        ),
    )
