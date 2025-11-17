# Mejoras del DataLoader de CacaoScan

## Resumen de Cambios

Se han implementado mejoras significativas en el DataLoader para asegurar la correcta carga y normalización de imágenes y targets.

## Características Implementadas

### 1. Validación de Formato de Imágenes

✅ **RGB garantizado**: Todas las imágenes se convierten explícitamente a RGB antes de procesar
✅ **Normalización ImageNet**: Validación automática de que las transformaciones incluyan normalización ImageNet estándar
✅ **Validación de canales**: Verificación de que las imágenes tengan exactamente 3 canales RGB

**Código:**
```python
# Convertir a RGB (asegura 3 canales)
if image.mode != 'RGB':
    image = image.convert('RGB')

# Validar formato del tensor
if image_tensor.shape[0] != 3:
    raise ValueError(f"Imagen debe tener 3 canales RGB")
```

### 2. Verificación de Mezclas entre .bmp y .png

✅ **Detección automática**: El DataLoader detecta y reporta mezclas entre formatos
✅ **Advertencias**: Alerta cuando se encuentran ambos formatos en el mismo dataset
✅ **Recomendación**: Sugiere usar solo .png (crops) para entrenamiento

**Código:**
```python
def _validate_image_paths(self) -> None:
    """Valida que las rutas de imágenes sean consistentes."""
    bmp_count = sum(1 for p in self.image_paths if p.suffix.lower() == '.bmp')
    png_count = sum(1 for p in self.image_paths if p.suffix.lower() == '.png')
    
    if bmp_count > 0 and png_count > 0:
        logger.warning(
            f"Mezcla de formatos detectada: {bmp_count} .bmp y {png_count} .png. "
            f"Se recomienda usar solo .png (crops) para entrenamiento."
        )
```

### 3. Labels en Orden Correcto

✅ **Orden garantizado**: Los targets siempre se devuelven en el orden `[alto, ancho, grosor, peso]`
✅ **Reordenamiento automático**: Si los targets no están en el orden correcto, se reordenan automáticamente
✅ **Constante de orden**: `TARGET_ORDER = ["alto", "ancho", "grosor", "peso"]`

**Código:**
```python
# Orden correcto de targets
TARGET_ORDER = ["alto", "ancho", "grosor", "peso"]

# Reordenar targets si es necesario
if target_keys != self.TARGET_ORDER:
    logger.warning("Reordenando targets...")
    self.targets = {k: self.targets[k] for k in self.TARGET_ORDER}

# Devolver en orden correcto
targets_tensor = torch.tensor([
    float(self.targets["alto"][idx]),
    float(self.targets["ancho"][idx]),
    float(self.targets["grosor"][idx]),
    float(self.targets["peso"][idx]),
], dtype=torch.float32)
```

### 4. Normalización de Targets Integrada

✅ **Clase TargetNormalizer**: Nueva clase para normalizar y desnormalizar targets
✅ **Soporte para StandardScaler y MinMaxScaler**: Dos tipos de normalización disponibles
✅ **Funciones de conveniencia**: `normalize_targets()` y `denormalize_predictions()`

**Uso:**
```python
from ml.data.improved_dataloader import normalize_targets, denormalize_predictions, TargetNormalizer

# Normalizar targets
normalized_targets, normalizer = normalize_targets(
    targets=targets_dict,
    scaler_type="standard"  # o "minmax"
)

# Desnormalizar predicciones
denormalized_predictions = denormalize_predictions(
    predictions=normalized_predictions,
    normalizer=normalizer
)
```

### 5. Funciones para Revertir Normalización

✅ **denormalize_predictions()**: Función para desnormalizar predicciones del modelo
✅ **normalize_single() / denormalize_single()**: Para valores individuales
✅ **Integración con escaladores**: Compatible con el sistema de escaladores existente

**Ejemplo:**
```python
# Durante evaluación
normalizer = TargetNormalizer(scaler_type="standard")
normalizer.fit(train_targets)

# Desnormalizar para calcular R² reales
denorm_pred = normalizer.denormalize(predictions)
denorm_targets = normalizer.denormalize(targets)

# Calcular R² sobre valores reales
r2 = r2_score(denorm_targets, denorm_pred)
```

