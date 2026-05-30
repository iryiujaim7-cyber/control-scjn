import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def buscar_normatividades_scjn(termino):
    opciones = Options()
    opciones.add_argument("--headless")
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--window-size=1920,1080")
    opciones.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=opciones)
    resultados = []
    
    try:
        driver.get("https://legislacion.scjn.gob.mx/consulta/home")
        
        # 1. Espera inteligente: no sigas hasta que la caja de búsqueda sea interactiva
        wait = WebDriverWait(driver, 15)
        caja = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[formcontrolname="q"]')))
        
        caja.send_keys(termino)
        caja.send_keys(Keys.ENTER)
        
        # 2. Espera a que los resultados (los paneles de expansión) se carguen
        # Esto es más seguro que un time.sleep fijo
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "mat-expansion-panel")))
        time.sleep(3) 
        
        # 3. Extraemos usando selectores de Angular Material
        paneles = driver.find_elements(By.TAG_NAME, "mat-expansion-panel")
        
        for p in paneles[:5]:
            # Buscamos el título dentro del panel (usando la estructura que vi en tu video)
            titulo = p.find_element(By.CSS_SELECTOR, ".mat-expansion-panel-header-title").text
            
            resultados.append({
                "Normatividad": titulo,
                "Detalles": "Vigente / SCJN", # Placeholder informativo
                "Url Descarga": driver.current_url
            })
            
    except Exception as e:
        print(f"Error en extracción: {e}")
    finally:
        driver.quit()
        
    return resultados
