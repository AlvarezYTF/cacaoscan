/**
 * Servicio API para métricas de modelos
 * 
 * Maneja todas las operaciones relacionadas con métricas de modelos de ML:
 * - Registro y consulta de métricas
 * - Comparación de modelos
 * - Tendencias de rendimiento
 * - Gestión de modelos en producción
 */

import api from './api'

// Endpoints de la API
const API_ENDPOINTS = {
  list: '/model-metrics/',
  create: '/model-metrics/create/',
  detail: (id) => `/model-metrics/${id}/`,
  update: (id) => `/model-metrics/${id}/update/`,
  delete: (id) => `/model-metrics/${id}/delete/`,
  stats: '/model-metrics/stats/',
  trend: '/model-metrics/trend/',
  compare: '/model-metrics/compare/',
  best: '/model-metrics/best/',
  production: '/model-metrics/production/'
}

/**
 * Obtiene lista de métricas de modelos
 * @param {Object} params - Parámetros de consulta
 * @param {number} params.page - Página actual
 * @param {number} params.page_size - Tamaño de página
 * @param {string} params.model_type - Tipo de modelo ('regression', 'vision', 'yolo')
 * @param {string} params.ordering - Ordenamiento ('-created_at', 'accuracy', etc.)
 * @returns {Promise<Object>} - Lista paginada de métricas
 */
