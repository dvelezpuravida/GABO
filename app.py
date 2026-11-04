import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
from google import genai
import os
from pathlib import Path
import re

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
    # Cargar modelo de embeddings
    model = SentenceTransformer('all-MiniLM-L6-v2')
    # Conectar a la BD vectorial local de Chroma
    db_path = Path(__file__).resolve().parent / "chroma_db"
    client_chroma = chromadb.PersistentClient(path=str(db_path))
    collection = client_chroma.get_collection(name="langchain")
    metadata = collection.get(include=["metadatas"])["metadatas"] or []
    sources = sorted({
        item["source"]
        for item in metadata
        if item and item.get("source")
    })
    return model, collection, sources


def buscar_fuente_consultada(query, sources):
    normalized_query = query.casefold()
    for source in sources:
        if Path(source).stem.casefold() in normalized_query:
            return source

    acta_match = re.search(
        r"\bacta\s*(?:n[úu]m(?:ero)?\.?\s*)?0*(\d{1,3})\b",
        query,
        flags=re.IGNORECASE,
    )
    if not acta_match:
        return None

    acta_number = int(acta_match.group(1))
    for source in sources:
        range_match = re.match(
            r"^\s*0*(\d{1,3})(?:\s*[-–]\s*0*(\d{1,3}))?",
            source,
        )
        if range_match:
            first_number = int(range_match.group(1))
            last_number = int(range_match.group(2) or first_number)
            if first_number <= acta_number <= last_number:
                return source
    return None

try:
    model, collection, sources = cargar_recursos()
except Exception as e:
    st.error(f"Error inicializando la base de datos vectorial: {e}")
    st.stop()

if collection.count() == 0:
    st.error("La colección 'langchain' existe, pero no contiene documentos indexados.")
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
        
        list_files_request = bool(re.search(
            r"\b(?:archivos?|documentos?)\b.*\b(?:disponibles|tienes|guardados|cargados|indexados)\b",
            user_query,
            flags=re.IGNORECASE,
        ))

        # A. Recuperar contexto de ChromaDB
        try:
            formatted_context_list = []
            requested_source = buscar_fuente_consultada(user_query, sources)
            if list_files_request:
                context = ""
            elif requested_source:
                documents = collection.get(
                    where={"source": requested_source},
                    include=["documents", "metadatas"],
                )
                for doc, meta in zip(documents["documents"], documents["metadatas"]):
                    source = meta.get("source", requested_source) if meta else requested_source
                    formatted_context_list.append(f"[Fuente: {source}]\n{doc}")
            else:
                query_embedding = model.encode(user_query).tolist()
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=collection.count(),
                )
                if results and results["documents"] and results["documents"][0]:
                    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                        source = meta.get("source", "Documento sin nombre") if meta else "Documento sin nombre"
                        formatted_context_list.append(f"[Fuente: {source}]\n{doc}")
            context = "\n\n---\n\n".join(formatted_context_list)
        except Exception as e:
            context = ""
            st.error(f"Error al consultar la base de datos de Gabo: {e}")

        # B. Responder usando Gemini si hay API Key disponible
        if list_files_request:
            if sources:
                full_response = "Estos son todos los documentos que tengo indexados:\n\n"
                full_response += "\n".join(f"- **{source}**" for source in sources)
            else:
                full_response = "No hay documentos indexados en este momento."
        elif gemini_key:
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
