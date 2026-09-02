"""Orquestador: descarga datos de Banco Central, CMF e INE y los deja en /data.

Uso:
    python src/main.py

Cada fuente se ejecuta de forma independiente: si a una fuente le falta una
credencial o falla la red, las demas igual se ejecutan y el resumen final
indica claramente que fuentes se completaron.
"""

from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))

import banco_central  # noqa: E402
import cmf  # noqa: E402
import ine_sdmx  # noqa: E402

CARPETA_DATA = Path(__file__).resolve().parent.parent / "data"


def ejecutar_banco_central(resumen: dict) -> None:
    try:
        tabla = banco_central.obtener_series(desde="2023-01-01", hasta=date.today().isoformat())
        tabla.to_csv(CARPETA_DATA / "banco_central_series.csv", index=False)
        resumen["Banco Central"] = f"OK ({len(tabla)} filas)"
    except Exception as error:  # noqa: BLE001 - queremos seguir con las demas fuentes
        resumen["Banco Central"] = f"ERROR: {error}"


def ejecutar_cmf(resumen: dict) -> None:
    try:
        filas = cmf.obtener_indicadores()
        ruta = CARPETA_DATA / "cmf_indicadores.csv"

        nuevas = pd.DataFrame(filas)
        if ruta.exists():
            historico = pd.read_csv(ruta)
            combinado = pd.concat([historico, nuevas], ignore_index=True)
            combinado = combinado.drop_duplicates(subset=["indicador", "fecha_valor"], keep="last")
        else:
            combinado = nuevas
        combinado.to_csv(ruta, index=False)
        resumen["CMF"] = f"OK ({len(filas)} indicadores)"
    except Exception as error:  # noqa: BLE001
        resumen["CMF"] = f"ERROR: {error}"


def ejecutar_ine(resumen: dict) -> None:
    try:
        catalogo = ine_sdmx.listar_dataflows()
        catalogo.to_csv(CARPETA_DATA / "ine_catalogo_dataflows.csv", index=False)

        datos = ine_sdmx.obtener_datos("DF_DES_SEXO", desde="2023-01")
        datos.to_csv(CARPETA_DATA / "ine_desocupados_regional_sexo.csv", index=False)

        tasas = ine_sdmx.obtener_datos("DF_TDES_SEXO", desde="2023-01")
        tasas.to_csv(CARPETA_DATA / "ine_tasa_desocupacion_regional_sexo.csv", index=False)

        participacion = ine_sdmx.obtener_datos("DF_TP_SEXO", desde="2023-01")
        participacion.to_csv(CARPETA_DATA / "ine_tasa_participacion_regional_sexo.csv", index=False)

        total_filas = len(datos) + len(tasas) + len(participacion)
        resumen["INE"] = f"OK ({len(catalogo)} dataflows catalogados, {total_filas} filas de datos)"
    except Exception as error:  # noqa: BLE001
        resumen["INE"] = f"ERROR: {error}"


def main() -> None:
    load_dotenv()
    CARPETA_DATA.mkdir(exist_ok=True)

    resumen: dict[str, str] = {}
    ejecutar_banco_central(resumen)
    ejecutar_cmf(resumen)
    ejecutar_ine(resumen)

    print(f"\nActualizacion de datos - {datetime.now().isoformat(timespec='seconds')}")
    print("=" * 60)
    for fuente, estado in resumen.items():
        print(f"{fuente:15s}: {estado}")


if __name__ == "__main__":
    main()
