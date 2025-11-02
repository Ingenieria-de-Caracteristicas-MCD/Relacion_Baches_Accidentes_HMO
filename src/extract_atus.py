"""
extract_atus.py

Automatiza la extracción del conjunto de datos ATUS: descarga y descomprime los archivos ZIP necesarios.
"""

from config import ROOT_DIR, get_logger
from zip_utils import extract_all_zips, get_zip_paths
from download_atus import download_atus, ATUS_DIR
from pathlib import Path
from datetime import datetime


# logger
logger = get_logger(Path(__file__).name)


def process_extraction_atus():
    start = datetime.now()
    logger.info(f'Inicia proceso de exrtacción ATUS:')
    
    zip_paths = get_zip_paths(ATUS_DIR)

    if not zip_paths: 
        logger.warning(f'No se encontraron archivos ZIP en el directorio {ATUS_DIR.relative_to(ROOT_DIR)}. ')
        zip_paths = download_atus()
    
    extracted_paths = extract_all_zips(zip_paths, ATUS_DIR)
    
    end = datetime.now()
    elapsed = (end - start).total_seconds()
    logger.info(f'Proceso de extracción ATUS completado en {elapsed:.2f} s')
    
    return extracted_paths


if __name__ == '__main__':
    process_extraction_atus()