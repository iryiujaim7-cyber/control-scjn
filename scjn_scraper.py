import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def buscar_normatividades_scjn(termino):
    opciones = Options()
    opciones.add_argument("--headless")
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--disable-gpu")
    # Este User-Agent es vital; sin él, nos bloquean instantáneamente
    opciones.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    resultados_scjn = []
    driver = None
    
    try:
        driver = webdriver.Chrome(options=opciones)
        # Búsqueda directa
        termino_enc = urllib.parse.quote(termino)
        driver.get(f"https://legislacion.scjn.gob.mx/consulta/buscador?q={termino_enc}")
        
        # ESPERA HUMANA: 8 segundos para que Angular renderice los resultados de forma natural
        time.sleep(8)
        
        # Buscamos todos los contenedores de resultados de la SCJN
        # Usamos los selectores que identificaste en tu video
        elementos = driver.find_elements(By.TAG_NAME, "mat-expansion-panel")
        
        if not elementos:
            # Plan B: Si no hay paneles, buscamos por elementos de texto que contengan "Vigente"
            elementos = driver.find_elements(By.XPATH, "//*[contains(text(), 'Vigente')]")

        for elem in elementos[:5]: # Solo los primeros 5 para rapidez
            try:
                texto = elem.text.strip()
                # Limpiamos el texto para que solo sea el título
                if texto:
                    titulo = texto.split('\n')[0]
                    # Generamos el enlace directo basado en la búsqueda
                    url_fija = f"https://legislacion.scjn.gob.mx/consulta/buscador?q={termino_enc}"
                    
                    resultados_scjn.append({
                        "Normatividad": titulo,
                        "Última actualización": "SCJN (Disponible)",
                        "Url Descarga": url_fija
                    })
            except:
                continue

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if driver: driver.quit()
        
    if not resultados_scjn:
        return [{"Normatividad": "No se encontraron resultados automáticos.", "Última actualización": "SCJN", "Url Descarga": "https://legislacion.scjn.gob.mx/consulta/home"}]
        
    return resultados_scjn
