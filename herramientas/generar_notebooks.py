"""Genera notebooks/cartagena<N>.ipynb a partir de los recuadros marcados.

Uso (desde la raíz del repo):
    .venv/bin/python herramientas/generar_notebooks.py <N> [<N> ...]

Cada archivo datos/cartagena<N>/recuadros/<material>.csv (menos otros.csv) es un material.
Cada material se compara contra otros.csv usando la longitud de arco, igual que en
Cuaderno_Asbesto_ArcoV3.ipynb: 2 tramos de bandas, similitud porcentual y umbral = similitud mínima.
"""
import glob
import os
import sys

import nbformat as nbf

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIMS = (40, 140, 150, 270)
# Color (RGB) según cómo empieza el nombre del material; el resto toma uno de la paleta
COLORES = {"agua_salada": (0, 255, 255), "agua_dulce": (255, 0, 255)}
PALETA = [(255, 0, 0), (255, 255, 0), (0, 255, 0), (255, 128, 0), (128, 0, 255)]

md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell


def materiales_de(n):
    archivos = sorted(glob.glob(os.path.join(RAIZ, "datos", f"cartagena{n}", "recuadros", "*.csv")))
    claves = [os.path.splitext(os.path.basename(a))[0] for a in archivos]
    claves = [c for c in claves if c != "otros"]
    resultado, libre = [], 0
    for clave in claves:
        color = next((c for pref, c in COLORES.items() if clave.startswith(pref)), None)
        if color is None:
            color, libre = PALETA[libre % len(PALETA)], libre + 1
        resultado.append((clave, clave.replace("_", " "), color))
    return resultado


def tiene_png(n):
    return os.path.exists(os.path.join(RAIZ, "datos", f"cartagena{n}", "imagen", f"cartagena{n}.png"))


def celdas_inicio(n, materiales):
    if tiene_png(n):
        base = f"""imagen=cv2.cvtColor(cv2.imread(ruta+"/imagen/cartagena{n}.png"), cv2.COLOR_BGR2RGB)"""
    else:
        base = """#Esta imagen no trae png: la armamos con las bandas (29, 50, 70), las mismas del original
imagen=(get_rgb(img,(29,50,70))*255).astype(np.uint8)"""
    lectura = "\n".join(f"""recuadros["{c}"]=pd.read_csv(ruta+"/recuadros/{c}.csv")""" for c, _, _ in materiales)
    return [
        md("Importamos librerías"),
        code("""from spectral import *
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
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
        md("Normalizamos el arreglo con la imagen"),
        code("""maximo=np.max(arr)
minimo=np.min(arr)
arr_norm=(arr-minimo)/(maximo-minimo)"""),
        md("Marcamos los píxeles que sí tienen datos. Las zonas negras de la imagen están en cero en todas las bandas y no se deben usar ni pintar"),
        code("""con_datos=np.max(arr,axis=2)>0
print("Píxeles sin datos:", np.sum(~con_datos))"""),
        md("Imagen base para dibujar"),
        code(base + """
plt.figure(figsize=(8, 8))
plt.imshow(imagen)
plt.show()"""),
        md("Definimos la función de longitud de arco y el método de similitud (iguales al original)"),
        code("""def long_arco(R):
  return np.sum(np.abs(np.diff(R)))

def similitud_porcentual(A, B):
  A, B = np.array(A), np.array(B)
  #Similitud por posición: 100 si iguales, 0 si muy distintos
  sims = 100 * (1 - np.abs(A - B) / (np.abs(A) + np.abs(B) + 1e-9))
  return np.mean(sims)"""),
        md("""# Recuadros de muestra
Los recuadros (x1, y1, x2, y2) se marcan a mano con `herramientas/marcar_recuadros.py` y se guardan en `datos/cartagenaN/recuadros/`.
Cada material tiene su archivo, y `otros.csv` tiene lo que seguro **no** es ninguno de los materiales."""),
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
        md("Función para sacar los píxeles (con datos) que hay dentro de unos recuadros"),
        code("""def pixeles_de(rec):
  l_pix=[]
  for id,r in rec.iterrows():
    for y in range(r.y1,r.y2):
      for x in range(r.x1,r.x2):
        if(con_datos[y][x]):
          l_pix.append((x,y))
  return pd.DataFrame(l_pix, columns=["x","y"])"""),
    ]


def celdas_material(n, k, clave, nombre, color):
    a, b, c, d = LIMS
    return [
        md(f"# Material {k}: {nombre}"),
        md(f"Sacamos los píxeles de los recuadros: {nombre} (si) y otros (no). Tomamos 250 de cada uno al azar, como en el original"),
        code(f"""df_si=pixeles_de(recuadros["{clave}"])
df_no=pixeles_de(recuadros_otros)
print("Píxeles de {nombre}:", len(df_si), " otros:", len(df_no))
df_si=df_si.sample(n=min(250,len(df_si)),random_state=42)
df_no=df_no.sample(n=min(250,len(df_no)),random_state=42)
punt_si=df_si[["x","y"]].astype(int).to_numpy()
punt_no=df_no[["x","y"]].astype(int).to_numpy()
print("Usados:", len(punt_si), len(punt_no))"""),
        md(f"Dibujamos los puntos sobre la imagen (rojo = {nombre}, azul = otros)"),
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
        md(f"Creamos el dataset (1 = {nombre}, 0 = otro), lo desordenamos y lo partimos en entrenamiento y prueba"),
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
        md("Calculamos el pixel promedio (mediana) del material y de los otros"),
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
        md("Longitud de arco por tramos de 55 bandas, para ver en qué tramos se diferencian más"),
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
        md("Definimos los límites de los 2 tramos y la longitud de arco del pixel promedio"),
        code(f"""lim1={a}
lim2={b}
lim3={c}
lim4={d}
s1=long_arco(pix_prom_train[lim1:lim2])
s2=long_arco(pix_prom_train[lim3:lim4])
arr_s_prom=np.asarray([s1,s2])
print(arr_s_prom)"""),
        md("Probamos con las firmas del material para sacar el umbral (la similitud mínima, como en el original)"),
        code("""l_arc_si=[]
for id,row in df_train.iterrows():
  if(row['label']==1):
    pix=np.asarray(row[0:380])
    long_arco1=long_arco(pix[lim1:lim2])
    long_arco2=long_arco(pix[lim3:lim4])
    arr_s_pix=np.asarray([long_arco1,long_arco2])
    sim=similitud_porcentual(arr_s_prom,arr_s_pix)
    l_arc_si.append(sim)
umbral=round(np.min(l_arc_si),3)
print("Min", umbral)
print("Max", round(np.max(l_arc_si),3))"""),
        md("Probamos con las firmas de otros materiales"),
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
        md("Probamos el método con el conjunto de prueba y calculamos las métricas"),
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
        md("Desplegamos el método sobre la imagen. Guardamos la similitud de cada píxel en `mapa` para usarla al final"),
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
plt.imsave("../resultados/cartagena{n}_{clave}.png", img_marcada)

#Guardamos lo de este material para la imagen final
mapas["{clave}"]=mapa
umbrales["{clave}"]=umbral"""),
    ]


