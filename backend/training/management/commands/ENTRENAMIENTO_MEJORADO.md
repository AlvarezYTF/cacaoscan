# 🚀 Diagrama de Flujo: Entrenamiento Mejorado con Calibración de Píxeles

## 🔄 Flujo Mejorado de Entrenamiento

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   ENTRENAMIENTO MEJORADO CON CALIBRACIÓN                    │
│          (Integra mediciones de píxeles → Modelos más precisos)           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌──────────────────────────────────────────────────┐
        │  1. PREPARACIÓN DE DATOS                         │
        │  ├─ Leer dataset_cacao.clean.csv                │
        │  ├─ Verificar imágenes .bmp en raw/              │
        │  └─ Cargar pixel_calibration.json (si existe)   │
        └──────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌──────────────────────────────────────────────────┐
        │  2. GENERAR/VERIFICAR CROPS SEGMENTADOS           │
        │  Para cada imagen sin crop:                      │
        │  ├─ Usar segment_and_crop_cacao_bean()          │
        │  ├─ Guardar PNG segmentado (sin fondo)           │
        │  └─ Si calibración existe, verificar calidad     │
        └──────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌──────────────────────────────────────────────────┐
        │  3. ENRIQUECER DATOS CON CALIBRACIÓN              │
        │  Si pixel_calibration.json existe:               │
        │  ├─ Para cada registro, buscar en calibración     │
        │  ├─ Obtener medidas de píxeles                    │
        │  ├─ Calcular factores de escala                  │
        │  └─ Añadir features adicionales:                │
        │     * pixel_width, pixel_height                   │
        │     * pixel_area                                 │
        │     * scale_factor                               │
        │     * aspect_ratio                                │
        └──────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌──────────────────────────────────────────────────┐
        │  4. PREPARAR DATASET ENRIQUECIDO                 │
        │  Crear dataset con:                              │
        │  ├─ Imágenes: PNG segmentadas (sin fondo)        │
        │  ├─ Targets: Valores reales del CSV               │
        │  ├─ Features adicionales: Medidas de píxeles       │
        │  └─ Metadata: Factores de escala                 │
        └──────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌──────────────────────────────────────────────────┐
        │  5. SPLIT DE DATOS                               │
        │  Train/Val/Test (70/15/15)                      │
        │  ├─ Estratificado por tamaño de grano           │
        │  ├─ Mantener balance de escala de píxeles       │
        │  └─ Validar que calibración esté distribuida     │
        └──────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌──────────────────────────────────────────────────┐
        │  6. CREAR MODELO HÍBRIDO                         │
        │  Arquitectura mejorada:                         │
        │  ├─ Backbone CNN (ResNet18/ConvNeXt)            │
        │  ├─ Branch 1: Predicción visual (RGB)           │
        │  ├─ Branch 2: Features de píxeles (opcional)    │
        │  └─ Fusion: Combinar ambas ramas                │
        └──────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌──────────────────────────────────────────────────┐
        │  7. ENTRENAMIENTO CON LOSS MEJORADO              │
        │  Loss function híbrida:                         │
        │  ├─ MSE(predicción, target_real)                │
        │  ├─ + λ * MSE(pred_pixel, target_pixel_calibrado)│
        │  └─ Validación con calibración                   │
        └──────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌──────────────────────────────────────────────────┐
        │  8. VALIDACIÓN MEJORADA                          │
        │  En cada época:                                 │
        │  ├─ Validar contra targets reales                │
        │  ├─ Validar contra predicción de píxeles         │
        │  ├─ Verificar rangos razonables (calibración)    │
        │  └─ Early stopping si ambos mejoran              │
        └──────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌──────────────────────────────────────────────────┐
        │  9. EVALUACIÓN FINAL                             │
        │  Métricas:                                       │
        │  ├─ MAE, RMSE vs targets reales                  │
        │  ├─ MAE vs predicción basada en píxeles          │
        │  ├─ R² score                                     │
        │  └─ Error promedio vs calibración                │
        └──────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌──────────────────────────────────────────────────┐
        │  10. GUARDAR MODELOS Y METADATOS                 │
        │  Guardar:                                        │
        │  ├─ Modelos entrenados (.pth)                    │
        │  ├─ Escaladores (scalers.pkl)                    │
        │  ├─ Estadísticas de entrenamiento                │
        │  └─ Referencia a calibración usada                │
        └──────────────────────────────────────────────────┘
```

## 🎯 Mejoras Principales

### 1. **Integración de Calibración de Píxeles**
```
Flujo Actual:
CSV → Cargar imágenes → Entrenar → Predicción

Flujo Mejorado:
CSV + Calibración → Enriquecer datos → Entrenar con features adicionales → Predicción mejorada
```

### 2. **Features Adicionales en el Dataset**
```python
# Dataset enriquecido incluye:
{
    'image': tensor_imagen,           # Imagen RGB segmentada
    'pixel_width': int,                # Ancho en píxeles
    'pixel_height': int,               # Alto en píxeles
    'pixel_area': int,                 # Área en píxeles
    'scale_factor': float,             # Factor de escala mm/píxel
    'aspect_ratio': float,             # Relación aspecto
    'target_alto': float,              # Target real (CSV)
    'target_ancho': float,
    'target_grosor': float,
    'target_peso': float
}
```

### 3. **Modelo Híbrido**
```
┌─────────────────┐
│  Imagen RGB     │ ──┐
│  (224x224)      │   │
└─────────────────┘   │
                       ▼
