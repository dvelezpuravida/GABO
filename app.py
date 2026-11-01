import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
from google import genai
import os

# 1. Configuración de la interfaz con la identidad de Gabo el Garrobo
st.set_page_config(page_title="Gabo el Garrobo - ASTICA RAG", page_icon="🦎", layout="centered")

# Diseño de cabecera con la mascota
st.markdown("""
    <div style='text-align: center;'>
        <h1>🏹 ASTICA RAG Bot</h1>
        <h3>¡Hola! Soy <b>Gabo el Garrobo</b> 🦎, tu asistente de tiro con arco</h3>
        <p style='color: gray;'>Pregúntame cualquier detalle sobre las actas oficiales de la Junta Directiva</p>
    </div>
""", unsafe_allow_html=True)

# 2. Inicializar recursos del sistema RAG de forma persistente o en caché
@st.cache_resource
def cargar_recursos_rag():
    # Cargar modelo de embeddings
    model = SentenceTransformer('all-MiniLM-L6-v2')
    # Conectar a la BD vectorial local de Chroma (se sube al Git junto con el proyecto)
    client_chroma = chromadb.PersistentClient(path="./chroma_db")
    collection = client_chroma.get_or_create_collection(name="actas_asociacion")
    return model, collection

model, collection = cargar_recursos_rag()

# 3. Configurar cliente de generación de forma segura
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
if user_query := st.chat_input("¿Qué acuerdo se tomó sobre el servicio de alimentación?"):
    # Mostrar pregunta del usuario
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_query)

    # Generar la respuesta del asistente
    with st.chat_message("assistant", avatar="🦎"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🔍 *Gabo está revisando las actas de ASTICA...*")
        
        # A. Recuperar contexto de ChromaDB
        try:
            query_embedding = model.encode(user_query).tolist()
            results = collection.query(query_embeddings=[query_embedding], n_results=3)
            
            formatted_context_list = []
            for idx in range(len(results['documents'][0])):
                doc = results['documents'][0][idx]
                meta = results['metadatas'][0][idx]
                formatted_context_list.append(f"[Fuente: {meta['source']} - Fragmento {meta['index']}]\n{doc}")
            context = "\n\n---\n\n".join(formatted_context_list)
        except Exception as e:
            context = ""
            st.error(f"Error al consultar la base de datos de Gabo: {e}")

        # B. Responder usando Gemini si hay API Key disponible
        if gemini_key:
            try:
                client_gemini = genai.Client(api_key=gemini_key)
                prompt = f"""Eres Gabo el Garrobo, la mascota oficial y asistente experto de IA de la Asociación de Tiro con Arco de Alajuela (ASTICA).
Responde de manera amigable, entusiasta y muy clara en español, usando ocasionalmente analogías divertidas de lagartijas o tiro con arco sin perder el profesionalismo.

Tu tarea es responder la pregunta basándote ÚNICA y EXCLUSIVAMENTE en el contexto provisto abajo.

Reglas estrictas:
- Si la respuesta no se puede deducir del contexto, di textualmente: 'No encuentro información sobre esa consulta en las actas que tengo guardadas bajo mi piedra.' No inventes nada.
- Al final, menciona de qué fragmentos provino la información.

Contexto:
{context}

Pregunta del usuario:
{user_query}

Respuesta de Gabo:"""
                
                response = client_gemini.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                full_response = response.text
            except Exception as e:
                full_response = f"¡Ups! Tuve un inconveniente al conectar con el cerebro de Gemini: {e}"
        else:
            full_response = "⚠️ Por favor, introduce tu Gemini API Key en la barra lateral izquierda para que pueda responderte."

        # C. Mostrar respuesta
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
