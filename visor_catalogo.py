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

# 2. INYECCIÓN DE IDENTIDAD VISUAL CORPORATIVA (CSS PERSONALIZADO)
st.markdown(f"""
    <style>
    /* Fondo principal blanco de la aplicación */
    .stApp {{
        background-color: #F8F9FA;
    }}
    
    /* Títulos principales en Azul Marino Profundo */
    h1, h2, h3 {{
        color: #1A2E40 !important;
        font-family: 'Georgia', serif;
        font-weight: bold;
        text-align: center;
    }}
    
    /* Textos secundarios y subtítulos en Gris Oxford */
    h4, p, span, label {{
        color: #4A5568 !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }}

    /* Contenedor del Logo centrado y con protagonismo */
    .logo-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem 0 1rem 0;
    }}

    /* Botón de acción en Azul Marino con texto blanco */
    div.stButton > button:first-child {{
        background-color: #1A2E40;
        color: #FFFFFF;
        border: 1px solid #1A2E40;
        border-radius: 4px;
        font-weight: bold;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        padding: 0.6rem 2rem;
        transition: all 0.3s ease;
    }}
    
    /* Efecto Hover para el botón: cambia a Dorado Corporativo */
    div.stButton > button:first-child:hover {{
        background-color: #C5A059;
        color: #FFFFFF;
        border-color: #C5A059;
    }}

    /* Valores de las Métricas Rápidas en Dorado Corporativo/Bronce */
    [data-testid="stMetricValue"] {{
        color: #C5A059 !important;
        font-family: 'Georgia', serif;
    }}
    
    /* Etiquetas de las métricas */
    [data-testid="stMetricLabel"] p {{
        color: #1A2E40 !important;
        font-weight: 600;
    }}
    
    /* Personalización armónica de la Tabla/Dataframe */
    div[data-testid="stDataFrame"] {{
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }}
    
    /* Estilo de los enlaces (Descargar última versión) en Dorado Corporativo */
    a {{
        color: #C5A059 !important;
        text-decoration: none !important;
        font-weight: 600;
    }}
    a:hover {{
        color: #1A2E40 !important;
        text-decoration: underline !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# 3. ENCABEZADO PRESIDENCIAL (PROTAGONISMO AL LOGO)
# Creamos tres columnas para centrar perfectamente el logotipo en el eje superior
_, col_center_logo, _ = st.columns([1, 2, 1])
with col_center_logo:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.image(LOGO_URL, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Título y subtítulos centrados con tipografía formal
st.markdown("<h1 style='font-size: 2.5rem; margin-bottom: 0.5rem;'>Catálogo y Control de Normatividades</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; font-weight: normal; margin-bottom: 2rem;'>En la siguiente tabla puedes consultar las últimas actualizaciones de diversas normatividades</h4>", unsafe_allow_html=True)
st.markdown("<hr style='border-top: 1px solid #E2E8F0; margin-bottom: 2rem;'>", unsafe_allow_html=True)

# 4. RUTAS DE INTERCAMBIO DE DATOS
EXCEL_PATH = "registro_normatividades.xlsx"
DOWNLOAD_DIR = "./descargas_leyes"

# Verificar existencia de la matriz de datos
if os.path.exists(EXCEL_PATH):
    df = pd.read_excel(EXCEL_PATH)
    
    # --- BLOQUE DE MÉTRICAS LINEALES ---
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total de Leyes Monitoreadas", value=len(df))
    with col2:
        archivos_descargados = len(os.listdir(DOWNLOAD_DIR)) if os.path.exists(DOWNLOAD_DIR) else 0
        st.metric(label="Archivos Guardados en Local", value=archivos_descargados)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- CUADRO COMPARATIVO INTERACTIVO ARMÓNICO ---
    st.markdown("<h3 style='text-align: left; font-size: 1.5rem; margin-bottom: 1rem;'>📋 Cuadro Comparativo de Actualizaciones</h3>", unsafe_allow_html=True)
    
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
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn, _ = st.columns([1, 3])
    with col_btn:
        if st.button("🔄 Forzar Ejecución del Scraper"):
            with st.spinner("Solicitando actualización al servidor..."):
                os.system("python actualizador_leyes.py")
            st.success("Petición enviada al bot de GitHub Actions.")

else:
    st.warning("⚠️ Cargando estructura base... Si acabas de desplegar la app, espera a que finalice el primer flujo en GitHub Actions.")
