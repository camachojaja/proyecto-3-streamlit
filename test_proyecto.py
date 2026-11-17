# Título: Dine de one nodo
# Nombre del autor: Osmar Delgado
# Fecha: 2026-11-16
# Descripción: Prueba Dijkstra, la consola y la persistencia.
"""Pruebas unitarias del grafo y la persistencia."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main as aplicacion

from excepciones import (
    ArchivoDatosError,
    ConexionInvalidaError,
    NodoNoEncontradoError,
    RutaNoEncontradaError,
)
from grafo import Grafo
from io_handler import cargar_grafo, guardar_grafo


class PruebasGrafo(unittest.TestCase):
    def setUp(self) -> None:
        self.grafo = Grafo()
        self.grafo.agregar_conexion("A", "B", 4)
        self.grafo.agregar_conexion("A", "C", 1)
        self.grafo.agregar_conexion("C", "B", 2)
        self.grafo.agregar_conexion("B", "D", 5)

    def test_ruta_mas_corta(self) -> None:
        costo, ruta = self.grafo.dijkstra("A", "D")
        self.assertEqual(costo, 8)
        self.assertEqual(ruta, ["A", "C", "B", "D"])

    def test_nodo_inexistente(self) -> None:
        with self.assertRaises(NodoNoEncontradoError):
            self.grafo.dijkstra("A", "Z")

    def test_sin_ruta(self) -> None:
        self.grafo.agregar_conexion("X", "Y", 1)
        with self.assertRaises(RutaNoEncontradaError):
            self.grafo.dijkstra("A", "X")

    def test_peso_invalido(self) -> None:
        for peso in (0, -3, float("nan"), float("inf")):
            with self.assertRaises(ConexionInvalidaError):
                self.grafo.agregar_conexion("A", "E", peso)

    def test_lazo_invalido(self) -> None:
        with self.assertRaises(ConexionInvalidaError):
            self.grafo.agregar_conexion("A", "A", 1)


class PruebasPersistencia(unittest.TestCase):
    def setUp(self) -> None:
        self.carpeta = tempfile.TemporaryDirectory()
        self.ruta = Path(self.carpeta.name) / "red.csv"

    def tearDown(self) -> None:
        self.carpeta.cleanup()

    def test_ida_y_vuelta(self) -> None:
        grafo = Grafo()
        grafo.agregar_conexion("A", "B", 3.5)
        guardar_grafo(self.ruta, grafo)
        cargado, avisos = cargar_grafo(self.ruta)
        self.assertEqual(cargado.conexiones(), [("A", "B", 3.5)])
        self.assertEqual(avisos, [])

    def test_archivo_inexistente(self) -> None:
        grafo, avisos = cargar_grafo(self.ruta)
        self.assertEqual(grafo.nodos, [])
        self.assertEqual(avisos, [])

    def test_filas_corruptas(self) -> None:
        self.ruta.write_text(
            "origen,destino,peso\nA,B,2\nA,C,abc\nC,C,1\n,D,4\n",
            encoding="utf-8")
        grafo, avisos = cargar_grafo(self.ruta)
        self.assertEqual(grafo.conexiones(), [("A", "B", 2.0)])
        self.assertEqual(len(avisos), 3)

    def test_columnas_faltantes(self) -> None:
        self.ruta.write_text("a,b\n1,2\n", encoding="utf-8")
        with self.assertRaises(ArchivoDatosError):
            cargar_grafo(self.ruta)

    def test_fallo_crear_temporal(self) -> None:
        with patch("io_handler.tempfile.mkstemp",
                   side_effect=PermissionError("Sin permiso")):
            with self.assertRaises(ArchivoDatosError):
                guardar_grafo(self.ruta, Grafo())

    def test_fallo_reemplazar_conserva_archivo(self) -> None:
        contenido = "origen,destino,peso\nA,B,2\n"
        self.ruta.write_text(contenido, encoding="utf-8")
        with patch("io_handler.os.replace",
                   side_effect=PermissionError("Archivo bloqueado")):
            with self.assertRaises(ArchivoDatosError):
                guardar_grafo(self.ruta, Grafo())
        self.assertEqual(self.ruta.read_text(encoding="utf-8"), contenido)
        self.assertEqual(list(self.ruta.parent.glob(".tmp_*.csv")), [])

    def test_inicio_rechaza_csv_corrupto(self) -> None:
        for contenido in ("a,b\n1,2\n",
                          "origen,destino,peso\nA,B,2\nA,C,abc\n"):
            with self.subTest(contenido=contenido):
                self.ruta.write_text(contenido, encoding="utf-8")
                with patch.object(aplicacion, "RUTA_CSV", self.ruta):
                    with patch("builtins.print"):
                        self.assertEqual(aplicacion.main(), 1)
                self.assertEqual(
                    self.ruta.read_text(encoding="utf-8"), contenido)

    def test_guardado_fallido_revierte_memoria(self) -> None:
        for anterior in (None, 2.0):
            with self.subTest(anterior=anterior):
                grafo = Grafo()
                if anterior is not None:
                    grafo.agregar_conexion("A", "B", anterior)
                with patch("main.leer_nodo", side_effect=["A", "B"]), \
                        patch("main.leer_peso", return_value=5.0), \
                        patch("main.confirmar", return_value=True), \
                        patch("io_handler.tempfile.mkstemp",
                              side_effect=PermissionError("Sin permiso")), \
                        patch("builtins.print"):
                    aplicacion.agregar_conexion(grafo, self.ruta)
                self.assertEqual(grafo.peso("A", "B"), anterior)
                if anterior is None:
                    self.assertEqual(grafo.nodos, [])

    def test_recarga_corrupta_conserva_archivo(self) -> None:
        self.ruta.write_text("origen,destino,peso\nA,B,2\n",
                             encoding="utf-8")
        contenido = "origen,destino,peso\nA,B,error\n"

        def corromper_y_recargar(*args: object) -> str:
            self.ruta.write_text(contenido, encoding="utf-8")
            return "4"

        with patch.object(aplicacion, "RUTA_CSV", self.ruta), \
                patch("main.leer_opcion",
                      side_effect=corromper_y_recargar), \
                patch("builtins.print"):
            self.assertEqual(aplicacion.main(), 1)
        self.assertEqual(self.ruta.read_text(encoding="utf-8"), contenido)


if __name__ == "__main__":
    unittest.main()
