# Flujo Completo: Ver Historial de Análisis (Frontend → Backend)

## Resumen del Flujo

El flujo de visualización de historial permite al usuario consultar y visualizar todos los análisis de imágenes realizados anteriormente, organizados por fecha, lote o finca.

**Endpoint:** `GET /api/v1/images/` o `GET /api/v1/analysis/history/`

**Autenticación:** Requerida (IsAuthenticated)

**Flujo:**
1. Usuario accede a sección "Historial de Análisis"
2. Frontend envía GET con filtros opcionales (fecha, lote, finca)
3. Backend valida permisos y aplica filtros
4. Backend obtiene análisis del usuario (o accesibles según permisos)
5. Backend aplica paginación (25 registros por página)
6. Backend retorna lista de análisis con predicciones
7. Frontend muestra historial con paginación y filtros

**Parámetros de consulta:**
- `page`: Número de página
- `page_size`: Tamaño de página (default: 25)
- `fecha_desde`: Fecha inicio (opcional)
- `fecha_hasta`: Fecha fin (opcional)
- `lote_id`: Filtrar por lote (opcional)
- `finca_id`: Filtrar por finca (opcional)

**Respuesta:**
```json
{
  "count": 100,
  "next": "http://example.com/api/v1/images/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "image_url": "...",
      "prediction": {
        "alto_mm": 25.5,
        "ancho_mm": 18.3,
        "peso_g": 8.7
      },
      "created_at": "2024-12-19T10:00:00Z"
    }
  ]
}
```

**Tests:**
```bash
pytest images_app/tests/test_image_views.py::TestImageListView::test_get_history -v
pytest api/tests/test_analysis_service.py::TestAnalysisService::test_get_analysis_history -v
```

