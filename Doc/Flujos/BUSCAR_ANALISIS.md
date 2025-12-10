# Flujo Completo: Buscar Análisis (Frontend → Backend)

## Resumen del Flujo

El flujo de búsqueda permite al usuario filtrar y localizar análisis específicos utilizando criterios de búsqueda como fecha, lote, rango de dimensiones o peso.

**Endpoint:** `GET /api/v1/images/` o `GET /api/v1/analysis/search/`

**Autenticación:** Requerida (IsAuthenticated)

**Flujo:**
1. Usuario ingresa criterios de búsqueda en el formulario
2. Frontend envía GET con parámetros de búsqueda
3. Backend valida criterios de búsqueda
4. Backend ejecuta consulta filtrando análisis
5. Backend aplica filtros de permisos
6. Backend retorna resultados de búsqueda
7. Frontend muestra resultados con resaltado de términos

**Parámetros de búsqueda:**
- `fecha_desde`: Fecha inicio
- `fecha_hasta`: Fecha fin
- `lote_id`: ID del lote
- `finca_id`: ID de la finca
- `peso_min`: Peso mínimo en gramos
- `peso_max`: Peso máximo en gramos
- `alto_min`: Alto mínimo en mm
- `alto_max`: Alto máximo en mm
- `variedad`: Variedad de cacao
- `search`: Búsqueda de texto libre

**Validaciones:**
- Rangos numéricos coherentes (mínimo <= máximo)
- Fechas válidas y coherentes
- Permisos del usuario para acceder a los análisis

**Tests:**
```bash
pytest images_app/tests/test_image_views.py::TestImageListView::test_search -v
pytest images_app/tests/test_image_views.py::TestImageListView::test_search_with_filters -v
```

