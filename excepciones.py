# Título: Dine de one nodo
# Nombre del autor: Osmar Delgado
# Fecha: 2026-11-16
# Descripción: Define los errores de la red de transporte.
"""Excepciones propias del dominio de la red de transporte."""


class RedTransporteError(Exception):
    """Error base de la aplicación."""


class ConexionInvalidaError(RedTransporteError):
    """La conexión no cumple las reglas del grafo (nodos o peso)."""


class NodoNoEncontradoError(RedTransporteError):
    """El nodo solicitado no existe en el grafo."""


class RutaNoEncontradaError(RedTransporteError):
    """No existe un camino entre el origen y el destino."""


class ArchivoDatosError(RedTransporteError):
    """El archivo CSV no se pudo leer o escribir."""
