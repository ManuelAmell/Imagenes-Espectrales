"""Arma los notebooks de cada imagen a partir de los CSV de muestras.

Uso: .venv/bin/python herramientas/generar_notebooks.py [--muestras] <N> [<N> ...]
Sin --muestras usa datos/cartagenaN/recuadros/ (agua) y con --muestras usa datos/cartagenaN/muestras/ (materiales)."""
import glob
import os
import sys

import nbformat as nbf

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIMS = (40, 140, 150, 270)
# Color (RGB) según cómo empieza el nombre del material; el resto toma uno de la paleta
COLORES = {"agua_salada": (0, 255, 255), "agua_dulce": (255, 0, 255)}
PALETA = [(255, 0, 0), (255, 255, 0), (0, 255, 0), (255, 128, 0), (128, 0, 255),
          (0, 0, 255), (255, 255, 255), (128, 64, 0), (0, 128, 0), (255, 160, 200)]

NOMBRES = {"techo_concreto": "techo de concreto", "techo_lamina": "techo de lámina", "techo_teja": "techo de teja",
           "vegetacion": "vegetación", "agua_dulce_rio": "agua dulce (río)", "agua_dulce_laguna": "agua dulce (laguna)"}

md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell


def materiales_de(n, carpeta):
    archivos = sorted(glob.glob(os.path.join(RAIZ, "datos", f"cartagena{n}", carpeta, "*.csv")))
    claves = [os.path.splitext(os.path.basename(a))[0] for a in archivos]
    claves = [c for c in claves if c != "otros"]
    resultado, libre = [], 0
    for clave in claves:
        color = next((c for pref, c in COLORES.items() if clave.startswith(pref)), None)
        if color is None:
            color, libre = PALETA[libre % len(PALETA)], libre + 1
        resultado.append((clave, NOMBRES.get(clave, clave.replace("_", " ")), color))
    return resultado


def dic_colores(materiales):
    return "{" + ", ".join(f'"{c}":{col}' for c, _, col in materiales) + "}"


def dic_nombres(materiales):
    return "{" + ", ".join(f'"{c}":"{nom}"' for c, nom, _ in materiales) + "}"


def lista(nombres):
    return ", ".join(nombres[:-1]) + " y " + nombres[-1] if len(nombres) > 1 else nombres[0]


def tiene_png(n):
    return os.path.exists(os.path.join(RAIZ, "datos", f"cartagena{n}", "imagen", f"cartagena{n}.png"))


def celdas_lectura(materiales, carpeta):
    if carpeta == "recuadros":
        lectura = "\n".join(f"""recuadros["{c}"]=pd.read_csv(ruta+"/recuadros/{c}.csv")""" for c, _, _ in materiales)
        return [
            md("Leemos los recuadros (x1, y1, x2, y2) de cada material y los de otros, que son zonas que no son ninguno de los materiales"),
            code(f"""recuadros={{}}
{lectura}
recuadros_otros=pd.read_csv(ruta+"/recuadros/otros.csv")
for nombre in recuadros:
  print(nombre, ":", len(recuadros[nombre]), "recuadros")
print("otros :", len(recuadros_otros), "recuadros")"""),
            md("Dibujamos los recuadros (cian = materiales, rojo = otros)"),
            code("""img_copy=imagen.copy()
for nombre in recuadros:
  for id,r in recuadros[nombre].iterrows():
    cv2.rectangle(img_copy, (r.x1,r.y1), (r.x2,r.y2), (0,255,255), 2)
for id,r in recuadros_otros.iterrows():
  cv2.rectangle(img_copy, (r.x1,r.y1), (r.x2,r.y2), (255,0,0), 2)
plt.figure(figsize=(8, 8))
plt.imshow(img_copy)
plt.show()"""),
        ]
    lectura = "\n".join(f"""recuadros["{c}"]=leer_imagej(ruta+"/muestras/{c}.csv")""" for c, _, _ in materiales)
    return [
        md("Leemos las muestras de cada material (se marcaron en ImageJ) y las pasamos a recuadros. Cada material se compara con los demás de la imagen"),
        code(f"""def leer_imagej(archivo):
  m=pd.read_csv(archivo)
  if "x" in m.columns:
    #Un píxel por fila (x, y): cada píxel es un recuadro de 1x1
    return pd.DataFrame({{"x1":m.x, "y1":m.y, "x2":m.x+1, "y2":m.y+1}}).round().astype(int)
  #Un rectángulo por fila: ImageJ guarda la esquina de arriba a la izquierda (BX, BY) y el tamaño (Width, Height)
  return pd.DataFrame({{"x1":m.BX, "y1":m.BY, "x2":m.BX+m.Width, "y2":m.BY+m.Height}}).round().astype(int)

recuadros={{}}
{lectura}
for nombre in recuadros:
  print(nombre, ":", len(recuadros[nombre]), "recuadros")"""),
        md("Dibujamos las muestras de cada material con su color"),
        code(f"""colores={dic_colores(materiales)}
nombres={dic_nombres(materiales)}
img_copy=imagen.copy()
for nombre in recuadros:
  for id,r in recuadros[nombre].iterrows():
    cv2.rectangle(img_copy, (r.x1,r.y1), (r.x2-1,r.y2-1), colores[nombre], 2)
plt.figure(figsize=(8, 8))
plt.imshow(img_copy)
plt.legend(handles=[mpatches.Patch(color=np.array(colores[m])/255, label=nombres[m]) for m in colores], loc="upper right")
plt.show()"""),
    ]


