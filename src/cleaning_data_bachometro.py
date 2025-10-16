import pandas as pd
import pathlib

def procesar_columna_fecha(df, col, month_map):
    """
    Procesa una columna de fecha en formato español a datetime de pandas.
    
    Convierte fechas en formato texto con meses en español (ej: '15 Enero 2023')
    a objetos datetime de pandas.
    
    Args:
        df (pd.DataFrame): DataFrame con la columna a procesar
        col (str): Nombre de la columna de fecha a procesar
        month_map (dict): Diccionario de mapeo de meses español → número
    
    Returns:
        pd.DataFrame: DataFrame con la columna de fecha convertida a datetime
    """
    # Máscara para filas válidas (no nulas)
    mask = df[col].notna()

    # Si no hay filas válidas, omite el procesamiento
    if mask.sum() == 0:
        return df

    # Convertir a string
    df.loc[mask, col] = df.loc[mask, col].astype(str)

    # Limpiar caracteres no alfanuméricos
    df.loc[mask, col] = df.loc[mask, col].str.replace(r'[^a-zA-Z0-9 ]', '', regex=True)

    # Reemplazar nombres de meses por números
    for month, num in month_map.items():
        df.loc[mask, col] = df.loc[mask, col].str.replace(month, str(num), regex=False)

    # Cambiar None por NA
    df[col] = df[col].replace({None: pd.NA})

    # Split en 3 columnas
    splitted = df[col].str.split(' ', expand=True)

    # Verifica si el split tiene exactamente 3 columnas
    if splitted.shape[1] != 3:
        #print(f"El split de '{col}' produjo {splitted.shape[1]} columnas en vez de 3")
        return df

    df[['month', 'day', 'year']] = splitted

    # Rellenar vacíos con "0"
    df['day'] = df['day'].fillna('0')
    df['month'] = df['month'].fillna('0')
    df['year'] = df['year'].fillna('0')

    # Unir a datetime
    df[col] = pd.to_datetime(df[['day', 'month', 'year']], errors='coerce')

    # Eliminar columnas auxiliares
    df = df.drop(columns=['day', 'month', 'year'])
    return df


def procesar_dataset(json_file_path, output_dir):
    """
    Procesa un archivo JSON de baches y lo guarda como CSV limpio.
    
    Args:
        json_file_path (str): Ruta al archivo JSON de entrada
        output_dir (str): Directorio donde guardar el CSV resultante
    
    Returns:
        pd.DataFrame: DataFrame procesado
    """
    try:
        # Cargar el archivo JSON
        df = pd.read_json(json_file_path)
        
        # Eliminar columnas no necesarias
        columnas_a_eliminar = [
            'descripcion', 'description', 'material', 
            'imagenes', 'date', 'neighborhoods', 'no_reparemos'
        ]
        
        # Eliminar solo las columnas que existen en el DataFrame
        columnas_existentes = [col for col in columnas_a_eliminar if col in df.columns]
        df = df.drop(columns=columnas_existentes)
        
        # Mapeo de meses en español a números
        month_map = { 
            'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 'Mayo': 5, 'Junio': 6,
            'Julio': 7, 'Agosto': 8, 'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12 
        }

        # Procesar columnas de fecha si existen
        if 'fecha_reporte' in df.columns:
            df = procesar_columna_fecha(df, 'fecha_reporte', month_map)
        
        if 'fecha_atencion' in df.columns:
            df = procesar_columna_fecha(df, 'fecha_atencion', month_map)

        # Crear carpeta processed si no existe
        pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generar nombre de archivo de salida
        archivo_entrada = pathlib.Path(json_file_path).stem  # ej: 'baches_2022'
        archivo_salida = f"{archivo_entrada}_limpio.csv"
        ruta_salida = pathlib.Path(output_dir) / archivo_salida
        
        # Exportar el DataFrame limpio a CSV
        df.to_csv(ruta_salida, index=False)
        print(f"Archivo CSV limpio creado: '{ruta_salida}'")
        
        return df
        
    except Exception as e:
        print(f"Error procesando {json_file_path}: {e}")
        return None


def main():
    """
    Función principal que procesa múltiples datasets de baches.
    """
    # Obtener el directorio actual del script
    script_dir = pathlib.Path(__file__).parent
    project_root = script_dir.parent  # Subir un nivel para llegar a la raíz del proyecto
    
    # Configuración de rutas RELATIVAS desde el script
    RAW_DIR = project_root / "data" / "raw"
    PROCESSED_DIR = project_root / "data" / "processed"
    
    print(f"Buscando datos en: {RAW_DIR.absolute()}")
    
    # Lista de datasets a procesar - usar los archivos que realmente existen
    datasets = [
        RAW_DIR / "baches_2021.json",
        RAW_DIR / "baches_2022.json",
        RAW_DIR / "baches_2023.json"
        # No incluir 2024 y 2025 si no existen
    ]
    
    print(f"Iniciando procesamiento de datasets...")
    print("=" * 60)
    
    # Procesar solo los archivos que existen
    archivos_procesados = 0
    for dataset_path in datasets:
        if dataset_path.exists():
            print(f"Procesando: {dataset_path.name}")
            procesar_dataset(dataset_path, PROCESSED_DIR)
            archivos_procesados += 1
        else:
            print(f"Archivo no encontrado: {dataset_path.name} - Saltando...")
    
    print(f"Procesamiento completado. Archivos procesados: {archivos_procesados}")


if __name__ == '__main__':
    main()