import streamlit as st
import datetime
import time

# Configuración de la página
st.set_page_config(page_title="Mi Primer Reloj", page_icon="⏰", layout="centered")

# Título de la app
st.title("⏰ Mi Primer Reloj en Streamlit")

# Contenedor para el reloj para evitar saltos visuales
placeholder = st.empty()

# Bucle infinito para actualizar el reloj en tiempo real
while True:
    now = datetime.datetime.now().strftime("%H:%M:%S")
    with placeholder.container():
        st.markdown(
            f"""
            <div style='text-align: center;'>
                <h1 style='font-size: 80px; color: #FF4B4B; font-family: monospace;'>
                    {now}
                </h1>
                <p style='color: gray;'>Actualizándose en tiempo real</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    time.sleep(1)
    st.rerun()
