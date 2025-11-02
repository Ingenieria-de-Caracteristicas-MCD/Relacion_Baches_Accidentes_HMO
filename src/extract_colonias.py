"""
extract_colonias.py

Extrae el archivo ZIP de colonias descargado desde INEGI. 
Guarda los resultados filtrados en data/raw/colonias
"""

from config import ROOT_DIR, get_logger
from zip_utils import get_zip_paths, extract_all_zips
from download_colonias import COLONIAS_DIR, download_colonias
from pathlib import Path
from datetime import datetime

# Logger
logger = get_logger(Path(__file__).name)


def process_extraction_colonias():
    start = datetime.now()
    logger.info('Inicia proceso de extracción COLONIAS-INEGI: ')

    zip_paths = get_zip_paths(dirpath=COLONIAS_DIR)
    if not zip_paths: 
        logger.warning(f'No se encontraron archivos ZIP en el directorio {COLONIAS_DIR.relative_to(ROOT_DIR)}')
        zip_paths = download_colonias()

    extracted_paths = extract_all_zips(zip_paths, COLONIAS_DIR)
        
    elapsed = (datetime.now() - start).total_seconds()
    logger.info(f'Proceso de extracción COLONIAS-INEGI completado en {elapsed:.2f} s')

    return extracted_paths


if __name__ == "__main__":
    process_extraction_colonias()
