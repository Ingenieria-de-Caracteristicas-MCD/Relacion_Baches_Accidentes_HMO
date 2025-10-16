"""
download_clima.py

Descarga los archivos del clima de Hermosillo desde el API de Open-Meteo.

Uso:
    python download_clima.py

Descarga los archivos correspondientes a los años 2021–2023 en un solo archivo
.CSV y los guarda en data/raw/clima. El archivo .txt se guarda directamente en la carpeta data/.
"""

import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from datetime import datetime
from pathlib import Path

# ******************************************************************
# Importar Rutas y Logger desde el archivo de configuración (config.py)
# NOTA: Solo importamos variables que sabemos que existen en el config.py de tu compañero.
from config import RAW_DIR, DATA_DIR, get_logger, init_paths 
# ******************************************************************

# Inicializar el logger para este script
logger = get_logger(__name__)

# --- 1. CONFIGURACIÓN DEL PROYECTO Y LA API ---

# Definición de parámetros para la documentación y la API
START_DATE = "2021-01-01"
END_DATE = "2023-12-31"
LATITUDE = 29.1026
LONGITUDE = -110.9773
CITY_NAME = "Hermosillo"
DATA_SOURCE_1 = "Open-Meteo Archive API (Clima)"
DATA_URL_1 = "https://open-meteo.com/en/docs/archive-api"

# Rutas de guardado usando las variables importadas
RAW_DATA_PATH = RAW_DIR / "clima_hermosillo.csv"

# ***************************************************************
# Se usa DATA_DIR (que apunta a 'data/raw') para el archivo .txt
RAW_METADATA_PATH = RAW_DIR / "info_descargas_clima.txt"
# ***************************************************************


# Setup del cliente de Open-Meteo con cache y retry
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "start_date": START_DATE,
    "end_date": END_DATE,
    "hourly": ["temperature_2m", "precipitation", "weather_code", "is_day", "relative_humidity_2m", "cloud_cover", "wind_speed_10m"],
}

# --- 2. DESCARGA Y PROCESAMIENTO ---

def download_and_process_data():
    """Descarga los datos de Open-Meteo y los convierte en DataFrame."""
    logger.info(f"Conectando a {DATA_SOURCE_1}...")
    try:
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        
        # Proceso de datos por hora
        hourly = response.Hourly()
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq = pd.Timedelta(seconds = hourly.Interval()),
                inclusive = "left"
            )
        }
        
        # Asignación de variables al DataFrame
        variable_names = ["temperature_2m", "precipitation", "weather_code", "is_day", "relative_humidity_2m", "cloud_cover", "wind_speed_10m"]
        
        for i, name in enumerate(variable_names):
            hourly_data[name] = hourly.Variables(i).ValuesAsNumpy()
            
        logger.info(f"Descargados {len(hourly_data['date'])} registros de clima.")
        return pd.DataFrame(data=hourly_data)

    except Exception as e:
        logger.error(f"Error al descargar o procesar los datos de Open-Meteo: {e}")
        return None

# --- 3. FUNCIONES DE GUARDADO Y DOCUMENTACIÓN ---

def save_csv(df, path: Path):
    """Guarda el DataFrame en la ruta especificada."""
    df.to_csv(path, index=False)
    logger.info(f"Datos guardados exitosamente en: {path}")

def generate_documentation():
    """Genera el archivo de texto con la descripción de la fuente."""
    
    doc_content = f"""
# ===============================================
# DESCRIPCIÓN DE FUENTES DE DATOS - CLIMA HMO
# ===============================================
    
## Fuente 1: Datos Meteorológicos Históricos
- **Nombre de la Fuente:** {DATA_SOURCE_1}
- **Enlace:** {DATA_URL_1}
- **Fecha de Descarga:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Ubicación:** {CITY_NAME} (Lat: {LATITUDE}, Lon: {LONGITUDE})
- **Rango de Fechas de los Datos:** {START_DATE} a {END_DATE}
- **Descripción de los Datos (Naturaleza):**
    Datos de reanálisis histórico del clima, a nivel horario. Proporcionan mediciones detalladas a nivel superficial.
    
- **Variables Descargadas:**
    - **temperature_2m:** Temperatura del aire a 2 metros (°C).
    - **precipitation:** Precipitación total (mm).
    - **weather_code (WMO):** Código que describe las condiciones del clima.
    - **is_day:** Indicador de día o noche.
    - **relative_humidity_2m:** Humedad relativa a 2 metros (%).
    - **cloud_cover:** Porcentaje de cobertura de nubes (%).
    - **wind_speed_10m:** Velocidad del viento a 10 metros (km/h).
    - **Frecuencia Temporal:** Horaria
    - **Formato de los Datos:** CSV
"""

    with open(RAW_METADATA_PATH , "w") as f:
        f.write(doc_content)
    logger.info(f"Documentación de fuentes generada en: {RAW_METADATA_PATH }")


# --- 4. EJECUCIÓN PRINCIPAL ---

if __name__ == "__main__":
    
    # 1. Asegurar la estructura de carpetas (solo las definidas en el config original)
    init_paths() 
    logger.info("Estructura de carpetas de datos verificada y lista.")

    # 2. Descarga y procesamiento
    df_clima = download_and_process_data()
    
    if df_clima is not None:
        # 3. Guardar el CSV en data/raw/
        save_csv(df_clima, RAW_DATA_PATH)
        
        # 4. Generar el archivo de documentación
        generate_documentation()
    
    logger.info("Proceso de descarga de Fuente clima completado.")