import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def buscar_normatividades_scjn(termino):
    opciones = Options()
    opciones.add_argument("--headless") # Navegador invisible
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    # Este user-agent es CLAVE para que no detecten que eres un script
    opciones.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=opciones)
    resultados = []
    
    try:
        driver.get("https://legislacion.scjn.gob.mx/consulta/home")
        time.sleep(5) # Espera a que cargue la interfaz de la Corte
        
        # Buscamos la caja de texto por su atributo 'formcontrolname'
        caja = driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="q"]')
        caja.send_keys(termino)
        caja.send_keys(Keys.ENTER)
        
        time.sleep(6) # Esperamos a que los resultados se rendericen
        
        # Capturamos los elementos que contienen las leyes
        elementos = driver.find_elements(By.TAG_NAME, "h4") # Ajusta esto según el tag donde veas los títulos
        for e in elementos[:5]:
            resultados.append({
                "Normatividad": e.text,
                "Url Descarga": driver.current_url
            })
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()
    return resultados
