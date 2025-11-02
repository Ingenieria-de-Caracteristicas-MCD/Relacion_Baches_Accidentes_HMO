"""
extract_vialidades.py

Descarga la red vial de Hermosillo, Sonora, desde OpenStreetMap (OSM) utilizando la librería OSMnx, 
y exporta los datos de nodos y edges a formato Shapefile.
Guarda los resultados limpios en data/processed
"""

from config import ROOT_DIR, RAW_DIR, get_logger
from datetime import datetime
import warnings
from pathlib import Path
import osmnx as ox

warnings.filterwarnings('ignore')

# Paths
RAW_VIALIDADES_DIR = RAW_DIR / "vialidades"
RAW_VIALIDADES_DIR.mkdir(exist_ok=True)

CACHE_DIR = RAW_VIALIDADES_DIR / "cache_osmnx"
CACHE_DIR.mkdir(exist_ok=True)

# Logger
logger = get_logger(Path(__file__).name)

# Configuración de OSMnx
ox.settings.use_cache = True
ox.settings.cache_folder = str(CACHE_DIR)
ox.settings.log_console = False


def download_hmo_roads(network_type="drive", simplify=False):
    place = 'Hermosillo, Sonora, México'

    start = datetime.now()
    logger.info(f'Descargando red vial de {place} (tipo={network_type})...')

    G = ox.graph_from_place(place, network_type=network_type, simplify=simplify)

    end = datetime.now()
    elapsed = (end - start).total_seconds()

    logger.info(f'Descarga de red vial de {place} (tipo={network_type}) finalizada en {elapsed:.2f} s')
    return G


def export_graph_to_shapefiles(G, output_dir=RAW_VIALIDADES_DIR):
    logger.info('Convirtiendo grafo a shapefiles...')
    nodes, edges = ox.graph_to_gdfs(G)

    edges_dir = output_dir / "edges"
    nodes_dir = output_dir / "nodes"
    edges_dir.mkdir(parents=True, exist_ok=True)
    nodes_dir.mkdir(parents=True, exist_ok=True)

    # Rutas de salida
    edges_path = edges_dir / "hermosillo_edges.shp"
    nodes_path = nodes_dir / "hermosillo_nodes.shp"

    # Exportar shapefiles
    logger.info(f'Exportando edges en: {edges_path.relative_to(ROOT_DIR)}')
    edges.to_file(edges_path)

    logger.info(f'Exportando nodes en: {nodes_path.relative_to(ROOT_DIR)}')
    nodes.to_file(nodes_path)

    return nodes_path, edges_path


def export_graph_to_geojson(G, output_dir=RAW_VIALIDADES_DIR):

    logger.info('Convirtiendo grafo a GeoJSON...')
    nodes, edges = ox.graph_to_gdfs(G)

    # Crear directorios
    edges_dir = output_dir / "edges"
    nodes_dir = output_dir / "nodes"
    edges_dir.mkdir(parents=True, exist_ok=True)
    nodes_dir.mkdir(parents=True, exist_ok=True)

    # Rutas de salida
    edges_path = edges_dir / "hermosillo_edges.geojson"
    nodes_path = nodes_dir / "hermosillo_nodes.geojson"

    # Exportar GeoJSON
    logger.info(f'Exportando edges en: {edges_path.relative_to(ROOT_DIR)}')
    edges.to_file(edges_path, driver='GeoJSON')

    logger.info(f'Exportando nodes en: {nodes_path.relative_to(ROOT_DIR)}')
    nodes.to_file(nodes_path, driver='GeoJSON')

    return nodes_path, edges_path


def process_extraction_vialidades(): 
    start = datetime.now()
    logger.info('Inicia proceso de extracción VIALIDADES-OSM: ')

    G = download_hmo_roads()
    nodes_path, edges_path, = export_graph_to_shapefiles(G)
    nodes_geojson_path, edges_geojson_path = export_graph_to_geojson(G)

    end = datetime.now()
    elapsed = (end - start).total_seconds()
    logger.info(f'Proceso de extracción VIALIDADES-OSM finalizado en {elapsed:.2f} s')
        
    return nodes_path, edges_path, nodes_geojson_path, edges_geojson_path


if __name__ == "__main__":
    process_extraction_vialidades()