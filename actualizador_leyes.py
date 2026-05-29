import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURACIÓN DE RUTAS ---
EXCEL_PATH = "registro_normatividades.xlsx"
DOWNLOAD_DIR = os.path.abspath("./descargas_leyes")

# Crear la carpeta de descargas si no existe
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Lista modificada: Solo incluye la Constitución
LEYES_A_BUSCAR = [
    "Constitución Política de los Estados Unidos Mexicanos"
]

def configurar_navegador():
    print("[DEBUG] 1. Configurando opciones de Chrome...")
    chrome_options = Options()
    
    # Preferencias para descargar PDFs automáticamente sin abrir ventanas de diálogo
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True 
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Parámetros para evitar bloqueos en entornos de automatización
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    
    print("[DEBUG] 2. Lanzando instancia de Chrome...")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("[DEBUG] 3. Navegador abierto con éxito.")
        return driver
    except Exception as e:
        print(f"[ERROR CRÍTICO] No se pudo iniciar Chrome: {e}")
        return None

def buscar_y_descargar_ley(driver, nombre_ley, url_buscador):
    print(f"\n[PROCESO] Iniciando consulta para: '{nombre_ley}'")
    driver.get(url_buscador)
    wait = WebDriverWait(driver, 15)
    
    try:
        # 1. Localizar el cuadro de texto usando el XPATH exacto que obtuviste
        print(" -> Localizando el campo de inserción de texto por XPATH...")
        input_busqueda = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_MainContentPlaceHolder_ucBusqueda1_txtPalabra"]')))
        
        input_busqueda.clear()
        input_busqueda.send_keys(nombre_ley)
        print(f" -> Término '{nombre_ley}' escrito con éxito.")
        
        # 2. Hacer clic en el botón "Buscar" de la página
        print(" -> Haciendo clic en el botón 'Buscar'...")
        try:
            boton_buscar = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Buscar'] | //input[@type='button' and @value='Buscar'] | //button[contains(text(), 'Buscar')]")))
            boton_buscar.click()
        except:
            input_busqueda.send_keys(Keys.ENTER)
            
        print(" -> Petición enviada. Esperando despliegue de resultados...")
        time.sleep(6) # Tiempo de espera para carga interna de la SCJN
        
        # 3. Extraer la Fecha de Última Modificación
        print(" -> Extrayendo fecha de actualización del resultado...")
        try:
            elemento_fecha = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'actualiz') or contains(text(), 'Modific') or contains(text(), 'Reform')]")))
            fecha_modificacion = elemento_fecha.text.strip()
        except:
            fecha_modificacion = "No localizada en los resultados actuales"
        
        print(f"    Resultado: {fecha_modificacion}")
        
        # 4. Intentar presionar 'Texto completo' para descargar el archivo
        print(" -> Localizando enlace de descarga ('Texto completo')...")
        try:
            archivos_antes = os.listdir(DOWNLOAD_DIR)
            boton_descarga = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Texto completo') or contains(text(), 'PDF')]")))
            boton_descarga.click()
            
            # Monitorear activamente que el archivo se descargue por completo
            timeout = 20
            segundos = 0
            nuevo_archivo = None
            while segundos < timeout:
                time.sleep(1)
                archivos_ahora = os.listdir(DOWNLOAD_DIR)
                nuevos = [f for f in archivos_ahora if f not in archivos_antes and not f.endswith('.crdownload')]
                if nuevos:
                    nuevo_archivo = nuevos[0]
                    break
                segundos += 1
                
            if nuevo_archivo:
                extension = os.path.splitext(nuevo_archivo)[1]
                nombre_final = f"{nombre_ley}{extension}"
                
                ruta_origen = os.path.join(DOWNLOAD_DIR, nuevo_archivo)
                ruta_destino = os.path.join(DOWNLOAD_DIR, nombre_final)
                
                if os.path.exists(ruta_destino):
                    os.remove(ruta_destino) 
                    
                os.rename(ruta_origen, ruta_destino)
                status_descarga = f"Descargado como {nombre_final}"
                print(f" -> ¡Éxito! Archivo renombrado y guardado.")
            else:
                status_descarga = "Descarga demorada (verificar carpeta)"
                print(" -> La descarga tardó más de lo esperado en completarse.")
        except Exception as e_descarga:
            status_descarga = "Botón de descarga no disponible tras la búsqueda"
            print(f" -> Aviso: No se localizó el enlace 'Texto completo' ({e_descarga})")

        return fecha_modificacion, status_descarga

    except Exception as e:
        print(f" [!] Error durante el procesamiento de la página: {str(e)}")
        return "Error en consulta", "No descargado"

def main():
    print("[DEBUG] Iniciando Ejecución del Script...")
    URL_SCJN = "https://legislacion.scjn.gob.mx/Buscador/Paginas/Buscar.aspx?q=rZIYFqANts7YJ0s7drjCRQ=="
    
    driver = configurar_navegador()
    if not driver:
        print("[ERROR] No se pudo inicializar la infraestructura del navegador. Proceso abortado.")
        return
        
    resultados = []
    for ley in LEYES_A_BUSCAR:
        fecha, status = buscar_y_descargar_ley(driver, ley, URL_SCJN)
        resultados.append({
            "Normatividad": ley,
            "Última modificación": fecha,
            "Descarga normatividad": status
        })
    
    print("\n[DEBUG] Cerrando el navegador...")
    driver.quit()

    # Guardar o actualizar la tabla final de Excel
    df_nuevos = pd.DataFrame(resultados)
    df_nuevos.to_excel(EXCEL_PATH, index=False)
    print(f"\n[PROCESO TERMINADO] Archivo de registro '{EXCEL_PATH}' generado/actualizado correctamente.")

if __name__ == "__main__":
    main()