┌─────────────────┐   │    ┌──────────────────┐
│  Features       │   │    │  CNN Backbone     │
│  Píxeles        │ ──┼───▶│  (ResNet18)       │
│  [5 features]   │   │    └──────────────────┘
└─────────────────┘   │             │
                       │             ▼
                       │    ┌──────────────────┐
                       └───▶│  Fusion Layer    │
                            │  (concatenate)   │
                            └──────────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │  Regression Head │
                            │  (alto, ancho,   │
                            │   grosor, peso)  │
                            └──────────────────┘
```

### 4. **Loss Function Mejorada**
```python
def hybrid_loss(prediction, target, pixel_prediction, pixel_target, lambda_pixel=0.3):
    """
    Combina pérdida estándar con validación contra predicción de píxeles.
    """
    # Loss estándar (predicción vs target real)
    standard_loss = mse_loss(prediction, target)
    
    # Loss contra predicción de píxeles (si está disponible)
    if pixel_prediction is not None and pixel_target is not None:
        pixel_loss = mse_loss(pixel_prediction, pixel_target)
        return standard_loss + lambda_pixel * pixel_loss
    
    return standard_loss
```

### 5. **Augmentación Inteligente**
```
Augmentación Tradicional:
- Rotación, flip, zoom aleatorio
- Puede distorsionar proporciones

Augmentación Mejorada:
- Mantener aspect_ratio real
- Ajustar scale_factor proporcionalmente
- Validar que medidas de píxeles sean consistentes
```

### 6. **Validación con Calibración**
```python
def validate_with_calibration(prediction, pixel_measurements, calibration_data):
    """
    Valida que las predicciones estén en rangos razonables usando calibración.
    """
    # Buscar registro similar en calibración
    similar_record = find_similar_in_calibration(pixel_measurements, calibration_data)
    
    # Obtener factor de escala esperado
    expected_scale = similar_record['scale_factors']['average_mm_per_pixel']
    
    # Calcular predicción basada en píxeles
    pixel_based_pred = calculate_from_pixels(pixel_measurements, expected_scale)
    
    # Comparar predicciones
    error = abs(prediction - pixel_based_pred)
    threshold = 0.2 * pixel_based_pred  # 20% tolerancia
    
    return error < threshold
```

## 📊 Comparación: Flujo Actual vs Mejorado

### Flujo Actual:
```
CSV → Cargar crops → Entrenar → Guardar modelos
```
- ✅ Funciona bien
- [ERROR] No usa información de píxeles
- [ERROR] No valida con calibración
- [ERROR] Puede entrenar con crops de mala calidad

### Flujo Mejorado:
```
CSV + Calibración → Generar crops → Enriquecer datos → 
Entrenar modelo híbrido → Validar con calibración → Guardar modelos mejorados
```
- ✅ Usa información de píxeles
- ✅ Valida con calibración durante entrenamiento
- ✅ Modelo más robusto y preciso
- ✅ Features adicionales mejoran generalización
- ✅ Validación doble (modelo + píxeles)

## 🔧 Implementación Propuesta

### Paso 1: Modificar Dataset Loader
```python
class EnrichedCacaoDataset(CacaoDataset):
    """Dataset enriquecido con información de calibración."""
    
    def __init__(self, image_paths, targets, calibration_data=None, ...):
        super().__init__(image_paths, targets, ...)
        self.calibration_data = calibration_data
        
    def __getitem__(self, idx):
        image, target = super().__getitem__(idx)
        
        # Obtener features de píxeles si calibración existe
        if self.calibration_data:
            image_id = self.get_image_id(idx)
            pixel_features = self.get_pixel_features(image_id)
            return image, target, pixel_features
        
        return image, target
```

### Paso 2: Modelo Híbrido
```python
class HybridCacaoRegressor(nn.Module):
    """Modelo híbrido que combina imagen y features de píxeles."""
    
    def __init__(self, backbone='resnet18', num_pixel_features=5):
        super().__init__()
        # Backbone CNN
        self.backbone = create_backbone(backbone)
        
        # Branch para features de píxeles
        self.pixel_branch = nn.Sequential(
            nn.Linear(num_pixel_features, 64),
            nn.ReLU(),
            nn.Linear(64, 128)
        )
        
        # Fusion
        self.fusion = nn.Linear(backbone_dim + 128, 512)
        
        # Regression head
        self.regressor = nn.Linear(512, 4)  # alto, ancho, grosor, peso
```

### Paso 3: Loss Function Híbrida
```python
def hybrid_regression_loss(pred, target, pixel_pred=None, pixel_target=None, lambda_pixel=0.3):
    """Loss que combina predicción estándar con validación de píxeles."""
    main_loss = nn.MSELoss()(pred, target)
    
    if pixel_pred is not None and pixel_target is not None:
        pixel_loss = nn.MSELoss()(pixel_pred, pixel_target)
        return main_loss + lambda_pixel * pixel_loss
    
    return main_loss
```

## 📈 Beneficios Esperados

1. **Mayor Precisión**: Modelo aprende de ambas fuentes (imagen + píxeles)
2. **Mejor Generalización**: Features de píxeles ayudan con casos edge
3. **Validación Robustez**: Validación doble reduce errores
4. **Consistencia**: Predicciones más consistentes con mediciones reales
5. **Debugging Mejorado**: Puede identificar qué fuente falla (imagen vs píxeles)

## 🚀 Plan de Implementación

1. **Fase 1**: Modificar dataset loader para incluir features de píxeles
2. **Fase 2**: Crear modelo híbrido (backward compatible)
3. **Fase 3**: Implementar loss function híbrida
4. **Fase 4**: Validación con calibración durante entrenamiento
5. **Fase 5**: Evaluación comparativa (actual vs mejorado)

