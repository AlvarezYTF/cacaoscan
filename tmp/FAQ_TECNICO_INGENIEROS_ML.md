# FAQ Técnico - Sistema ML CacaoScan
## Guía de Respuestas para Ingenieros

Este documento contiene las preguntas técnicas más comunes que los ingenieros pueden hacer sobre el sistema ML de CacaoScan, junto con respuestas detalladas y técnicas.

---

## 🏗️ ARQUITECTURA Y DISEÑO

### Q1: ¿Por qué eligieron PyTorch en lugar de TensorFlow?

**Respuesta:**
- **Flexibilidad de debugging**: PyTorch permite debugging más intuitivo con ejecución dinámica
- **API más pythonica**: Más natural para desarrolladores Python
- **Mejor soporte para investigación**: Facilita experimentación rápida
- **Ecosistema maduro**: torchvision, timm, y otras librerías bien integradas
- **Detección automática GPU/CPU**: Manejo transparente de dispositivos
- **Comunidad activa**: Buen soporte y documentación

**Contexto adicional**: TensorFlow fue considerado, pero PyTorch se alinea mejor con el desarrollo iterativo y la experimentación requerida para este proyecto.

---

### Q2: ¿Por qué un modelo híbrido en lugar de solo CNN?

**Respuesta:**
El modelo híbrido combina:
1. **CNN (ResNet18 + ConvNeXt)**: Aprende features visuales complejas de la imagen
2. **Pixel Features**: Features de dominio específico (dimensiones en píxeles, área, aspect ratio)

**Ventajas**:
- **Mejor precisión**: Las features de píxeles proporcionan información métrica directa
- **Rápida convergencia**: Menos datos necesarios gracias a features de dominio
- **Interpretabilidad**: Features de píxeles son comprensibles
- **Robustez**: Si una fuente falla, la otra puede compensar

**Evidencia**: Los modelos híbridos muestran mejor R² que modelos solo CNN (típicamente +5-10% de mejora).

---

### Q3: ¿Por qué usan ResNet18 y ConvNeXt juntos?

**Respuesta:**
- **Complementariedad**: ResNet18 y ConvNeXt capturan diferentes aspectos de la imagen
- **Diversidad de features**: ResNet18 (512 dims) + ConvNeXt (768 dims) = 1280 dimensiones de features
- **Redundancia**: Si un backbone falla, el otro puede compensar
- **Transfer learning**: Ambos pre-entrenados en ImageNet, conocimiento complementario

**Nota técnica**: Se podría usar solo uno, pero la combinación mejora el rendimiento sin aumentar significativamente el costo computacional (son pre-entrenados).

---

### Q4: ¿Por qué YOLO es obligatorio para validación?

**Respuesta:**
**Prevención de falsos positivos**:
- YOLO valida que la imagen contiene realmente un grano de cacao
- Evita procesar imágenes sin granos (ruido, fondos, otros objetos)
- Valida clase correcta: solo acepta clases "cacao", "cacao_grain", "cocoa", "cocoa_bean"
- Valida tamaño y proporción del objeto

**Validaciones estrictas**:
- Confianza mínima: 75%
- Área mínima: 0.5% de la imagen (mínimo 2000 píxeles)
- Área máxima: 40% de la imagen
- Aspect ratio: entre 0.2 y 4.0

**Beneficio**: Reduce errores de predicción y procesamiento de imágenes inválidas.

---

### Q5: ¿Por qué usan una cascada de segmentación (U-Net → rembg → OpenCV)?

**Respuesta:**
**Estrategia de fallback progresivo**:

1. **U-Net (primario)**: Modelo entrenado específicamente para nuestro dominio
   - Mejor precisión cuando funciona
   - Requiere entrenamiento

2. **rembg/U2Net (secundario)**: Modelo general de eliminación de fondo
   - Alta calidad
   - No requiere entrenamiento específico
   - Fallback si U-Net falla

3. **OpenCV (terciario)**: Métodos tradicionales (GrabCut, watershed)
   - No requiere modelos ML
   - Funciona como último recurso
   - Menor precisión pero mayor robustez

**Ventaja**: Garantiza que siempre hay un método disponible, incluso si los modelos ML fallan.

---

## ⚡ PERFORMANCE Y ESCALABILIDAD

### Q6: ¿Cómo manejan el rendimiento del sistema?

**Respuesta:**
**Optimizaciones implementadas**:

