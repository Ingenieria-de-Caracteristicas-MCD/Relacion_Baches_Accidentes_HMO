"""
clean_colonias.py

Filtra y limpia el conjunto de datos de colonias descargado desde INEGI.
Guarda los resultados filtrados en data/processed
"""

from config import ROOT_DIR, INTERIM_DIR, PROCESSED_DIR, get_logger
from extract_colonias import COLONIAS_DIR
from pathlib import Path
from datetime import datetime
import geopandas as gpd

# Logger
logger = get_logger(Path(__file__).name)

# Paths
INTERIM_COLONIAS_DIR = INTERIM_DIR / "colonias"
INTERIM_COLONIAS_DIR.mkdir(exist_ok=True)

PROCESSED_COLONIAS_DIR = PROCESSED_DIR / "colonias"
PROCESSED_COLONIAS_DIR.mkdir(exist_ok=True)

# CRS real según documentación del INEGI (data/raw/colonias/794551132180_s/catalogos/contenido)
CSR_INEGI = (
    'PROJCS["ITRF2008 / LCC Mexico",'
    'GEOGCS["ITRF2008",DATUM["ITRF_2008",SPHEROID["GRS 1980",6378137,298.257222101]],'
    'PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],'
    'PROJECTION["Lambert_Conformal_Conic_2SP"],'
    'PARAMETER["standard_parallel_1",17.5],'
    'PARAMETER["standard_parallel_2",29.5],'
    'PARAMETER["latitude_of_origin",12],'
    'PARAMETER["central_meridian",-102],'
    'PARAMETER["false_easting",2500000],'
    'PARAMETER["false_northing",0],'
    'UNIT["metre",1]]'
)


def get_shp_path(dir):
    shp_list = list(dir.rglob("*.shp"))
    if not shp_list:
        raise FileNotFoundError(f'No .shp found in {dir}')
    return shp_list[0]


def save_geo_data(gdf, dest_path, filestem):

    # Guardar GeoPackage (manteniendo CRS proyectado)
    gpkg_path = dest_path / f"{filestem}.gpkg"
    gdf.to_file(gpkg_path, driver='GPKG')

    # Guardar GeoJSON (proyección EPSG:4326)
    gdf_wgs84 = gdf.to_crs(epsg=4326)
    geojson_path = dest_path / f"{filestem}.geojson"
    gdf_wgs84.to_file(geojson_path, driver='GeoJSON')

    return gpkg_path, geojson_path


def filter_hermosillo_colonias(gdf):
    gdf[['CVE_ENT', 'CVE_MUN', 'CVE_LOC']] = gdf[['CVE_ENT', 'CVE_MUN', 'CVE_LOC']].astype(int)

    gdf_hmo = gdf[(gdf['CVE_ENT'] == 26) & (gdf['CVE_MUN'] == 30)]
    gdf_hmo_urb = gdf_hmo[gdf_hmo['CVE_LOC'] == 1]

    # Guardar datos filtrados
    gpkg_path, geojson_path = save_geo_data(gdf_hmo_urb, INTERIM_COLONIAS_DIR, 'colonias_hmo')
    logger.info(f'Archivos filtrado guardado en: {INTERIM_COLONIAS_DIR.relative_to(ROOT_DIR)}')
    return gdf_hmo_urb


def columns_to_lower(gdf):
    obj_cols = gdf.select_dtypes(include='object')
    
    for col in obj_cols.columns:
        gdf[col] = gdf[col].str.lower()
    
    return gdf


def process_cleaning_colonias():    
    start = datetime.now()
    logger.info('Inicia el proceso de limpieza COLONIAS-INEGI:')

    shp_path = get_shp_path(COLONIAS_DIR)

    # Cargar datos
    gdf = gpd.read_file(shp_path)
    
    # Filtrar zona urbana de Hermosillo
    gdf_hmo = filter_hermosillo_colonias(gdf)

    # Asignar el CRS INEGI
    gdf_hmo = gdf_hmo.set_crs(CSR_INEGI, allow_override=True)

    # Renombrar columnas lower
    gdf_hmo.columns = gdf_hmo.columns.str.lower()

    # Normalizar columnas tipo str
    gdf_hmo = columns_to_lower(gdf_hmo)

    # Eliminar columnas {'cve_ent', 'cve_mun', 'cve_loc', 'fecha_act', 'institucio'}
    gdf_hmo.drop(columns=['cve_ent', 'cve_mun', 'cve_loc', 'fecha_act', 'institucio'], inplace=True)

    gpkg_path, geojson_path = save_geo_data(gdf_hmo, PROCESSED_COLONIAS_DIR, 'colonias_hmo')

    logger.info(f'Archivos limpios guardados en: {PROCESSED_COLONIAS_DIR.relative_to(ROOT_DIR)}')

    end = datetime.now()
    elapsed = (end - start).total_seconds()
    logger.info(f'Proceso de limpieza COLONIAS-INEGI completado en {elapsed:.2f} s')
 
    return gpkg_path, geojson_path


if __name__ == '__main__': 
    process_cleaning_colonias()

