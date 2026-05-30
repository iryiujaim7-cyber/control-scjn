import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def buscar_normatividades_scjn(termino):
    """
    Controla un navegador invisible para buscar en tiempo real dentro 
    del portal de legislación de la Suprema Corte de Justicia de la Nación.
    """
    
    # 1. Configuración del "Navegador Fantasma" para la nube
    opciones = Options()
    opciones.add_argument("--headless") 
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--disable-gpu")
    
    resultados_scjn = []
    driver = None
    
    try:
        # Iniciar Chrome utilizando las configuraciones anteriores
        driver = webdriver.Chrome(options=opciones)
        
        # 2. Navegar directamente al portal de la SCJN que indicaste
        url_scjn = "https://legislacion.scjn.gob.mx/consulta/home"
        driver.get(url_scjn)
        
        # 3. Esperar a que la página cargue y localizar la barra de búsqueda principal
        wait = WebDriverWait(driver, 10)
        caja_busqueda = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']")))
        
        # 4. Simular que un humano escribe el término y presiona la tecla ENTER
        caja_busqueda.clear()
        caja_busqueda.send_keys(termino)
        caja_busqueda.send_keys(Keys.RETURN)
        
        # 5. Pausa estratégica de 4 segundos para dejar que el servidor de la SCJN procese y cargue la lista
        time.sleep(4)
        
        # 6. Escanear la pantalla en busca de los resultados (los hipervínculos de las leyes)
        enlaces = driver.find_elements(By.TAG_NAME, "a")
        leyes_encontradas = set() # Set para evitar mostrar resultados duplicados
        
        for enlace in enlaces:
            texto = enlace.text.strip()
            url_documento = enlace.get_attribute("href")
            
            # Filtro inteligente: Si el enlace tiene texto largo y apunta a un documento o consulta interna
            if len(texto) > 15 and url_documento and ("consulta" in url_documento or "Documento" in url_documento):
                if texto not in leyes_encontradas:
                    leyes_encontradas.add(texto)
                    resultados_scjn.append({
                        # El diccionario tiene los nombres exactos que tu archivo visor_catalogo.py espera recibir
                        "Normatividad": texto,
                        "Última actualización": "Búsqueda en tiempo real",
                        "Url Descarga": url_documento
                    })
            
            # Limitar a los 5 mejores resultados para mantener tu interfaz limpia
            if len(resultados_scjn) >= 5:
                break
                
    except Exception as e:
        print(f"Error en la extracción automatizada: {e}")
        
    finally:
        # Apagar el navegador al terminar para liberar la memoria del servidor de Streamlit
        if driver:
            driver.quit()
            
    # Fallback de seguridad: Si la página de la SCJN se cae o no responde, devuelve un aviso controlado
    if not resultados_scjn:
        resultados_scjn.append({
            "Normatividad": f"No se encontraron resultados para '{termino}' o el portal de la SCJN está saturado.",
            "Última actualización": "Intenta con otra palabra clave",
            "Url Descarga": "https://legislacion.scjn.gob.mx/consulta/home"
        })
        
    return resultados_scjn
