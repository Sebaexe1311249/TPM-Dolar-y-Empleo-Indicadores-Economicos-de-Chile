# Indicadores economicos de Chile via API (Banco Central, CMF, INE)

Proyecto de portafolio: conecta tres APIs publicas y oficiales de Chile
(Banco Central, CMF Bancos e INE) para descargar indicadores economicos
reales, y los deja versionados en este mismo repositorio, actualizados
automaticamente cada semana.

## Por que este proyecto

Lo arme pensando en un rol de **analista de centro de contacto** (por ejemplo,
BancoEstado Contacto 24 Horas). Un analista de este tipo no solo mide
volumen de llamadas o SLA: para explicarlos necesita contexto macro y
regulatorio real:

- **Tasa de Politica Monetaria (TPM) y dolar observado** (Banco Central):
  cuando la TPM sube o baja, cambian las condiciones de creditos hipotecarios
  y de consumo, y con ellas el volumen de llamadas por repactacion,
  renegociacion o consultas sobre nuevas condiciones.
- **Imacec e IPC** (Banco Central): actividad economica e inflacion
  anticipan presion de mora, reclamos por reajustes UF y quejas por costo
  de vida.
- **Desocupacion por region y sexo** (INE, Encuesta Nacional de Empleo): el
  desempleo correlaciona directamente con mora y renegociacion de deuda; la
  apertura regional sirve para explicar por que ciertas zonas generan mas
  contactos que otras.
- **Dolar, UF y UTM del dia** (CMF Bancos, ex SBIF): indicadores que los
  ejecutivos de contacto usan a diario para responder consultas de clientes
  sobre creditos indexados a UF o pagos en UTM.

La idea no es solo "consumir una API", sino demostrar que puedo conectar
datos oficiales externos con el tipo de pregunta que realmente se hace un
analista de centro de contacto: **por que subio el volumen, y que dato
externo lo explica.**

## Que hace el proyecto

```text
src/banco_central.py   -> TPM, dolar observado, Imacec, IPC (via libreria bcchapi)
src/cmf.py              -> Dolar, UF, UTM del dia (API CMF Bancos / ex SBIF)
src/ine_sdmx.py         -> Catalogo de series INE + desocupados por region/sexo (SDMX)
src/main.py             -> ejecuta las tres fuentes y guarda todo en /data
.github/workflows/      -> actualiza /data automaticamente cada semana (GitHub Actions)
```

Cada conector es independiente: si falta una credencial o una fuente falla,
las otras dos igual se ejecutan y `main.py` lo indica claramente en el
resumen final, en vez de detener todo el proceso.

## Datos publicados en `/data`

| Archivo | Contenido |
|---|---|
| `banco_central_series.csv` | TPM, dolar observado, Imacec e IPC mensual, serie historica |
| `cmf_indicadores.csv` | Dolar, UF y UTM, con fecha de consulta (se acumula en cada corrida) |
| `ine_catalogo_dataflows.csv` | Catalogo completo de series disponibles en el SDMX del INE |
| `ine_desocupados_regional_sexo.csv` | Personas desocupadas estimadas, por region y sexo (ENE) |

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
cd portafolio-apis-economicas-chile
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # Windows (usar "cp" en Linux/Mac)
# completar .env con tus credenciales de Banco Central y CMF
python src/main.py
```

Los resultados quedan en la carpeta `data/`.

## Automatizacion (GitHub Actions)

El workflow `.github/workflows/actualizar_datos.yml` corre todos los lunes
y tambien se puede lanzar manualmente desde la pestana **Actions** del
repositorio. Para que funcione en GitHub (no solo en local), hay que cargar
las credenciales como *Secrets* del repositorio:

`Settings -> Secrets and variables -> Actions -> New repository secret`

- `BCCH_API_TOKEN`
- `CMF_API_KEY`

El INE no necesita secreto porque su API es publica.

## Como publicar este repositorio en GitHub

1. Crear un repositorio nuevo, vacio, en https://github.com/new (nombre
   sugerido: `portafolio-apis-economicas-chile`, visibilidad **Publico**,
   sin README/gitignore/license iniciales para no chocar con los ya creados).
2. Desde esta carpeta local:

   ```bash
   git init
   git add .
   git commit -m "Primera version: conectores Banco Central, CMF e INE"
   git branch -M main
   git remote add origin https://github.com/<tu-usuario>/portafolio-apis-economicas-chile.git
   git push -u origin main
   ```

3. Ejecutar `python src/main.py` al menos una vez localmente (con tus
   credenciales en `.env`) y volver a commitear `data/` para que el
   repositorio ya muestre datos reales desde el primer momento:

   ```bash
   git add data/
   git commit -m "Primeros datos reales"
   git push
   ```

4. Configurar los *Secrets* del paso anterior para que la actualizacion
   semanal automatica funcione sin intervencion manual.
5. Copiar la URL del repositorio (`https://github.com/<tu-usuario>/portafolio-apis-economicas-chile`)
   y usarla como link en el curriculum — el repositorio publico ya incluye
   codigo, datos y esta documentacion, sin necesidad de adjuntar nada mas.

## Limitaciones y proximos pasos

- `ine_desocupados_regional_sexo.csv` entrega personas desocupadas
  estimadas por region y sexo, no una tasa nacional unica. Para una tasa de
  desocupacion nacional habria que cruzar este dataflow con el de fuerza de
  trabajo (`DF_FDT_SEXO`) — queda documentado como extension futura, no
  implementado todavia.
- El conector CMF solo trae el valor vigente del dia de cada indicador; un
  historico propio se va construyendo automaticamente cada vez que corre el
  workflow semanal (por eso `cmf_indicadores.csv` se acumula en vez de
  sobrescribirse).
- No se hizo ningun tipo de scraping ni se inventaron endpoints: los tres
  conectores usan unicamente APIs oficiales y documentadas publicamente.

## Stack

Python 3.11, `bcchapi`, `pandas`, `requests`, `python-dotenv`, GitHub Actions.
