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

# 3. ENCAB
