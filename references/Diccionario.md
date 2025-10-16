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

| Nombre Final | Nombre de la API | Unidad | Descripción |
| :--- | :--- | :--- | :--- |
| **fecha** | `date` | UTC Timestamp | Fecha y hora de la medición horaria. |
| **temperatura** | `temperature_2m` | °C | Temperatura del aire a 2 metros sobre la superficie (redondeado a 1 decimal). |
| **humedad** | `relative_humidity_2m` | % | Humedad relativa del aire a 2 metros sobre la superficie (redondeado a 1 decimal). |
| **precipitacion** | `precipitation` | mm | Lluvia, nieve u otras formas de precipitación total acumulada (redondeado a 1 decimal). |
| **velocidad_viento** | `wind_speed_10m` | km/h | Velocidad del viento medida a 10 metros sobre la superficie (redondeado a 1 decimal). |
| **nubosidad** | `cloud_cover` | % | Porcentaje total de cielo cubierto por nubes (redondeado a 1 decimal). |
| **codigo_clima** | `weather_code` | Código WMO | Código que describe las condiciones meteorológicas generales. |
| **es_de_dia** | `is_day` | Binario (0/1) | Indicador que determina si es de día (1) o de noche (0). |

---

## 2. Accidentes de Tránsito (ATUS)


Los datos originales provienen del INEGI y fueron procesados y decodificados conforme al **diccionario de datos oficial** ubicado en `raw/atus/diccionario_de_datos.xlsx`.

### Naturaleza del Origen

* **Fuente:** INEGI — Accidentes de Tránsito Terrestre en Zonas Urbanas y Suburbanas (ATUS)
* **Cobertura:** Hermosillo, Sonora
* **Frecuencia:** Registro individual de accidentes
* **Periodo:** 2021–2023
* **Formato final:** CSV (`data/processed/atus_2021-2023_clean.csv`)

Durante la limpieza se realizaron las siguientes transformaciones:

* Estandarización de nombres de columnas a minúsculas.
* Eliminación de columnas redundantes (`edo`, `mpio`).
* Creación de una columna combinada `datetime`.
* Conversión de todas las variables categóricas numéricas a texto legible mediante funciones `decode_*`.
* Normalización de texto (`lowercase`).

### Variables del Dataset Limpio

| Nombre Final              | Tipo de Dato | Descripción                                                                                | Transformación Aplicada                     |
| :------------------------ | :----------- | :----------------------------------------------------------------------------------------- | :------------------------------------------ |
| **datetime**              | datetime     | Fecha y hora completa del accidente (a partir de `anio`, `mes`, `dia`, `hora`, `minutos`). | Generada por `create_datetime()`            |
| **anio**                  | int          | Año del accidente.                                                                         | Copiado sin cambios                         |
| **mes**                   | int          | Mes del accidente (1–12).                                                                  | Copiado sin cambios                         |
| **dia**                   | int          | Día del mes (1–31).                                                                        | Copiado sin cambios                         |
| **hora**                  | int          | Hora del accidente (0–23).                                                                 | Copiado sin cambios                         |
| **minutos**               | int          | Minutos del accidente (0–59).                                                              | Copiado sin cambios                         |
| **diasemana**             | str          | Día de la semana (`lunes` a `domingo`).                                                    | Decodificado con `decode_dia_semana()`      |
| **urbana**                | str          | Tipo de zona urbana: `suburbana`, `intersección`, `no intersección`.                       | Decodificado con `decode_zona_urbana()`     |
| **suburbana**             | str          | Tipo de zona suburbana: `urbana`, `camino rural`, `carretera estatal`, `otro camino`.      | Decodificado con `decode_zona_suburbana()`  |
| **tipaccid**              | str          | Tipo de accidente (ej. `colisión con vehículo automotor`, `volcadura`, `otro`).            | Decodificado con `decode_tipo_accidente()`  |
| **causaacci**             | str          | Causa probable del accidente (`conductor`, `peatón/pasajero`, `falla del vehículo`, etc.). | Decodificado con `decode_causa_accidente()` |
| **caparod**               | str          | Tipo de superficie del camino (`pavimentada`, `no pavimentada`).                           | Decodificado con `decode_capa_rodamiento()` |
| **sexo**                  | str          | Sexo del conductor presunto responsable (`hombre`, `mujer`, `se fugó`).                    | Decodificado con `decode_sexo()`            |
| **aliento**               | str          | Presencia de aliento alcohólico (`sí`, `no`, `se ignora`).                                 | Decodificado con `decode_aliento()`         |
| **cinturon**              | str          | Uso de cinturón de seguridad (`sí`, `no`, `se ignora`).                                    | Decodificado con `decode_cinturon()`        |
| **clase**                 | str          | Gravedad del accidente (`fatal`, `no fatal`, `solo daños`).                                | Decodificado con `decode_clase_accidente()` |
| **latitud**, **longitud** | float        | Coordenadas geográficas del accidente.                                                     | Copiadas sin cambios                        |
| **colonia**               | str          | Colonia o ubicación aproximada.                                                            | Normalizada en minúsculas                   |
| **clavevial**             | str          | Identificador vial o carretera.                                                            | Normalizada en minúsculas                   |

### Notas

* Los valores nulos en `datetime` indican registros con información incompleta de fecha u hora.
* Los textos están en minúsculas para asegurar consistencia en análisis posteriores.
* Este dataset se usará para combinarse con datos de baches y clima en la fase de integración.


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
