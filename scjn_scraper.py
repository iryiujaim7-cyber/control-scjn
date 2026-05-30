import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def buscar_normatividades_scjn(termino):
    """
    Scraper optimizado para extraer títulos de normatividades 
    desde el portal de la SCJN utilizando selectores de Angular Material.
    """
    opciones = Options()
    opciones.add_argument("--headless")
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--window-size=1920,1080")
    # Camuflaje como navegador real
    opciones.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=opciones)
    resultados = []
    
    try:
        driver.get("https://legislacion.scjn.gob.mx/consulta/home")
        
        # 1. Esperar a que la caja de búsqueda esté lista
        wait = WebDriverWait(driver, 15)
        caja = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[formcontrolname="q"]')))
        
        # 2. Ejecutar la búsqueda
        caja.send_keys(termino)
        caja.send_keys(Keys.ENTER)
        
        # 3. Esperar a que aparezcan los paneles de resultados
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "mat-expansion-panel")))
        time.sleep(3) # Pausa táctica para asegurar renderizado completo de texto
        
        # 4. Extraer títulos de los paneles de Angular Material
        paneles = driver.find_elements(By.TAG_NAME, "mat-expansion-panel")
        
        for p in paneles[:5]:
            try:
                # Extraer título
                titulo = p.find_element(By.CSS_SELECTOR, ".mat-expansion-panel-header-title").text
                # Intentar extraer detalles (Ámbito/Fecha) si existen
                try:
                    detalles = p.find_element(By.CSS_SELECTOR, ".mat-expansion-panel-header-description").text
                except:
                    detalles = "Vigente / SCJN"
                
                resultados.append({
                    "Normatividad": titulo.strip(),
                    "Detalles": detalles.strip(),
                    "Url Descarga": driver.current_url
                })
            except Exception:
                continue
                
    except Exception as e:
        print(f"Error crítico en el scraper: {e}")
    finally:
        driver.quit()
        
    return resultados
