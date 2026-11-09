"""Pruebas para el manejo de recuadros y píxeles muestrales.

Cubre:
- `roi_a_recuadros` (herramientas/marcar_recuadros.py)
- `leer_recuadros` y `agregar_recuadros` (herramientas/marcar_recuadros.py) usando `tmp_path` de pytest.
- `pixeles_de` (herramientas/analizar_confusiones.py) para la extracción de píxeles con máscara.
"""
import os
import numpy as np
import pandas as pd
import pytest

from herramientas.marcar_recuadros import (
    roi_a_recuadros,
    leer_recuadros,
    agregar_recuadros,
    ruta_imagen,
    ruta_csv,
    COLUMNAS,
    RAIZ,
)
from herramientas.analizar_confusiones import pixeles_de


class TestRoiARecuadros:
    """Verificación de conversión de ROIs de OpenCV a tuplas de recuadros (x1, y1, x2, y2, nombre)."""

    def test_conversion_basica_y_nombres(self):
        """Convierte (x, y, w, h) a (x1, y1, x1+w, y1+h) con numeración correlativa desde 'desde'."""
        rois = [
            (10, 20, 30, 40),
            (100, 150, 20, 25),
        ]
        resultado = roi_a_recuadros(rois, material="agua_salada", desde=1)

        esperado = [
            (10, 20, 40, 60, "agua_salada 1"),
            (100, 150, 120, 175, "agua_salada 2"),
        ]
        assert resultado == esperado

    def test_offset_desde_personalizado(self):
        """Si ya existen 5 recuadros previos, los nuevos inician en desde=6."""
        rois = [(5, 5, 10, 10), (25, 25, 15, 15)]
        resultado = roi_a_recuadros(rois, material="asfalto", desde=6)

        assert resultado[0][4] == "asfalto 6"
        assert resultado[1][4] == "asfalto 7"

    def test_filtrado_rois_degeneradas(self):
        """Los clics erróneos o rectángulos con ancho/alto <= 0 deben ignorarse."""
        rois = [
            (10, 10, 0, 20),    # w = 0
            (10, 10, 20, 0),    # h = 0
            (10, 10, -5, 20),   # w negativo
            (10, 10, 20, -5),   # h negativo
            (0, 0, 0, 0),       # clic accidental
            (5, 5, 12, 18),     # válida
        ]
        resultado = roi_a_recuadros(rois, material="techo", desde=1)
        assert len(resultado) == 1
        assert resultado[0] == (5, 5, 17, 23, "techo 1")

    def test_lista_vacia(self):
        """Lista vacía devuelve lista vacía."""
        assert roi_a_recuadros([], material="vegetacion", desde=1) == []


class TestLeerYAgregarRecuadrosCSV:
    """Verificación de persistencia CSV de recuadros con tmp_path (sin tocar archivos reales de datos/)."""

    def test_leer_archivo_inexistente_retorna_lista_vacia(self, tmp_path):
        """Si el archivo CSV no existe, leer_recuadros devuelve [] sin lanzar excepción."""
        archivo_inexistente = str(tmp_path / "no_existe.csv")
        assert leer_recuadros(archivo_inexistente) == []

    def test_agregar_crea_archivo_y_encabezado(self, tmp_path):
        """La primera llamada crea el archivo, directorios padres si no existen, y el encabezado."""
        archivo = str(tmp_path / "subcarpeta" / "recuadros.csv")
        datos = [
            (10, 20, 30, 40, "agua 1"),
            (50, 60, 70, 80, "agua 2"),
        ]

        agregar_recuadros(archivo, datos)

        assert os.path.exists(archivo)
        # Verificar contenido leído
        leidos = leer_recuadros(archivo)
        assert leidos == datos

        # Verificar encabezado exacto
        with open(archivo, "r") as f:
            primera_linea = f.readline().strip().split(",")
        assert primera_linea == COLUMNAS

    def test_agregar_consecutivo_anexa_sin_duplicar_encabezado(self, tmp_path):
        """Llamadas subsecuentes a agregar_recuadros agregan registros al final sin repetir encabezado."""
        archivo = str(tmp_path / "recuadros.csv")
        lote1 = [(0, 0, 10, 10, "mat 1")]
        lote2 = [(20, 20, 30, 30, "mat 2"), (40, 40, 50, 50, "mat 3")]

        agregar_recuadros(archivo, lote1)
        agregar_recuadros(archivo, lote2)

        leidos = leer_recuadros(archivo)
        assert len(leidos) == 3
        assert leidos == lote1 + lote2

        # Contar encabezados en el archivo bruto
        with open(archivo, "r") as f:
            lineas = [line.strip() for line in f if line.strip()]
        # Primera línea es el encabezado, seguidas por exactamente 3 líneas de datos
        assert lineas[0] == ",".join(COLUMNAS)
        assert len(lineas) == 4


class TestPixelesDe:
    """Verificación de la función pixeles_de (extracción de coordenadas y orden)."""

    def test_extraccion_coordenadas_y_orden(self):
        """pixeles_de itera primero por filas (y) y luego por columnas (x)."""
        rec = pd.DataFrame([{"x1": 1, "y1": 2, "x2": 3, "y2": 4}])  # x: [1, 2], y: [2, 3]
        con_datos = np.ones((10, 10), dtype=bool)

        df_pix = pixeles_de(rec, con_datos)

        esperado = [
            (1, 2), (2, 2),  # y = 2
            (1, 3), (2, 3),  # y = 3
        ]
        assert df_pix.to_records(index=False).tolist() == esperado

    def test_filtrado_por_mascara_con_datos(self):
        """Los píxeles donde con_datos es False (zonas negras sin datos) son excluidos."""
        rec = pd.DataFrame([{"x1": 0, "y1": 0, "x2": 3, "y2": 3}])
        con_datos = np.ones((5, 5), dtype=bool)
        # Marcamos píxeles sin datos
        con_datos[1, 1] = False
        con_datos[2, 2] = False

        df_pix = pixeles_de(rec, con_datos)
        assert len(df_pix) == 9 - 2  # 3x3 - 2 = 7 píxeles
        pix_set = set(zip(df_pix.x, df_pix.y))
        assert (1, 1) not in pix_set
        assert (2, 2) not in pix_set
        assert (0, 0) in pix_set

    def test_recuadros_multiples(self):
        """Maneja múltiples recuadros en un DataFrame."""
        rec = pd.DataFrame([
            {"x1": 0, "y1": 0, "x2": 2, "y2": 1},  # (0, 0), (1, 0) -> 2 píxeles
            {"x1": 5, "y1": 5, "x2": 6, "y2": 7},  # (5, 5), (5, 6) -> 2 píxeles
        ])
        con_datos = np.ones((10, 10), dtype=bool)

        df_pix = pixeles_de(rec, con_datos)
        assert len(df_pix) == 4
        assert set(zip(df_pix.x, df_pix.y)) == {(0, 0), (1, 0), (5, 5), (5, 6)}


class TestRutasRecuadros:
    """Verificación de generación de rutas de datos e imágenes para recuadros."""

    def test_ruta_imagen(self):
        """Genera la ruta esperada dentro del directorio datos/."""
        ruta = ruta_imagen(4)
        assert ruta == os.path.join(RAIZ, "datos", "cartagena4", "imagen")

    def test_ruta_csv(self):
        """Genera la ruta esperada para el CSV de un material dentro de recuadros/."""
        ruta = ruta_csv(3, "agua_dulce_rio")
        assert ruta == os.path.join(RAIZ, "datos", "cartagena3", "recuadros", "agua_dulce_rio.csv")

