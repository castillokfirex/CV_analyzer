# Analizador de currículums con IA (Google Gemini)

Aplicación de **Streamlit** que compara un currículum en PDF con la descripción de un puesto. Extrae el texto del documento, lo envía a **Google Gemini** (`gemini-3.8-flash` por defecto) mediante el SDK oficial `google-genai` con salida estructurada JSON y muestra un análisis completo del candidato validado con **Pydantic**.

## Funcionalidades

- Carga de un CV en formato PDF con texto seleccionable.
- Entrada de requisitos y responsabilidades del puesto (con opción de autocompletar un ejemplo).
- Extracción de nombre, años de experiencia, educación y habilidades relevantes.
- Identificación de fortalezas y áreas de mejora.
- Estimación del porcentaje de ajuste al puesto, entre 0 y 100.
- Presentación de una recomendación de contratación según el resultado.
- Persistencia del análisis en la sesión activa (`st.session_state`) y limpieza real del formulario y del archivo PDF cargado.

El módulo no utiliza una base de datos ni implementa exportación de análisis. El botón **Guardar Análisis** muestra un aviso de funcionalidad en desarrollo.

## Funcionamiento

1. `app.py` llama a `main()` de la interfaz de Streamlit (`ui/streamlit_ui.py`).
2. El usuario carga un PDF y escribe la descripción del puesto.
3. Al pulsar **Analizar Candidato**, la interfaz comprueba que existan ambas entradas.
4. `extraer_texto_pdf()` lee el archivo en memoria con `pypdf`, recorre sus páginas y concatena el texto con separadores `--- Página N ---`. Si no encuentra texto, el PDF está cifrado o falla la lectura, devuelve un mensaje de error que la interfaz muestra antes de detener el proceso.
5. `crear_sistema_prompts()` combina las instrucciones del reclutador y el mensaje que contiene el CV y la descripción del puesto.
6. `crear_evaluador_cv()` verifica `GEMINI_API_KEY` e inicializa el cliente `genai.Client`.
7. `evaluar_candidato()` invoca `client.interactions.create()` con `model="gemini-3.8-flash"` (configurable vía `GEMINI_MODEL`), `response_format` vinculado al esquema JSON de `AnalisisCV`, `thinking_level="low"` y `store=False`, validando la salida con `AnalisisCV.model_validate_json()`.
8. La interfaz guarda el análisis en `st.session_state` y muestra el porcentaje de ajuste, el perfil del candidato, las habilidades, las fortalezas, las áreas de desarrollo y la recomendación final.

### Criterios de evaluación

El prompt solicita los siguientes pesos:

| Criterio | Peso solicitado |
| --- | --- |
| Experiencia relevante | 40 % |
| Habilidades técnicas | 35 % |
| Formación y certificaciones | 15 % |
| Coherencia profesional | 10 % |

La interfaz utiliza dos conjuntos de umbrales (`services/scoring.py`):

| Porcentaje | Evaluación principal |
| --- | --- |
| 80–100 | Excelente |
| 60–79 | Bueno |
| 40–59 | Regular |
| 0–39 | Bajo |

| Porcentaje | Recomendación final |
| --- | --- |
| 70–100 | Candidato recomendado |
| 50–69 | Candidato con potencial |
| 0–49 | Candidato no recomendado |

Por ejemplo, un resultado de 65 % aparece como **Bueno** en la evaluación principal y como **Candidato con potencial** en la recomendación final.

## Estructura

```text
CV_analyzer/
├── .env.example                     # Plantilla de variables de entorno
├── .gitignore
├── .dockerignore
├── requirements.txt                 # Dependencias con versiones mínimas fijadas
├── Dockerfile                       # Imagen base con Python 3.12-slim
├── docker-compose.yml               # Entorno compartido: app, PostgreSQL y pgAdmin
└── app/intermedio/cv_analyzer/
    ├── README.md
    ├── app.py                       # Punto de entrada de Streamlit
    ├── .streamlit/
    │   └── config.toml              # Configuración visual y límite de subida (10 MB)
    ├── models/
    │   └── cv_model.py              # Esquema Pydantic AnalisisCV
    ├── prompts/
    │   └── cv_prompts.py            # Instrucciones y plantilla de evaluación
    ├── services/
    │   ├── pdf_processor.py         # Extracción y validación de texto del PDF
    │   ├── cv_evaluator.py          # Configuración e invocación de Gemini
    │   └── scoring.py               # Umbrales de evaluación y recomendación
    └── ui/
        └── streamlit_ui.py          # Entradas, validaciones, sesión y presentación
```

