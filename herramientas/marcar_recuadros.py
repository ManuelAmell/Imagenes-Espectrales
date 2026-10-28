"""Marca recuadros de un material sobre la imagen y los guarda en datos/cartagenaN/recuadros/<material>.csv.

Uso: .venv/bin/python herramientas/marcar_recuadros.py <N> <material>   (por ejemplo: 4 agua_salada, o 4 otros)
Arrastra con el mouse y presiona ENTER para guardar cada recuadro; ESC para terminar. Los recuadros nuevos se agregan a los que ya hay."""
import csv
import os
import sys

import cv2
import numpy as np

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLUMNAS = ["x1", "y1", "x2", "y2", "nombre"]


def ruta_imagen(n):
    return os.path.join(RAIZ, "datos", f"cartagena{n}", "imagen")


def ruta_csv(n, material):
    return os.path.join(RAIZ, "datos", f"cartagena{n}", "recuadros", f"{material}.csv")


def cargar_imagen(n):
    """Devuelve la imagen en BGR (para OpenCV). Si no hay png, la arma con las bandas (29, 50, 70)."""
    png = os.path.join(ruta_imagen(n), f"cartagena{n}.png")
    if os.path.exists(png):
        return cv2.imread(png)
    from spectral import open_image, get_rgb
    img = open_image(os.path.join(ruta_imagen(n), f"cartagena{n}.hdr"))
    rgb = (get_rgb(img, (29, 50, 70)) * 255).astype(np.uint8)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def leer_recuadros(archivo):
    if not os.path.exists(archivo):
        return []
    with open(archivo, newline="") as f:
        return [(int(r["x1"]), int(r["y1"]), int(r["x2"]), int(r["y2"]), r["nombre"]) for r in csv.DictReader(f)]


def agregar_recuadros(archivo, nuevos):
    """Agrega recuadros (x1, y1, x2, y2, nombre) al CSV, creándolo con encabezado si no existe."""
    existe = os.path.exists(archivo)
    os.makedirs(os.path.dirname(archivo), exist_ok=True)
    with open(archivo, "a", newline="") as f:
        w = csv.writer(f)
        if not existe:
            w.writerow(COLUMNAS)
        w.writerows(nuevos)


def roi_a_recuadros(rois, material, desde):
    """Convierte lo que devuelve cv2.selectROIs (x, y, ancho, alto) a (x1, y1, x2, y2, nombre)."""
    recuadros = []
    for x, y, w, h in rois:
        if w > 0 and h > 0:
            recuadros.append((int(x), int(y), int(x + w), int(y + h), f"{material} {desde + len(recuadros)}"))
    return recuadros


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    n, material = int(sys.argv[1]), sys.argv[2]
    archivo = ruta_csv(n, material)
    existentes = leer_recuadros(archivo)

    imagen = cargar_imagen(n)
    vista = imagen.copy()
    for x1, y1, x2, y2, nombre in existentes:
        cv2.rectangle(vista, (x1, y1), (x2, y2), (0, 255, 255), 1)

    titulo = f"cartagena{n} - {material}: arrastra, ENTER guarda, ESC termina"
    rois = cv2.selectROIs(titulo, vista, showCrosshair=False, fromCenter=False)
    cv2.destroyAllWindows()

    nuevos = roi_a_recuadros(rois, material, len(existentes) + 1)
    if not nuevos:
        print("No se guardó ningún recuadro.")
        return
    agregar_recuadros(archivo, nuevos)
    print(f"Se agregaron {len(nuevos)} recuadros a {os.path.relpath(archivo, RAIZ)}:")
    for r in nuevos:
        print("  ", r)


if __name__ == "__main__":
    main()
