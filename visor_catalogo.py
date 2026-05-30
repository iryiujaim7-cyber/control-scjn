import streamlit as st
import google.generativeai as genai
from scjn_scraper import buscar_normatividades_scjn

# 1. Configuración de API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Inicialización de resultados en la sesión (para que no desaparezcan)
if "resultados" not in st.session_state:
    st.session_state.resultados = None

st.title("Ágora - Inteligencia Normativa")
termino = st.text_input("Buscar normatividad:")

if st.button("Buscar en SCJN"):
    with st.spinner("Buscando en la Corte..."):
        st.session_state.resultados = buscar_normatividades_scjn(termino)

# Mostrar resultados si existen
if st.session_state.resultados:
    st.write(st.session_state.resultados)
