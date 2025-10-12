"""
utils.py

Funciones utilitarias para la descarga y validación de archivos ZIP
"""

from src.config import ROOT_DIR, get_logger

import zipfile
from pathlib import Path

import requests
from tqdm import tqdm


# Logger
logger = get_logger(Path(__file__).name)


def is_valid_zip(zip_path: Path):
    """
    Verifica si un archivo ZIP es válido y no está corrupto.
    """
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


def download_zip(url: str, output_dir: Path, chunk_size: int = 1024 * 1024):
    """
    Descarga un archivo ZIP desde una URL y lo guarda en el directorio especificado.
    Muestra una barra de progreso durante la descarga.
    """
    filename = Path(url).name
    zip_path = output_dir / filename

    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()

        total_size = int(r.headers.get('content-length', 0))

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

        # Validar archivo ZIP
        if not is_valid_zip(zip_path):
            logger.error(f"Archivo ZIP inválido: {zip_path.name}. Reintentando...")
            return download_zip(url, output_dir, chunk_size)

        return zip_path

    except requests.RequestException as e:
        logger.exception(f"Error al descargar {url}: {e}")
        return None
