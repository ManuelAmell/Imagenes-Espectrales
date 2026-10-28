"""Mide con qué se confunde cada material y prepara los datos de los documentos.
Escribe docs/fuentes/confusiones.json y docs/fuentes/datos.json (necesita los .img)."""
import glob
import json
import os

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from spectral import open_image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUENTES = os.path.join(RAIZ, "docs", "fuentes")
LIMS = (40, 140, 150, 270)


def long_arco(R):
    return np.sum(np.abs(np.diff(R, axis=-1)), axis=-1)


def dos_numeros(F):
    # las 2 longitudes de arco de cada firma
    return np.stack([long_arco(F[..., LIMS[0]:LIMS[1]]), long_arco(F[..., LIMS[2]:LIMS[3]])], axis=-1)


def similitud(prom, F):
    A, B = dos_numeros(prom), dos_numeros(F)
    return np.mean(100 * (1 - np.abs(A - B) / (np.abs(A) + np.abs(B) + 1e-9)), axis=-1)


def cargar(n):
    ruta = os.path.join(RAIZ, "datos", f"cartagena{n}", "imagen", f"cartagena{n}.hdr")
    arr = np.asarray(open_image(ruta).load())
    arr = (arr - arr.min()) / (arr.max() - arr.min())
    return arr, np.max(arr, axis=2) > 0


def entrenar(arr, si, no):
    # igual que el notebook: mezcla, 80 % para entrenar, firma promedio y similitudes
    f_si, f_no = arr[si.y.values, si.x.values], arr[no.y.values, no.x.values]
    df = pd.DataFrame(np.concatenate([f_si, f_no]))
    df["label"] = [1] * len(f_si) + [0] * len(f_no)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    tr, _ = train_test_split(df, test_size=0.20, stratify=df["label"], random_state=42)
    F = tr[tr.label == 1].drop(columns="label").to_numpy()
    prom = np.median(F, axis=0)
    return prom, F, similitud(prom, F)


def limite_atipicas(s):
    q1, q3 = np.percentile(s, [25, 75])
    return q1, q3, q1 - 1.5 * (q3 - q1)


def pixeles_de(rec, con_datos):
    # mismo orden que el notebook (primero filas, luego columnas)
    pix = [(x, y) for _, r in rec.iterrows() for y in range(r.y1, r.y2) for x in range(r.x1, r.x2) if con_datos[y][x]]
    return pd.DataFrame(pix, columns=["x", "y"])


def analizar(n):
    arr, con_datos = cargar(n)
    pix = {}
    for a in sorted(glob.glob(os.path.join(RAIZ, "datos", f"cartagena{n}", "muestras", "*.csv"))):
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
        prom, _, s = entrenar(arr, si, no)
        umbral = float(np.min(s[s >= limite_atipicas(s)[2]]))
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


def datos_documentos():
    # cartagena4: firmas de agua salada, asfalto, techo de concreto y vegetación
    arr, con_datos = cargar(4)
    rec = pd.read_csv(os.path.join(RAIZ, "datos", "cartagena4", "recuadros", "agua_salada.csv"))
    agua = pixeles_de(rec, con_datos)
    firmas = {"agua salada": np.median(arr[agua.y.values, agua.x.values], axis=0)}
    for m in ("asfalto", "techo_concreto", "vegetacion"):
        d = pd.read_csv(os.path.join(RAIZ, "datos", "cartagena4", "muestras", f"{m}.csv"))
        firmas[m.replace("_", " ")] = np.median(arr[d.y.values, d.x.values], axis=0)
    del arr
    # cartagena3: el río, con las mismas muestras y la misma partición que el notebook
    arr, con_datos = cargar(3)
    rio = pixeles_de(pd.read_csv(os.path.join(RAIZ, "datos", "cartagena3", "recuadros", "agua_dulce_rio.csv")), con_datos)
    otros = pixeles_de(pd.read_csv(os.path.join(RAIZ, "datos", "cartagena3", "recuadros", "otros.csv")), con_datos)
    si = rio.sample(n=min(250, len(rio)), random_state=42)
    no = otros.sample(n=min(250, len(otros)), random_state=42)
    prom, F, s = entrenar(arr, si, no)
    q1, q3, lim = limite_atipicas(s)
    return {
        "firmas_cartagena4": {k: [round(float(v), 5) for v in f] for k, f in firmas.items()},
        "longitud_arco_cartagena4": {k: {"tramo_40_140": round(float(long_arco(f[40:140])), 4),
                                         "tramo_150_270": round(float(long_arco(f[150:270])), 4)} for k, f in firmas.items()},
        "rio_cartagena3": {
            "firma_promedio": [round(float(v), 5) for v in prom],
            "firma_pixel_con_ruido": [round(float(v), 5) for v in F[int(np.argmin(s))]],
            "similitudes_muestras": [round(float(v), 2) for v in s],
            "q1": round(float(q1), 2), "q3": round(float(q3), 2), "limite_atipicas": round(float(lim), 2),
            "minimo_sin_limpiar": round(float(s.min()), 2),
            "minimo_limpio": round(float(s[s >= lim].min()), 2),
            "atipicas": int(np.sum(s < lim)),
        },
    }


if __name__ == "__main__":
    resultado = {}
    for c in sorted(glob.glob(os.path.join(RAIZ, "datos", "cartagena*"))):
        nombre = os.path.basename(c)
        r = analizar(int(nombre[-1]))
        if r is None:
            print(nombre + ": menos de 2 materiales en muestras/, se omite")
            continue
        resultado[nombre] = r
        print(nombre + ": ok")
    with open(os.path.join(FUENTES, "confusiones.json"), "w") as f:
        json.dump(resultado, f, ensure_ascii=False)
    with open(os.path.join(FUENTES, "datos.json"), "w") as f:
        json.dump(datos_documentos(), f, ensure_ascii=False)
    print("ok: confusiones.json y datos.json")
