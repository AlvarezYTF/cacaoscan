# Tests de Correcciones de SonarQube

Este directorio contiene tests específicos para verificar que cada bug reportado por SonarQube fue corregido correctamente.

## Estructura de Tests

### 1. `test_error_response_details.py`
**Bug SonarQube:** "Remove this unexpected named argument 'errors'"  
**Archivos corregidos:**
- `backend/api/incremental_views.py`
- `backend/api/model_metrics_views.py`

**Tests:**
- Verifica que `create_error_response` usa el parámetro `details` correctamente
- Verifica que las vistas usan `details` en lugar de `errors`

### 2. `test_model_metrics_error_response.py`
**Bug SonarQube:** "Remove this unexpected named argument 'errors'"  
**Archivo corregido:**
- `backend/api/model_metrics_views.py`

**Tests:**
- Verifica que `ModelMetricsCreateView` usa `details` en respuestas de error
- Verifica que las excepciones usan `details` correctamente

### 3. `test_redundant_elif.py`
**Bug SonarQube:** "This branch duplicates the one on line X"  
**Archivos corregidos:**
- `backend/api/services/auth_service.py`
- `backend/auth_app/models.py`

**Tests:**
- Verifica que se eliminaron los `elif` redundantes
- Verifica que los métodos retornan resultados consistentes

### 4. `test_create_model_parameters.py`
**Bug SonarQube:** "Remove this unexpected named argument 'target'"  
**Archivo corregido:**
- `backend/ml/regression/incremental_train.py`

**Tests:**
- Verifica que `create_model` se llama con `num_outputs=1` y no con `target`

### 5. `test_html_accessibility.py`
**Bug SonarQube:** "Add a description to this table"  
**Archivos corregidos:**
- `backend/api/templates/emails/analysis_complete.html`
- `frontend/src/components/admin/AdminAgricultorComponents/DataTable.vue`

**Tests:**
- Verifica que las tablas HTML tienen elementos `<caption>` para accesibilidad
- Verifica que los componentes Vue tienen `aria-label` y `caption`

### 6. `test_html_lang_attribute.py`
**Bug SonarQube:** "Add 'lang' and/or 'xml:lang' attributes to this '<html>' element"  
**Archivo corregido:**
- `frontend/cypress/support/component-index.html`

**Tests:**
- Verifica que el elemento `<html>` tiene atributos `lang` y `xml:lang`

## Ejecutar Tests

### En el contenedor Docker:
```bash
docker compose exec backend python manage.py test api.tests.test_sonarqube
```

### Ejecutar un test específico:
```bash
docker compose exec backend python manage.py test api.tests.test_sonarqube.test_error_response_details
```

### Con verbosidad:
```bash
docker compose exec backend python manage.py test api.tests.test_sonarqube --verbosity=2
```

## Notas

- Algunos tests pueden requerir que el contenedor esté ejecutándose
- Los tests de HTML/Vue verifican archivos estáticos, por lo que pueden fallar si los archivos no existen
- Los tests de `create_model` pueden requerir mocks adicionales dependiendo de la implementación

