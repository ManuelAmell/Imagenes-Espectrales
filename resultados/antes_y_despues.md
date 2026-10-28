# Antes y después: cada imagen original y su imagen pintada

A la izquierda está la imagen original y a la derecha la que sale del notebook, con los píxeles del material pintados.
El método está explicado en el [README](../README.md) y en [docs/explicacion_metodo.pdf](../docs/explicacion_metodo.pdf).

Colores del agua: agua salada en cian y agua dulce en magenta. En los mapas de materiales el color depende de los materiales de cada imagen,
y se indica debajo de cada mapa.

| Imagen | Material | Precisión | % de la imagen pintado | Notebook |
|---|---|---|---|---|
| cartagena2 | agua salada | 0,84 | 49 % | [cartagena2.ipynb](../notebooks/cartagena2.ipynb) |
| cartagena3 | agua dulce (río) | 1,00 | 19 % | [cartagena3.ipynb](../notebooks/cartagena3.ipynb) |
| cartagena3 | agua dulce (laguna) | 0,98 | 11 % | [cartagena3.ipynb](../notebooks/cartagena3.ipynb) |
| cartagena4 | agua salada | 1,00 | 39 % | [cartagena4.ipynb](../notebooks/cartagena4.ipynb) |
| cartagena1 | asfalto | 1,00 | 17 % | [cartagena1_materiales.ipynb](../notebooks/cartagena1_materiales.ipynb) |
| cartagena1 | techo de concreto | 1,00 | 14 % | [cartagena1_materiales.ipynb](../notebooks/cartagena1_materiales.ipynb) |
| cartagena1 | techo de lámina | 0,77 | 11 % | [cartagena1_materiales.ipynb](../notebooks/cartagena1_materiales.ipynb) |
| cartagena1 | techo de teja | 0,56 | 30 % | [cartagena1_materiales.ipynb](../notebooks/cartagena1_materiales.ipynb) |
| cartagena1 | vegetación | 0,72 | 12 % | [cartagena1_materiales.ipynb](../notebooks/cartagena1_materiales.ipynb) |
| cartagena3 | asfalto | 1,00 | 4 % | [cartagena3_materiales.ipynb](../notebooks/cartagena3_materiales.ipynb) |
| cartagena3 | vegetación | 1,00 | 51 % | [cartagena3_materiales.ipynb](../notebooks/cartagena3_materiales.ipynb) |
| cartagena4 | asfalto | 1,00 | 35 % | [cartagena4_materiales.ipynb](../notebooks/cartagena4_materiales.ipynb) |
| cartagena4 | techo de concreto | 0,98 | 6 % | [cartagena4_materiales.ipynb](../notebooks/cartagena4_materiales.ipynb) |
| cartagena4 | vegetación | 0,56 | 16 % | [cartagena4_materiales.ipynb](../notebooks/cartagena4_materiales.ipynb) |

En los mapas de materiales cada material se compara con los demás de su imagen, así que una precisión de 1,00 solo dice que se separa bien de esos otros materiales.
Lo que no se marcó (asbesto, tierra, contenedores, y el agua en esos mapas) se pinta como el material más parecido.

---

## cartagena1: barrio

| Original | Pintada |
|---|---|
| <img src="../datos/cartagena1/imagen/cartagena1.png" width="400"> | <img src="cartagena1_materiales_final.png" width="400"> |

Colores: rojo = asfalto, amarillo = techo de concreto, verde = techo de lámina, naranja = techo de teja, morado = vegetación.

No tiene agua. Las calles (asfalto) y los árboles (vegetación) se marcan bien; la teja se extiende de más sobre otros techos. Mapa de cada material por separado:

| Asfalto | Techo de concreto | Techo de lámina | Techo de teja | Vegetación |
|---|---|---|---|---|
| <img src="cartagena1_asfalto.png" width="190"> | <img src="cartagena1_techo_concreto.png" width="190"> | <img src="cartagena1_techo_lamina.png" width="190"> | <img src="cartagena1_techo_teja.png" width="190"> | <img src="cartagena1_vegetacion.png" width="190"> |

## cartagena2: contenedores y mar

| Original | Pintada: agua salada |
|---|---|
| <img src="../datos/cartagena2/imagen/cartagena2.png" width="400"> | <img src="cartagena2_agua_salada.png" width="400"> |

El mar queda marcado, con algunas manchas sueltas en el patio de contenedores.
La imagen original se ve oscura porque la armamos con las bandas 29, 50 y 70 (no venía en color).

De materiales solo se marcó asfalto, y hacen falta al menos 2 para compararlos, así que cartagena2 no tiene mapa de materiales.

## cartagena3: río, laguna y manglar

| Original | Pintada: río y laguna juntos |
|---|---|
| <img src="../datos/cartagena3/imagen/cartagena3.png" width="400"> | <img src="cartagena3_final.png" width="400"> |

| Solo el río | Solo la laguna |
|---|---|
| <img src="cartagena3_agua_dulce_rio.png" width="400"> | <img src="cartagena3_agua_dulce_laguna.png" width="400"> |

El río se marca casi sin tocar la tierra. La laguna se marca en su mayor parte, aunque se queda corta en la punta de abajo.

| Original | Pintada: materiales |
|---|---|
| <img src="../datos/cartagena3/imagen/cartagena3.png" width="400"> | <img src="cartagena3_materiales_final.png" width="400"> |

Colores: rojo = asfalto, amarillo = vegetación.

El manglar se marca como vegetación. Como solo hay 2 materiales, las bodegas también salen como vegetación y parte del río como asfalto (el agua va en el otro notebook).
Mapa de cada material por separado:

| Asfalto | Vegetación |
|---|---|
| <img src="cartagena3_asfalto.png" width="300"> | <img src="cartagena3_vegetacion.png" width="300"> |

## cartagena4: puerto y mar

| Original | Pintada: agua salada |
|---|---|
| <img src="../datos/cartagena4/imagen/cartagena4.png" width="400"> | <img src="cartagena4_agua_salada.png" width="400"> |

El mar queda marcado casi por completo y la tierra queda limpia, salvo algunas líneas sueltas de sombras.

| Original | Pintada: materiales |
|---|---|
| <img src="../datos/cartagena4/imagen/cartagena4.png" width="400"> | <img src="cartagena4_materiales_final.png" width="400"> |

Colores: rojo = asfalto, amarillo = techo de concreto, verde = vegetación.

El techo blanco grande sale como concreto y los árboles como vegetación. El asfalto se extiende sobre las bodegas y la vegetación marca de más.
Mapa de cada material por separado:

| Asfalto | Techo de concreto | Vegetación |
|---|---|---|
| <img src="cartagena4_asfalto.png" width="250"> | <img src="cartagena4_techo_concreto.png" width="250"> | <img src="cartagena4_vegetacion.png" width="250"> |
