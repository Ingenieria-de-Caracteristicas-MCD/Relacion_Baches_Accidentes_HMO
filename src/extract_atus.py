"""
extract_atus.py

...
"""

from src.config import ROOT_DIR, DATA_DIR, RAW_DIR, INTERIM_DIR, get_logger
from src.download_atus import ATUS_DIR

import zipfile
from shutil import rmtree
from pathlib import Path
from datetime import datetime

import pandas as pd

# Paths
INTERIM_ATUS_DIR = INTERIM_DIR / "atus"
INTERIM_ATUS_DIR.mkdir(exist_ok=True)


# logger
logger = get_logger(Path(__file__).name)


def extract_zip_file(zip_path: Path, output_path=None):
    if not output_path: 
        filename = zip_path.stem
        output_path = ATUS_DIR / filename

    try: 
        with zipfile.ZipFile(zip_path, 'r') as zf: 
            zf.extractall(path=output_path)
        
        return output_path, True
    
    except zipfile.BadZipFile: 
        logger.exception(f'ZIP corrupto: {zip_path.relative_to(ROOT_DIR)}')
        return output_path, False


def extract_all_zips(zip_paths):
    extracted_paths = []
    for zip_path in zip_paths:
        extracted_path, valid = extract_zip_file(zip_path)
        if valid: 
            extracted_paths.append(extracted_path)
            logger.info(f'Archivo ZIP {zip_path.relative_to(ROOT_DIR)} descomprimido -> {extracted_path.relative_to(ROOT_DIR)}\n')
            
    return extracted_paths


def get_zip_paths(dirpath=ATUS_DIR):
    paths = [] 
    # logger.debug(f'trol get_zip_paths:  {type(dirpath)}, {dirpath}')
    for item in dirpath.iterdir():
        # logger.debug(item)  # OK
        if item.suffix == '.zip':
            paths.append(item)    
    return paths


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
    
    zip_paths = get_zip_paths()    
    # logger.debug(zip_paths)
    extracted_paths = extract_all_zips(zip_paths)
    paths_atus_hmo = filter_all_csvs(extracted_paths)

    end = datetime.now()
    elapsed = (end - start).total_seconds()
    logger.info(f'Proceso de descarga finalizado en {elapsed:.2f} s\n')

    logger.info('Archivos procesados:')
    for p in paths_atus_hmo:
        print(' - {p.relative_to(ROOT_DIR)}')
    print()
    if clean: 
        rmtree(path=ATUS_DIR)


if __name__ == '__main__':
    processed_files = process_extraction_atus_hmo(clean=True)