<img src="miscellaneous/mcd.png" alt="Logo de la Maestría" width="150"/> 

# Relacion_Baches_Accidentes_HMO 

<img src="miscellaneous/bachometro.svg" alt="Logo del Bachómetro" width="1000"/>

**Análisis Exploratorio de Datos (EDA) sobre la relación entre reportes de baches y accidentes de tránsito en la ciudad de Hermosillo (HMO), Sonora, México.**

Este proyecto explora la correlación espacial y temporal entre la ubicación de baches reportados (fuente **Bachómetro**) y los accidentes de tránsito registrados (**INEGI**), incorporando datos de **clima** de **Open Meteo** y tareas de **geocodificación** mediante **Google Maps API**. El objetivo es identificar patrones y zonas de riesgo para contribuir a una mejor toma de decisiones en la gestión urbana.

---

## Estructura del Proyecto
```
├── LICENSE <- Licencia del proyecto 
├── README.md <- Este archivo, descripción general del proyecto
│
├── data
│ ├── raw <- Datos originales (clima, baches, choques)
│ ├── interim <- Datos intermedios (tras limpieza y extracción)
│ └── processed <- Datos finales listos para análisis
│
├── docs <- Documentación adicional del proyecto
│
├── notebooks <- Jupyter Notebooks con el flujo de trabajo
│ ├── experimentos <- Pruebas preliminares
│ ├── 1.0-extraccion-datos.ipynb <- Descarga de datos desde APIs y archivos
│ ├── 2.0-limpieza-integracion.ipynb <- Limpieza e integración de fuentes
│ ├── 3.0-analisis-exploratorio.ipynb <- Visualizaciones y estadísticas descriptivas
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
│ ├── config.py <- Configuración general (rutas, claves)
│ ├── clean.py <- Transformaciones y limpieza de datos
│ ├── features.py <- Creación de columnas derivadas
│ ├── dataset.py <- Lectura y unión de datasets
│ ├── plots.py <- Funciones para visualizaciones y mapas
│ └── utils.py <- Funciones auxiliares (fechas, coords, etc.)
│
└── baches_vs_accidentes_eda <- Código fuente del proyecto
├── python-version <- Versión de python utilizada en el proyecto
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

## Contacto

¿Comentarios o sugerencias?  
Abre un Issue en el repositorio o contáctanos directamente.
