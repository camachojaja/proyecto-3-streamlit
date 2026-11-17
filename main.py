# Título: Dine de one nodo
# Nombre del autor: Osmar Delgado
# Fecha: 2026-11-16
# Descripción: Ejecuta el menú interactivo en consola.
"""Punto de entrada: menú interactivo de la red de transporte."""

import sys
from pathlib import Path
from typing import Optional

from entrada import confirmar, leer_nodo, leer_opcion, leer_peso
from excepciones import ArchivoDatosError, RedTransporteError
from grafo import Grafo
from io_handler import RUTA_CSV, cargar_grafo, guardar_grafo

MENU = """
========= RED DE TRANSPORTE =========
 1. Agregar conexión
 2. Ver red
 3. Calcular ruta más corta (Dijkstra)
 4. Recargar desde CSV
 0. Salir
====================================="""


def cargar(ruta: Path) -> Optional[Grafo]:
    """Carga la red; rechaza archivos dañados para no sobrescribirlos."""
    try:
        grafo, avisos = cargar_grafo(ruta)
    except ArchivoDatosError as error:
        print(f"  ✗ {error}")
        print("  Corrige el archivo y vuelve a iniciar el programa.")
        return None
    for aviso in avisos:
        print(f"  ! {aviso}")
    if avisos:
        print("  Hay filas inválidas. Corrige el CSV antes de continuar.")
        print("  El archivo original se conserva sin cambios.")
        return None
    print(f"  ✓ {len(grafo.nodos)} nodos y {len(grafo.conexiones())} "
          f"conexiones cargadas desde '{ruta.name}'.")
    return grafo


def agregar_conexion(grafo: Grafo, ruta: Path) -> None:
    """Captura una conexión, la agrega al grafo y la persiste."""
    origen = leer_nodo("  Nodo origen: ")
    destino = leer_nodo("  Nodo destino: ")
    if origen == destino:
        print("  ✗ El origen y el destino deben ser distintos.")
        return
    anterior = grafo.peso(origen, destino)
    if anterior is not None and not confirmar(
            f"  La conexión ya existe con peso {anterior}. ¿Reemplazar?"):
        return
    peso = leer_peso("  Peso (distancia/tiempo): ")

    try:
        grafo.agregar_conexion(origen, destino, peso)
        guardar_grafo(ruta, grafo)
    except ArchivoDatosError as error:
        # Revertir para que memoria y archivo no queden desalineados.
        if anterior is None:
            grafo.eliminar_conexion(origen, destino)
        else:
            grafo.agregar_conexion(origen, destino, anterior)
        print(f"  ✗ {error}")
    except RedTransporteError as error:
        print(f"  ✗ {error}")
    else:
        print(f"  ✓ Guardado: {origen} ↔ {destino} ({peso})")


def mostrar_red(grafo: Grafo) -> None:
    """Imprime las conexiones registradas."""
    conexiones = grafo.conexiones()
    if not conexiones:
        print("  La red está vacía.")
        return
    print(f"  Nodos: {', '.join(grafo.nodos)}")
    for origen, destino, peso in conexiones:
        print(f"  {origen:>15} ↔ {destino:<15} {peso:>8.2f}")


def calcular_ruta(grafo: Grafo) -> None:
    """Pide origen y destino y ejecuta Dijkstra."""
    if len(grafo.nodos) < 2:
        print("  Se necesitan al menos dos nodos conectados.")
        return
    print(f"  Nodos disponibles: {', '.join(grafo.nodos)}")
    origen = leer_nodo("  Origen: ")
    destino = leer_nodo("  Destino: ")
    try:
        costo, ruta = grafo.dijkstra(origen, destino)
    except RedTransporteError as error:
        print(f"  ✗ {error}")
        return
    print(f"  Ruta: {' → '.join(ruta)}")
    print(f"  Costo total: {costo:.2f}")


def main() -> int:
    """Ciclo principal del programa."""
    grafo = cargar(RUTA_CSV)
    if grafo is None:
        return 1
    try:
        while True:
            print(MENU)
            opcion = leer_opcion("Opción: ", {"0", "1", "2", "3", "4"})
            if opcion == "1":
                agregar_conexion(grafo, RUTA_CSV)
            elif opcion == "2":
                mostrar_red(grafo)
            elif opcion == "3":
                calcular_ruta(grafo)
            elif opcion == "4":
                grafo = cargar(RUTA_CSV)
                if grafo is None:
                    return 1
            else:
                print("Hasta luego.")
                return 0
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma interrumpido. Los datos ya guardados se conservan.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