1. **GPU Acceleration**: 
   - Detección automática GPU/CPU
   - Uso de GPU cuando está disponible
   - Fallback automático a CPU

2. **Lazy Loading**:
   - Modelos se cargan solo cuando se necesitan
   - Patrón Singleton para evitar cargas múltiples
   - Cache de modelos en memoria

3. **Batch Processing**:
   - Procesamiento por lotes de imágenes
   - Optimización de operaciones vectorizadas

4. **Caching**:
   - Cache de estado de modelos (5 minutos)
   - Cache de validación de dataset
   - Cache de predicciones (donde aplica)

5. **Async Processing**:
   - Tareas largas (entrenamiento, validación) pueden ejecutarse asíncronamente con Celery
   - No bloquea el servidor web

**Métricas típicas**:
- Predicción individual: ~500-1500ms (CPU), ~200-500ms (GPU)
- Segmentación: ~200-800ms
- Batch de 10 imágenes: ~5-15 segundos

---

### Q7: ¿Cómo escalan el sistema si aumenta la carga?

**Respuesta:**
**Estrategias de escalabilidad**:

1. **Horizontal Scaling**:
   - Múltiples instancias del backend
   - Load balancer distribuye requests
   - Cada instancia carga sus propios modelos

2. **Model Serving Separado**:
   - Servidor dedicado para ML (TorchServe, TensorFlow Serving)
   - Backend web se comunica vía API/gRPC
   - Permite escalar ML independientemente

3. **Queue System**:
   - Celery + Redis/RabbitMQ para procesamiento asíncrono
   - Workers escalables independientemente
   - Priorización de tareas

4. **Model Optimization**:
   - Quantization (INT8) para reducir tamaño y aumentar velocidad
   - Model pruning para reducir complejidad
   - TensorRT para optimización GPU (NVIDIA)

5. **Caching Agresivo**:
   - Cache de predicciones (si misma imagen)
   - CDN para servir crops/resultados
   - Redis para cache distribuido

**Nota**: Actualmente diseñado para escalar, pero implementación actual es single-instance.

---

### Q8: ¿Cuánta memoria RAM necesita el sistema?

**Respuesta:**
**Requisitos de memoria**:

- **Modelos cargados en memoria**:
  - ResNet18: ~45 MB
  - ConvNeXt Tiny: ~110 MB
  - U-Net: ~10 MB
  - YOLOv8-seg: ~50 MB
  - **Total modelos**: ~215 MB

- **Memoria de trabajo**:
  - Procesamiento de imagen: ~50-200 MB por imagen
  - Batch processing: ~200 MB - 1 GB (depende del batch size)
  - Overhead del sistema: ~500 MB

**Recomendación**:
- **Mínimo**: 4 GB RAM (CPU mode, batch size pequeño)
- **Recomendado**: 8-16 GB RAM (GPU mode, batch processing)
- **Producción**: 16+ GB RAM (múltiples workers, caching)

**Nota**: Con GPU, la memoria GPU también se usa (~2-4 GB VRAM).

---

## 🔒 SEGURIDAD Y ROBUSTEZ

### Q9: ¿Cómo validan que las imágenes son válidas?

**Respuesta:**
**Validación en múltiples capas**:

1. **Validación de archivo**:
   - Formato: JPG, PNG, BMP, TIFF
   - Tamaño máximo: Configurable (default: 10 MB)
   - Resolución mínima: 50x50 píxeles

2. **Validación YOLO (obligatoria)**:
   - Verifica que contiene un grano de cacao
   - Valida clase correcta
   - Valida tamaño y proporción

3. **Validación de segmentación**:
   - Área mínima del crop
   - Ratio de visibilidad mínimo
   - Validación de calidad del crop

4. **Validación de predicción**:
   - Límites físicos razonables (alto: 5-60mm, ancho: 3-30mm, etc.)
   - Validación de confianza mínima

**Si alguna validación falla**: Se rechaza la imagen y se retorna error descriptivo.

---

### Q10: ¿Cómo manejan errores y excepciones?

**Respuesta:**
**Estrategia de manejo de errores**:

1. **Excepciones personalizadas**:
   - `SegmentationError`: Error en segmentación
   - `ModelNotLoadedError`: Modelos no cargados
   - `InvalidImageError`: Imagen inválida
   - `PredictionError`: Error en predicción

2. **Logging detallado**:
   - Todos los errores se registran con contexto completo
   - Stack traces para debugging
   - Niveles de log: DEBUG, INFO, WARNING, ERROR

