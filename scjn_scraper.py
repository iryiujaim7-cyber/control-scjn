import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def buscar_normatividades_scjn(termino):
    """
    Robot optimizado para evadir bloqueos de Angular Material en la SCJN.
    Simula comportamiento humano interactuando con los selectores exactos del DOM.
    """
    
    opciones = Options()
    opciones.add_argument("--headless") 
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--disable-gpu")
    opciones.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    resultados_scjn = []
    driver = None
    
    try:
        driver = webdriver.Chrome(options=opciones)
        
        # 1. Entrar por la puerta grande (página de inicio) para no alertar a Angular
        driver.get("https://legislacion.scjn.gob.mx/consulta/home")
        wait = WebDriverWait(driver, 15) 
        
        # 2. ATAQUE DE PRECISIÓN: Usamos el atributo exacto que descubriste en el código HTML
        caja_busqueda = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[formcontrolname="q"]')))
        
        # 3. Simular escritura humana
        caja_busqueda.clear()
        caja_busqueda.send_keys(termino)
        time.sleep(1) # Pequeña pausa para que Angular registre el texto
        
        # 4. Enviar el formulario (Enter)
        caja_busqueda.send_keys(Keys.ENTER)
        
        # 5. Pausa táctica: Angular hace la petición a la base de datos sin recargar la página
        time.sleep(6)
        
        # 6. Escanear la nueva información generada
        enlaces = driver.find_elements(By.TAG_NAME, "a")
        leyes_encontradas = set() 
        
        for enlace in enlaces:
            texto = enlace.text.strip()
            url_documento = enlace.get_attribute("href")
            
            if url_documento and len(texto) > 10:
                url_baja = url_documento.lower()
                # Filtrar solo los enlaces que contienen leyes
                if "consulta" in url_baja or "documento" in url_baja or "ordenamiento" in url_baja:
                    if "Buscador" not in texto and "avanzada" not in texto and "SCJN" not in texto:
                        if texto not in leyes_encontradas:
                            leyes_encontradas.add(texto)
                            resultados_scjn.append({
                                "Normatividad": texto,
                                "Última actualización": "Búsqueda exitosa",
                                "Url Descarga": url_documento
                            })
                            
            if len(resultados_scjn) >= 5:
                break
                
        # 7. Plan de Respaldo por si Angular ofusca los enlaces (Pasa seguido en páginas gubernamentales)
        if not resultados_scjn:
            import urllib.parse
            texto_pantalla = driver.find_element(By.TAG_NAME, "body").text
            # Si el robot ve que sí hubo resultados pero no pudo sacar el enlace directo...
            if "Total de resultados" in texto_pantalla:
                url_directa = f"https://legislacion.scjn.gob.mx/consulta/buscador?q={urllib.parse.quote(termino)}"
                resultados_scjn.append({
                    "Normatividad": f"Se encontraron resultados para: '{termino}'. Haz clic en Añadir para cargar el dictamen principal.",
                    "Última actualización": "SCJN (Enlace Forzado)",
                    "Url Descarga": url_directa
                })

    except Exception as e:
        print(f"Error en la extracción: {e}")
        
    finally:
        if driver:
            driver.quit()
            
    if not resultados_scjn:
        resultados_scjn.append({
            "Normatividad": f"No se pudo extraer '{termino}'. La SCJN está bloqueando la conexión automatizada.",
            "Última actualización": "Error de servidor",
            "Url Descarga": "https://legislacion.scjn.gob.mx/consulta/home"
        })
        
    return resultados_scjn
