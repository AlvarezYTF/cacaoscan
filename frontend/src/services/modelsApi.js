/**
 * Servicio API para gestión de estado de modelos
 * 
 * Maneja todas las operaciones relacionadas con el estado y gestión de modelos ML:
 * - Estado de modelos cargados
 * - Carga y descarga de modelos
 * - Validación de dataset
 * - Inicialización automática
 */

import api from './api'

// Endpoints de la API
const API_ENDPOINTS = {
  status: '/models/status/',
  load: '/models/load/',
  datasetValidation: '/dataset/validation/',
  autoInitialize: '/auto-initialize/'
}

/**
 * Obtiene el estado actual de los modelos cargados en el sistema
 * @returns {Promise<Object>} - Estado de los modelos
 */
export async function getModelsStatus() {
  try {
    console.log('🔍 Obteniendo estado de modelos')

    const response = await api.get(API_ENDPOINTS.status)

    console.log('✅ Estado de modelos obtenido:', response.data)

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error obteniendo estado de modelos:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener el estado de los modelos'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Carga los modelos en memoria
 * @param {Object} options - Opciones de carga
 * @param {boolean} options.force_reload - Forzar recarga de modelos
 * @param {Array<string>} options.model_types - Tipos de modelos a cargar ['regression', 'vision', 'yolo']
 * @returns {Promise<Object>} - Resultado de la carga
 */
export async function loadModels(options = {}) {
  try {
    console.log('📥 Cargando modelos:', options)

    // Emitir evento de loading
    window.dispatchEvent(new CustomEvent('api-loading-start', {
      detail: { type: 'models-loading', message: 'Cargando modelos...' }
    }))

    const response = await api.post(API_ENDPOINTS.load, options, {
      timeout: 120000 // 2 minutos para carga de modelos
    })

    console.log('✅ Modelos cargados exitosamente:', response.data)

    return {
      success: true,
      data: response.data,
      message: 'Modelos cargados exitosamente'
    }

  } catch (error) {
    console.error('❌ Error cargando modelos:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al cargar los modelos'

    return {
      success: false,
      error: errorMessage
    }
  } finally {
    window.dispatchEvent(new CustomEvent('api-loading-end'))
  }
}

/**
 * Valida el dataset para entrenamiento
 * @param {Object} validationOptions - Opciones de validación
 * @param {string} validationOptions.dataset_path - Ruta del dataset (opcional)
 * @param {boolean} validationOptions.check_integrity - Verificar integridad
 * @param {boolean} validationOptions.check_balance - Verificar balance de clases
 * @returns {Promise<Object>} - Resultado de la validación
 */
export async function validateDataset(validationOptions = {}) {
  try {
    console.log('🔍 Validando dataset:', validationOptions)

    // Emitir evento de loading
    window.dispatchEvent(new CustomEvent('api-loading-start', {
      detail: { type: 'dataset-validation', message: 'Validando dataset...' }
    }))

    const response = await api.post(API_ENDPOINTS.datasetValidation, validationOptions, {
      timeout: 60000 // 1 minuto
    })

    console.log('✅ Validación de dataset completada:', response.data)

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error validando dataset:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al validar el dataset'

    return {
      success: false,
      error: errorMessage
    }
  } finally {
    window.dispatchEvent(new CustomEvent('api-loading-end'))
  }
}

/**
 * Inicializa automáticamente el sistema completo
 * @param {Object} options - Opciones de inicialización
 * @param {boolean} options.load_models - Cargar modelos
 * @param {boolean} options.validate_dataset - Validar dataset
 * @param {boolean} options.check_dependencies - Verificar dependencias
 * @returns {Promise<Object>} - Resultado de la inicialización
 */
export async function autoInitialize(options = {}) {
  try {
    console.log('🚀 Inicializando sistema automáticamente:', options)

    // Emitir evento de loading
    window.dispatchEvent(new CustomEvent('api-loading-start', {
      detail: { type: 'auto-initialize', message: 'Inicializando sistema...' }
    }))

    const response = await api.post(API_ENDPOINTS.autoInitialize, options, {
      timeout: 180000 // 3 minutos para inicialización completa
    })

    console.log('✅ Sistema inicializado exitosamente:', response.data)

    return {
      success: true,
      data: response.data,
      message: 'Sistema inicializado exitosamente'
    }

  } catch (error) {
    console.error('❌ Error inicializando sistema:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al inicializar el sistema'

    return {
      success: false,
      error: errorMessage
    }
  } finally {
    window.dispatchEvent(new CustomEvent('api-loading-end'))
  }
}

/**
 * Tipos de modelos soportados
 */
export const MODEL_TYPES = {
  REGRESSION: 'regression',
  VISION: 'vision',
  YOLO: 'yolo',
  SEGMENTATION: 'segmentation'
}

/**
 * Estados posibles de los modelos
 */
export const MODEL_STATUS = {
  NOT_LOADED: 'not_loaded',
  LOADING: 'loading',
  LOADED: 'loaded',
  ERROR: 'error'
}

/**
 * Verifica si un modelo específico está cargado
 * @param {Object} modelsStatus - Estado de modelos
 * @param {string} modelType - Tipo de modelo a verificar
 * @returns {boolean} - True si el modelo está cargado
 */
export function isModelLoaded(modelsStatus, modelType) {
  if (!modelsStatus || !modelsStatus.models) {
    return false
  }

  const model = modelsStatus.models[modelType]
  return model && model.status === MODEL_STATUS.LOADED
}

/**
 * Obtiene información detallada de un modelo
 * @param {Object} modelsStatus - Estado de modelos
 * @param {string} modelType - Tipo de modelo
 * @returns {Object} - Información del modelo
 */
export function getModelInfo(modelsStatus, modelType) {
  if (!modelsStatus || !modelsStatus.models) {
    return {
      loaded: false,
      status: MODEL_STATUS.NOT_LOADED,
      message: 'No se pudo obtener información del modelo'
    }
  }

  const model = modelsStatus.models[modelType]
  if (!model) {
    return {
      loaded: false,
      status: MODEL_STATUS.NOT_LOADED,
      message: 'Modelo no encontrado'
    }
  }

  return {
    loaded: model.status === MODEL_STATUS.LOADED,
    status: model.status,
    version: model.version || 'N/A',
    path: model.path || 'N/A',
    loaded_at: model.loaded_at,
    message: model.message || 'Modelo disponible'
  }
}

/**
 * Verifica si todos los modelos están cargados
 * @param {Object} modelsStatus - Estado de modelos
 * @returns {boolean} - True si todos los modelos están cargados
 */
export function areAllModelsLoaded(modelsStatus) {
  if (!modelsStatus || !modelsStatus.models) {
    return false
  }

  const requiredModels = [MODEL_TYPES.REGRESSION, MODEL_TYPES.VISION, MODEL_TYPES.YOLO]
  return requiredModels.every(modelType => isModelLoaded(modelsStatus, modelType))
}

/**
 * Formatea el estado de modelos para visualización
 * @param {Object} modelsStatus - Estado de modelos
 * @returns {Array} - Array de modelos formateados
 */
export function formatModelsStatus(modelsStatus) {
  if (!modelsStatus || !modelsStatus.models) {
    return []
  }

  return Object.entries(modelsStatus.models).map(([type, model]) => ({
    type,
    name: getModelTypeName(type),
    status: model.status,
    loaded: model.status === MODEL_STATUS.LOADED,
    version: model.version || 'N/A',
    path: model.path,
    loaded_at: model.loaded_at,
    error: model.error,
    // Información visual
    status_color: getStatusColor(model.status),
    status_icon: getStatusIcon(model.status),
    status_text: getStatusText(model.status)
  }))
}

/**
 * Obtiene el nombre legible del tipo de modelo
 * @param {string} modelType - Tipo de modelo
 * @returns {string} - Nombre legible
 */
function getModelTypeName(modelType) {
  const names = {
    [MODEL_TYPES.REGRESSION]: 'Modelo de Regresión',
    [MODEL_TYPES.VISION]: 'Modelo de Visión',
    [MODEL_TYPES.YOLO]: 'Modelo YOLO',
    [MODEL_TYPES.SEGMENTATION]: 'Modelo de Segmentación'
  }
  return names[modelType] || modelType
}

/**
 * Obtiene el color del estado
 * @param {string} status - Estado del modelo
 * @returns {string} - Color
 */
function getStatusColor(status) {
  const colors = {
    [MODEL_STATUS.NOT_LOADED]: 'gray',
    [MODEL_STATUS.LOADING]: 'blue',
    [MODEL_STATUS.LOADED]: 'green',
    [MODEL_STATUS.ERROR]: 'red'
  }
  return colors[status] || 'gray'
}

/**
 * Obtiene el icono del estado
 * @param {string} status - Estado del modelo
 * @returns {string} - Icono
 */
function getStatusIcon(status) {
  const icons = {
    [MODEL_STATUS.NOT_LOADED]: 'circle',
    [MODEL_STATUS.LOADING]: 'spinner',
    [MODEL_STATUS.LOADED]: 'check-circle',
    [MODEL_STATUS.ERROR]: 'exclamation-circle'
  }
  return icons[status] || 'circle'
}

/**
 * Obtiene el texto del estado
 * @param {string} status - Estado del modelo
 * @returns {string} - Texto
 */
function getStatusText(status) {
  const texts = {
    [MODEL_STATUS.NOT_LOADED]: 'No cargado',
    [MODEL_STATUS.LOADING]: 'Cargando...',
    [MODEL_STATUS.LOADED]: 'Cargado',
    [MODEL_STATUS.ERROR]: 'Error'
  }
  return texts[status] || status
}

/**
 * Valida opciones de carga de modelos
 * @param {Object} options - Opciones a validar
 * @returns {Object} - Resultado de la validación
 */
export function validateLoadOptions(options) {
  const errors = []

  if (options.model_types && !Array.isArray(options.model_types)) {
    errors.push('model_types debe ser un array')
  }

  if (options.model_types) {
    const validTypes = Object.values(MODEL_TYPES)
    const invalidTypes = options.model_types.filter(type => !validTypes.includes(type))
    
    if (invalidTypes.length > 0) {
      errors.push(`Tipos de modelo inválidos: ${invalidTypes.join(', ')}`)
    }
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}

/**
 * Analiza resultados de validación de dataset
 * @param {Object} validationResult - Resultado de la validación
 * @returns {Object} - Análisis estructurado
 */
export function analyzeDatasetValidation(validationResult) {
  if (!validationResult || !validationResult.data) {
    return {
      valid: false,
      issues: ['No se pudo analizar el resultado de validación'],
      summary: 'Error en validación'
    }
  }

  const data = validationResult.data
  const issues = []
  let valid = true

  // Verificar integridad
  if (data.integrity_check === false) {
    valid = false
    issues.push('Problemas de integridad en el dataset')
  }

  // Verificar balance
  if (data.balance_check === false) {
    issues.push('Dataset desbalanceado')
  }

  // Verificar tamaño mínimo
  if (data.total_samples < 100) {
    issues.push(`Dataset muy pequeño (${data.total_samples} muestras, recomendado: >100)`)
  }

  // Verificar archivos corruptos
  if (data.corrupted_files && data.corrupted_files.length > 0) {
    valid = false
    issues.push(`${data.corrupted_files.length} archivo(s) corrupto(s)`)
  }

  return {
    valid,
    issues,
    summary: valid 
      ? 'Dataset válido y listo para usar'
      : 'Dataset requiere correcciones',
    details: {
      total_samples: data.total_samples || 0,
      corrupted_files: data.corrupted_files || [],
      balance_ratio: data.balance_ratio || 'N/A',
      recommendations: data.recommendations || []
    }
  }
}

/**
 * Configuración del servicio de modelos
 */
export const MODELS_CONFIG = {
  // Intervalo de actualización de estado (ms)
  STATUS_REFRESH_INTERVAL: 30000, // 30 segundos
  
  // Timeout para operaciones de carga (ms)
  LOAD_TIMEOUT: 120000, // 2 minutos
  
  // Timeout para inicialización (ms)
  INIT_TIMEOUT: 180000, // 3 minutos
  
  // Colores por estado
  STATUS_COLORS: {
    not_loaded: 'gray',
    loading: 'blue',
    loaded: 'green',
    error: 'red'
  },
  
  // Iconos por tipo de modelo
  MODEL_TYPE_ICONS: {
    regression: 'chart-line',
    vision: 'eye',
    yolo: 'brain',
    segmentation: 'layer-group'
  }
}

// Exportación por defecto
export default {
  getModelsStatus,
  loadModels,
  validateDataset,
  autoInitialize,
  isModelLoaded,
  getModelInfo,
  areAllModelsLoaded,
  formatModelsStatus,
  validateLoadOptions,
  analyzeDatasetValidation,
  MODEL_TYPES,
  MODEL_STATUS,
  MODELS_CONFIG
}

