"""
download_colonias.py

Descarga el archivo ZIP del conjunto de datos:
Colonias — Delimitaciones Geoestadísticas (INEGI)

Uso:
    python download_colonias.py

Descarga el archivo ZIP, valida su integridad y lo guarda en data/raw/geo/colonias.
"""

from src.config import ROOT_DIR, RAW_DIR, get_logger
from pathlib import Path
from datetime import datetime
import zipfile
import requests
from tqdm import tqdm


# Paths
GEO_DIR = RAW_DIR / "geo"
GEO_DIR.mkdir(exist_ok=True)

COLONIAS_DIR = GEO_DIR / "colonias"
COLONIAS_DIR.mkdir(exist_ok=True)


# Logger
logger = get_logger(Path(__file__).name)


# URL
URL_COLONIAS = r"https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/geografia/delimitaciones/794551132180_s.zip"


def is_valid_zip(zip_path: Path):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            bad_file = zf.testzip()
            if bad_file:
                logger.error(f"ZIP corrupto: {zip_path.relative_to(ROOT_DIR)}")
                return False
            return True
    except zipfile.BadZipFile:
        logger.exception(f"ZIP corrupto: {zip_path.relative_to(ROOT_DIR)}")
        return False



def download_zip(url):
    filename = Path(url).name
    zip_path = COLONIAS_DIR / filename

    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()

        total_size = int(r.headers.get('content-length', 0))
        chunk_size = 1024 * 1024  # 1 MB

        with open(zip_path, 'wb') as f, tqdm(
            total=total_size,
            unit='B',
            unit_scale=True,
            desc=f"Descargando {filename}",
            ascii=True,
        ) as pbar:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

        if not is_valid_zip(zip_path):
            logger.error(f"Archivo ZIP inválido: {zip_path.name}. Reintentando...")
            return download_zip(url)

        return zip_path

    except requests.RequestException as e:
            logger.exception(f"Error al descargar {url}: {e}")
            return None

def download_colonias():
    start = datetime.now()
    logger.info("Inicia proceso de descarga de Colonias (INEGI)\n")

    zip_paths = [download_zip(URL_COLONIAS)]

    elapsed = (datetime.now() - start).total_seconds()
    logger.info(f"Descarga finalizada en {elapsed:.2f} s\n")

    logger.info("Archivos descargados:")
    for z in zip_paths:
        print(f" - {z.relative_to(ROOT_DIR)}")
    print()
    
    return zip_paths


if __name__ == "__main__":
    zip_paths = download_colonias()

