# Cómo Ejecutar los Tests de CacaoScan

## Opción 1: Usando el Script (Recomendado)

### Windows:
```bash
cd backend
python run_tests.py
```

### Linux/Mac:
```bash
cd backend
python run_tests.py
```

O usando el script shell:
```bash
cd backend
chmod +x run_tests.sh
./run_tests.sh
```

## Opción 2: Usando pytest directamente

### Ejecutar todos los tests:
```bash
cd backend
pytest tests/ -v
```

### Ejecutar un archivo específico:
```bash
cd backend
pytest tests/test_ml_prediction_predict.py -v
```

### Ejecutar una clase específica:
```bash
cd backend
pytest tests/test_ml_prediction_predict.py::TestCacaoPredictor -v
```

### Ejecutar un test específico:
```bash
cd backend
pytest tests/test_ml_prediction_predict.py::TestCacaoPredictor::test_cacao_predictor_initialization -v
```

## Opciones Útiles

### Detenerse en el primer error:
```bash
pytest tests/ -v -x
```

### Mostrar más detalles:
```bash
pytest tests/ -v --tb=long
```

### Ejecutar con cobertura:
```bash
pytest tests/ --cov=. --cov-report=html
```

### Ejecutar solo tests rápidos (excluir marcados como 'slow'):
```bash
pytest tests/ -v -m "not slow"
```

## Estructura de Tests

Los tests están organizados por módulo:

- **ML Prediction**: `test_ml_prediction_*.py`
- **ML Segmentation**: `test_ml_segmentation_*.py`
- **ML Data & Scalers**: `test_ml_*.py`
- **API Services**: `test_api_services_*.py`
- **Image Processing**: `test_images_services_*.py`
- **Training Commands**: `test_training_commands_*.py`
- **Reports**: `test_reports_*.py`

## Solución de Problemas

### Si pytest no está instalado:
```bash
pip install pytest pytest-django
```

### Si hay errores de importación:
Asegúrate de que Django esté configurado correctamente:
```bash
export DJANGO_SETTINGS_MODULE=cacaoscan.settings
```

O en Windows:
```cmd
set DJANGO_SETTINGS_MODULE=cacaoscan.settings
```

### Si hay errores de módulos faltantes:
Instala las dependencias:
```bash
pip install -r requirements.txt
```

