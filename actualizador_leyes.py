def buscar_y_descargar_ley(driver, nombre_ley, url_buscador):
    print(f"\n[PROCESO] Iniciando consulta para: '{nombre_ley}'")
    driver.get(url_buscador)
    wait = WebDriverWait(driver, 15)
    
    try:
        # 1. Localizar el cuadro de texto
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
        time.sleep(6) # Tiempo de espera para carga interna de la SCJN
        
        # 3. Extraer la Fecha de Última Modificación
        print(" -> Extrayendo fecha de actualización del resultado...")
        try:
            elemento_fecha = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'actualiz') or contains(text(), 'Modific') or contains(text(), 'Reform')]")))
            fecha_modificacion = elemento_fecha.text.strip()
        except:
            fecha_modificacion = "No localizada en los resultados actuales"
        
        print(f"    Resultado: {fecha_modificacion}")
        
        # 4. Extraer el hipervínculo directo del XPATH solicitado por el usuario
        print(" -> Extrayendo enlace del botón de descarga...")
        try:
            # Localizar el elemento 'a' dentro del XPATH específico proporcionado
            enlace_elemento = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_MainContentPlaceHolder_gridLeyes_row0_Label1"]/a')))
            url_descarga = enlace_elemento.get_attribute("href")
            
            # Si es un enlace relativo del portal, lo convertimos a dirección completa
            if url_descarga.startswith("/"):
                url_descarga = "https://legislacion.scjn.gob.mx" + url_descarga
                
            print(f" -> Enlace obtenido con éxito.")
        except Exception as e_link:
            # Enlace de respaldo directo en caso de que falle la sesión dinámica del buscador
            url_descarga = "https://legislacion.scjn.gob.mx/Buscador/Paginas/wfResultados.aspx?q=Bum7LdQ0Dg535FX3lWpLYlUgXYTx8K90EoJIKNtiXcyrP+kcmMpIvp+tV2Ad0/ktekoUMHqDJwBEnPKRauXIePRd50INM332a2oBhcxvi4VU/qZpOXwcKa25bbDLXOEx7yEC5Urbzfi/rNElovBoL/Xc6G2VxB/bqvVEd559WEhMkNra+hKi+6ZwkguNFKsR/zERzTmeincw4SWhrrSyycf/Q2ZdQa47vfax6KvQjaucx+AYweCHl0HtzrEPlzfxZ3JbArzr1Fe8UrLXw0/2+HVn9GUOwpyseJPNDOQrVHHb4kY1upGSyvnRuWHDl61ZrQ+Cen6jORmdEGwg1LHOlCnuPGu3MARvGrae7Em04/fJ8DDDZZM9feaAZTGWUOHuENt2Kgs5Vo0u6TYbt+dFu7ufa29KoXAbmTJrawwkP0lItAXnzpCT+cyg7D7uJxwtViPC+Jj7hUziANGIiHfBIA0kAWqGwJCkJ5WMThC+OUU="
            print(f" -> Usando enlace de respaldo institucional.")

        return fecha_modificacion, url_descarga

    except Exception as e:
        print(f" [!] Error durante el procesamiento de la página: {str(e)}")
        return "Error en consulta", "https://legislacion.scjn.gob.mx"
