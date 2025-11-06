"""
clean_atus.py

Filtra, combina y limpia los archivos de accidentes de tránsito (ATUS)
para Hermosillo, Sonora.

El diccionario de datos de referencia: raw/atus/diccionario_de_datos.xlsx

Guarda los resultados limpios en data/processed/atus/
"""

from config import ROOT_DIR, INTERIM_DIR, PROCESSED_DIR, get_logger
from extract_atus import ATUS_DIR
import re
from pathlib import Path
from datetime import datetime
import pandas as pd
import geopandas as gpd
from shapely.geometry import box, Point

# Paths
INTERIM_ATUS_DIR = INTERIM_DIR / "atus"
INTERIM_ATUS_DIR.mkdir(exist_ok=True)

PROCESSED_ATUS_DIR = PROCESSED_DIR / "atus"
PROCESSED_ATUS_DIR.mkdir(exist_ok=True)

# Logger
logger = get_logger(Path(__file__).name)


def get_all_csvs(base_path):
    return list(base_path.rglob("*.csv"))


def filter_hermosillo_records(csv_path):
    df = pd.read_csv(csv_path, encoding='latin1')
    df_hmo = df[(df['EDO'] == 26) & (df['MPIO'] == 30)]
    match = re.search(r'(\d{4})', csv_path.stem)
    year = match.group(1) if match else "xxxx"

    outpath = INTERIM_ATUS_DIR / f"ATUS_HMO_{year}.csv"
    df_hmo.to_csv(outpath, index=False)
    return outpath


def filter_all_csvs(csv_paths):
    paths_atus_hmo = []
    for csv_path in csv_paths:
        outpath = filter_hermosillo_records(csv_path)
        logger.info(f'Archivo {csv_path.relative_to(ROOT_DIR)} filtrado -> {outpath.relative_to(ROOT_DIR)}')
        paths_atus_hmo.append(outpath)
    return paths_atus_hmo


def decode_dia_semana(valor):
    """
    Convierte el valor numérico del campo DIASEMANA en su equivalente textual.
    """
    dias = {
        1: "lunes", 2: "martes", 3: "miércoles", 4: "jueves",
        5: "viernes", 6: "sábado", 7: "domingo"
    }
    return dias.get(valor)


def decode_zona_urbana(valor):
    """
    Decodifica el campo URBANA según las claves del diccionario de datos.
    """
    zonas = {0: "suburbana", 1: "intersección", 2: "no intersección"}
    return zonas.get(valor)


def decode_zona_suburbana(valor):
    """
    Decodifica el campo SUBURBANA según las claves del diccionario de datos.
    """
    zonas = {
        0: "urbana", 1: "camino rural",
        2: "carretera estatal", 3: "otro camino"
    }
    return zonas.get(valor)


def decode_tipo_accidente(valor):
    """
    Decodifica el campo TIPACCID (tipo de accidente) según el diccionario de datos.
    """
    tipos = {
        0: "certificado cero",
        1: "colisión con vehículo automotor",
        2: "atropellamiento",
        3: "colisión con animal",
        4: "colisión con objeto fijo",
        5: "volcadura",
        6: "caída de pasajero",
        7: "salida del camino",
        8: "incendio",
        9: "colisión con ferrocarril",
        10: "colisión con motocicleta",
        11: "colisión con ciclista",
        12: "otro"
    }
    return tipos.get(valor)


def decode_causa_accidente(valor):
    """
    Decodifica el campo CAUSAACCI (causa probable del accidente).
    """
    causas = {
        1: "conductor", 2: "peatón/pasajero",
        3: "falla del vehículo", 4: "mala condición del camino", 5: "otra"
    }
    return causas.get(valor)


def decode_capa_rodamiento(valor):
    """
    Decodifica el campo CAPAROD (tipo de superficie).
    """
    capas = {1: "pavimentada", 2: "no pavimentada"}
    return capas.get(valor)


def decode_sexo(valor):
    """
    Decodifica el campo SEXO del conductor presunto responsable.
    """
    sexos = {1: "se fugó", 2: "hombre", 3: "mujer"}
    return sexos.get(valor)


def decode_aliento(valor):
    """
    Decodifica el campo ALIENTO (presencia de aliento alcohólico).
    """
    aliento = {4: "sí", 5: "no", 6: "se ignora"}
    return aliento.get(valor)


