"""
clean_atus.py

Filtra, Combina y limpa los archivos de accidentes de tránsito (ATUS) para
Hermosillo, Sonora. 

El diccionario de datos de referencia: raw/atus/diccionario_de_datos.xlxs

Guarda los resultados limpios en data/processed
"""

from config import ROOT_DIR, INTERIM_DIR, PROCESSED_DIR, get_logger
from extract_atus import ATUS_DIR

import re
from pathlib import Path
from datetime import datetime

import pandas as pd


# Paths
INTERIM_ATUS_DIR = INTERIM_DIR / "atus"
INTERIM_ATUS_DIR.mkdir(exist_ok=True)


# Logger
logger = get_logger(Path(__file__).name)


def get_all_csvs(base_path):
    return list(base_path.rglob("*.csv"))


def filter_hermosillo_records(csv_path):
    df = pd.read_csv(csv_path, encoding='latin1')
    df_hmo = df[
        (df['EDO'] == 26) & (df['MPIO'] == 30)
    ]
    filename = csv_path.stem

    # Encontrar el año en el nombre del archivo
    match = re.search(r'(\d{4})', filename) 
    year = match.group(1)
    
    outpath = INTERIM_ATUS_DIR / f"ATUS_HMO_{year}.csv"
    df_hmo.to_csv(outpath)
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

def decode_all(df):
    """
    Decodifica las columnas categóricas del DataFrame de acuerdo con los valores
    definidos en el diccionario de datos.
    """
    df = df.copy()

    df['diasemana'] = df['diasemana'].apply(decode_dia_semana)
    df['urbana'] = df['urbana'].apply(decode_zona_urbana)
    df['suburbana'] = df['suburbana'].apply(decode_zona_suburbana)
    df['tipaccid'] = df['tipaccid'].apply(decode_tipo_accidente)
    df['causaacci'] = df['causaacci'].apply(decode_causa_accidente)
    df['caparod'] = df['caparod'].apply(decode_capa_rodamiento)
    df['sexo'] = df['sexo'].apply(decode_sexo)
    df['aliento'] = df['aliento'].apply(decode_aliento)
    df['cinturon'] = df['cinturon'].apply(decode_cinturon)
    df['clase'] = df['clase'].apply(decode_clase_accidente)

    return df

def create_datetime(df):
    df["datetime"] = pd.to_datetime(
        df["anio"].astype(str) + "-" +
        df["mes"].astype(str).str.zfill(2) + "-" +
        df["dia"].astype(str).str.zfill(2) + " " +
        df["hora"].astype(str).str.zfill(2) + ":" +
        df["minutos"].astype(str).str.zfill(2),
        errors="coerce"
    )
    return df

def process_cleaning_atus(csv_paths=[]):    
    start = datetime.now()
    logger.info(f'Inicia el proceso de limpieza ATUS: ')

    if not csv_paths: 
        logger.info(f'No se proporcionaron rutas de archivos. Se cargarán todos los archivos CSV en {ATUS_DIR.relative_to(ROOT_DIR)}.')
        csv_paths = get_all_csvs(ATUS_DIR)
    
    # Filtrado
    paths_atus_hmo = filter_all_csvs(csv_paths)
    
    # Carga y concatenación de archivos
    dfs = [pd.read_csv(p, index_col=0) for p in paths_atus_hmo]
    df = pd.concat(dfs, ignore_index=True)

    # Normalización de nombres de columnas
    df.columns = df.columns.str.lower()
    
    # Eliminamos columnas redundantes
    df.drop(columns=["edo", "mpio"], inplace=True)

    # Combinamos fecha y hora en un solo campo datetime
    df = create_datetime(df)

    # Normalizacion de str types
    df[df.select_dtypes(include='object').columns] = df.select_dtypes(include='object').apply(lambda x: x.str.lower())

    # Decodificaciones
    df = decode_all(df)

    # Guardamos archivo en data/processed/atus_clean.csv
    clean_atus_path = PROCESSED_DIR / "atus_clean.csv"
    logger.info(f'Archivo limpio guardado en: {clean_atus_path.relative_to(ROOT_DIR)}')
    df.to_csv(clean_atus_path)

    end = datetime.now()
    elapsed = (end - start).total_seconds()
    logger.info(f'Proceso de limpieza ATUS completado en {elapsed:.2f} s')

    return clean_atus_path


if __name__ == '__main__': 
    process_cleaning_atus()
