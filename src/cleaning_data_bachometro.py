import pandas as pd


def procesar_columna_fecha(df, col, month_map):
    # Máscara para filas válidas (no nulas)
    mask = df[col].notna()
    #print(f"[DEBUG] Filas válidas para '{col}': {mask.sum()} de {len(df)}")

    # Si no hay filas válidas, omite el procesamiento
    if mask.sum() == 0:
        #print(f"[DEBUG] No hay filas válidas para '{col}'. Se omite el procesamiento.")
        return df

    # Convertir a string
    df.loc[mask, col] = df.loc[mask, col].astype(str)
    #print(f"[DEBUG] Tipos tras astype(str): {df.loc[mask, col].apply(type).unique()}")

    # Limpiar caracteres no alfanuméricos
    df.loc[mask, col] = df.loc[mask, col].str.replace(r'[^a-zA-Z0-9 ]', '', regex=True)

    # Reemplazar nombres de meses por números
    for month, num in month_map.items():
        df.loc[mask, col] = df.loc[mask, col].str.replace(month, str(num), regex=False)

    # Cambiar None por NA
    df[col] = df[col].replace({None: pd.NA})

    # DEBUG: Ver ejemplos antes del split
    #print(f"[DEBUG] Ejemplo de valores antes del split en '{col}':")
    #print(df.loc[mask, col].head(10).to_list())

    # Split en 3 columnas
    splitted = df[col].str.split(' ', expand=True)
    #print(f"[DEBUG] Shape del split: {splitted.shape}")
    #print(f"[DEBUG] Primeras filas del split:\n{splitted.head(10)}")

    # Verifica si el split tiene exactamente 3 columnas
    if splitted.shape[1] != 3:
        #print(f"[ERROR] El split produjo {splitted.shape[1]} columnas en vez de 3. Revisa el formato de las fechas en '{col}'.")
        return df  # O puedes lanzar un error si prefieres: raise ValueError(...)

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


# Cargar el archivo JSON
df = pd.read_json("../../data/raw/baches_2022.json")

df = df.drop(columns=['descripcion'])
df = df.drop(columns=['description'])
df = df.drop(columns=['material'])
df = df.drop(columns=['imagenes'])
df = df.drop(columns=['date'])
df = df.drop(columns=['neighborhoods'])
df = df.drop(columns=['no_reparemos'])  

#Mappeando meses del año a numeros
month_map = { 'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 'Mayo': 5, 'Junio': 6,
              'Julio': 7, 'Agosto': 8, 'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12 }

# Procesando las columnas de fecha
df = procesar_columna_fecha(df, 'fecha_reporte', month_map)
df = procesar_columna_fecha(df, 'fecha_atencion', month_map)

