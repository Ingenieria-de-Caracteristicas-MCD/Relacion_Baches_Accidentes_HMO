"""
extract_colonias.py

Extrae el archivo ZIP de colonias descargado desde INEGI,
lee los archivos geoespaciales y filtra las colonias
correspondientes a Hermosillo, Sonora (CVE_ENT=26, CVE_MUN=30, CVE_LOC=0001).

Guarda los resultados filtrados en data/interim/geo.
"""

from src.config import ROOT_DIR, RAW_DIR, INTERIM_DIR, get_logger
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


def extract_zip_file(zip_path: Path, output_path=None):
    if not output_path:
        filename = zip_path.stem
        output_path = COLONIAS_DIR / filename

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(path=output_path)
        return output_path, True

    except zipfile.BadZipFile:
        logger.exception(f"ZIP corrupto: {zip_path.relative_to(ROOT_DIR)}")
        return output_path, False


def extract_all_zips(zip_paths):
    extracted = []
    for zip_path in zip_paths:
        outpath, valid = extract_zip_file(zip_path)
        if valid:
            extracted.append(outpath)
            logger.info(f"ZIP {zip_path.name} extraído -> {outpath.relative_to(ROOT_DIR)}")
    return extracted


def get_zip_paths(dirpath=COLONIAS_DIR):
    return [p for p in dirpath.iterdir() if p.suffix == ".zip"]


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

    logger.info(f"Colonias de Hermosillo filtradas -> {outpath.relative_to(ROOT_DIR)}")
    return outpath


def process_extraction_colonias(clean=False):
    start = datetime.now()
    logger.info("Inicia proceso de extracción de Colonias\n")

    zip_paths = get_zip_paths()
    extracted_paths = extract_all_zips(zip_paths)

    for extracted_dir in extracted_paths:
        shp_path = get_shp_path(extracted_dir)
        if shp_path:
            filter_hermosillo_colonias(shp_path)

    elapsed = (datetime.now() - start).total_seconds()
    logger.info(f"Proceso completado en {elapsed:.2f} s\n")

    if clean:
        rmtree(path=COLONIAS_DIR)
        print(f"Directorio {COLONIAS_DIR.relative_to(ROOT_DIR)} eliminado")
    
    return 

if __name__ == "__main__":
    process_extraction_colonias(clean=True)
