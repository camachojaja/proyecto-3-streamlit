# Título: Dine de one nodo
# Nombre del autor: Osmar Delgado
# Fecha: 2026-11-16
# Descripción: Valida la captura de nodos y pesos.
"""Captura validada de datos desde la consola."""

import math

LONGITUD_MAXIMA = 40


def normalizar_nodo(texto: str) -> str:
    """Valida el nombre y lo normaliza a mayúsculas."""
    nombre = texto.strip().upper()
    if not nombre:
        raise ValueError("El nombre del nodo no puede estar vacío.")
    if len(nombre) > LONGITUD_MAXIMA:
        raise ValueError(f"Máximo {LONGITUD_MAXIMA} caracteres por nodo.")
    return nombre


def convertir_peso(texto: str) -> float:
    """Convierte a número un peso decimal positivo."""
    try:
        peso = float(texto.strip().replace(",", "."))
    except ValueError as error:
        raise ValueError("Ingresa un peso numérico.") from error
    if not math.isfinite(peso) or peso <= 0:
        raise ValueError("El peso debe ser finito y mayor que cero.")
    return peso


def leer_nodo(mensaje: str) -> str:
    """Pide el nombre de un nodo hasta que sea válido."""
    while True:
        try:
            return normalizar_nodo(input(mensaje))
        except ValueError as error:
            print(f"  ✗ {error}")


def leer_peso(mensaje: str) -> float:
    """Pide un peso positivo hasta que sea válido."""
    while True:
        try:
            return convertir_peso(input(mensaje))
        except ValueError as error:
            print(f"  ✗ {error}")


def leer_opcion(mensaje: str, validas: set[str]) -> str:
    """Pide una opción hasta que pertenezca al conjunto permitido."""
    while True:
        opcion = input(mensaje).strip().lower()
        if opcion in validas:
            return opcion
        print(f"  ✗ Opción inválida. Usa: {', '.join(sorted(validas))}")


def confirmar(mensaje: str) -> bool:
    """Pregunta sí/no."""
    return leer_opcion(f"{mensaje} (s/n): ", {"s", "n"}) == "s"
