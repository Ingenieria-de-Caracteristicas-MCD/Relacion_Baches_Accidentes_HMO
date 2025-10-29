"""
clean_colonias.py

Filtra y limpia el conjunto de datos de colonias descargado desde INEGI.
Guarda los resultados filtrados en data/processed
"""

from config import ROOT_DIR, PROCESSED_DIR, get_logger
from extract_colonias import COLONIAS_DIR
from pathlib import Path
from datetime import datetime
import geopandas as gpd

# Logger
logger = get_logger(Path(__file__).name)


def get_shp_path(dir):
    return list(dir.rglob("*.shp"))[0]


def filter_hermosillo_colonias(shp_path):
    gdf = gpd.read_file(shp_path)
    gdf[["CVE_ENT", "CVE_MUN", "CVE_LOC"]] = gdf[["CVE_ENT", "CVE_MUN", "CVE_LOC"]].astype(int)

    gdf_hmo = gdf[(gdf["CVE_ENT"] == 26) & (gdf["CVE_MUN"] == 30)]
    gdf_hmo_urb = gdf_hmo[gdf_hmo["CVE_LOC"] == 1]

    outpath = PROCESSED_DIR / "colonias_hmo.geojson"
    gdf_hmo_urb.to_file(outpath, driver="GeoJSON")

    logger.info(f"Archivo {shp_path.relative_to(ROOT_DIR)} filtrado guardado en: {outpath.relative_to(ROOT_DIR)}")
    return outpath


def process_cleaning_colonias(csv_paths=[]):    
    start = datetime.now()
    logger.info(f'Inicia el proceso de limpieza COLONIAS-INEGI: ')

    shp_path = get_shp_path(COLONIAS_DIR)
    path_colonias_hmo = filter_hermosillo_colonias(shp_path)

    end = datetime.now()
    elapsed = (end - start).total_seconds()
    logger.info(f"Proceso de limpieza COLONIAS-INEGI completado en {elapsed:.2f} s")
 
    return path_colonias_hmo


if __name__ == '__main__': 
    process_cleaning_colonias()
