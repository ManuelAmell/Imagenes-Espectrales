# Antes y después: cada imagen original y su imagen pintada

A la izquierda está la imagen original y a la derecha la imagen que sale del notebook, con los píxeles del
material pintados. El método es la longitud de arco con limpieza de muestras atípicas (ver el
[README](../README.md) y [docs/explicacion_metodo.pdf](../docs/explicacion_metodo.pdf)).

**Colores:** agua salada en **cian** · agua dulce en **magenta**.

| Imagen | Material | Precisión | % de la imagen pintado | Notebook |
|---|---|---|---|---|
| cartagena2 | Agua salada | 0,84 | 49 % | [cartagena2.ipynb](../notebooks/cartagena2.ipynb) |
| cartagena3 | Agua dulce: río | 1,00 | 19 % | [cartagena3.ipynb](../notebooks/cartagena3.ipynb) |
| cartagena3 | Agua dulce: laguna café | 0,98 | 11 % | [cartagena3.ipynb](../notebooks/cartagena3.ipynb) |
| cartagena4 | Agua salada | 1,00 | 39 % | [cartagena4.ipynb](../notebooks/cartagena4.ipynb) |

---

## cartagena1 · barrio urbano

| Original | Pintada |
|---|---|
| <img src="../datos/cartagena1/imagen/cartagena1.png" width="400"> | *En preparación* |

No tiene agua. Sus materiales (asfalto, techos de concreto, lámina y teja, vegetación) se están marcando en la
rama `DatosCSV`; su imagen pintada se agrega aquí cuando esas muestras se unan a `master`.

## cartagena2 · patio de contenedores y mar

| Original | Pintada: agua salada |
|---|---|
| <img src="../datos/cartagena2/imagen/cartagena2.png" width="400"> | <img src="cartagena2_agua_salada.png" width="400"> |

El mar queda marcado. Quedan algunas manchas sueltas sobre el patio de contenedores.
La imagen original se ve oscura porque se armó con las bandas 29, 50 y 70 (no venía en color).

## cartagena3 · río, laguna café y manglar

| Original | Pintada: río y laguna juntos |
|---|---|
| <img src="../datos/cartagena3/imagen/cartagena3.png" width="400"> | <img src="cartagena3_final.png" width="400"> |

| Solo el río | Solo la laguna café |
|---|---|
| <img src="cartagena3_agua_dulce_rio.png" width="400"> | <img src="cartagena3_agua_dulce_laguna.png" width="400"> |

El río se marca casi sin tocar la tierra. La laguna se marca en su mayor parte, aunque se queda corta en la
punta de abajo.

## cartagena4 · puerto y mar

| Original | Pintada: agua salada |
|---|---|
| <img src="../datos/cartagena4/imagen/cartagena4.png" width="400"> | <img src="cartagena4_agua_salada.png" width="400"> |

El mar queda marcado casi por completo y la tierra queda limpia, salvo algunas líneas sueltas de sombras.
