# Herramientas, Métodos y Principios de Construcción del Sistema ML - CacaoScan

## 📋 Resumen Ejecutivo

Este documento detalla las **herramientas**, **métodos de Machine Learning**, **arquitecturas de red neuronal**, **patrones de diseño** y **principios de ingeniería de software** utilizados para construir el sistema ML de CacaoScan.

---

## 🛠️ HERRAMIENTAS Y LIBRERÍAS

### 1. **Framework de Deep Learning**

#### **PyTorch 2.5.1**
- **Uso**: Framework principal para deep learning
- **Funcionalidades utilizadas**:
  - `torch.nn.Module`: Base para todos los modelos
  - `torch.optim`: Optimizadores (Adam, SGD, AdamW)
  - `torch.utils.data.DataLoader`: Carga eficiente de datos
  - `torchvision.models`: Modelos pre-entrenados (ResNet18, etc.)
  - GPU/CPU automático: Detección automática de dispositivo
- **Ventajas**: Flexibilidad, debugging fácil, soporte dinámico

#### **TorchVision 0.20.1**
- **Uso**: Utilidades de visión por computadora para PyTorch
- **Funcionalidades**:
  - Transformaciones de imágenes (`transforms`)
  - Modelos pre-entrenados (`resnet18`, etc.)
  - Conjuntos de datos estándar

### 2. **Visión por Computadora**

#### **OpenCV 4.12.0.88** (`opencv-python` + `opencv-python-headless`)
- **Uso**: Procesamiento de imágenes y segmentación
- **Funcionalidades utilizadas**:
  - Segmentación de objetos (GrabCut, watershed)
  - Operaciones morfológicas
  - Filtros y transformaciones
  - Conversión de formatos de imagen
- **Versión headless**: Para servidores sin GUI

#### **YOLOv8 (Ultralytics 8.3.234)**
- **Uso**: Detección y segmentación de objetos en tiempo real
- **Funcionalidades**:
  - YOLOv8-seg para segmentación semántica
  - Detección de granos de cacao
  - Validación obligatoria de imágenes antes del procesamiento
- **Ventajas**: Alta precisión, velocidad, detección en tiempo real

#### **rembg** (vía `rembg`)
- **Uso**: Eliminación de fondo usando U2Net
- **Funcionalidades**: Segmentación de objetos de alta calidad
- **Uso en cascada**: Como respaldo si U-Net falla

### 3. **Machine Learning Tradicional**

#### **scikit-learn 1.7.2**
- **Uso**: Normalización y escalado de datos
- **Funcionalidades**:
  - `StandardScaler`, `MinMaxScaler`, `RobustScaler`
  - Normalización de targets (dimensiones y peso)
  - Validación cruzada

#### **scikit-image 0.25.2**
- **Uso**: Procesamiento avanzado de imágenes
- **Funcionalidades**: Transformaciones, filtros, segmentación

### 4. **Procesamiento de Datos**

#### **NumPy 2.1.3**
- **Uso**: Operaciones numéricas y arrays
- **Funcionalidades**: Álgebra lineal, operaciones sobre arrays

#### **Pandas 2.3.3**
- **Uso**: Manipulación y análisis de datos estructurados
- **Funcionalidades**: Carga de CSVs, procesamiento de datasets

#### **Pillow 12.0.0**
- **Uso**: Procesamiento básico de imágenes
- **Funcionalidades**: Apertura, guardado, conversión de formatos

### 5. **Modelos Pre-entrenados**

#### **timm 0.9.12** (PyTorch Image Models)
- **Uso**: Modelos pre-entrenados adicionales
- **Modelo utilizado**: `ConvNeXt Tiny`
- **Ventajas**: Modelos modernos, optimizados, pre-entrenados en ImageNet-12k

### 6. **Data Augmentation**

#### **albumentations 2.0.8**
- **Uso**: Aumento de datos avanzado para imágenes
- **Funcionalidades**: Transformaciones aleatorias, aumentación rápida

