import streamlit as st
import pandas as pd
import os

# Configuración de la página web local
st.set_page_config(page_title="Control de Normatividades - SCJN", page_icon="⚖️", layout="wide")

st.title("⚖️ Catálogo y Control de Normatividades")
st.markdown("Este cuadro comparativo refleja las últimas actualizaciones consultadas automáticamente en el portal de la SCJN.")

EXCEL_PATH = "registro_normatividades.xlsx"
DOWNLOAD_DIR = "./descargas_leyes"

# Verificar si el script automatizado ya generó los datos
if os.path.exists(EXCEL_PATH):
    df = pd.read_excel(EXCEL_PATH)
    
    # --- MÉTRICAS RÁPIDAS ---
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total de Leyes Monitoreadas", value=len(df))
    with col2:
        archivos_descargados = len(os.listdir(DOWNLOAD_DIR)) if os.path.exists(DOWNLOAD_DIR) else 0
        st.metric(label="Archivos Guardados en Local", value=archivos_descargados)
        
    st.markdown("---")
    
    # --- CUADRO COMPARATIVO ---
    st.subheader("📋 Cuadro Comparativo de Actualizaciones")
    
    st.dataframe(
        df, 
        use_container_width=True,
        column_config={
            "Normatividad": st.column_config.TextColumn("Nombre de la Norma", help="Nombre oficial de la ley buscada"),
            "Última modificación": st.column_config.TextColumn("Dato de Última Actualización (SCJN)"),
            "Descarga normatividad": st.column_config.TextColumn("Estado del Archivo Local")
        }
    )
    
    # --- BOTÓN DE ACTUALIZACIÓN MANUAL ---
    st.markdown(" ")
    if st.button("🔄 Forzar Ejecución del Scraper"):
        with st.spinner("Ejecutando actualizador en segundo plano..."):
            os.system("python actualizador_leyes.py")
        st.success("¡Script ejecutado! Recarga la página para ver los cambios.")

else:
    st.warning("⚠️ Aún no se ha generado el archivo 'registro_normatividades.xlsx'. Ejecuta el script principal primero para poblar el cuadro comparativo.")
