import streamlit as st
import pandas as pd
import os

# 1. CONFIGURACIÓN DE PÁGINA Y FAVICON INSTITUCIONAL
LOGO_URL = "https://raw.githubusercontent.com/iryiujaim7-cyber/control-scjn/main/logo.png"

st.set_page_config(
    page_title="Ágora - Control de Normatividades",
    page_icon=LOGO_URL,
    layout="wide"
)

# 2. INYECCIÓN DE IDENTIDAD VISUAL (CSS PERSONALIZADO)
st.markdown(f"""
    <style>
    /* Fondo principal blanco de la aplicación */
    .stApp {{
        background-color: #FFFFFF;
    }}
    
    /* Encabezados y textos generales en Púrpura Profundo Elegante */
    h1, h2, h3, h4, p, span, label {{
        color: rgb(85, 37, 130) !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }}

    /* Botón de acción en Verde Brillante Institucional */
    div.stButton > button:first-child {{
        background-color: rgb(142, 198, 63);
        color: white;
        border: None;
        border-radius: 10px;
        font-weight: bold;
        padding: 0.5rem 1.5rem;
    }}
    
    /* Efecto Hover para el botón */
    div.stButton > button:first-child:hover {{
        background-color: rgb(85, 37, 130);
        color: white;
        border: None;
    }}

    /* Valores de las Métricas Rápidas en Verde Brillante */
    [data-testid="stMetricValue"] {{
        color: rgb(142, 198, 63) !important;
    }}
    
    /* Ajuste de color para los enlaces dentro de la tabla */
    a {{
        color: rgb(85, 37, 130) !important;
        text-decoration: underline;
    }}
    a:hover {{
        color: rgb(142, 198, 63) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# 3. ENCABEZADO ESTRUCTURADO CON LOGO DE ÁGORA
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    st.image(LOGO_URL, width=180)

with col_titulo:
    st.title("Catálogo y Control de Normatividades")

# Redacción personalizada solicitada
st.markdown("#### En la siguiente tabla puedes consultar las últimas actualizaciones de diversas normatividades")
st.markdown("---")

# 4. RUTAS DE INTERCAMBIO DE DATOS
EXCEL_PATH = "registro_normatividades.xlsx"
DOWNLOAD_DIR = "./descargas_leyes"

# Verificar existencia de la matriz de datos
if os.path.exists(EXCEL_PATH):
    df = pd.read_excel(EXCEL_PATH)
    
    # --- BLOQUE DE MÉTRICAS ---
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total de Leyes Monitoreadas", value=len(df))
    with col2:
        archivos_descargados = len(os.listdir(DOWNLOAD_DIR)) if os.path.exists(DOWNLOAD_DIR) else 0
        st.metric(label="Archivos Guardados en Local", value=archivos_descargados)
        
    st.markdown(" ")
    
    # --- CUADRO COMPARATIVO INTERACTIVO ---
    st.subheader("📋 Cuadro Comparativo de Actualizaciones")
    
    # Renderizado de la tabla con los nombres de columnas y el LinkColumn configurado
    st.dataframe(
        df, 
        use_container_width=True,
        column_config={
            "Normatividad": st.column_config.TextColumn("Normatividad"),
            "Última modificación": st.column_config.TextColumn("Última actualización de la normatividad"),
            "Descarga normatividad": st.column_config.LinkColumn(
                "Descargar normatividad",
                display_text="Descargar última versión"
            )
        }
    )
    
    # --- INTERFAZ DE CONTROL MANUAL ---
    st.markdown(" ")
    if st.button("🔄 Forzar Ejecución del Scraper"):
        with st.spinner("Solicitando actualización al servidor..."):
            os.system("python actualizador_leyes.py")
        st.success("Petición enviada. El bot de GitHub Actions procesará los cambios en segundo plano.")

else:
    st.warning("⚠️ Cargando estructura base... Si acabas de desplegar la app, espera a que finalice el primer flujo en GitHub Actions.")
