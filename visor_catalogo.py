import streamlit as st
import pandas as pd
import os

# 1. CONFIGURACIÓN DE PÁGINA Y FAVICON
# Usamos la URL directa de la imagen en tu GitHub para el favicon
LOGO_URL = "https://raw.githubusercontent.com/iryiujaim7-cyber/control-scjn/main/logo.png"

st.set_page_config(
    page_title="Ágora - Control de Normatividades",
    page_icon=LOGO_URL,
    layout="wide"
)

# 2. INYECCIÓN DE COLORES PERSONALIZADOS (CSS)
st.markdown(f"""
    <style>
    /* Color de fondo principal y texto */
    .stApp {{
        background-color: #FFFFFF;
    }}
    
    /* Títulos y Encabezados en Púrpura */
    h1, h2, h3, h4, p, span {{
        color: rgb(85, 37, 130) !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }}

    /* Botón en Verde con texto blanco */
    div.stButton > button:first-child {{
        background-color: rgb(142, 198, 63);
        color: white;
        border: None;
        border-radius: 10px;
        font-weight: bold;
    }}
    
    div.stButton > button:first-child:hover {{
        background-color: rgb(85, 37, 130);
        color: white;
    }}

    /* Estilo de la tabla (Métricas) */
    [data-testid="stMetricValue"] {{
        color: rgb(142, 198, 63) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# 3. ENCABEZADO CON LOGO
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    st.image(LOGO_URL, width=200)

with col_titulo:
    st.title("Catálogo y Control de Normatividades")

st.markdown("#### En la siguiente tabla puedes consultar las últimas actualizaciones de diversas normatividades")

# 4. LÓGICA DE DATOS
EXCEL_PATH = "registro_normatividades.xlsx"
DOWNLOAD_DIR = "./descargas_leyes"

if os.path.exists(EXCEL_PATH):
    df = pd.read_excel(EXCEL_PATH)
    
    # --- MÉTRICAS ---
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
            "Normatividad": st.column_config.TextColumn("Normatividad"),
            "Última modificación": st.column_config.TextColumn("Última actualización de la normatividad"),
            "Descarga normatividad": st.column_config.TextColumn("Descargar normatividad")
        }
    )
    
    st.markdown(" ")
    if st.button("🔄 Forzar Ejecución del Scraper"):
        with st.spinner("Ejecutando actualizador en segundo plano..."):
            # Nota: En Streamlit Cloud esto ejecutará el script, pero GitHub Actions es quien guardará los cambios permanentes
            os.system("python actualizador_leyes.py")
        st.success("Petición enviada. El sistema se actualizará en breve.")

else:
    st.warning("⚠️ Cargando base de datos... Si es la primera vez, el bot de GitHub Actions debe terminar su proceso.")
