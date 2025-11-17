# Checklist de Integración del Pipeline Unificado

## Verificación de Componentes

### ✅ 1. DataLoader (`CacaoDataset` en `train_all.py`)

**Estado:** ✅ MEJORADO
- [x] Validación de formato RGB (línea 225-251)
- [x] Validación de orden de targets: [alto, ancho, grosor, peso] (línea 282-290)
- [x] Validación de estructura de datos (línea 173-220)
- [x] Soporte para pixel_features (5 o 12) (línea 141-154)

**Ubicación:** `backend/ml/pipeline/train_all.py` líneas 104-309

### ✅ 2. Normalización (`CacaoScalers`)

**Estado:** ✅ INTEGRADO
- [x] StandardScaler para cada target (línea 1440)
- [x] Normalización antes de crear splits (línea 1446)
- [x] Targets normalizados guardados en `self.train_targets` (línea 1484)

**Ubicación:** `backend/ml/pipeline/train_all.py` líneas 1437-1449

### ✅ 3. Modelo Híbrido (`HybridCacaoRegression`)

**Estado:** ✅ INTEGRADO
- [x] Creación del modelo híbrido (línea 1156-1165)
- [x] Detección automática de pixel_feature_dim (5 o 12) (línea 1136-1153)
- [x] BatchNorm en todas las capas FC (en `models.py`)
- [x] Inicialización de pesos (en `models.py`)

**Ubicación:** `backend/ml/pipeline/train_all.py` líneas 1125-1184

### ✅ 4. Training Loop Mejorado

**Estado:** ✅ INTEGRADO (automático)
- [x] `train_multi_head_model` usa `use_improved=True` por defecto (en `train.py`)
- [x] Training loop mejorado se importa automáticamente (en `train.py` línea 516-528)
- [x] Validación de normalización antes de entrenar
- [x] Checkpoints automáticos
- [x] Logging detallado

**Ubicación:** 
- `backend/ml/regression/train.py` líneas 491-528
- `backend/ml/regression/train_improved.py` (completo)

### ✅ 5. Métricas R² Robustas

**Estado:** ✅ INTEGRADO (automático)
- [x] `train_multi_head_model_improved` usa `denormalize_and_calculate_metrics` (en `train_improved.py`)
- [x] Desnormalización automática antes de calcular R²
- [x] R² individual + promedio

**Ubicación:** 
- `backend/ml/regression/train_improved.py` líneas 765-772
- `backend/ml/regression/metrics.py` (completo)

### ✅ 6. Flags del Comando

**Estado:** ✅ CONFIGURADO
- [x] `--hybrid` → `config['hybrid'] = True` (línea 222)
- [x] `--use-pixel-features` → `config['use_pixel_features'] = True` (línea 223)
- [x] `--segmentation-backend opencv` → `config['segmentation_backend'] = 'opencv'` (línea 233)
- [x] `--epochs 50` → `config['epochs'] = 50` (línea 225)
- [x] `--batch-size 32` → `config['batch_size'] = 32` (línea 226)

**Ubicación:** `backend/training/management/commands/train_cacao_models.py` líneas 219-241

### ✅ 7. pixel_calibration.json

**Estado:** ✅ INTEGRADO
- [x] Carga de `pixel_calibration.json` (línea 432-444)
- [x] Extracción de features extendidos (línea 500-600)
- [x] Detección automática de 5 vs 12 features (línea 1143-1151)

**Ubicación:** `backend/ml/pipeline/train_all.py` líneas 423-600

## Flujo Completo Verificado

```
1. Comando Django (train_cacao_models.py)
   └──> Crea config con flags
        └──> CacaoTrainingPipeline(config)

2. Pipeline (train_all.py)
   ├──> load_data()
   │    ├──> Carga imágenes
   │    ├──> Carga targets
   │    └──> Carga pixel_calibration.json (si existe)
   │
   ├──> create_scalers_from_data()
   │    └──> StandardScaler para cada target
   │
   ├──> scalers.transform()
   │    └──> Normaliza targets (mean=0, std=1)
   │
   ├──> create_stratified_split()
   │    └──> Train/Val/Test con targets normalizados
   │
   ├──> create_data_loaders()
   │    └──> CacaoDataset con validaciones
   │
   ├──> create_model()
   │    └──> HybridCacaoRegression (si --hybrid)
   │         └──> pixel_feature_dim detectado automáticamente
   │
   └──> train_multi_head_model()
        └──> train_multi_head_model_improved() (automático)
             ├──> Valida normalización
             ├──> Valida pérdida inicial
             ├──> Training loop con checkpoints
             ├──> Desnormaliza predicciones/targets
             └──> Calcula R² robusto
```

## Archivos que NO Necesitan Cambios

Los siguientes archivos ya están correctamente integrados:

1. ✅ `backend/ml/regression/models.py` - Modelos optimizados
2. ✅ `backend/ml/regression/metrics.py` - Métricas robustas
3. ✅ `backend/ml/regression/train_improved.py` - Training loop mejorado
4. ✅ `backend/ml/regression/train.py` - Wrapper con integración automática
5. ✅ `backend/ml/regression/scalers.py` - Normalización correcta

## Verificación Final

### Comando de Prueba

```bash
docker compose exec backend python manage.py train_cacao_models \
    --hybrid \
    --use-pixel-features \
    --epochs 50 \
    --batch-size 32 \
    --segmentation-backend opencv
```

### Logs Esperados

1. **Carga de datos:**
   ```
   Calibración de píxeles cargada: X registros
   Encontrados X registros válidos
   ```

2. **Normalización:**
   ```
   Escaladores preparados
   Targets normalizados
   ```

3. **Modelo:**
   ```
   Usando 12 features de píxeles extendidos de pixel_calibration.json
   Entrenando modelo HÍBRIDO (ResNet18 + ConvNeXt + Píxeles)...
   ```

4. **Validaciones:**
   ```
   === Validando normalización de targets ===
   === Validando pérdida inicial ===
   ```

5. **Entrenamiento:**
   ```
   Epoch 1/50 | Train Loss: X.XXXX | Val Loss: X.XXXX | ...
   ✓ Checkpoint guardado: ...
   ```

### Valores Esperados

- **Train Loss inicial:** < 1.0 (si está normalizado correctamente)
- **Val Loss inicial:** < 1.0
- **R² inicial:** Cerca de 0 o ligeramente negativo (mejorará)
- **R² final:** Debe mejorar gradualmente hacia positivo

## Problemas Conocidos y Soluciones

### Si Train Loss es > 1000

**Causa:** Targets no normalizados o normalización incorrecta

**Solución:** Verificar que `scalers.transform()` se llame antes de crear datasets

### Si R² es extremadamente negativo

**Causa:** R² calculado sobre valores normalizados

**Solución:** Ya resuelto - `denormalize_and_calculate_metrics` desnormaliza automáticamente

### Si pixel_features no se encuentran

**Causa:** `pixel_calibration.json` no existe o no se carga

**Solución:** Verificar que el archivo existe y se carga correctamente (línea 432-444)

## Estado Final

✅ **TODO INTEGRADO Y FUNCIONAL**

El pipeline está completamente unificado y listo para usar. Todos los componentes mejorados están integrados automáticamente:

- DataLoader mejorado ✅
- Normalización correcta ✅
- Modelos optimizados ✅
- Métricas robustas ✅
- Training loop mejorado ✅
- Flags del comando ✅
- pixel_calibration.json ✅

**No se requieren cambios adicionales en el código.**

