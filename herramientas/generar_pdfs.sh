#!/usr/bin/env bash
# Convierte los HTML de docs/fuentes/ en los PDF de docs/ (necesita Chromium o Chrome).
# Uso, desde la raíz del proyecto: bash herramientas/generar_pdfs.sh
set -eu
cd "$(dirname "$0")/../docs/fuentes"
for navegador in chromium chromium-browser google-chrome; do
  if command -v "$navegador" >/dev/null; then break; fi
  navegador=""
done
[ -n "$navegador" ] || { echo "No encontré Chromium ni Chrome"; exit 1; }
for doc in explicacion_metodo reporte; do
  "$navegador" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="../$doc.pdf" "file://$PWD/$doc.html"
  echo "listo docs/$doc.pdf"
done