#### **PyTorch Transforms**
- **Uso**: Transformaciones estándar de PyTorch
- **Funcionalidades**: Normalización, redimensionado, recorte

---

## 🧠 MÉTODOS DE MACHINE LEARNING

### 1. **Técnicas de Aprendizaje**

#### **Transfer Learning (Aprendizaje por Transferencia)**
- **Método**: Usar modelos pre-entrenados en ImageNet
- **Modelos utilizados**:
  - **ResNet18**: Pre-entrenado en ImageNet-1K
  - **ConvNeXt Tiny**: Pre-entrenado en ImageNet-12k
- **Estrategia**: 
  - Fine-tuning completo o parcial
  - Congelamiento opcional del backbone
- **Ventajas**: Menos datos requeridos, mejor generalización

#### **Multi-Task Learning (Aprendizaje Multi-Tarea)**
- **Método**: Predecir múltiples targets simultáneamente (alto, ancho, grosor, peso)
- **Arquitectura**: Multi-head regression
- **Ventajas**: Compartir representaciones, mejor generalización

#### **Hybrid Learning (Aprendizaje Híbrido)**
- **Método**: Combinar CNN + Features de píxeles
- **Componentes**:
  - **CNN**: Extrae features visuales profundas (ResNet18 + ConvNeXt)
  - **Pixel Features**: Features extraídas manualmente (ancho, alto, área, escala, aspect ratio)
- **Fusión**: Concatenación o Feature Gating
- **Ventajas**: Combina aprendizaje profundo con conocimiento del dominio

#### **Incremental Learning (Aprendizaje Incremental)**
- **Métodos implementados**:
  - **Elastic Weight Consolidation (EWC)**: Preserva pesos importantes
  - **L2 Regularization**: Regularización L2 para prevenir olvido catastrófico
  - **Replay Buffer**: Almacena ejemplos antiguos
  - **Mixed Strategy**: Combinación de estrategias
- **Uso**: Entrenar con nuevos datos sin perder conocimiento previo

### 2. **Arquitecturas de Red Neuronal**

#### **ResNet18 (Residual Network)**
- **Arquitectura**: Red residual de 18 capas
- **Uso**: Backbone para extracción de características visuales
- **Características**: 
  - Conexiones residuales
  - 512 dimensiones de salida
  - Pre-entrenado en ImageNet-1K
- **Ventajas**: Fácil entrenamiento, buenos resultados, rápido

#### **ConvNeXt Tiny**
- **Arquitectura**: Arquitectura moderna inspirada en Vision Transformers
- **Uso**: Backbone alternativo más moderno
- **Características**:
  - 768 dimensiones de salida
  - Pre-entrenado en ImageNet-12k
  - Arquitectura más eficiente
- **Ventajas**: Mejor rendimiento, arquitectura moderna

#### **U-Net**
- **Arquitectura**: Encoder-decoder con conexiones skip
- **Uso**: Segmentación de fondo de granos de cacao
- **Características**:
  - Arquitectura ligera
  - Segmentación binaria (fondo vs. objeto)
  - Conexiones skip para preservar detalles
- **Ventajas**: Efectivo para segmentación, arquitectura simple

#### **YOLOv8-seg**
- **Arquitectura**: Detector de objetos + segmentación semántica
- **Uso**: Detección y segmentación de granos de cacao
- **Características**:
  - Detección en tiempo real
  - Segmentación de máscaras
  - Validación obligatoria de imágenes
- **Ventajas**: Alta precisión, velocidad, validación robusta

#### **Hybrid Model (Modelo Híbrido)**
- **Arquitectura**: Fusiona múltiples fuentes de información
- **Componentes**:
  ```
  ResNet18 (512 dims) ──┐
                        ├──> Feature Fusion ──> MLP ──> 4 outputs
  ConvNeXt (768 dims) ──┤    (Concatenación o Gating)
                        │
  Pixel Features (5-12) ─┘
  ```
- **Fusion Strategies**:
  - **Concatenation**: Simple concatenación
  - **Feature Gating**: Mecanismo de atención para controlar qué features usar