### Modelo de salida (`AnalisisCV`)

Todos los campos de `AnalisisCV` son obligatorios:

| Campo | Tipo | Contenido |
| --- | --- | --- |
| `nombre_candidato` | `str` | Nombre extraído del CV |
| `experiencia_años` | `int` | Años de experiencia relevante (`>= 0`) |
| `habilidades_clave` | `list[str]` | Habilidades relevantes para el puesto |
| `education` | `str` | Nivel educativo y especialización |
| `experiencia_relevante` | `str` | Resumen de experiencia relacionada |
| `fortalezas` | `list[str]` | Fortalezas del candidato |
| `areas_mejora` | `list[str]` | Áreas de desarrollo |
| `porcentaje_ajuste` | `int` | Ajuste al puesto, validado entre 0 y 100 |

## Requisitos

- Python 3.12+ (referencia del `Dockerfile`).
- Una clave de API de Google Gemini (`GEMINI_API_KEY`) obtenida en [Google AI Studio](https://aistudio.google.com/apikey).
- Conexión a Internet para las llamadas al modelo.
- Un PDF con texto extraíble; no se implementa OCR para documentos escaneados.

## Ejecución local

Los siguientes comandos se ejecutan desde la raíz del repositorio, salvo donde se indica el cambio de directorio.

### 1. Crear un entorno e instalar dependencias

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

En Windows PowerShell, activa el entorno con:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Configurar la clave de Gemini

En macOS o Linux:

```bash
export GEMINI_API_KEY="tu_clave_de_gemini"
```

En Windows PowerShell:

```powershell
$env:GEMINI_API_KEY = "tu_clave_de_gemini"
```

Opcionalmente puedes elegir otro modelo compatible (por defecto `gemini-3.8-flash`, o por ejemplo `gemini-3.5-flash-lite`):

```powershell
$env:GEMINI_MODEL = "gemini-3.8-flash"
```

### 3. Iniciar Streamlit

```bash
cd app/intermedio/cv_analyzer
python -m streamlit run app.py --server.port=8501
```

Abre <http://localhost:8501>.

## Ejecución con Docker

### Contenedor independiente

Desde la raíz del repositorio, con `GEMINI_API_KEY` ya definida en la terminal:

```bash
docker build -t cv-analyzer .
docker run --rm -p 8501:8501 \
  -e GEMINI_API_KEY \
  cv-analyzer
```

Abre <http://localhost:8501>.

### Entorno Docker Compose

1. Copia `.env.example` a `.env` y define tu `GEMINI_API_KEY`:

```bash
cp .env.example .env
```

2. Levanta los servicios e inicia Streamlit:

```bash
docker compose up -d --build
docker compose exec -w /app/app/intermedio/cv_analyzer app \
  python -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501
```

Para detener el entorno:

```bash
docker compose down
```

## Mejoras implementadas sobre el diseño original

- **Manejo robusto de errores en el evaluador:** se reemplazó el bloque `except` defectuoso (que tenía errores tipográficos `fotalezas` y `porcetaje_ajuste`) por la excepción controlada `EvaluacionError` con registro en logs y mensajes claros en la interfaz.
- **Persistencia en sesión (`st.session_state`):** el resultado del análisis se conserva durante interacciones posteriores (como pulsar **Guardar Análisis**).
- **Botón Limpiar funcional:** reinicia el análisis, limpia la descripción del puesto y resetea el `st.file_uploader` mediante clave dinámica.
- **Control de longitud de PDF:** trunca de forma segura documentos que excedan 60 000 caracteres.
