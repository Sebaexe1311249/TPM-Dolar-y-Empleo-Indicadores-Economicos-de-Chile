"""Conector para la API CMF Bancos (ex SBIF) - indicadores financieros oficiales.

Documentacion: https://api.cmfchile.cl/documentacion/index.html
Solicitud de apikey gratuita: https://api.cmfchile.cl/que-es-api.html

La apikey nunca se hardcodea: se lee desde la variable de entorno CMF_API_KEY.
"""

from __future__ import annotations

import os
from datetime import date

import requests

BASE_URL = "https://api.cmfchile.cl/api-sbifv3/recursos_api"

# Recursos verificados contra la documentacion oficial. Puedes agregar mas
# (ipc, euro, tasas) revisando el slug exacto en api.cmfchile.cl/documentacion.
RECURSOS_VERIFICADOS = ("dolar", "uf", "utm")


def _apikey() -> str:
    apikey = os.environ.get("CMF_API_KEY")
    if not apikey:
        raise RuntimeError(
            "Falta CMF_API_KEY. Solicita una apikey gratuita en "
            "https://api.cmfchile.cl/que-es-api.html y agregala a tu .env."
        )
    return apikey


def obtener_indicador(recurso: str, formato: str = "json") -> dict:
    """Consulta el valor vigente de un indicador (dolar, uf, utm, ...)."""
    parametros = {"apikey": _apikey(), "formato": formato}
    respuesta = requests.get(f"{BASE_URL}/{recurso}", params=parametros, timeout=15)
    respuesta.raise_for_status()
    return respuesta.json()


def obtener_indicadores(recursos: list[str] | None = None) -> list[dict]:
    """Consulta varios indicadores y los deja en formato tabla (largo).

    La API devuelve un unico contenedor por respuesta (p.ej. ``Dolares``,
    ``UFs``, ``UTMs``) con una lista de un elemento ``{Valor, Fecha}``. Se
    extrae ese valor sin depender del nombre exacto del contenedor, que no
    sigue una regla de pluralizacion uniforme entre recursos.
    """
    recursos = recursos or list(RECURSOS_VERIFICADOS)
    filas = []
    hoy = date.today().isoformat()
    for recurso in recursos:
        datos = obtener_indicador(recurso)
        contenedor = next(iter(datos.values()), [])
        item = contenedor[0] if contenedor else {}
        filas.append(
            {
                "indicador": recurso,
                "valor": item.get("Valor"),
                "fecha_valor": item.get("Fecha"),
                "fecha_consulta": hoy,
            }
        )
    return filas


if __name__ == "__main__":
    for fila in obtener_indicadores():
        print(fila)
