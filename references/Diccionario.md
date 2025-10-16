# Diccionario de Datos del Proyecto: Relacion_Baches_Accidentes_HMO

Este documento define las variables utilizadas en el análisis, su origen (API, archivo) y la unidad de medida después de la fase de limpieza (`data/processed`).

---

## 1. Datos Climáticos (Open-Meteo Archive API)

### Naturaleza del Origen

La fuente de datos climáticos es la **Open-Meteo Archive API**, que proporciona datos históricos de reanálisis meteorológico.

Los datos no provienen de una estación meteorológica física, sino de un **modelo de reanálisis** de alta resolución. Este modelo combina miles de observaciones históricas con modelos numéricos para generar un *dataset* completo y uniforme a nivel global.

* **Frecuencia:** Los datos se descargan en formato **horario** (una medición por hora).
* **Cobertura:** Los valores corresponden a la ubicación geográfica de Hermosillo.

### Variables del Dataset de Clima

### Variables del Dataset de Clima

### Variables del Dataset de Clima

| Nombre Final | Nombre de la API | Tipo de Dato | Unidad | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **fecha** | `date` | `datetime` | UTC Timestamp | Fecha y hora de la medición horaria (usado como índice). |
| **temperatura** | `temperature_2m` | `float` | °C | Temperatura del aire a 2 metros sobre la superficie (redondeado a 1 decimal). |
| **humedad** | `relative_humidity_2m` | `float` | % | Humedad relativa del aire a 2 metros sobre la superficie (redondeado a 1 decimal). |
| **precipitacion** | `precipitation` | `float` | mm | Lluvia, nieve u otras formas de precipitación total acumulada (redondeado a 1 decimal). |
| **velocidad_viento** | `wind_speed_10m` | `float` | km/h | Velocidad del viento medida a 10 metros sobre la superficie (redondeado a 1 decimal). |
| **nubosidad** | `cloud_cover` | `float` | % | Porcentaje total de cielo cubierto por nubes (redondeado a 1 decimal). |
| **codigo_clima** | `weather_code` | `int` | Código WMO | Código entero que describe las condiciones meteorológicas generales. **[Referencia WMO aquí](https://www.open-meteo.com/en/docs/archive-api#weather_code_wmo)** |
| **es_de_dia** | `is_day` | `bool` (Binario) | (0/1) | Indicador que determina si es de día (1) o de noche (0). |

---

## 2. Datos de Accidentes Viales (INEGI / ATUS)

Esta sección se completará una vez que se extraigan las variables específicas del *dataset* de INEGI (Accidentes de Tránsito Terrestre en Zonas Urbanas) y se aplique el *script* de limpieza.

| Nombre Final | Nombre de Origen | Tipo de Dato | Descripción |
| :--- | :--- | :--- | :--- |
| **[PENDIENTE]** | [Origen en INEGI] | [int/str] | [Descripción de la variable clave: fecha, gravedad, ubicación, etc.] |
| **[PENDIENTE]** | [Origen en INEGI] | [int/str] | [Ejemplo: Tipo de Accidente] |
| **[PENDIENTE]** | [Origen en INEGI] | [int/str] | [Ejemplo: Ubicación (Colonia o Tramo)] |

---

## 3. Datos de Reportes de Baches (Bachómetro)

### Naturaleza del Origen

La fuente de datos de baches es el **Bachómetro Municipal de Hermosillo**, un sistema implementado por el municipio para el reporte, seguimiento y atención de baches en la vía pública.

Los datos representan reportes ciudadanos verificados por el municipio y contienen información geográfica, temporal y descriptiva de cada bache reportado.

* **Frecuencia:** Los datos se actualizan en tiempo real según reportes ciudadanos.
* **Cobertura:** Todo el municipio de Hermosillo, Sonora.
* **Formato Original:** JSON a través de API web.

### Variables del Dataset de Baches

| Nombre Final | Nombre de Origen | Tipo de Dato | Descripción |
| :--- | :--- | :--- | :--- |
| **latitude** | `latitude` | float | Latitud geográfica del bache en sistema WGS84. |
| **longitude** | `longitude` | float | Longitud geográfica del bache en sistema WGS84. |
| **id** | `id` | int | Identificador único del reporte de bache en el sistema municipal. |
| **folio** | `folio` | float | Folio único del reporte municipal (puede contener decimales por formato de exportación). |
| **fecha_reporte** | `fecha_reporte` | date | Fecha en que se reportó el bache (formato YYYY-MM-DD). |
| **fecha_atencion** | `fecha_atencion` | date | Fecha en que el bache fue atendido (formato YYYY-MM-DD, puede estar vacío si no ha sido atendido). |
| **colonia** | `colonia` | str | Nombre de la colonia donde se ubica el bache. |
| **direccion** | `direccion` | str | Dirección específica del bache. |

**Notas sobre los datos de baches:**
- Las fechas de atención pueden estar vacías si el bache no ha sido atendido.
- Las coordenadas están en sistema WGS84 (latitud/longitud) y son precisas para análisis geoespacial.
- El campo `folio` puede contener valores decimales debido al formato de exportación del sistema municipal.
- Los datos incluyen reportes desde 2021 hasta la fecha actual.
