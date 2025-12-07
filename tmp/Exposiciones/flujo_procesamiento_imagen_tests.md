# Flujo de Procesamiento de Imagen con Comandos de Test

## 📋 Resumen del Flujo

El flujo completo de procesamiento de imagen sigue estos pasos:

1. **Request HTTP** → `POST /api/v1/scan/measure/`
2. **Vista API** → `ScanMeasureView.post()`
3. **Servicio de Análisis** → `AnalysisService.process_image_with_segmentation()`
4. **Validación** → `ImageProcessingService.validate_image_file_complete()`
5. **Almacenamiento y Segmentación** → `ImageStorageService.save_uploaded_image_with_segmentation()`
6. **Carga de Imagen** → `ImageProcessingService.load_image()`
7. **Predicción ML** → `PredictionService.predict()`
8. **Guardado de Predicción** → `ImageStorageService.save_prediction()`
9. **Response** → JSON con resultados

---

## 🔄 Flujo Detallado con Archivos y Tests

### Paso 1: Endpoint HTTP

**Archivo**: `backend/images_app/views/image/user/scan_views.py`

**Flujo**:
```43:161:backend/images_app/views/image/user/scan_views.py
class ScanMeasureView(APIView):
    """
    Endpoint para medición de granos de cacao.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Procesa una imagen y devuelve mediciones del grano.
        """
        image_file, error_response = self._validate_image_file(request)
        if error_response:
            return error_response
        
        analysis_service = AnalysisService()
        result = analysis_service.process_image_with_segmentation(image_file, request.user)
        
        if result.success:
            serializer = ScanMeasureResponseSerializer(data=result.data)
            if serializer.is_valid():
                self._send_analysis_email(request.user, result.data)
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
```

**Tests de Vista**:
```bash
# Desde backend/
pytest images_app/tests/test_scan_views.py -v

# Test específico: Validación de archivo
pytest images_app/tests/test_scan_views.py::test_validate_image_file_success -v

# Test específico: POST exitoso
pytest images_app/tests/test_scan_views.py::test_post_success -v

# Test específico: POST sin imagen
pytest images_app/tests/test_scan_views.py::test_post_no_image -v

# Test específico: Error de servicio
pytest images_app/tests/test_scan_views.py::test_post_service_error -v

# Test de mapeo de errores
pytest images_app/tests/test_scan_views.py::test_map_error_to_status_code_validation -v
```

---

### Paso 2: Servicio de Análisis (Orquestador)

**Archivo**: `backend/api/services/analysis_service.py`

**Flujo**:
```43:120:backend/api/services/analysis_service.py
def process_image_with_segmentation(self, image_file: UploadedFile, user: User) -> ServiceResult:
    """
    Processes a complete image: validation, storage, segmentation, and prediction.
    """
    try:
        start_time = time.time()
        
        # 1. Validate image file
        validation_result = self.processing_service.validate_image_file_complete(image_file)
        if not validation_result.success:
            return validation_result
        
        # 2. Save image with segmentation
        save_result = self.storage_service.save_uploaded_image_with_segmentation(image_file, user)
        if not save_result.success:
            return save_result
        
        cacao_image = save_result.data['cacao_image']
        processed_png_path = save_result.data.get('processed_png_path')
        
        # 3. Load image for prediction
        load_result = self.processing_service.load_image(image_file)
        if not load_result.success:
            return load_result
        
        image = load_result.data
        
        # 4. Perform prediction
        prediction_result = self.prediction_service.predict(image)
        if not prediction_result.success:
            return prediction_result
        
        result = prediction_result.data
        prediction_time_ms = result.get('processing_time_ms', 0)
        
        # 5. Save prediction
        save_pred_result = self.storage_service.save_prediction(
            cacao_image,
            result,
            prediction_time_ms
        )
```

**Tests del Servicio de Análisis**:
```bash
# Desde backend/
pytest api/tests/test_analysis_service.py -v

# Test específico: Procesamiento exitoso completo
pytest api/tests/test_analysis_service.py::TestAnalysisService::test_process_image_with_segmentation_success -v

# Test específico: Error de validación
pytest api/tests/test_analysis_service.py::TestAnalysisService::test_process_image_validation_failure -v

# Test de historial de análisis
pytest api/tests/test_analysis_service.py::TestAnalysisService::test_get_analysis_history -v

# Test de estadísticas
pytest api/tests/test_analysis_service.py::TestAnalysisService::test_get_analysis_statistics -v
```

---

### Paso 3: Validación de Imagen

**Archivo**: `backend/images_app/services/image/processing_service.py`

**Flujo**:
- Validación de tipo de archivo (JPG, PNG, BMP)
- Validación de tamaño (máximo 8MB para análisis)
- Validación de dimensiones mínimas
- Validación de nombre de archivo

