import streamlit as st
import time
from io import BytesIO
import google.generativeai as genai
from scjn_scraper import buscar_normatividades_scjn

# =====================================================================
# 1. INICIALIZACIÓN DE MEMORIA Y CONFIGURACIÓN
# =====================================================================
if "expediente" not in st.session_state: st.session_state.expediente = {}
if "resultados_busqueda" not in st.session_state: st.session_state.resultados_busqueda = []

st.set_page_config(page_title="Ágora - Inteligencia Normativa", layout="wide")
st.title("🏛️ Ágora - Inteligencia Normativa")

col1, col2 = st.columns([1, 1])

# =====================================================================
# 2. PANEL DE BÚSQUEDA (COLUMNA IZQUIERDA)
# =====================================================================
with col1:
    st.subheader("🔍 Consulta Directa en la SCJN")
    termino = st.text_input("Escribe el concepto a buscar:")
    
    if st.button("Buscar en SCJN"):
        with st.spinner("Navegando en los servidores de la Corte..."):
            st.session_state.resultados_busqueda = buscar_normatividades_scjn(termino)
            st.rerun()

    # Visualización de resultados corregida para evitar errores de renderizado
    if st.session_state.resultados_busqueda:
        st.markdown("### Resultados encontrados:")
        for idx, item in enumerate(st.session_state.resultados_busqueda):
            # Imprimimos el título de manera independiente para asegurar visibilidad
            st.markdown(f"**{item['Normatividad']}**")
            st.caption(f"📅 {item['Última actualización']}")
            
            if st.button("Añadir al Expediente", key=f"btn_{idx}"):
                st.session_state.expediente[item['Normatividad']] = item['Url Descarga']
                st.success(f"¡{item['Normatividad']} añadida!")
            
            st.divider()

# =====================================================================
# 3. PANEL DE CONSULTA DE IA (COLUMNA DERECHA)
# =====================================================================
with col2:
    st.subheader("🤖 Consultor Jurídico")
    
    if not st.session_state.expediente:
        st.info("Tu expediente está vacío. Busca y añade una ley para comenzar.")
    else:
        st.write("Leyes en tu expediente actual:")
        for ley in st.session_state.expediente.keys():
            st.markdown(f"- 🏛️ {ley}")
            
    pregunta = st.chat_input("Plantea tu duda jurídica sobre estas leyes...")
    
    if pregunta:
        if not st.session_state.expediente:
            st.error("Por favor, añade al menos una ley a tu expediente primero.")
        else:
            with st.status("🧠 Analizando documentos con Google GenAI...", expanded=True) as status:
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    model = genai.GenerativeModel('gemini-flash-latest')
                    
                    # Unimos los nombres de las leyes en el contexto
                    contexto = "\n".join([f"Normatividad: {k}" for k in st.session_state.expediente.keys()])
                    
                    # Llamada a la IA
                    instruccion = f"Basado estrictamente en las normatividades cargadas:\n{contexto}\n\nResponde a: {pregunta}"
                    respuesta = model.generate_content(instruccion)
                    
                    st.markdown(respuesta.text)
                    status.update(label="✅ Análisis completado", state="complete")
                except Exception as e:
                    st.error(f"Error técnico: {e}")
