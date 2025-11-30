"""
download_clima.py

Descarga los archivos del clima de Hermosillo desde el API de Open-Meteo.

Uso:
    python download_clima.py
"""

import pandas as pd
import requests_cache
from retry_requests import retry
from datetime import datetime
from pathlib import Path

from config import ROOT_DIR, RAW_DIR, get_logger

logger = get_logger(Path(__file__).name)

# Parámetros
START_DATE = "2021-01-01"
END_DATE = "2023-12-31"

LATITUDE = 29.1026
LONGITUDE = -110.9773
CITY_NAME = "Hermosillo"
DATA_SOURCE_1 = "Open-Meteo Archive API (Clima)"
DATA_URL_1 = "https://open-meteo.com/en/docs/archive-api"

# Rutas
CACHE_DIR = RAW_DIR / "cache_clima"
CLIMA_DIR = RAW_DIR / "clima"

CACHE_DIR.mkdir(parents=True, exist_ok=True)   # Crear cache_clima/
CLIMA_DIR.mkdir(parents=True, exist_ok=True)   # Crear clima/

# Archivos de salida
RAW_DATA_PATH = CLIMA_DIR / "clima_hermosillo.csv"
RAW_METADATA_PATH = RAW_DIR / "info_descargas_clima.txt"

# Cliente HTTP con cache + retry
cache = requests_cache.CachedSession(CACHE_DIR / "http_cache.sqlite", expire_after=-1)
session = retry(cache, retries=5, backoff_factor=0.2)

API_URL = "https://archive-api.open-meteo.com/v1/archive"

PARAMS = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "start_date": START_DATE,
    "end_date": END_DATE,
    "hourly": [
        "temperature_2m",
        "precipitation",
        "weather_code",
        "is_day",
        "relative_humidity_2m",
        "cloud_cover",
        "wind_speed_10m"
    ],
    "timezone": "UTC"
}


# Descarga y procesamiento
def download_and_process_data():
    """Descarga los datos del API y los convierte a DataFrame."""
    logger.info(f"Conectando a {DATA_SOURCE_1}…")

    try:
        resp = session.get(API_URL, params=PARAMS)
        resp.raise_for_status()
        data = resp.json()

        if "hourly" not in data:
            raise ValueError("La respuesta no contiene datos horarios ('hourly').")

        hourly = data["hourly"]

        df = pd.DataFrame(hourly)
        df["time"] = pd.to_datetime(df["time"], utc=True)
        df.rename(columns={"time": "date"}, inplace=True)

        logger.info(f"Descargados {len(df)} registros de clima.")
        return df

    except Exception as e:
        logger.error(f"Error al descargar o procesar los datos: {e}")
        return None


# Guardado y documentación

def save_csv(df, path: Path):
    df.to_csv(path, index=False)
    logger.info(f"Datos guardados exitosamente en: {path.relative_to(ROOT_DIR)}")


def generate_documentation():
    contenido = f"""
# ===============================================
# DESCRIPCIÓN DE FUENTES DE DATOS - CLIMA HMO
# ===============================================

## Fuente 1: Datos Meteorológicos Históricos
- **Nombre de la Fuente:** {DATA_SOURCE_1}
- **Enlace:** {DATA_URL_1}
- **Fecha de Descarga:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Ubicación:** {CITY_NAME} (Lat: {LATITUDE}, Lon: {LONGITUDE})
- **Rango de Fechas de los Datos:** {START_DATE} a {END_DATE}

- **Variables Descargadas:**
    - temperature_2m
    - precipitation
    - weather_code
    - is_day
    - relative_humidity_2m
    - cloud_cover
    - wind_speed_10m

- **Frecuencia Temporal:** Horaria
- **Formato de los Datos:** CSV
"""

    RAW_METADATA_PATH.write_text(contenido, encoding="utf-8")
    logger.info(f"Documentación generada en: {RAW_METADATA_PATH.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    logger.info("Estructura de carpetas verificada.")

    df = download_and_process_data()

    if df is not None:
        save_csv(df, RAW_DATA_PATH)
        generate_documentation()

    logger.info("Proceso de descarga de clima completado.")
