# Dependencias e importaciones necesarias para ejecutar el código.
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Clase de mayor responsabilidad. En su constructor se indican los parámetros que deben estar presentes para su correcto funcionamiento.


class CountryScraper:
    def __init__(self, url, xpath_param, column_names, start_index, data_indices, excel_filename, dato):
        self.url = url
        self.xpath_param = xpath_param
        self.column_names = column_names
        self.start_index = start_index
        self.data_indices = data_indices
        self.excel_filename = excel_filename
        self.dato = dato
# Método scrape_table, encargado del scraping de los datos, de acuerdo a los parametros seleccionados.

    def scrape_table(self):

        driver = webdriver.Chrome()
        driver.get(self.url)

        try:
            # Se añade tiempo de espera para que cargue todo el contenido de la página
            table = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, self.xpath_param))
            )

            # Se crea el dataframe que servirá de encabezado para el archivo de excel generado

            df = pd.DataFrame(columns=self.column_names)

            rows = table.find_elements(By.TAG_NAME, 'tr')
            for row in rows[self.start_index:]:
                cells = row.find_elements(By.TAG_NAME, 'td')
                row_data = [cell.text.strip() for cell in cells]
                # Imprimir los datos de la fila para depuración
                print("Row data:", row_data)

                # Este subproceso inspeccionara el elemento seleccionado, el cual según la configuración contiene un enlace que se usará más tarde en el proceso.
                try:
                    link = cells[self.data_indices[0]].find_element(
                        By.TAG_NAME, 'a').get_attribute('href')
                    print("Enlace:", link)
                    # Por cada iteración se abrirá una segunda venta, con el link obtenido anteriormente del primer elemento
                    driver.execute_script(
                        "window.open('{}', '_blank');".format(link))
                    # Se cambia el enfoque de pantalla al segundo link.
                    driver.switch_to.window(driver.window_handles[-1])
                    # Se espera un momento para asegurar que la nueva página se cargue completamente
                    time.sleep(2)
                    # Se encuentra el elemento h2 que contiene el texto deseado- Según el analisis es el modo más genérico de encontrar el texto requerido de acuerdo al dato.
                    try:
                        span_text = driver.find_element(
                            By.XPATH, f"//h2/span[text()='{self.dato}']")
                       # Se encuentra el elemento p siguiente al h2. Es donde se encuentra el dato a seleccionar.
                        p_element = span_text.find_element(
                            By.XPATH, "./following::p[1]")
                        # Se imprime el texto obtenido. Se puede ver en consola para ver como se ejecuta el programa.
                        print("Texto obtenido:", p_element.text)
                        texto_dato = p_element.text
                    # Manejo de excepción, ya que no todas las páginas de wikipedia contienen la sección solicitada.
                    except:
                        print("No contiene la sección")
                        texto_dato = "Información no disponible."
                        # Se ciera la ventana secundaria
                    driver.close()
                    # Se cambia el enfoque de vuelta a la ventana principal
                    driver.switch_to.window(driver.window_handles[0])
                except Exception as e:
                    print("Error:", e)

                # Se verifica si la longitud de row_data es suficiente para los índices en data_indices. Es una validación para evitar discrepancias
                if len(row_data) >= max(self.data_indices) + 1:
                    row_values = [row_data[i] for i in self.data_indices]
                    # Se agregan dos datos al final, el link y el dato que fue requerido (etimologia o toponimia).
                    row_values.append(link)
                    # Agregar texto_dato a la fila
                    row_values.append(texto_dato)
                    df.loc[len(df)] = row_values
                else:
                    print("La longitud de row_data es insuficiente para los índices en data_indices:", len(
                        row_data))

            # Se aplica una transformación a la columna 'Estado'. Asegura que solo se conserven letras y espacios en la columna Estado.
            df['Estado'] = df['Estado'].apply(lambda x: re.sub(r'\d+', '', x))

            print(df)

            # Se convierte el arreglo obtenido a excel.
            df.to_excel(self.excel_filename, index=False)

        finally:
            if driver.window_handles:
                driver.quit()


