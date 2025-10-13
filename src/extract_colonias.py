"""
extract_colonias.py

Extrae el archivo ZIP de colonias descargado desde INEGI,
lee los archivos geoespaciales y filtra las colonias
correspondientes a Hermosillo, Sonora (CVE_ENT=26, CVE_MUN=30, CVE_LOC=0001).

Guarda los resultados filtrados en data/interim/geo.
"""

from src.config import ROOT_DIR, RAW_DIR, INTERIM_DIR, get_logger
from src.utils import extract_zip_file, extract_all_zips, get_zip_paths
from src.download_colonias import COLONIAS_DIR

from shutil import rmtree
from pathlib import Path
from datetime import datetime
import zipfile

import geopandas as gpd


# Paths
INTERIM_GEO_DIR = INTERIM_DIR / "geo"
INTERIM_GEO_DIR.mkdir(exist_ok=True)

# Logger
logger = get_logger(Path(__file__).name)


def get_shp_path(extracted_dir):
    for shp_file in extracted_dir.rglob("*.shp"):
        return shp_file
    logger.error(f"No se encontró archivo .shp en {extracted_dir}")
    return None


def filter_hermosillo_colonias(shp_path):
    gdf = gpd.read_file(shp_path)
    gdf[["CVE_ENT", "CVE_MUN", "CVE_LOC"]] = gdf[["CVE_ENT", "CVE_MUN", "CVE_LOC"]].astype(int)

    gdf_hmo = gdf[(gdf["CVE_ENT"] == 26) & (gdf["CVE_MUN"] == 30)]
    gdf_hmo_urb = gdf_hmo[gdf_hmo["CVE_LOC"] == 1]

    outpath = INTERIM_GEO_DIR / "colonias_hmo.geojson"
    gdf_hmo_urb.to_file(outpath, driver="GeoJSON")

    logger.info(f"Archivo {shp_path.relative_to(ROOT_DIR)} filtrado -> {outpath.relative_to(ROOT_DIR)}")
    return outpath


def process_extraction_colonias(clean=False):
    start = datetime.now()
    logger.info("Inicia proceso de extracción: \n")

    zip_paths = get_zip_paths(dirpath=COLONIAS_DIR)
    extracted_paths = extract_all_zips(zip_paths)

    for extracted_dir in extracted_paths:
        shp_path = get_shp_path(extracted_dir)
        if shp_path:
            path_colonias_hmo = filter_hermosillo_colonias(shp_path)

    elapsed = (datetime.now() - start).total_seconds()
    print()
    logger.info(f"Proceso de extracción completado en {elapsed:.2f} s\n")

    if clean:
        rmtree(path=COLONIAS_DIR)
        logger.info(f"Directorio {COLONIAS_DIR.relative_to(ROOT_DIR)} eliminado\n")
    
    return path_colonias_hmo

if __name__ == "__main__":
    process_extraction_colonias(clean=True)
