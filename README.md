# 📄 Scraper DOGV (Diari Oficial de la Generalitat Valenciana)

Este proyecto es un **scraper automatizado con Selenium** que permite descargar boletines oficiales del **DOGV** en los idiomas *valenciano* y *castellano*, guardar su contenido en texto y HTML y generar un índice JSON con los metadatos recopilados.

El script realiza automáticamente una búsqueda avanzada en la web del DOGV dentro de un rango de fechas, recorre miles de resultados, abre cada boletín en una nueva pestaña, extrae la información estructurada y genera los archivos correspondientes.


## 🚀 Características principales

- Uso de **Selenium en modo headless** para automatizar la navegación.
- Búsqueda avanzada automática en el portal oficial del DOGV.
- Scraping de:
  - Título del boletín.
  - Metadata del documento (mediante `<dl>`, `<dt>`, `<dd>`).
  - Contenido textual principal.
- Descarga del boletín tanto en **valenciano (`va`)** como en **castellano (`es`)**.
- Guardado de:
  - Documento completo en **HTML**.
  - Contenido limpio en **TXT**.
  - Índice global en **JSON**.
- Control robusto mediante:
  - `WebDriverWait`
  - Manejo de iframes
  - Reintentos en caso de error de carga.


## 📁 Estructura de archivos generados

El script se ejecuta en base a la siguiente estructura:

```
dogv/
│
├── html/
│ └── <fechas>/
│ ├── va/
│ │ └── <ID>.html
│ └── es/
│ └── <ID>.html
│
├── plain/
│ └── <fechas>/
│ ├── va/
│ │ └── <ID>.txt
│ └── es/
│ └── <ID>.txt
│
└── index-<fechas>.json
```

Las carpetas `<fechas>` hacen referencia a la fecha que estamos descargando. Cada archivo `<ID>` corresponde al identificador obtenido desde la URL del boletín.

## 🧰 Requisitos

### 📦 Dependencias de Python

- `selenium`
- `json`
- `time`
- `os`

### 🖥️ Requisitos del sistema

- Chrome instalado.
- ChromeDriver compatible con tu versión de Chrome.
- Sistema operativo Windows/Linux/macOS.

## ▶️ Ejecución del script

Ejecuta:

```
python scraper_dogv.py
```

El flujo principal de ejecución:

1. Inicializa dos instancias de Chrome en modo headless (una para va y otra para es).
2. Accede al portal del DOGV y abre la búsqueda avanzada dentro del iframe.
3. Inserta el rango de fechas configurado en el script.
4. Itera por las páginas de resultados (hasta el límite fijado en el bucle).
5. Para cada boletín:
    - Abre la tarjeta en una nueva pestaña.
    - Extrae título, metadatos (`<dl>`) y contenido.
    - Guarda HTML y TXT en las carpetas correspondientes.
    - Registra la entrada en el índice JSON.
6. Repite el proceso con la versión en castellano (`/es/`).

## 🧠 Funcionamiento interno
### Inicialización del navegador

- Se crean chrome_options con argumentos:
    - `--headless`
    - `--no-sandbox`
    - `--disable-notifications`
    - `--incognito`
    - `--window-size=1920,1080`
- Se desactivan indicadores de automatización mediante:
    - `excludeSwitches: ["enable-automation"]`
    - `useAutomationExtension: False`
- Se inicializan dos `webdriver.Chrome(options=chrome_options)` (uno para cada idioma).

### Navegación y manejo de iframes

- El portal del DOGV carga el buscador dentro de un `iframe`: el script siempre hace `switch_to.frame(...)` antes de interactuar.
- Se usan `time.sleep()` y `WebDriverWait` para sincronizar.
- Para avanzar páginas en los resultados se utiliza el selector `a[aria-label="Next"]` con reintentos si falla.

### Extracción de datos

- **Título**: se busca el primer `<h2>` visible.
- **Metadatos**: se extraen desde la lista de definición (`<dl>`) emparejando `<dt>` y `<dd>`.
- **Contenido**: toma el texto del contenedor `div.col-sm-12.col-lg-7.scroll-h-container`.
- **Guardado**:
    - HTML: se guarda `driver.page_source en dogv/html/<fechas>/<lang>/<ID>.html`.
    - Texto: se guarda el `content` en `dogv/plain/<fechas>/<lang>/<ID>.txt`.
- **Índice JSON**: se va añadiendo un diccionario por documento y se escribe en `dogv/index-<fechas>.json`.

### 4. Generación del índice JSON

Cada boletín se añade como un objeto:

```
{
  "source": "https://dogv.gva.es/...",
  "title": "Título",
  "metadata": { ... },
  "language": <lang>,
  "path2html": "/html/<fechas>/<lang>/<ID>.html",
  "path2txt": "/plain/<fechas>/<lang>/<ID>.txt"
}
```

## Funding

This resource is funded by the *Ministerio para la Transformación Digital y de la Función Pública* — Funded by **EU – NextGenerationEU**, within the framework of the project *Desarrollo de Modelos ALIA*.

## Acknowledgments

We extend our gratitude to all individuals and institutions that contributed to the development of this resource.

Special thanks to:

- [Data providers]  
- [Technological support providers]

We also acknowledge the financial, scientific, and technical contributions of the *Ministerio para la Transformación Digital y de la Función Pública – Funded by EU – NextGenerationEU* within the framework of the *Desarrollo de Modelos ALIA* project.

## Reference

Please cite this dataset using the following BibTeX entry:

```bibtex
@misc{uji_parallel_va_en_2025,
  author       = {Espinosa Zaragoza, Sergio and Sep{\'u}lveda Torres, Robiert and Mu{\~n}oz Guillena, Rafael and Consuegra-Ayala, Juan Pablo}, <-- ACTUALIZAR
  title        = {ALIA_DOGV Scraper},
  year         = {2025},
  institution  = {Language and Information Systems Group (GPLSI) and Centro de Inteligencia Digital (CENID), University of Alicante (UA)},
  howpublished = {\url{https://huggingface.co/datasets/gplsi/uji_parallel_va_es}} <-- ACTUALIZAR
}
```

## Disclaimer

This resource may contain biases or unintended artifacts.
Any third party using or deploying systems based on this resource is solely responsible for ensuring compliant, safe, and ethical use, including adherence to relevant AI and data protection regulations.

The University of Alicante, as creator and owner of the resource, assumes no liability for outcomes resulting from third-party use.

## License

[Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0)

