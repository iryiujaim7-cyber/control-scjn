import streamlit as st
import os
from pypdf import PdfReader
from docx import Document
from io import BytesIO

# =====================================================================
# ÁREA DE INGESTA AUTOMÁTICA (El "Buffer")
# =====================================================================
st.subheader("📥 Área de Análisis y Cruce de Normatividad")

# Este file_uploader actúa como tu puerta de entrada
archivos_cargados = st.file_uploader(
    "Arrastra aquí las leyes descargadas de la SCJN:", 
    type=["pdf", "docx"], 
    accept_multiple_files=True
)

# Diccionario para almacenar el texto extraído
if "expediente_texto" not in st.session_state:
    st.session_state.expediente_texto = {}

# PROCESAMIENTO AUTOMÁTICO (Pasos 3 y 4)
if archivos_cargados:
    for archivo in archivos_cargados:
        if archivo.name not in st.session_state.expediente_texto:
            with st.spinner(f"Procesando {archivo.name}..."):
                # Lógica de extracción según extensión
                texto = ""
                if archivo.name.endswith(".pdf"):
                    reader = PdfReader(archivo)
                    texto = "".join([p.extract_text() for p in reader.pages])
                elif archivo.name.endswith(".docx"):
                    doc = Document(archivo)
                    texto = "\n".join([p.text for p in doc.paragraphs])
                
                st.session_state.expediente_texto[archivo.name] = texto
                st.success(f"✅ {archivo.name} agregado al análisis.")

# Mostrar lista de leyes actuales en el análisis
if st.session_state.expediente_texto:
    st.write("Leyes en análisis:", list(st.session_state.expediente_texto.keys()))
