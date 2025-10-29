"""
download_colonias.py

Descarga el archivo ZIP del conjunto de datos: Colonias — Delimitaciones Geoestadísticas (INEGI)
Guarda los datos en data/raw/colonias
"""

from config import RAW_DIR, get_logger
from zip_utils import download_zip
from datetime import datetime
from pathlib import Path

# Paths
COLONIAS_DIR = RAW_DIR / "colonias"
COLONIAS_DIR.mkdir(exist_ok=True)

# Logger
logger = get_logger(Path(__file__).name)

# URL
URL_COLONIAS = r"https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/geografia/delimitaciones/794551132180_s.zip"


def download_colonias():
    start = datetime.now()
    logger.info("Inicia proceso de descarga COLONIAS-INEGI: ")

    zip_path = download_zip(URL_COLONIAS, COLONIAS_DIR)

    elapsed = (datetime.now() - start).total_seconds()

    logger.info(f"Proceso de descarga COLONIAS-INEGI finalizado en {elapsed:.2f} s")

    return [zip_path]


if __name__ == "__main__":
    download_colonias()