#!/bin/bash
# Script para generar reporte de cobertura en formato texto
# Uso: ./generate_coverage.sh [nombre_archivo_salida.txt]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

OUTPUT_FILE="${1:-coverage_report.txt}"

echo "========================================"
echo "Generando reporte de cobertura..."
echo "========================================"
echo ""

python3 generate_coverage_report.py "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "Reporte generado exitosamente!"
    echo "========================================"
    echo ""
    echo "Archivo: $OUTPUT_FILE"
    echo ""
else
    echo ""
    echo "========================================"
    echo "Error al generar el reporte"
    echo "========================================"
    exit 1
fi

