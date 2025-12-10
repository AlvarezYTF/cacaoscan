# Flujo de Análisis de Imagen con Comandos de Test

## Resumen del Flujo

El flujo de análisis de imagen procesa la imagen mediante modelos de inteligencia artificial (YOLOv8, modelos de regresión) para predecir las dimensiones (alto, ancho, grosor) y peso del grano de cacao. Este flujo se ejecuta automáticamente después del procesamiento, pero también puede ejecutarse de forma independiente sobre una imagen ya procesada.

**Nota:** El análisis está integrado en el flujo de procesamiento (`PROCESAR_IMAGEN.md`), pero este documento describe el análisis como operación independiente.

---

## Componentes del Flujo

### 1. Endpoint HTTP

**Archivo:** `backend/images_app/views/image/user/scan_views.py` o endpoint específico de análisis

**Vista:** `ScanMeasureView` (análisis completo) o `AnalyzeImageView` (análisis independiente)

**Flujo:**
1. Recibe petición POST con `image_id` o imagen procesada
2. Valida que la imagen esté procesada
3. Llama al servicio de análisis
4. Retorna predicciones

### 2. Servicio de Análisis

**Archivo:** `backend/api/services/analysis_service.py`

**Servicio:** `AnalysisService`

**Método:** `analyze_image(image_id, user)` o `process_image_with_segmentation()`

**Flujo:**
1. Obtiene imagen procesada (crop sin fondo)
2. Carga modelos de IA necesarios
3. Aplica transformaciones de normalización
4. Extrae características de píxeles
5. Ejecuta modelo de regresión híbrido
6. Desnormaliza predicciones
7. Aplica factores de calibración
8. Guarda resultados en `CacaoPrediction`

---

## Endpoint de la API

**URL:** `POST /api/v1/scan/measure/` (análisis completo) o `POST /api/v1/images/{image_id}/analyze/` (análisis independiente)

**Autenticación:** Requerida (IsAuthenticated)

**Content-Type:** `multipart/form-data` (análisis completo) o `application/json` (análisis independiente)

**Parámetros:**
- `image`: Archivo de imagen (análisis completo)
- `image_id`: ID de imagen procesada (análisis independiente)

**Respuesta exitosa (200 OK):**
```json
{
  "success": true,
  "data": {
    "image_id": 1,
    "prediction": {
      "alto_mm": 25.5,
      "ancho_mm": 18.3,
      "grosor_mm": 12.1,
      "peso_g": 8.7,
      "confidence": 0.92
    },
    "processing_time_ms": 8500
  }
}
```

---

## Comandos de Test

### Tests de Servicio de Análisis

**Archivo:** `backend/api/tests/test_analysis_service.py`

```bash
# Test: Análisis exitoso de imagen procesada
pytest api/tests/test_analysis_service.py::TestAnalysisService::test_analyze_image_success -v

# Test: Imagen no encontrada
pytest api/tests/test_analysis_service.py::TestAnalysisService::test_analyze_image_not_found -v

# Test: Sin permisos
pytest api/tests/test_analysis_service.py::TestAnalysisService::test_analyze_image_no_permission -v

# Test: Modelos no disponibles
pytest api/tests/test_analysis_service.py::TestAnalysisService::test_analyze_image_models_unavailable -v
```

### Tests de Predicción ML

**Archivo:** `backend/ml/tests/test_prediction.py` (si existe)

```bash
# Test: Predicción exitosa
pytest ml/tests/test_prediction.py::TestCacaoPredictor::test_predict_success -v

# Test: Predicción con mock
pytest ml/tests/test_prediction.py::TestCacaoPredictor::test_predict_with_mock -v
```

---

## Flujo Completo Paso a Paso

### 1. Usuario solicita análisis
- Desde imagen procesada o como parte del flujo completo

### 2. Backend valida precondiciones
- Imagen procesada existe
- Modelos ML están cargados
- Factores de calibración calculados

### 3. Backend ejecuta análisis
- Carga imagen procesada
- Preprocesa imagen
- Ejecuta modelos de ML
- Obtiene predicciones normalizadas
- Desnormaliza predicciones
- Aplica calibración

### 4. Backend guarda resultados
- Crea/actualiza registro `CacaoPrediction`
- Asocia predicción con imagen
- Guarda métricas y confianzas

### 5. Respuesta al frontend
- Retorna predicciones con dimensiones y peso
- Incluye confianza del modelo
- Incluye tiempo de procesamiento

---

## Validaciones Implementadas

- Imagen debe estar procesada
- Modelos ML deben estar disponibles
- Usuario debe tener permisos para analizar la imagen
- Predicciones deben estar en rangos físicamente posibles

---

## Archivos Relacionados

### Backend
- `backend/api/services/analysis_service.py` - Servicio de análisis
- `backend/training/services/prediction_service.py` - Servicio de predicción
- `backend/ml/prediction/predict.py` - Clase CacaoPredictor
- `backend/images_app/models.py` - Modelos CacaoImage y CacaoPrediction

### Frontend
- `frontend/src/views/PredictionView.vue` - Vista de predicción
- `frontend/src/services/predictionApi.js` - Servicio de API

---

## Notas Adicionales

- El análisis se ejecuta automáticamente después del procesamiento en el flujo completo
- Puede ejecutarse de forma independiente sobre imágenes ya procesadas
- Los modelos ML deben estar cargados en memoria
- El tiempo de análisis no debe exceder 60 segundos por imagen
- Las predicciones se validan contra rangos físicamente posibles para granos de cacao

