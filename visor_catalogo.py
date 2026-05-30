import streamlit as st
import time
from io import BytesIO
import google.generativeai as genai
from scjn_scraper import buscar_normatividades_scjn

# --- INICIALIZACIÓN DE MEMORIA SEGURA ---
if "expediente" not in st.session_state: st.session_state.expediente = {}
if "resultados_busqueda" not in st.session_state: st.session_state.resultados_busqueda = []

st.set_page_config(layout="wide")
st.title("Ágora - Inteligencia Normativa")

col1, col2 = st.columns(2)

# --- PANEL DE BÚSQUEDA ---
with col1:
    termino = st.text_input("Buscar normatividad en SCJN:")
    if st.button("Buscar en SCJN"):
        with st.spinner("Conectando con la Corte..."):
            # Aquí llamamos a tu scjn_scraper.py
            st.session_state.resultados_busqueda = buscar_normatividades_scjn(termino)
            st.rerun()

    for idx, item in enumerate(st.session_state.resultados_busqueda):
        st.markdown(f"**{item['Normatividad']}**")
        if st.button(f"Añadir", key=f"btn_{idx}"):
            st.session_state.expediente[item['Normatividad']] = item['Url Descarga']
            st.success("¡Añadido!")

# --- PANEL DE ANÁLISIS ---
with col2:
    st.subheader("🤖 Consultor Jurídico")
    pregunta = st.chat_input("Escribe tu duda sobre las leyes añadidas...")
    if pregunta:
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-flash-latest')
            
            # Unimos los textos del expediente
            contexto = "\n".join([f"Ley: {k}, Fuente: {v}" for k, v in st.session_state.expediente.items()])
            
            respuesta = model.generate_content(f"Contexto: {contexto}\n\nPregunta: {pregunta}")
            st.markdown(respuesta.text)
        except Exception as e:
            st.error(f"Error en IA: {e}")
