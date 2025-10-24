# CacaoScan - Sistema Completamente Automático

## 🎯 **Descripción**

CacaoScan ahora es un sistema **completamente automático** que entrena los modelos y genera predicciones sin necesidad de comandos manuales. Solo necesitas consumir los endpoints desde el frontend.

## 🚀 **Flujo Automático**

### **Primera vez (Inicialización)**
1. **Frontend llama**: `POST /api/v1/auto-initialize/`
2. **Sistema automáticamente**:
   - ✅ Valida dataset CSV
   - ✅ Genera crops con YOLOv8-seg
   - ✅ Entrena 4 modelos de regresión
   - ✅ Carga modelos en memoria
   - ✅ Sistema listo para predicciones

### **Uso normal (Predicciones)**
1. **Frontend llama**: `POST /api/v1/scan/measure/` con imagen
2. **Sistema automáticamente**:
   - ✅ Segmenta el grano con YOLOv8-seg
   - ✅ Predice dimensiones y peso
   - ✅ Devuelve JSON con resultados
   - ✅ Guarda crop procesado

## 📋 **Endpoints Principales**

### 1. **Inicialización Automática**
```
POST /api/v1/auto-initialize/
```

**Descripción**: Inicializa completamente el sistema la primera vez.

**Response** (200 OK):
```json
{
  "message": "Sistema inicializado automáticamente y listo para predicciones",
  "status": "success",
  "steps_completed": [
    "✅ Dataset validado",
    "✅ Crops generados", 
    "✅ Modelos entrenados",
    "✅ Modelos cargados",
    "🎉 Sistema listo para predicciones"
  ],
  "total_time_seconds": 120.5,
  "ready_for_predictions": true
}
```

### 2. **Predicción de Granos**
```
POST /api/v1/scan/measure/
```

**Descripción**: Predice dimensiones y peso de un grano de cacao.

**Request**: `multipart/form-data` con campo `image`

**Response** (200 OK):
```json
{
  "alto_mm": 10.5,
  "ancho_mm": 8.3,
  "grosor_mm": 6.1,
  "peso_g": 2.3,
  "confidences": {
    "alto": 0.85,
    "ancho": 0.80,
    "grosor": 0.75,
    "peso": 0.70
  },
  "crop_url": "/media/cacao_images/crops_runtime/uuid.png",
  "debug": {
    "segmented": true,
    "yolo_conf": 0.9,
    "latency_ms": 150,
    "models_version": "v1"
  }
}
```

### 3. **Estado del Sistema**
```
GET /api/v1/models/status/
```

**Descripción**: Verifica el estado de los modelos cargados.

## 🎯 **Uso desde el Frontend**

### **JavaScript/React**
```javascript
// 1. Inicialización (solo la primera vez)
const initializeSystem = async () => {
  const response = await fetch('/api/v1/auto-initialize/', {
    method: 'POST'
  });
  const data = await response.json();
  console.log('Sistema inicializado:', data);
};

// 2. Predicción de grano
const predictGrain = async (imageFile) => {
  const formData = new FormData();
  formData.append('image', imageFile);
  
  const response = await fetch('/api/v1/scan/measure/', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  console.log('Predicciones:', data);
  return data;
};
```

### **Vue.js**
```javascript
// 1. Inicialización
async initializeSystem() {
  try {
    const response = await this.$http.post('/api/v1/auto-initialize/');
    this.$toast.success('Sistema inicializado correctamente');
    return response.data;
  } catch (error) {
    this.$toast.error('Error inicializando sistema');
  }
}

// 2. Predicción
async predictGrain(imageFile) {
  const formData = new FormData();
  formData.append('image', imageFile);
  
  try {
    const response = await this.$http.post('/api/v1/scan/measure/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  } catch (error) {
    this.$toast.error('Error en predicción');
  }
}
```

### **Angular**
```typescript
// 1. Inicialización
initializeSystem(): Observable<any> {
  return this.http.post('/api/v1/auto-initialize/', {});
}

// 2. Predicción
predictGrain(imageFile: File): Observable<any> {
  const formData = new FormData();
  formData.append('image', imageFile);
  
  return this.http.post('/api/v1/scan/measure/', formData);
}
```

## 🔧 **Configuración Automática**

### **Entrenamiento Automático**
- **Epochs**: 20 (configurable)
- **Batch Size**: 16
- **Learning Rate**: 0.001
- **Modelo**: ResNet18
- **Early Stopping**: 8 epochs de paciencia
- **Targets**: 4 modelos independientes (alto, ancho, grosor, peso)

### **Segmentación Automática**
- **Modelo**: YOLOv8-seg
- **Confianza**: 0.5
- **Crop Size**: 512x512
- **Formato**: PNG con transparencia

## 📊 **Métricas Esperadas**

### **Primera Inicialización**
- **Tiempo total**: 2-5 minutos (CPU) / 1-3 minutos (GPU)
- **Dataset**: Validación automática de CSV e imágenes
- **Crops**: Generación automática si no existen
- **Modelos**: Entrenamiento automático si no existen

### **Predicciones**
- **Tiempo de respuesta**: <5 segundos
- **Precisión**: MAE <2.0mm para dimensiones, MAE <0.5g para peso
- **Confianza**: >0.7 para predicciones buenas

## 🚨 **Manejo de Errores**

### **Si no hay modelos entrenados**
```json
{
  "error": "Modelos no disponibles. Ejecutar inicialización automática primero.",
  "status": "error",
  "suggestion": "POST /api/v1/auto-initialize/ para inicializar el sistema"
}
```

### **Si hay errores en inicialización**
```json
{
  "error": "Error en inicialización automática: [descripción]",
  "status": "error",
  "steps_completed": ["✅ Dataset validado", "❌ Error en crops"]
}
```

## 📁 **Estructura Automática**

```
backend/
├── media/
│   ├── datasets/
│   │   └── dataset_sin_comillas.csv  # Dataset automático
│   └── cacao_images/
│       ├── raw/                      # Imágenes originales
│       ├── crops/                    # Crops generados automáticamente
│       └── crops_runtime/            # Crops de predicciones
├── ml/
│   └── artifacts/
│       └── regressors/               # Modelos entrenados automáticamente
│           ├── alto.pt
│           ├── ancho.pt
│           ├── grosor.pt
│           ├── peso.pt
│           └── *_scaler.pkl
```

## 🎉 **Ventajas del Sistema Automático**

1. **Sin comandos manuales**: Todo desde el frontend
2. **Entrenamiento automático**: Modelos se entrenan solos
3. **Inicialización inteligente**: Solo hace lo que falta
4. **Manejo de errores**: Respuestas claras y sugerencias
5. **Documentación automática**: Swagger/ReDoc incluido
6. **Escalable**: Fácil de integrar en cualquier frontend

## 🚀 **Pasos para Implementar**

1. **Colocar datos**: CSV en `media/datasets/` e imágenes en `media/cacao_images/raw/`
2. **Iniciar Django**: `python manage.py runserver`
3. **Frontend llama**: `POST /api/v1/auto-initialize/` (primera vez)
4. **Sistema listo**: Usar `POST /api/v1/scan/measure/` para predicciones

## 📋 **Checklist de Implementación**

- ✅ Dataset CSV con formato correcto
- ✅ Imágenes .bmp nombradas por ID
- ✅ Django servidor ejecutándose
- ✅ Frontend configurado para llamar endpoints
- ✅ Inicialización automática ejecutada
- ✅ Sistema listo para predicciones

**¡El sistema CacaoScan está completamente automatizado y listo para usar desde el frontend!** 🎯
