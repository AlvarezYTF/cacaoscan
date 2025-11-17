# Mejoras del Pipeline Híbrido V2 - CacaoScan

## Resumen Ejecutivo

Este documento describe todas las mejoras implementadas en el pipeline de entrenamiento híbrido de CacaoScan para predecir `alto_mm`, `ancho_mm`, `grosor_mm`, y `peso_g` usando ConvNeXt + pixel features.

## Mejoras Implementadas (A-H)

### 🔥 A) Auto-weighted Loss (Dinámico) - Uncertainty-based

**Archivo:** `backend/ml/utils/losses.py`

**Implementación:**
- Loss multi-target con pesos automáticos aprendidos siguiendo "Uncertainty-based multi-task loss weighting (Kendall et al.)"
- Fórmula: `L_total = Σ [ (1 / (2 * σ_i²)) * L_i + log σ_i ]`
- Cada salida (alto, ancho, grosor, peso) tiene su propio `σ_i` aprendido
- Inicialización: `σ_i = 0.3`
- Base loss: SmoothL1Loss para cada target
- Evita que outliers (como grosor) dominen o exploten los gradientes

**Cambios:**
- Nueva clase `UncertaintyWeightedLoss` que extiende `nn.Module`
- Parámetros aprendibles `log_sigmas` para cada target
- Método `get_sigmas()` para obtener valores actuales de σ_i

### 🔥 B) Nuevos Pixel Features

**Archivo:** `backend/ml/data/cacao_dataset.py`

**Features agregados:**
1. `area_mm2` = grain_area_pixels * (average_mm_per_pixel²)
2. `perimeter_mm` = 2 × (width_pixels + height_pixels) × average_mm_per_pixel
3. `compactness` = (perimeter²) / (4π·area)
4. `roundness` = 4π·area / perimeter²

**Total:** 10 pixel features (anteriormente 8)

**Normalización:**
- Cambiado de `RobustScaler` a `StandardScaler` según especificaciones
- Normalización aplicada a todos los features

### 🔥 C) Log-transform Selectivo

**Archivo:** `backend/ml/utils/scalers.py`

**Implementación:**
- Log-transform aplicado SOLO a:
  - `grosor_mm` → `log(grosor_mm + 1)`
  - `peso_g` → `log(peso_g + 1)`
- `alto_mm` y `ancho_mm` NO reciben log-transform
- Desnormalización: `exp(pred) - 1` para grosor y peso

**Propósito:**
- Estabiliza la varianza
- Evita R² negativos extremos

### 🔥 D) EarlyStopping Inteligente

**Archivo:** `backend/ml/utils/early_stopping.py`

**Reglas implementadas:**
- Paciencia = 8 epochs
- Mejora mínima en Val Loss: 1% (0.01)
- Si algún R² < -2 por 2 épocas consecutivas → reduce LR a la mitad
- Si Val Loss sube 3 épocas seguidas → rollback al mejor checkpoint

**Características:**
- Monitoreo de R² por target
- Reducción automática de LR cuando detecta problemas
- Sistema de rollback para recuperar el mejor modelo

### 🔥 E) Nueva Fusión Híbrida Avanzada (Feature Gating Fusion)

**Archivo:** `backend/ml/regression/hybrid_model.py`

**Arquitectura:**
```
img_feat → Linear(768→512)
pix_feat → Linear(P→256)
gating = sigmoid(Linear(img_feat + pix_feat))
fusion = concat(
    img_feat * gating,
    pix_feat * (1 - gating)
)
→ MLP 512 → 256 → 128 → Salidas (4)
```

**Propósito:**
- Evitar que pixel features contaminen predicción de altura/ancho
- Evitar que imagen contamine grosor/peso
- Controlar la dominancia del feature-map

**Cambios:**
- Nueva clase `HybridRegressor` con feature gating
- Proyecciones separadas para imagen y pixel features
- Gating adaptativo basado en sigmoid
- Retorna tanto predicciones como valores de gating para logging

### 🔥 F) Optimización del Entrenamiento

**Archivo:** `backend/ml/regression/hybrid_trainer.py`

**Configuración:**
- Optimizer: `AdamW(lr=1e-4, weight_decay=0.01)`
- Scheduler: `CosineAnnealingWarmRestarts(T_0=10)`
- Batch size: 16 (configurable)
- Augmentations: RandomColorJitter(0.2), RandomAffine(±4°), ElasticTransform leve

**Checkpoints guardados:**
- `best_loss.pt` - Mejor modelo por val_loss
- `best_avg_r2.pt` - Mejor modelo por R² promedio
- `last_epoch.pt` - Última época entrenada

**Ubicación:** `ml/artifacts/regressors/checkpoints/`

### 🔥 G) Logs Mejorados

**Archivo:** `backend/ml/regression/hybrid_trainer.py`

**Métricas logueadas por época:**
- Train Loss
- Val Loss
- R² por variable (alto, ancho, grosor, peso)
- R² promedio
- σ_i actuales (incertidumbres aprendidas)
- Pearson correlation (real vs pred) por target
- Gradiente máximo del backward
- Porcentaje de gating entre imagen/pixel

