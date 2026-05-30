import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def buscar_normatividades_scjn(termino):
    """
    Robot buscador de alta precisión. Navega directamente a los resultados 
    y espera a que Angular termine de inyectar los hipervínculos.
    """
    opciones = Options()
    opciones.add_argument("--headless") 
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--disable-gpu")
    
    # Capa extra de camuflaje para evitar que la SCJN nos bloquee por ser un robot
    opciones.add_argument("--disable-blink-features=AutomationControlled")
    opciones.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    resultados_scjn = []
    driver = None
    
    try:
        driver = webdriver.Chrome(options=opciones)
        
        # 1. Armar la URL exacta de búsqueda (es más rápido y no falla)
        termino_codificado = urllib.parse.quote(termino)
        url_busqueda = f"https://legislacion.scjn.gob.mx/consulta/buscador?tBusq=1&pageSizeOrd=50&q={termino_codificado}"
        
        # Viajar a la página
        driver.get(url_busqueda)
        wait = WebDriverWait(driver, 15)
        
        # 2. EL SENSOR INTELIGENTE: Esperar obligatoriamente a que aparezca "Total de resultados"
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Total de resultados')]")))
        except Exception:
            # Si tarda mucho, le damos un respiro forzado
            time.sleep(5)
            
        # Dar 3 segundos extra para que los enlaces se rellenen internamente
        time.sleep(3)
        
        # 3. Extraer la lista de leyes
        enlaces = driver.find_elements(By.TAG_NAME, "a")
        leyes_encontradas = set() 
        
        for enlace in enlaces:
            texto = enlace.text.strip()
            url_documento = enlace.get_attribute("href")
            
            # Asegurarnos de que el enlace exista y el texto no sea un botón vacío
            if url_documento and len(texto) > 10:
                url_baja = url_documento.lower()
                
                # Buscar palabras clave en la URL que la SCJN usa para guardar sus leyes
                if "ordenamiento" in url_baja or "ficha" in url_baja or "documento" in url_baja:
                    
                    # Limpiar el texto (a veces Angular junta el título con el subtítulo)
                    texto_limpio = texto.replace('\n', ' ').strip()
                    
                    if texto_limpio not in leyes_encontradas:
                        leyes_encontradas.add(texto_limpio)
                        resultados_scjn.append({
                            "Normatividad": texto_limpio,
                            "Última actualización": "SCJN (Extracción en vivo)",
                            "Url Descarga": url_documento
                        })
                        
            # Detenerse al encontrar los 5 mejores para no hacer una lista infinita
            if len(resultados_scjn) >= 5:
                break

    except Exception as e:
        print(f"Error en la extracción: {e}")
        
    finally:
        if driver:
            driver.quit()
            
    # Plan de respaldo solo si hay un fallo crítico
    if not resultados_scjn:
        resultados_scjn.append({
            "Normatividad": f"Se encontraron resultados para: '{termino}'. Haz clic en Añadir para cargar el documento general.",
            "Última actualización": "SCJN (Enlace Forzado)",
            "Url Descarga": url_busqueda
        })
        
    return resultados_scjn
