"""Pruebas para el cálculo de la longitud de arco del método hiperespectral.

Cubre las dos implementaciones del repositorio:
1. `herramientas.analizar_confusiones.long_arco(R)`: `np.sum(np.abs(np.diff(R, axis=-1)), axis=-1)`
2. `herramientas.generar_figuras.long_arco(r)`: `float(np.sum(np.abs(np.diff(r))))`

Incluye:
- Valores calculados a mano: firmas planas (-> 0), escalones, series crecientes, decrecientes y alternadas.
- Comparación entre ambas implementaciones:
  * Coincidencia numérica exacta sobre entradas unidimensionales (1D).
  * Documentación del hallazgo/discrepancia en entradas bidimensionales (2D):
    `analizar_confusiones` opera vectorialmente sobre la última dimensión (`axis=-1`) devolviendo un
    array con la longitud de arco de cada firma independiente; mientras que `generar_figuras` suma
    globalmente todo el array aplanado sin especificar `axis` en `np.sum` y convierte el total a un `float` escalar.
"""
import numpy as np
import pytest

from herramientas.analizar_confusiones import long_arco as long_arco_ac
from herramientas.generar_figuras import long_arco as long_arco_gf


class TestLongArcoValoresConocidos:
    """Verificación con valores calculados a mano sobre entradas 1D."""

    @pytest.mark.parametrize("long_arco_fn", [long_arco_ac, long_arco_gf], ids=["analizar_confusiones", "generar_figuras"])
    def test_firma_plana_da_cero(self, long_arco_fn):
        """Una firma espectral constante no tiene variación entre bandas vecinas; la longitud de arco debe ser 0."""
        # Todos ceros
        assert long_arco_fn(np.zeros(50, dtype=np.float64)) == 0.0
        # Todos unos
        assert long_arco_fn(np.ones(100, dtype=np.float64)) == 0.0
        # Valor constante arbitrario
        assert long_arco_fn(np.full(380, 0.725)) == 0.0

    @pytest.mark.parametrize("long_arco_fn", [long_arco_ac, long_arco_gf], ids=["analizar_confusiones", "generar_figuras"])
    def test_escalon_simple(self, long_arco_fn):
        """Un escalón unitario tiene una única diferencia no nula de magnitud 1.0."""
        # [0, 0, 1, 1] -> diffs: [0, 1, 0] -> sum(|diffs|) = 1.0
        escalon = np.array([0.0, 0.0, 1.0, 1.0])
        assert long_arco_fn(escalon) == pytest.approx(1.0)

    @pytest.mark.parametrize("long_arco_fn", [long_arco_ac, long_arco_gf], ids=["analizar_confusiones", "generar_figuras"])
    def test_escalon_pulso_y_magnitud(self, long_arco_fn):
        """Un pulso que sube de 0 a 3 y baja a 0 tiene saltos |+3| + |-3| = 6.0."""
        pulso = np.array([0.0, 3.0, 3.0, 0.0])
        assert long_arco_fn(pulso) == pytest.approx(6.0)

        # Escalón con salto negativo: [5.0, 5.0, 2.0, 2.0] -> diffs: [0, -3, 0] -> sum = 3.0
        escalon_bajada = np.array([5.0, 5.0, 2.0, 2.0])
        assert long_arco_fn(escalon_bajada) == pytest.approx(3.0)

    @pytest.mark.parametrize("long_arco_fn", [long_arco_ac, long_arco_gf], ids=["analizar_confusiones", "generar_figuras"])
    def test_series_sencillas(self, long_arco_fn):
        """Series lineales crecientes, decrecientes y alternadas con resultado conocido a mano."""
        # Serie creciente: [0, 1, 2, 3, 4] -> diffs: [1, 1, 1, 1] -> sum = 4.0
        creciente = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        assert long_arco_fn(creciente) == pytest.approx(4.0)

        # Serie decreciente: [10, 8, 6, 4] -> diffs: [-2, -2, -2] -> sum(|diffs|) = 6.0
        decreciente = np.array([10.0, 8.0, 6.0, 4.0])
        assert long_arco_fn(decreciente) == pytest.approx(6.0)

        # Serie alternada / zig-zag: [1, 3, 2, 5] -> diffs: [+2, -1, +3] -> |+2| + |-1| + |+3| = 6.0
        zigzag = np.array([1.0, 3.0, 2.0, 5.0])
        assert long_arco_fn(zigzag) == pytest.approx(6.0)

    @pytest.mark.parametrize("long_arco_fn", [long_arco_ac, long_arco_gf], ids=["analizar_confusiones", "generar_figuras"])
    def test_casos_borde_unidimensionales(self, long_arco_fn):
        """Un solo elemento no produce diferencias; dos elementos producen exactamente |a - b|."""
        # Un solo elemento -> diff vacía -> suma 0.0
        un_elemento = np.array([42.0])
        assert long_arco_fn(un_elemento) == 0.0

        # Dos elementos -> |4.5 - 1.0| = 3.5
        dos_elementos = np.array([1.0, 4.5])
        assert long_arco_fn(dos_elementos) == pytest.approx(3.5)


