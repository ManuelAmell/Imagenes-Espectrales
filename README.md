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
  muestras/    <material>.csv  ← muestras NUEVAS de los materiales (tarea de Samuel, ver el plan)
  recuadros/   <material>.csv y otros.csv  ← muestras de agua de la etapa anterior
  puntos/      puntos de muestra viejos (x,y), ya no se usan en los notebooks
  originales/  archivos de puntos tal como llegaron
herramientas/
  marcar_recuadros.py   para dibujar recuadros de muestra sobre una imagen
  generar_notebooks.py  arma notebooks/cartagenaN.ipynb a partir de los recuadros
notebooks/     un notebook por imagen
resultados/    imágenes marcadas que salen de los notebooks
```

## Plan: identificación de materiales

Queremos identificar con la longitud de arco **todos los materiales** que aparecen en las 4 imágenes:
agua, techos de lámina, asbesto, vegetación, tierra, etc. Empezamos de cero con muestras nuevas:
los datos viejos de `puntos/` y `originales/` **no se usan**.

| Fase | Qué se hace | Quién |
|---|---|---|
| 1 | Marcar los materiales en las 4 imágenes y extraer sus firmas | **Samuel Cogollo** |
| 2 | Revisar las muestras y calcular la firma promedio de cada material | Nosotros |
| 3 | Un notebook por imagen con la longitud de arco de cada material y sus métricas | Nosotros |
| 4 | Mapa final de cada imagen con todos los materiales pintados | Nosotros |

### Tarea de Samuel Cogollo: marcar materiales y extraer sus firmas

#### ¿Qué es una firma y por qué importa marcar bien?

Una foto normal guarda 3 colores por píxel (rojo, verde, azul). Estas imágenes guardan **380 bandas**
por píxel. Si graficas esos 380 valores obtienes una curva, la **firma espectral**, y cada material
tiene una forma de curva propia: el agua, un techo de zinc y un árbol se ven distintos.

El método toma tus muestras, saca la firma "típica" de cada material y busca en toda la imagen
los píxeles que se le parecen. **Si en una muestra se cuela un solo píxel de otra cosa** (una sombra,
un borde, un carro), el método se vuelve permisivo y termina marcando casi toda la imagen.
Por eso lo más importante de tu tarea es que **las muestras estén limpias**.

#### Las imágenes

Son 4 imágenes de Cartagena de 750×750 píxeles. Los `.img` (los que tienen las 380 bandas) se bajan
del Drive del curso y van en `datos/cartagenaN/imagen/`. Aquí está cómo se ven:

| cartagena1 | cartagena2 |
|---|---|
| ![cartagena1](datos/cartagena1/imagen/cartagena1.png) | ![cartagena2](datos/cartagena2/imagen/cartagena2.png) |
| Barrio: techos de teja, lámina y concreto, árboles, calles y contenedores abajo | Patio de contenedores y mar (se ve oscura, no tiene foto a color original) |

| cartagena3 | cartagena4 |
|---|---|
| ![cartagena3](datos/cartagena3/imagen/cartagena3.png) | ![cartagena4](datos/cartagena4/imagen/cartagena4.png) |
| Río, laguna café, manglar, bodegas, barrio y tierra | Puerto: contenedores, bodegas, tanques blancos, árboles, tierra y mar |

#### Qué tenemos y qué falta

✅ ya lo tenemos · ❌ **falta, hay que marcarlo** · ❓ no sabemos si aparece, revísalo · — no aparece

| Material | cartagena1 | cartagena2 | cartagena3 | cartagena4 |
|---|---|---|---|---|
| Agua salada (mar) | — | ✅ | — | ✅ |
| Agua dulce (río, laguna) | — | — | ✅ | — |
| Techos de lámina (zinc, metal) | ❌ | ❓ | ❌ | ❌ |
| Asbesto (techos de asbesto-cemento / eternit) | ❓ | ❓ | ❓ | ❓ |
| Techos de teja (barro, rojizos) | ❌ | — | ❓ | ❓ |
| Techos de concreto / blancos | ❌ | ❓ | ❌ | ❌ |
| Vegetación (árboles, manglar, pasto) | ❌ | — | ❌ | ❌ |
| Tierra / suelo desnudo | ❓ | — | ❌ | ❌ |
| Carretera / asfalto | ❌ | ❌ | ❌ | ❌ |
| Contenedores | ❌ | ❌ | — | ❌ |

La tabla es lo que **creemos** que hay mirando las fotos. Confírmalo tú al revisar cada imagen:
si encuentras un material que no está en la tabla, márcalo también, y si algo de la tabla no aparece, no pasa nada.

#### Con qué programa

**Manuel te indica qué programa usar.** Si el programa lo permite, abre el `.hdr`/`.img` (la imagen con
las 380 bandas) y no solo el `.png`, para que puedas ver la firma de los píxeles que marcas.

#### Cómo marcar bien

- Marca solo zonas donde estés **seguro** de qué material es. Si dudas, no la marques.
- Toma el **centro** del objeto: nada de bordes, sombras, carros, personas ni mezcla con otro material.
- Marca **varias zonas** de cada material en cada imagen, repartidas por la imagen (no todas juntas):
  como mínimo unas **3 zonas** o unos **200 píxeles** por material.
- Si el programa te muestra la firma, revisa que las curvas de una misma muestra se parezcan entre sí.
  Si una se sale mucho de las demás, quita ese píxel o esa zona.

#### Qué entregar y dónde

Un archivo CSV **por material y por imagen** en `datos/cartagenaN/muestras/<material>.csv`. Por ejemplo:

```
datos/cartagena1/muestras/techo_lamina.csv
datos/cartagena1/muestras/vegetacion.csv
datos/cartagena3/muestras/tierra.csv
```

- Nombres en minúscula y sin espacios ni tildes: `techo_lamina`, `asbesto`, `techo_teja`, `techo_concreto`,
  `vegetacion`, `tierra`, `asfalto`, `contenedor`...
- Sirve cualquiera de estos 2 formatos (nosotros lo adaptamos):
  - **Un píxel por fila:** columnas `x,y`.
  - **Un recuadro por fila:** columnas `x1,y1,x2,y2,nombre` (esquina de arriba a la izquierda y esquina de abajo a la derecha).
- Las coordenadas van en **píxeles** de la imagen de 750×750: `x` es la columna, `y` es la fila, y el (0, 0) es la
  esquina de **arriba a la izquierda**.
- Si el programa exporta también la firma (los valores de las bandas de cada píxel), inclúyela en el mismo CSV o en otro
  con el mismo nombre terminado en `_firma.csv`.
- No modifiques ni borres nada de `recuadros/`, `puntos/` ni `originales/`.

#### Cómo subirlo

```bash
git clone git@github.com:ManuelAmell/Imagenes-Espectrales.git
cd Imagenes-Espectrales
git checkout -b muestras-samuel
# ... marcas y guardas los CSV en datos/cartagenaN/muestras/ ...
git add datos/*/muestras
git commit -m "feat: muestras de materiales de cartagenaN"
git push -u origin muestras-samuel
```

Luego avisa a Manuel. Puedes subir por partes (por ejemplo, una imagen a la vez).

#### Lista de chequeo antes de entregar

- [ ] Revisé las 4 imágenes y marqué todos los materiales que encontré (los ❌ y los ❓ que sí aparecen).
- [ ] Cada material tiene al menos ~3 zonas o ~200 píxeles por imagen.
- [ ] Ninguna muestra toca bordes, sombras ni otro material.
- [ ] Los archivos están en `datos/cartagenaN/muestras/` con nombres sin espacios.
- [ ] Las coordenadas son en píxeles (x = columna, y = fila, origen arriba a la izquierda).
- [ ] Subí todo a la rama `muestras-samuel` y avisé.

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
