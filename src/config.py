from pathlib import Path

# Rutas base
ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
INTERIM_DIR = DATA_DIR / "interim"

def init_paths(): 
    for path in [DATA_DIR, RAW_DIR, PROCESSED_DIR, INTERIM_DIR]: 
        path.mkdir(parents=True, exist_ok=True)