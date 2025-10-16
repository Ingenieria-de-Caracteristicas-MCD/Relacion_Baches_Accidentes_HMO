"""
download_colonias.py

Descarga el archivo ZIP del conjunto de datos:
Colonias — Delimitaciones Geoestadísticas (INEGI)

Uso:
    python download_colonias.py

Descarga el archivo ZIP, valida su integridad y lo guarda en data/raw/geo/colonias.
"""

from config import ROOT_DIR, RAW_DIR, get_logger
from utils import download_zip

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


def generate_documentation_colonias():
    doc_content = f"""
# DESCRIPCIÓN DE FUENTES DE DATOS - COLONIAS INEGI

Fuente: Delimitaciones Geoestadísticas (Colonias)
- Nombre de la Fuente: Delimitaciones Geoestadísticas (Colonias)
- Institución: INEGI
- Enlace: {URL_COLONIAS}
- Fecha de Descarga: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- Ubicación: México
- Formato de los Datos: ZIP (contiene archivos Shapefile)
- Descripción de los Datos:
    Conjunto de delimitaciones espaciales de colonias urbanas a nivel nacional, 
    usadas para análisis geográficos y de ubicación territorial.
"""

    doc_path = RAW_DIR / "documentacion_colonias.txt"
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(doc_content)
    logger.info(f"Documentación de fuentes generada en: {doc_path}")


def download_colonias():
    start = datetime.now()
    logger.info("Inicia proceso de descarga de Colonias (INEGI)")

    zip_path = download_zip(URL_COLONIAS, COLONIAS_DIR)

    elapsed = (datetime.now() - start).total_seconds()

    logger.info(f"Descarga finalizada en {elapsed:.2f} s")

    generate_documentation_colonias()

    logger.info("Archivos descargados:")
    if zip_path:
        print(f" - {zip_path.relative_to(ROOT_DIR)}")

    return zip_path


if __name__ == "__main__":
    download_colonias()

