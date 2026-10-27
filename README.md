# Imágenes Espectrales: materiales con longitud de arco

Identificamos materiales en imágenes hiperespectrales de Cartagena (750×750 píxeles, 380 bandas)
usando la **longitud de arco** de su firma espectral, el mismo método de `Cuaderno_Asbesto_ArcoV3.ipynb`:

1. Se toman muestras del material y de otros materiales.
2. Se calcula la firma promedio (mediana) del material.
3. Para cada píxel se mide la longitud de arco en 2 tramos de bandas (40–140 y 150–270) y se compara con la del promedio (similitud porcentual).
4. Se pinta el píxel si su similitud es mayor o igual al umbral, que es la similitud mínima de las muestras del material
   (después de quitar las muestras atípicas, ver "Resultados actuales").

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
| 1 | Marcar los materiales en las 4 imágenes con ImageJ y exportar las zonas en CSV | **Samuel Cogollo** |
| 2 | Revisar las muestras y calcular la firma promedio de cada material | Nosotros |
| 3 | Un notebook por imagen con la longitud de arco de cada material y sus métricas | Nosotros |
| 4 | Mapa final de cada imagen con todos los materiales pintados | Nosotros |

### Tarea de Samuel Cogollo: marcar materiales en ImageJ

#### ¿Qué es una firma y por qué importa marcar bien?

Una foto normal guarda 3 colores por píxel (rojo, verde, azul). Estas imágenes guardan **380 bandas**
por píxel. Si graficas esos 380 valores obtienes una curva, la **firma espectral**, y cada material
tiene una forma de curva propia: el agua, un techo de zinc y un árbol se ven distintos.

Tú marcas **dónde** está cada material y nosotros sacamos la firma de esas zonas desde la imagen de 380 bandas.
El método toma esas muestras, saca la firma "típica" de cada material y busca en toda la imagen
los píxeles que se le parecen. **Si en una muestra se cuela un solo píxel de otra cosa** (una sombra,
un borde, un carro), el método se vuelve permisivo y termina marcando casi toda la imagen.
Por eso lo más importante de tu tarea es que **las muestras estén limpias**.

#### Las imágenes

Son 4 imágenes de Cartagena de 750×750 píxeles. Para marcar usas el `.png` de cada una, que ya está en el repo
(`datos/cartagenaN/imagen/cartagenaN.png`); no necesitas bajar los `.img`. Aquí está cómo se ven:

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
| Techos de lámina (zinc, metal) | ✅ | ❓ | ❌ | ❌ |
| Asbesto (techos de asbesto-cemento / eternit) | ❓ | ❓ | ❓ | ❓ |
| Techos de teja (barro, rojizos) | ✅ | — | ❓ | ❓ |
| Techos de concreto / blancos | ✅ | ❓ | ❌ | ✅ |
| Vegetación (árboles, manglar, pasto) | ✅ | — | ✅ | ✅ |
| Tierra / suelo desnudo | ❓ | — | ❌ | ❌ |
| Carretera / asfalto | ✅ | ✅ | ✅ | ✅ |
| Contenedores | ❌ | ❌ | — | ❌ |

Los ✅ de los materiales nuevos son las muestras que ya entregó Samuel (rama `DatosCSV`).
La tabla es lo que **creemos** que hay mirando las fotos. Confírmalo tú al revisar cada imagen:
si encuentras un material que no está en la tabla, márcalo también, y si algo de la tabla no aparece, no pasa nada.

#### Cómo marcar con ImageJ

Usa **ImageJ** (gratis y open source): <https://imagej.net/ij/download.html> (también sirve Fiji).

**Una sola vez, al abrir ImageJ:**
1. `Analyze > Set Measurements...` → deja marcado **solo** `Bounding rectangle` → `OK`.
2. `Analyze > Set Scale...` → si dice algo distinto de `pixels`, presiona `Click to Remove Scale` → `OK`.
   Así las coordenadas salen en píxeles.

**Por cada material de cada imagen:**
1. `File > Open...` → abre `datos/cartagenaN/imagen/cartagenaN.png`.
   Puedes acercar con la lupa o con las teclas `+` y `-`.
   La cartagena2 se ve oscura: `Image > Adjust > Brightness/Contrast... > Auto` la aclara (no guardes la imagen).
2. Escoge la herramienta de **rectángulo** (la primera de la barra). Usa solo rectángulos.
3. Dibuja un rectángulo **dentro** del material y presiona `Ctrl+M` (`Analyze > Measure`).
   Se agrega una fila a la ventana **Results**.
4. Repite el paso 3 con todas las zonas de ese material en esa imagen.
5. En la ventana **Results**: `File > Save As...` → guárdalo como
   `datos/cartagenaN/muestras/<material>.csv` (ver nombres abajo).
6. Antes de pasar al siguiente material, limpia la tabla: en la ventana **Results**, `Results > Clear Results`.

#### Cómo marcar bien

