# CacaoScan - Módulo de Machine Learning

Este módulo implementa la funcionalidad de segmentación y procesamiento de imágenes de granos de cacao usando YOLOv8-seg.

## Estructura del Proyecto

```
backend/
├── ml/
│   ├── data/
│   │   ├── dataset_loader.py    # Cargador y validador del dataset
│   │   └── transforms.py        # Transformaciones de imágenes
│   ├── segmentation/
│   │   ├── infer_yolo_seg.py    # Inferencia con YOLOv8-seg
│   │   └── cropper.py           # Procesador de recortes
│   ├── utils/
│   │   ├── paths.py             # Utilidades de rutas
│   │   ├── io.py                # Operaciones de E/O
│   │   └── logs.py              # Configuración de logging
│   └── artifacts/               # Modelos entrenados
├── media/
│   ├── datasets/
│   │   └── dataset.csv          # Dataset tabular
│   └── cacao_images/
│       ├── raw/                 # Imágenes originales BMP
│       ├── crops/               # Recortes procesados PNG
│       └── masks/               # Máscaras de segmentación (opcional)
└── management/commands/
    └── make_cacao_crops.py      # Comando para generar crops
```

## Instalación

### 1. Instalar dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 2. Preparar datos

Coloca tu archivo `dataset.csv` en `backend/media/datasets/` con las columnas:
- `ID`: Identificador único del grano
- `ALTO`: Altura en mm
- `ANCHO`: Ancho en mm  
- `GROSOR`: Grosor en mm
- `PESO`: Peso en gramos

Coloca las imágenes BMP en `backend/media/cacao_images/raw/` nombradas como `{ID}.bmp`.

### 3. Configurar Django

```bash
cd backend
python manage.py migrate
```

## Uso

### Generar recortes de granos

El comando principal para generar recortes es:

```bash
python manage.py make_cacao_crops
```

#### Parámetros disponibles:

- `--conf FLOAT`: Umbral de confianza para YOLO (default: 0.5)
- `--limit INT`: Límite de imágenes a procesar (0 = todas, default: 0)
- `--overwrite`: Sobrescribir crops existentes
- `--save-masks`: Guardar máscaras para debug
- `--crop-size INT`: Tamaño del crop cuadrado (default: 512)
- `--padding INT`: Padding adicional para el recorte (default: 10)
- `--validate-only`: Solo validar dataset sin procesar imágenes

#### Ejemplos:

```bash
# Procesar todas las imágenes con confianza 0.7
python manage.py make_cacao_crops --conf 0.7

# Procesar solo las primeras 10 imágenes
python manage.py make_cacao_crops --limit 10

# Procesar con máscaras guardadas para debug
python manage.py make_cacao_crops --save-masks

# Solo validar el dataset
python manage.py make_cacao_crops --validate-only

# Sobrescribir crops existentes con tamaño personalizado
python manage.py make_cacao_crops --overwrite --crop-size 256
```

### Uso programático

```python
from ml.data.dataset_loader import CacaoDatasetLoader
from ml.segmentation.cropper import create_cacao_cropper

# Cargar dataset
loader = CacaoDatasetLoader()
valid_records = loader.get_valid_records()

# Crear procesador de crops
cropper = create_cacao_cropper(
    confidence_threshold=0.5,
    crop_size=512,
    padding=10,
    save_masks=False
)

# Procesar lote
stats = cropper.process_batch(valid_records)
print(f"Procesadas {stats['successful']} imágenes exitosamente")
```

## Validación de Datos

El sistema valida automáticamente:

1. **Integridad del CSV**: Verifica columnas requeridas y tipos de datos
2. **Correspondencia de imágenes**: Valida que existan imágenes BMP para cada ID
3. **Calidad de segmentación**: Filtra detecciones de baja confianza
4. **Calidad de recortes**: Valida proporciones y áreas mínimas

Los IDs con imágenes faltantes se registran en `media/datasets/missing_ids.log`.

## Outputs

### Recortes procesados

Los recortes se guardan en `media/cacao_images/crops/` como archivos PNG con:
- Canal alpha para transparencia (estilo iPhone)
- Tamaño cuadrado normalizado
- Recorte ajustado al bounding box del grano

### Máscaras (opcional)

Si se usa `--save-masks`, las máscaras se guardan en `media/cacao_images/masks/` para debug.

### Logs

El sistema genera logs detallados con:
- Progreso de procesamiento
- Estadísticas de éxito/fallo
- Errores específicos por imagen

## Testing

Ejecutar tests:

```bash
cd backend
python -m pytest tests/ -v
```

Los tests cubren:
- Cargador de dataset
- Validación de datos
- Procesamiento de recortes
- Manejo de errores

## Troubleshooting

### Error: "Ultralytics no está instalado"

```bash
pip install ultralytics>=8.3.0
```

### Error: "Dataset CSV no encontrado"

Verificar que el archivo esté en `backend/media/datasets/dataset.csv`

### Error: "No se encontraron detecciones"

- Verificar que las imágenes estén en formato BMP
- Reducir el umbral de confianza con `--conf 0.3`
- Verificar que las imágenes contengan granos de cacao visibles

### Error: "Recorte de baja calidad"

El sistema filtra automáticamente recortes con:
- Proporciones extremas (muy alargados)
- Área muy pequeña
- Máscaras vacías

## Próximos Pasos

1. **Entrenamiento de modelos de regresión**: Usar los crops generados para entrenar modelos que predigan dimensiones
2. **API REST**: Implementar endpoints para predicción en tiempo real
3. **Optimización**: Fine-tuning del modelo YOLOv8-seg para granos de cacao específicos
4. **Validación cruzada**: Implementar splits estratificados para entrenamiento robusto

## Contribución

Para contribuir al módulo ML:

1. Seguir las convenciones de código Python (PEP 8)
2. Añadir tests para nuevas funcionalidades
3. Documentar cambios en este README
4. Validar con el comando `make_cacao_crops` antes de commitear
