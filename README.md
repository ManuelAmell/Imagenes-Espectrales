# Imágenes espectrales: materiales con longitud de arco

Autores: Manuel Amell y Samuel Cogollo

> Profesor, este trabajo también está en GitHub: https://github.com/ManuelAmell/Imagenes-Espectrales (repositorio público).
> Ahí está el historial de cómo lo fuimos haciendo.

Identificamos materiales en 4 imágenes hiperespectrales de Cartagena (750 × 750 píxeles, 380 bandas) con la **longitud de arco** de su firma espectral,
el mismo método de `referencia/Cuaderno_Asbesto_ArcoV3.ipynb`:

1. Tomamos muestras del material y de otros materiales.
2. Calculamos la firma promedio (la mediana) del material.
3. Medimos la longitud de arco de cada píxel en 2 tramos de bandas (40–140 y 150–270) y la comparamos con la del promedio (similitud porcentual).
4. Pintamos el píxel si su similitud llega al umbral, que es la similitud mínima de las muestras del material una vez quitadas las muestras atípicas.

## Qué abrir primero

| Archivo | Qué es |
|---|---|
| [docs/video_explicativo.mp4](docs/video_explicativo.mp4) | Video de unos 3 minutos, solo texto y sin sonido |
| [docs/explicacion_metodo.pdf](docs/explicacion_metodo.pdf) | El método paso a paso, del píxel a la imagen pintada |
| [docs/reporte.pdf](docs/reporte.pdf) | Qué hicimos en cada etapa, los resultados y por qué se equivoca |
| [resultados/antes_y_despues.md](resultados/antes_y_despues.md) | Cada imagen original junto a su imagen pintada |

## Resultados

Agua (`notebooks/cartagenaN.ipynb`):

| Imagen | Material | Precisión | % de la imagen pintado | Comentario |
|---|---|---|---|---|
| cartagena4 | agua salada | 1,00 | 39 % | Marca bien el mar |
| cartagena3 | agua dulce (río) | 1,00 | 19 % | Marca el río y casi nada de tierra |
| cartagena3 | agua dulce (laguna) | 0,98 | 11 % | Bien, aunque se queda corta en la punta de abajo |
| cartagena2 | agua salada | 0,84 | 49 % | Marca el mar, con manchas sueltas en el patio de contenedores |

Materiales (`notebooks/cartagenaN_materiales.ipynb`; cada material se compara con los demás de su imagen):

| Imagen | Material | Precisión | % pintado | Comentario |
|---|---|---|---|---|
| cartagena1 | asfalto | 1,00 | 17 % | Marca las calles |
| cartagena1 | techo de concreto | 1,00 | 14 % | Bien |
| cartagena1 | techo de lámina | 0,77 | 11 % | Marca los techos azules y algo de más |
| cartagena1 | techo de teja | 0,56 | 30 % | Se extiende sobre otros techos |
| cartagena1 | vegetación | 0,72 | 12 % | Marca los árboles |
| cartagena3 | asfalto | 1,00 | 4 % | Marca la calle del borde del río |
| cartagena3 | vegetación | 1,00 | 51 % | Marca el manglar y también las bodegas, porque no hay otro material para ellas |
| cartagena4 | asfalto | 1,00 | 35 % | Se extiende sobre las bodegas |
| cartagena4 | techo de concreto | 0,98 | 6 % | Marca el techo blanco grande |
| cartagena4 | vegetación | 0,56 | 16 % | Marca los árboles y algo de más |

**La limpieza de muestras atípicas** fue el cambio que más ayudó. Entre el 1 % y el 5 % de las muestras de agua tienen ruido (brillo del sol, olas, bordes),
y una sola bastaba para bajar la similitud mínima: el río pintaba el 97 % de la imagen. Ahora quitamos las muestras que quedan por debajo de Q1 − 1,5·(Q3 − Q1)
(regla del diagrama de caja) antes de tomar el mínimo, y el río pinta el 19 %.

**No alcanzamos a marcar** asbesto, tierra ni contenedores. En cartagena2 solo se marcó asfalto, y hacen falta al menos 2 materiales para compararlos,
así que no tiene notebook de materiales.

**Por qué se equivoca:** el método mira la forma de la firma, no su brillo, y por eso se confunden materiales parecidos (lámina, teja y vegetación);
un material con muestras muy variadas tiene un umbral bajo y acepta de más; y lo que no se marcó se lo queda el material más parecido.
La explicación con cifras está en `docs/reporte.pdf`.

## Estructura

