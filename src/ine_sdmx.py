"""Conector para el API SDMX del INE (Instituto Nacional de Estadisticas de Chile).

Base: https://sdmx.ine.gob.cl (agencia CL01). API publica, SIN autenticacion:
no requiere API key ni registro.

Este modulo cubre dos capacidades:
1. Catalogo de dataflows disponibles (que series existen y con que ID).
2. Descarga de datos reales de un dataflow puntual, en formato CSV SDMX.

Dataflow de ejemplo verificado: DF_DES_SEXO (Poblacion desocupada nacional y
regional segun sexo, Encuesta Nacional de Empleo). Entrega personas
desocupadas estimadas por region (AREA_REF) y sexo (SEXO), no una tasa
nacional unica: para una tasa de desocupacion nacional habria que cruzarlo
con el dataflow de fuerza de trabajo (DF_FDT_SEXO). Queda como extension.
"""

from __future__ import annotations

import io
import xml.etree.ElementTree as ET

import pandas as pd
import requests

BASE_URL = "https://sdmx.ine.gob.cl"
AGENCIA = "CL01"

# Namespace SDMX-ML usado por el catalogo de estructura.
_NS = {
    "str": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
    "com": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common",
}


def listar_dataflows(filtro: str | None = None) -> pd.DataFrame:
    """Descarga el catalogo completo de dataflows y opcionalmente lo filtra.

    `filtro` busca (sin distinguir mayusculas) dentro del id o el nombre.
    """
    respuesta = requests.get(f"{BASE_URL}/rest/dataflow/all", timeout=30)
    respuesta.raise_for_status()

    raiz = ET.fromstring(respuesta.content)
    filas = []
    for nodo in raiz.iter("{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure}Dataflow"):
        id_flow = nodo.get("id")
        version = nodo.get("version")
        agencia = nodo.get("agencyID")
        nombre_nodo = nodo.find("com:Name", _NS)
        nombre = nombre_nodo.text if nombre_nodo is not None else ""
        filas.append({"id": id_flow, "agencia": agencia, "version": version, "nombre": nombre})

    tabla = pd.DataFrame(filas)
    if filtro:
        patron = filtro.lower()
        tabla = tabla[
            tabla["id"].str.lower().str.contains(patron)
            | tabla["nombre"].str.lower().str.contains(patron)
        ]
    return tabla.reset_index(drop=True)


def obtener_datos(
    dataflow_id: str,
    version: str = "1.0",
    agencia: str = AGENCIA,
    clave: str = "all",
    desde: str | None = None,
) -> pd.DataFrame:
    """Descarga los datos reales de un dataflow como DataFrame (via CSV SDMX)."""
    url = f"{BASE_URL}/rest/data/{agencia},{dataflow_id},{version}/{clave}"
    parametros = {"format": "csv"}
    if desde:
        parametros["startPeriod"] = desde

    respuesta = requests.get(url, params=parametros, timeout=60)
    respuesta.raise_for_status()
    return pd.read_csv(io.StringIO(respuesta.text))


if __name__ == "__main__":
    catalogo = listar_dataflows(filtro="desocupad")
    print(catalogo)

    datos = obtener_datos("DF_DES_SEXO", desde="2024-01")
    print(datos.head())
