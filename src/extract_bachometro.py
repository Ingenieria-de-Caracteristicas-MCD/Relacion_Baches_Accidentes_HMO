"""
Script para extraer datos del sistema Bachómetro del municipio de Hermosillo.

Este módulo permite scrapear información sobre reportes de baches incluyendo
su ubicación, estado, fechas de reporte/atención, materiales utilizados e imágenes.
Los datos se obtienen mediante requests a la API del sitio web y se procesan
con BeautifulSoup para el parsing de HTML.
"""

import re
import json
from pathlib import Path
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Configuración de rutas para almacenamiento de datos
ROOT = Path().resolve()  # Directorio raíz del proyecto
DATA = ROOT / "data"     # Directorio para datos procesados
RAW = DATA / "raw"       # Directorio para datos crudos sin procesar

# URL base del sitio del Bachómetro
BASE_URL = "https://bachometro.hermosillo.gob.mx/"

# Configuración del archivo de log
LOG_FILE = RAW / "info_descarga_datos_bachometro.txt"

def crear_log_descarga(years, total_registros):
    """
    Crea un archivo de log con información descriptiva de los datos descargados.
    
    Args:
        years (list): Lista de años descargados
        total_registros (int): Número total de registros obtenidos
    """
    fecha_descarga = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    contenido_log = f"""
INFORMACIÓN DE DESCARGA - SISTEMA BACHÓMETRO HERMOSILLO
========================================================

FECHA DE DESCARGA: {fecha_descarga}
AÑOS DESCARGADOS: {', '.join(map(str, years))}
TOTAL DE REGISTROS OBTENIDOS: {total_registros}

DESCRIPCIÓN DE LAS FUENTES DE DATOS
====================================

FUENTE PRINCIPAL: Bachómetro Municipal de Hermosillo
URL: https://bachometro.hermosillo.gob.mx/

NATURALEZA DE LOS DATOS:
------------------------
El Bachómetro es un sistema implementado por el municipio de Hermosillo, Sonora,
para el reporte, seguimiento y atención de baches en la vía pública. Los datos
incluyen:

1. DATOS GEOGRÁFICOS:
   - Coordenadas de ubicación (latitud, longitud)
   - Colonia y dirección específica
   - Zona de la ciudad

2. DATOS TEMPORALES:
   - Fecha de reporte del bache por ciudadanos
   - Fecha de atención por parte del municipio
   - Año de registro en el sistema

3. DATOS DESCRIPTIVOS:
   - Número de reporte (#ReparemosHermosillo)
   - Folio único de identificación
   - Material utilizado en la reparación
   - Descripción del problema reportado
   - Imágenes del bache (antes/durante/después de la reparación)

4. METADATOS TÉCNICOS:
   - ID único del registro
   - Estado del reporte
   - Información de categorización

ENLACES Y REFERENCIAS:
----------------------
- Sitio oficial: https://bachometro.hermosillo.gob.mx/
- Aplicación móvil: Disponible en tiendas de aplicaciones
- Programa #ReparemosHermosillo: Iniciativa ciudadana-municipal

PROPÓSITO DEL DATASET:
----------------------
Este dataset permite analizar:
- Patrones temporales y espaciales de baches en Hermosillo
- Eficiencia en los tiempos de respuesta del municipio
- Distribución geográfica de problemas de infraestructura vial
- Estacionalidad en la aparición de baches
- Impacto de factores climáticos en la infraestructura vial

ESTRUCTURA DE ARCHIVOS:
-----------------------
- Formato: JSON para datos crudos, CSV para datos procesados
- Codificación: UTF-8
- Frecuencia de actualización: Diaria (según reportes ciudadanos)
- Periodo histórico disponible: Desde 2021 hasta actualidad

NOTAS TÉCNICAS:
---------------
- Los datos se obtienen mediante scraping de la API pública del sistema
- Se utiliza token CSRF para autenticación en las peticiones
- Las imágenes están almacenadas en servidores municipales
- Coordenadas en sistema WGS84 (lat/lon)

CONTACTO Y MÁS INFORMACIÓN:
---------------------------
- Municipio de Hermosillo: https://hermosillo.gob.mx/
- Dirección de Obras Públicas: Responsable del mantenimiento vial
- App #ReparemosHermosillo: Para reportar baches desde móviles

========================================================
LOG DE DESCARGA COMPLETADO: {fecha_descarga}
"""
    
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write(contenido_log)
    
    print(f"Archivo de log creado: {LOG_FILE}")

