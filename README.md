# TPM, Dolar y Empleo: Indicadores Economicos de Chile

Conecta tres APIs publicas y oficiales de Chile (Banco Central, CMF Bancos
e INE) para descargar indicadores economicos reales, y los deja
versionados en este mismo repositorio, actualizados automaticamente todos
los dias.

## Por que estos indicadores

Son cuatro insumos habituales en analisis financiero y economico:

- **Tasa de Politica Monetaria (TPM) y dolar observado** (Banco Central):
  referencia para evaluar condiciones crediticias y costo de financiamiento.
- **Imacec e IPC** (Banco Central): miden actividad economica e inflacion,
  dos variables clave para cualquier analisis de contexto macroeconomico.
- **Desocupacion por region y sexo** (INE, Encuesta Nacional de Empleo):
  permite comparar la situacion laboral entre regiones y por sexo.
- **Dolar, UF y UTM del dia** (CMF Bancos, ex SBIF): valores de referencia
  usados en contratos, creditos y pagos indexados.

El proyecto automatiza la obtencion de estos datos para tenerlos siempre
actualizados y listos para analisis, sin depender de descargas manuales.

## Que hace el proyecto

```text
src/banco_central.py   -> TPM, dolar observado, Imacec, IPC (via libreria bcchapi)
src/cmf.py              -> Dolar, UF, UTM del dia (API CMF Bancos / ex SBIF)
src/ine_sdmx.py         -> Catalogo de series INE + desocupados por region/sexo (SDMX)
src/main.py             -> ejecuta las tres fuentes y guarda todo en /data
.github/workflows/      -> actualiza /data automaticamente todos los dias (GitHub Actions)
analisis/                -> Excel y Power BI con los analisis (ver seccion siguiente)
```

Cada conector es independiente: si falta una credencial o una fuente falla,
las otras dos igual se ejecutan y `main.py` lo indica claramente en el
resumen final, en vez de detener todo el proceso.

## Alcance del proyecto

| Parte | Contenido |
|---|---|
| Extraccion automatica (`src/`) | Conectores a las tres APIs oficiales |
| Automatizacion diaria (`.github/workflows/`) | Actualiza los datos todos los dias, sin intervencion manual |
| Limpieza de datos | En Excel (Power Query): tipos, regiones, sexo, fechas |
| Analisis (`analisis/`) | TPM, TPM vs. dolar, TPM vs. IPC, volatilidad del dolar, desocupacion regional por sexo, indices normalizados — en Excel y Power BI |

## Datos publicados en `/data`

| Archivo | Contenido |
|---|---|
| `banco_central_series.csv` | TPM, dolar observado, Imacec e IPC mensual, serie historica |
| `cmf_indicadores.csv` | Dolar, UF y UTM, con fecha de consulta (se acumula en cada corrida) |
| `ine_catalogo_dataflows.csv` | Catalogo completo de series disponibles en el SDMX del INE |
| `ine_desocupados_regional_sexo.csv` | Personas desocupadas estimadas, por region y sexo (ENE) |
| `ine_tasa_desocupacion_regional_sexo.csv` | Tasa de desocupacion (%), por region y sexo (ENE) |
| `ine_tasa_participacion_regional_sexo.csv` | Tasa de participacion laboral (%), por region y sexo (ENE) |

Estos archivos se generan corriendo el proyecto localmente o via GitHub
Actions; no se incluyen datos falsos ni de ejemplo en el repositorio.

## Fuentes y credenciales

Ninguna credencial se guarda en el codigo. Todas se leen desde variables de
entorno (`.env` local, o *Secrets* de GitHub Actions en produccion).

| Fuente | Autenticacion | Como obtenerla |
|---|---|---|
| Banco Central (BDE) | Token o usuario/contrasena | Cuenta gratuita en https://si3.bcentral.cl |
| CMF Bancos (ex SBIF) | API key | Solicitud gratuita en https://api.cmfchile.cl/que-es-api.html |
| INE (SDMX) | Ninguna | API publica, sin registro |

## Instalacion y uso local

```bash
git clone <URL-de-este-repositorio>
cd apis-economicas-chile
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # Windows (usar "cp" en Linux/Mac)
# completar .env con tus credenciales de Banco Central y CMF
python src/main.py
```

Los resultados quedan en la carpeta `data/`.

## Automatizacion (GitHub Actions)

El workflow `.github/workflows/actualizar_datos.yml` corre todos los dias
y tambien se puede lanzar manualmente desde la pestana **Actions** del
repositorio. Para que funcione en GitHub (no solo en local), hay que cargar
las credenciales como *Secrets* del repositorio:

`Settings -> Secrets and variables -> Actions -> New repository secret`

- `BCCH_API_TOKEN`
- `CMF_API_KEY`

El INE no necesita secreto porque su API es publica.

## Limitaciones y proximos pasos

- `ine_desocupados_regional_sexo.csv` entrega personas desocupadas
  estimadas (cantidad) por region y sexo; `ine_tasa_desocupacion_regional_sexo.csv`
  entrega la tasa (%) equivalente, tambien por region y sexo.
- El conector CMF solo trae el valor vigente del dia de cada indicador; un
  historico propio se va construyendo automaticamente cada vez que corre el
  workflow diario (por eso `cmf_indicadores.csv` se acumula en vez de
  sobrescribirse).
- No se hizo ningun tipo de scraping ni se inventaron endpoints: los tres
  conectores usan unicamente APIs oficiales y documentadas publicamente.

## Stack

Python 3.11, `bcchapi`, `pandas`, `requests`, `python-dotenv`, GitHub Actions.