**Tests de Procesamiento**:
```bash
# Desde backend/
pytest images_app/tests/test_processing_service.py -v

# Test específico: Validación exitosa
pytest images_app/tests/test_processing_service.py::TestImageProcessingService::test_validate_image_file_success -v

# Test específico: Tipo de archivo inválido
pytest images_app/tests/test_processing_service.py::TestImageProcessingService::test_validate_image_file_invalid_type -v

# Test específico: Archivo demasiado grande
pytest images_app/tests/test_processing_service.py::TestImageProcessingService::test_validate_image_file_too_large -v

# Test específico: Validación completa exitosa
pytest images_app/tests/test_processing_service.py::TestImageProcessingService::test_validate_image_file_complete_success -v

# Test específico: Imagen demasiado pequeña
pytest images_app/tests/test_processing_service.py::TestImageProcessingService::test_validate_image_file_complete_too_small -v

# Test de carga de imagen
pytest images_app/tests/test_processing_service.py::TestImageProcessingService::test_load_image_success -v

# Test de conversión a RGB
pytest images_app/tests/test_processing_service.py::TestImageProcessingService::test_load_image_converts_to_rgb -v

# Test de segmentación
pytest images_app/tests/test_processing_service.py::TestImageProcessingService::test_segment_image_success -v
```

---

### Paso 4: Almacenamiento y Segmentación

**Archivo**: `backend/images_app/services/image/storage_service.py`

**Flujo**:
- Guardar imagen original
- Segmentar y recortar el fondo
- Guardar imagen procesada (PNG con transparencia)
- Crear registro en base de datos (CacaoImage)

**Tests de Almacenamiento**:
```bash
# Desde backend/
pytest images_app/tests/test_storage_service.py -v

# Test específico: Guardar imagen exitosa
pytest images_app/tests/test_storage_service.py::TestImageStorageService::test_save_uploaded_image_success -v

# Test específico: Guardar imagen con segmentación
pytest images_app/tests/test_storage_service.py::TestImageStorageService::test_save_uploaded_image_with_segmentation_success -v

# Test específico: Guardar predicción
pytest images_app/tests/test_storage_service.py::TestImageStorageService::test_save_prediction_success -v

# Test de error en segmentación
pytest images_app/tests/test_storage_service.py::TestImageStorageService::test_save_uploaded_image_with_segmentation_segmentation_error -v
```

---

### Paso 5: Predicción ML

**Archivo**: `backend/training/services/prediction_service.py`

**Flujo**:
- Cargar modelos ML
- Preprocesar imagen
- Ejecutar predicción de dimensiones (alto, ancho, grosor)
- Ejecutar predicción de peso
- Calcular confianzas

**Tests de Predicción** (si existen):
```bash
# Desde backend/
pytest ml/tests/ -v

# Tests de segmentación ML
pytest ml/tests/test_processor.py -v

# Test específico: Segmentación básica
pytest ml/tests/test_processor.py::TestDeshadowAlpha::test_deshadow_alpha_basic -v
```

---

### Paso 6: Guardado de Predicción

**Archivo**: `backend/images_app/services/image/storage_service.py`

**Flujo**:
- Crear registro CacaoPrediction
- Vincular con CacaoImage
- Guardar métricas y confianzas

---

## 🧪 Comandos Completos de Test por Componente

### Tests Unitarios de Componentes Individuales

```bash
# Navegar al directorio backend
cd backend

# Activar entorno virtual (si es necesario)
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 1. Tests de Validación y Procesamiento de Imagen
pytest images_app/tests/test_processing_service.py -v

# 2. Tests de Almacenamiento
pytest images_app/tests/test_storage_service.py -v

# 3. Tests de Servicio de Análisis (Orquestador)
pytest api/tests/test_analysis_service.py -v

# 4. Tests de Vistas (API Endpoints)
pytest images_app/tests/test_scan_views.py -v

# 5. Tests de Vistas Generales de Imágenes
pytest images_app/tests/test_views.py -v

# 6. Tests de Serializers
pytest images_app/tests/test_images_serializers.py -v

# 7. Tests de Segmentación ML
pytest ml/tests/test_processor.py -v
```

---

### Tests de Integración Completa

```bash
# Desde backend/
# Test de flujo completo (requiere base de datos)
pytest images_app/tests/test_scan_views.py::test_post_success -v
pytest api/tests/test_analysis_service.py::TestAnalysisService::test_process_image_with_segmentation_success -v
```

---

### Tests con Cobertura