def actualizar_log_progreso(year, registros_year, estado="completado"):
    """
    Actualiza el log con el progreso de descarga por año.
    
    Args:
        year (int): Año siendo procesado
        registros_year (int): Número de registros obtenidos para el año
        estado (str): Estado del proceso ('completado', 'error', 'en_progreso')
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        if estado == "en_progreso":
            f.write(f"\n[{timestamp}] INICIANDO descarga para año {year}\n")
        elif estado == "completado":
            f.write(f"[{timestamp}] COMPLETADO año {year}: {registros_year} registros\n")
        elif estado == "error":
            f.write(f"[{timestamp}] ERROR en año {year}: 0 registros\n")

class Bachometro:
    """
    Cliente para interactuar con la API del Bachómetro de Hermosillo.
    
    Maneja la autenticación, sesiones y extracción de datos sobre baches.
    """
    
    def __init__(self):
        """Inicializa el cliente con una sesión persistente y token CSRF."""
        self.session = requests.Session()
        self.csrf_token = None
        self._init_session()
    
    def _init_session(self):
        """
        Inicializa la sesión obteniendo el token CSRF necesario para las peticiones.
        
        Realiza una petición inicial a la página principal y extrae el token
        CSRF desde las meta etiquetas del HTML.
        """
        r = self.session.get(BASE_URL)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        self.csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']

    def _headers(self):
        """
        Genera los headers HTTP necesarios para las peticiones a la API.
        
        Returns:
            dict: Headers con User-Agent, tokens CSRF y tipos de contenido aceptados.
        """
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-TOKEN': self.csrf_token,
            'Referer': BASE_URL,
        }

    def get_baches(self, year):
        """
        Obtiene la lista de baches reportados para un año específico.
        
        Args:
            year (int): Año del cual obtener los reportes de baches.
            
        Returns:
            list: Lista de diccionarios con información básica de cada bache.
        """
        url = BASE_URL + "mapa/ajax"
        r = self.session.get(url, headers=self._headers(), params={'year': year})
        r.raise_for_status()
        return r.json()

    def get_bache_details(self, bache_id: int):
        """
        Obtiene los detalles específicos de un bache mediante su ID.
        
        Args:
            bache_id (int): Identificador único del bache.
            
        Returns:
            str: HTML con la información detallada del bache.
        """
        url = BASE_URL + "mapa/bache/ajax"
        r = self.session.post(url, headers=self._headers(), data={'id': bache_id})
        r.raise_for_status()
        return r.text
    
    def get_full_dataset(self, year, parser_func):
        """
        Obtiene el dataset completo de baches para un año, combinando información
        básica con detalles específicos de cada reporte.
        
        Args:
            year (int): Año del cual obtener los datos.
            parser_func (function): Función para parsear el HTML de detalles.
            
        Returns:
            list: Lista de diccionarios con información completa de cada bache.
        """
        full_data = []
        baches = self.get_baches(year)
        
        # Actualizar log con progreso
        actualizar_log_progreso(year, len(baches), "en_progreso")
        
        i = 0
        for b in baches: 
            bache_id = b.get('id')
            try: 
                # Obtiene HTML con detalles del bache
                html = self.get_bache_details(bache_id)
                # Parsea el HTML para extraer información estructurada
                details = parser_func(html)

                # Combina información básica con detalles específicos
                combined = {**b, **details}
                full_data.append(combined)
                i += 1

            except requests.HTTPError as e: 
                print(f"Error al obtener los detalles de ID: {bache_id}")
                print(e)
                continue
        
        return full_data

def parse_bache_details(html):
    """
    Parsea el HTML de detalles de un bache para extraer información estructurada.
    
    Args:
        html (str): Contenido HTML con los detalles del bache.
        
    Returns:
        dict: Diccionario con toda la información parseada del bache.
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Estructura base con todas las claves esperadas
    data = {
        'no_reparemos': None,    # Número de reporte en el sistema #ReparemosHermosillo
        'folio': None,           # Folio único del reporte
        'fecha_reporte': None,   # Fecha en que se reportó el bache
        'fecha_atencion': None,  # Fecha en que se atendió el bache
        'material': None,        # Material utilizado en la reparación
        'colonia': None,         # Colonia donde se ubica el bache
        'direccion': None,       # Dirección específica del bache
        'descripcion': None,     # Descripción del problema
        'imagenes': [],          # URLs de imágenes del bache
    }

    # Encabezado principal (No. #ReparemosHermosillo)
    header = soup.find('h5', id='potholeModalLabel')
    if header:
        header_text = header.get_text(' ', strip=True)
        no_reparemos = re.search(r'No\. ([\d/]+)', header_text)
        if no_reparemos:
            data['no_reparemos'] = no_reparemos.group(1)

        folio = header.find_next('span', class_='fw-400')
        if folio:
            data['folio'] = folio.get_text(strip=True)

    # Fechas - Extrae fechas de reporte y atención
    fecha_reporte = soup.find('strong', string=lambda s: s and 'Reporte' in s)
    if fecha_reporte and fecha_reporte.next_sibling:
        data['fecha_reporte'] = fecha_reporte.next_sibling.strip()

    fecha_atencion = soup.find('strong', string=lambda s: s and 'Atención' in s)
    if fecha_atencion and fecha_atencion.next_sibling:
        data['fecha_atencion'] = fecha_atencion.next_sibling.strip()

    # Material - Tipo de material usado en la reparación
    material = soup.find('strong', string=lambda s: s and 'Material' in s)
    if material:
        span = material.find_next('span')
        if span:
            data['material'] = span.get_text(strip=True)

    # Colonia - Ubicación por colonia
    colonia = soup.find('strong', string=lambda s: s and 'Colonia' in s)
    if colonia:
        data['colonia'] = (
            colonia.parent.get_text(strip=True).replace('Colonias:', '').strip()
        )

    # Dirección - Ubicación específica
    direccion = soup.find('strong', string=lambda s: s and 'Dirección' in s)
    if direccion:
        data['direccion'] = (
            direccion.parent.get_text(strip=True).replace('Dirección:', '').strip()
        )

    # Descripción - Detalles adicionales del reporte
    descripcion = soup.find('strong', string=lambda s: s and 'Descripción' in s)
    if descripcion:
        data['descripcion'] = (
            descripcion.parent.get_text(strip=True).replace('Descripción:', '').strip()
        )

    # Imágenes - Extrae todas las URLs de imágenes del bache
    imgs = soup.find_all('img', src=True)
    if imgs:
        data['imagenes'] = [img['src'] for img in imgs]

    return data


