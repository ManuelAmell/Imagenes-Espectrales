"""Pruebas para 'dos_numeros', 'similitud' y 'similitud_porcentual'.

Verifica el núcleo del método:
- dos_numeros: reducción de firmas hiperespectrales de 380 bandas a 2 longitudes de arco
  en los tramos específicos de bandas 40-140 y 150-270 (descritos en el README).
- similitud (analizar_confusiones.py): comparación de firmas completas usando dos_numeros.
- similitud_porcentual (generar_notebooks.py): comparación vector a vector (A vs B).

Requisitos cubiertos:
- Casos idénticos -> 100 %.
- Simetría: similitud(A, B) == similitud(B, A).
- Valores calculados a mano.
- Invarianza a bandas fuera de los dos tramos.
- Soporte de dimensiones: 1D, 2D (matrices de firmas) y 3D (imágenes).
"""
import numpy as np
import pytest

from herramientas.analizar_confusiones import dos_numeros, similitud, LIMS


class TestDosNumeros:
    """Pruebas sobre la función dos_numeros y la selección de bandas."""

    def test_limites_de_bandas_segun_metodo(self):
        """Los tramos definidos en el código deben coincidir con la documentación (README):

        Tramo 1: bandas 40 a 140 (100 bandas de longitud).
        Tramo 2: bandas 150 a 270 (120 bandas de longitud).
        """
        assert LIMS == (40, 140, 150, 270)
        tramo1_len = LIMS[1] - LIMS[0]
        tramo2_len = LIMS[3] - LIMS[2]
        assert tramo1_len == 100
        assert tramo2_len == 120

    def test_firma_plana_dos_numeros_cero(self, firma_plana_380):
        """Una firma constante en las 380 bandas produce (0.0, 0.0)."""
        res = dos_numeros(firma_plana_380)
        assert res.shape == (2,)
        np.testing.assert_allclose(res, [0.0, 0.0])

    def test_valores_conocidos_a_mano(self):
        """Verifica que escalones en bandas específicas impacten únicamente el tramo correspondiente."""
        firma = np.zeros(380, dtype=np.float64)

        # Escalón de altura 4.0 en la banda 60 (dentro del tramo 1: 40-140)
        firma[60:] = 4.0
        res = dos_numeros(firma)
        np.testing.assert_allclose(res, [4.0, 0.0])

        # Escalón adicional de altura 2.5 en la banda 200 (dentro del tramo 2: 150-270)
        firma[200:] += 2.5
        res = dos_numeros(firma)
        np.testing.assert_allclose(res, [4.0, 2.5])

    def test_invarianza_a_bandas_fuera_de_tramos(self):
        """Cualquier perturbación en bandas [0:40], [140:150] y [270:380] es ignorada por el método."""
        base = np.zeros(380, dtype=np.float64)
        base[80:100] = 1.0  # escalón en tramo 1: longitud de arco = 2.0 (sube 1 y baja 1)
        base[180:200] = 2.0  # escalón en tramo 2: longitud de arco = 4.0 (sube 2 y baja 2)

        esperado = dos_numeros(base)
        np.testing.assert_allclose(esperado, [2.0, 4.0])

        # Modificamos bandas previas a 40
        modificado = base.copy()
        modificado[:40] = np.linspace(0, 10, 40)
        np.testing.assert_allclose(dos_numeros(modificado), esperado)

        # Modificamos la brecha de bandas 140 a 150
        modificado = base.copy()
        modificado[140:150] = 999.0
        np.testing.assert_allclose(dos_numeros(modificado), esperado)

        # Modificamos bandas posteriores a 270
        modificado = base.copy()
        modificado[270:] = np.random.default_rng(0).uniform(0, 50, 110)
        np.testing.assert_allclose(dos_numeros(modificado), esperado)

    def test_formas_dimensionales(self, rng):
        """dos_numeros preserva dimensiones espaciales y apila las 2 longitudes al final."""
        # 1D: (380,) -> (2,)
        f_1d = rng.uniform(0, 1, 380)
        assert dos_numeros(f_1d).shape == (2,)

        # 2D: (N, 380) -> (N, 2)
        f_2d = rng.uniform(0, 1, (15, 380))
        assert dos_numeros(f_2d).shape == (15, 2)

        # 3D: (H, W, 380) -> (H, W, 2)
        f_3d = rng.uniform(0, 1, (4, 5, 380))
        assert dos_numeros(f_3d).shape == (4, 5, 2)


