import streamlit as st
import pandas as pd
import os
import requests
import json
from docx import Document
from pypdf import PdfReader
from io import BytesIO
from scjn_scraper import buscar_normatividades_scjn

# =====================================================================
# 1. CONFIGURACIÓN DE PÁGINA Y LLAVE DE API
# =====================================================================
LOGO_URL = "https://raw.githubusercontent.com/iryiujaim7-cyber/control-scjn/main/logo.png"

st.set_page_config(
    page_title="Ágora - Inteligencia Normativa",
    page_icon=LOGO_URL,
    layout="wide"
)

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if "expediente" not in st.session_state:
    st.session_state.expediente = {}  
if "archivos_locales" not in st.session_state:
    st.session_state.archivos_locales = {}  
if "historial_chat" not in st.session_state:
    st.session_state.historial_chat = []
if "resultados_busqueda" not in st.session_state:
    st.session_state.resultados_busqueda = []

# =====================================================================
# 2. INYECCIÓN DE IDENTIDAD VISUAL CORPORATIVA
# =====================================================================
st.markdown(f"""
    <style>
    .stApp {{
        background-color: #F8F9FA;
    }}
    .block-container {{
        padding-top: 0.5rem !important;
        padding-bottom: 1rem !important;
    }}
    .header-block {{
        text-align: center;
        margin-top: 0px !important;
        padding-top: 0px !important;
    }}
    .header-block img {{
        display: block;
        margin: 0 auto !important;
        padding: 0 !important;
        max-width: 240px;
        height: auto;
    }}
    .header-block h1 {{
        color: #1A2E40 !important;
        font-family: 'Georgia', serif;
        font-weight: bold;
        margin-top: 5px !important;
        margin-bottom: 0.2rem !important;
        font-size: 2.2rem;
    }}
    h2, h3, h4 {{
        color: #1A2E40 !important;
        font-family: 'Georgia', serif;
        font-weight: bold;
    }}
    /* Estilo para los botones principales y de añadir */
    div.stButton > button {{
        background-color: #1A2E40;
        color: #FFFFFF;
        border: 1px solid #1A2E40;
        border-radius: 4px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }}
    div.stButton > button:hover {{
        background-color: #C5A059;
        color: #FFFFFF;
        border-color: #C5A059;
    }}
    div.stButton > button[key="limpiar_exp"] {{
        background-color: #E2E8F0 !important;
        color: #4A5568 !important;
        border: 1px solid #CBD5E1 !important;
    }}
    div.stButton > button[key="limpiar_exp"]:hover {{
        background-color: #CBD5E1 !important;
        color: #1A2E40 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 3. ENCABEZADO INTEGRADO COMPACTO
# =====================================================================
st.markdown(f"""
    <div class="header-block">
        <img src="{LOGO_URL}" alt="Logo Ágora">
        <h1>Catálogo e Inteligencia de Normatividades</h1>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<h5 style='text-align: center; font-weight: normal; color: #4A5568; margin-top: 0px; margin-bottom: 1.5rem;'>Buscador Jurídico en Tiempo Real e Intérprete Basado en Inteligencia Artificial</h5>", unsafe_allow_html=True)
st.markdown("<hr style='border-top: 1px solid #E2E8F0; margin-top: 0px; margin-bottom: 1.5rem;'>", unsafe_allow_html=True)

# =====================================================================
# 4. PANEL DE BÚSQUEDA DINÁMICA (COLUMNA IZQUIERDA)
# =====================================================================
col_izq, col_der = st.columns([6, 6])

with col_izq:
    st.subheader("🔍 Consulta Directa en la SCJN")
    
    termino = st.text_input("Escribe el nombre de la ley, reglamento o normatividad que deseas buscar:", placeholder="Ej. Ley General de Instituciones y Procedimientos Electorales")
    
    if st.button("Buscar en SCJN"):
        if termino.strip():
            with st.spinner("Navegando de forma segura y extrayendo datos de la SCJN..."):
                st.session_state.resultados_busqueda = buscar_normatividades_scjn(termino)
        else:
            st.warning("Por favor ingresa un concepto válido para buscar.")

    if st.session_state.resultados_busqueda:
        st.markdown("##### Resultados encontrados. Añade los elementos necesarios a tu espacio de trabajo:")
        for idx, item in enumerate(st.session_state.resultados_busqueda):
            col_info, col_btn = st.columns([4, 1.2])
            with col_info:
                st.markdown(f"🏛️ **{item['Normatividad']}**", unsafe_allow_html=True)
                st.markdown(f"📅 *Última actualización:* <span style='color:#C5A059; font-weight:bold;'>{item['Última actualización']}</span>", unsafe_allow_html=True)
            with col_btn:
                if item["Normatividad"] in st.session_state.expediente:
                    st.markdown("<p style='color:#C5A059; font-weight:bold; text-align:center; margin-top:10px;'>Agregada ✓</p>", unsafe_allow_html=True)
                else:
                    if st.button("Añadir", key=f"btn_{idx}"):
                        st.session_state.expediente[item["Normatividad"]] = item["Url Descarga"]
                        st.rerun()
            st.markdown("<hr style='border-top: 1px dashed #E2E8F0; margin: 0.5rem 0;'>", unsafe_allow_html=True)

# =====================================================================
# 5. EXPEDIENTE VIRTUAL (COLUMNA DERECHA)
# =====================================================================
with col_der:
    st.subheader("📂 Tu Expediente Virtual de Análisis")
    
    st.markdown("🌐 **Cargar documentos locales:**")
    archivos_subidos = st.file_uploader("Sube tus propios archivos para incluirlos en el cruce de información:", type=["pdf", "docx"], accept_multiple_files=True, label_visibility="collapsed")
    
    if archivos_subidos:
        for archivo in archivos_subidos:
            if archivo.name not in st.session_state.archivos_locales:
                try:
                    texto_extraido = ""
                    if archivo.name.endswith(".pdf"):
                        lector_pdf = PdfReader(BytesIO(archivo.read()))
                        for pagina in lector_pdf.pages:
                            texto_extraido += pagina.extract_text() + "\n"
                    elif archivo.name.endswith(".docx"):
                        doc_local = Document(BytesIO(archivo.read()))
                        texto_extraido = "\n".join([p.text for p in doc_local.paragraphs])
                    
                    if texto_extraido.strip():
                        st.session_state.archivos_locales[archivo.name] = texto_extraido
                except Exception as e_archivo:
                    st.error(f"Error procesando {archivo.name}: {str(e_archivo)}")

    if archivos_subidos is not None:
        nombres_actuales = [a.name for a in archivos_subidos]
        for nombre_guardado in list(st.session_state.archivos_locales.keys()):
            if nombre_guardado not in nombres_actuales:
                st.session_state.archivos_locales.pop(nombre_guardado, None)

    if st.session_state.expediente:
        st.markdown("<p style='font-weight: bold; margin-bottom: 5px;'>Leyes institucionales añadidas (SCJN):</p>", unsafe_allow_html=True)
        for ley in list(st.session_state.expediente.keys()):
            col_ley_txt, col_ley_del = st.columns([7, 1])
            with col_ley_txt:
                st.markdown(f"🏛️ `{ley}`", unsafe_allow_html=True)
            with col_ley_del:
                if st.button("❌", key=f"del_scjn_{ley}"):
                    st.session_state.expediente.pop(ley, None)
                    st.rerun()

    if st.session_state.expediente or st.session_state.archivos_locales:
        st.markdown(" ")
        if st.button("Limpiar Todo el Expediente", key="limpiar_exp"):
            st.session_state.expediente = {}
            st.session_state.archivos_locales = {}
            st.session_state.historial_chat = []
            st.session_state.resultados_busqueda = []
            st.rerun()

# =====================================================================
# 6. ENTORNO DE CONSULTA INTELIGENTE (ESTILO NOTEBOOKLM + ESCAPADO JSON)
# =====================================================================
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("🤖 Asistente Jurídico Experto (Análisis RAG Unificado)")

if not st.session_state.expediente and not st.session_state.archivos_locales:
    st.warning("⚠️ Integra al menos una normatividad de la SCJN o un archivo local a tu expediente superior para habilitar el consultor de Inteligencia Artificial.")
elif not GEMINI_API_KEY:
    st.error("🔑 Falta la clave de API de Gemini en los Secrets de tu Streamlit Cloud.")
else:
    total_docs = len(st.session_state.expediente) + len(st.session_state.archivos_locales)
    st.success(f"Ecosistema integrado con éxito al estilo NotebookLM. Analizando {total_docs} documentos en total.")
    
    for mensaje in st.session_state.historial_chat:
        with st.chat_message(mensaje["role"]):
            st.markdown(mensaje["content"])
            
    st.markdown("### 💬 Haz preguntas sobre estas normatividades")
    
    if pregunta_usuario := st.chat_input("Plantea tu duda (El sistema responderá basándose estrictamente en tus documentos cargados)..."):
        
        with st.chat_message("user"):
            st.markdown(pregunta_usuario)
        st.session_state.historial_chat.append({"role": "user", "content": pregunta_usuario})
        
        with st.chat_message("assistant"):
            respuesta_placeholder = st.empty()
            
            with st.status("🧠 Analizando expediente unificado...", expanded=True) as status:
                status.write("⏬ Cargando y estructurando las leyes del expediente virtual...")
                texto_total_contexto = ""
                
                # Cargar leyes SCJN
                for nombre_ley, url_ley in st.session_state.expediente.items():
                    try:
                        if ".docx" in url_ley or "wfDescarga" in url_ley or "aspx" in url_ley:
                            res = requests.get(url_ley, timeout=15)
                            doc = Document(BytesIO(res.content))
                            texto_ley = "\n".join([p.text for p in doc.paragraphs])
                            texto_total_contexto += f"\n\n=== ORDENAMIENTO OFICIAL (SCJN): {nombre_ley} ===\n" + texto_ley[:150000]
                    except Exception:
                        pass
                
                # Cargar y sanitizar archivos locales
                status.write("📖 Indexando y sanitizando los textos de tus archivos locales cargados...")
                for nombre_doc, texto_doc in st.session_state.archivos_locales.items():
                    status.write(f" -> Procesando de forma segura: `{nombre_doc}`")
                    # Reemplazar caracteres problemáticos comunes para asegurar estabilidad en JSON
                    texto_limpio = texto_doc.replace('"', '\\"').replace('\r', '')
                    texto_total_contexto += f"\n\n=== ARCHIVO CARGADO: {nombre_doc} ===\n" + texto_limpio[:150000]
                
                status.write("🧠 Sincronizando modelo analítico cerrado de Gemini 1.5 Flash...")
                prompt_sistema = (
                    "Actúa estrictamente como un sistema experto de análisis documental cerrado (estilo Google NotebookLM).\n"
                    "Tu única fuente de verdad legítima son los documentos provistos en el bloque de CONTEXTO DOCUMENTAL UNIFICADO.\n\n"
                    "Reglas obligatorias de comportamiento:\n"
                    "1. Responde a la pregunta planteada basándote ÚNICAMENTE en la información explícita de los documentos.\n"
                    "2. Si la respuesta no se encuentra plasmada en los textos, debes contestar de manera exacta y literal:\n"
                    "'Lo siento, la información solicitada no se encuentra disponible en las normatividades ni en los documentos cargados en el expediente.'\n"
                    "No inventes, asumas, presupongas ni utilices conocimientos externos al contexto bajo ninguna circunstancia.\n"
                    "3. Usa un lenguaje formal, técnico y estructurado. Cita siempre el artículo o documento del que extrajiste el argumento.\n\n"
                    f"CONTEXTO DOCUMENTAL UNIFICADO:\n{texto_total_contexto}\n\n"
                    f"PREGUNTA DEL USUARIO:\n{pregunta_usuario}"
                )
                
                status.write("⚖️ Formulando fundamentación y construyendo respuesta jurídica...")
                
                try:
                    url_api = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                    headers = {"Content-Type": "application/json"}
                    
                    # Construcción ultra segura del payload usando la librería json nativa para evitar malformaciones
                    payload = {
                        "contents": [{
                            "parts": [{"text": prompt_sistema}]
                        }]
                    }
                    
                    response = requests.post(url_api, data=json.dumps(payload), headers=headers, timeout=45)
                    res_json = response.json()
                    
                    if 'candidates' in res_json:
                        respuesta_ia = res_json['candidates'][0]['content']['parts'][0]['text']
                        status.update(label="✅ Análisis completado con éxito", state="complete", expanded=False)
                    else:
                        # Si la API responde con un error de cuota o restricción estructurada
                        msg_err = res_json.get('error', {}).get('message', 'Estructura de datos rechazada por el servidor.')
                        respuesta_ia = f"El motor de Google no pudo procesar el volumen de texto. Detalle técnico: {msg_err}"
                        status.update(label="❌ Error en los parámetros del documento", state="error", expanded=False)
                        
                except Exception as e_api:
                    respuesta_ia = f"Error de comunicación con el núcleo analítico: {str(e_api)}"
                    status.update(label="❌ Error de conexión de red", state="error", expanded=False)
            
            respuesta_placeholder.markdown(respuesta_ia)
            st.session_state.historial_chat.append({"role": "assistant", "content": respuesta_ia})
