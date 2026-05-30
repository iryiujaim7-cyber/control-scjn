import streamlit as st
import google.generativeai as genai
from scjn_scraper import buscar_normatividades_scjn

# 1. Configuración de API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Interfaz básica para probar
st.title("Ágora - Inteligencia Normativa")
termino = st.text_input("Buscar normatividad:")

if st.button("Buscar en SCJN"):
    with st.spinner("Buscando..."):
        # Esto llamará a tu scraper
        resultados = buscar_normatividades_scjn(termino)
        st.write(resultados) # Para ver si realmente trae datos