def celdas_final(n, materiales):
    colores = "{" + ", ".join(f'"{c}":{col}' for c, _, col in materiales) + "}"
    return [
        md("# Imagen final con todos los materiales"),
        md("Si un píxel pasa el umbral de varios materiales, gana el más parecido (el de mayor % de similitud)"),
        code(f"""colores={colores}
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
plt.legend(handles=[mpatches.Patch(color=np.array(colores[m])/255, label=m.replace("_"," ")) for m in colores], loc="upper right")
plt.title("Cartagena {n}")
plt.show()
plt.imsave("../resultados/cartagena{n}_final.png", img_final)"""),
    ]


def generar(n):
    materiales = materiales_de(n)
    if not materiales:
        print(f"cartagena{n}: no hay recuadros de materiales en datos/cartagena{n}/recuadros/, se omite")
        return
    if not os.path.exists(os.path.join(RAIZ, "datos", f"cartagena{n}", "recuadros", "otros.csv")):
        print(f"cartagena{n}: falta otros.csv (márcalo con marcar_recuadros.py {n} otros), se omite")
        return
    titulo = " y ".join(nom for _, nom, _ in materiales)
    celdas = [md(f"# Cartagena {n}: {titulo} con longitud de arco")]
    celdas += celdas_inicio(n, materiales)
    celdas.append(code("#Aquí se guardan los mapas de similitud y umbrales de cada material\nmapas={}\numbrales={}"))
    for k, (clave, nombre, color) in enumerate(materiales, start=1):
        celdas += celdas_material(n, k, clave, nombre, color)
    if len(materiales) > 1:
        celdas += celdas_final(n, materiales)
    nb = nbf.v4.new_notebook()
    nb.cells = celdas
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    salida = os.path.join(RAIZ, "notebooks", f"cartagena{n}.ipynb")
    nbf.write(nb, salida)
    print("ok", os.path.relpath(salida, RAIZ))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for n in sys.argv[1:]:
        generar(int(n))
