import streamlit as st
import pandas as pd
import os
import requests
from docx import Document
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

# Inicializar cliente de Gemini si la API Key está configurada en los Secrets de Streamlit
# O puedes pegarla temporalmente aquí como string: GEMINI_API_KEY = "TU_API_KEY"
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# Inicializar estados de la sesión para el expediente virtual y el chat
if "expediente" not in st.session_state:
    st.session_state.expediente = {}  # {Nombre: Url_Descarga}
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
    /* Estilo para los botones principales */
    div.stButton > button:first-child {{
        background-color: #1A2E40;
        color: #FFFFFF;
        border: 1px solid #1A2E40;
        border-radius: 4px;
        font-weight: bold;
        transition: all 0.3s ease;
    }}
    div.stButton > button:first-child:hover {{
        background-color: #C5A059;
        color: #FFFFFF;
        border-color: #C5A059;
    }}
    /* Botón secundario/limpieza */
    div.stButton > button[key="limpiar_exp"] {{
        background-color: #E2E8F0;
        color: #4A5568;
        border: 1px solid #CBD5E1;
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
# 4. PANEL DE BÚSQUEDA DINÁMICA (MULTILEYES)
# =====================================================================
col_izq, col_der = st.columns([7, 5])

with col_izq:
    st.subheader("🔍 Consulta Directa en la SCJN")
    
    # Campo de texto e interacción
    termino = st.text_input("Escribe el nombre de la ley, reglamento o normatividad que deseas buscar:", placeholder="Ej. Ley General de Instituciones y Procedimientos Electorales")
    
    if st.button("Buscar en SCJN"):
        if termino.strip():
            with st.spinner("Navegando de forma segura y extrayendo datos de la SCJN..."):
                st.session_state.resultados_busqueda = buscar_normatividades_scjn(termino)
        else:
            st.warning("Por favor ingresa un concepto válido para buscar.")

    # Desplegar tabla de resultados si existen
    if st.session_state.resultados_busqueda:
        st.markdown("##### Selecciona las normatividades que deseas agregar a tu expediente de análisis:")
        
        # Iterar resultados para mostrarlos con un checkbox de control individual
        for idx, item in enumerate(st.session_state.resultados_busqueda):
            col_check, col_info = st.columns([1, 15])
            with col_check:
                # Determinar si ya está en el expediente para dejarlo marcado
                marcado_previo = item["Normatividad"] in st.session_state.expediente
                if st.checkbox("", key=f"check_{idx}", value=marcado_previo):
                    st.session_state.expediente[item["Normatividad"]] = item["Url Descarga"]
                else:
                    # Si se desmarca, remover del expediente activo
                    st.session_state.expediente.pop(item["Normatividad"], None)
                    
            with col_info:
                st.markdown(f"**{item['Normatividad']}** — <span style='color:#C5A059; font-weight:bold;'>{item['Última actualización']}</span>", unsafe_allow_html=True)
                st.caption(f"Enlace oficial mapeado: {item['Url Descarga']}")
        st.markdown("---")

# =====================================================================
# 5. EXPEDIENTE VIRTUAL (ACUMULADOR MULTIDISCIPLINARIO)
# =====================================================================
with col_der:
    st.subheader("📂 Tu Expediente Virtual de Análisis")
    st.markdown("Las leyes seleccionadas de tus búsquedas se concentrarán aquí para cruzarse simultáneamente:")
    
    if st.session_state.expediente:
        for ley in list(st.session_state.expediente.keys()):
            st.markdown(f"✅ `<span style='color:#1A2E40; font-weight:600;'>{ley}</span>`", unsafe_allow_html=True)
        
        st.markdown(" ")
        if st.button("Limpiar Expediente", key="limpiar_exp"):
            st.session_state.expediente = {}
            st.session_state.historial_chat = []
            st.rerun()
    else:
        st.info("Tu expediente está vacío. Busca una ley a la izquierda y marca la casilla correspondiente para agregarla.")

# =====================================================================
# 6. ENTORNO DE CONSULTA INTELIGENTE (CHATEAR CON EL EXPEDIENTE)
# =====================================================================
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("🤖 Asistente Jurídico Experto (Análisis RAG Unificado)")

if not st.session_state.expediente:
    st.warning("⚠️ Agrega al menos una normatividad a tu expediente arriba para habilitar el consultor de Inteligencia Artificial.")
elif not GEMINI_API_KEY:
    st.error("🔑 Falta la clave de API de Gemini. Por favor configúrala en tus Secrets de Streamlit con el nombre 'GEMINI_API_KEY' para activar el motor analítico.")
else:
    st.success(f"Listo. El consultor analizará las {len(st.session_state.expediente)} normatividades seleccionadas en conjunto.")
    
    # Renderizar el historial de conversación en la pantalla
    for mensaje in st.session_state.historial_chat:
        with st.chat_message(mensaje["role"]):
            st.markdown(mensaje["content"])
            
    # Entrada de texto del chat interactivo
    if pregunta_usuario := st.chat_input("Escribe tu duda jurídica (Ej. ¿Cuáles fueron las modificaciones en materia de fiscalización o plazos transitorios?)"):
        
        # Mostrar la pregunta de inmediato en la UI
        with st.chat_message("user"):
            st.markdown(pregunta_usuario)
        st.session_state.historial_chat.append({"role": "user", "content": pregunta_usuario})
        
        # Procesamiento y llamada RAG hacia la API de Google
        with st.chat_message("assistant"):
            respuesta_placeholder = st.empty()
            with st.spinner("Descargando normatividades vigentes desde la SCJN e interpretando correlaciones jurídicas..."):
                
                # 1. Descargar el texto de todas las leyes en el expediente
                texto_total_contexto = ""
                for nombre_ley, url_ley in st.session_state.expediente.items():
                    texto_total_contexto += f"\n\n=== NORMATIVIDAD: {nombre_ley} ===\n"
                    try:
                        # Si es un enlace de descarga directa de Word de la SCJN
                        if ".docx" in url_ley or "wfDescarga" in url_ley:
                            res = requests.get(url_ley, timeout=15)
                            doc = Document(BytesIO(res.content))
                            texto_ley = "\n".join([p.text for p in doc.paragraphs])
                            texto_total_contexto += texto_ley[:150000] # Control prudencial de tamaño por documento
                        else:
                            texto_total_contexto += f"Contenido referenciado mediante portal web oficial: {url_ley}\n"
                    except Exception as e_descarga:
                        texto_total_contexto += f"(Error al extraer texto en tiempo real: {str(e_descarga)})\n"
                
                # 2. Configurar el Prompt Estricto del Sistema Jurídico
                prompt_sistema = (
                    "Eres un consultor jurídico de la Suprema Corte de Justicia de la Nación y un abogado experto "
                    "en el marco legal y electoral mexicano. Tu tarea es responder con un lenguaje formal, técnico "
                    "y preciso. Responde a la duda basándote en los textos de las normatividades adjuntas vigentes.\n\n"
                    f"CONTEXTO DOCUMENTAL DE LAS LEYES SELECCIONADAS:\n{texto_total_contexto}\n\n"
                    f"PREGUNTA DEL ABOGADO:\n{pregunta_usuario}"
                )
                
                # 3. Invocar la API de Gemini 1.5 Flash usando requests directo (para evitar conflictos de versión SDK)
                try:
                    url_api = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                    headers = {"Content-Type": "application/json"}
                    payload = {
                        "contents": [{
                            "parts": [{"text": prompt_sistema}]
                        }]
                    }
                    
                    response = requests.post(url_api, json=payload, headers=headers, timeout=30)
                    res_json = response.json()
                    
                    # Extraer el texto de la respuesta de Google
                    respuesta_ia = res_json['candidates'][0]['content']['parts'][0]['text']
                except Exception as e_api:
                    respuesta_ia = f"Error al conectar con el motor analítico de Gemini: {str(e_api)}"
                
                # Pintar la respuesta en la interfaz
                respuesta_placeholder.markdown(respuesta_ia)
                st.session_state.historial_chat.append({"role": "assistant", "content": respuesta_ia})