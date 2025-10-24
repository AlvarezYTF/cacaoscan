# Componentes de Usuario para Predicción de Cacao

Este directorio contiene los componentes Vue.js para la funcionalidad de predicción de características físicas de granos de cacao.

## Componentes

### 1. ImageUpload.vue

Componente para subir imágenes de granos de cacao y enviarlas al backend para análisis.

#### Props
Ninguna prop requerida. El componente es autocontenido.

#### Eventos Emitidos

- `prediction-result`: Emitido cuando la predicción es exitosa
  ```javascript
  {
    id: number,
    width: number,
    height: number,  
    thickness: number,
    predicted_weight: number,
    confidence_level: string,
    confidence_score: number,
    processing_time: number,
    image_url: string,
    created_at: string,
    // ... otros campos opcionales
  }
  ```

- `prediction-error`: Emitido cuando hay un error en la predicción
  ```javascript
  Error object with message property
  ```

#### Funcionalidades

- **Drag & Drop**: Arrastra y suelta imágenes
- **File Browser**: Clic para abrir selector de archivos
- **Validación**: Validación de tipo, tamaño y dimensiones de imagen
- **Preview**: Vista previa de la imagen seleccionada
- **Metadatos**: Campos opcionales para lote, origen y notas
- **Loading State**: Indicador de carga durante el procesamiento
- **Error Handling**: Manejo y visualización de errores

#### Uso
```vue
<template>
  <ImageUpload 
    @prediction-result="handleResult"
    @prediction-error="handleError"
  />
</template>

<script>
import ImageUpload from '@/components/user/ImageUpload.vue';

export default {
  components: { ImageUpload },
  methods: {
    handleResult(prediction) {
      console.log('Predicción recibida:', prediction);
    },
    handleError(error) {
      console.error('Error:', error);
    }
  }
};
</script>
```

### 2. PredictionResults.vue

Componente para mostrar los resultados de predicción de manera visual y organizada.

#### Props

- `predictionData` (Object, required): Datos de la predicción
  - Debe contener al menos: `width`, `height`, `thickness`, `predicted_weight`
  - Campos opcionales: `confidence_level`, `confidence_score`, `image_url`, etc.

#### Eventos Emitidos

- `new-analysis`: Emitido cuando el usuario quiere hacer un nuevo análisis
- `save-analysis`: Emitido cuando el usuario quiere guardar el análisis actual

#### Funcionalidades

- **Visualización de dimensiones**: Ancho, alto, grosor en tarjetas visuales
- **Peso predicho**: Destacado con indicador visual especial
- **Nivel de confianza**: Indicador visual con colores y recomendaciones
- **Imagen analizada**: Muestra la imagen original con overlay de información
- **Métricas derivadas**: Volumen, densidad, área proyectada (si están disponibles)
- **Comparación de métodos**: Comparación entre CNN y regresión (si está disponible)
- **Acciones**: Descargar, compartir, guardar análisis
- **Información temporal**: Fecha/hora del análisis y tiempo de procesamiento

#### Uso
```vue
<template>
  <PredictionResults 
    :prediction-data="currentPrediction"
    @new-analysis="startNewAnalysis"
    @save-analysis="saveCurrentAnalysis"
  />
</template>

<script>
import PredictionResults from '@/components/user/PredictionResults.vue';

export default {
  components: { PredictionResults },
  data() {
    return {
      currentPrediction: {
        id: 1,
        width: 12.5,
        height: 8.3,
        thickness: 4.2,
        predicted_weight: 1.25,
        confidence_level: 'high',
        confidence_score: 0.85
      }
    };
  },
  methods: {
    startNewAnalysis() {
      this.currentPrediction = null;
    },
    saveCurrentAnalysis() {
      // Lógica para guardar
    }
  }
};
</script>
```

## Servicio de API

### predictionApi.js

Servicio para interactuar con el backend de predicción.

#### Funciones Principales

- `predictImage(formData)`: Envía imagen para predicción
- `getImage(imageId)`: Obtiene imagen por ID
- `getImageHistory(filters)`: Obtiene historial con filtros
- `getPredictionStats()`: Obtiene estadísticas
- `createImageFormData(file, metadata)`: Crea FormData para envío
- `validateImageFile(file)`: Valida archivo de imagen
- `formatPredictionResult(prediction)`: Formatea resultado para UI

#### Configuración

```javascript
// URL base configurada via variable de entorno
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Endpoints
const API_ENDPOINTS = {
  predict: '/api/images/predict/',
  images: '/api/images/',
  stats: '/api/images/stats/'
};
```

#### Validaciones

- **Formatos soportados**: JPG, PNG, BMP, TIFF
- **Tamaño máximo**: 20MB
- **Dimensiones mínimas**: 32x32 píxeles  
- **Dimensiones máximas**: 4096x4096 píxeles

## Vista de Ejemplo