def get_available_years():
    """
    Obtiene los años disponibles con datos en el sistema Bachómetro.
    
    Realiza scraping de los botones de año en la interfaz del mapa.
    
    Returns:
        list: Lista de años disponibles como enteros.
    """
    try: 
        r = requests.get(BASE_URL)
        soup = BeautifulSoup(r.text, features='html.parser')
        # Encuentra todos los botones de selección de año
        year_buttons = soup.select('#map_slider button.btnYear')
        available_years = [int(btn['id']) for btn in year_buttons]
        return available_years
    
    except requests.HTTPError as e: 
        print(e)
        return []


def main(years=None):
    """
    Función principal que orquesta la extracción de datos del Bachómetro.
    
    Args:
        years (list, optional): Lista de años a procesar. Si es None, 
                               obtiene todos los años disponibles.
    """
    # Si no se especifican años, obtiene los disponibles automáticamente
    if years is None: 
        years = get_available_years()

    client = Bachometro()

    # Crea directorio de salida si no existe
    output_dir = RAW 
    output_dir.mkdir(exist_ok=True, parents=True)

    total_registros = 0
    años_procesados = []

    # Procesa cada año solicitado
    for year in years: 
        print(f'\nObteniendo datos del año {year}...')
        dataset = client.get_full_dataset(year, parse_bache_details)

        if not dataset: 
            print(f'Error al obtener los datos del año {year}, siguiente...')
            actualizar_log_progreso(year, 0, "error")
            continue
        
        # Guarda los datos en archivo JSON
        output_file = output_dir / f"baches_{year}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)        
        
        print(f'Datos guardados en: {output_file.relative_to(ROOT)}')
        
        # Actualizar contadores para el log
        total_registros += len(dataset)
        años_procesados.append(year)
        actualizar_log_progreso(year, len(dataset), "completado")
    
    # Crear archivo de log final con toda la información
    crear_log_descarga(años_procesados, total_registros)
    
    print(f'\nProceso completado. Total de registros: {total_registros}')
    print(f'Log de descarga guardado en: {LOG_FILE}')

if __name__ == '__main__':
    # Ejecuta el proceso para los años 2021-2025
    main([2021, 2022, 2023, 2024, 2025])