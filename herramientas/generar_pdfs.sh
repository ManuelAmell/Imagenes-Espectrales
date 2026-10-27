#!/usr/bin/env bash
# Convierte los HTML de docs/fuentes/ en los PDF de docs/ con Chromium sin ventana.
# Uso (desde la raíz del repo): bash herramientas/generar_pdfs.sh
set -euo pipefail
cd "$(dirname "$0")/../docs/fuentes"
for doc in explicacion_metodo reporte; do
  [ -f "$doc.html" ] || continue
  chromium --headless=new --disable-gpu --no-pdf-header-footer \
    --print-to-pdf="../$doc.pdf" "file://$PWD/$doc.html" 2>/dev/null
  echo "ok docs/$doc.pdf"
done
