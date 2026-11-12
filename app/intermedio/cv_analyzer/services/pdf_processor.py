"""Servicio de extracción y validación de texto desde archivos PDF."""

from io import BytesIO
from typing import BinaryIO, Union

from pypdf import PdfReader
from pypdf.errors import PdfReadError

MAX_CARACTERES_CV = 60_000


def extraer_texto_pdf(archivo_pdf: Union[BinaryIO, bytes]) -> str:
    """Extrae y concatena el texto de todas las páginas de un archivo PDF.

    Recorre las páginas del documento agregando separadores de página. Si el
    documento está vacío, escaneado (sin capa de texto) o dañado, devuelve un
    mensaje que comienza con ``"Error:"`` para que la interfaz detenga el flujo
    y lo muestre al usuario.

    Args:
        archivo_pdf: Objeto de archivo en memoria (como ``UploadedFile`` de
            Streamlit, ``BytesIO``) o bytes crudos del PDF.

    Returns:
        El texto extraído con separadores de página, o un mensaje que inicia
        con ``"Error:"`` en caso de fallo.
    """
    if archivo_pdf is None:
        return "Error: No se proporcionó ningún archivo PDF."

    try:
        if isinstance(archivo_pdf, (bytes, bytearray)):
            flujo = BytesIO(archivo_pdf)
        else:
            if hasattr(archivo_pdf, "seek"):
                archivo_pdf.seek(0)
            flujo = archivo_pdf

        lector = PdfReader(flujo)

        if lector.is_encrypted:
            try:
                lector.decrypt("")
            except Exception:
                return (
                    "Error: El archivo PDF está protegido con contraseña y no "
                    "puede leerse. Sube un PDF sin cifrado."
                )

        total_paginas = len(lector.pages)
        if total_paginas == 0:
            return "Error: El archivo PDF no contiene páginas."

        paginas_texto: list[str] = []
        for indice, pagina in enumerate(lector.pages, start=1):
            texto_pagina = (pagina.extract_text() or "").strip()
            if texto_pagina:
                paginas_texto.append(f"--- Página {indice} ---\n{texto_pagina}")

        texto_completo = "\n\n".join(paginas_texto).strip()

        if not texto_completo:
            return (
                "Error: No se pudo extraer texto del PDF. Es posible que sea un "
                "documento escaneado (compuesto solo por imágenes); esta aplicación "
                "no implementa OCR. Utiliza un PDF con texto seleccionable."
            )

        if len(texto_completo) > MAX_CARACTERES_CV:
            texto_completo = (
                texto_completo[:MAX_CARACTERES_CV]
                + "\n\n[Nota: Texto truncado automáticamente al superar el límite de "
                f"{MAX_CARACTERES_CV:,} caracteres.]"
            )

        return texto_completo

    except PdfReadError as exc:
        return f"Error: El archivo no es un PDF válido o está dañado ({exc})."
    except Exception as exc:
        return f"Error al procesar el archivo PDF: {exc}"