- **Ventajas**: Combina lo mejor de múltiples enfoques

### 3. **Técnicas de Optimización**

#### **Optimizadores**
- **Adam**: Optimizador adaptativo (learning rate automático)
- **AdamW**: Adam con decaimiento de peso separado
- **SGD**: Descenso de gradiente estocástico (opcional)

#### **Learning Rate Scheduling**
- **ReduceLROnPlateau**: Reduce LR cuando el loss se estanca
- **StepLR**: Reduce LR en épocas específicas
- **CosineAnnealingLR**: Reducción suave tipo coseno

#### **Regularización**
- **Dropout**: Previene overfitting (tasa: 0.1-0.3)
- **Weight Decay**: Regularización L2 en los pesos
- **Batch Normalization**: Normalización por lotes
- **Early Stopping**: Detención temprana basada en validación

#### **Loss Functions (Funciones de Pérdida)**
- **MSE (Mean Squared Error)**: Pérdida estándar para regresión
- **MAE (Mean Absolute Error)**: Alternativa más robusta
- **Uncertainty Weighted Loss**: Pérdida ponderada por incertidumbre
- **Huber Loss**: Combinación de MSE y MAE (robusta a outliers)

### 4. **Técnicas de Preprocesamiento**

#### **Normalización**
- **ImageNet Normalization**: Media y desviación estándar de ImageNet
- **Target Normalization**: 
  - StandardScaler (z-score)
  - MinMaxScaler (0-1)
  - RobustScaler (resistente a outliers)

#### **Data Augmentation (Aumento de Datos)**
- **Técnicas aplicadas**:
  - Rotación aleatoria
  - Volteo horizontal/vertical
  - Cambio de brillo/contraste
  - Cambio de saturación
  - Recorte aleatorio
  - MixUp: Mezcla de imágenes
  - CutMix: Recorte y mezcla
  - Random Erasing: Eliminación aleatoria de regiones

#### **Segmentación de Fondo**
- **Cascada de métodos**:
  1. **U-Net** (primario): Segmentación basada en deep learning
  2. **rembg (U2Net)** (secundario): Eliminación de fondo de alta calidad
  3. **OpenCV** (terciario): Métodos tradicionales (GrabCut, watershed)
- **Validación YOLO**: Validación obligatoria antes de procesar

---

## 🏗️ PRINCIPIOS DE INGENIERÍA DE SOFTWARE

### 1. **SOLID Principles**

#### **Single Responsibility Principle (SRP)**
- **Aplicación**:
  - Cada módulo tiene una responsabilidad única
  - `models.py`: Solo definición de modelos
  - `train.py`: Solo entrenamiento
  - `predict.py`: Solo predicción
  - `scalers.py`: Solo normalización
- **Ejemplo**:
  ```python
  # Separación clara de responsabilidades
  - regression/models.py      → Modelos CNN
  - regression/scalers.py     → Normalización
  - regression/train.py       → Entrenamiento
  - prediction/predict.py     → Predicción
  - segmentation/processor.py → Segmentación
  ```

#### **Open/Closed Principle (OCP)**
- **Aplicación**:
  - Extensible sin modificar código existente
  - Factory Pattern para crear modelos
  - Strategy Pattern para diferentes estrategias
- **Ejemplo**:
  ```python
  # Nuevos modelos se agregan sin modificar código existente
  class CreadorModeloBase(ABC):
      @abstractmethod
      def crear_modelo(...): pass
  
  class CreadorModeloHibrido(CreadorModeloBase):
      def crear_modelo(...): ...  # Nueva implementación
  ```

#### **Liskov Substitution Principle (LSP)**
- **Aplicación**:
  - Clases base intercambiables
  - `PredictorBase` puede ser sustituido por `PredictorCacao`
  - `ExtractionStrategy` puede ser sustituido por estrategias específicas

#### **Interface Segregation Principle (ISP)**
- **Aplicación**:
  - Interfaces específicas y pequeñas
  - `PredictorBase` solo expone métodos necesarios
  - Estrategias específicas para cada caso de uso

