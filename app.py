import logging
import os
from pathlib import Path

import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
from google import genai

logger = logging.getLogger(__name__)
CHROMA_DB_PATH = Path(__file__).resolve().parent / "chroma_db"

# 1. Configuración de la interfaz con la identidad de Gabo el Garrobo
st.set_page_config(page_title="Gabo el Garrobo - ASTICA RAG", page_icon="🦎", layout="centered")

# Diseño de cabecera con la mascota
st.markdown("""
    <div style='text-align: center;'>
        <h1>🏹 ASTICA RAG Bot</h1>
        <h3>¡Hola! Soy <b>Gabo el Garrobo</b> 🦎, tu asistente de tiro con arco</h3>
        <p style='color: gray;'>Pregúntame sobre actas, respuestas de torneos, accesos o cualquier documento de ASTICA</p>
    </div>
""", unsafe_allow_html=True)

# 2. Inicializar recursos del sistema RAG de forma persistente o en caché
@st.cache_resource
def cargar_recursos():
    # Conectar a la BD vectorial local de Chroma
    client_chroma = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    collection_names = [
        str(getattr(item, "name", item))
        for item in client_chroma.list_collections()
    ]
    if not collection_names:
        db_file = CHROMA_DB_PATH / "chroma.sqlite3"
        db_status = (
            f"Existe chroma.sqlite3 ({db_file.stat().st_size} bytes)."
            if db_file.is_file()
            else "No existe chroma.sqlite3."
        )
        raise RuntimeError(
            "No se encontraron colecciones en Chroma. "
            f"Base esperada: {db_status}"
        )

    collections = [
        client_chroma.get_collection(name=name)
        for name in collection_names
    ]
    collection_counts = {
        collection.name: collection.count()
        for collection in collections
    }
    collections = [
        collection for collection in collections
        if collection_counts[collection.name] > 0
    ]
    if not collections:
        raise RuntimeError(
            f"Las colecciones encontradas están vacías en {CHROMA_DB_PATH}: "
            f"{collection_counts}."
        )
    logger.info(
        "Colecciones cargadas desde %s: %s",
        CHROMA_DB_PATH,
        {collection.name: collection_counts[collection.name] for collection in collections},
    )
    # Cargar modelo de embeddings después de validar la colección.
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model, collections

try:
    model, collections = cargar_recursos()
except Exception as e:
    logger.exception("No se pudo inicializar la base vectorial")
    st.error(
        f"No se pudo cargar la base vectorial en {CHROMA_DB_PATH}. "
        f"Verifica que la carpeta y las colecciones estén incluidas en el "
        f"despliegue. Detalle: {e}"
    )
    st.stop()

# 3. Configurar cliente de generación de forma segura
try:
    gemini_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    gemini_key = ""

if not gemini_key:
    gemini_key = os.environ.get("GOOGLE_API_KEY", "")
if not gemini_key:
    # Campo en la barra lateral para introducir la API Key si no se configuró como variable de entorno
    gemini_key = st.sidebar.text_input("Ingresa tu Gemini API Key", type="password")

# 4. Inicializar historial de chat de Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes anteriores con el avatar de Gabo
for message in st.session_state.messages:
    avatar = "🦎" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 5. Entrada del usuario
if user_query := st.chat_input("¿Cuáles son las tareas pendientes de la asociación?"):
    # Mostrar pregunta del usuario
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_query)

    # Generar la respuesta del asistente
    with st.chat_message("assistant", avatar="🦎"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🔍 *Gabo está buscando en todos los documentos de ASTICA...*")
        
        # A. Recuperar contexto de ChromaDB
        try:
            query_embedding = model.encode(user_query).tolist()
            candidates = []
            searched_collections = []
            for collection in collections:
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=4,
                    include=["documents", "metadatas", "distances"],
                )
                searched_collections.append(collection.name)
                documents = results["documents"][0]
                metadatas = results["metadatas"][0]
                distances = results["distances"][0]

                for doc, meta, distance in zip(documents, metadatas, distances):
                    if doc is None:
                        continue
                    source = (
                        meta.get("source", collection.name)
                        if meta
                        else collection.name
                    )
                    candidates.append((distance, source, doc))

            candidates.sort(key=lambda result: result[0])
            selected_results = candidates[:4]
            if selected_results:
                context = "\n\n---\n\n".join(
                    f"[Fuente: {source}]\n{doc}"
                    for _, source, doc in selected_results
                )
                logger.info(
                    "Consulta vectorial: %s fragmentos recuperados en %s",
                    len(selected_results),
                    ", ".join(searched_collections),
                )
                st.caption(
                    f"Diagnóstico de búsqueda: {len(selected_results)} "
                    f"fragmentos recuperados en {len(searched_collections)} "
                    "colección(es)."
                )
            else:
                context = ""
                logger.info(
                    "Consulta vectorial: no se recuperaron fragmentos en %s",
                    searched_collections,
                )
                st.caption(
                    "Diagnóstico de búsqueda: no se recuperaron fragmentos "
                    "en las colecciones."
                )
        except Exception as e:
            logger.exception("Error al consultar la base vectorial")
            st.error(f"Error al consultar la base de datos de Gabo: {e}")
            st.stop()

        # B. Responder usando Gemini si hay API Key disponible
        if gemini_key:
            try:
                client_gemini = genai.Client(api_key=gemini_key)
                prompt = f"""Eres Gabo el Garrobo, la mascota oficial y asistente experto de IA de la Asociación de Tiro con Arco de Alajuela (ASTICA).
Responde de manera amigable, entusiasta y muy clara en español, usando ocasionalmente analogías divertidas de lagartijas o tiro con arco sin perder el profesionalismo.

Tu tarea es responder la pregunta basándote ÚNICA y EXCLUSIVAMENTE en el contexto provisto abajo.

Reglas estrictas:
- Si la respuesta no se puede deducir del contexto, di textualmente: 'No encuentro información sobre esa consulta en los archivos que tengo guardados bajo mi piedra.' No inventes nada.
- Al final, menciona de qué documentos/fuentes provino la información.

Contexto:
{context}

Pregunta del usuario:
{user_query}

Respuesta de Gabo:"""
                
                response = client_gemini.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=prompt
                )
                full_response = response.text
            except Exception as e:
                full_response = f"¡Ups! Tuve un inconveniente al conectar con mi cerebro de IA: {e}"
        else:
            full_response = "⚠️ Por favor, introduce tu Gemini API Key en la barra lateral izquierda para que pueda responderte."

        # C. Mostrar respuesta
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
