#!/bin/bash

# Ejecuta todos los scripts de extracción en src
python src/download_atus.py
python src/extract_atus.py
python src/download_colonias.py
python src/download_clima.py
python src/extract_colonias.py
python src/extract_vialidades.py
python src/extract_bachometro.py
python src/cleaning_data_bachometro.py