class TestSimilitudYSimilitudPorcentual:
    """Pruebas de similitud y similitud_porcentual (casos idénticos, simetría y valores a mano)."""

    def test_casos_identicos_producen_100_por_ciento(self, funciones_notebook, rng):
        """Si dos firmas o dos vectores son idénticos, la similitud es exactamente 100 %."""
        sim_pct = funciones_notebook["similitud_porcentual"]

        # Vectores 2D idénticos directos
        assert sim_pct([5.0, 12.0], [5.0, 12.0]) == pytest.approx(100.0)
        assert sim_pct(np.array([0.0, 0.0]), np.array([0.0, 0.0])) == pytest.approx(100.0)

        # Firmas espectrales 1D idénticas
        f1 = rng.uniform(0.1, 0.9, 380)
        assert similitud(f1, f1) == pytest.approx(100.0)

        # Matriz 2D de firmas idénticas al promedio
        f_mat = np.tile(f1, (8, 1))
        res = similitud(f1, f_mat)
        assert res.shape == (8,)
        np.testing.assert_allclose(res, 100.0)

    def test_simetria_matematica(self, funciones_notebook, rng):
        """La fórmula:

            100 * (1 - |A - B| / (|A| + |B| + 1e-9))
        es matemáticamente simétrica ya que |A - B| == |B - A| y |A| + |B| == |B| + |A|.
        """
        sim_pct = funciones_notebook["similitud_porcentual"]

        # Prueba sobre similitud_porcentual
        for _ in range(50):
            a = rng.uniform(0.01, 20.0, 2)
            b = rng.uniform(0.01, 20.0, 2)
            assert sim_pct(a, b) == pytest.approx(sim_pct(b, a), rel=1e-12, abs=1e-12)

        # Prueba sobre similitud con firmas completas
        f_a = rng.uniform(0.0, 1.0, 380)
        f_b = rng.uniform(0.0, 1.0, 380)
        assert similitud(f_a, f_b) == pytest.approx(similitud(f_b, f_a), rel=1e-12, abs=1e-12)

    def test_valores_a_mano_similitud_porcentual(self, funciones_notebook):
        """Casos con cálculo manual exacto paso a paso."""
        sim_pct = funciones_notebook["similitud_porcentual"]

        # Caso extremo 1: uno tiene ceros y el otro valores positivos
        # A = [10.0, 20.0], B = [0.0, 0.0]
        # Para cada componente: 100 * (1 - 10 / (10 + 1e-9)) ≈ 0.0
        # Promedio = 0.0 %
        assert sim_pct([10.0, 20.0], [0.0, 0.0]) == pytest.approx(0.0, abs=1e-5)

        # Caso intermedio calculado a mano:
        # A = [10.0, 30.0], B = [20.0, 10.0]
        # Componente 1: |10 - 20| / (10 + 20) = 10 / 30 = 1/3 -> 100 * (1 - 1/3) = 66.66667 %
        # Componente 2: |30 - 10| / (30 + 10) = 20 / 40 = 1/2 -> 100 * (1 - 1/2) = 50.0 %
        # Media = (66.6666667 + 50.0) / 2 = 58.3333333 %
        esperado = (100.0 * (2.0 / 3.0) + 50.0) / 2.0
        assert sim_pct([10.0, 30.0], [20.0, 10.0]) == pytest.approx(esperado, abs=1e-5)

    def test_equivalencia_entre_similitud_y_similitud_porcentual(self, funciones_notebook, rng):
        """Verifica que 'similitud(prom, F)' es exactamente 'similitud_porcentual(dos_numeros(prom), dos_numeros(F))'."""
        sim_pct = funciones_notebook["similitud_porcentual"]

        for _ in range(25):
            prom = rng.uniform(0.1, 0.8, 380)
            f = rng.uniform(0.1, 0.8, 380)

            sim_directa = similitud(prom, f)
            sim_descompuesta = sim_pct(dos_numeros(prom), dos_numeros(f))

            assert float(sim_directa) == pytest.approx(sim_descompuesta, rel=1e-12, abs=1e-12)

    def test_estabilidad_numerica_con_epsilon(self, funciones_notebook):
        """El término 1e-9 en el denominador previene división por cero cuando A=0 y B=0."""
        sim_pct = funciones_notebook["similitud_porcentual"]
        # Sin 1e-9 habría NaN por 0/0. Con 1e-9 da 100 * (1 - 0 / 1e-9) = 100.0
        resultado = sim_pct([0.0, 0.0], [0.0, 0.0])
        assert not np.isnan(resultado)
        assert resultado == pytest.approx(100.0)