# Clase definida en el inciso A con los datos específicos para esa sección de México. Se añade también buscar toponimia y se heredan parametros de la clase CountryScraper.
class MexicoSuperficieScraper(CountryScraper):
    def __init__(self):
        url = 'https://es.wikipedia.org/wiki/Anexo:Entidades_federativas_de_M%C3%A9xico_por_superficie,_poblaci%C3%B3n_y_densidad'
        xpath_param = "//table[.//caption[contains(., 'Entidades federativas de México por superficie, población y densidad')]]"
        column_names = ['Estado', 'Superficie (km²)', 'Poblacion estatal(2020)', 'Densidad(2015)',
                        'Capital', 'Población de Capital(2020)', 'Densidad (hab/km²)', 'Link', 'Información enlace']
        start_index = 3
        data_indices = [3, 4, 6, 7, 8, 9, 10]
        excel_filename = 'mexico_superficie.xlsx'
        dato = "Toponimia"  # Dato específico para México
        super().__init__(url, xpath_param, column_names,
                         start_index, data_indices, excel_filename, dato)

# Clase definida en el inciso B con los datos específicos para esa sección de México. Se añade también buscar toponimia y se heredan parametros de la clase CountryScraper.


class MexicoPoblacionHistoricaScraper(CountryScraper):
    def __init__(self):
        url = 'https://es.wikipedia.org/wiki/Anexo:Entidades_federativas_de_M%C3%A9xico_por_superficie,_poblaci%C3%B3n_y_densidad'
        xpath_param = "//table[@class='wikitable sortable striped jquery-tablesorter'][.//th[contains(text(), 'Población histórica de México')]]"
        column_names = ['Estado', '2020', '2010', '2000', '1990', '1980', '1970',
                        '1960', '1950', '1940', '1930', '1921', '1910', 'Link', 'Información enlace']
        start_index = 1
        data_indices = list(range(1, 14))
        excel_filename = 'mexico_poblacion_historica.xlsx'
        dato = "Toponimia"  # Dato específico para México
        super().__init__(url, xpath_param, column_names,
                         start_index, data_indices, excel_filename, dato)

# Clase definida en el inciso C con los datos específicos para esa sección de México. Se añade también buscar toponimia y se heredan parametros de la clase CountryScraper.


class MexicoProyeccionesPoblacionScraper(CountryScraper):
    def __init__(self):
        url = 'https://es.wikipedia.org/wiki/Anexo:Entidades_federativas_de_M%C3%A9xico_por_superficie,_poblaci%C3%B3n_y_densidad'
        xpath_param = "//a[contains(@href, '/wiki/Consejo_Nacional_de_Poblaci%C3%B3n_(M%C3%A9xico)')]/following::table[contains(@class, 'wikitable')][2]"
        column_names = ['Estado', '2010', '2015', '2020',
                        '2025', '2030', 'Link', 'Información enlace']
        start_index = 1
        data_indices = list(range(1, 7))
        excel_filename = 'mexico_poblacion_proyecciones.xlsx'
        dato = "Toponimia"  # Dato específico para México
        super().__init__(url, xpath_param, column_names,
                         start_index, data_indices, excel_filename, dato)

# Clase definida en el inciso C con los datos específicos para esa sección de México. Se añade también buscar toponimia y se heredan parametros de la clase CountryScraper.


class USAStatesScraper(CountryScraper):
    def __init__(self):
        url = 'https://es.wikipedia.org/wiki/Estado_de_los_Estados_Unidos'
        xpath_param = "//table[@class='wikitable sortable jquery-tablesorter']"
        column_names = ['Estado', 'Link', 'Información enlace']
        start_index = 1
        data_indices = [1]
        excel_filename = 'usa-states.xlsx'
        dato = "Etimología"  # Dato específico para Estados Unidos
        super().__init__(url, xpath_param, column_names,
                         start_index, data_indices, excel_filename, dato)


# Ejecución de scrapers para México
mexico_superficie_scraper = MexicoSuperficieScraper()
mexico_superficie_scraper.scrape_table()

mexico_poblacion_historica_scraper = MexicoPoblacionHistoricaScraper()
mexico_poblacion_historica_scraper.scrape_table()

mexico_proyecciones_poblacion_scraper = MexicoProyeccionesPoblacionScraper()
mexico_proyecciones_poblacion_scraper.scrape_table()

# Ejecución de scraper para Estados Unidos
usa_states_scraper = USAStatesScraper()
usa_states_scraper.scrape_table()
