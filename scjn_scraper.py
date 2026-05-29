import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def configurar_navegador():
    """Configura Chrome en modo headless para la nube de Streamlit o GitHub Actions."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def buscar_normatividades_scjn(termino_busqueda):
    """
    Navega a la SCJN, busca el término y extrae los resultados de la primera página.
    Devuelve una lista de diccionarios con la información de cada ley encontrada.
    """
    URL_BASE = "https://legislacion.scjn.gob.mx/Buscador/Paginas/wfResultados.aspx?q=Bum7LdQ0Dg535FX3lWpLYlUgXYTx8K90EoJIKNtiXcyrP+kcmMpIvp+tV2Ad0/ktekoUMHqDJwBEnPKRauXIePRd50INM332a2oBhcxvi4VU/qZpOXwcKa25bbDLXOEx7yEC5Urbzfi/rNElovBoL/Xc6G2VxB/bqvVEd559WEhMkNra+hKi+6ZwkguNFKsR/zERzTmeincw4SWhrrSyycf/Q2ZdQa47vfax6KvQjaucx+AYweCHl0HtzrEPlzfxZ3JbArzr1Fe8UrLXw0/2+HVn9GUOwpyseJPNDOQrVHHb4kY1upGSyvnRuWHDl61ZrQ+Cen6jORmdEGwg1LHOlCnuPGu3MARvGrae7Em04/fJ8DDDZZM9feaAZTGWUOHuENt2Kgs5Vo0u6TYbt+dFu7ufa29KoXAbmTJrawwkP0lItAXnzpCT+cyg7D7uJxwtViPC+Jj7hUziANGIiHfBIA0kAWqGwJCkJ5WMThC+OUU="
    
    print(f"[SCRAPER] Buscando en la SCJN el término: '{termino_busqueda}'")
    driver = configurar_navegador()
    wait = WebDriverWait(driver, 12)
    resultados = []
    
    try:
        driver.get(URL_BASE)
        
        # 1. Localizar e interactuar con el cuadro de búsqueda
        input_busqueda = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_MainContentPlaceHolder_ucBusqueda1_txtPalabra"]')))
        input_busqueda.clear()
        input_busqueda.send_keys(termino_busqueda)
        
        # 2. Ejecutar la búsqueda
        try:
            boton_buscar = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Buscar'] | //input[@type='button' and @value='Buscar']")))
            boton_buscar.click()
        except:
            input_busqueda.send_keys(Keys.ENTER)
            
        print(" -> Búsqueda enviada. Esperando carga de la tabla...")
        time.sleep(6) # Tiempo para renderizado del grid de la SCJN
        
        # 3. Localizar las filas de la tabla de resultados
        # La SCJN usa id compuesto como ctl00_MainContentPlaceHolder_gridLeyes
        tabla_resultados = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_MainContentPlaceHolder_gridLeyes"]')))
        filas = tabla_resultados.find_elements(By.XPATH, "./tbody/tr")
        
        # Omitimos la primera fila (encabezado) y recorremos las de datos (normalmente tr con datos de leyes)
        # Cada celda de datos de ley está en un 'td'. El formato suele traer pares tr de datos.
        indice_real = 0
        for i in range(1, len(filas)):
            fila_texto = filas[i].text.strip()
            
            # Verificamos si la fila contiene datos reales de un ordenamiento
            if fila_texto and ("Vigencia:" in fila_texto or "Ámbito:" in fila_texto):
                try:
                    # Extraer Fecha de última actualización de la celda
                    fecha_modificacion = "No localizada"
                    for linea in fila_texto.split('\n'):
                        if "Última actualización:" in linea:
                            fecha_modificacion = linea.replace("Última actualización:", "").strip()
                            break
                    
                    # El nombre de la norma suele ser el primer texto o un enlace fuerte en la celda
                    # Intentamos extraer el texto del título exacto del ordenamiento
                    elemento_titulo = filas[i].find_element(By.XPATH, f'.//span[contains(@id, "lblLey")] | .//a[contains(@style, "bold") or contains(@id, "Ley")]')
                    nombre_norma = elemento_titulo.text.strip()
                    
                    if not nombre_norma:
                        # Respaldo de extracción de título si el span cambia de ID
                        nombre_norma = fila_texto.split('\n')[0].strip()
                except:
                    continue
                
                # Extraer el enlace de descarga correspondiente a la fila actual
                try:
                    enlace_elemento = filas[i].find_element(By.XPATH, f'//*[@id="ctl00_MainContentPlaceHolder_gridLeyes_row{indice_real}_Label1"]/a')
                    url_descarga = enlace_elemento.get_attribute("href")
                    if url_descarga and url_descarga.startswith("/"):
                        url_descarga = "https://legislacion.scjn.gob.mx" + url_descarga
                except:
                    url_descarga = URL_BASE # Respaldo si no se mapea el row id secuencial
                
                resultados.append({
                    "Normatividad": nombre_norma,
                    "Última actualización": fecha_modificacion,
                    "Url Descarga": url_descarga
                })
                indice_real += 1
                
                # Limitamos a los primeros 5 resultados más relevantes para mantener fluida la interfaz
                if len(resultados) >= 5:
                    break

    except Exception as e:
        print(f"[!] Error en el raspado dinámico: {str(e)}")
        
    finally:
        driver.quit()
        print(f"[SCRAPER] Proceso terminado. Registros encontrados: {len(resultados)}")
        
    return resultados
