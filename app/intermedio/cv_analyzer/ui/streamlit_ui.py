"""Interfaz de usuario en Streamlit para el Analizador de Currículums con IA."""

import html
import os

import streamlit as st

from models.cv_model import AnalisisCV
from services.cv_evaluator import (
    EvaluacionError,
    evaluar_candidato,
    obtener_modelo_configurado,
)
from services.pdf_processor import extraer_texto_pdf
from services.scoring import (
    obtener_evaluacion_principal,
    obtener_recomendacion_final,
)

EJEMPLO_DESCRIPCION = (
    "Puesto: Desarrollador Python\n"
    "Requisitos obligatorios: 3 años de experiencia, Python, APIs REST y PostgreSQL.\n"
    "Deseables: Docker, pruebas automatizadas y experiencia con IA generativa.\n"
    "Responsabilidades: desarrollar servicios, integrar APIs y mantener pruebas."
)


def _inicializar_estado() -> None:
    """Inicializa las claves necesarias en st.session_state."""
    if "analisis_actual" not in st.session_state:
        st.session_state.analisis_actual = None
    if "texto_cv_extraido" not in st.session_state:
        st.session_state.texto_cv_extraido = ""
    if "nombre_archivo_cv" not in st.session_state:
        st.session_state.nombre_archivo_cv = ""
    if "descripcion_puesto" not in st.session_state:
        st.session_state.descripcion_puesto = ""
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0


def _limpiar_formulario() -> None:
    """Reinicia el estado del formulario, el archivo PDF cargado y el análisis."""
    st.session_state.analisis_actual = None
    st.session_state.texto_cv_extraido = ""
    st.session_state.nombre_archivo_cv = ""
    st.session_state.descripcion_puesto = ""
    st.session_state.uploader_key += 1


def _cargar_ejemplo() -> None:
    """Rellena el área de texto con la descripción de puesto de ejemplo."""
    st.session_state.descripcion_puesto = EJEMPLO_DESCRIPCION


def _renderizar_barra_lateral() -> None:
    """Muestra el estado de configuración y los criterios de evaluación en el sidebar."""
    with st.sidebar:
        st.header("⚙️ Configuración y Criterios")

        api_key_configurada = bool(os.getenv("GEMINI_API_KEY", "").strip())
        modelo = obtener_modelo_configurado()

        if api_key_configurada:
            st.success("Clave `GEMINI_API_KEY` detectada")
        else:
            st.warning(
                "⚠️ No se detectó `GEMINI_API_KEY` en el entorno. "
                "Configúrala antes de analizar un candidato."
            )

        st.caption(f"**Modelo activo:** `{modelo}`")
        st.divider()

        st.subheader("📊 Pesos de Evaluación")
        st.markdown(
            """
            - **Experiencia relevante:** 40 %
            - **Habilidades técnicas:** 35 %
            - **Formación y certificaciones:** 15 %
            - **Coherencia profesional:** 10 %
            """
        )
        st.divider()

        st.subheader("🎯 Escalas de Interpretación")
        st.markdown(
            """
            **Evaluación principal:**
            - `80–100 %`: Excelente
            - `60–79 %`: Bueno
            - `40–59 %`: Regular
            - `0–39 %`: Bajo

            **Recomendación final:**
            - `70–100 %`: Candidato recomendado
            - `50–69 %`: Candidato con potencial
            - `0–49 %`: Candidato no recomendado
            """
        )


def _renderizar_chips_habilidades(habilidades: list[str]) -> None:
    """Muestra las habilidades clave como etiquetas estilizadas."""
    if not habilidades:
        st.info("No se identificaron habilidades relevantes específicas.")
        return

    chips_html = " ".join(
        f'<span style="display:inline-block;background-color:#eff6ff;'
        f'color:#1d4ed8;border:1px solid #bfdbfe;border-radius:9999px;'
        f'padding:4px 12px;margin:4px 4px 4px 0;font-size:0.88rem;'
        f'font-weight:500;">{html.escape(habilidad)}</span>'
        for habilidad in habilidades
    )
    st.markdown(chips_html, unsafe_allow_html=True)


