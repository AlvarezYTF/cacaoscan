# Pipeline Unificado de Entrenamiento - CacaoScan

## Resumen

Este documento describe el pipeline unificado que integra todas las mejoras realizadas:

1. ✅ DataLoader mejorado con validaciones
2. ✅ Modelos optimizados (BatchNorm, inicialización)
3. ✅ Métricas robustas (R² con desnormalización)
4. ✅ Training loop mejorado (checkpoints, early stopping, logging)
5. ✅ Normalización correcta de imágenes y targets
6. ✅ Integración de pixel_features y pixel_calibration.json
7. ✅ Soporte para segmentation-backend=opencv

## Comando de Uso

```bash
docker compose exec backend python manage.py train_cacao_models \
    --hybrid \
    --use-pixel-features \
    --epochs 50 \
    --batch-size 32 \
    --segmentation-backend opencv
```

## Flujo del Pipeline Unificado

```
1. Cargar Datos
   ├── Cargar imágenes (crops)
   ├── Cargar targets (alto, ancho, grosor, peso)
   ├── Cargar pixel_calibration.json (si existe)
   └── Extraer pixel_features (5 básicos o 12 extendidos)

2. Normalizar Targets
   ├── Crear StandardScaler para cada target
   ├── Normalizar targets (mean=0, std=1)
   └── Validar normalización

3. Crear Splits
   ├── Train/Val/Test split
   ├── Mantener pixel_features en splits
   └── Validar consistencia

4. Crear DataLoaders
   ├── CacaoDataset con validaciones
   ├── Transformaciones ImageNet
   ├── Validar formato RGB
   └── Validar orden de targets

5. Crear Modelo
   ├── HybridCacaoRegression (si --hybrid)
   ├── ResNet18 + Pixel Features
   ├── BatchNorm en todas las capas FC
   └── Inicialización de pesos

6. Entrenar
   ├── Validar pérdida inicial
   ├── Training loop mejorado
   ├── Checkpoints automáticos
   ├── Early stopping
   └── Logging detallado

7. Evaluar
   ├── Desnormalizar predicciones
   ├── Desnormalizar targets
   ├── Calcular R² robusto
   └── Guardar métricas
```

## Componentes Integrados

### 1. DataLoader (`CacaoDataset`)

**Ubicación:** `backend/ml/pipeline/train_all.py`

**Mejoras:**
- ✅ Validación de formato RGB
- ✅ Validación de normalización ImageNet
- ✅ Validación de orden de targets: [alto, ancho, grosor, peso]
- ✅ Validación de mezclas .bmp/.png
- ✅ Soporte para pixel_features (5 o 12)

### 2. Modelos (`HybridCacaoRegression`)

**Ubicación:** `backend/ml/regression/models.py`

**Mejoras:**
- ✅ BatchNorm en todas las capas FC
- ✅ Inicialización Xavier Uniform
- ✅ Salida correcta: dict con 4 valores
- ✅ Soporte dinámico para 5 o 12 pixel_features

### 3. Métricas (`robust_r2_score`)

**Ubicación:** `backend/ml/regression/metrics.py`

**Mejoras:**
- ✅ Desnormalización automática antes de calcular R²
- ✅ Validación de dimensiones
- ✅ Filtrado de NaN/Inf
- ✅ R² individual + promedio

### 4. Training Loop (`train_multi_head_model_improved`)

**Ubicación:** `backend/ml/regression/train_improved.py`

**Mejoras:**
- ✅ Validación de normalización antes de entrenar
- ✅ Validación de pérdida inicial
- ✅ Checkpoints automáticos
- ✅ Logging detallado (loss por batch, tiempo, R²)
- ✅ Early stopping robusto

### 5. Normalización (`CacaoScalers`)

**Ubicación:** `backend/ml/regression/scalers.py`

**Mejoras:**
- ✅ StandardScaler para cada target
- ✅ Validación de normalización
- ✅ Desnormalización correcta

## Configuración Unificada

```python
config = {
    # Modelo
    'hybrid': True,
    'use_pixel_features': True,
    'model_type': 'hybrid',
    
    # Entrenamiento
    'epochs': 50,
    'batch_size': 32,
    'learning_rate': 1e-4,  # Validado automáticamente (max 1e-3)
    'loss_type': 'smooth_l1',  # Más robusta que MSE
    'scheduler_type': 'reduce_on_plateau',  # Adaptativo
    
    # Normalización
    'scaler_type': 'standard',  # StandardScaler
    
    # DataLoader
    'img_size': 224,
    'num_workers': 0,  # Para evitar problemas de shared memory
    
    # Early Stopping
    'early_stopping_patience': 10,
    'improvement_threshold': 1e-4,
    
    # Otros
    'dropout_rate': 0.3,
    'weight_decay': 1e-4,
    'max_grad_norm': 1.0,
    'min_lr': 1e-7,
    'segmentation_backend': 'opencv'
}
```

