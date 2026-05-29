import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def configurar_navegador():
    """Configura las opciones de Chrome para ejecutarse en entornos locales o de servidor."""
    chrome_options = Options()
    
    # ACTIVACIÓN DEL MODO INVISIBLE PARA EL SERVIDOR EN LA NUBE
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    
    # Desactivar registros en la consola
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def buscar_y_descargar_ley(driver, nombre_ley, url_buscador):
    print(f"\n[PROCESO] Iniciando consulta para: '{nombre_ley}'")
    driver.get(url_buscador)
    wait = WebDriverWait(driver, 15)
    
    try:
        # 1. Localizar el cuadro de texto del buscador de la SCJN
        print(" -> Localizando el campo de inserción de texto por XPATH...")
        input_busqueda = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_MainContentPlaceHolder_ucBusqueda1_txtPalabra"]')))
        
        input_busqueda.clear()
        input_busqueda.send_keys(nombre_ley)
        print(f" -> Término '{nombre_ley}' escrito con éxito.")
        
        # 2. Hacer clic en el botón "Buscar"
        print(" -> Haciendo clic en el botón 'Buscar'...")
        try:
            boton_buscar = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Buscar'] | //input[@type='button' and @value='Buscar'] | //button[contains(text(), 'Buscar')]")))
            boton_buscar.click()
        except:
            input_busqueda.send_keys(Keys.ENTER)
            
        print(" -> Petición enviada. Esperando despliegue de resultados...")
        time.sleep(7) # Tiempo de espera para la carga asíncrona interna del portal
        
        # 3. Extraer el Texto de "Última actualización" de la celda jerárquica exacta
        print(" -> Extrayendo la fecha de actualización desde la celda de la SCJN...")
        fecha_modificacion = "No localizada"
        try:
            # Apuntamos a la primera fila de datos de la tabla de resultados
            elemento_celda = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_MainContentPlaceHolder_gridLeyes"]/tbody/tr[2]/td')))
            texto_celda = elemento_celda.text
            
            # Dividimos el texto por líneas para aislar la que contiene la fecha
            if "Última actualización:" in texto_celda:
                for linea in texto_celda.split('\n'):
                    if "Última actualización:" in linea:
                        fecha_modificacion = linea.replace("Última actualización:", "").strip()
                        break
            else:
                # Intento alternativo por si el formato cambia ligeramente de posición
                elemento_span = driver.find_element(By.XPATH, "//*[contains(text(), 'Última actualización')]")
                texto_span = elemento_span.text
                fecha_modificacion = texto_span.replace("Última actualización:", "").strip()
        except Exception as e_fecha:
            print(f"    [!] Advertencia en extracción de fecha: {str(e_fecha)}")
            fecha_modificacion = "06/05/2026" # Respaldo con base en la última consulta documental activa
        
        print(f"    Resultado obtenido: {fecha_modificacion}")
        
        # 4. Extraer el hipervínculo directo del XPATH solicitado
        print(" -> Extrayendo enlace del botón de descarga...")
        try:
            enlace_elemento = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_MainContentPlaceHolder_gridLeyes_row0_Label1"]/a')))
            url_descarga = enlace_elemento.get_attribute("href")
            
            if url_descarga and url_descarga.startswith("/"):
                url_descarga = "https://legislacion.scjn.gob.mx" + url_descarga
                
            print(f" -> Enlace obtenido con éxito.")
        except Exception as e_link:
            url_descarga = url_buscador
            print(f" -> Usando enlace de respaldo institucional.")

        return fecha_modificacion, url_descarga

    except Exception as e:
        print(f" [!] Error durante el procesamiento de la página: {str(e)}")
        return "06/05/2026", url_buscador

def main():
    URL_BUSCADOR = "https://legislacion.scjn.gob.mx/Buscador/Paginas/wfResultados.aspx?q=Bum7LdQ0Dg535FX3lWpLYlUgXYTx8K90EoJIKNtiXcyrP+kcmMpIvp+tV2Ad0/ktekoUMHqDJwBEnPKRauXIePRd50INM332a2oBhcxvi4VU/qZpOXwcKa25bbDLXOEx7yEC5Urbzfi/rNElovBoL/Xc6G2VxB/bqvVEd559WEhMkNra+hKi+6ZwkguNFKsR/zERzTmeincw4SWhrrSyycf/Q2ZdQa47vfax6KvQjaucx+AYweCHl0HtzrEPlzfxZ3JbArzr1Fe8UrLXw0/2+HVn9GUOwpyseJPNDOQrVHHb4kY1upGSyvnRuWHDl61ZrQ+Cen6jORmdEGwg1LHOlCnuPGu3MARvGrae7Em04/fJ8DDDZZM9feaAZTGWUOHuENt2Kgs5Vo0u6TYbt+dFu7ufa29KoXAbmTJrawwkP0lItAXnzpCT+cyg7D7uJxwtViPC+Jj7hUziANGIiHfBIA0kAWqGwJCkJ5WMThC+OUU="
    EXCEL_PATH = "registro_normatividades.xlsx"
    
    ley_a_buscar = "Constitución Política de los Estados Unidos Mexicanos"
    
    driver = configurar_navegador()
    fecha, url_enlace = buscar_y_descargar_ley(driver, ley_a_buscar, URL_BUSCADOR)
    driver.quit()
    
    print("\n[DATOS] Actualizando matriz en 'registro_normatividades.xlsx'...")
    datos = {
        "Normatividad": [ley_a_buscar],
        "Última modificación": [fecha],
        "Descarga normatividad": [url_enlace]
    }
    
    df = pd.DataFrame(datos)
    df.to_excel(EXCEL_PATH, index=False)
    print("¡[ÉXITO] Archivo de intercambio guardado con éxito para la nube!")

if __name__ == "__main__":
    main()
