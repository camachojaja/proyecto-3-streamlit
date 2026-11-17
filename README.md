# Dine de one nodo

Proyecto 3 de Programación III. Registra conexiones bidireccionales y calcula
rutas de costo mínimo con el algoritmo de Dijkstra del Proyecto 2.

## Ejecutar en Windows

Abre una terminal en la carpeta del proyecto, donde está `app.py`, y ejecuta:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m streamlit run app.py
```

El navegador abrirá la aplicación. En **Ruta más corta**, prueba con
`ZAPOPAN` y `EL SALTO`. La ruta de ejemplo pasa por `TLAJOMULCO` y
tiene un costo total de 43.

En la barra lateral puedes registrar un origen y destino nuevos con un
peso positivo. Los nombres se normalizan a mayúsculas. Para un peso
decimal se acepta punto o coma. Consulta ambas tablas en **Red actual**.

`nodos.csv` contiene los tramos de ejemplo y guarda los cambios en disco.
Una sesión nueva carga el archivo una vez. Si otra sesión modificó los
datos, vuelve a abrir la página para ver los cambios antes de guardar.
Si el CSV tiene filas inválidas, la app muestra un aviso de error y
protege el archivo.

Para usar el menú anterior desde la misma carpeta:

```powershell
.\.venv\Scripts\python main.py
```

## Verificar

```powershell
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python -m unittest -v
.\.venv\Scripts\python -m flake8 .
```
