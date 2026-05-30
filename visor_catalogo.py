import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from scjn_scraper import buscar_normatividades_scjn

# =====================================================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN
# =====================================================================
if "expediente" not in st.session_state: st.session_state.expediente = {}
if "resultados_busqueda" not in st.session_state: st.session_state.resultados_busqueda = []

st.set_page_config(page_title="Ágora - Inteligencia Normativa", layout="wide")
st.title("🏛️ Ágora - Inteligencia Normativa")

col1, col2 = st.columns([1, 1])

# =====================================================================
# 2. PANEL IZQUIERDO: BÚSQUEDA Y NAVEGADOR
# =====================================================================
with col1:
    st.subheader("🔍 Consulta Directa en la SCJN")
    termino = st.text_input("Escribe el concepto a buscar:")
    
    if st.button("Buscar en SCJN"):
        with st.spinner("Navegando en los servidores de la Corte..."):
            st.session_state.resultados_busqueda = buscar_normatividades_scjn(termino)
            st.rerun()

    if st.session_state.resultados_busqueda:
        st.markdown("### Resultados encontrados:")
        for idx, item in enumerate(st.session_state.resultados_busqueda):
            st.markdown(f"**🏛️ {item['Normatividad']}**")
            st.caption(f"ℹ️ {item.get('Detalles', 'SCJN')}")
            if st.button("Añadir al Expediente", key=f"btn_{idx}"):
                st.session_state.expediente[item['Normatividad']] = item['Url Descarga']
                st.success("¡Añadido!")
            st.divider()

    st.subheader("🌐 Navegador SCJN Integrado")
    with st.expander("Abrir visor oficial de la Corte"):
        components.iframe("https://legislacion.scjn.gob.mx/consulta/home", height=500, scrolling=True)

# =====================================================================
# 3. PANEL DERECHO: CONSULTOR JURÍDICO (IA)
# =====================================================================
with col2:
    st.subheader("🤖 Consultor Jurídico")
    
    if not st.session_state.expediente:
        st.info("Tu expediente está vacío. Busca y añade una ley para comenzar.")
    
    pregunta = st.chat_input("Plantea tu duda jurídica sobre estas leyes...")
    
    if pregunta:
        if not st.session_state.expediente:
            st.error("Por favor, añade al menos una ley a tu expediente primero.")
        else:
            with st.status("🧠 Analizando documentos con Google GenAI...", expanded=True) as status:
                try:
                    # Conexión directa y moderna
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    contexto = "\n".join([f"Normatividad cargada: {k}" for k in st.session_state.expediente.keys()])
                    instruccion = f"Contexto legal:\n{contexto}\n\nPregunta: {pregunta}\n\nResponde como un experto jurídico:"
                    
                    respuesta = model.generate_content(instruccion)
                    
                    st.markdown(respuesta.text)
                    status.update(label="✅ Análisis completado", state="complete")
                except Exception as e:
                    st.error(f"Error técnico: {e}")
