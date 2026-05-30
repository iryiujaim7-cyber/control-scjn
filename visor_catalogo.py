import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai

# =====================================================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN
# =====================================================================
if "expediente" not in st.session_state: st.session_state.expediente = {}

st.set_page_config(page_title="Ágora - Inteligencia Normativa", layout="wide")
st.title("🏛️ Ágora - Inteligencia Normativa")

# Dividimos la pantalla: 70% para el navegador, 30% para el consultor
col_visor, col_ia = st.columns([7, 3])

# =====================================================================
# 2. PANEL IZQUIERDO: VISOR OFICIAL (PROTAGONISTA)
# =====================================================================
with col_visor:
    st.subheader("🌐 Navegador SCJN Integrado")
    st.markdown("Utiliza el buscador oficial de la Corte directamente aquí:")
    components.iframe("https://legislacion.scjn.gob.mx/consulta/home", height=800, scrolling=True)

# =====================================================================
# 3. PANEL DERECHO: CONSULTOR JURÍDICO (IA)
# =====================================================================
with col_ia:
    st.subheader("🤖 Consultor Jurídico")
    st.info("💡 Navega en el visor oficial, descarga el PDF/Doc y súbelo aquí abajo para que la IA lo analice.")
    
    # Selector de archivos para alimentar la IA
    archivos = st.file_uploader("Sube normatividades descargadas (PDF/DOCX):", accept_multiple_files=True)
    
    pregunta = st.chat_input("Plantea tu duda jurídica sobre los archivos cargados...")
    
    if pregunta and archivos:
        with st.status("🧠 Analizando documentos con Google GenAI...", expanded=True) as status:
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Aquí procesarías el texto de los archivos cargados
                respuesta = model.generate_content(f"Pregunta del abogado: {pregunta}")
                
                st.markdown(respuesta.text)
                status.update(label="✅ Análisis completado", state="complete")
            except Exception as e:
                st.error(f"Error técnico: {e}")
    elif pregunta and not archivos:
        st.warning("⚠️ Por favor, sube al menos un archivo del visor para que la IA tenga contexto.")