3. **Fallbacks**:
   - Cascada de métodos de segmentación
   - Fallback CPU si GPU falla
   - Métodos alternativos si primarios fallan

4. **Respuestas de error descriptivas**:
   - Códigos HTTP apropiados (400, 500, 503)
   - Mensajes de error claros y accionables
   - Sugerencias de solución cuando es posible

5. **Validación temprana**:
   - Validar inputs antes de procesar
   - Detectar problemas lo antes posible

---

### Q11: ¿Cómo garantizan la reproducibilidad de los resultados?

**Respuesta:**
**Estrategias de reproducibilidad**:

1. **Versionado de modelos**:
   - Cada modelo entrenado tiene versión
   - Metadata almacenada (epochs, batch size, hiperparámetros)
   - Timestamps y checksums

2. **Seeds aleatorios**:
   - Seeds fijos para inicialización de pesos
   - Seeds para data augmentation
   - Seeds para shuffling de datos

3. **Normalización consistente**:
   - Scalers guardados con el modelo
   - Misma normalización en entrenamiento y predicción

4. **Configuración guardada**:
   - Hiperparámetros guardados en archivos JSON
   - Configuración de entrenamiento versionada

5. **Determinismo**:
   - `torch.manual_seed()` para reproducibilidad
   - `torch.use_deterministic_algorithms(True)` cuando es posible

**Limitación**: Con GPU, algunas operaciones pueden no ser completamente determinísticas, pero los resultados son muy consistentes.

---

## 📊 MÉTRICAS Y EVALUACIÓN

### Q12: ¿Qué métricas usan para evaluar los modelos?

**Respuesta:**
**Métricas de regresión**:

1. **R² Score (Coeficiente de Determinación)**:
   - Principal métrica de bondad de ajuste
   - Rango: -∞ a 1.0 (1.0 = perfecto)
   - Target: > 0.85 para cada dimensión

2. **MAE (Mean Absolute Error)**:
   - Error absoluto promedio en mm/gramos
   - Más interpretable que RMSE
   - Target: < 2mm para dimensiones, < 0.5g para peso

3. **RMSE (Root Mean Squared Error)**:
   - Penaliza errores grandes más
   - Útil para detectar outliers
   - Target: < 3mm para dimensiones

4. **MAPE (Mean Absolute Percentage Error)**:
   - Error porcentual
   - Útil para comparar entre diferentes escalas
   - Target: < 10%

**Métricas adicionales**:
- Robust R²: Versión robusta a outliers
- Métricas por target: Alto, ancho, grosor, peso separados

**Almacenamiento**: Todas las métricas se guardan en BD para comparación histórica.

---

### Q13: ¿Cuál es el rendimiento actual del modelo?

**Respuesta:**
**Rendimiento típico (Modelo Híbrido)**:

| Target | R² Score | MAE | RMSE | MAPE |
|--------|----------|-----|------|------|
| **Alto** | 0.88-0.92 | 1.5-2.0 mm | 2.0-2.5 mm | 6-8% |
| **Ancho** | 0.85-0.90 | 1.2-1.8 mm | 1.8-2.2 mm | 7-9% |
| **Grosor** | 0.82-0.88 | 1.0-1.5 mm | 1.5-2.0 mm | 8-10% |
| **Peso** | 0.86-0.91 | 0.3-0.5 g | 0.4-0.6 g | 9-12% |

**Notas**:
- Estos valores pueden variar según el dataset de validación
- El modelo híbrido supera consistentemente a modelos solo CNN
- Grosor y peso son más difíciles de predecir (menor R²)

**Comparación con modelos base**:
- ResNet18 solo: R² ~0.75-0.80
- ConvNeXt solo: R² ~0.78-0.83
- Híbrido: R² ~0.85-0.92 (mejora de 5-10%)

---

## 🔧 MANTENIMIENTO Y OPERACIONES

### Q14: ¿Cómo entrenan nuevos modelos?

**Respuesta:**
**Proceso de entrenamiento**:

1. **Preparación de datos**:
   ```bash
   # Colocar imágenes en backend/media/cacao_images/raw/
   # Colocar CSV del dataset en backend/media/datasets/
   ```

2. **Segmentación y crops**:
   ```bash
   python manage.py train_unet_background --epochs 20
   python manage.py calibrate_dataset_pixels --segmentation-backend auto
   ```

3. **Entrenamiento de regresión**:
   ```bash
   python manage.py train_cacao_models --hybrid --use-pixel-features --epochs 50
   ```

