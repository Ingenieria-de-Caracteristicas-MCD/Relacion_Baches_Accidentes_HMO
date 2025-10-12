"""
extract_vialidades.py

...
"""

from src.config import ROOT_DIR, INTERIM_DIR, get_logger

from datetime import datetime
from pathlib import Path

import osmnx as ox
import geopandas as gpd


# Paths
INTERIM_GEO_DIR = INTERIM_DIR / "geo"
INTERIM_GEO_DIR.mkdir(exist_ok=True)

CACHE_DIR = INTERIM_GEO_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)


# Logger
logger = get_logger(Path(__file__).name)


# Configuración de OSMnx
ox.settings.use_cache = True
ox.settings.cache_folder = str(CACHE_DIR)
ox.settings.log_console = False  # Cambir a False


def download_hmo_roads(network_type="drive", simplify=True):
    place = "Hermosillo, Sonora, México"
    logger.info(f"Descargando red vial de {place} (tipo={network_type})...\n")

    G = ox.graph_from_place(place, network_type=network_type, simplify=simplify)

    logger.info("Descarga completada\n")
    return G

def export_graph_to_shapefiles(G, output_dir=INTERIM_GEO_DIR): 
    logger.info("Convirtiendo grafo a GeoDataFrames...\n")
    nodes, edges = ox.graph_to_gdfs(G)

    edges_path = output_dir / "hermosillo_edges.shp"
    nodes_path = output_dir / "hermosillo_nodes.shp"

    logger.info(f"Exportando edges -> {edges_path.relative_to(ROOT_DIR)}")
    edges.to_file(edges_path)

    logger.info(f"Exportando nodes -> {nodes_path.relative_to(ROOT_DIR)}")
    nodes.to_file(nodes_path)

    return nodes_path, edges_path


def process_extraction_roads_hmo(): 
    start = datetime.now()
    logger.info("Inicia proceso de extracción de vialidades: ")

    G = download_hmo_roads()
    nodes_path, edges_path, = export_graph_to_shapefiles(G)

    end = datetime.now()
    elapsed = (end - start).total_seconds()
    logger.info(f"Proceso finalizado en {elapsed:.2f} s\n")

    logger.info("Archivos generados en:")
    for p in INTERIM_GEO_DIR.glob("*.shp"):
        print(f" - {p.relative_to(ROOT_DIR)}")
    print()

    return nodes_path, edges_path


if __name__ == "__main__":
    _, _ = process_extraction_roads_hmo()