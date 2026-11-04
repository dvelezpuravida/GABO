# Gabo el Garrobo — ASTICA RAG

Aplicación de preguntas y respuestas para consultar documentos de la Asociación de Tiro con Arco de Alajuela (ASTICA). Está construida con Streamlit, utiliza ChromaDB para recuperar fragmentos de documentos y Google Gemini para redactar respuestas en español.

## Funcionalidades

- Login con un usuario y contraseña configurados en los secretos de Streamlit.
- Consultas sobre documentos indexados en la base vectorial.
- Recuperación de todos los fragmentos de un acta cuando se pregunta por su número o nombre de archivo.
- Listado directo de los documentos indexados al preguntar por los archivos disponibles.
- Respuestas basadas en el contexto recuperado, con indicación de las fuentes.

## Requisitos

- Python 3.10 o posterior.
- Las dependencias listadas en [`requirements.txt`](./requirements.txt).
- Secretos de acceso y una clave de Google Gemini.

## Ejecución local en Windows

Desde la carpeta del proyecto, crea y activa un entorno virtual e instala las dependencias:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Configura los secretos localmente en `.streamlit/secrets.toml`:

```toml
user = "tu_usuario"
password = "una_contraseña_segura"
GEMINI_API_KEY = "tu_clave_de_google_gemini"
```

Luego inicia la aplicación:

```powershell
streamlit run app.py
```

No agregues `secrets.toml`, claves API ni contraseñas reales al repositorio.

## Despliegue en Streamlit Community Cloud

1. Publica este repositorio en GitHub.
2. En Streamlit Community Cloud, crea una aplicación apuntando al repositorio y selecciona `app.py` como archivo principal.
3. En **App settings → Secrets**, configura:

   ```toml
   user = "tu_usuario"
   password = "una_contraseña_segura"
   GEMINI_API_KEY = "tu_clave_de_google_gemini"
   ```

4. Guarda la configuración y espera a que Streamlit termine el despliegue.

La app requiere los secretos `user` y `password`; si faltan o están vacíos, bloquea el acceso. `GEMINI_API_KEY` es la clave usada para generar respuestas. Si no está configurada como secreto, también se puede ingresar desde la barra lateral o establecer la variable de entorno `GOOGLE_API_KEY`.

## Base de documentos

La aplicación abre la base persistente de ChromaDB ubicada en `chroma_db/` y la colección `langchain`. Esa carpeta debe estar disponible en el entorno de despliegue y contener tanto `chroma.sqlite3` como los archivos de segmentos de Chroma. La app no ingiere ni indexa archivos PDF al iniciar; consulta los documentos que ya están representados en esa colección.

Si actualizas o reconstruyes el índice, conserva la colección `langchain` y los metadatos `source` de cada fragmento para que las fuentes aparezcan correctamente. Una colección ausente o vacía impide iniciar la aplicación.

## Uso y limitaciones

- Pregunta, por ejemplo, “resumen del acta 83” o escribe el nombre de un documento indexado.
- Pregunta “archivos disponibles” para ver el catálogo de fuentes que contiene el índice.
- La búsqueda general usa similitud semántica y actualmente envía todos los fragmentos indexados como contexto a Gemini. Un índice grande puede hacer más lentas las consultas o superar los límites de contexto del servicio.
- Gemini debe poder responder desde el contexto proporcionado; si no encuentra respaldo en los documentos, se le indica que lo diga en lugar de inventar información.

## Solución de problemas

- **Faltan los secretos `user` y `password`:** agrégalos en la configuración de Secrets de Streamlit y reinicia o vuelve a desplegar la app.
- **Error al inicializar ChromaDB o colección vacía:** revisa que `chroma_db/` esté incluido en el repositorio y que contenga una base válida con la colección `langchain`.
- **No se conecta con Gemini:** revisa que `GEMINI_API_KEY` sea válida o ingresa la clave desde la barra lateral.
- **La respuesta no encuentra información:** confirma que el documento y su texto estén indexados en `langchain`; que el archivo aparezca en el catálogo no garantiza que contenga el dato específico solicitado.
