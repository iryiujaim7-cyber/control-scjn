import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def buscar_normatividades_scjn(termino):
    """
    Controla un navegador invisible con enrutamiento directo al buscador 
    de la Suprema Corte de Justicia de la Nación.
    """
    
    # 1. Configuración del "Navegador Fantasma" con camuflaje
    opciones = Options()
    opciones.add_argument("--headless") 
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--disable-gpu")
    
    # Fundamental para sitios de gobierno: simular que somos un navegador Chrome real en Windows
    opciones.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    resultados_scjn = []
    driver = None
    
    try:
        driver = webdriver.Chrome(options=opciones)
        
        # 2. ENRUTAMIENTO DIRECTO: Codificamos el término (ej. espacios a %20) y armamos la URL exacta
        termino_codificado = urllib.parse.quote(termino)
        url_busqueda = f"https://legislacion.scjn.gob.mx/consulta/buscador?tBusq=1&pageSizeOrd=50&q={termino_codificado}"
        
        # Viajamos directo a los resultados, saltándonos la página de inicio
        driver.get(url_busqueda)
        
        # 3. Esperar a que el servidor de la SCJN renderice la base de datos (le damos 6 segundos por ser pesada)
        time.sleep(6)
        
        # 4. Escanear la pantalla
        enlaces = driver.find_elements(By.TAG_NAME, "a")
        leyes_encontradas = set() 
        
        for enlace in enlaces:
            texto = enlace.text.strip()
            url_documento = enlace.get_attribute("href")
            
            # Filtro para capturar los títulos de las leyes (ignorar botones de menú)
            if texto and url_documento and len(texto) > 10:
                url_baja = url_documento.lower()
                # La SCJN usa estas palabras en los enlaces reales de los documentos
                if "consulta" in url_baja or "documento" in url_baja or "ordenamiento" in url_baja:
                    if "Buscador" not in texto and "avanzada" not in texto:
                        if texto not in leyes_encontradas:
                            leyes_encontradas.add(texto)
                            resultados_scjn.append({
                                "Normatividad": texto,
                                "Última actualización": "Búsqueda en tiempo real",
                                "Url Descarga": url_documento
                            })
            
            # Limitar a los 5 mejores para no saturar tu pantalla
            if len(resultados_scjn) >= 5:
                break
                
    except Exception as e:
        print(f"Error en la extracción automatizada: {e}")
        
    finally:
        # Apagar el navegador
        if driver:
            driver.quit()
            
    # Fallback de seguridad
    if not resultados_scjn:
        resultados_scjn.append({
            "Normatividad": f"No se encontraron resultados para '{termino}' o el portal de la SCJN está saturado.",
            "Última actualización": "Intenta con otra palabra clave",
            "Url Descarga": "https://legislacion.scjn.gob.mx/consulta/home"
        })
        
    return resultados_scjn
