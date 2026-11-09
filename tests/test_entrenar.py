"""Pruebas para el proceso de entrenamiento y cálculo del perfil promedio (entrenar).

Cubre:
- `herramientas.analizar_confusiones.entrenar(arr, si, no)`
- Uso exclusivo de arrays sintéticos pequeños con numpy (evitando cargar datos reales pesados).
- Verificación del split estratificado (80 % entrenamiento / 20 % prueba).
- Verificación de la firma mediana 'prom', matriz de firmas de entrenamiento 'F', y similitudes 's'.
- Determinismo y reproducibilidad por fijación de semilla (random_state=42).
"""
import numpy as np
import pandas as pd
import pytest

from herramientas.analizar_confusiones import entrenar, similitud


@pytest.fixture
def dataset_sintetico_pequeno():
    """Genera una imagen sintética pequeña (12x12 píxeles con 380 bandas) y coordenadas de muestra."""
    H, W, B = 12, 12, 380
    rng = np.random.default_rng(123)

    # Creamos un cubo sintético base
    arr = np.zeros((H, W, B), dtype=np.float32)

    # Zona positiva (material objetivo 'si'): cuadrante superior izquierdo (y < 6, x < 6)
    # Firma con escalón marcado en tramo 1 (banda 70)
    firma_objetivo = np.linspace(0.1, 0.4, B, dtype=np.float32)
    firma_objetivo[70:120] += 0.5
    for y in range(6):
        for x in range(6):
            ruido = rng.normal(0, 0.01, B).astype(np.float32)
            arr[y, x] = firma_objetivo + ruido

    # Zona negativa ('no' / otros materiales): cuadrante inferior derecho (y >= 6, x >= 6)
    # Firma plana con pendiente suave distinta
    firma_otros = np.linspace(0.8, 0.2, B, dtype=np.float32)
    for y in range(6, 12):
        for x in range(6, 12):
            ruido = rng.normal(0, 0.01, B).astype(np.float32)
            arr[y, x] = firma_otros + ruido

    # Seleccionamos 20 coordenadas para 'si' y 20 para 'no'
    coords_si = [(x, y) for y in range(5) for x in range(4)]  # 20 puntos
    coords_no = [(x, y) for y in range(6, 11) for x in range(6, 10)]  # 20 puntos

    df_si = pd.DataFrame(coords_si, columns=["x", "y"])
    df_no = pd.DataFrame(coords_no, columns=["x", "y"])

    return arr, df_si, df_no, firma_objetivo


class TestEntrenar:
    """Verificación de la función entrenar."""

    def test_formas_y_tipos_de_salida(self, dataset_sintetico_pequeno):
        """Con 20 muestras positivas y 20 negativas, el 80 % de entrenamiento debe contener 16 muestras positivas."""
        arr, df_si, df_no, _ = dataset_sintetico_pequeno

        prom, F, s = entrenar(arr, df_si, df_no)

        # 80 % de 20 muestras positivas = 16
        assert F.shape == (16, 380)
        assert prom.shape == (380,)
        assert s.shape == (16,)

        assert isinstance(prom, np.ndarray)
        assert isinstance(F, np.ndarray)
        assert isinstance(s, np.ndarray)

    def test_consistencia_matematica_prom_y_similitud(self, dataset_sintetico_pequeno):
        """Verifica que:

        1. 'prom' es exactamente la mediana por bandas de las firmas de entrenamiento 'F'.
        2. 's' es exactamente 'similitud(prom, F)'.
        3. Todos los valores de 's' están en el intervalo [0, 100].
        """
        arr, df_si, df_no, _ = dataset_sintetico_pequeno

        prom, F, s = entrenar(arr, df_si, df_no)

        # La firma promedio es la mediana
        mediana_esperada = np.median(F, axis=0)
        np.testing.assert_allclose(prom, mediana_esperada)

        # Las similitudes coinciden con la función similitud
        sim_esperada = similitud(prom, F)
        np.testing.assert_allclose(s, sim_esperada)

        # Rango válido de porcentaje
        assert np.all(s >= 0.0)
        assert np.all(s <= 100.0)

    def test_determinismo_reproducibilidad(self, dataset_sintetico_pequeno):
        """Dado que random_state=42 está prefijado en entrenar, ejecuciones consecutivas deben ser idénticas bit a bit."""
        arr, df_si, df_no, _ = dataset_sintetico_pequeno

        prom1, F1, s1 = entrenar(arr, df_si, df_no)
        prom2, F2, s2 = entrenar(arr, df_si, df_no)

        np.testing.assert_array_equal(prom1, prom2)
        np.testing.assert_array_equal(F1, F2)
        np.testing.assert_array_equal(s1, s2)

    def test_muestras_positivas_homogeneas_producen_similitud_100(self):
        """Si todas las muestras positivas tienen exactamente la misma firma espectral,

        su firma promedio es idéntica a cada muestra y todas las similitudes en 's' son 100 %.
        """
        H, W, B = 8, 8, 380
        arr = np.zeros((H, W, B), dtype=np.float32)

        firma_constante = np.full(B, 0.5, dtype=np.float32)
        # Asignamos esa firma a los píxeles de si
        for y in range(4):
            for x in range(4):
                arr[y, x] = firma_constante

        # Otros píxeles con otra firma
        arr[4:, 4:] = np.full(B, 0.1, dtype=np.float32)

        df_si = pd.DataFrame([(x, y) for y in range(4) for x in range(3)], columns=["x", "y"])  # 12 muestras
        df_no = pd.DataFrame([(x, y) for y in range(4, 8) for x in range(4, 7)], columns=["x", "y"])  # 12 muestras

        prom, F, s = entrenar(arr, df_si, df_no)

        np.testing.assert_allclose(prom, firma_constante)
        np.testing.assert_allclose(s, 100.0)

    def test_tamano_minimo_admisible_estratificado(self):
        """Prueba con el tamaño mínimo para train_test_split estratificado con test_size=0.20 (5 muestras por clase)."""
        H, W, B = 5, 5, 380
        arr = np.ones((H, W, B), dtype=np.float32)

        # 5 muestras para cada clase: 4 entrenamiento (80 %) y 1 prueba (20 %)
        df_si = pd.DataFrame({"x": [0, 1, 2, 3, 4], "y": [0, 0, 0, 0, 0]})
        df_no = pd.DataFrame({"x": [0, 1, 2, 3, 4], "y": [1, 1, 1, 1, 1]})

        prom, F, s = entrenar(arr, df_si, df_no)
        assert F.shape == (4, 380)
        assert s.shape == (4,)
