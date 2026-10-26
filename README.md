# Imágenes Espectrales: materiales con longitud de arco

Identificamos materiales en imágenes hiperespectrales de Cartagena (750×750 píxeles, 380 bandas)
usando la **longitud de arco** de su firma espectral, el mismo método de `Cuaderno_Asbesto_ArcoV3.ipynb`:

1. Se toman muestras del material y de otros materiales.
2. Se calcula la firma promedio (mediana) del material.
3. Para cada píxel se mide la longitud de arco en 2 tramos de bandas (40–140 y 150–270) y se compara con la del promedio (similitud porcentual).
4. Se pinta el píxel si su similitud es mayor o igual al umbral, que es la similitud mínima de las muestras del material.

## Estructura

```
Cuaderno_Asbesto_ArcoV3.ipynb   notebook original (asbesto), de referencia
datos/cartagenaN/
  imagen/      cartagenaN.hdr, cartagenaN.img (NO está en git), cartagenaN.png
  recuadros/   <material>.csv y otros.csv  ← muestras marcadas a mano
  puntos/      puntos de muestra viejos (x,y), ya no se usan en los notebooks
  originales/  archivos de puntos tal como llegaron
herramientas/
  marcar_recuadros.py   para dibujar recuadros de muestra sobre una imagen
  generar_notebooks.py  arma notebooks/cartagenaN.ipynb a partir de los recuadros
notebooks/     un notebook por imagen
resultados/    imágenes marcadas que salen de los notebooks
```

## Preparar el entorno (una sola vez)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Los archivos `.img` pesan 855 MB cada uno y **no se suben a git**. Hay que descargarlos del Drive del curso
y ponerlos en `datos/cartagenaN/imagen/cartagenaN.img`. A `cartagena2` le falta el `.hdr` original;
el que está en el repo es una copia del de `cartagena1` (mismo tamaño).

## Cómo trabajar

### 1. Marcar recuadros de un material

```bash
.venv/bin/python herramientas/marcar_recuadros.py 4 agua_salada
```

- Se abre la imagen. Los recuadros que ya existen se ven en amarillo.
- Arrastra con el mouse sobre una zona donde **seguro** está el material y presiona **ENTER**. Repite las veces que quieras.
- Presiona **ESC** para terminar. Los recuadros se **agregan** a `datos/cartagena4/recuadros/agua_salada.csv`.

Haz lo mismo con `otros` para marcar zonas donde seguro **no** está ningún material
(techos, vegetación, calles...). Esas zonas se usan para medir las métricas.

```bash
.venv/bin/python herramientas/marcar_recuadros.py 4 otros
```

Consejos:
- Recuadros **limpios**: sin bordes, botes, boyas, sombras ni mezcla con otro material.
  Un solo píxel raro baja el umbral (la similitud mínima) y hace que se marque casi toda la imagen.
- El nombre del archivo es el nombre del material. Usa `agua_salada`, `agua_dulce_rio`, etc. (sin espacios).
- Si la ventana no abre en Wayland, prueba con `QT_QPA_PLATFORM=xcb` antes del comando.

### 2. Generar y correr el notebook

```bash
.venv/bin/python herramientas/generar_notebooks.py 4
cd notebooks && ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace cartagena4.ipynb
```

El generador toma **cada CSV** de `recuadros/` (menos `otros.csv`) como un material.
Si hay varios materiales en una imagen, al final sale una imagen conjunta donde, si un píxel pasa varios umbrales,
gana el más parecido. Los resultados quedan en `resultados/`.

También puedes abrir el notebook con `.venv/bin/jupyter lab` y correrlo celda por celda.

## Resultados actuales

| Imagen | Material | Precisión | % marcado | Comentario |
|---|---|---|---|---|
| cartagena4 | agua salada | 0.98 | 42 % | Marca bien el mar |
| cartagena3 | agua dulce (laguna café) | 0.94 | 27 % | Bien |
| cartagena3 | agua dulce (río) | 0.50 | 97 % | El umbral mínimo queda muy bajo (~20) por píxeles con ruido |
| cartagena2 | agua salada | 0.53 | 88 % | Mismo problema del umbral (~32) |

**Por qué fallan c2 y el río de c3:** entre el 1 % y el 5 % de los píxeles de agua tienen ruido
(brillo del sol, olas, ruido del sensor). Si uno de ellos cae entre las 250 muestras, la similitud mínima
baja mucho y casi todo pasa el umbral. Mejorar los recuadros ayuda, pero con el umbral mínimo sigue
pasando. Se probó suavizar la firma y no sirvió.
