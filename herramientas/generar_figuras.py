"""Genera las figuras de los documentos (docs/fuentes/img/fig_*.png) a partir de datos.json.

Uso (desde la raíz del repo):
    .venv/bin/python herramientas/generar_figuras.py

docs/fuentes/datos.json tiene datos reales del proyecto: firmas promedio de cartagena4 y las
similitudes de 200 muestras del río de cartagena3.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AQUI = os.path.join(RAIZ, "docs", "fuentes")
IMG = os.path.join(AQUI, "img")
COLORES = {"agua salada": "#1fb6d4", "asfalto": "#6c7a89", "techo concreto": "#f2a516", "vegetacion": "#2fb36b"}
NOMBRES = {"agua salada": "Agua salada", "asfalto": "Asfalto", "techo concreto": "Techo de concreto", "vegetacion": "Vegetación"}
TRAMOS = [(40, 140, "#7c5cff"), (150, 270, "#ff5c8a")]
TEXTO = "#1d2433"

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 12, "axes.edgecolor": "#c9cfdb", "axes.labelcolor": TEXTO,
    "xtick.color": "#5a6378", "ytick.color": "#5a6378", "axes.spines.top": False, "axes.spines.right": False,
})


def guardar(fig, nombre):
    fig.savefig(os.path.join(IMG, nombre), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def long_arco(r):
    return float(np.sum(np.abs(np.diff(r))))


datos = json.load(open(os.path.join(AQUI, "datos.json")))
firmas = {k: np.array(v) for k, v in datos["firmas_cartagena4"].items()}
rio = datos["rio_cartagena3"]

# 1. Firmas de los 4 materiales con los 2 tramos sombreados
fig, ax = plt.subplots(figsize=(9, 4.2))
for a, b, c in TRAMOS:
    ax.axvspan(a, b, color=c, alpha=0.08)
    ax.text((a + b) / 2, 1.0, f"tramo {a}–{b}", transform=ax.get_xaxis_transform(), ha="center", va="bottom", color=c, fontsize=11, fontweight="bold")
for k, f in firmas.items():
    ax.plot(f, color=COLORES[k], lw=2.4, label=NOMBRES[k])
ax.set_xlabel("Banda (1 a 380)")
ax.set_ylabel("Reflectancia normalizada")
ax.set_xlim(0, 379)
ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.18))
guardar(fig, "fig_firmas.png")

# 2. Qué mide la longitud de arco: los saltos entre bandas vecinas (zoom sobre vegetación)
f = firmas["vegetacion"]
x = np.arange(150, 171)
fig, ax = plt.subplots(figsize=(9, 3.6))
ax.plot(x, f[x], color=COLORES["vegetacion"], lw=2.4, marker="o", ms=5)
for i in x[:-1]:
    ax.plot([i + 1, i + 1], [f[i], f[i + 1]], color="#ff5c8a", lw=3, alpha=0.85)
ax.set_xlabel("Banda")
ax.set_ylabel("Reflectancia")
ax.set_xticks(x[::2])
ax.set_title("Cada salto rosado es |R(i+1) − R(i)|. La longitud de arco es la suma de todos", color=TEXTO, fontsize=12, loc="left")
guardar(fig, "fig_saltos.png")

# 3. Longitud de arco de cada material en los 2 tramos
fig, ax = plt.subplots(figsize=(9, 3.8))
nombres = list(firmas)
y = np.arange(len(nombres))
l1 = [long_arco(firmas[k][40:140]) for k in nombres]
l2 = [long_arco(firmas[k][150:270]) for k in nombres]
ax.barh(y + 0.2, l1, height=0.38, color=TRAMOS[0][2], label="Tramo 40–140")
ax.barh(y - 0.2, l2, height=0.38, color=TRAMOS[1][2], label="Tramo 150–270")
for yi, a, b in zip(y, l1, l2):
    ax.text(a + 0.006, yi + 0.2, f"{a:.3f}".replace(".", ","), va="center", fontsize=11, color=TEXTO)
    ax.text(b + 0.006, yi - 0.2, f"{b:.3f}".replace(".", ","), va="center", fontsize=11, color=TEXTO)
ax.set_yticks(y, [NOMBRES[k] for k in nombres])
for t, k in zip(ax.get_yticklabels(), nombres):
    t.set_color(COLORES[k]); t.set_fontweight("bold")
ax.set_xlabel("Longitud de arco")
ax.set_xlim(0, max(l2) * 1.18)
ax.legend(frameon=False, loc="lower right")
guardar(fig, "fig_longitud_arco.png")

# 4. Firma promedio del río frente a un píxel con ruido
fig, ax = plt.subplots(figsize=(9, 3.6))
ax.plot(rio["firma_promedio"], color=COLORES["agua salada"], lw=2.4, label="Firma promedio del río")
ax.plot(rio["firma_pixel_con_ruido"], color="#ff4d4d", lw=1.6, label="Una muestra con ruido")
ax.set_xlabel("Banda")
ax.set_ylabel("Reflectancia normalizada")
ax.set_xlim(0, 379)
ax.legend(frameon=False)
guardar(fig, "fig_ruido.png")

# 5. Diagrama de caja de las similitudes del río y el límite de atípicas
s = np.array(rio["similitudes_muestras"])
lim = rio["limite_atipicas"]
fig, ax = plt.subplots(figsize=(9, 3.4))
rng = np.random.default_rng(0)
fuera = s < lim
ax.scatter(s[~fuera], 1.32 + rng.uniform(-0.1, 0.1, (~fuera).sum()), s=14, color="#8a94a8", alpha=0.7, label="Muestras limpias")
ax.scatter(s[fuera], 1.32 + rng.uniform(-0.1, 0.1, fuera.sum()), s=70, color="#ff4d4d", label="Atípicas (se quitan)", zorder=3)
ax.boxplot(s, orientation="horizontal", positions=[1], widths=0.3, patch_artist=True, showfliers=False,
           boxprops=dict(facecolor="#d6f4fa", edgecolor=COLORES["agua salada"], lw=1.8),
           medianprops=dict(color=TEXTO, lw=2), whiskerprops=dict(color=TEXTO), capprops=dict(color=TEXTO))
ax.axvline(lim, color="#f2a516", ls="--", lw=2)
ax.text(lim - 1, 1.62, f"límite = {lim:.1f}".replace(".", ","), color="#c98500", ha="right", fontweight="bold")
ax.annotate(f"mínimo sin limpiar: {rio['minimo_sin_limpiar']:.1f} %".replace(".", ","), (rio["minimo_sin_limpiar"], 1.32),
            xytext=(rio["minimo_sin_limpiar"] + 4, 0.72), color="#ff4d4d", arrowprops=dict(arrowstyle="->", color="#ff4d4d"))
ax.annotate(f"mínimo limpio: {rio['minimo_limpio']:.1f} %".replace(".", ","), (rio["minimo_limpio"], 1.32),
            xytext=(rio["minimo_limpio"] + 3, 0.68), color="#2fb36b", fontweight="bold", arrowprops=dict(arrowstyle="->", color="#2fb36b"))
ax.set_yticks([])
ax.set_ylim(0.6, 1.75)
ax.set_xlabel("Similitud de cada muestra con la firma promedio (%)")
ax.spines["left"].set_visible(False)
ax.legend(frameon=False, loc="upper left")
guardar(fig, "fig_caja.png")

print("ok:", sorted(n for n in os.listdir(IMG) if n.startswith("fig_")))
