# Título: Dine de one nodo
# Nombre del autor: Osmar Delgado
# Fecha: 2026-11-16
# Descripción: Carga y guarda los tramos en un archivo CSV.
"""Lectura y escritura de la red de transporte en archivos CSV."""

import csv
import os
import tempfile
from copy import deepcopy
from pathlib import Path
from threading import Lock
from typing import Optional

from excepciones import ArchivoDatosError, ConexionInvalidaError
from grafo import Grafo

CABECERA: list[str] = ["origen", "destino", "peso"]
CODIFICACION = "utf-8"
RUTA_CSV = Path(__file__).with_name("nodos.csv")
BLOQUEO_CSV = Lock()
VersionCSV = tuple[int, int, int]


def cargar_grafo(ruta: Path) -> tuple[Grafo, list[str]]:
    """Carga el CSV y devuelve el grafo junto con avisos de filas omitidas.

    Si el archivo no existe se devuelve un grafo vacío (primer uso).
    """
    grafo = Grafo()
    avisos: list[str] = []

    try:
        with ruta.open("r", newline="", encoding=CODIFICACION) as archivo:
            lector = csv.DictReader(archivo)
            if lector.fieldnames is None:
                return grafo, avisos
            faltantes = set(CABECERA) - set(lector.fieldnames)
            if faltantes:
                raise ArchivoDatosError(
                    f"Faltan columnas en el CSV: {sorted(faltantes)}")
            for numero, fila in enumerate(lector, start=2):
                try:
                    origen = (fila["origen"] or "").strip().upper()
                    destino = (fila["destino"] or "").strip().upper()
                    peso = float(fila["peso"] or "")
                    grafo.agregar_conexion(origen, destino, peso)
                except (ValueError, ConexionInvalidaError) as error:
                    avisos.append(f"Línea {numero} omitida: {error}")
    except FileNotFoundError:
        return grafo, avisos
    except (OSError, UnicodeDecodeError, csv.Error) as error:
        raise ArchivoDatosError(
            f"No se pudo leer '{ruta}': {error}") from error
    return grafo, avisos


def guardar_grafo(ruta: Path, grafo: Grafo) -> VersionCSV:
    """Escribe todas las conexiones de forma atómica.

    Se escribe primero en un archivo temporal y luego se reemplaza el
    original, para no dejar un CSV a medias si algo falla.
    """
    carpeta = ruta.parent if str(ruta.parent) else Path(".")
    temporal: Optional[str] = None
    try:
        descriptor, temporal = tempfile.mkstemp(
            dir=carpeta, prefix=".tmp_", suffix=".csv")
        with os.fdopen(descriptor, "w", newline="",
                       encoding=CODIFICACION) as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(CABECERA)
            for origen, destino, peso in grafo.conexiones():
                escritor.writerow([origen, destino, peso])
        version = version_csv(Path(temporal))
        os.replace(temporal, ruta)
        return version
    except OSError as error:
        if temporal is not None:
            try:
                os.remove(temporal)
            except OSError:
                # Conservar como causa el error original de guardado.
                pass
        raise ArchivoDatosError(
            f"No se pudo guardar '{ruta}': {error}") from error


def version_csv(ruta: Path) -> Optional[VersionCSV]:
    """Identifica una versión del archivo sin leer sus filas."""
    try:
        datos = ruta.stat()
    except FileNotFoundError:
        return None
    return datos.st_ino, datos.st_mtime_ns, datos.st_size


def cargar_red(ruta: Path) -> tuple[Grafo, Optional[VersionCSV]]:
    """Carga una red completa y conserva la versión de origen."""
    with BLOQUEO_CSV:
        try:
            version = version_csv(ruta)
        except OSError as error:
            raise ArchivoDatosError(f"No se pudo revisar {ruta}.") from error
        grafo, avisos = cargar_grafo(ruta)
    if avisos:
        raise ArchivoDatosError("Filas inválidas en nodos.csv: "
                                + " | ".join(avisos))
    return grafo, version


def registrar_conexion(
    ruta: Path, grafo: Grafo, version: Optional[VersionCSV],
    origen: str, destino: str, peso: float,
) -> tuple[Grafo, VersionCSV]:
    """Publica una copia del grafo solo si el archivo se guarda."""
    actual = deepcopy(grafo)
    actual.agregar_conexion(origen, destino, peso)
    with BLOQUEO_CSV:
        try:
            vigente = version_csv(ruta)
        except OSError as error:
            raise ArchivoDatosError(f"No se pudo revisar {ruta}.") from error
        if vigente != version:
            raise ArchivoDatosError(
                "nodos.csv cambió. Abre una sesión nueva y vuelve a intentar."
            )
        return actual, guardar_grafo(ruta, actual)