- Marca solo zonas donde estés **seguro** de qué material es. Si dudas, no la marques.
- El rectángulo va en el **centro** del objeto: nada de bordes, sombras, carros, personas ni mezcla con otro material.
  Es mejor un rectángulo pequeño y limpio que uno grande que se salga.
- Marca **varias zonas** de cada material en cada imagen, repartidas por la imagen (no todas juntas):
  como mínimo unas **3 zonas** o unos **200 píxeles** por material.

#### No hace falta marcar `otros`

Para medir si el método funciona, cada material se compara contra **los demás materiales que marcaste en esa
misma imagen**. Por eso:

- Cada imagen necesita **al menos 2 materiales** (cartagena2 por ahora solo tiene asfalto).
- Entre más materiales marques en una imagen, mejor: lo que no se marca, el método lo confunde con el
  material más parecido.

#### Qué entregar y dónde

El CSV que guarda ImageJ, **uno por material y por imagen**, en `datos/cartagenaN/muestras/<material>.csv`. Por ejemplo:

```
datos/cartagena1/muestras/techo_lamina.csv
datos/cartagena1/muestras/vegetacion.csv
datos/cartagena3/muestras/tierra.csv
```

- Nombres en minúscula y sin espacios ni tildes: `techo_lamina`, `asbesto`, `techo_teja`, `techo_concreto`,
  `vegetacion`, `tierra`, `asfalto`, `contenedor`...
- Sirven 2 formatos:
  - **Un píxel por fila**, con columnas `x,y` (así entregó Samuel la primera parte).
  - **Un rectángulo por fila**, con columnas `BX, BY, Width, Height` (el `Results` de los pasos de arriba).
    `BX, BY` es la esquina de arriba a la izquierda del rectángulo, en píxeles.
- Solo en `muestras/`: no copies los CSV en otras carpetas (por ejemplo `imagen/`).
- Si te equivocaste en una zona, bórrala de la tabla (clic en la fila → `Edit > Clear`) antes de guardar,
  o borra esa fila del CSV.
- No modifiques ni borres nada de `recuadros/`, `puntos/` ni `originales/`.

#### Cómo subirlo

Samuel trabaja en su rama `DatosCSV`. Antes de seguir marcando, trae lo último de `master`:

```bash
git checkout DatosCSV
git pull origin master
# ... marcas y guardas los CSV en datos/cartagenaN/muestras/ ...
git add datos/*/muestras
git commit -m "feat: muestras de materiales de cartagenaN"
git push
```

Luego avisa a Manuel. Puedes subir por partes (por ejemplo, una imagen a la vez).

#### Lista de chequeo antes de entregar

- [ ] Revisé las 4 imágenes y marqué todos los materiales que encontré (los ❌ y los ❓ que sí aparecen).
- [ ] Cada material tiene al menos ~3 zonas o ~200 píxeles por imagen.
- [ ] Ninguna muestra toca bordes, sombras ni otro material.
- [ ] Cada imagen tiene al menos 2 materiales.
- [ ] Los archivos están solo en `datos/cartagenaN/muestras/`, con nombres sin espacios.
- [ ] Cada CSV tiene las columnas `x,y` o `BX, BY, Width, Height`, en píxeles.
- [ ] Subí todo a la rama `DatosCSV` y avisé.

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

Para los materiales de Samuel (los CSV de ImageJ en `muestras/`) se usa `--muestras`. Sale un notebook aparte,
`cartagena4_materiales.ipynb`, que compara cada material contra los demás materiales de la imagen
(se necesitan al menos 2):

```bash
.venv/bin/python herramientas/generar_notebooks.py --muestras 4
cd notebooks && ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace cartagena4_materiales.ipynb
```

Si hay varios materiales en una imagen, al final sale una imagen conjunta donde, si un píxel pasa varios umbrales,
gana el más parecido. Los resultados quedan en `resultados/`.

También puedes abrir el notebook con `.venv/bin/jupyter lab` y correrlo celda por celda.

## Resultados actuales

| Imagen | Material | Precisión | % marcado | Comentario |
|---|---|---|---|---|
| cartagena4 | agua salada | 1.00 | 39 % | Marca bien el mar |
| cartagena3 | agua dulce (río) | 1.00 | 19 % | Marca el río y casi nada de tierra |
| cartagena3 | agua dulce (laguna café) | 0.98 | 11 % | Bien, se queda un poco corto en la punta de abajo |
| cartagena2 | agua salada | 0.84 | 49 % | Marca el mar, con manchas sueltas en el patio de contenedores |

**Limpieza de muestras atípicas:** entre el 1 % y el 5 % de los píxeles de muestra tienen ruido
(brillo del sol, olas, ruido del sensor, bordes). Antes, uno solo de ellos bajaba la similitud mínima y casi
toda la imagen pasaba el umbral (el río marcaba el 97 % y c2 el 88 %). Ahora, antes de tomar el mínimo,
se quitan las muestras atípicas con la regla del diagrama de caja (similitud menor que Q1 − 1,5·(Q3 − Q1)).
El umbral sigue siendo la similitud mínima, pero de las muestras limpias.
