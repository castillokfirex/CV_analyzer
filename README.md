# 📄 CV_analyzer — Analizador de Currículums con IA (Google Gemini)

Aplicación web construida con **Streamlit**, **Google Gemini (`gemini-3.8-flash`)** y **Pydantic** que evalúa el grado de ajuste de un currículum en PDF frente a la descripción de un puesto de trabajo.

---

## ✨ Características Principales

- **Extracción de PDF en memoria (`pypdf`)**: lectura multipágina con detección de archivos dañados, protegidos o escaneados sin capa de texto, y límite seguro de longitud.
- **Evaluación estructurada con Gemini (`google-genai`)**: uso de la API de Interactions con esquema JSON estricto (`AnalisisCV`) y validación con Pydantic.
- **Ponderación de criterios de selección**:
  - Experiencia relevante: **40 %**
  - Habilidades técnicas: **35 %**
  - Formación y certificaciones: **15 %**
  - Coherencia profesional: **10 %**
- **Interfaz interactiva en Streamlit**:
  - Persistencia del resultado en `st.session_state`.
  - Botón **Limpiar** que reinicia tanto el texto como el archivo PDF cargado.
  - Botón **Usar ejemplo** para probar rápidamente la aplicación.
- **Entorno Docker listo para usar**: incluye `Dockerfile` independiente y `docker-compose.yml` con servicios de aplicación, PostgreSQL y pgAdmin.

---

## 🗂️ Estructura del Proyecto

```text
CV_analyzer/
├── .env.example                     # Plantilla de variables de entorno
├── requirements.txt                 # Dependencias del proyecto
├── Dockerfile                       # Imagen con Python 3.12-slim
├── docker-compose.yml               # Servicios: app, postgres y pgadmin
└── app/intermedio/cv_analyzer/
    ├── README.md                    # Documentación detallada del módulo
    ├── app.py                       # Punto de entrada de Streamlit
    ├── .streamlit/config.toml       # Tema y configuración del servidor
    ├── models/cv_model.py           # Esquema Pydantic AnalisisCV
    ├── prompts/cv_prompts.py        # Prompt de reclutador y plantilla
    ├── services/
    │   ├── pdf_processor.py         # Extracción de texto desde PDF
    │   ├── cv_evaluator.py          # Cliente e invocación a Google Gemini
    │   └── scoring.py               # Umbrales de evaluación y recomendación
    └── ui/streamlit_ui.py           # Interfaz de usuario en Streamlit
```

---

## 🚀 Inicio Rápido (Ejecución Local)

### 1. Crear entorno virtual e instalar dependencias

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 2. Configurar tu clave de Google Gemini

Obtén una clave gratuita en [Google AI Studio](https://aistudio.google.com/apikey) y expórtala en tu terminal:

```powershell
$env:GEMINI_API_KEY = "tu_clave_de_gemini"
```

### 3. Ejecutar la aplicación

```powershell
cd app/intermedio/cv_analyzer
python -m streamlit run app.py --server.port=8501
```

Abre <http://localhost:8501> en tu navegador.

---

## 🐳 Ejecución con Docker

```powershell
docker build -t cv-analyzer .
docker run --rm -p 8501:8501 -e GEMINI_API_KEY="tu_clave_de_gemini" cv-analyzer
```

Para más detalles sobre `docker-compose`, umbrales y resolución de problemas, consulta [app/intermedio/cv_analyzer/README.md](app/intermedio/cv_analyzer/README.md).