4. **Evaluación**:
   - Métricas calculadas automáticamente
   - Reportes generados
   - Modelo guardado con versión

5. **Despliegue**:
   - Promover modelo a producción vía API o admin
   - Cargar nuevo modelo: `POST /api/v1/models/load/`

**Tiempo estimado**:
- U-Net: 30-60 min (GPU) o 2-4 horas (CPU)
- Calibración: 5-15 min
- Regresión: 1-3 horas (GPU) o 6-12 horas (CPU)

---

### Q15: ¿Cómo actualizan el sistema sin downtime?

**Respuesta:**
**Estrategia de actualización sin downtime**:

1. **Modelo en memoria**:
   - Modelos se cargan en memoria al iniciar
   - Nuevos modelos pueden cargarse sin reiniciar: `POST /api/v1/models/load/`
   - Modelos antiguos se mantienen hasta que se reemplacen

2. **Blue-Green Deployment**:
   - Nueva versión en instancia separada
   - Migración gradual de tráfico
   - Rollback fácil si hay problemas

3. **Versionado de modelos**:
   - Múltiples versiones pueden coexistir
   - API permite especificar versión a usar
   - Promoción gradual (canary deployment)

4. **Zero-downtime migrations**:
   - Cambios de BD con migraciones compatibles hacia atrás
   - Nuevos campos opcionales primero
   - Eliminación de campos en pasos posteriores

**Limitación actual**: Implementación básica permite hot-reload de modelos, pero actualizaciones de código requieren restart.

---

### Q16: ¿Cómo monitorean el sistema en producción?

**Respuesta:**
**Monitoreo implementado**:

1. **Logging estructurado**:
   - Todos los eventos se registran
   - Niveles: DEBUG, INFO, WARNING, ERROR
   - Contexto completo (usuario, imagen, tiempo, etc.)

2. **Métricas de modelo**:
   - API para consultar métricas: `GET /api/v1/ml/metrics/`
   - Tendencias de rendimiento: `GET /api/v1/ml/performance-trend/`
   - Comparación de modelos: `POST /api/v1/ml/model-comparison/`

3. **Health checks**:
   - Estado de modelos: `GET /api/v1/models/status/`
   - Estado de calibración: `GET /api/v1/ml/calibration/status/`

4. **Tracking de predicciones**:
   - Todas las predicciones se guardan en BD
   - Estadísticas de uso
   - Tiempo de procesamiento

**Recomendaciones adicionales** (no implementadas aún):
- Prometheus + Grafana para métricas en tiempo real
- Sentry para errores en producción
- APM tools (New Relic, DataDog) para performance

---

## 🚀 FUTURAS MEJORAS

### Q17: ¿Qué mejoras planean implementar?

**Respuesta:**
**Mejoras planificadas**:

1. **Rendimiento**:
   - Model quantization (INT8) para reducir latencia
   - TensorRT para optimización GPU
   - Model pruning para reducir tamaño

2. **Funcionalidades**:
   - Clasificación de calidad de granos
   - Detección de defectos
   - Análisis de madurez

3. **Arquitectura**:
   - Model serving separado (TorchServe)
   - Inferencia distribuida
   - Edge deployment (modelos móviles)

4. **Monitoreo**:
   - Dashboard en tiempo real
   - Alertas automáticas
   - Drift detection (detección de cambio de distribución)

5. **Experiencia**:
   - Batch processing mejorado
   - API streaming para resultados
   - Webhooks para notificaciones

---

### Q18: ¿Cómo manejan el concepto drift (cambio de distribución de datos)?

**Respuesta:**
**Estrategias actuales y planificadas**:

**Implementado**:
- Incremental learning (EWC) para adaptarse a nuevos datos
- Versiones de modelos para comparar rendimiento
- Tracking de predicciones para detectar cambios

**Planificado**:
1. **Drift Detection**:
   - Comparar distribución de features actual vs. entrenamiento
   - Alertas cuando drift es detectado
   - Retraining automático cuando es necesario

2. **Data Collection**:
   - Feedback loop para recopilar nuevos ejemplos
   - Validación humana de predicciones
   - Dataset balanceado con nuevos casos

3. **A/B Testing**:
   - Comparar modelos en producción
   - Migración gradual basada en métricas

**Nota**: Incremental learning ayuda, pero retraining periódico es recomendado.

---

## 🔬 PREGUNTAS TÉCNICAS AVANZADAS