export async function getModelMetrics(params = {}) {
  try {
    console.log('📊 Obteniendo métricas de modelos:', params)

    const response = await api.get(API_ENDPOINTS.list, { params })

    console.log('✅ Métricas de modelos obtenidas:', {
      count: response.data.count || 0,
      results: response.data.results?.length || 0
    })

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error obteniendo métricas de modelos:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener las métricas de modelos'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Obtiene detalle de una métrica específica
 * @param {number} metricsId - ID de la métrica
 * @returns {Promise<Object>} - Detalle de la métrica
 */
export async function getModelMetricsDetail(metricsId) {
  try {
    if (!metricsId) {
      throw new Error('ID de métrica requerido')
    }

    console.log('🔍 Obteniendo detalle de métrica:', metricsId)

    const response = await api.get(API_ENDPOINTS.detail(metricsId))

    console.log('✅ Detalle de métrica obtenido')

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error obteniendo detalle de métrica:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener el detalle de la métrica'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Crea un nuevo registro de métricas
 * @param {Object} metricsData - Datos de las métricas
 * @param {string} metricsData.model_type - Tipo de modelo
 * @param {string} metricsData.model_version - Versión del modelo
 * @param {Object} metricsData.metrics - Métricas del modelo
 * @param {Object} metricsData.hyperparameters - Hiperparámetros utilizados
 * @param {string} metricsData.training_data_size - Tamaño del dataset de entrenamiento
 * @param {string} metricsData.notes - Notas adicionales
 * @returns {Promise<Object>} - Métrica creada
 */
export async function createModelMetrics(metricsData) {
  try {
    console.log('➕ Creando registro de métricas:', metricsData)

    const response = await api.post(API_ENDPOINTS.create, metricsData)

    console.log('✅ Métricas registradas exitosamente')

    return {
      success: true,
      data: response.data,
      message: 'Métricas registradas exitosamente'
    }

  } catch (error) {
    console.error('❌ Error creando métricas:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al registrar las métricas'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Actualiza un registro de métricas
 * @param {number} metricsId - ID de la métrica
 * @param {Object} updateData - Datos a actualizar
 * @returns {Promise<Object>} - Métrica actualizada
 */
export async function updateModelMetrics(metricsId, updateData) {
  try {
    if (!metricsId) {
      throw new Error('ID de métrica requerido')
    }

    console.log('✏️ Actualizando métricas:', metricsId)

    const response = await api.patch(API_ENDPOINTS.update(metricsId), updateData)

    console.log('✅ Métricas actualizadas exitosamente')

    return {
      success: true,
      data: response.data,
      message: 'Métricas actualizadas exitosamente'
    }

  } catch (error) {
    console.error('❌ Error actualizando métricas:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al actualizar las métricas'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Elimina un registro de métricas
 * @param {number} metricsId - ID de la métrica
 * @returns {Promise<Object>} - Resultado de la operación
 */
export async function deleteModelMetrics(metricsId) {
  try {
    if (!metricsId) {
      throw new Error('ID de métrica requerido')
    }

    console.log('🗑️ Eliminando métricas:', metricsId)

    await api.delete(API_ENDPOINTS.delete(metricsId))

    console.log('✅ Métricas eliminadas exitosamente')

    return {
      success: true,
      message: 'Métricas eliminadas exitosamente'
    }

  } catch (error) {
    console.error('❌ Error eliminando métricas:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al eliminar las métricas'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Obtiene estadísticas generales de métricas
 * @param {Object} params - Parámetros de consulta
 * @param {string} params.model_type - Filtrar por tipo de modelo
 * @returns {Promise<Object>} - Estadísticas de métricas
 */
export async function getModelMetricsStats(params = {}) {
  try {
    console.log('📊 Obteniendo estadísticas de métricas:', params)

    const response = await api.get(API_ENDPOINTS.stats, { params })

    console.log('✅ Estadísticas de métricas obtenidas')

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error obteniendo estadísticas de métricas:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener las estadísticas de métricas'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Obtiene tendencias de rendimiento de modelos
 * @param {Object} params - Parámetros de consulta
 * @param {string} params.model_type - Tipo de modelo
 * @param {string} params.metric_name - Nombre de la métrica ('accuracy', 'loss', 'mse', etc.)
 * @param {number} params.limit - Número de registros recientes
 * @returns {Promise<Object>} - Datos de tendencia
 */
export async function getModelPerformanceTrend(params = {}) {
  try {
    console.log('📈 Obteniendo tendencias de rendimiento:', params)

    const response = await api.get(API_ENDPOINTS.trend, { params })

    console.log('✅ Tendencias de rendimiento obtenidas')

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error obteniendo tendencias:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener las tendencias de rendimiento'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Compara múltiples modelos
 * @param {Array<number>} metricsIds - IDs de métricas a comparar
 * @returns {Promise<Object>} - Comparación de modelos
 */
export async function compareModels(metricsIds) {
  try {
    if (!metricsIds || metricsIds.length < 2) {
      throw new Error('Se requieren al menos 2 modelos para comparar')
    }

    console.log('⚖️ Comparando modelos:', metricsIds)

    const response = await api.post(API_ENDPOINTS.compare, {
      metrics_ids: metricsIds
    })

    console.log('✅ Comparación de modelos completada')

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error comparando modelos:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al comparar los modelos'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Obtiene los mejores modelos por tipo
 * @param {Object} params - Parámetros de consulta
 * @param {string} params.model_type - Tipo de modelo
 * @param {number} params.limit - Número de modelos a retornar (default: 5)
 * @param {string} params.metric - Métrica para ordenar ('accuracy', 'mse', etc.)
 * @returns {Promise<Object>} - Lista de mejores modelos
 */
export async function getBestModels(params = {}) {
  try {
    console.log('🏆 Obteniendo mejores modelos:', params)

    const response = await api.get(API_ENDPOINTS.best, { params })

    console.log('✅ Mejores modelos obtenidos')

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error obteniendo mejores modelos:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener los mejores modelos'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Obtiene modelos en producción
 * @returns {Promise<Object>} - Lista de modelos en producción
 */
export async function getProductionModels() {
  try {
    console.log('🚀 Obteniendo modelos en producción')

    const response = await api.get(API_ENDPOINTS.production)

    console.log('✅ Modelos en producción obtenidos')

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error obteniendo modelos en producción:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener los modelos en producción'

    return {
      success: false,
      error: errorMessage
    }
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
 * Métricas comunes por tipo de modelo
 */
export const COMMON_METRICS = {
  regression: [
    { key: 'mse', label: 'MSE (Error Cuadrático Medio)', format: 'decimal' },
    { key: 'mae', label: 'MAE (Error Absoluto Medio)', format: 'decimal' },
    { key: 'r2_score', label: 'R² Score', format: 'percentage' },
    { key: 'rmse', label: 'RMSE', format: 'decimal' }
  ],
  vision: [
    { key: 'accuracy', label: 'Precisión', format: 'percentage' },
    { key: 'loss', label: 'Loss', format: 'decimal' },
    { key: 'val_accuracy', label: 'Precisión de Validación', format: 'percentage' },
    { key: 'val_loss', label: 'Loss de Validación', format: 'decimal' }
  ],
  yolo: [
    { key: 'map', label: 'mAP (Mean Average Precision)', format: 'percentage' },
    { key: 'map50', label: 'mAP@50', format: 'percentage' },
    { key: 'map75', label: 'mAP@75', format: 'percentage' },
    { key: 'precision', label: 'Precisión', format: 'percentage' },
    { key: 'recall', label: 'Recall', format: 'percentage' }
  ]
}

/**
 * Valida datos de métricas antes de envío
 * @param {Object} metricsData - Datos a validar
 * @returns {Object} - Resultado de la validación
 */
export function validateMetricsData(metricsData) {
  const errors = []

  if (!metricsData.model_type) {
    errors.push('El tipo de modelo es requerido')
  } else if (!Object.values(MODEL_TYPES).includes(metricsData.model_type)) {
    errors.push('Tipo de modelo inválido')
  }

  if (!metricsData.model_version || metricsData.model_version.trim().length === 0) {
    errors.push('La versión del modelo es requerida')
  }

  if (!metricsData.metrics || Object.keys(metricsData.metrics).length === 0) {
    errors.push('Las métricas son requeridas')
  }

  if (metricsData.training_data_size && metricsData.training_data_size < 0) {
    errors.push('El tamaño del dataset debe ser mayor o igual a 0')
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}

/**
 * Formatea una métrica para visualización
 * @param {number} value - Valor de la métrica
 * @param {string} format - Formato ('decimal', 'percentage', 'integer')
 * @param {number} decimals - Número de decimales
 * @returns {string} - Valor formateado
 */
export function formatMetricValue(value, format = 'decimal', decimals = 4) {
  if (value === null || value === undefined || isNaN(value)) {
    return 'N/A'
  }

  switch (format) {
    case 'percentage':
      return `${(value * 100).toFixed(2)}%`
    case 'integer':
      return Math.round(value).toString()
    case 'decimal':
    default:
      return parseFloat(value).toFixed(decimals)
  }
}

/**
 * Calcula mejora porcentual entre dos métricas
 * @param {number} oldValue - Valor anterior
 * @param {number} newValue - Valor nuevo
 * @param {boolean} lowerIsBetter - True si valores menores son mejores (ej: loss, mse)
 * @returns {Object} - Información de mejora
 */
export function calculateImprovement(oldValue, newValue, lowerIsBetter = false) {
  if (!oldValue || !newValue) {
    return {
      improvement: 0,
      percentage: 0,
      improved: false,
      message: 'N/A'
    }
  }

  const diff = newValue - oldValue
  const percentage = (Math.abs(diff) / oldValue) * 100

  let improved
  if (lowerIsBetter) {
    improved = diff < 0 // Mejoró si el nuevo valor es menor
  } else {
    improved = diff > 0 // Mejoró si el nuevo valor es mayor
  }

  return {
    improvement: diff,
    percentage: percentage.toFixed(2),
    improved,
    message: improved 
      ? `Mejora del ${percentage.toFixed(2)}%`
      : `Reducción del ${percentage.toFixed(2)}%`
  }
}

/**
 * Exporta métricas a formato CSV
 * @param {Array} metrics - Array de métricas
 * @returns {string} - Contenido CSV
 */
export function exportMetricsToCSV(metrics) {
  if (!metrics || metrics.length === 0) {
    return ''
  }

  // Headers
  const headers = ['ID', 'Tipo', 'Versión', 'Fecha', 'Métricas', 'Hiperparámetros']
  let csv = headers.join(',') + '\n'

  // Rows
  metrics.forEach(metric => {
    const row = [
      metric.id,
      metric.model_type,
      metric.model_version,
      new Date(metric.created_at).toISOString(),
      JSON.stringify(metric.metrics).replace(/,/g, ';'),
      JSON.stringify(metric.hyperparameters).replace(/,/g, ';')
    ]
    csv += row.join(',') + '\n'
  })

  return csv
}

/**
 * Configuración del servicio
 */
export const MODEL_METRICS_CONFIG = {
  // Intervalo de actualización (ms)
  REFRESH_INTERVAL: 60000, // 1 minuto
  
  // Tamaño de página por defecto
  DEFAULT_PAGE_SIZE: 20,
  
  // Número máximo de modelos a comparar
  MAX_MODELS_TO_COMPARE: 5,
  
  // Colores por tipo de modelo
  MODEL_TYPE_COLORS: {
    regression: 'blue',
    vision: 'green',
    yolo: 'purple',
    segmentation: 'orange'
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
  getModelMetrics,
  getModelMetricsDetail,
  createModelMetrics,
  updateModelMetrics,
  deleteModelMetrics,
  getModelMetricsStats,
  getModelPerformanceTrend,
  compareModels,
  getBestModels,
  getProductionModels,
  validateMetricsData,
  formatMetricValue,
  calculateImprovement,
  exportMetricsToCSV,
  MODEL_TYPES,
  COMMON_METRICS,
  MODEL_METRICS_CONFIG
}