## Validaciones Implementadas

### Antes de Entrenar

1. **Normalización de Targets**
   - ✅ Mean ~0, std ~1
   - ✅ No NaN/Inf
   - ✅ Todos los targets presentes

2. **Pérdida Inicial**
   - ✅ < 1000 (si > 1000, error crítico)
   - ✅ < 100 (si > 100, advertencia)

3. **Modelo**
   - ✅ Inicializado correctamente
   - ✅ En modo train

### Durante Entrenamiento

1. **Pérdidas**
   - ✅ Valida que sean finitas
   - ✅ Omite batches problemáticos

2. **Gradientes**
   - ✅ Gradient clipping (max_norm=1.0)

3. **Learning Rate**
   - ✅ Validado automáticamente
   - ✅ Ajustado por scheduler

### Después de Entrenar

1. **Métricas**
   - ✅ Desnormalización automática
   - ✅ Validación de alineación
   - ✅ R² robusto

## Logs Esperados

### Inicio
```
=== Validando normalización de targets ===
alto: mean=0.0001, std=1.0002, range=[-2.3456, 2.5678]
ancho: mean=-0.0002, std=0.9998, range=[-2.1234, 2.3456]
grosor: mean=0.0000, std=1.0001, range=[-2.2345, 2.4567]
peso: mean=0.0001, std=0.9999, range=[-2.3456, 2.5678]
==========================================

=== Validando pérdida inicial ===
Pérdida inicial (promedio de 5 batches): 0.1234
=================================

=== Iniciando entrenamiento (50 épocas) ===
```

### Durante Entrenamiento
```
Epoch 1/50 | Train Loss: 0.1234 | Val Loss: 0.2345 | LR: 1.00e-04 | Time: 12.34s | alto R²: 0.1234 | ancho R²: 0.2345 | grosor R²: 0.3456 | peso R²: 0.4567 | Avg R²: 0.2901
✓ Checkpoint guardado: checkpoints/best_model_epoch_1.pt (Val Loss: 0.2345)
```

### Final
```
Early stopping en época 25 (mejor época: 20, Val Loss: 0.1234)
Mejor modelo cargado (Época 20, Val Loss: 0.1234)
=== Entrenamiento completado en 234.56s ===
```

## Archivos del Pipeline Unificado

1. **`backend/ml/pipeline/train_all.py`**
   - Pipeline principal
   - Carga de datos
   - Normalización
   - Creación de DataLoaders
   - Integración con training loop

2. **`backend/ml/regression/models.py`**
   - Modelos optimizados
   - HybridCacaoRegression

3. **`backend/ml/regression/metrics.py`**
   - Métricas robustas
   - R² con desnormalización

4. **`backend/ml/regression/train_improved.py`**
   - Training loop mejorado
   - Validaciones
   - Checkpoints

5. **`backend/ml/regression/train.py`**
   - Wrapper que usa training loop mejorado

6. **`backend/training/management/commands/train_cacao_models.py`**
   - Comando Django
   - Parsing de flags
   - Configuración

## Checklist de Verificación

Antes de ejecutar, verificar:

- [x] Targets están normalizados (validación automática)
- [x] Imágenes en formato RGB
- [x] pixel_calibration.json cargado (si --use-pixel-features)
- [x] Modelo híbrido creado correctamente
- [x] Pérdida inicial razonable (<100)
- [x] Learning rate validado (1e-6 a 1e-3)
- [x] Checkpoints se guardan automáticamente
- [x] R² se calcula sobre valores desnormalizados
- [x] Logs muestran información detallada

## Troubleshooting

### Pérdida Inicial Muy Alta

**Síntoma:** `PÉRDIDA INICIAL EXTREMADAMENTE ALTA: 1580141`

**Soluciones:**
1. Verificar que targets estén normalizados
2. Reducir learning rate a 1e-5
3. Verificar inicialización del modelo

### R² Extremadamente Negativo

**Síntoma:** `alto R²: -1306`

**Soluciones:**
1. Verificar que se desnormalice antes de calcular R² (ya implementado)
2. Verificar alineación de predicciones y targets
3. Verificar que el modelo esté aprendiendo (loss debe disminuir)

### pixel_features No Encontrados

**Síntoma:** `Faltan las siguientes features de píxeles: [...]`

**Soluciones:**
1. Verificar que pixel_calibration.json existe
2. Verificar que --use-pixel-features está activado
3. Verificar que --hybrid está activado

## Resultado Esperado

Con el pipeline unificado, deberías obtener:

- ✅ Train Loss: Debe disminuir gradualmente (empezar < 1.0)
- ✅ Val Loss: Debe disminuir gradualmente
- ✅ R²: Debe mejorar gradualmente (empezar cerca de 0, mejorar hacia positivo)
- ✅ Checkpoints: Guardados automáticamente
- ✅ Logs: Detallados y informativos