### Q19: ¿Por qué normalizan los targets en lugar de usar valores directos?

**Respuesta:**
**Ventajas de normalización**:

1. **Convergencia más rápida**:
   - Valores en rango similar (0-1 o z-score)
   - Gradientes más estables
   - Learning rate más fácil de ajustar

2. **Balance entre targets**:
   - Peso (0.2-10g) y dimensiones (5-60mm) en escalas diferentes
   - Sin normalización, el modelo se enfocaría más en targets con valores mayores
   - Normalización permite que todos los targets tengan peso similar

3. **Estabilidad numérica**:
   - Evita problemas de overflow/underflow
   - Operaciones matemáticas más estables

4. **Desnormalización**:
   - Scalers guardados con el modelo
   - Desnormalización automática en predicción
   - Transparente para el usuario final

**Trade-off**: Requiere guardar scalers, pero el beneficio es significativo.

---

### Q20: ¿Por qué usan early stopping inteligente en lugar de entrenar épocas fijas?

**Respuesta:**
**Early Stopping Inteligente**:

**Ventajas**:
1. **Previene overfitting**: Detiene cuando validación deja de mejorar
2. **Ahorro de tiempo**: No desperdicia tiempo en entrenamiento innecesario
3. **Mejor generalización**: Modelo que generaliza mejor

**Inteligente vs. Simple**:
- **Simple**: Detiene cuando validación empeora
- **Inteligente**: Considera tendencias, patience adaptativo, múltiples métricas

**Configuración típica**:
- Patience: 10-15 épocas
- Monitoreo: Validation loss o R²
- Restauración: Mejor modelo guardado automáticamente

**Resultado**: Entrenamientos más eficientes y modelos de mejor calidad.

---

## 📋 CHECKLIST PARA PREGUNTAS IMPREVISTAS

Si te hacen una pregunta técnica que no conoces:

1. **Admite desconocimiento honestamente**: "No tengo esa información exacta, pero puedo investigarlo"

2. **Ofrece documentación**:
   - "Tenemos documentación técnica detallada en `tmp/HERRAMIENTAS_METODOS_PRINCIPIOS_ML.md`"
   - "El código está bien documentado con comentarios"

3. **Sugiere consultar el código**:
   - "Podemos revisar el código fuente para confirmar"
   - "Los archivos principales están en `backend/ml/`"

4. **Deja seguimiento abierto**:
   - "Puedo investigar y responder después de la reunión"
   - "Podemos programar una sesión técnica más detallada"

---

## 📚 REFERENCIAS RÁPIDAS

### Arquitecturas de Modelo
- **ResNet18**: Red residual, 512 features, ImageNet-1K
- **ConvNeXt Tiny**: Arquitectura moderna, 768 features, ImageNet-12k
- **U-Net**: Encoder-decoder, segmentación binaria
- **YOLOv8-seg**: Detección + segmentación, validación obligatoria

### Patrones de Diseño
- **Factory**: Creación de modelos (`factories/model_factory.py`)
- **Singleton**: Servicios ML (`MLService`)
- **Strategy**: Extracción de features (`extractors/strategies/`)

### Endpoints Clave
- Predicción: `POST /api/v1/scan/measure/`
- Estado: `GET /api/v1/models/status/`
- Entrenar: `POST /api/v1/ml/train/`
- Métricas: `GET /api/v1/ml/metrics/`

### Archivos Importantes
- Modelos: `backend/ml/regression/models.py`
- Predicción: `backend/ml/prediction/predict.py`
- Segmentación: `backend/ml/segmentation/processor.py`
- Servicio: `backend/training/services/ml/ml_service.py`

---

## 💡 TIPS PARA LA REUNIÓN

1. **Preparación**:
   - Lee este documento completo
   - Revisa `HERRAMIENTAS_METODOS_PRINCIPIOS_ML.md`
   - Familiarízate con la estructura de código

2. **Durante la reunión**:
   - Toma notas de preguntas sin respuesta inmediata
   - Ofrece demostración en vivo si es posible
   - Comparte documentación relevante

3. **Si no sabes algo**:
   - No inventes respuestas
   - Ofrece investigar y responder después
   - Dirige a documentación o código

4. **Enfócate en**:
   - Fortalezas del sistema (arquitectura sólida, principios SOLID)
   - Decisiones técnicas justificadas
   - Escalabilidad y mantenibilidad

---

**¡Buena suerte con la reunión! 🚀**

