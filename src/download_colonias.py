"""
download_colonias.py

Descarga el archivo ZIP del conjunto de datos:
Colonias — Delimitaciones Geoestadísticas (INEGI)

Uso:
    python download_colonias.py

Descarga el archivo ZIP, valida su integridad y lo guarda en data/raw/geo/colonias.
"""

from src.config import ROOT_DIR, RAW_DIR, get_logger
from src.utils import download_zip

from datetime import datetime
from pathlib import Path


# Paths
GEO_DIR = RAW_DIR / "geo"
GEO_DIR.mkdir(exist_ok=True)


COLONIAS_DIR = GEO_DIR / "colonias"
COLONIAS_DIR.mkdir(exist_ok=True)


# Logger
logger = get_logger(Path(__file__).name)


# URL
URL_COLONIAS = r"https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/geografia/delimitaciones/794551132180_s.zip"


def download_colonias():
    start = datetime.now()
    logger.info("Inicia proceso de descarga de Colonias (INEGI)\n")

    zip_path = download_zip(URL_COLONIAS, COLONIAS_DIR)

    elapsed = (datetime.now() - start).total_seconds()

    logger.info(f"Descarga finalizada en {elapsed:.2f} s\n")

    logger.info("Archivos descargados:")
    if zip_path:
        print(f" - {zip_path.relative_to(ROOT_DIR)}")
    print()

    return zip_path


if __name__ == "__main__":
    download_colonias()