**Ejemplo de log:**
```
Epoch 10/50 - Train Loss: 0.5234, Val Loss: 0.6123, Avg R²: 0.6543, LR: 1.00e-04
  Sigmas: {'alto': 0.28, 'ancho': 0.31, 'grosor': 0.35, 'peso': 0.42}
  Pearson: {'alto': 0.82, 'ancho': 0.89, 'grosor': 0.45, 'peso': 0.58}
  Max Gradient: 2.3456, Gating %: 45.23%
```

### 🔥 H) Reentrenamiento

**Comando:**
```bash
docker compose exec backend python manage.py train_cacao_models \
    --hybrid \
    --use-pixel-features \
    --epochs 50 \
    --batch-size 16 \
    --segmentation-backend opencv
```

**Resultados esperados:**
- Grosor R² positivo (+0.25 mínimo)
- Peso R² > 0.35
- Alto y Ancho R² entre 0.65–0.85
- Val Loss < 1.0 después de epoch 10–20

## Archivos Modificados

### Archivos Nuevos/Creados:
1. `backend/ml/utils/losses.py` - Uncertainty-weighted loss
2. `backend/ml/utils/early_stopping.py` - Early stopping inteligente
3. `backend/ml/utils/scalers.py` - Scaler con log-transform selectivo

### Archivos Modificados:
1. `backend/ml/data/cacao_dataset.py`
   - Agregados features: compactness, roundness
   - Cambio a StandardScaler
   - Total: 10 pixel features

2. `backend/ml/regression/hybrid_model.py`
   - Nueva arquitectura con feature gating
   - Proyecciones separadas (img→512, pix→256)
   - Gating adaptativo

3. `backend/ml/regression/hybrid_trainer.py`
   - Uncertainty-based loss
   - CosineAnnealingWarmRestarts scheduler
   - Logging mejorado
   - Múltiples checkpoints
   - Sistema de rollback

4. `backend/ml/regression/augmentation.py`
   - RandomColorJitter(0.2)
   - RandomAffine(±4°)
   - ElasticTransform leve

5. `backend/ml/pipeline/hybrid_v2_training.py`
   - Integración de todas las mejoras
   - Soporte para 10 pixel features

## Cómo Probar

### 1. Verificar Instalación
```bash
docker compose exec backend python -c "import torch; import timm; import scipy; print('OK')"
```

### 2. Entrenar Modelo
```bash
docker compose exec backend python manage.py train_cacao_models \
    --hybrid \
    --use-pixel-features \
    --epochs 50 \
    --batch-size 16 \
    --segmentation-backend opencv
```

### 3. Verificar Checkpoints
```bash
ls -lh backend/ml/artifacts/regressors/checkpoints/
# Debería mostrar: best_loss.pt, best_avg_r2.pt, last_epoch.pt
```

### 4. Verificar Logs
Los logs deberían mostrar:
- Sigmas por target
- Pearson correlations
- Gating percentage
- R² por variable

## Instrucciones de Migración

### Para Usuarios Existentes:

1. **Backup de modelos anteriores:**
   ```bash
   cp -r backend/ml/artifacts/regressors/checkpoints backend/ml/artifacts/regressors/checkpoints_backup
   ```

2. **Actualizar código:**
   - Los archivos han sido actualizados automáticamente
   - No se requiere migración manual

3. **Reentrenar:**
   - Ejecutar el comando de entrenamiento
   - El sistema detectará automáticamente las mejoras

### Compatibilidad:

- ✅ Compatible con comando existente
- ✅ No rompe rutas ni loaders actuales
- ✅ Mantiene compatibilidad con Docker
- ✅ Fallback a pipeline anterior si hay errores

## Explicación de Cambios

### ¿Por qué Uncertainty-based Loss?
- Permite al modelo aprender automáticamente la importancia relativa de cada target
- Evita que targets con mayor varianza (como grosor) dominen el entrenamiento
- Los parámetros σ_i se aprenden durante el entrenamiento

### ¿Por qué Feature Gating?
- Permite al modelo decidir dinámicamente cuánto peso dar a features de imagen vs pixel
- Evita contaminación cruzada entre targets
- Mejora la estabilidad del entrenamiento

### ¿Por qué Log-transform Selectivo?
- Grosor y peso tienen distribuciones más sesgadas
- Log-transform estabiliza la varianza
- Alto y ancho no necesitan transformación

### ¿Por qué CosineAnnealingWarmRestarts?
- Permite exploración periódica del espacio de parámetros
- Mejor convergencia que ReduceLROnPlateau para este caso
- T_0=10 proporciona ciclos de aprendizaje apropiados

## Troubleshooting

### Error: "pixel_dim mismatch"
- Verificar que el dataset tenga 10 features
- Revisar `cacao_dataset.py` línea 151-162

### Error: "σ_i explota"
- Reducir learning rate
- Verificar que initial_sigma=0.3

### R² negativo extremo
- Verificar log-transform en grosor/peso
- Revisar scalers guardados

### Gating siempre en 0 o 1
- Normal: el modelo aprende a usar uno u otro
- Si es problemático, ajustar arquitectura de gating

## Próximos Pasos

1. Monitorear resultados en producción
2. Ajustar hyperparámetros si es necesario
3. Considerar ensemble de modelos si R² no mejora
4. Evaluar necesidad de más datos para grosor/peso

## Contacto

Para preguntas o problemas, revisar logs en:
- `backend/ml/artifacts/logs/`
- Checkpoints en: `backend/ml/artifacts/regressors/checkpoints/`

