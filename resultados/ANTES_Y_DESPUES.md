# Antes y después: cada imagen original y su imagen pintada

A la izquierda está la imagen original y a la derecha la imagen que sale del notebook, con los píxeles del
material pintados. El método es la longitud de arco con limpieza de muestras atípicas (ver el
[README](../README.md) y [docs/explicacion_metodo.pdf](../docs/explicacion_metodo.pdf)).

**Colores del agua:** agua salada en **cian** · agua dulce en **magenta**.
**Colores de los materiales:** cada mapa trae su leyenda debajo (el color depende de los materiales de esa imagen).

| Imagen | Material | Precisión | % de la imagen pintado | Notebook |
|---|---|---|---|---|
| cartagena2 | Agua salada | 0,84 | 49 % | [cartagena2.ipynb](../notebooks/cartagena2.ipynb) |
| cartagena3 | Agua dulce: río | 1,00 | 19 % | [cartagena3.ipynb](../notebooks/cartagena3.ipynb) |
| cartagena3 | Agua dulce: laguna café | 0,98 | 11 % | [cartagena3.ipynb](../notebooks/cartagena3.ipynb) |
| cartagena4 | Agua salada | 1,00 | 39 % | [cartagena4.ipynb](../notebooks/cartagena4.ipynb) |
| cartagena1 | Asfalto | 1,00 | 17 % | [cartagena1_materiales.ipynb](../notebooks/cartagena1_materiales.ipynb) |
| cartagena1 | Techo de concreto | 1,00 | 14 % | [cartagena1_materiales.ipynb](../notebooks/cartagena1_materiales.ipynb) |
| cartagena1 | Techo de lámina | 0,77 | 11 % | [cartagena1_materiales.ipynb](../notebooks/cartagena1_materiales.ipynb) |
| cartagena1 | Techo de teja | 0,56 | 30 % | [cartagena1_materiales.ipynb](../notebooks/cartagena1_materiales.ipynb) |
| cartagena1 | Vegetación | 0,72 | 12 % | [cartagena1_materiales.ipynb](../notebooks/cartagena1_materiales.ipynb) |
| cartagena3 | Asfalto | 1,00 | 4 % | [cartagena3_materiales.ipynb](../notebooks/cartagena3_materiales.ipynb) |
| cartagena3 | Vegetación | 1,00 | 51 % | [cartagena3_materiales.ipynb](../notebooks/cartagena3_materiales.ipynb) |
| cartagena4 | Asfalto | 1,00 | 35 % | [cartagena4_materiales.ipynb](../notebooks/cartagena4_materiales.ipynb) |
| cartagena4 | Techo de concreto | 0,98 | 6 % | [cartagena4_materiales.ipynb](../notebooks/cartagena4_materiales.ipynb) |
| cartagena4 | Vegetación | 0,56 | 16 % | [cartagena4_materiales.ipynb](../notebooks/cartagena4_materiales.ipynb) |

En los mapas de materiales, cada material se compara contra los demás de la misma imagen, así que una precisión
de 1,00 solo dice que se separa bien de esos otros materiales. Lo que no se marcó (agua en esos mapas, asbesto, tierra,
contenedores) se pinta como el material más parecido.

---

## cartagena1 · barrio urbano

| Original | Pintada |
|---|---|
| <img src="../datos/cartagena1/imagen/cartagena1.png" width="400"> | <img src="cartagena1_materiales_final.png" width="400"> |

🟥 asfalto · 🟨 techo de concreto · 🟩 techo de lámina · 🟧 techo de teja · 🟪 vegetación

No tiene agua. Las calles (asfalto) y los árboles (vegetación) se marcan bien; la teja se extiende de más
sobre otros techos.

## cartagena2 · patio de contenedores y mar

| Original | Pintada: agua salada |
|---|---|
| <img src="../datos/cartagena2/imagen/cartagena2.png" width="400"> | <img src="cartagena2_agua_salada.png" width="400"> |

El mar queda marcado. Quedan algunas manchas sueltas sobre el patio de contenedores.
La imagen original se ve oscura porque se armó con las bandas 29, 50 y 70 (no venía en color).

De materiales solo se marcó asfalto, y hacen falta al menos 2 para compararlos, así que c2 no tiene mapa de materiales.

## cartagena3 · río, laguna café y manglar

| Original | Pintada: río y laguna juntos |
|---|---|
| <img src="../datos/cartagena3/imagen/cartagena3.png" width="400"> | <img src="cartagena3_final.png" width="400"> |

| Solo el río | Solo la laguna café |
|---|---|
| <img src="cartagena3_agua_dulce_rio.png" width="400"> | <img src="cartagena3_agua_dulce_laguna.png" width="400"> |

El río se marca casi sin tocar la tierra. La laguna se marca en su mayor parte, aunque se queda corta en la
punta de abajo.

| Original | Pintada: materiales |
|---|---|
| <img src="../datos/cartagena3/imagen/cartagena3.png" width="400"> | <img src="cartagena3_materiales_final.png" width="400"> |

🟥 asfalto · 🟨 vegetación

El manglar se marca como vegetación. Como solo hay 2 materiales, las bodegas también salen como vegetación y
parte del río como asfalto (el agua va en el otro notebook).

## cartagena4 · puerto y mar

| Original | Pintada: agua salada |
|---|---|
| <img src="../datos/cartagena4/imagen/cartagena4.png" width="400"> | <img src="cartagena4_agua_salada.png" width="400"> |

El mar queda marcado casi por completo y la tierra queda limpia, salvo algunas líneas sueltas de sombras.

| Original | Pintada: materiales |
|---|---|
| <img src="../datos/cartagena4/imagen/cartagena4.png" width="400"> | <img src="cartagena4_materiales_final.png" width="400"> |

🟥 asfalto · 🟨 techo de concreto · 🟩 vegetación

El techo blanco grande sale como concreto y los árboles como vegetación. El asfalto se extiende sobre las bodegas,
y la vegetación todavía marca de más.
