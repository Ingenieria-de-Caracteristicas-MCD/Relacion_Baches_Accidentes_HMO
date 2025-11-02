"""
download_atus.py

Descarga los archivos correspondientes a los años 2021–2023 del conjunto
de datos ATUS y los guarda en data/raw/atus.
"""

from config import RAW_DIR, get_logger
from zip_utils import download_zip
from itertools import repeat
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Paths
ATUS_DIR = RAW_DIR / "atus"
ATUS_DIR.mkdir(exist_ok=True)

# logger
logger = get_logger(Path(__file__).name)

# URL's
URL_2021 = r"https://www.inegi.org.mx/contenidos/programas/accidentes/datosabiertos/atus_2021_shp.zip"
URL_2022 = r"https://www.inegi.org.mx/contenidos/programas/accidentes/datosabiertos/atus_2022_shp.zip"
URL_2023 = r"https://www.inegi.org.mx/contenidos/programas/accidentes/datosabiertos/atus_2023_shp.zip"


def shoot_parallel_download(zip_urls, downloader=download_zip):
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(downloader, zip_urls, repeat(ATUS_DIR)))
    return results


def download_atus():
    zip_urls = [URL_2021, URL_2022, URL_2023]
    start = datetime.now()
    logger.info(f'Inicia proceso de descarga ATUS:')

    zip_paths = shoot_parallel_download(zip_urls)

    end = datetime.now()
    elapsed = (end - start).total_seconds()

    logger.info(f'Proceso de descarga ATUS finalizado en {elapsed:.2f} s')
    return zip_paths
 

if __name__ == '__main__': 
    download_atus()