#### **Dependency Inversion Principle (DIP)**
- **Aplicación**:
  - Dependencias de abstracciones, no implementaciones
  - Uso de interfaces y clases base
  - Inyección de dependencias

### 2. **Design Patterns (Patrones de Diseño)**

#### **Factory Pattern (Patrón Fábrica)**
- **Ubicación**: `backend/ml/regression/factories/`
- **Uso**: Creación de modelos de forma dinámica
- **Implementación**:
  ```python
  class FabricaModelo:
      def create_model(self, model_type, ...):
          # Delega a creadores específicos
          return self._selector.crear_modelo(...)
  ```
- **Ventajas**: Extensibilidad, desacoplamiento

#### **Singleton Pattern (Patrón Singleton)**
- **Ubicación**: `MLService`, Factory instances
- **Uso**: Una sola instancia de servicios críticos
- **Implementación**:
  ```python
  class MLService:
      _instance = None
      def __new__(cls):
          if cls._instance is None:
              cls._instance = super().__new__(cls)
          return cls._instance
  ```
- **Ventajas**: Control de recursos, acceso global

#### **Strategy Pattern (Patrón Estrategia)**
- **Ubicación**: `backend/ml/data/datasets/extractors/strategies/`
- **Uso**: Diferentes estrategias de extracción de features
- **Implementación**:
  ```python
  class ExtractionStrategy(ABC):
      @abstractmethod
      def extract(...): pass
  
  class BasicExtractionStrategy(ExtractionStrategy): ...
  class ExtendedExtractionStrategy(ExtractionStrategy): ...
  ```
- **Ventajas**: Intercambiabilidad, extensibilidad

#### **Template Method Pattern**
- **Uso**: Pipeline de entrenamiento con pasos definidos
- **Implementación**: Clase base con métodos abstractos

#### **Adapter Pattern**
- **Uso**: Adaptar diferentes formatos de datos
- **Implementación**: Conversores entre formatos

### 3. **Otros Principios de Diseño**

#### **DRY (Don't Repeat Yourself)**
- **Aplicación**:
  - Funciones reutilizables
  - Utilidades compartidas
  - Evitar duplicación de código

#### **KISS (Keep It Simple, Stupid)**
- **Aplicación**:
  - Código simple y directo
  - Evitar complejidad innecesaria
  - Claridad sobre optimización prematura

#### **YAGNI (You Aren't Gonna Need It)**
- **Aplicación**:
  - Solo implementar lo necesario
  - Evitar funcionalidades anticipadas
  - Enfoque incremental

---

## 📐 ARQUITECTURA DEL SISTEMA ML

### Estructura Modular

```
backend/ml/
├── regression/          # Modelos de regresión
│   ├── models.py        # Arquitecturas CNN
│   ├── train.py         # Entrenamiento
│   ├── evaluate.py      # Evaluación
│   ├── scalers.py       # Normalización
│   └── factories/       # Factory Pattern
├── prediction/          # Predicción
│   ├── predict.py       # Predictor principal
│   └── base_predictor.py # Clase base
├── segmentation/        # Segmentación
│   ├── processor.py     # Procesador principal
│   └── infer_yolo_seg.py # YOLO inference
├── data/                # Procesamiento de datos
│   ├── dataset_loader.py
│   ├── normalizers/     # Normalización
│   └── transforms/      # Transformaciones
└── utils/               # Utilidades
```

### Flujo de Procesamiento

```
1. Input Image
   ↓
2. YOLO Validation (obligatorio)
   ↓
3. Segmentation (U-Net → rembg → OpenCV)
   ↓
4. Crop Extraction
   ↓
5. Pixel Feature Extraction
   ↓
6. CNN Feature Extraction (ResNet18 + ConvNeXt)
   ↓
7. Feature Fusion
   ↓
8. Regression Head
   ↓
9. Denormalization
   ↓
10. Output (alto, ancho, grosor, peso)
```

---

## 🔬 MÉTODOS DE VALIDACIÓN Y EVALUACIÓN

### 1. **Métricas de Regresión**

