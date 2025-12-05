import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

if __name__ == '__main__':
    #Opciones de selenium para el scraper (Sin header, sin interfaz, sin notificaciones, pestaña de incognito)
    chrome_options =  webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=chrome_options)
    driver_es = webdriver.Chrome(options=chrome_options)

    #Entramos en el dogv, y hacemos una busqueda avanzada de las fechas que queremos descargar
    driver.get('https://dogv.gva.es/va/inici')
    actions = ActionChains(driver)
    buscador = driver.find_element(By.TAG_NAME, 'iframe')
    driver.switch_to.frame(buscador)
    time.sleep(1)
    busqueda_avanzada = driver.find_element(By.CSS_SELECTOR, 'mat-panel-title[class="mat-expansion-panel-header-title ng-tns-c75-1"]')
    busqueda_avanzada.click()
    time.sleep(1)
    desde = driver.find_element(By.CSS_SELECTOR, 'input[class="datepicker-margin ng-untouched ng-pristine ng-valid"]')
    hasta = driver.find_element(By.CSS_SELECTOR, 'input[class="datepicker-margin onSelect ng-untouched ng-pristine ng-valid"]')
    desde.send_keys('01011990') #Cambiar la fecha de inicio acorde con lo que queramos descargar
    hasta.send_keys('16041990') #Cambiar la fecha de fin acorde con lo que queramos descargar
    time.sleep(1)
    buscar = driver.find_element(By.CSS_SELECTOR, 'button[class="btn btn-primary search-button"]')
    buscar.click()

    #Scrapeamos todas las páginas de boletines oficiales del dogv -> estamos en la página que muestra 10 boletines
    index = 0
    dogv = []
    for i in range(1, 2500):
        datos_documento_dogv = []
        time.sleep(1)
        iframe = driver.page_source
        buscador = driver.find_element(By.TAG_NAME, 'iframe')
        driver.switch_to.frame(buscador)
        time.sleep(1)
        #Aquí pasamos de página
        if i > 1:
            try:
                next = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Next"]')
                time.sleep(2)
                next.click()
                time.sleep(2)
            except:
                driver.refresh()
                time.sleep(2)
                next = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Next"]')
                time.sleep(2)
                next.click()
                time.sleep(2)
        boletines = driver.find_elements(By.CSS_SELECTOR, 'div[class="card bg-white bg-dogv cursor-pointer"]')
        window_buscador = driver.current_window_handle
        #Abrimos cada página de boletín en una pestaña
        for boletin in boletines:
            boletin.click()
            time.sleep(1)
        #Vamos extrayendo su información y vamos cerrando la pestaña
        for boletin in boletines:
            datos_documento_dogv = []
            driver.switch_to.window(driver.window_handles[1])
            iframe = driver.page_source
            buscador = driver.find_element(By.TAG_NAME, 'iframe')
            driver.switch_to.frame(buscador)
            time.sleep(1)
            try:
                error = driver.find_element(By.CSS_SELECTOR, 'div[class="imc--contingut imc-mi--con"]')
                if error:
                    driver.close()
                    continue
            except:
                pass
            wait = WebDriverWait(driver, 60)
            try:
                element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2")))
            except:
                driver.refresh()
                time.sleep(2)
                try:
                    element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2")))
                except:
                    continue
            headline = driver.find_element(By.TAG_NAME, 'h2')
            if headline:
                headline = headline.text.strip()
            datos_documento = driver.find_element(By.TAG_NAME, 'dl')
            metadata_dict = ""
            if datos_documento:
                datos_titulo = datos_documento.find_elements(By.TAG_NAME, 'dt')
                datos_contenido = datos_documento.find_elements(By.TAG_NAME, 'dd')
                for y in range(0, len(datos_contenido)):
                    if datos_contenido[y]:
                        contenido = datos_contenido[y].text.strip()
                    else:
                        contenido = ""
                    datos_documento_dogv.append({datos_titulo[y].text.strip(): contenido})
                metadata_dict = {list(item.keys())[0]: list(item.values())[0] for item in datos_documento_dogv}
            content = driver.find_element(By.CSS_SELECTOR, 'div[class="col-sm-12 col-lg-7 scroll-h-container"]')
            if content:
                content = content.text.strip()
            #Guardamos el contenido en html y txt
            filename = driver.current_url.split("?")[1]
            filename = filename.replace("/", "-")
            #Aqui tenemos la ruta (cread las carpetas o cambiadla a vuestor gusto)
            ruta = os.path.join("dogv", "html", "1996-1990", "va", filename + '.html')
            f = open(os.getcwd() + "\\" + ruta, "w+", encoding='utf-8')
            f.write(driver.page_source)
            ruta = os.path.join("dogv", "plain", "1996-1990", "va", filename + '.txt')
            f = open(os.getcwd() + "\\" + ruta, "w+", encoding='utf-8')
            f.write(content)
            dogv.append(
                {'source': driver.current_url, 'title': headline, 'metadata': metadata_dict, 'language': 'va',
                 'path2html': '/html/1996-1990/va/' + filename + ".html", 'path2txt': '/plain/1996-1990/va/' + filename + ".txt"})
            #Repetimos el mismo proceso pero con la página del boletín en castellano
            driver_es.get(driver.current_url.replace("/va/", "/es/"))
            driver.close()
            datos_documento_dogv = []
            iframe = driver_es.page_source
            buscador = driver_es.find_element(By.TAG_NAME, 'iframe')
            driver_es.switch_to.frame(buscador)
            time.sleep(1)
            wait = WebDriverWait(driver_es, 60)
            try:
                element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2")))
            except:
                driver_es.refresh()
                time.sleep(2)
                element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2")))
                try:
                    element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2")))
                except:
                    continue
            headline = driver_es.find_element(By.TAG_NAME, 'h2')
            if headline:
                headline = headline.text.strip()
            datos_documento = driver_es.find_element(By.TAG_NAME, 'dl')
            metadata_dict = ""
            if datos_documento:
                datos_titulo = datos_documento.find_elements(By.TAG_NAME, 'dt')
                datos_contenido = datos_documento.find_elements(By.TAG_NAME, 'dd')
                for y in range(0, len(datos_contenido)):
                    if datos_contenido[y]:
                        contenido = datos_contenido[y].text.strip()
                    else:
                        contenido = ""
                    datos_documento_dogv.append({datos_titulo[y].text.strip(): contenido})
                metadata_dict = {list(item.keys())[0]: list(item.values())[0] for item in datos_documento_dogv}
            content = driver_es.find_element(By.CSS_SELECTOR, 'div[class="col-sm-12 col-lg-7 scroll-h-container"]')
            if content:
                content = content.text.strip()
            ruta = os.path.join("dogv", "html", "1996-1990", "es", filename + '.html')
            f = open(os.getcwd() + "\\" + ruta, "w+", encoding='utf-8')
            f.write(driver_es.page_source)
            ruta = os.path.join("dogv", "plain", "1996-1990", "es", filename + '.txt')
            f = open(os.getcwd() + "\\" + ruta, "w+", encoding='utf-8')
            f.write(content)
            dogv.append(
                {'source': driver_es.current_url, 'title': headline, 'metadata': metadata_dict, 'language': 'es',
                 'path2html': '/html/1996-1990/es/' + filename + ".html", 'path2txt': '/plain/1996-1990/es/' + filename + ".txt"})
            index += 1
        ruta = os.path.join("dogv", "index-1996-1990-9.json")
        f = open(os.getcwd() + "\\" + ruta, "w+", encoding='utf-8')
        f.write(json.dumps(dogv, indent=4, ensure_ascii=False))
        print("BOLETIN NUMERO: " + str(index) + " DESCARGADA")
        print("ID DE INTERACION: " + str(i))