### 6. Validación de Estructura de Datos

✅ **Validación automática**: Verifica que la estructura coincida con `pixel_calibration.json`
✅ **Validación de longitudes**: Asegura que imágenes, targets y pixel_features tengan la misma longitud
✅ **Validación de targets**: Verifica que todos los targets estén presentes

**Código:**
```python
def _validate_structure(self) -> None:
    """Valida la estructura de datos."""
    # Validar que todos los targets estén presentes
    missing_targets = set(self.TARGET_ORDER) - set(self.targets.keys())
    if missing_targets:
        raise ValueError(f"Targets faltantes: {missing_targets}")
    
    # Validar longitudes
    n_images = len(self.image_paths)
    n_targets = {k: len(v) for k, v in self.targets.items()}
    if not all(n == n_images for n in n_targets.values()):
        raise ValueError(f"Longitudes inconsistentes")
```

## Archivos Modificados

1. **`backend/ml/pipeline/train_all.py`**:
   - Mejorado `CacaoDataset` con validaciones
   - Agregada validación de formato de imágenes
   - Agregada validación de orden de targets
   - Mejorado manejo de errores en carga de imágenes

2. **`backend/ml/data/improved_dataloader.py`** (NUEVO):
   - Clase `TargetNormalizer` para normalización de targets
   - Clase `ImprovedCacaoDataset` con validaciones completas
   - Funciones `normalize_targets()` y `denormalize_predictions()`
   - Función `create_improved_dataloader()` para crear DataLoaders validados

## Uso del DataLoader Mejorado

### Opción 1: Usar el DataLoader mejorado directamente

```python
from ml.data.improved_dataloader import (
    create_improved_dataloader,
    normalize_targets,
    denormalize_predictions
)

# Normalizar targets
normalized_targets, normalizer = normalize_targets(
    targets=targets_dict,
    scaler_type="standard"
)

# Crear DataLoader
train_loader, _ = create_improved_dataloader(
    image_paths=train_images,
    targets=normalized_targets,
    transform=train_transform,
    pixel_features=train_pixel_features,
    batch_size=32,
    shuffle=True,
    validate_structure=True,
    use_crops=True  # Usar .png en lugar de .bmp
)
```

### Opción 2: Usar el DataLoader existente (mejorado)

El `CacaoDataset` existente ahora incluye todas las validaciones automáticamente:

```python
from ml.pipeline.train_all import CacaoDataset

dataset = CacaoDataset(
    image_paths=image_paths,
    targets=targets,
    transform=transform,
    pixel_features=pixel_features,
    validate_structure=True  # Validación automática activada
)
```

## Validación con pixel_calibration.json

El DataLoader mejorado puede validar que los datos coincidan con `pixel_calibration.json`:

```python
dataset = ImprovedCacaoDataset(...)

# Cargar calibración
calibration_data = load_json("pixel_calibration.json")

# Validar
validation_results = dataset.validate_with_calibration(calibration_data)
print(f"Match rate: {validation_results['match_rate']:.2%}")
```

## Estructura Esperada por Imagen

El DataLoader valida que la estructura coincida con:

```json
{
  "id": 510,
  "filename": "510.bmp",
  "original_image_path": ".../raw/510.bmp",
  "processed_image_path": ".../crops/510.png",
  "real_dimensions": {
    "alto_mm": 22.8,
    "ancho_mm": 16.3,
    "grosor_mm": 10.2,
    "peso_g": 1.72
  }
}
```

## Beneficios

1. **Detección temprana de errores**: Los problemas se detectan antes del entrenamiento
2. **R² correctos**: Las métricas se calculan sobre valores desnormalizados
3. **Consistencia garantizada**: Orden de targets y formato de imágenes siempre correctos
4. **Debugging facilitado**: Logs detallados sobre problemas encontrados
5. **Compatibilidad**: Funciona con el código existente sin cambios mayores

## Próximos Pasos

1. Ejecutar el entrenamiento y verificar que las validaciones funcionen correctamente
2. Revisar los logs para confirmar que no hay mezclas de formatos
3. Verificar que los R² se calculen correctamente sobre valores desnormalizados
4. Considerar usar `ImprovedCacaoDataset` para nuevos entrenamientos

