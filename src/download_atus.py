"""
download_atus.py

Descarga los archivos ZIP del conjunto de datos:
Accidentes de Tránsito Terrestre en Zonas Urbanas y Suburbanas (ATUS)
publicados por el INEGI.

Uso:
    python download_atus.py

Descarga los archivos correspondientes a los años 2021–2023 en paralelo,
valida su integridad (ZIP válido) y los guarda en data/raw/atus.
"""


from config import ROOT_DIR, RAW_DIR, get_logger
from utils import download_zip

from itertools import repeat
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor


# Paths
ATUS_DIR = RAW_DIR / "atus"
ATUS_DIR.mkdir(exist_ok=True)


# logger
logger = get_logger(Path(__file__).name)


# URL's
URL_2021 = r"https://www.inegi.org.mx/contenidos/programas/accidentes/datosabiertos/atus_2021_shp.zip"
URL_2022 = r"https://www.inegi.org.mx/contenidos/programas/accidentes/datosabiertos/atus_2022_shp.zip"
URL_2023 = r"https://www.inegi.org.mx/contenidos/programas/accidentes/datosabiertos/atus_2023_shp.zip"


def shoot_parallel_download(zip_urls, downloader=download_zip):
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(downloader, zip_urls, repeat(ATUS_DIR)))
    return results

def generate_documentation_atus():
    doc_content = f"""
# DESCRIPCIÓN DE FUENTE DE DATOS - ATUS (Accidentes de Tránsito)

Fuente
- Nombre: INEGI - Accidentes de Tránsito Terrestre en Zonas Urbanas y Suburbanas (ATUS)
- Enlace: [INEGI - ATUS](https://www.inegi.org.mx/programas/accidentes/#Datos_abiertos)
- Fecha de descarga: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- Cobertura temporal: 2021–2023
- Cobertura geográfica: Hermosillo, Sonora
- Frecuencia de actualización: Anual
- Formato de los datos: ZIP (archivos SHP y CSV incluidos)

Descripción general
    El conjunto ATUS contiene información sobre accidentes de tránsito registrados
    en zonas urbanas y suburbanas del país. Cada registro representa un accidente e
    incluye información sobre la ubicación, causas probables, condiciones del camino
    y características del conductor.

Variables principales
- anio, mes, dia, hora, minutos: Fecha y hora del accidente.
- diasemana: Día de la semana del evento.
- urbana / suburbana: Tipo de zona donde ocurrió el accidente.
- tipaccid: Tipo de accidente (colisión, atropellamiento, volcadura, etc.).
- causaacci: Causa probable del accidente.
- caparod: Tipo de superficie del camino.
- sexo, aliento, cinturon: Características del conductor.
- clase: Gravedad del accidente.
"""
    doc_path = RAW_DIR / "documentacion_atus.txt"
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(doc_content)

    logger.info(f"Documentación de fuentes generada en: {doc_path}")


def download_atus():
    zip_urls = [URL_2021, URL_2022, URL_2023]
    start = datetime.now()
    logger.info(f'Inicia proceso de descarga (ATUS):')

    zip_paths = shoot_parallel_download(zip_urls)

    end = datetime.now()
    elapsed = (end - start).total_seconds()
    print()
    logger.info(f'Proceso de descarga finalizado en {elapsed:.2f} s')

    generate_documentation_atus()

    logger.info("Archivos descargados:")
    for z in zip_paths:
        print(f" - {z.relative_to(ROOT_DIR)}")
    
    return zip_paths
 

if __name__ == '__main__': 
    download_atus()
