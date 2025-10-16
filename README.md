<img src="miscellaneous/mcd.png" alt="Logo de la Maestría" width="150"/> 

# Relacion Baches Accidentes HMO 

<img src="miscellaneous/bachometro.svg" alt="Logo del Bachómetro" width="1000"/>

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

**Análisis Exploratorio de Datos (EDA) sobre la relación entre reportes de baches y accidentes de tránsito en la ciudad de Hermosillo (HMO), Sonora, México.**

Este proyecto explora la correlación espacial y temporal entre la ubicación de baches reportados (fuente **Bachómetro**) y los accidentes de tránsito registrados (**INEGI**), incorporando datos de **clima** de **Open Meteo**. El objetivo es identificar patrones y zonas de riesgo para contribuir a una mejor toma de decisiones en la gestión urbana.

---

## Alcance del Proyecto y Pregunta Central

Este análisis se centra en la problemática de la infraestructura vial de Hermosillo y su impacto directo en la seguridad.

### Pregunta Guía del Análisis

> **¿Cuál es el impacto que tienen los baches en Hermosillo sobre la frecuencia y gravedad de los accidentes viales, y en qué colonias o tramos son más peligrosos?**

### Tipos de Datos Involucrados

El proyecto integra diversas estructuras de datos que permiten un análisis espacio-temporal robusto:

| Tipo de Dato | Fuentes de Origen | Descripción |
| :--- | :--- | :--- |
| **Series de Tiempo** | Clima (Open Meteo), Reportes de Baches, Accidentes (INEGI) | **Análisis Temporal:** Registros con marca de tiempo utilizados para identificar tendencias, estacionalidad, y correlaciones a lo largo del tiempo (mensual/anual). |
| **Georreferenciada** | Bachómetro, INEGI | **Análisis Espacial:** Coordenadas geográficas (lat/lon) y ubicación por colonia/tramo, esencial para generar mapas de calor y calcular la densidad de eventos. |
| **Cuantitativos** | Reportes, Accidentes, Clima | **Métricas:** Conteo de baches/accidentes, velocidades del viento, fatalidades y daños materiales. |
| **Cualitativos** | INEGI | **Categorización:** Tipo de accidente (colisión, atropellamiento), causa del accidente, y percepciones de riesgo (futuro). |

---

## Público Objetivo y Fuentes Primarias

### Destinatarios del Producto Final (Tablero)

El producto de datos final (el tablero o `informe.pdf`) está destinado a orientar la toma de decisiones y a informar a la ciudadanía. Los principales públicos son:

1.  **Gobierno Municipal / Cidue:** Para priorizar la inversión en bacheo hacia los tramos de mayor riesgo.
2.  **Ciudadanía de Hermosillo:** Para conocer el peligro real en sus rutas diarias.
3.  **Organizaciones Civiles de Movilidad:** Para apoyo en políticas públicas y supervisión ciudadana.

### Fuentes de Datos Utilizadas

* **Bachómetro (Ayuntamiento de Hermosillo):** Reportes ciudadanos y ubicación geográfica de baches.
* **INEGI (Estadísticas de Accidentes):** Datos históricos de accidentes de tránsito terrestre en zonas urbanas.
* **Open Meteo API:** Datos climáticos horarios (temperatura, precipitación) para análisis estacionales.

---

