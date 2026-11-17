# Título: Dine de one nodo
# Nombre del autor: Osmar Delgado
# Fecha: 2026-11-16
# Descripción: Interfaz web para registrar conexiones y calcular rutas.
"""Interfaz de Streamlit para la red de transporte."""

import pandas as pd
import streamlit as st

from entrada import normalizar_nodo, convertir_peso
from excepciones import (
    ArchivoDatosError,
    ConexionInvalidaError,
    NodoNoEncontradoError,
    RutaNoEncontradaError,
)
from io_handler import RUTA_CSV, cargar_red, registrar_conexion


def inicializar_red() -> None:
    """Carga la red una vez y conserva el resultado en la sesión."""
    estado = st.session_state
    if "grafo" not in estado:
        estado.grafo = None
        try:
            estado.grafo, estado.version_csv = cargar_red(RUTA_CSV)
        except ArchivoDatosError as error:
            estado.error_csv = str(error)
    if estado.grafo is None:
        st.error(estado.error_csv)
        st.warning("Revisa nodos.csv y vuelve a abrir la aplicación.")
        st.stop()


def formulario_conexion() -> None:
    """Registra nodos y el tramo que los conecta."""
    estado = st.session_state
    with st.sidebar.form("registro"):
        st.subheader("Registrar conexión")
        origen = st.text_input("Origen", key="registro_origen")
        destino = st.text_input("Destino", key="registro_destino")
        peso = st.text_input("Peso", key="registro_peso", placeholder="3.5")
        reemplazar = st.checkbox("Actualizar el peso si la conexión existe")
        enviado = st.form_submit_button("Guardar conexión")

    barra = st.sidebar
    if enviado:
        try:
            origen = normalizar_nodo(origen)
            destino = normalizar_nodo(destino)
            costo = convertir_peso(peso)
            existe = estado.grafo.peso(origen, destino) is not None
            if existe and not reemplazar:
                raise ConexionInvalidaError(
                    "La conexión ya existe. Activa la opción de actualizar."
                )
            estado.grafo, estado.version_csv = registrar_conexion(
                RUTA_CSV, estado.grafo, estado.version_csv,
                origen, destino, costo,
            )
        except (ValueError, ConexionInvalidaError, ArchivoDatosError) as error:
            barra.error(str(error))
        else:
            barra.success(f"Conexión guardada: {origen} ↔ {destino}.")


def formulario_ruta() -> None:
    """Calcula y muestra la secuencia y el costo mínimo."""
    with st.form("ruta"):
        origen_col, destino_col = st.columns(2)
        origen = origen_col.text_input("Origen", key="ruta_origen")
        destino = destino_col.text_input("Destino", key="ruta_destino")
        enviado = st.form_submit_button("Calcular ruta")
    if enviado:
        try:
            costo, recorrido = st.session_state.grafo.dijkstra(
                normalizar_nodo(origen), normalizar_nodo(destino),
            )
        except (ValueError, NodoNoEncontradoError) as error:
            st.error(str(error))
        except RutaNoEncontradaError as error:
            st.warning(str(error))
        else:
            st.success(" → ".join(recorrido))
            st.metric("Costo total mínimo", f"{costo:.12g}")


def mostrar_red() -> None:
    """Presenta el catálogo y la tabla de conexiones de la sesión."""
    grafo = st.session_state.grafo
    if not grafo.nodos:
        st.info("Registra una conexión en la barra lateral para crear la red.")
        return
    st.subheader("Nodos")
    st.dataframe(pd.DataFrame({"Nodo": grafo.nodos}), hide_index=True)
    st.subheader("Conexiones")
    conexiones = pd.DataFrame(
        grafo.conexiones(), columns=["Origen", "Destino", "Peso"],
    )
    st.dataframe(conexiones, hide_index=True)


def main() -> None:
    """Organiza las acciones y vistas de la aplicación."""
    st.set_page_config(page_title="Dine de one nodo", layout="wide")
    st.title("Dine de one nodo")
    inicializar_red()
    formulario_conexion()
    ruta, red = st.tabs(["Ruta más corta", "Red actual"])
    with ruta:
        formulario_ruta()
    with red:
        mostrar_red()


if __name__ == "__main__":
    main()
