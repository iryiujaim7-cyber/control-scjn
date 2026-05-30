import streamlit as st
import streamlit.components.v1 as components
from pypdf import PdfReader
from docx import Document
import google.generativeai as genai

# =====================================================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN
# =====================================================================
if "expediente" not in st.session_state: 
    st.session_state.expediente = {}

st.set_page_config(page_title="Ágora - Inteligencia Normativa", layout="wide")
st.title("🏛️ Ágora - Inteligencia Normativa")

# --- VERIFICACIÓN DE CREDENCIALES ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ No se encontró la llave GEMINI_API_KEY en los secretos de Streamlit.")
    st.info("Por favor, ve a Settings -> Secrets en tu app y añade: GEMINI_API_KEY = 'tu_llave'")
    st.stop()

# Configuración del modelo
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

col1, col2 = st.columns([7, 3])

# =====================================================================
# 2. PANEL IZQUIERDO: VISOR OFICIAL
# =====================================================================
with col1:
    st.subheader("🌐 Navegador SCJN Integrado")
    components.iframe("https://legislacion.scjn.gob.mx/consulta/home", height=800, scrolling=True)

# =====================================================================
# 3. PANEL DERECHO: ÁREA DE ANÁLISIS
# =====================================================================
with col2:
    st.subheader("📥 Área de Análisis")
    archivos = st.file_uploader("Sube tus leyes (PDF/DOCX):", accept_multiple_files=True)

    if archivos:
        for archivo in archivos:
            if archivo.name not in st.session_state.expediente:
                st.session_state.expediente[archivo.name] = {"archivo": archivo, "nombre_display": archivo.name}

        # --- RENOMBRADO RÁPIDO ---
        st.markdown("---")
        st.write("##### 🏷️ Renombrar leyes:")
        for nombre_original in list(st.session_state.expediente.keys()):
            nuevo_nombre = st.text_input(f"Renombrar {nombre_original}:", 
                                        value=st.session_state.expediente[nombre_original]["nombre_display"],
                                        key=f"input_{nombre_original}")
            st.session_state.expediente[nombre_original]["nombre_display"] = nuevo_nombre

    st.markdown("---")
    pregunta = st.chat_input("Plantea tu duda jurídica sobre los archivos cargados...")

    if pregunta:
        if not st.session_state.expediente:
            st.warning("⚠️ Primero sube y renombra tus leyes.")
        else:
            with st.status("🧠 Analizando documentos...", expanded=True) as status:
                try:
                    contexto_unificado = ""
                    for data in st.session_state.expediente.values():
                        archivo = data["archivo"]
                        nombre_final = data["nombre_display"]
                        
                        # Reset al puntero del archivo para leerlo nuevamente
                        archivo.seek(0)
                        
                        texto = ""
                        if archivo.name.endswith(".pdf"):
                            reader = PdfReader(archivo)
                            texto = "".join([p.extract_text() for p in reader.pages])
                        elif archivo.name.endswith(".docx"):
                            doc = Document(archivo)
                            texto = "\n".join([p.text for p in doc.paragraphs])
                        
                        contexto_unificado += f"\n\n--- DOCUMENTO: {nombre_final} ---\n{texto}"

                    instruccion = f"Basado en estos documentos:\n{contexto_unificado}\n\nPregunta: {pregunta}"
                    respuesta = model.generate_content(instruccion)
                    
                    st.markdown(respuesta.text)
                    status.update(label="✅ Análisis completado", state="complete")
                except Exception as e:
                    st.error(f"Error técnico: {e}")
