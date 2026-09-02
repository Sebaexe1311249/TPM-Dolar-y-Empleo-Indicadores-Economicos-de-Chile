"""Conector para la API del Banco Central de Chile (Base de Datos Estadisticos, BDE).

Usa la libreria oficial `bcchapi` (https://pypi.org/project/bcchapi/), que
internamente consume el web service REST del BCCh. Las credenciales nunca se
escriben en este archivo: se leen siempre desde variables de entorno.

Registro gratuito de cuenta BDE: https://si3.bcentral.cl
"""

from __future__ import annotations

import os

import bcchapi
import pandas as pd

# Codigos de serie reales y verificados en la Base de Datos Estadisticos.
# Puedes buscar mas series con `siete.buscar("palabra clave")`.
SERIES_BCCH = {
    "tpm": ("F022.TPM.TIN.D001.NO.Z.D", "Tasa de Politica Monetaria (%)"),
    "dolar_observado": ("F073.TCO.PRE.Z.D", "Dolar observado (CLP por USD)"),
    "imacec": ("F032.IMC.IND.Z.Z.EP18.Z.Z.0.M", "Imacec (indice, base 2018)"),
    "ipc_indice": ("G073.IPC.IND.2018.M", "Indice de Precios al Consumidor, mensual (base 2018=100)"),
}


def conectar() -> bcchapi.Siete:
    """Crea el cliente `Siete` a partir de variables de entorno.

    Prioriza el token moderno (BCCH_API_TOKEN). Si no existe, intenta el
    metodo legado de usuario/contrasena. Nunca acepta credenciales por
    parametro para evitar que terminen hardcodeadas en un script.
    """
    token = os.environ.get("BCCH_API_TOKEN")
    if token:
        return bcchapi.Siete(token=token)

    usuario = os.environ.get("BCCH_USUARIO")
    password = os.environ.get("BCCH_PASSWORD")
    if usuario and password:
        return bcchapi.Siete(usuario, password)

    raise RuntimeError(
        "Faltan credenciales del Banco Central. Define BCCH_API_TOKEN o "
        "BCCH_USUARIO/BCCH_PASSWORD en tu archivo .env (ver .env.example)."
    )


def obtener_series(desde: str, hasta: str, claves: list[str] | None = None) -> pd.DataFrame:
    """Descarga una o varias series del BDE como un DataFrame con fechas.

    Args:
        desde: fecha inicial "YYYY-MM-DD".
        hasta: fecha final "YYYY-MM-DD".
        claves: subconjunto de SERIES_BCCH a descargar (por defecto, todas).
    """
    siete = conectar()
    claves = claves or list(SERIES_BCCH.keys())
    codigos = [SERIES_BCCH[clave][0] for clave in claves]

    df = siete.cuadro(series=codigos, nombres=claves, desde=desde, hasta=hasta)
    df = df.reset_index().rename(columns={df.reset_index().columns[0]: "fecha"})
    return df


def buscar_series(termino: str) -> pd.DataFrame:
    """Busca series por nombre cuando no conoces el codigo exacto."""
    siete = conectar()
    return siete.buscar(termino)


if __name__ == "__main__":
    tabla = obtener_series(desde="2024-01-01", hasta="2025-12-01")
    print(tabla.tail(12))
