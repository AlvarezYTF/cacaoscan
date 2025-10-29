# 📋 Guía de Carga del Dataset para CacaoScan

## 📍 Ubicación de Archivos

### Estructura de Directorios Requerida

```
backend/
├── media/
│   ├── datasets/           # 📁 Dataset CSV
│   │   └── dataset.csv     # Archivo CSV con medidas reales
│   └── cacao_images/
│       └── raw/            # 📁 Imágenes originales BMP
│           ├── 1.bmp
│           ├── 2.bmp
│           ├── 3.bmp
│           └── ...
```

## 📄 Formato del Dataset CSV

### Ubicación
```
backend/media/datasets/dataset.csv
```

### Formato
El archivo CSV debe tener el siguiente formato:

```csv
ID,ALTO,ANCHO,GROSOR,PESO
1,22.8,10.2,16.3,1.72
2,22.0,10.9,13.3,1.45
3,23.1,11.0,16.5,1.80
```

**IMPORTANTE:** El orden de las columnas puede variar. Estas son válidas:
- `ID,ALTO,ANCHO,GROSOR,PESO` (orden estándar)
- `ID,ALTO,GROSOR,ANCHO,PESO` (orden alternativo - también soportado)
- Cualquier orden mientras tengan los nombres correctos

### Columnas Requeridas:
- **ID**: Número identificador del grano (ej: 510, 509, 1, 2, 3, ...)
- **ALTO**: Altura del grano en milímetros (mm)
- **ANCHO**: Ancho del grano en milímetros (mm)
- **GROSOR**: Grosor del grano en milímetros (mm)
- **PESO**: Peso del grano en gramos (g)

### Ejemplo de Datos Reales:
```csv
ID,ALTO,ANCHO,GROSOR,PESO
1,22.8,10.2,16.3,1.72
2,22.0,10.9,13.3,1.45
3,23.1,11.0,16.5,1.80
4,21.5,9.8,15.2,1.55
5,24.0,11.5,17.0,2.00
```

## 🖼️ Formato de Imágenes

### Ubicación
```
backend/media/cacao_images/raw/
```

### Nomenclatura
Las imágenes deben nombrarse según el ID en el CSV:
- `1.bmp` corresponde al ID 1
- `2.bmp` corresponde al ID 2
- `3.bmp` corresponde al ID 3

### Formato de Archivo
- **Formato**: BMP (Bitmap)
- **Extensión**: `.bmp`
- **Dimensiones**: Cualquier tamaño (se procesarán automáticamente)

### Estructura de Archivos:
```
backend/media/cacao_images/raw/
├── 1.bmp
├── 2.bmp
├── 3.bmp
├── 4.bmp
└── 5.bmp
```

## 🔄 Pasos para Cargar el Dataset

### 1. Crear los Directorios

Si no existen, créalos manualmente o ejecuta estos comandos en la raíz del proyecto:

```bash
cd backend
mkdir -p media/datasets
mkdir -p media/cacao_images/raw
```

En Windows:
```powershell
cd backend
if not exist "media\datasets" mkdir "media\datasets"
if not exist "media\cacao_images\raw" mkdir "media\cacao_images\raw"
```

### 2. Copiar el Archivo CSV

```bash
# Copiar tu archivo CSV a:
backend/media/datasets/dataset.csv
```

### 3. Copiar las Imágenes BMP

```bash
# Copiar todas las imágenes BMP a:
backend/media/cacao_images/raw/
```

**Asegúrate de que:**
- Los archivos se nombren `{ID}.bmp` (ej: `1.bmp`, `2.bmp`, etc.)
- El formato sea BMP
- Los IDs coincidan con los del CSV

### 4. Verificar la Estructura

Ejecuta este comando para validar el dataset:

```bash
cd backend
python manage.py shell
```

Luego en el shell de Python:

```python
from ml.data.dataset_loader import CacaoDatasetLoader

loader = CacaoDatasetLoader()
stats = loader.get_dataset_stats()
print(stats)
```

### 5. Inicializar el Sistema

Una vez cargado el dataset, inicializa el sistema ML:

```bash
# Opción 1: Usando la API (recomendado)
curl -X POST http://localhost:8000/api/v1/auto-initialize/

# Opción 2: Usando comandos de Django
python manage.py train_cacao_models
```

## 📊 Validación del Dataset

El sistema automáticamente:
- ✅ Valida el formato del CSV
- ✅ Verifica existencia de imágenes
- ✅ Registra imágenes faltantes en `backend/media/datasets/missing_ids.log`
- ✅ Genera estadísticas del dataset

## ⚠️ Notas Importantes

1. **Formato BMP**: El sistema actual espera imágenes en formato BMP
2. **Nomenclatura**: Los IDs en el CSV y el nombre de las imágenes deben coincidir
3. **Separador CSV**: Usa coma (`,`) como separador
4. **Encabezados**: Deben ser en MAYÚSCULAS (ID, ALTO, ANCHO, GROSOR, PESO)
5. **Imágenes Faltantes**: Si una imagen no existe, se registra en `missing_ids.log` pero el entrenamiento continúa

## 🚀 Próximos Pasos

Después de cargar el dataset:

1. Ejecuta la inicialización automática
2. Espera a que se generen los crops
3. Espera a que se entrenen los modelos
4. Comienza a usar el análisis de lotes

## 📝 Ejemplo Completo

```
backend/
└── media/
    ├── datasets/
    │   ├── dataset.csv        # Tu archivo CSV con las medidas
    │   └── missing_ids.log # Generado automáticamente
    └── cacao_images/
        └── raw/
            ├── 1.bmp          # Imagen del grano 1
            ├── 2.bmp          # Imagen del grano 2
            ├── 3.bmp          # Imagen del grano 3
            ├── 4.bmp          # Imagen del grano 4
            └── 5.bmp          # Imagen del grano 5
```

## 🔍 Verificación Rápida

Para verificar que todo está en su lugar:

```bash
# Verificar archivo CSV
ls -lh backend/media/datasets/dataset.csv

# Verificar imágenes
ls -lh backend/media/cacao_images/raw/*.bmp

# Contar imágenes
ls backend/media/cacao_images/raw/*.bmp | wc -l

# Comparar con líneas en CSV
wc -l backend/media/datasets/dataset.csv
```

¡Listo! 🎉 Ahora puedes entrenar y usar los modelos ML de CacaoScan.

