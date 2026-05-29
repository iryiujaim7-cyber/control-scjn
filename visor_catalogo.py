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
# 2. INYECCIÓN DE IDENTIDAD VISUAL Y CAJA DE CHAT LUMINOSA
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
    
    /* Botones principales */
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

    /* Estilo luminoso y elegante para la caja de chat */
    div[data-testid="stChatInput"] {{
        background-color: #FFFFFF !important;
        border: 2px solid #C5A059 !important; 
        border-radius: 12px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important;
        padding: 5px !important;
    }}
    div[data-testid="stChatInput"] textarea {{
        color: #1A2E40 !important; 
        background-color: #FFFFFF !important;
        font-weight: 500 !important;
    }}
    div[data-testid="stChatInput"] svg {{
        fill: #C5A059 !important;
    }}
    div[data-testid="stChatInput"] textarea::placeholder {{
        color: #718096 !important;
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
                    st.error(f"Error extrayendo texto de {archivo.name}: {str(e_archivo)}")

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
# 6. ENTORNO DE CONSULTA INTELIGENTE (SDK ESTABLE GOOGLE-GENERATIVEAI)
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
            
            with st.status("🧠 Analizando expediente unificado con Google GenAI...", expanded=True) as status:
                try:
                    # Configurar la API directamente
                    genai.configure(api_key=GEMINI_API_KEY)
                    texto_total_unificado = ""

                    status.write("⏬ Unificando textos de las leyes oficiales...")
                    for nombre_ley, url_ley in st.session_state.expediente.items():
                        try:
                            if ".docx" in url_ley or "wfDescarga" in url_ley or "aspx" in url_ley:
                                res = requests.get(url_ley, timeout=15)
                                doc = Document(BytesIO(res.content))
                                texto_total_unificado += f"\n\n=== LEY OFICIAL SCJN: {nombre_ley} ===\n"
                                texto_total_unificado += "\n".join([p.text for p in doc.paragraphs])
                        except Exception:
                            pass

                    status.write("📖 Añadiendo textos de documentos locales...")
                    for nombre_doc, texto_doc in st.session_state.archivos_locales.items():
                        texto_total_unificado += f"\n\n=== ARCHIVO LOCAL CARGADO: {nombre_doc} ===\n{texto_doc}"

                    status.write("⚖️ Ejecutando análisis jurisprudencial directo...")
                    
                    # Inyectamos el texto extraído directamente al prompt, sin subir archivos
                    instrucciones_sistema = (
                        "Actúas estrictamente como un sistema experto de análisis documental cerrado (estilo Google NotebookLM).\n"
                        "Tu única fuente de verdad legítima son los documentos provistos a continuación.\n\n"
                        "Reglas obligatorias de comportamiento:\n"
                        "1. Responde a la pregunta planteada basándote ÚNICAMENTE en la información de los documentos.\n"
                        "2. Si la respuesta no se encuentra, debes contestar de manera exacta y literal:\n"
                        "'Lo siento, la información solicitada no se encuentra disponible en las normatividades ni en los documentos cargados en el expediente.'\n"
                        "No inventes, asumas, ni utilices conocimientos externos.\n"
                        "3. Usa un lenguaje formal, técnico y estructurado. Cita siempre el artículo o documento del que extrajiste el argumento.\n\n"
                        f"DOCUMENTOS DE REFERENCIA:\n{texto_total_unificado}\n\n"
                        f"PREGUNTA DEL USUARIO:\n{pregunta_usuario}"
                    )

                    # Invocar al modelo
                    model = genai.GenerativeModel('gemini-flash-latest')
                    response = model.generate_content(
                        instrucciones_sistema,
                        generation_config={"temperature": 0.0}
                    )
                    
                    respuesta_ia = response.text
                    status.update(label="✅ Análisis completado con éxito", state="complete", expanded=False)

                except Exception as e_general:
                    respuesta_ia = f"El motor analítico experimentó un fallo. Detalle técnico: {str(e_general)}"
                    status.update(label="❌ Error de procesamiento en la nube", state="error", expanded=True)
            
            respuesta_placeholder.markdown(respuesta_ia)
            st.session_state.historial_chat.append({"role": "assistant", "content": respuesta_ia})
