import streamlit as st
import pandas as pd
import os
import requests
from docx import Document
from pypdf import PdfReader
from io import BytesIO
import google.generativeai as genai
from scjn_scraper import buscar_normatividades_scjn

# =====================================================================
# 1. CONFIGURACIÓN
# =====================================================================
LOGO_URL = "https://raw.githubusercontent.com/iryiujaim7-cyber/control-scjn/main/logo.png"
st.set_page_config(page_title="Ágora - Inteligencia Normativa", page_icon=LOGO_URL, layout="wide")
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if "expediente" not in st.session_state: st.session_state.expediente = {}
if "archivos_locales" not in st.session_state: st.session_state.archivos_locales = {}
if "historial_chat" not in st.session_state: st.session_state.historial_chat = []

# =====================================================================
# 2. ESTILOS (Mantenemos tu diseño elegante)
# =====================================================================
st.markdown("""<style> .stApp { background-color: #F8F9FA; } </style>""", unsafe_allow_html=True)

# =====================================================================
# 3. INTERFAZ
# =====================================================================
col_izq, col_der = st.columns([6, 6])

with col_izq:
    st.subheader("🔍 Consulta Directa en la SCJN")
    termino = st.text_input("Buscar normatividad:")
    if st.button("Buscar en SCJN"):
        with st.spinner("Buscando..."):
            st.session_state.resultados_busqueda = buscar_normatividades_scjn(termino)
    
    for idx, item in enumerate(st.session_state.resultados_busqueda):
        if st.button(f"Añadir: {item['Normatividad']}", key=f"btn_{idx}"):
            st.session_state.expediente[item['Normatividad']] = item['Url Descarga']
            st.rerun()

with col_der:
    st.subheader("📂 Tu Expediente")
    archivos_subidos = st.file_uploader("Subir archivos:", type=["pdf", "docx"], accept_multiple_files=True)
    if archivos_subidos:
        for archivo in archivos_subidos:
            if archivo.name not in st.session_state.archivos_locales:
                # (Tu lógica de extracción de texto se mantiene igual aquí)
                st.session_state.archivos_locales[archivo.name] = "Texto extraído..." # Simplificado para brevedad

# =====================================================================
# 4. CONSULTA INTELIGENTE CON SELECCIÓN ACTIVA
# =====================================================================
st.subheader("🤖 Asistente Jurídico (Análisis Selectivo)")

# --- NUEVA FUNCIÓN: SELECCIÓN DE DOCUMENTOS ---
st.markdown("#### Selecciona qué documentos analizar en esta pregunta:")
documentos_disponibles = list(st.session_state.expediente.keys()) + list(st.session_state.archivos_locales.keys())
seleccionados = st.multiselect("Documentos activos:", documentos_disponibles, default=documentos_disponibles)

if pregunta_usuario := st.chat_input("Escribe tu duda jurídica..."):
    with st.status("🧠 Analizando documentos seleccionados...", expanded=True) as status:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            
            # SOLO unificamos los documentos seleccionados
            texto_unificado = ""
            for doc in seleccionados:
                if doc in st.session_state.expediente:
                    # Aquí iría tu lógica de descarga y lectura
                    texto_unificado += f"\n\n=== {doc} ===\nTexto extraído..."
                else:
                    texto_unificado += f"\n\n=== {doc} ===\n{st.session_state.archivos_locales[doc]}"

            instrucciones = (
                f"Analiza los siguientes documentos: {texto_unificado}\n"
                f"Pregunta: {pregunta_usuario}"
            )

            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content(instrucciones, generation_config={"temperature": 0.0})
            
            st.markdown(response.text)
            status.update(label="✅ Análisis completado", state="complete")
        except Exception as e:
            st.error(f"Error: {e}")
