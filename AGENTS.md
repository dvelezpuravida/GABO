# Instrucciones para agentes

## Contexto del proyecto

- Gabo el Garrobo es una aplicación de preguntas y respuestas de ASTICA construida con Streamlit.
- `app.py` implementa el login, la recuperación de documentos de ChromaDB y la generación de respuestas mediante Google Gemini.
- La base vectorial persistida se encuentra en `chroma_db/`; la aplicación espera que exista la colección `langchain`.
- `requirements.txt` contiene las dependencias de Python.
- `README.md` documenta la instalación, configuración, despliegue y solución de problemas.

## Configuración y ejecución

- Para el login, Streamlit necesita los secretos `user` y `password`.
- Para generar respuestas, configura `GEMINI_API_KEY` como secreto o utiliza `GOOGLE_API_KEY` como variable de entorno. También se puede ingresar la clave desde la barra lateral.
- En local, crea `.streamlit/secrets.toml` con esos valores; nunca agregues credenciales reales al repositorio.
- Instala dependencias con `python -m pip install -r requirements.txt` y ejecuta con `streamlit run app.py`.

## Pautas de cambios

- Conserva la colección `langchain` y los metadatos `source`: el código los utiliza para recuperar documentos y mostrar las fuentes.
- La app consulta el índice existente; no procesa ni vuelve a indexar PDFs al iniciar. Si cambia el formato o la ubicación de la base, actualiza también la configuración de carga y la documentación.
- Mantén la autenticación antes del contenido de la app y no muestres ni registres valores de secretos.
- Las consultas generales actualmente recuperan todos los fragmentos. Considera el tamaño del contexto y los límites de Gemini antes de aumentar el índice o cambiar la estrategia.
- Haz cambios acotados, sigue el estilo existente y actualiza `README.md` cuando cambien los pasos de instalación, configuración o despliegue.

## Validación

- Comprueba la sintaxis de `app.py` y ejecuta `git diff --check`.
- Si modificas recuperación de documentos, verifica consultas por número de acta, por nombre de archivo y consultas generales.
- No afirmes que la app fue probada en ejecución si no se ejecutó con sus dependencias, secretos y base vectorial disponibles.