### PredictionView.vue

Vista completa que demuestra el uso integrado de ambos componentes.

#### Funcionalidades

- **Layout responsivo**: Grid adaptativo para desktop y móvil
- **Gestión de estado**: Manejo centralizado de predicción actual y historial
- **Error handling**: Manejo global de errores con notificaciones
- **Historial reciente**: Lista de análisis recientes con navegación
- **Mensajes de éxito**: Notificaciones de acciones completadas
- **Consejos de uso**: Información para mejores resultados

#### Uso

Accesible en la ruta `/prediccion` después de agregar al router:

```javascript
{
  path: '/prediccion',
  name: 'prediction', 
  component: PredictionView,
  meta: {
    title: 'Análisis de Granos de Cacao | CacaoScan'
  }
}
```

## Estructura de Respuesta de la API

### Predicción Exitosa

```json
{
  "success": true,
  "id": 1,
  "width": 12.5,
  "height": 8.3,
  "thickness": 4.2,
  "predicted_weight": 1.25,
  "prediction_method": "vision_cnn",
  "confidence_level": "high",
  "confidence_score": 0.85,
  "processing_time": 0.125,
  "image_url": "http://localhost:8000/media/cacao_images/grain_001.jpg",
  "created_at": "2024-01-15T10:30:00Z",
  "derived_metrics": {
    "volume_mm3": 215.3,
    "density_g_per_cm3": 0.98,
    "aspect_ratio": 1.51,
    "projected_area_mm2": 81.7
  },
  "weight_comparison": {
    "vision_weight": 1.25,
    "regression_weight": 1.23,
    "difference": 0.02,
    "agreement_level": "excellent"
  }
}
```

### Error de Predicción

```json
{
  "success": false,
  "error": "Error en el procesamiento de la imagen",
  "details": "Formato de imagen no soportado",
  "message": "Error en la validación de la imagen"
}
```

## Estilos y Diseño

### Framework CSS
- **Tailwind CSS**: Framework principal para estilos
- **Componente**: Estilos scoped para cada componente
- **Responsive**: Diseño adaptativo para todos los dispositivos

### Colores y Temas
- **Verde**: Color principal para acciones y estados exitosos
- **Rojo**: Errores y validaciones fallidas  
- **Azul**: Información y acciones secundarias
- **Gris**: Texto neutro y fondos

### Iconos
- **Heroicons**: Conjunto de iconos SVG consistente
- **Estados**: Iconos específicos para cada tipo de contenido
- **Acciones**: Iconos descriptivos para botones y enlaces

## Mejores Prácticas

### Rendimiento
- **Validación client-side**: Validar antes de enviar al servidor
- **Imágenes optimizadas**: Redimensionar si es necesario
- **Loading states**: Indicadores de progreso para mejor UX
- **Error boundaries**: Manejo graceful de errores

### Accesibilidad
- **ARIA labels**: Etiquetas descriptivas para lectores de pantalla
- **Keyboard navigation**: Soporte completo de teclado
- **Focus management**: Gestión apropiada del foco
- **Color contrast**: Contrastes adecuados para visibilidad

### Seguridad
- **Validación dual**: Cliente y servidor
- **Sanitización**: Limpieza de inputs del usuario
- **File validation**: Verificación estricta de archivos
- **Error handling**: No exposer información sensible

## Desarrollo y Testing

### Estructura de Archivos
```
src/
├── components/
│   └── user/
│       ├── ImageUpload.vue
│       ├── PredictionResults.vue
│       └── README.md
├── services/
│   └── predictionApi.js
└── views/
    └── PredictionView.vue
```

### Testing
- **Unit tests**: Probar componentes individualmente
- **Integration tests**: Probar flujo completo
- **E2E tests**: Probar desde la perspectiva del usuario
- **API mocking**: Simular respuestas del backend

### Variables de Entorno

```bash
# .env.development
VITE_API_URL=http://localhost:8000
VITE_MAX_FILE_SIZE=10485760
VITE_SUPPORTED_FORMATS=image/jpeg,image/jpg,image/png,image/bmp,image/tiff
```

## Próximos Pasos

### Funcionalidades Futuras
- **Batch processing**: Análisis de múltiples imágenes
- **Comparación**: Comparar múltiples granos
- **Exportación**: Exportar resultados a CSV/PDF
- **Offline mode**: Funcionalidad sin conexión

### Mejoras de UX
- **Progress tracking**: Progreso detallado del análisis
- **Image editing**: Herramientas básicas de edición
- **Annotations**: Anotaciones sobre la imagen
- **3D visualization**: Vista 3D de las dimensiones

### Integraciones
- **Camera API**: Captura directa desde cámara
- **Cloud storage**: Almacenamiento en la nube
- **Social sharing**: Compartir en redes sociales
- **Analytics**: Métricas de uso y rendimiento
