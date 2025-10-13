"""
extract_atus.py

...
"""

from config import ROOT_DIR, INTERIM_DIR, get_logger
from utils import extract_zip_file, extract_all_zips, get_zip_paths
from download_atus import ATUS_DIR

from shutil import rmtree
from pathlib import Path
from datetime import datetime

import pandas as pd

# Paths
INTERIM_ATUS_DIR = INTERIM_DIR / "atus"
INTERIM_ATUS_DIR.mkdir(exist_ok=True)


# logger
logger = get_logger(Path(__file__).name)


def filter_hermosillo_records(csv_path):
     df = pd.read_csv(csv_path, encoding='latin1')
     df_hmo = df[
         (df['EDO'] == 26) & (df['MPIO'] == 30)
     ]
     filename = csv_path.stem

     outpath = INTERIM_ATUS_DIR / f"{filename}_HMO.csv"
     df_hmo.to_csv(outpath)
     return outpath


def get_csv_paths(paths):
    csv_paths = []
    for path in paths:
        for csv_file in path.rglob("*.csv"):
            csv_paths.append(csv_file)
    return csv_paths


def filter_all_csvs(paths):
    csv_paths = get_csv_paths(paths)
    paths_atus_hmo = []
    for csv_path in csv_paths: 
        outpath = filter_hermosillo_records(csv_path)
        logger.info(f'Archivo {csv_path.relative_to(ROOT_DIR)} filtrado -> {outpath.relative_to(ROOT_DIR)}\n')
        paths_atus_hmo.append(outpath)            

    return paths_atus_hmo


def process_extraction_atus_hmo(clean=False):
    start = datetime.now()
    logger.info(f'Inicia proceso de exrtacción:\n')
    
    zip_paths = get_zip_paths(ATUS_DIR)    
    extracted_paths = extract_all_zips(zip_paths)
    print()
    paths_atus_hmo = filter_all_csvs(extracted_paths)

    end = datetime.now()
    elapsed = (end - start).total_seconds()
    print()
    logger.info(f'Proceso de extracción completado en {elapsed:.2f} s\n')

    if clean: 
        rmtree(path=ATUS_DIR)
        logger.info(f"Directorio {ATUS_DIR.relative_to(ROOT_DIR)} eliminado\n")
    
    return paths_atus_hmo

if __name__ == '__main__':
    processed_files = process_extraction_atus_hmo(clean=True)