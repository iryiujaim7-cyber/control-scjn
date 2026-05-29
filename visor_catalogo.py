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

# 2. INYECCIÓN DE IDENTIDAD VISUAL CORPORATIVA (MÁXIMA COMPRESIÓN)
st.markdown(f"""
    <style>
    /* Fondo principal de la aplicación */
    .stApp {{
        background-color: #F8F9FA;
    }}
    
    /* Reducción del espacio en blanco superior general de la página */
    .block-container {{
        padding-top: 0.5rem !important;
        padding-bottom: 1rem !important;
    }}
    
    /* BLOQUE UNIFICADO: Alineación del logo y títulos sin espacios */
    .header-block {{
        text-align: center;
        margin-top: 0px !important;
        padding-top: 0px !important;
    }}
    
    .header-block img {{
        display: block;
        margin: 0 auto !important;
        padding: 0 !important;
        max-width: 280px; /* Tamaño controlado del logotipo */
        height: auto;
    }}
    
    .header-block h1 {{
        color: #1A2E40 !important;
        font-family: 'Georgia', serif;
        font-weight: bold;
        margin-top: 5px !important; /* Espacio mínimo e inmediato debajo del logo */
        margin-bottom: 0.2rem !important;
        font-size: 2.3rem;
    }}
    
    h2, h3 {{
        color: #1A2E40 !important;
        font-family: 'Georgia', serif;
        font-weight: bold;
    }}
    
    /* Textos secundarios y subtítulos en Gris Oxford */
    h4, p, span, label {{
        color: #4A5568 !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }}

    /* Botón de acción en Azul Marino */
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
    
    /* Efecto Hover para el botón */
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
    
    /* Estilo de los enlaces en Dorado Corporativo */
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

# 3. ENCABEZADO INTEGRADO EN UN SOLO BLOQUE HTML 
# Al meter el logo y el h1 juntos, evitamos la separación estructural de Streamlit
st.markdown(f"""
    <div class="header-block">
        <img src="{LOGO_URL}" alt="Logo Ágora">
        <h1>Catálogo y Control de Normatividades</h1>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<h4 style='text-align: center; font-weight: normal; margin-top: 0px; margin-bottom: 1.5rem; font-size: 1.1rem;'>En la siguiente tabla puedes consultar las últimas actualizaciones de diversas normatividades</h4>", unsafe_allow_html=True)
st.markdown("<hr style='border-top: 1px solid #E2E8F0; margin-top: 0px; margin-bottom: 1.5rem;'>", unsafe_allow_html=True)

# 4. RUTAS DE INTERCAMBIO DE DATOS
EXCEL_PATH = "registro_normatividades.xlsx"
DOWNLOAD_DIR = "./descargas_leyes"

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
    st.markdown("<h3 style='text-align: left; font-size: 1.4rem; margin-bottom: 0.8rem;'>📋 Cuadro Comparativo de Actualizaciones</h3>", unsafe_allow_html=True)
    
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