- **R² Score (Coeficiente de Determinación)**: Medida de bondad de ajuste
- **MAE (Mean Absolute Error)**: Error absoluto promedio
- **RMSE (Root Mean Squared Error)**: Raíz del error cuadrático medio
- **MAPE (Mean Absolute Percentage Error)**: Error porcentual promedio
- **Robust R²**: Versión robusta del R²

### 2. **Validación del Modelo**

- **Train/Validation/Test Split**: División estándar (70/15/15)
- **Cross-Validation**: Validación cruzada K-fold
- **Early Stopping**: Basado en métricas de validación
- **Model Checkpointing**: Guardar mejores modelos

### 3. **Monitoreo de Entrenamiento**

- **Training History**: Seguimiento de loss y métricas
- **Learning Curves**: Visualización de progreso
- **Model Metrics Storage**: Almacenamiento en BD
- **Comparison Tools**: Comparación entre modelos

---

## 🚀 OPTIMIZACIONES Y MEJORAS

### 1. **Optimizaciones de Rendimiento**

- **GPU Acceleration**: Uso automático de GPU si está disponible
- **Batch Processing**: Procesamiento por lotes
- **Lazy Loading**: Carga diferida de modelos
- **Caching**: Cache de predicciones y estado

### 2. **Optimizaciones de Modelo**

- **Model Quantization**: Reducción de precisión (opcional)
- **Optimized Models**: Versiones optimizadas de modelos
- **Feature Extraction Caching**: Cache de features extraídas

### 3. **Mejoras de Arquitectura**

- **Batch Normalization**: Normalización por lotes
- **Dropout**: Regularización
- **Weight Initialization**: Inicialización adecuada
- **Feature Gating**: Control de features en modelos híbridos

---

## 📚 TECNOLOGÍAS COMPLEMENTARIAS

### Backend
- **Django 5.2.9**: Framework web
- **Django REST Framework**: API REST
- **PostgreSQL**: Base de datos
- **Redis** (opcional): Cache y colas

### Herramientas de Desarrollo
- **pytest**: Testing
- **coverage**: Cobertura de código
- **black/flake8**: Formateo y linting

---

## 📊 RESUMEN DE TECNOLOGÍAS

| Categoría | Tecnología | Versión | Uso Principal |
|-----------|-----------|---------|---------------|
| **Deep Learning** | PyTorch | 2.5.1 | Framework principal |
| **Vision** | TorchVision | 0.20.1 | Utilidades de visión |
| **CV** | OpenCV | 4.12.0.88 | Procesamiento de imágenes |
| **Detection** | Ultralytics (YOLOv8) | 8.3.234 | Detección y segmentación |
| **Segmentation** | rembg (U2Net) | - | Eliminación de fondo |
| **ML Tradicional** | scikit-learn | 1.7.2 | Normalización |
| **Image Processing** | scikit-image | 0.25.2 | Procesamiento avanzado |
| **Pre-trained** | timm | 0.9.12 | ConvNeXt Tiny |
| **Augmentation** | albumentations | 2.0.8 | Data augmentation |
| **NumPy** | numpy | 2.1.3 | Operaciones numéricas |
| **Data** | pandas | 2.3.3 | Manipulación de datos |
| **Images** | Pillow | 12.0.0 | Procesamiento básico |

---

## ✅ CONCLUSIÓN

El sistema ML de CacaoScan utiliza:

✅ **Herramientas modernas**: PyTorch, YOLOv8, modelos pre-entrenados  
✅ **Arquitecturas avanzadas**: ResNet, ConvNeXt, U-Net, modelos híbridos  
✅ **Principios SOLID**: Código mantenible y extensible  
✅ **Design Patterns**: Factory, Singleton, Strategy  
✅ **Métodos avanzados**: Transfer learning, multi-task learning, incremental learning  
✅ **Optimizaciones**: GPU, batch processing, caching  

El sistema está diseñado para ser **robusto**, **extensible** y **eficiente**, siguiendo las mejores prácticas de ingeniería de software y machine learning.

