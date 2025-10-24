# CacaoScan - Módulo de Regresión

Este módulo implementa modelos de regresión para predecir dimensiones y peso de granos de cacao a partir de imágenes recortadas.

## Estructura del Proyecto

```
backend/ml/regression/
├── models.py          # Arquitecturas CNN (ResNet18, ConvNeXt)
├── train.py           # Scripts de entrenamiento
├── evaluate.py        # Evaluación y métricas
└── scalers.py         # Manejo de escaladores

backend/ml/pipeline/
└── train_all.py       # Pipeline completo de entrenamiento

backend/ml/artifacts/regressors/
├── alto.pt            # Modelo para altura
├── ancho.pt           # Modelo para ancho
├── grosor.pt          # Modelo para grosor
├── peso.pt            # Modelo para peso
├── multihead.pt       # Modelo multi-head (opcional)
├── alto_scaler.pkl    # Escalador para altura
├── ancho_scaler.pkl   # Escalador para ancho
├── grosor_scaler.pkl  # Escalador para grosor
└── peso_scaler.pkl    # Escalador para peso
```

## Características

### Modelos Disponibles

1. **ResNet18**: Arquitectura ligera y eficiente
   - Modelos individuales por target
   - Modelo multi-head con 4 salidas
   - Transfer learning con pesos pre-entrenados

2. **ConvNeXt Tiny**: Arquitectura moderna (requiere timm)
   - Mejor rendimiento que ResNet18
   - Mayor capacidad de generalización

### Escaladores

- **StandardScaler**: Normalización estándar (media=0, std=1)
- **MinMaxScaler**: Normalización a rango [0,1]
- **RobustScaler**: Normalización robusta a outliers

### Métricas de Evaluación

- **MAE**: Error Absoluto Medio
- **RMSE**: Raíz del Error Cuadrático Medio
- **R²**: Coeficiente de Determinación
- **MAPE**: Error Absoluto Porcentual Medio

## Instalación

### 1. Instalar dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 2. Dependencias específicas

Para ConvNeXt (opcional):
```bash
pip install timm
```

## Uso

### Entrenar Modelos

#### Comando Django (Recomendado)

```bash
# Entrenamiento básico
python manage.py train_cacao_models

# Entrenamiento con parámetros personalizados
python manage.py train_cacao_models --epochs 100 --batch-size 16 --multihead

# Solo validar datos
python manage.py train_cacao_models --validate-only

# Modo de prueba (configuración reducida)
python manage.py train_cacao_models --test-mode --epochs 5
```

#### Script Directo

```bash
# Entrenar modelos individuales
python -m ml.pipeline.train_all --epochs 50 --batch-size 32

# Entrenar modelo multi-head
python -m ml.pipeline.train_all --multihead true --epochs 50
```

### Parámetros de Entrenamiento

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `--epochs` | Número de épocas | 50 |
| `--batch-size` | Tamaño de batch | 32 |
| `--img-size` | Tamaño de imagen | 224 |
| `--learning-rate` | Learning rate | 1e-4 |
| `--multihead` | Usar modelo multi-head | false |
| `--model-type` | Tipo de modelo (resnet18/convnext_tiny) | resnet18 |
| `--early-stopping-patience` | Paciencia para early stopping | 10 |

### Uso Programático

```python
from ml.regression.models import create_model
from ml.regression.scalers import load_scalers
from ml.regression.train import get_device

# Crear modelo
model = create_model(
    model_type="resnet18",
    num_outputs=1,
    pretrained=True,
    multi_head=False
)

# Cargar escaladores
scalers = load_scalers()

# Preparar datos
device = get_device()
model = model.to(device)

# Predicción (ejemplo)
import torch
x = torch.randn(1, 3, 224, 224).to(device)
with torch.no_grad():
    prediction = model(x)
```

## Configuración de Datos

### Split de Datos

- **Train**: 80% de los datos
- **Validation**: 10% de los datos  
- **Test**: 10% de los datos

### Estratificación

Los datos se estratifican por cuantiles de peso para mantener la distribución en todos los splits.

### Augmentaciones

- Rotación leve: ±5°
- Jitter de brillo/contraste: ±10%
- Normalización ImageNet estándar

## Evaluación

### Métricas por Target

```python
from ml.regression.evaluate import RegressionEvaluator

# Crear evaluador
evaluator = RegressionEvaluator(
    model=model,
    test_loader=test_loader,
    scalers=scalers
)

# Evaluar modelo individual
results = evaluator.evaluate_single_model("alto")

# Evaluar modelo multi-head
results = evaluator.evaluate_multi_head_model()
```

### Gráficos de Evaluación

```python
# Gráficos de paridad (predicción vs realidad)
evaluator.plot_parity_plots(save_path="parity_plots.png")

# Gráficos de residuos
evaluator.plot_residual_plots(save_path="residual_plots.png")

# Reporte completo
report = evaluator.generate_report(save_path="evaluation_report.json")
```

## Testing

Ejecutar tests:

```bash
cd backend
python -m pytest tests/test_regression_models.py -v
python -m pytest tests/test_regression_scalers.py -v
```

### Smoke Tests

Los tests incluyen verificaciones básicas:

- Forward pass sin errores
- Gradientes calculados correctamente
- Modelos cargables desde archivos
- Escaladores funcionan correctamente

## Troubleshooting

### Error: "timm no está instalado"

```bash
pip install timm
```

### Error: "No se encontraron crops"

Verificar que los crops se generaron correctamente:
```bash
python manage.py make_cacao_crops --validate-only
```

### Error: "CUDA out of memory"

Reducir el batch size:
```bash
python manage.py train_cacao_models --batch-size 8
```

### Error: "Muy pocos crops disponibles"

Se necesitan al menos 10 crops para entrenamiento. Generar más crops o verificar el dataset.

## Rendimiento Esperado

### ResNet18

- **Parámetros**: ~11M
- **Tiempo de entrenamiento**: ~30 min (50 épocas, CPU)
- **Tiempo de inferencia**: ~50ms por imagen (CPU)

### ConvNeXt Tiny

- **Parámetros**: ~28M  
- **Tiempo de entrenamiento**: ~45 min (50 épocas, CPU)
- **Tiempo de inferencia**: ~80ms por imagen (CPU)

### Métricas Típicas

- **MAE**: 0.5-1.0 mm/g
- **RMSE**: 0.7-1.5 mm/g
- **R²**: 0.7-0.9

## Próximos Pasos

1. **API REST**: Implementar endpoint de predicción
2. **Fine-tuning**: Ajustar modelos específicos para cacao
3. **Ensemble**: Combinar múltiples modelos
4. **Optimización**: Cuantización y optimización para producción
5. **Validación cruzada**: Implementar k-fold cross validation

## Contribución

Para contribuir al módulo de regresión:

1. Seguir las convenciones de código Python (PEP 8)
2. Añadir tests para nuevas funcionalidades
3. Documentar cambios en este README
4. Validar con tests antes de commitear
5. Usar el comando de entrenamiento para verificar funcionalidad