def celdas_inicio(n, materiales, carpeta, varios):
    if tiene_png(n):
        base = f"""imagen=cv2.cvtColor(cv2.imread(ruta+"/imagen/cartagena{n}.png"), cv2.COLOR_BGR2RGB)"""
    else:
        base = """#Esta imagen no trae png: la armamos con las bandas 29, 50 y 70, como en el cuaderno original
imagen=(get_rgb(img,(29,50,70))*255).astype(np.uint8)"""
    leyenda = carpeta == "muestras" or varios
    return [
        md("Importamos librerías"),
        code("""from spectral import *
import matplotlib.pyplot as plt
""" + ("import matplotlib.patches as mpatches\n" if leyenda else "") + """import numpy as np
import pandas as pd
import cv2
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)"""),
        md("Cargamos la imagen"),
        code(f"""ruta="../datos/cartagena{n}"
img=open_image(ruta+"/imagen/cartagena{n}.hdr")
arr=np.asarray(img.load())
arr.shape"""),
        md("Normalizamos la imagen"),
        code("""maximo=np.max(arr)
minimo=np.min(arr)
arr_norm=(arr-minimo)/(maximo-minimo)"""),
        md("Marcamos los píxeles con datos (las zonas negras están en cero y no se usan)"),
        code("""con_datos=np.max(arr,axis=2)>0
print("Píxeles sin datos:", np.sum(~con_datos))"""),
        md("Imagen base para dibujar"),
        code(base + """
plt.figure(figsize=(8, 8))
plt.imshow(imagen)
plt.show()"""),
        md("Definimos la longitud de arco y la similitud porcentual, como en el cuaderno original"),
        code("""def long_arco(R):
  return np.sum(np.abs(np.diff(R)))

def similitud_porcentual(A, B):
  A, B = np.array(A), np.array(B)
  #Similitud por posición: 100 si iguales, 0 si muy distintos
  sims = 100 * (1 - np.abs(A - B) / (np.abs(A) + np.abs(B) + 1e-9))
  return np.mean(sims)"""),
    ] + celdas_lectura(materiales, carpeta) + [
        md("Función para sacar los píxeles con datos que hay dentro de unos recuadros"),
        code("""def pixeles_de(rec):
  l_pix=[]
  for id,r in rec.iterrows():
    for y in range(r.y1,r.y2):
      for x in range(r.x1,r.x2):
        if(con_datos[y][x]):
          l_pix.append((x,y))
  return pd.DataFrame(l_pix, columns=["x","y"])"""),
    ]


