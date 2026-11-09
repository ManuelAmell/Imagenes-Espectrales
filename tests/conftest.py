"""Configuración global y fixtures para la suite de pruebas del método de longitud de arco."""
import os
import sys
import numpy as np
import pytest

# Asegurar que la raíz del proyecto esté en el PYTHONPATH
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

import herramientas.generar_notebooks as gn


@pytest.fixture(scope="session")
def funciones_notebook():
    """Extrae las funciones 'long_arco' y 'similitud_porcentual' generadas en las plantillas de notebooks.

    generar_notebooks.py define estas funciones dentro de cadenas de celdas de notebook
    en 'celdas_inicio'. Esta fixture extrae dinámicamente el código y lo compila
    para verificar directamente la implementación que se inyecta en los cuadernos.
    """
    material_dummy = [("agua_salada", "agua salada", (0, 255, 255))]
    celdas = gn.celdas_inicio(4, material_dummy, "recuadros", False)
    celda_metodo = next(c for c in celdas if "def similitud_porcentual" in c.source)
    namespace = {"np": np}
    exec(celda_metodo.source, namespace)
    return {
        "long_arco": namespace["long_arco"],
        "similitud_porcentual": namespace["similitud_porcentual"],
    }


@pytest.fixture
def firma_plana_380():
    """Firma espectral constante de 380 bandas."""
    return np.full(380, 0.45, dtype=np.float64)


@pytest.fixture
def rng():
    """Generador pseudoaleatorio determinista para pruebas repetibles."""
    return np.random.default_rng(42)