def decode_cinturon(valor):
    """
    Decodifica el campo CINTURON (uso de cinturón de seguridad).
    """
    cinturon = {7: "sí", 8: "no", 9: "se ignora"}
    return cinturon.get(valor)


def decode_clase_accidente(valor):
    """
    Decodifica el campo CLASE (tipo de gravedad del accidente).
    """
    clases = {1: "fatal", 2: "no fatal", 3: "solo daños"}
    return clases.get(valor)


def decode_all(gdf):
    """
    Decodifica las columnas categóricas del DataFrame de acuerdo con los valores
    definidos en el diccionario de datos.
    """
    gdf = gdf.copy()

    gdf['diasemana'] = gdf['diasemana'].apply(decode_dia_semana)
    gdf['urbana'] = gdf['urbana'].apply(decode_zona_urbana)
    gdf['suburbana'] = gdf['suburbana'].apply(decode_zona_suburbana)
    gdf['tipaccid'] = gdf['tipaccid'].apply(decode_tipo_accidente)
    gdf['causaacci'] = gdf['causaacci'].apply(decode_causa_accidente)
    gdf['caparod'] = gdf['caparod'].apply(decode_capa_rodamiento)
    gdf['sexo'] = gdf['sexo'].apply(decode_sexo)
    gdf['aliento'] = gdf['aliento'].apply(decode_aliento)
    gdf['cinturon'] = gdf['cinturon'].apply(decode_cinturon)
    gdf['clase'] = gdf['clase'].apply(decode_clase_accidente)

    return gdf


def create_datetime(gdf):
    gdf["datetime"] = pd.to_datetime(
        gdf["anio"].astype(str) + "-" +
        gdf["mes"].astype(str).str.zfill(2) + "-" +
        gdf["dia"].astype(str).str.zfill(2) + " " +
        gdf["hora"].astype(str).str.zfill(2) + ":" +
        gdf["minutos"].astype(str).str.zfill(2),
        errors="coerce"
    )
    return gdf


def filter_urban_data(gdf):
    x_min, x_max = -111.075, -110.900
    y_min, y_max = 28.900, 29.200
    bbox = box(x_min, y_min, x_max, y_max)

    filtered = gdf[gdf.intersects(bbox)]
    filtered.to_file(INTERIM_ATUS_DIR / "atus_hmo_urb.geojson", driver="GeoJSON")
    logger.info(f'Archivo filtrado guardado en: {INTERIM_ATUS_DIR.relative_to(ROOT_DIR)}')
    return filtered


def process_cleaning_atus(csv_paths=None):
    start = datetime.now()
    logger.info('Inicia el proceso de limpieza ATUS')

    if not csv_paths:
        csv_paths = get_all_csvs(ATUS_DIR)
        logger.info(f'Se cargarán todos los archivos CSV en {ATUS_DIR.relative_to(ROOT_DIR)}')

    paths_atus_hmo = filter_all_csvs(csv_paths)

    # Carga y concatenación
    dfs = [pd.read_csv(p) for p in paths_atus_hmo]
    gdf = pd.concat(dfs, ignore_index=True)

    gdf.columns = gdf.columns.str.lower()
    gdf.drop(columns=["edo", "mpio"], inplace=True, errors="ignore")

    # Crear geometría
    lon_col = [c for c in gdf.columns if 'lon' in c][0]
    lat_col = [c for c in gdf.columns if 'lat' in c][0]
    gdf = gpd.GeoDataFrame(
        gdf,
        geometry=gpd.points_from_xy(gdf[lon_col], gdf[lat_col]),
        crs="EPSG:4326"
    )

    # Filtrado espacial
    gdf = filter_urban_data(gdf)

    # Campos derivados
    gdf = create_datetime(gdf)
    gdf = decode_all(gdf)

    # Guardado
    clean_csv_path = PROCESSED_ATUS_DIR / "atus_clean.csv"
    clean_geojson_path = PROCESSED_ATUS_DIR / "atus_clean.geojson"

    gdf.to_csv(clean_csv_path, index=False)
    gdf.to_file(clean_geojson_path, driver="GeoJSON")

    elapsed = (datetime.now() - start).total_seconds()
    logger.info(f'Proceso de limpieza ATUS completado en {elapsed:.2f} s')
    logger.info(f'Archivos guardados en {PROCESSED_ATUS_DIR.relative_to(ROOT_DIR)}')

    return clean_csv_path


if __name__ == '__main__': 
    process_cleaning_atus()