def celdas_material(n, k, clave, nombre, color, carpeta, varios):
    a, b, c, d = LIMS
    if carpeta == "recuadros":
        otros, de_otros = "otros", "pixeles_de(recuadros_otros)"
    else:
        otros = "los demás materiales"
        de_otros = f"""pixeles_de(pd.concat([recuadros[m] for m in recuadros if m!="{clave}"]))"""
    return [
        md(f"# Material {k}: {nombre}"),
        md(f"Sacamos los píxeles de {nombre} (sí) y de {otros} (no) y tomamos hasta 250 de cada uno al azar"),
        code(f"""df_si=pixeles_de(recuadros["{clave}"])
df_no={de_otros}
print("Píxeles de {nombre}:", len(df_si), " otros:", len(df_no))
df_si=df_si.sample(n=min(250,len(df_si)),random_state=42)
df_no=df_no.sample(n=min(250,len(df_no)),random_state=42)
punt_si=df_si[["x","y"]].astype(int).to_numpy()
punt_no=df_no[["x","y"]].astype(int).to_numpy()
print("Usados:", len(punt_si), len(punt_no))"""),
        md(f"Dibujamos los puntos (rojo = {nombre}, azul = {otros})"),
        code("""img_copy=imagen.copy()
for (x, y) in punt_si:
    cv2.circle(img_copy, (x, y), 1, (255, 0, 0), 2)
for (x, y) in punt_no:
    cv2.circle(img_copy, (x, y), 1, (0, 0, 255), 2)
plt.figure(figsize=(8, 8))
plt.imshow(img_copy)
plt.show()"""),
        md("Sacamos las firmas espectrales de cada punto y las dibujamos"),
        code(f"""l_pix_si=[]
l_pix_no=[]
for pix in punt_si:
  l_pix_si.append(arr_norm[pix[1],pix[0],:])
for pix in punt_no:
  l_pix_no.append(arr_norm[pix[1],pix[0],:])

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, (lista, titulo) in zip(axes, [(l_pix_si, "Firmas de {nombre}"), (l_pix_no, "Firmas de otros materiales")]):
    for pix in lista:
        ax.plot(pix)
    ax.set_xlabel("Bandas")
    ax.set_ylabel("Reflectancia normalizada")
    ax.set_title(titulo)
    ax.grid(True)
plt.tight_layout()
plt.show()"""),
        md(f"Armamos el dataset (1 = {nombre}, 0 = {otros}), lo desordenamos y lo partimos en entrenamiento (80 %) y prueba (20 %)"),
        code("""firmas=np.concatenate([l_pix_si, l_pix_no])
etiquetas=[1]*len(l_pix_si) + [0]*len(l_pix_no)
df=pd.DataFrame(firmas)
df['label']=etiquetas
df=df.sample(frac=1, random_state=42).reset_index(drop=True)

df_train, df_test = train_test_split(
    df,
    test_size=0.20,
    stratify=df['label'],
    random_state=42
)
df_train.shape"""),
        md("Calculamos el píxel promedio (la mediana) de cada grupo"),
        code(f"""firm_si_train=df_train[df_train['label']==1].drop(columns='label').to_numpy()
firm_no_train=df_train[df_train['label']==0].drop(columns='label').to_numpy()
pix_prom_train=np.median(firm_si_train, axis=0)
pix_prom_no=np.median(firm_no_train, axis=0)
plt.plot(pix_prom_train, label="{nombre}")
plt.plot(pix_prom_no, label="Otros")
plt.xlabel("Bandas")
plt.ylabel("Reflectancia normalizada")
plt.legend()
plt.grid()
plt.show()"""),
        md("Medimos la longitud de arco cada 55 bandas para ver en qué tramos se diferencian"),
        code(f"""for i in range(55,381,55):
  s_si=long_arco(pix_prom_train[i-55:i])
  s_no=long_arco(pix_prom_no[i-55:i])
  plt.scatter(i, s_si, color="red")
  plt.scatter(i, s_no, color="blue")
  print(i-55,"-",i, " material:", round(s_si,4), " otros:", round(s_no,4))
plt.scatter([], [], color="red", label="{nombre}")
plt.scatter([], [], color="blue", label="Otros")
plt.xlabel("Fin del tramo (banda)")
plt.ylabel("Longitud de arco")
plt.legend()
plt.grid()
plt.show()"""),
        md("Definimos los 2 tramos de bandas y la longitud de arco del píxel promedio"),
        code(f"""lim1={a}
lim2={b}
lim3={c}
lim4={d}
s1=long_arco(pix_prom_train[lim1:lim2])
s2=long_arco(pix_prom_train[lim3:lim4])
arr_s_prom=np.asarray([s1,s2])
print(arr_s_prom)"""),
        md("""Sacamos el umbral con las firmas del material. Antes quitamos las muestras atípicas (ruido de brillos, olas o bordes):
las que quedan por debajo de Q1 - 1,5·(Q3 - Q1) en el diagrama de caja. El umbral es la similitud mínima de las que quedan"""),
        code("""l_arc_si=[]
for id,row in df_train.iterrows():
  if(row['label']==1):
    pix=np.asarray(row[0:380])
    long_arco1=long_arco(pix[lim1:lim2])
    long_arco2=long_arco(pix[lim3:lim4])
    arr_s_pix=np.asarray([long_arco1,long_arco2])
    sim=similitud_porcentual(arr_s_prom,arr_s_pix)
    l_arc_si.append(sim)
q1,q3=np.percentile(l_arc_si,[25,75])
limite=q1-1.5*(q3-q1)
limpias=[s for s in l_arc_si if s>=limite]
print("Muestras atípicas quitadas:", len(l_arc_si)-len(limpias), "de", len(l_arc_si))
plt.boxplot(l_arc_si, orientation="horizontal")
plt.axvline(limite, color="red", linestyle="--", label="límite de atípicas")
plt.xlabel("Similitud con la firma promedio (%)")
plt.legend()
plt.show()
umbral=round(np.min(limpias),3)
print("Min", umbral)
print("Max", round(np.max(l_arc_si),3))"""),
        md(f"Probamos con las firmas de {otros}"),
        code("""l_arc_no=[]
cont=0
for id,row in df_train.iterrows():
  if(row['label']==0):
    pix=np.asarray(row[0:380])
    long_arco1=long_arco(pix[lim1:lim2])
    long_arco2=long_arco(pix[lim3:lim4])
    arr_s_pix=np.asarray([long_arco1,long_arco2])
    sim=similitud_porcentual(arr_s_prom,arr_s_pix)
    l_arc_no.append(sim)
    if(sim<umbral):
      cont+=1
print("Otros bien separados:", cont, "de", len(l_arc_no))
print("Min", round(np.min(l_arc_no),3))
print("Max", round(np.max(l_arc_no),3))"""),
        md("Probamos con el conjunto de prueba y calculamos las métricas"),
        code("""predicciones=[]
for id,row in df_test.iterrows():
  pix=np.asarray(row[0:380])
  long_arco1=long_arco(pix[lim1:lim2])
  long_arco2=long_arco(pix[lim3:lim4])
  arr_s_pix=np.asarray([long_arco1,long_arco2])
  sim=similitud_porcentual(arr_s_prom,arr_s_pix)
  if(sim>=umbral):
    predicciones.append(1)
  else:
    predicciones.append(0)
df_test['pred']=predicciones

y_true = df_test['label']
y_pred = df_test['pred']
print("Accuracy :", round(accuracy_score(y_true, y_pred),3))
print("Precision:", round(precision_score(y_true, y_pred),3))
print("Recall   :", round(recall_score(y_true, y_pred),3))
print("F1-score :", round(f1_score(y_true, y_pred),3))
print("\\nMatriz de confusión:")
print(confusion_matrix(y_true, y_pred))"""),
        md("Pintamos la imagen con el método" + (" y guardamos la similitud de cada píxel en `mapa` para el mapa final" if varios else "")),
        code(f"""img_marcada=imagen.copy()
tam=arr_norm.shape
mapa=np.zeros((tam[0],tam[1]))
cont_pix=0
for i in range(tam[0]):
  for j in range(tam[1]):
    if(not con_datos[i][j]):
      continue
    #Obtenemos el pixel i,j de la imagen
    pix=arr_norm[i][j]
    long_arco1=long_arco(pix[lim1:lim2])
    long_arco2=long_arco(pix[lim3:lim4])
    arr_s_pix=np.asarray([long_arco1,long_arco2])
    sim=similitud_porcentual(arr_s_prom,arr_s_pix)
    mapa[i][j]=sim
    if(sim>=umbral):
      img_marcada[i][j]={color}
      cont_pix+=1
porc_pix_arc=(cont_pix/(tam[0]*tam[1]))*100
print("Porcentaje de {nombre}:", round(porc_pix_arc,3),"%")

fig, axes = plt.subplots(1, 2, figsize=(16, 8))
axes[0].imshow(imagen)
axes[0].set_title("Original")
axes[1].imshow(img_marcada)
axes[1].set_title("{nombre.capitalize()}")
plt.show()
plt.imsave("../resultados/cartagena{n}_{clave}.png", img_marcada)""" + (f"""

#Guardamos lo de este material para la imagen final
mapas["{clave}"]=mapa
umbrales["{clave}"]=umbral""" if varios else "")),
    ]