```bash
# Desde backend/
# Cobertura del servicio de procesamiento
pytest images_app/tests/test_processing_service.py --cov=images_app.services.image.processing_service --cov-report=html

# Cobertura del servicio de análisis
pytest api/tests/test_analysis_service.py --cov=api.services.analysis_service --cov-report=html

# Cobertura de vistas
pytest images_app/tests/test_scan_views.py --cov=images_app.views.image.user.scan_views --cov-report=html

# Cobertura completa de imágenes
pytest images_app/tests/ --cov=images_app --cov-report=html
```

---

## 🔍 Orden Recomendado de Ejecución de Tests

Para verificar el flujo completo paso a paso:

```bash
cd backend

# 1. Primero: Tests unitarios de validación
pytest images_app/tests/test_processing_service.py::TestImageProcessingService::test_validate_image_file_success -v

# 2. Segundo: Tests de almacenamiento
pytest images_app/tests/test_storage_service.py::TestImageStorageService::test_save_uploaded_image_with_segmentation_success -v

# 3. Tercero: Tests del servicio de análisis completo
pytest api/tests/test_analysis_service.py::TestAnalysisService::test_process_image_with_segmentation_success -v

# 4. Cuarto: Tests de la vista API completa
pytest images_app/tests/test_scan_views.py::test_post_success -v

# 5. Finalmente: Todos los tests relacionados
pytest images_app/tests/test_processing_service.py images_app/tests/test_storage_service.py api/tests/test_analysis_service.py images_app/tests/test_scan_views.py -v
```

---

## 📊 Estructura de Tests por Archivo

### `test_processing_service.py`
- ✅ `test_validate_image_file_success`
- ✅ `test_validate_image_file_invalid_type`
- ✅ `test_validate_image_file_too_large`
- ✅ `test_validate_image_file_complete_success`
- ✅ `test_validate_image_file_complete_too_small`
- ✅ `test_load_image_success`
- ✅ `test_load_image_converts_to_rgb`
- ✅ `test_segment_image_success`

### `test_storage_service.py`
- ✅ `test_save_uploaded_image_success`
- ✅ `test_save_uploaded_image_with_segmentation_success`
- ✅ `test_save_prediction_success`
- ✅ `test_save_uploaded_image_with_segmentation_segmentation_error`

### `test_analysis_service.py`
- ✅ `test_process_image_with_segmentation_success`
- ✅ `test_process_image_validation_failure`
- ✅ `test_get_analysis_history`
- ✅ `test_get_analysis_statistics`

### `test_scan_views.py`
- ✅ `test_validate_image_file_success`
- ✅ `test_validate_image_file_missing`
- ✅ `test_post_success`
- ✅ `test_post_no_image`
- ✅ `test_post_service_error`
- ✅ `test_map_error_to_status_code_validation`

---

## 🚀 Test End-to-End Completo

Para probar el flujo completo desde HTTP hasta base de datos:

```bash
cd backend

# Ejecutar todos los tests del flujo de procesamiento
pytest \
    images_app/tests/test_processing_service.py \
    images_app/tests/test_storage_service.py \
    api/tests/test_analysis_service.py \
    images_app/tests/test_scan_views.py \
    -v --tb=short
```

---

## 📝 Notas Importantes

1. **Base de Datos**: Los tests de integración requieren una base de datos de prueba configurada en `pytest.ini` o `conftest.py`

2. **Mocks**: Muchos tests usan mocks para evitar dependencias de modelos ML y servicios externos

3. **Archivos de Imagen**: Los tests crean imágenes en memoria usando `SimpleUploadedFile` y `PIL.Image`

4. **Autenticación**: Los tests de vistas requieren usuarios autenticados (usando `force_authenticate`)

5. **Segmentation**: La segmentación real requiere los modelos ML cargados, por lo que se mockea en muchos tests

---

## 🔗 Archivos Relacionados

- **Vista API**: `backend/images_app/views/image/user/scan_views.py`
- **Servicio de Análisis**: `backend/api/services/analysis_service.py`
- **Servicio de Procesamiento**: `backend/images_app/services/image/processing_service.py`
- **Servicio de Almacenamiento**: `backend/images_app/services/image/storage_service.py`
- **Servicio de Predicción**: `backend/training/services/prediction_service.py`
- **Segmentación ML**: `backend/ml/segmentation/processor.py`
- **URLs**: `backend/api/urls.py` (línea 65: `scan/measure/`)

---

## ✅ Checklist de Verificación

Para verificar que el flujo completo funciona:

- [ ] Tests de validación pasan
- [ ] Tests de procesamiento pasan
- [ ] Tests de almacenamiento pasan
- [ ] Tests del servicio de análisis pasan
- [ ] Tests de vistas API pasan
- [ ] Tests de integración end-to-end pasan
- [ ] Cobertura de código > 80%

