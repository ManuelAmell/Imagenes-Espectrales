"""Mide con qué se confunde cada material y guarda el resultado para los documentos.

Uso (desde la raíz del repo; necesita los .img de datos/cartagenaN/imagen/):
    .venv/bin/python herramientas/analizar_confusiones.py

Para cada imagen con muestras (datos/cartagenaN/muestras/) repite lo que hace el notebook generado con
--muestras (mismo muestreo, misma partición y misma limpieza de atípicas) y mide:
- qué % de los píxeles de cada material pasa el umbral de cada otro material,
- qué % de las zonas sin muestra propia (las de recuadros/: agua y otros) pasa cada umbral,
- la longitud de arco y el brillo (reflectancia media) de cada firma promedio,
- una muestra de píxeles con sus 2 longitudes de arco y su brillo (para graficar).
Escribe docs/fuentes/confusiones.json, que lee herramientas/generar_figuras.py.
"""
import glob
import json
import os

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from spectral import open_image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIMS = (40, 140, 150, 270)


def long_arco(R):
    return np.sum(np.abs(np.diff(R, axis=-1)), axis=-1)


def dos_numeros(F):
    """Las 2 longitudes de arco de cada firma (una fila por píxel)."""
    return np.stack([long_arco(F[..., LIMS[0]:LIMS[1]]), long_arco(F[..., LIMS[2]:LIMS[3]])], axis=-1)


def similitud(prom, F):
    A, B = dos_numeros(prom), dos_numeros(F)
    return np.mean(100 * (1 - np.abs(A - B) / (np.abs(A) + np.abs(B) + 1e-9)), axis=-1)


def modelo(arr, si, no):
    """Firma promedio y umbral, igual que el notebook."""
    f_si, f_no = arr[si.y.values, si.x.values], arr[no.y.values, no.x.values]
    df = pd.DataFrame(np.concatenate([f_si, f_no]))
    df["label"] = [1] * len(f_si) + [0] * len(f_no)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    tr, _ = train_test_split(df, test_size=0.2, stratify=df["label"], random_state=42)
    F = tr[tr.label == 1].drop(columns="label").to_numpy()
    prom = np.median(F, axis=0)
    s = similitud(prom, F)
    q1, q3 = np.percentile(s, [25, 75])
    return prom, float(np.min(s[s >= q1 - 1.5 * (q3 - q1)]))


def analizar(n):
    arr = np.asarray(open_image(os.path.join(RAIZ, "datos", f"cartagena{n}", "imagen", f"cartagena{n}.hdr")).load())
    arr = (arr - arr.min()) / (arr.max() - arr.min())
    con_datos = np.max(arr, axis=2) > 0
    archivos = sorted(glob.glob(os.path.join(RAIZ, "datos", f"cartagena{n}", "muestras", "*.csv")))
    pix = {}
    for a in archivos:
        d = pd.read_csv(a)
        d = d[con_datos[d.y, d.x]]
        pix[os.path.basename(a)[:-4]] = pd.DataFrame({"x": d.x.values, "y": d.y.values})
    if len(pix) < 2:
        return None
    modelos, salida = {}, {"materiales": {}, "zonas": {}}
    rng = np.random.default_rng(0)
    for m in pix:
        otros = pd.concat([pix[o] for o in pix if o != m])
        si = pix[m].sample(n=min(250, len(pix[m])), random_state=42)
        no = otros.sample(n=min(250, len(otros)), random_state=42)
        prom, umbral = modelo(arr, si, no)
        modelos[m] = (prom, umbral)
        F = arr[pix[m].y.values, pix[m].x.values]
        muestra = F[rng.choice(len(F), min(300, len(F)), replace=False)]
        L = dos_numeros(prom)
        salida["materiales"][m] = {
            "umbral": round(umbral, 2), "L1": round(float(L[0]), 3), "L2": round(float(L[1]), 3),
            "brillo": round(float(prom.mean()), 3),
            "puntos": [[round(float(a), 4), round(float(b), 4), round(float(c), 4)]
                       for (a, b), c in zip(dos_numeros(muestra), muestra.mean(axis=1))],
        }
    for m, (prom, umbral) in modelos.items():
        salida["materiales"][m]["pasan"] = {
            o: round(float(np.mean(similitud(prom, arr[pix[o].y.values, pix[o].x.values]) >= umbral) * 100), 1)
            for o in pix}
    for a in sorted(glob.glob(os.path.join(RAIZ, "datos", f"cartagena{n}", "recuadros", "*.csv"))):
        for _, z in pd.read_csv(a).iterrows():
            ys, xs = np.mgrid[z.y1:z.y2, z.x1:z.x2]
            Fz = arr[ys.ravel(), xs.ravel()]
            Fz = Fz[np.max(Fz, axis=1) > 0]
            salida["zonas"][f"{os.path.basename(a)[:-4]}: {z.nombre}"] = {
                m: round(float(np.mean(similitud(p, Fz) >= u) * 100), 1) for m, (p, u) in modelos.items()}
    return salida


if __name__ == "__main__":
    resultado = {}
    for n in (1, 2, 3, 4):
        r = analizar(n)
        if r is None:
            print(f"cartagena{n}: menos de 2 materiales en muestras/, se omite")
            continue
        resultado[f"cartagena{n}"] = r
        print(f"cartagena{n}: ok")
    salida = os.path.join(RAIZ, "docs", "fuentes", "confusiones.json")
    json.dump(resultado, open(salida, "w"), ensure_ascii=False)
    print("ok", os.path.relpath(salida, RAIZ))