def celdas_final(n, materiales, sufijo):
    return [
        md("Imagen final con todos los materiales. Si un píxel pasa el umbral de varios, gana el más parecido (el de mayor similitud)"),
        code(f"""colores={dic_colores(materiales)}
nombres={dic_nombres(materiales)}
img_final=imagen.copy()
mejor_sim=np.zeros(con_datos.shape)
ganador=np.full(con_datos.shape, "", dtype=object)
for nombre in mapas:
  pasa=(mapas[nombre]>=umbrales[nombre]) & (mapas[nombre]>mejor_sim)
  mejor_sim[pasa]=mapas[nombre][pasa]
  ganador[pasa]=nombre
for nombre in mapas:
  img_final[ganador==nombre]=colores[nombre]
  print(nombre, ":", round(np.mean(ganador==nombre)*100,3), "%")

plt.figure(figsize=(10, 10))
plt.imshow(img_final)
plt.legend(handles=[mpatches.Patch(color=np.array(colores[m])/255, label=nombres[m]) for m in colores], loc="upper right")
plt.title("Cartagena {n}")
plt.show()
plt.imsave("../resultados/cartagena{n}{sufijo}_final.png", img_final)"""),
    ]


def generar(n, carpeta="recuadros"):
    # los de materiales van aparte de los de agua
    sufijo = "" if carpeta == "recuadros" else "_materiales"
    materiales = materiales_de(n, carpeta)
    if not materiales:
        print(f"cartagena{n}: no hay materiales en datos/cartagena{n}/{carpeta}/, se omite")
        return
    if carpeta == "recuadros" and not os.path.exists(os.path.join(RAIZ, "datos", f"cartagena{n}", "recuadros", "otros.csv")):
        print(f"cartagena{n}: falta datos/cartagena{n}/recuadros/otros.csv, se omite")
        return
    if carpeta == "muestras" and len(materiales) < 2:
        print(f"cartagena{n}: hace falta al menos 2 materiales en muestras/ para compararlos entre sí, se omite")
        return
    varios = len(materiales) > 1
    celdas = [md(f"# Cartagena {n}: {lista([nom for _, nom, _ in materiales])} con longitud de arco")]
    celdas += celdas_inicio(n, materiales, carpeta, varios)
    if varios:
        celdas.append(code("#Aquí se guardan los mapas de similitud y los umbrales de cada material\nmapas={}\numbrales={}"))
    for k, (clave, nombre, color) in enumerate(materiales, start=1):
        celdas += celdas_material(n, k, clave, nombre, color, carpeta, varios)
    if varios:
        celdas += celdas_final(n, materiales, sufijo)
    nb = nbf.v4.new_notebook()
    nb.cells = celdas
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    salida = os.path.join(RAIZ, "notebooks", f"cartagena{n}{sufijo}.ipynb")
    nbf.write(nb, salida)
    print("ok", os.path.relpath(salida, RAIZ))


if __name__ == "__main__":
    args = sys.argv[1:]
    carpeta = "recuadros"
    if args and args[0] == "--muestras":
        carpeta, args = "muestras", args[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    for n in args:
        generar(int(n), carpeta)
