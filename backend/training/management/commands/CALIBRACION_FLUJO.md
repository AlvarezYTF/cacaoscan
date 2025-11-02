# 📊 Diagrama de Flujo: Sistema de Calibración Basado en Píxeles

## 🔄 Flujo Completo del Sistema de Calibración

```
┌─────────────────────────────────────────────────────────────────┐
│                    CALIBRACIÓN DEL DATASET                      │
│         (Procesa imágenes BMP → Mide píxeles → Crea JSON)      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  1. LEER DATASET CSV                │
        │  dataset_cacao.clean.csv            │
        │  - ID, ALTO, ANCHO, GROSOR, PESO    │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  2. PARA CADA IMAGEN EN CSV         │
        │  Por cada registro válido:         │
        │  - Leer imagen .bmp desde raw/      │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  3. SEGMENTAR (QUITAR FONDO)         │
        │  Usa: segment_and_crop_cacao_bean() │
        │  ├─ Intenta U-Net (remove_bg_ai)   │
        │  ├─ Fallback: OpenCV/GrabCut       │
        │  └─ Resultado: PNG con alpha        │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  4. MEDIR PÍXELES DEL GRANO         │
        │  De la imagen segmentada (PNG):     │
        │  - grain_area_pixels (área total)   │
        │  - width_pixels (bbox ancho)        │
        │  - height_pixels (bbox alto)        │
        │  - background_pixels (eliminados)   │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  5. CALCULAR FACTORES DE ESCALA     │
        │  Usando datos REALES del CSV:      │
        │  - scale_alto = alto_real / height_px│
        │  - scale_ancho = ancho_real / width_px│
        │  - scale_promedio = promedio        │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  6. GUARDAR DATOS DE CALIBRACIÓN     │
        │  Por cada imagen:                   │
        │  - PNG procesado en processed_png/  │
        │  - Registro JSON con:               │
        │    * Datos reales (CSV)              │
        │    * Medidas en píxeles              │
        │    * Factores de escala              │
        │    * Píxeles de fondo eliminados     │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  7. GENERAR ARCHIVO JSON            │
        │  pixel_calibration.json             │
        │  - Lista de registros calibrados     │
        │  - Estadísticas agregadas            │
        │  - Factor escala promedio           │
        └─────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    USO EN PREDICCIÓN                            │
│         (Carga calibración → Busca registro similar)           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  1. CARGAR CALIBRACIÓN              │
        │  Al inicializar CacaoPredictor:     │
        │  - Lee pixel_calibration.json       │
        │  - Carga registros en memoria       │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  2. ANALIZAR IMAGEN NUEVA          │
        │  - Segmentar imagen                │
        │  - Medir píxeles del grano         │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  3. BUSCAR REGISTRO SIMILAR         │
        │  Compara dimensiones en píxeles:    │
        │  - width_pixels, height_pixels       │
        │  - Calcula distancia euclidiana     │
        │  - Selecciona registro más cercano  │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  4. USAR FACTOR DE ESCALA           │
        │  Del registro similar:              │
        │  - Si distancia < 50% → usar      │
        │    factor de ese registro           │
        │  - Si no → usar promedio            │
        │  - Calcular dimensiones físicas     │
        └─────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  5. PREDICCIÓN FINAL                │
        │  - Alto, Ancho, Grosor, Peso        │
        │  - Basado en píxeles medidos        │
        │  - Calibrado con datos reales       │
        └─────────────────────────────────────┘
```

## 📋 Componentes y Funciones Utilizadas

### Funciones Existentes que se Reutilizan:

1. **Segmentación (Quitar Fondo)**
   - `segment_and_crop_cacao_bean(image_path, method="ai")` 
     - Ubicación: `ml/segmentation/processor.py`
     - Convierte BMP → PNG segmentado
     - Quita fondo usando U-Net o OpenCV

2. **Cropper para Procesamiento**
   - `create_cacao_cropper()` 
     - Ubicación: `ml/segmentation/cropper.py`
     - Procesa imágenes con YOLO

3. **Loader de Dataset**
   - `CacaoDatasetLoader()`
     - Ubicación: `ml/data/dataset_loader.py`
     - Lee CSV y valida imágenes

### Flujo de Datos:

```
CSV Dataset → Leer Registros
    ↓
Por cada imagen:
    ↓
    BMP en raw/ → segment_and_crop_cacao_bean() → PNG segmentado
    ↓
    Medir píxeles (área, ancho, alto)
    ↓
    Calcular: factor_escala = dimension_real / dimension_pixeles
    ↓
    Guardar PNG + Datos JSON
    ↓
Generar pixel_calibration.json
    ↓
Al predecir:
    ↓
    Segmentar imagen nueva
    ↓
    Medir píxeles
    ↓
    Buscar registro similar en calibración
    ↓
    Usar factor_escala del registro similar
    ↓
    Calcular dimensiones físicas precisas
```

## 🎯 Ventajas del Sistema

1. **Reutiliza funciones existentes** - No duplica código
2. **Calibración precisa** - Usa datos reales del dataset
3. **Escalable** - Añade más imágenes al dataset automáticamente
4. **Validado** - Cada imagen tiene datos reales del CSV

