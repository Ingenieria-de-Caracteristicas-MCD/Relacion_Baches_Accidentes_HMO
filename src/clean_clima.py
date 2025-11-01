import pandas as pd
from pathlib import Path
import sys

# ----------------------------------------------------------------------
# A. ARREGLO DE PATH PARA IMPORTAR MÓDULOS DEL PROYECTO (SRC)
# Nota: Esta sección es crucial para que el script encuentre 'src.config'.
# Se asume que el script se ejecuta desde la raíz del proyecto o un nivel inferior.
# ----------------------------------------------------------------------
current_dir = Path(__file__).resolve().parent if '__file__' in locals() else Path.cwd()
project_root = current_dir

# Buscamos la raíz del proyecto (donde está la carpeta 'src')
for _ in range(5):
    if (project_root / 'src').is_dir():
        break
    project_root = project_root.parent
else:
    raise FileNotFoundError("No se pudo encontrar la carpeta 'src'. Verifica la estructura del proyecto.")

# Añadir la raíz del proyecto al path de Python si no está
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# ----------------------------------------------------------------------

# B. IMPORTAR HERRAMIENTAS Y CONFIGURACIÓN
# Ahora importamos PROCESSED_DIR en lugar de INTERIM_DIR
from src.config import RAW_DIR, PROCESSED_DIR, get_logger, init_paths

# Inicializar logger
logger = get_logger(__name__)

# Asegurar que las carpetas existan
init_paths()

# Definir la ruta del archivo a cargar y guardar
INPUT_FILE = RAW_DIR / "clima_hermosillo.csv"
OUTPUT_FILE = PROCESSED_DIR / "clima_final_processed.csv"

print("Rutas, logger y PATH inicializados correctamente para el procesamiento.")
# ----------------------------------------------------------------------
# C. LÓGICA DE CARGA Y LIMPIEZA DE DATOS
# ----------------------------------------------------------------------

df_clima = pd.DataFrame()

# 1. Cargar el archivo CSV
try:
    df_clima = pd.read_csv(INPUT_FILE)
    print(f"Dataset cargado exitosamente. Filas: {len(df_clima)}, Columnas: {len(df_clima.columns)}")

except FileNotFoundError:
    logger.error(f"ERROR: El archivo no fue encontrado en la ruta: {INPUT_FILE}")
    logger.error("Asegúrate de haber ejecutado previamente el script 'download_clima.py'.")
except Exception as e:
    logger.error(f"Error al cargar el CSV: {e}")


if not df_clima.empty:

    # 2. Conversión a Datetime e Índice
    df_clima['date'] = pd.to_datetime(df_clima['date'])
    df_clima = df_clima.set_index('date')
    print("Columna 'date' convertida a tipo datetime y establecida como índice.")

    # 3. Revisión e Imputación de Nulos (ffill)
    nulos_por_columna = df_clima.isnull().sum()
    nulos_existentes = nulos_por_columna[nulos_por_columna > 0]

    if not nulos_existentes.empty:
        logger.warning("Se encontraron nulos. Aplicando imputación 'ffill'.")
        df_clima.fillna(method='ffill', inplace=True)
        print(f"Nulos restantes: {df_clima.isnull().sum().sum()}")
    else:
        print("No se detectaron valores nulos. La integridad es buena.")

    # 4. Definición del mapeo y Renombrar columnas
    columnas_renombrar = {
        'temperature_2m': 'temperatura',
        'precipitation': 'precipitacion',
        'weather_code': 'codigo_clima',
        'is_day': 'es_de_dia',
        'relative_humidity_2m': 'humedad',
        'cloud_cover': 'nubosidad',
        'wind_speed_10m': 'velocidad_viento'
    }
    df_clima.rename(columns=columnas_renombrar, inplace=True)
    print("Columnas renombradas a español.")

    # 5. Redondear valores numéricos
    columnas_a_redondear = ['temperatura', 'precipitacion', 'humedad', 'nubosidad', 'velocidad_viento']

    for col in columnas_a_redondear:
        if col in df_clima.columns:
            df_clima[col] = df_clima[col].round(1)

    print("Valores numéricos redondeados a un decimal para estandarización.")

    # 6. Guardar el DataFrame PROCESADO
    try:
        df_clima.to_csv(OUTPUT_FILE)
        print("\n--- Inspección Final ---")
        print(f"Dataset de clima PROCESADO guardado exitosamente en: {OUTPUT_FILE}")
        print(f"Columnas finales y dtypes:\n{df_clima.dtypes}")
    except Exception as e:
        logger.error(f"Error al guardar el archivo: {e}")

else:
    logger.error("Procesamiento finalizado sin guardar archivo porque el DataFrame está vacío.")