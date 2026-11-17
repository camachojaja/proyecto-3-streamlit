# Título: Dine de one nodo
# Nombre del autor: Osmar Delgado
# Fecha: 2026-11-16
# Descripción: Modela la red e implementa Dijkstra.
"""Modelo de grafo ponderado y algoritmo de Dijkstra (Unidad 1)."""

import heapq
import math
from typing import Optional

from excepciones import (
    ConexionInvalidaError,
    NodoNoEncontradoError,
    RutaNoEncontradaError,
)

Adyacencia = dict[str, dict[str, float]]
Conexion = tuple[str, str, float]


class Grafo:
    """Grafo no dirigido y ponderado que modela la red de transporte."""

    def __init__(self) -> None:
        self._adyacencia: Adyacencia = {}

    def agregar_conexion(self, origen: str, destino: str,
                         peso: float) -> None:
        """Agrega (o actualiza) una conexión en ambos sentidos."""
        if not origen or not destino:
            raise ConexionInvalidaError("Los nodos no pueden estar vacíos.")
        if origen == destino:
            raise ConexionInvalidaError(
                "El origen y el destino deben ser distintos.")
        if not math.isfinite(peso) or peso <= 0:
            raise ConexionInvalidaError(
                "El peso debe ser un número positivo.")
        self._adyacencia.setdefault(origen, {})[destino] = peso
        self._adyacencia.setdefault(destino, {})[origen] = peso

    def eliminar_conexion(self, origen: str, destino: str) -> None:
        """Quita una conexión y limpia los nodos que queden aislados."""
        for a, b in ((origen, destino), (destino, origen)):
            vecinos = self._adyacencia.get(a)
            if vecinos is not None:
                vecinos.pop(b, None)
                if not vecinos:
                    del self._adyacencia[a]

    def peso(self, origen: str, destino: str) -> Optional[float]:
        """Devuelve el peso de la conexión o None si no existe."""
        return self._adyacencia.get(origen, {}).get(destino)

    @property
    def nodos(self) -> list[str]:
        """Lista ordenada de nodos."""
        return sorted(self._adyacencia)

    def conexiones(self) -> list[Conexion]:
        """Lista de conexiones sin duplicar el sentido inverso."""
        resultado: list[Conexion] = []
        for origen, vecinos in self._adyacencia.items():
            for destino, peso in vecinos.items():
                if origen < destino:
                    resultado.append((origen, destino, peso))
        return sorted(resultado)

    def dijkstra(self, origen: str,
                 destino: str) -> tuple[float, list[str]]:
        """Calcula el camino de costo mínimo entre dos nodos.

        Devuelve una tupla (costo_total, ruta).
        """
        for nodo in (origen, destino):
            if nodo not in self._adyacencia:
                raise NodoNoEncontradoError(
                    f"El nodo '{nodo}' no existe en la red.")

        distancias: dict[str, float] = {origen: 0.0}
        previos: dict[str, str] = {}
        visitados: set[str] = set()
        cola: list[tuple[float, str]] = [(0.0, origen)]

        while cola:
            distancia, actual = heapq.heappop(cola)
            if actual in visitados:
                continue
            visitados.add(actual)
            if actual == destino:
                break
            for vecino, peso in self._adyacencia[actual].items():
                nueva = distancia + peso
                if nueva < distancias.get(vecino, math.inf):
                    distancias[vecino] = nueva
                    previos[vecino] = actual
                    heapq.heappush(cola, (nueva, vecino))

        if destino not in visitados:
            raise RutaNoEncontradaError(
                f"No hay ruta entre '{origen}' y '{destino}'.")

        ruta = [destino]
        while ruta[-1] != origen:
            ruta.append(previos[ruta[-1]])
        ruta.reverse()
        return distancias[destino], ruta
