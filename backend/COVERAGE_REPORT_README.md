# 📊 Generador de Reporte de Cobertura

Este script genera un reporte detallado de cobertura de código en formato texto, mostrando qué archivos y qué líneas están cubiertas por los tests y cuáles no.

## 🚀 Uso Rápido

### Windows
```bash
cd backend
generate_coverage.bat
```

O con nombre personalizado:
```bash
generate_coverage.bat mi_reporte.txt
```

### Linux/Mac
```bash
cd backend
./generate_coverage.sh
```

O con nombre personalizado:
```bash
./generate_coverage.sh mi_reporte.txt
```

### Python directo
```bash
cd backend
python generate_coverage_report.py
```

O con nombre personalizado:
```bash
python generate_coverage_report.py mi_reporte.txt
```

## 📋 Qué hace el script

1. **Ejecuta los tests con coverage**: Ejecuta `pytest` con `--cov` para recopilar datos de cobertura
2. **Analiza los datos**: Lee los datos de cobertura generados
3. **Genera el reporte**: Crea un archivo de texto con:
   - Resumen general (porcentaje total, archivos analizados)
   - Lista de archivos con líneas NO cubiertas (prioridad)
   - Lista de archivos con cobertura completa (100%)
   - Para cada archivo con líneas faltantes, muestra:
     - Porcentaje de cobertura
     - Líneas cubiertas (agrupadas por rangos)
     - Líneas faltantes (agrupadas por rangos)

## 📄 Formato del Reporte

El reporte incluye:

```
================================================================================
REPORTE DE COBERTURA DE CÓDIGO
Generado: 2024-01-15 10:30:45
================================================================================

RESUMEN GENERAL
--------------------------------------------------------------------------------
Total de archivos analizados: 45
Total de líneas ejecutables: 1250
Líneas ejecutadas: 1100 (88.0%)
Líneas no ejecutadas: 150 (12.0%)
Archivos con cobertura completa: 30
Archivos con líneas faltantes: 15

================================================================================
ARCHIVOS CON LÍNEAS NO CUBIERTAS
================================================================================

📄 api/services/stats/stats_service.py
   Cobertura: 85.5% (120/140 líneas)

  ✅ Cubiertas: 1-50, 52-80, 82-100, 102-120
  ❌ Faltantes: 51, 81, 101, 121-140

...
```

## ⚙️ Requisitos

- Python 3.8+
- `pytest` instalado
- `pytest-cov` instalado
- `coverage` instalado

## 🔍 Ejemplo de Salida

El reporte se guarda por defecto en `coverage_report.txt` en el directorio `backend/`.

Puedes abrirlo con cualquier editor de texto para ver:
- Qué archivos necesitan más tests
- Qué líneas específicas no están cubiertas
- El porcentaje de cobertura de cada archivo

## 💡 Tips

- Ejecuta el script después de agregar nuevos tests para ver el progreso
- Los archivos se ordenan por porcentaje de cobertura (menor primero)
- Las líneas se agrupan en rangos para facilitar la lectura (ej: `10-15` en lugar de `10, 11, 12, 13, 14, 15`)