class TestComparacionAmbasImplementaciones:
    """Verifica la coincidencia de ambas implementaciones y documenta sus diferencias."""

    def test_coincidencia_numerica_en_1d(self, rng):
        """En entradas 1D, ambas implementaciones producen exactamente el mismo valor numérico."""
        # Comparación sobre 100 firmas sintéticas 1D aleatorias
        for _ in range(100):
            longitud = rng.integers(2, 381)
            firma = rng.uniform(0.0, 1.0, size=longitud)
            val_ac = float(long_arco_ac(firma))
            val_gf = long_arco_gf(firma)
            assert val_ac == pytest.approx(val_gf, rel=1e-12, abs=1e-12)

    def test_discrepancia_tipo_retorno_en_1d(self):
        """Hallazgo de tipado:

        - generar_figuras.long_arco siempre devuelve un `float` primitivo de Python.
        - analizar_confusiones.long_arco preserva el tipo numpy (e.g. np.int64 o np.float64).
        """
        entrada_int = np.array([1, 4, 2])
        res_ac = long_arco_ac(entrada_int)
        res_gf = long_arco_gf(entrada_int)

        assert res_ac == 5
        assert res_gf == 5.0
        assert isinstance(res_gf, float)
        assert isinstance(res_ac, (np.integer, np.int64))

    def test_hallazgo_discrepancia_dimensional_en_2d(self):
        """HALLAZGO / DISCREPANCIA DOCUMENTADA:

        Comportamiento frente a entradas 2D (varias firmas apiladas):
        - `analizar_confusiones.long_arco` incluye `axis=-1`:
            np.sum(np.abs(np.diff(R, axis=-1)), axis=-1)
          Por ende, opera por filas y devuelve un array 1D con la longitud de arco
          de cada firma independiente (diseñado para evaluar múltiples píxeles a la vez).

        - `generar_figuras.long_arco` hace:
            float(np.sum(np.abs(np.diff(r))))
          np.diff calcula las diferencias por filas (axis=-1 por omisión de numpy), pero
          np.sum() no tiene argumento de eje, por lo que suma TODOS los elementos de la
          matriz completa y hace cast a `float`, devolviendo un único número escalar.

        Demostración con una matriz 2D de (2 firmas, 4 bandas):
          Fila 0: [1, 3, 2, 5] -> longitud de arco = |2| + |1| + |3| = 6.0
          Fila 1: [0, 1, 0, 1] -> longitud de arco = |1| + |1| + |1| = 3.0
        """
        x_2d = np.array([
            [1.0, 3.0, 2.0, 5.0],
            [0.0, 1.0, 0.0, 1.0],
        ])

        res_ac = long_arco_ac(x_2d)
        res_gf = long_arco_gf(x_2d)

        # analizar_confusiones devuelve vector con una longitud por cada fila
        assert isinstance(res_ac, np.ndarray)
        assert res_ac.shape == (2,)
        np.testing.assert_allclose(res_ac, [6.0, 3.0])

        # generar_figuras colapsa todo a un único escalar float (6.0 + 3.0 = 9.0)
        assert isinstance(res_gf, float)
        assert res_gf == pytest.approx(9.0)

        # La suma del resultado vectorial de analizar_confusiones coincide con el escalar de generar_figuras
        assert float(np.sum(res_ac)) == pytest.approx(res_gf)

    def test_comparacion_con_long_arco_de_cuadernos(self, funciones_notebook, rng):
        """Verifica que la función `long_arco` inyectada en los cuadernos también coincida en 1D."""
        long_arco_nb = funciones_notebook["long_arco"]
        firma = rng.uniform(0.0, 1.0, size=380)

        val_nb = float(long_arco_nb(firma))
        val_ac = float(long_arco_ac(firma))
        val_gf = long_arco_gf(firma)

        assert val_nb == pytest.approx(val_ac)
        assert val_nb == pytest.approx(val_gf)
