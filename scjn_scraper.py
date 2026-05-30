import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def buscar_normatividades_scjn(termino):
    opciones = Options()
    opciones.add_argument("--headless")
    opciones.add_argument("--window-size=1920,1080")
    opciones.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=opciones)
    resultados = []
    
    try:
        url = f"https://legislacion.scjn.gob.mx/consulta/buscador?q={termino.replace(' ', '%20')}"
        driver.get(url)
        time.sleep(8) # Espera paciente para Angular
        
        # BUSCAMOS LOS CONTENEDORES PRINCIPALES DE LEYES
        paneles = driver.find_elements(By.TAG_NAME, "mat-expansion-panel")
        
        for panel in paneles[:5]:
            # EXTRAEMOS EL TÍTULO (Usando un XPATH que apunta al primer párrafo dentro del panel)
            titulo = panel.find_element(By.XPATH, ".//p[contains(@class, 'ng-star-inserted')]").text
            # EXTRAEMOS EL ÁMBITO O FECHA (Buscando texto pequeño que suele estar abajo)
            detalles = panel.find_element(By.XPATH, ".//span[contains(text(), 'Ámbito') or contains(text(), 'Fecha')]").text
            
            resultados.append({
                "Normatividad": titulo.strip(),
                "Detalles": detalles.strip(),
                "Url Descarga": driver.current_url
            })
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()
    return resultados
