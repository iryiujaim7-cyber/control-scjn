import streamlit as st
import pandas as pd
import os
import requests
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

# Inicializar cliente de Gemini desde Secrets de forma segura
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# Inicializar estados de la sesión para el expediente virtual, archivos locales y chat
if "expediente" not in st.session_state:
    st.session_state.expediente = {}  # {Nombre: Url_Descarga}
if "archivos_locales" not in st.session_state:
    st.session_state.archivos_locales = {}  # {Nombre: Texto_Extraido}
if "historial_chat" not in st.session_state:
    st.session_state.historial_chat = []
if "resultados_busqueda" not in st.session_state:
    st.session_state.resultados_busqueda = []

# =====================================================================
# 2. INYECCIÓN DE IDENTIDAD VISUAL CORPORATIVA (MÁXIMA COMPRESIÓN)
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
    p, span, label, div {{
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
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
    /* Botón de limpieza */
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

    # Desplegar lista de resultados
    if st.session_state.resultados_busqueda:
        st.markdown("##### Resultados encontrados. Añade los elementos necesarios a tu espacio de trabajo:")
        
        for idx, item in enumerate(st.session_state.resultados_busqueda):
            col_info, col_btn = st.columns([4, 1.2])
            
            with col_info:
                st.markdown(f"**{item['Normatividad']}**", unsafe_allow_html=True)
                st.markdown(f"📅 *Última actualización:* <span style='color:#C5A059; font-weight:bold;'>{item['Última actualización']}</span>", unsafe_allow_html=True)
                st.caption(f"Enlace de origen: {item['Url Descarga']}")
            
            with col_btn:
                if item["Normatividad"] in st.session_state.expediente:
                    st.markdown("<p style='color:#C5A059; font-weight:bold; text-align:center; margin-top:10px;'>Agregada ✓</p>", unsafe_allow_html=True)
                else:
                    if st.button("Añadir", key=f"btn_{idx}"):
                        st.session_state.expediente[item["Normatividad"]] = item["Url Descarga"]
                        st.rerun()
            st.markdown("<hr style='border-top: 1px dashed #E2E8F0; margin: 0.5rem 0;'>", unsafe_allow_html=True)

# =====================================================================
# 5. EXPEDIENTE VIRTUAL Y CARGA DE ARCHIVOS LOCALES (COLUMNA DERECHA)
# =====================================================================
with col_der:
    st.subheader("📂 Tu Expediente Virtual de Análisis")
    
    # --- SUBSECCIÓN A: Subir documentos propios ---
    st.markdown("🌐 **Cargar documentos locales (.pdf, .docx):**")
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

    st.markdown("<br><p style='font-weight: bold; margin-bottom: 5px;'>Documentos listos para el cruce analítico simultáneo:</p>", unsafe_allow_html=True)
    
    hay_contenido = False
    
    # Desplegar leyes de la SCJN
    if st.session_state.expediente:
        hay_contenido = True
        for ley in list(st.session_state.expediente.keys()):
            col_ley_txt, col_ley_del = st.columns([7, 1])
            with col_ley_txt:
                st.markdown(f"🏛️ `<span style='color:#1A2E40; font-weight:600;'>{ley}</span>` (SCJN)", unsafe_allow_html=True)
            with col_ley_del:
                if st.button("❌", key=f"del_scjn_{ley}"):
                    st.session_state.expediente.pop(ley, None)
                    st.rerun()

    # Desplegar archivos locales cargados
    if st.session_state.archivos_locales:
        hay_contenido = True
        for nombre_doc in list(st.session_state.archivos_locales.keys()):
            col_doc_txt, col_doc_del = st.columns([7, 1])
            with col_doc_txt:
                st.markdown(f"📄 `<span style='color:#C5A059; font-weight:600;'>{nombre_doc}</span>` (Archivo local)", unsafe_allow_html=True)
            with col_doc_del:
                if st.button("❌", key=f"del_local_{nombre_doc}"):
                    st.session_state.archivos_locales.pop(nombre_doc, None)
                    st.rerun()
                    
    if hay_contenido:
        st.markdown(" ")
        if st.button("Limpiar Todo el Expediente", key="limpiar_exp"):
            st.session_state.expediente = {}
            st.session_state.archivos_locales = {}
            st.session_state.historial_chat = []
            st.session_state.resultados_busqueda = []
            st.rerun()
    else:
        st.info("Tu expediente está vacío. Busca leyes a la izquierda o arrastra tus archivos PDF/Word aquí arriba.")

# =====================================================================
# 6. ENTORNO DE CONSULTA INTELIGENTE (CHATEAR CON EL EXPEDIENTE MULTIDISCIPLINARIO)
# =====================================================================
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("🤖 Asistente Jurídico Experto (Análisis RAG Unificado)")

if not st.session_state.expediente and not st.session_state.archivos_locales:
    st.warning("⚠️ Integra al menos una normatividad de la SCJN o un archivo local a tu expediente superior para habilitar el consultor de Inteligencia Artificial.")
elif not GEMINI_API_KEY:
    st.error("🔑 Falta la clave de API de Gemini en los Secrets de tu Streamlit Cloud.")
else:
    total_docs = len(st.session_state.expediente) + len(st.session_state.archivos_locales)
    st.success(f"Ecosistema integrado con éxito. El consultor cruzará información de los {total_docs} documentos agregados.")
    
    # Renderizar el historial acumulado en pantalla
    for mensaje in st.session_state.historial_chat:
        with st.chat_message(mensaje["role"]):
            st.markdown(mensaje["content"])
            
    # Entrada de texto del chat interactivo
    if pregunta_usuario := st.chat_input("Plantea tu duda jurídica sobre el expediente unificado..."):
        
        with st.chat_message("user"):
            st.markdown(pregunta_usuario)
        st.session_state.historial_chat.append({"role": "user", "content": pregunta_usuario})
        
        with st.chat_message("assistant"):
            respuesta_placeholder = st.empty()
            with st.spinner("Compilando documentos e hilando interpretación jurídica cruzada..."):
                
                # 1. Mapeo y descarga dinámica de leyes de la SCJN
                texto_total_contexto = ""
                for nombre_ley, url_ley in st.session_state.expediente.items():
                    texto_total_contexto += f"\n\n=== ORDENAMIENTO (SCJN): {nombre_ley} ===\n"
                    try:
                        if ".docx" in url_ley or "wfDescarga" in url_ley or "aspx" in url_ley:
                            res = requests.get(url_ley, timeout=15)
                            doc = Document(BytesIO(res.content))
                            texto_ley = "\n".join([p.text for p in doc.paragraphs])
                            texto_total_contexto += texto_ley[:150000]
                        else:
                            texto_total_contexto += f"Contenido indexado mediante referencia oficial: {url_ley}\n"
                    except Exception:
                        texto_total_contexto += f"(Nota: Contenido procesado mediante enlace de referencia debido a restricción de descarga directa)\n"
                
                # 2. Sumar el texto de los archivos locales cargados
                for nombre_doc, texto_doc in st.session_state.archivos_locales.items():
                    texto_total_contexto += f"\n\n=== DOCUMENTO LOCAL USER: {nombre_doc} ===\n"
                    texto_total_contexto += texto_doc[:150000]
                
                # 3. Ingeniería de Prompts Jurídicos Especializados
                prompt_sistema = (
                    "Eres un consultor jurídico de la Suprema Corte de Justicia de la Nación y un abogado experto "
                    "en el marco legal y electoral de los Estados Unidos Mexicanos. Tu tarea es responder con un lenguaje altamente "
                    "formal, técnico, pragmático y rigurosamente estructurado.\n\n"
                    "Instrucciones de actuación:\n"
                    "1. Responde a la consulta del usuario basándote de forma estricta y prioritaria en el contexto documental adjunto, "
                    "el cual incluye tanto leyes oficiales de la SCJN como documentos personales provistos por el usuario.\n"
                    "2. Realiza un cruce de información minucioso: analiza cómo interactúan los documentos locales con el marco jurídico oficial.\n"
                    "3. Cita siempre de manera explícita el artículo, capítulo, apartado o el nombre del documento de origen para fundamentar tu dicho.\n\n"
                    f"CONTEXTO DOCUMENTAL UNIFICADO:\n{texto_total_contexto}\n\n"
                    f"PREGUNTA DEL ABOGADO:\n{pregunta_usuario}"
                )
                
                # 4. Petición HTTPS Nativa a la API de Google Gemini 1.5 Flash
                try:
                    url_api = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                    headers = {"Content-Type": "application/json"}
                    payload = {
                        "contents": [{
                            "parts": [{"text": prompt_sistema}]
                        }]
                    }
                    
                    response = requests.post(url_api, json=payload, headers=headers, timeout=45)
                    res_json = response.json()
                    respuesta_ia = res_json['candidates'][0]['content']['parts'][0]['text']
                except Exception as e_api:
                    respuesta_ia = f"Error de comunicación con el núcleo de Gemini: {str(e_api)}"
                
                # Desplegar respuesta final
                respuesta_placeholder.markdown(respuesta_ia)
                st.session_state.historial_chat.append({"role": "assistant", "content": respuesta_ia})