def _renderizar_resultado(analisis: AnalisisCV) -> None:
    """Presenta en pantalla el resultado estructurado de la evaluación."""
    porcentaje = analisis.porcentaje_ajuste
    etiqueta_eval, color_eval = obtener_evaluacion_principal(porcentaje)
    titulo_rec, detalle_rec, nivel_alerta = obtener_recomendacion_final(porcentaje)

    st.divider()
    st.header("📋 Resultado del Análisis")

    col_metrica, col_barra = st.columns([1, 2])
    with col_metrica:
        st.metric(
            label="Porcentaje de Ajuste al Puesto",
            value=f"{porcentaje} %",
            delta=f"Evaluación: {etiqueta_eval}",
        )
    with col_barra:
        st.markdown(
            f"**Evaluación principal:** "
            f"<span style='color:{color_eval};font-weight:700;font-size:1.15rem;'>"
            f"{etiqueta_eval} ({porcentaje} %)</span>",
            unsafe_allow_html=True,
        )
        st.progress(max(0, min(100, porcentaje)) / 100.0)
        if st.session_state.nombre_archivo_cv:
            st.caption(f"Documento analizado: `{st.session_state.nombre_archivo_cv}`")

    st.subheader("👤 Perfil del Candidato")
    col_p1, col_p2, col_p3 = st.columns([2, 1, 2])
    with col_p1:
        st.markdown(f"**Nombre:**\n\n{analisis.nombre_candidato}")
    with col_p2:
        unidad = "año" if analisis.experiencia_años == 1 else "años"
        st.markdown(
            f"**Experiencia relevante:**\n\n{analisis.experiencia_años} {unidad}"
        )
    with col_p3:
        st.markdown(f"**Formación / Educación:**\n\n{analisis.education}")

    st.markdown("**Resumen de experiencia relevante:**")
    st.write(analisis.experiencia_relevante)

    st.subheader("🛠️ Habilidades Clave Identificadas")
    _renderizar_chips_habilidades(analisis.habilidades_clave)

    st.subheader("⚖️ Fortalezas y Áreas de Desarrollo")
    col_fort, col_mej = st.columns(2)
    with col_fort:
        st.markdown("#### ✅ Fortalezas")
        if analisis.fortalezas:
            for fortaleza in analisis.fortalezas:
                st.markdown(f"- {fortaleza}")
        else:
            st.write("No se registraron fortalezas destacadas.")

    with col_mej:
        st.markdown("#### 📈 Áreas de Mejora")
        if analisis.areas_mejora:
            for area in analisis.areas_mejora:
                st.markdown(f"- {area}")
        else:
            st.write("No se registraron áreas de mejora específicas.")

    st.subheader("🏁 Recomendación Final")
    mensaje_recomendacion = f"**{titulo_rec} ({porcentaje} %)** — {detalle_rec}"
    if nivel_alerta == "success":
        st.success(mensaje_recomendacion, icon="✅")
    elif nivel_alerta == "warning":
        st.warning(mensaje_recomendacion, icon="⚠️")
    else:
        st.error(mensaje_recomendacion, icon="❌")

    if st.session_state.texto_cv_extraido:
        with st.expander("🔎 Ver texto extraído del PDF"):
            st.text(st.session_state.texto_cv_extraido)

    col_guardar, _ = st.columns([1, 3])
    with col_guardar:
        if st.button("💾 Guardar Análisis", use_container_width=True):
            st.info(
                "ℹ️ Funcionalidad en desarrollo: el almacenamiento y la exportación "
                "de análisis estarán disponibles en una próxima versión."
            )


def main() -> None:
    """Punto de entrada principal de la interfaz de Streamlit."""
    st.set_page_config(
        page_title="Analizador de Currículums con IA",
        page_icon="📄",
        layout="wide",
    )

    _inicializar_estado()
    _renderizar_barra_lateral()

    st.title("📄 Analizador de Currículums con IA")
    st.markdown(
        "Compara un currículum en formato **PDF** con la descripción de un puesto "
        "mediante **Google Gemini** y obtén una evaluación estructurada del ajuste del candidato."
    )

    col_izq, col_der = st.columns(2)

    with col_izq:
        st.subheader("1. Cargar Currículum (PDF)")
        archivo_pdf = st.file_uploader(
            "Selecciona un archivo PDF con texto seleccionable",
            type=["pdf"],
            key=f"cv_uploader_{st.session_state.uploader_key}",
            help="No se admite OCR sobre documentos escaneados compuestos únicamente por imágenes.",
        )

    with col_der:
        encabezado_der, boton_ej = st.columns([2, 1])
        with encabezado_der:
            st.subheader("2. Descripción del Puesto")
        with boton_ej:
            st.button(
                "📝 Usar ejemplo",
                on_click=_cargar_ejemplo,
                use_container_width=True,
                help="Rellena el campo con una descripción de puesto de ejemplo.",
            )

        descripcion_puesto = st.text_area(
            "Requisitos obligatorios, deseables y responsabilidades",
            key="descripcion_puesto",
            height=190,
            placeholder=EJEMPLO_DESCRIPCION,
        )

    col_btn_analizar, col_btn_limpiar, _ = st.columns([1, 1, 2])
    with col_btn_analizar:
        analizar_clic = st.button(
            "🔍 Analizar Candidato",
            type="primary",
            use_container_width=True,
        )
    with col_btn_limpiar:
        st.button(
            "🧹 Limpiar",
            on_click=_limpiar_formulario,
            use_container_width=True,
        )

    if analizar_clic:
        if archivo_pdf is None and not descripcion_puesto.strip():
            st.error(
                "Por favor, carga un currículum en PDF y escribe la descripción del puesto."
            )
            return
        if archivo_pdf is None:
            st.error("Por favor, carga un archivo PDF con el currículum del candidato.")
            return
        if not descripcion_puesto.strip():
            st.error("Por favor, ingresa la descripción y requisitos del puesto.")
            return

        with st.spinner("Extrayendo texto del PDF..."):
            texto_cv = extraer_texto_pdf(archivo_pdf)

        if texto_cv.startswith("Error"):
            st.error(texto_cv)
            return

        with st.spinner("Evaluando candidato con IA (Gemini)..."):
            try:
                resultado = evaluar_candidato(texto_cv, descripcion_puesto)
                st.session_state.analisis_actual = resultado
                st.session_state.texto_cv_extraido = texto_cv
                st.session_state.nombre_archivo_cv = archivo_pdf.name
            except EvaluacionError as exc:
                st.error(f"Error en la evaluación: {exc}")
                return

    if st.session_state.analisis_actual is not None:
        _renderizar_resultado(st.session_state.analisis_actual)
