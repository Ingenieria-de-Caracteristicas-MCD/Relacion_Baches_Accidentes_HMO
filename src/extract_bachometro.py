import re
import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup


ROOT = Path().resolve()
DATA = ROOT / "data"
RAW = DATA / "raw"

BASE_URL = "https://bachometro.hermosillo.gob.mx/"

class Bachometro:
    def __init__(self):
        self.session = requests.Session()
        self.csrf_token = None
        self._init_session()
    
    def _init_session(self):
        r = self.session.get(BASE_URL)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        self.csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']

    def _headers(self):
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-TOKEN': self.csrf_token,
            'Referer': BASE_URL,
        }

    def get_baches(self, year):
        url = BASE_URL + "mapa/ajax"
        r = self.session.get(url, headers=self._headers(), params={'year': year})
        r.raise_for_status()
        return r.json()

    def get_bache_details(self, bache_id: int):
        url = BASE_URL + "mapa/bache/ajax"
        r = self.session.post(url, headers=self._headers(), data={'id': bache_id})
        r.raise_for_status()
        return r.text
    
    def get_full_dataset(self, year, parser_func): 
        full_data = []
        baches = self.get_baches(year)
        # print('trol: ', baches[0])  # OK
        i = 0
        for b in baches: 
            bache_id = b.get('id')
            # print('trol', bache_id)  # OK
            try: 
                html = self.get_bache_details(bache_id)
                details = parser_func(html)

                # bache actual + detalles
                combined = {**b, **details}
                # print('trol', combined)  OK 
                full_data.append(combined)
                i +=1

            except requests.HTTPError as e: 
                print(f"Error al ibener los detalles de ID: {bache_id}")
                print(e)
                continue
        
        return full_data

def parse_bache_details(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Estructura base con todas las claves esperadas
    data = {
        'no_reparemos': None,
        'folio': None,
        'fecha_reporte': None,
        'fecha_atencion': None,
        'material': None,
        'colonia': None,
        'direccion': None,
        'descripcion': None,
        'imagenes': [],
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

    # Fechas
    fecha_reporte = soup.find('strong', string=lambda s: s and 'Reporte' in s)
    if fecha_reporte and fecha_reporte.next_sibling:
        data['fecha_reporte'] = fecha_reporte.next_sibling.strip()

    fecha_atencion = soup.find('strong', string=lambda s: s and 'Atención' in s)
    if fecha_atencion and fecha_atencion.next_sibling:
        data['fecha_atencion'] = fecha_atencion.next_sibling.strip()

    # Material
    material = soup.find('strong', string=lambda s: s and 'Material' in s)
    if material:
        span = material.find_next('span')
        if span:
            data['material'] = span.get_text(strip=True)

    # Colonia
    colonia = soup.find('strong', string=lambda s: s and 'Colonia' in s)
    if colonia:
        data['colonia'] = (
            colonia.parent.get_text(strip=True).replace('Colonias:', '').strip()
        )

    # Dirección
    direccion = soup.find('strong', string=lambda s: s and 'Dirección' in s)
    if direccion:
        data['direccion'] = (
            direccion.parent.get_text(strip=True).replace('Dirección:', '').strip()
        )

    # Descripción
    descripcion = soup.find('strong', string=lambda s: s and 'Descripción' in s)
    if descripcion:
        data['descripcion'] = (
            descripcion.parent.get_text(strip=True).replace('Descripción:', '').strip()
        )

    # Imágenes
    imgs = soup.find_all('img', src=True)
    if imgs:
        data['imagenes'] = [img['src'] for img in imgs]

    return data


def get_available_years(): 
    try: 
        r = requests.get(BASE_URL)
        soup = BeautifulSoup(r.text, features='html.parser')
        year_buttons = soup.select('#map_slider button.btnYear')
        available_years = [int(btn['id']) for btn in year_buttons]
        return available_years
    
    except requests.HTTPError as e: 
        print(e)
        return []


def main(years=None): 

    if years is None: 
        years = get_available_years()

    client = Bachometro()

    output_dir = RAW 
    output_dir.mkdir(exist_ok=True, parents=True)

    for year in years: 
        print(f'\nObteniendo datos del año {year}...')
        dataset = client.get_full_dataset(year, parse_bache_details)

        if not dataset: 
            print(f'Error al obtener los datos del año {year}, siguiente...')
            continue
        
        output_file = output_dir / f"baches_{year}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2)        
        
        print(f'Datos guardatos en: {output_file.relative_to(ROOT)}')
    
    print('\nProceso completado. ')

if __name__ == '__main__':
    main([2022])  # OK
    # main([2021, 2022, 2023])  OK
    # main()  # OK