```
referencia/    cuaderno original (asbesto) y el encabezado de la imagen que usaba
datos/cartagenaN/
  imagen/      cartagenaN.hdr, cartagenaN.img (no está en el repositorio) y cartagenaN.png
  muestras/    CSV con los píxeles de cada material, marcados en ImageJ (x,y)
  recuadros/   recuadros de agua y de "otros" marcados con el mouse
  puntos/      puntos de la primera prueba (ya no se usan)
  originales/  archivos de puntos tal como llegaron
herramientas/  scripts: generar_notebooks.py, marcar_recuadros.py, analizar_confusiones.py, generar_figuras.py y generar_pdfs.sh
notebooks/     un notebook por imagen
resultados/    imágenes pintadas y antes_y_despues.md
docs/          video, PDF y docs/fuentes/ (el HTML, las imágenes y los datos con los que se arman los PDF)
video/         proyecto del video (HTML y animaciones)
```

## Cómo reproducirlo

Todo se corre desde la carpeta del proyecto.

**1. Entorno** (una sola vez; en Windows el pip está en `.venv\Scripts\pip`):

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

**2. Datos.** Los 4 archivos `.img` pesan 855 MB cada uno y no están en el repositorio: se descargan del Drive del curso y se guardan en
`datos/cartagenaN/imagen/cartagenaN.img`. El `cartagena2.hdr` es una copia del de `cartagena1` (tienen el mismo tamaño).

**3. Notebooks.** El generador arma el notebook y `nbconvert` lo ejecuta:

```bash
.venv/bin/python herramientas/generar_notebooks.py 4                # agua: usa datos/cartagena4/recuadros/
cd notebooks && ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace cartagena4.ipynb && cd ..

.venv/bin/python herramientas/generar_notebooks.py --muestras 4     # materiales: usa datos/cartagena4/muestras/
cd notebooks && ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace cartagena4_materiales.ipynb && cd ..
```

Cada CSV de la carpeta es un material. Los de `recuadros/` se comparan con `otros.csv` y los de `muestras/` se comparan entre sí.
Si una imagen tiene varios materiales, el mapa final pinta cada píxel con el más parecido. Los notebooks también se pueden abrir con `.venv/bin/jupyter lab`.

**4. Marcar más recuadros** (OpenCV): `.venv/bin/python herramientas/marcar_recuadros.py 4 agua_salada` abre la imagen; se arrastra el mouse,
ENTER guarda cada recuadro y ESC termina. Si la ventana no abre en Wayland, se antepone `QT_QPA_PLATFORM=xcb`.

**5. Figuras y PDF** (necesita Chromium o Chrome):

```bash
.venv/bin/python herramientas/analizar_confusiones.py   # escribe docs/fuentes/*.json (necesita los .img)
.venv/bin/python herramientas/generar_figuras.py
bash herramientas/generar_pdfs.sh
```

**6. Video** (necesita Node e internet, porque carga GSAP y las fuentes):

```bash
cd video
npx hyperframes preview                                         # vista previa
npx hyperframes render --output ../docs/video_explicativo.mp4   # renderizar
```

## Lo que hicimos

| Etapa | Qué hicimos | Resultado |
|---|---|---|
| 1. Primera prueba | Aplicamos el método a todos los materiales con los puntos que llegaron | Solo el agua pasó de 0,7; el resto marcaba de más (los techos de c1, el 99 % de la imagen) |
| 2. Muestras a mano | Marcamos recuadros donde seguro había agua, y otros donde seguro no | c4 y la laguna bien; el río (97 %) y c2 (88 %) marcaban casi todo |
| 3. Limpieza de atípicas | Quitamos las muestras atípicas antes de tomar el mínimo | Agua bien en las 3 imágenes: precisión de 0,84 a 1,00 |
| 4. Más materiales | Samuel marcó asfalto, techos y vegetación en ImageJ; cada material se compara con los demás | Asfalto y concreto bien; la teja y la vegetación marcan de más |

## Qué usamos y qué dejamos de usar

| Qué | Para qué lo usamos | Después |
|---|---|---|
| `datos/*/originales/` | Archivos de puntos tal como llegaron (txt, csv, xlsx, docx), en formatos distintos | Los conservamos; ningún notebook los lee |
| `datos/*/puntos/` | Etapa 1: los puntos originales pasados a CSV `x,y` | Varios puntos de "agua" caían en tierra y los cambiamos por recuadros. Quedan como registro |
| `marcar_recuadros.py` y `recuadros/` | Etapas 2 y 3: recuadros de agua y `otros.csv` marcados con el mouse | Siguen en uso para el agua. Para los materiales nuevos usamos ImageJ, que deja marcar píxel por píxel |
| `recuadros/otros.csv` | Comparar el agua con lo que no es agua | Solo sirve para el agua: tenía vegetación y techos, que eran justo lo que íbamos a marcar. Por eso los materiales se comparan entre sí |
| Umbral sin limpiar | Era el del cuaderno original | Lo cambiamos en la etapa 3 porque una muestra con ruido bajaba el umbral |
| `datos/*/muestras/` | Etapa 4: píxeles de cada material marcados en ImageJ | En uso |

## Créditos

- **Manuel Amell:** notebooks y herramientas, análisis de resultados, documentos y video.
- **Samuel Cogollo:** marcó con ImageJ las muestras de asfalto, techos y vegetación (`datos/cartagenaN/muestras/`).
