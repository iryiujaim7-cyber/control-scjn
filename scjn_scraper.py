import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def buscar_normatividades_scjn(termino):
    """
    Extracción Profunda (Deep Scraper):
    1. Busca la ley general.
    2. Entra a la página de detalles de cada ley.
    3. Extrae la fecha de la última modificación (Registro 1).
    4. Captura la URL directa de descarga (Icono Word/PDF) de esa modificación.
    """
    opciones = Options()
    opciones.add_argument("--headless") 
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--disable-gpu")
    opciones.add_argument("--window-size=1920,1080") 
    opciones.add_argument("--disable-blink-features=AutomationControlled")
    opciones.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    resultados_scjn = []
    driver = None
    
    try:
        driver = webdriver.Chrome(options=opciones)
        termino_codificado = urllib.parse.quote(termino)
        url_busqueda = f"https://legislacion.scjn.gob.mx/consulta/buscador?tBusq=1&pageSizeOrd=50&q={termino_codificado}"
        
        # FASE 1: Obtener las leyes principales de la búsqueda
        driver.get(url_busqueda)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Total de resultados') or contains(text(), 'No se encontraron')]")))
        time.sleep(3)
        
        enlaces = driver.find_elements(By.TAG_NAME, "a")
        leyes_encontradas = []
        nombres_vistos = set()
        palabras_ignoradas = ["buscar", "avanzada", "inicio", "filtros", "resumen", "extractos", "descargar", "scjn"]
        
        for enlace in enlaces:
            texto = enlace.text.replace('\n', ' ').strip()
            url_general = enlace.get_attribute("href")
            
            if url_general and len(texto) > 15:
                if not any(palabra in texto.lower() for palabra in palabras_ignoradas):
                    if texto not in nombres_vistos:
                        nombres_vistos.add(texto)
                        leyes_encontradas.append({"nombre": texto, "url": url_general})
                        
            # Limitamos a 3 leyes para que el sistema sea rápido y no se quede pensando demasiado tiempo
            if len(leyes_encontradas) >= 3:
                break
                
        # FASE 2: Extracción Profunda (Entrar a cada ley y sacar el último archivo)
        for ley in leyes_encontradas:
            driver.get(ley["url"])
            time.sleep(3.5) # Esperamos a que Angular cargue las tarjetas de "Reformas del Ordenamiento"
            
            fecha_modificacion = "Fecha no disponible"
            url_descarga_directa = ley["url"] # Por defecto, dejamos la URL de la página si falla
            
            try:
                # 1. Extraemos la "Fecha de publicación" de la primera tarjeta (La más reciente)
                elemento_fecha = driver.find_element(By.XPATH, "(//*[contains(text(), 'Fecha de publicación:')])[1]")
                fecha_modificacion = elemento_fecha.text.strip()
                
                # 2. Extraemos el enlace del icono de descarga (Word o PDF) de esa misma primera tarjeta
                # Buscamos un enlace que contenga 'Descarga', 'doc', 'docx' o 'pdf'
                elemento_descarga = driver.find_element(By.XPATH, "(//a[contains(@href, 'Descarga') or contains(@href, 'doc') or contains(@href, 'pdf')])[1]")
                url_descarga_directa = elemento_descarga.get_attribute("href")
                
            except Exception as e:
                # Si la ley no tiene reformas o documentos adjuntos, lo manejamos en silencio
                pass
                
            resultados_scjn.append({
                "Normatividad": ley["nombre"],
                "Última actualización": fecha_modificacion,
                "Url Descarga": url_descarga_directa
            })

    except Exception as e:
        print(f"Error en la extracción: {e}")
        
    finally:
        if driver:
            driver.quit()
            
    if not resultados_scjn:
        resultados_scjn.append({
            "Normatividad": f"No se pudo completar la extracción para '{termino}'.",
            "Última actualización": "Intenta de nuevo",
            "Url Descarga": url_busqueda
        })
        
    return resultados_scjn