## Estructura del Proyecto
```


├── LICENSE <- Licencia del proyecto
├── README.md <- Este archivo, descripción general del proyecto
│
├── miscellaneous <- Fotos utilizadas para decorar repositorio 
├── data
│ ├── raw <- Datos originales (clima, baches, choques)
│ ├── interim <- Datos intermedios (tras limpieza y extracción)
│ └── processed <- Datos finales listos para análisis
│
├── docs <- Documentación adicional del proyecto
│
├── notebooks <- Jupyter Notebooks con el flujo de trabajo
│ ├── experimentos <- Pruebas preliminares
│ ├── 1.1-limpieza-integracion_clima <- Limpieza e integración de datos del clima
│ ├── 1.2-limpieza-integracion_bachometro.ipynb <- Limpieza e integración de datos del bachometro
│ ├── 1.3-limpieza-integracion_ATUS.ipynb <- Limpieza e integración de datos del ATUS
│ ├── 2.0-analisis-exploratorio.ipynb <- Visualizaciones y estadísticas descriptivas
│ └── 4.0-reporte-final.ipynb <- Resultados y conclusiones
│
├── references <- Diccionarios de datos y referencias de APIs
│
├── reports
│ ├── figures <- Mapas y gráficas generadas
│ └── informe.pdf <- Reporte final del análisis
│
├── requirements.txt <- Dependencias del proyecto
│
└── src <- Scripts de automatización
│ ├── __init__.py <- Define el directorio como paquete de Python.
│ ├── clean_atus.py <- Script para la limpieza de datos de choques (ATUS).
│ ├── cleaning_data_bachometro.py <- Script para la limpieza de datos del bachómetro.
│ ├── config.py <- Configuración general (rutas, claves)
│ ├── download_atus.py <- Funciones para descargar datos de choques (ATUS).
│ ├── download_clima.py <- Funciones para descargar datos del clima.
│ ├── download_colonias.py <- Funciones para descargar datos de colonias.
│ ├── extract_bachometro.py <- Extracción y procesamiento del bachómetro.
│ ├── extract_colonias.py <- Extracción y procesamiento de datos de colonias.
│ ├── extract_vialidades.py <- Extracción y procesamiento de datos de vialidades.
│ └── utils.py <- Funciones auxiliares
│
└── baches_vs_accidentes_eda <- Código fuente del proyecto
├── python-version <- Versión de python utilizada en el proyecto
├── requirements.txt <- Librerias utilizadas en el proyecto
├── run_extraction.sh <- Comando de consola para descargar datos
└── pyproject.toml <- Librerias a utilizar e el proyecto
```

## Flujo de Trabajo

El análisis se desarrolla mediante Jupyter Notebooks, siguiendo este orden:

1. **`1.0-extraccion-datos.ipynb`**
   - Descarga y organización de los datos crudos desde:
     - Bachómetro (reportes de baches)
     - INEGI (accidentes de tránsito)
     - Open Meteo (datos climáticos)

2. **`2.0-limpieza-integracion.ipynb`**
   - Limpieza de los datasets y unión por coordenadas/fechas.

3. **`3.0-analisis-exploratorio.ipynb`**
   - Análisis exploratorio: series de tiempo, mapas de calor, correlaciones.

4. **`4.0-api-googlemaps.ipynb`**
   - Uso de Google Maps API para enriquecer los datos con información geográfica adicional.

5. **`5.0-reporte-final.ipynb`**
   - Visualizaciones finales, hallazgos clave y generación del informe (informe.pdf).

---

## Resultados

Los productos del análisis se encuentran en la carpeta `reports/`:

- **`informe.pdf`**: Documento final con conclusiones.
- **`figures/`**: Visualizaciones generadas (mapas, gráficas, tablas).

---

## Instalación y Configuración (Get Started)

Para comenzar a trabajar en este proyecto, sigue estos pasos para configurar tu entorno virtual (`.venv`) y las dependencias:

1.  **Clonar el Repositorio:**
    ```bash
    git clone [https://docs.github.com/es/repositories/creating-and-managing-repositories/quickstart-for-repositories](https://docs.github.com/es/repositories/creating-and-managing-repositories/quickstart-for-repositories)
    cd Relacion_Baches_Accidentes_HMO
    ```

2.  **Verificar Versión de Python:**
    La versión requerida para este proyecto es **Python 3.11** o superior.
    ```bash
    python3 --version
    ```

3.  **Crear y Activar el Entorno Virtual:**
    ```bash
    # Crea el entorno (.venv)
    python3.11 -m venv .venv 

    # Activa el entorno (Mac/Linux)
    source .venv/bin/activate
    ```

4.  **Instalar Dependencias:**
    Con el entorno activado, instala todas las librerías necesarias:
    ```bash
    pip install -r requirements.txt
    ```
    
5.  **Configurar VS Code:**
    Dentro de VS Code, usa **Cmd+Shift+P** y selecciona **Python: Select Interpreter** para elegir la ruta `./.venv/bin/python`.

---

---

## Descarga y Extracción de Datos 

Una vez que el entorno virtual (`.venv`) esté activado e instalado, puedes ejecutar el script de extracción para descargar los datos de las fuentes originales y procesarlos en el directorio `data/raw`.

### Ejecutar el Script de Extracción:

1.  Asegúrate de estar en el directorio raíz del proyecto (`Relacion_Baches_Accidentes_HMO`) y que tu entorno virtual esté **activo**.

2.  Corre el siguiente comando en tu terminal:

    ```bash
    ./run_extraction.sh
    ```

    **Nota:** Este comando ejecutará una serie de scripts de Python para obtener datos de fuentes externas (ATUS, Clima, etc.) y guardarlos localmente.

## Contacto

¿Comentarios o sugerencias?  
Abre un Issue en el repositorio o contáctanos directamente.
