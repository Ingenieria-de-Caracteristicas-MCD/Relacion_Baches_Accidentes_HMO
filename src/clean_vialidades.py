"""
clean_vialidades.py

Filtra y limpia el conjunto de datos de vialidades de Hermosillo descargado desde OSM.
Guarda los resultados filtrados en data/processed/vialidades
"""

from config import ROOT_DIR, RAW_DIR,  INTERIM_DIR, PROCESSED_DIR, get_logger
from extract_vialidades import RAW_VIALIDADES_DIR
from datetime import datetime
from pathlib import Path
from shapely.geometry import box
import geopandas as gpd
import pandas as pd

# Logger
logger = get_logger(Path(__file__).name)

# Paths
# Paths
INTERIM_VIALIDADES_DIR = INTERIM_DIR / "vialidades"
INTERIM_VIALIDADES_DIR.mkdir(exist_ok=True)

PROCESSED_VIALIDADES_DIR = PROCESSED_DIR / "vialidades"
PROCESSED_VIALIDADES_DIR.mkdir(exist_ok=True)


def filter_urban_roads(gdf): 
    # Coordenadas límite (x = longitudes, y = latitudes)
    x_min, x_max = -111.075, -110.900
    y_min, y_max = 28.000, 29.250
    # Creamos el rectángulo que representa el área de Hermosillo
    bbox = box(x_min, y_min, x_max, y_max)
    filtered = gdf[gdf.intersects(bbox)]

    # Guardar datos filtrados
    gpkg_path, geojson_path = save_geo_data(filtered, INTERIM_VIALIDADES_DIR, 'vialidades_hmo_urb')
    logger.info(f'Archivos filtrado guardado en: {INTERIM_VIALIDADES_DIR.relative_to(ROOT_DIR)}')

    return filtered


def drop_cols(gdf):
    cols_to_drop = [
        'u', 'v', 'key', 'osmid',
        'bridge', 
        'tunnel', 
        'width',
        'junction', 
        'access', 
        'ref', 
        'reversed',
        ]
    return gdf.drop(columns=cols_to_drop)
        

def rename_cols(gdf): 
    rename_map = {
        "maxspeed": "vel_max",       # velocidad máxima permitida
        # "osmid": "id_osm",           # identificador OSM
        "oneway": "un_sentido",      # indica si es de un solo sentido
        "lanes": "num_carriles",     # número de carriles
        "name": "nombre_vialidad",   # nombre de la vialidad
        "highway": "tipo_vialidad",  # categoría según OSM (calle, avenida, etc.)
        "length": "longitud"         # longitud estimada de la vialidad (m)
    }
    return gdf.rename(columns=rename_map)


def rename_tipo_vialidad(gdf):
    vialidades_map = {
        'motorway': 'Autopista',
        'motorway_link': 'Conector autopista',
        'trunk': 'Carretera principal',
        'trunk_link': 'Conector carretera',
        'primary': 'Vía primaria',
        'primary_link': 'Conector primaria',
        'secondary': 'Vía secundaria',
        'secondary_link': 'Conector secundaria',
        'tertiary': 'Vía terciaria',
        'tertiary_link': 'Conector terciaria',
        'residential': 'Calle residencial',
        'unclassified': 'Calle menor',
        'living_street': 'Calle peatonal'
    }

    gdf['tipo_vialidad'] = gdf['tipo_vialidad'].replace(vialidades_map)
    return gdf


def save_geo_data(gdf, dest_path, filestem):

    # Guardar GeoPackage (manteniendo CRS proyectado)
    gpkg_path = dest_path / f"{filestem}.gpkg"
    gdf.to_file(gpkg_path, driver='GPKG')

    # Guardar GeoJSON (proyección EPSG:4326)
    gdf_wgs84 = gdf.to_crs(epsg=4326)
    geojson_path = dest_path / f"{filestem}.geojson"
    gdf_wgs84.to_file(geojson_path, driver='GeoJSON')

    return gpkg_path, geojson_path


def columns_to_lower(gdf):
    obj_cols = gdf.select_dtypes(include='object')
    
    for col in obj_cols.columns:
        gdf[col] = gdf[col].str.lower()
    
    return gdf


def process_cleaning_vialidades(): 

    start = datetime.now()
    logger.info('Inicia proceso de limpieza VIALIDADES-OSM: ')

    raw_path = RAW_VIALIDADES_DIR.joinpath("edges/hermosillo_edges.geojson")
    gdf = gpd.read_file(raw_path)

    # Filtrar vialidades en la zona urbana de Hermosillo
    gdf = filter_urban_roads(gdf)

    # Eliminar columnas innecesarias
    gdf = drop_cols(gdf)

    # Renombrar columnas
    gdf = rename_cols(gdf)

    # Remombrar tipo_vialidad
    gdf = rename_tipo_vialidad(gdf)

    # Normalizar columnas tipo str
    gdf = columns_to_lower(gdf)

    # Guardar datos 
    gpkg_path, geojson_path = save_geo_data(gdf, PROCESSED_VIALIDADES_DIR, 'vialidades_hmo')
    logger.info(f'Archivos limpios guardados en: {PROCESSED_VIALIDADES_DIR.relative_to(ROOT_DIR)}')
    
    end = datetime.now()
    elapsed = (end - start).total_seconds()
    logger.info(f'Proceso de limpieza VIALIDADES-OSM finalizado en {elapsed:.2f} s')
    
    return gpkg_path, geojson_path


if __name__ == '__main__': 
    process_cleaning_vialidades()
