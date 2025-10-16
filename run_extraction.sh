#!/bin/bash

# Ejecuta todos los scripts de extracción en src
python src/extract_atus.py
python src/extract_colonias.py
python src/extract_vialidades.py
python src/extract_bachometro.py