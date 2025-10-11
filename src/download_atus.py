"""
download_atus.py

Descarga los archivos ZIP del conjunto de datos:
Accidentes de Tránsito Terrestre en Zonas Urbanas y Suburbanas (ATUS)
publicados por el INEGI.

Uso:
    python download_atus.py

Descarga los archivos correspondientes a los años 2021–2023 en paralelo,
valida su integridad (ZIP válido) y los guarda en RAW_DIR/atus.
"""


from src.config import ROOT_DIR, DATA_DIR, RAW_DIR, get_logger

import zipfile
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import requests
from tqdm import tqdm


# Paths
ATUS_DIR = RAW_DIR / "atus"
ATUS_DIR.mkdir(exist_ok=True)


# logger
logger = get_logger(Path(__file__).name)


# URL's
URL_2021 = r"https://www.inegi.org.mx/contenidos/programas/accidentes/datosabiertos/atus_2021_shp.zip"
URL_2022 = r"https://www.inegi.org.mx/contenidos/programas/accidentes/datosabiertos/atus_2022_shp.zip"
URL_2023 = r"https://www.inegi.org.mx/contenidos/programas/accidentes/datosabiertos/atus_2023_shp.zip"


def is_valid_zip(zip_path: Path): 
    try: 
        with zipfile.ZipFile(zip_path, 'r') as zf: 
            bad_file = zf.testzip()

            if bad_file:
                logger.error(f"ZIP corrupto: {zip_path.relative_to(ROOT_DIR)}") 
                return False
            else: 
                return True
    except zipfile.BadZipFile as e: 
        logger.exception(f"ZIP corrupto: {zip_path.relative_to(ROOT_DIR)}")
        return False


def download_zip(url):
    filename = Path(url).name
    zip_path = ATUS_DIR / filename

    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()

        total_size = int(r.headers.get('content-length', 0))
        chunk_size = 1024 * 1024  # 1 MB

        with open(zip_path, 'wb') as file, tqdm(
            total=total_size,
            unit='B',
            unit_scale=True,
            desc=f"Descargando {filename}",
            initial=0,
            ascii=True,
        ) as pbar:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    file.write(chunk)
                    pbar.update(len(chunk))

        # Validar el ZIP
        if not is_valid_zip(zip_path):
            logger.error(f"\nEl archivo descargado desde {url} no es un ZIP válido. Reintentando...")
            return download_zip(url)

        return zip_path

    except requests.HTTPError as e:
        logger.exception(f"Error al descargar desde {url}. Código de error HTTP: {e.response.status_code}.")

    except requests.RequestException as e:
        logger.exception(f"Error en la solicitud al intentar descargar {url}. Verifica la conexción a internet. ")


def shoot_parallel_download(zip_urls, downloader=download_zip):
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(downloader, zip_urls))
    return results


def download_atus():
    zip_urls = [URL_2021, URL_2022, URL_2023]
    start = datetime.now()
    logger.info(f'Inicia proceso de descarga...\n')

    zip_paths = shoot_parallel_download(zip_urls)

    end = datetime.now()
    elapsed = (end - start).total_seconds()
    logger.info(f'\nProceso de descarga finalizado en {elapsed:.2f} s')

    logger.info("\nArchivos descargados:")
    for z in zip_paths:
        logger.info(f" - {z.relative_to(ROOT_DIR)}")
    
    return zip_paths
 

if __name__ == '__main__': 
    # for x in [ROOT_DIR, DATA_DIR, RAW_DIR, ATUS_DIR]: logger.debug(f'{x.exists()}, {x.is_dir()}')  # OK
    zip_paths = download_atus()
