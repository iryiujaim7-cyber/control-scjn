import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def buscar_normatividades_scjn(termino):
    opciones = Options()
    opciones.add_argument("--headless") 
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--disable-gpu")
    
    # CLAVE: Forzar una resolución de monitor grande para que Angular no oculte elementos
    opciones.add_argument("--window-size=1920,1080") 
    opciones.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    resultados_scjn = []
    driver = None
    
    try:
        driver = webdriver.Chrome(options=opciones)
        termino_codificado = urllib.parse.quote(termino)
        url_busqueda = f"https://legislacion.scjn.gob.mx/consulta/buscador?tBusq=1&pageSizeOrd=50&q={termino_codificado}"
        
        driver.get(url_busqueda)
        wait = WebDriverWait(driver, 15)
        
        # Esperar a que la base de datos de la SCJN renderice
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Total de resultados') or contains(text(), 'No se encontraron')]")))
        time.sleep(3) # Pausa breve para que terminen las animaciones de la interfaz
        
        # ESTRATEGIA 1: Buscar hipervínculos tradicionales
        enlaces = driver.find_elements(By.TAG_NAME, "a")
        leyes_encontradas = set()
        palabras_ignoradas = ["buscar", "avanzada", "inicio", "filtros", "resumen", "extractos", "descargar", "scjn"]
        
        for enlace in enlaces:
            texto = enlace.text.strip()
            url_documento = enlace.get_attribute("href")
            
            if url_documento and len(texto) > 15:
                # Si el enlace no es un botón genérico del menú
                if not any(palabra in texto.lower() for palabra in palabras_ignoradas):
                    texto_limpio = texto.replace('\n', ' ').strip()
                    if texto_limpio not in leyes_encontradas:
                        leyes_encontradas.add(texto_limpio)
                        resultados_scjn.append({
                            "Normatividad": texto_limpio,
                            "Última actualización": "SCJN (Extracción directa)",
                            "Url Descarga": url_documento
                        })
            if len(resultados_scjn) >= 5:
                break
                
        # ESTRATEGIA 2: Si Angular ofuscó los enlaces, leemos literalmente la pantalla
        if not resultados_scjn:
            cuerpo_texto = driver.find_element(By.TAG_NAME, "body").text
            lineas = cuerpo_texto.split('\n')
            
            for i, linea in enumerate(lineas):
                # En la SCJN, debajo de cada ley siempre dice "Ámbito: FEDERAL..."
                if "Ámbito: " in linea or "Categoría: " in linea:
                    titulo_ley = lineas[i-1].strip() # Tomamos la línea de arriba (el título)
                    
                    if len(titulo_ley) > 10 and titulo_ley not in leyes_encontradas and "resultados" not in titulo_ley.lower():
                        leyes_encontradas.add(titulo_ley)
                        # Como los enlaces están bloqueados, asignamos la URL general
                        resultados_scjn.append({
                            "Normatividad": titulo_ley,
                            "Última actualización": "SCJN (Lectura visual)",
                            "Url Descarga": url_busqueda
                        })
                if len(resultados_scjn) >= 5:
                    break

    except Exception as e:
        print(f"Error en la extracción: {e}")
        
    finally:
        if driver:
            driver.quit()
            
    if not resultados_scjn:
        resultados_scjn.append({
            "Normatividad": f"No hay resultados disponibles en la SCJN para '{termino}'.",
            "Última actualización": "Verifica tu búsqueda",
            "Url Descarga": url_busqueda
        })
        
    return resultados_scjn
