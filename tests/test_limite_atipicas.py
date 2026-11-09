"""Pruebas para la detección y limpieza de muestras atípicas (limite_atipicas).

El cálculo de límite de atípicas con la regla de Tukey (Q1 - 1.5 * IQR) fue la innovación
clave del proyecto que permitió pasar de pintar el 97 % de la imagen a aislar correctamente
el agua dulce y salada (como se detalla en el README y reporte).

Cubre:
- Exactitud de los percentiles Q1, Q3 y el límite inferior.
- Valores calculados a mano.
- Filtrado efectivo de muestras ruidosas (brillo solar, oleaje) frente al mínimo sin limpiar.
- Casos sin atípicas y casos con IQR = 0.
"""
import numpy as np
import pytest

from herramientas.analizar_confusiones import limite_atipicas


class TestLimiteAtipicas:
    """Pruebas matemáticas del cálculo de cuartiles y límite de Tukey."""

    def test_valores_a_mano_array_pequeno(self):
        """Para s = [10, 20, 30, 40]:

        np.percentile([10, 20, 30, 40], [25, 75]) da Q1 = 17.5, Q3 = 32.5.
        IQR = 32.5 - 17.5 = 15.0.
        Límite = Q1 - 1.5 * IQR = 17.5 - 22.5 = -5.0.
        """
        s = np.array([10.0, 20.0, 30.0, 40.0])
        q1, q3, lim = limite_atipicas(s)

        assert q1 == pytest.approx(17.5)
        assert q3 == pytest.approx(32.5)
        assert lim == pytest.approx(-5.0)

    def test_valores_a_mano_secuencia_uniforme(self):
        """Para valores uniformes de 0 a 100:

        Q1 = 25.0, Q3 = 75.0, IQR = 50.0.
        Límite = 25.0 - 1.5 * 50.0 = -50.0.
        """
        s = np.arange(101, dtype=np.float64)
        q1, q3, lim = limite_atipicas(s)

        assert q1 == pytest.approx(25.0)
        assert q3 == pytest.approx(75.0)
        assert lim == pytest.approx(-50.0)

    def test_varianza_cero_iqr_cero(self):
        """Si todas las muestras tienen la misma similitud, IQR = 0 y límite = Q1."""
        s = np.full(50, 92.5)
        q1, q3, lim = limite_atipicas(s)

        assert q1 == pytest.approx(92.5)
        assert q3 == pytest.approx(92.5)
        assert lim == pytest.approx(92.5)

    def test_filtrado_de_atipicas_simulacion_metodo(self, rng):
        """Simula el comportamiento real del método sobre agua ruidosa:

        - 95 % de muestras limpias agrupadas en [88 %, 98 %].
        - 5 % de muestras con ruido intenso (brillos, olas) en [30 %, 50 %].
        Verifica que:
        1. El mínimo sin limpiar sea ~30-40 %.
        2. El límite de atípicas detecte las muestras ruidosas.
        3. El umbral limpio (mínimo de las que pasan el límite) recupere el rango limpio (>= 88 %).
        """
        muestras_limpias = rng.uniform(88.0, 98.0, size=95)
        muestras_ruido = rng.uniform(30.0, 50.0, size=5)
        s = np.concatenate([muestras_limpias, muestras_ruido])

        q1, q3, lim = limite_atipicas(s)

        min_sin_limpiar = float(np.min(s))
        assert min_sin_limpiar < 50.0, "El mínimo sin limpiar debe ser bajo debido al ruido"

        # El límite debe estar entre el ruido (< 50) y las muestras limpias (~88)
        assert 50.0 < lim < 88.0

        # Filtramos muestras que quedan por debajo del límite
        limpias = s[s >= lim]
        atipicas = s[s < lim]

        assert len(atipicas) == 5, "Deben identificarse exactamente las 5 muestras ruidosas"
        assert len(limpias) == 95

        umbral_limpio = float(np.min(limpias))
        assert umbral_limpio >= 88.0, "El umbral limpio debe situarse dentro del grupo limpio"
        assert umbral_limpio > min_sin_limpiar

    def test_comportamiento_sin_atipicas(self, rng):
        """En una distribución simétrica y acotada sin colas extremas, ninguna muestra cae por debajo del límite."""
        s = rng.uniform(80.0, 95.0, size=100)
        q1, q3, lim = limite_atipicas(s)

        atipicas = s[s < lim]
        assert len(atipicas) == 0
        assert np.min(s) >= lim
