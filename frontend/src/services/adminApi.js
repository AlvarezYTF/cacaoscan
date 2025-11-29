/**
 * Servicio API especializado para funciones administrativas avanzadas
 * 
 * Principios aplicados:
 * - SRP: Solo responsabilidades administrativas específicas
 * - DRY: Reutiliza funciones base de datasetApi pero extiende funcionalidad
 * - KISS: Interfaces simples para operaciones complejas
 */

// Importar funciones base para reutilizar (DRY)
import { 
  trainRegressionModel as baseTrainRegression,
  trainVisionModel as baseTrainVision,
  getTrainingJobStatus as baseGetJobStatus,
  getTrainingJobs as baseGetJobs,
  formatNumber
} from './datasetApi.js';

// Importar configuración centralizada del API
import { getApiBaseUrlWithPath } from '@/utils/apiConfig'

// Reutilizar utilidades del archivo base (DRY)
const API_BASE_URL = getApiBaseUrlWithPath();

// Funciones utilitarias simples para este módulo (KISS)
const makeRequest = async (url, options = {}) => {
  try {
    // Obtener token de autenticación
    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(url, {
      ...options,
      headers
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: response.statusText }));
      throw new Error(errorData.error || errorData.message || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error en petición a ${url}:`, error);
    throw error;
  }
};

// ==========================================
// GESTIÓN AVANZADA DE ENTRENAMIENTO (SRP)
// ==========================================

/**
 * Configuraciones predefinidas de entrenamiento (KISS)
 */
const TRAINING_PRESETS = {
  FAST: {
    name: 'Entrenamiento Rápido',
    description: 'Para pruebas rápidas y desarrollo',
    regression: {
      epochs: 20,
      learning_rate: 0.01,
      batch_size: 64,
      validation_split: 0.2,
      early_stopping: true
    },
    vision: {
      epochs: 15,
      learning_rate: 0.001,
      batch_size: 32,
      validation_split: 0.2,
      early_stopping: true
    }
  },
  STANDARD: {
    name: 'Entrenamiento Estándar',
    description: 'Configuración balanceada para uso general',
    regression: {
      epochs: 50,
      learning_rate: 0.001,
      batch_size: 32,
      validation_split: 0.2,
      early_stopping: true
    },
    vision: {
      epochs: 30,
      learning_rate: 0.0005,
      batch_size: 16,
      validation_split: 0.2,
      early_stopping: true
    }
  },
  PRODUCTION: {
    name: 'Entrenamiento de Producción',
    description: 'Máxima calidad para modelos en producción',
    regression: {
      epochs: 100,
      learning_rate: 0.0005,
      batch_size: 16,
      validation_split: 0.15,
      early_stopping: false
    },
    vision: {
      epochs: 50,
      learning_rate: 0.0001,
      batch_size: 8,
      validation_split: 0.15,
      early_stopping: false
    }
  },
  CUSTOM: {
    name: 'Configuración Personalizada',
    description: 'Parámetros definidos por el usuario'
  }
};

/**
 * Filtros avanzados para selección de datos de entrenamiento (DRY)
 */
const DATA_FILTERS = {
  QUALITY_LEVELS: {
    ALL: { min_quality_score: 0.0, label: 'Todos los datos' },
    HIGH: { min_quality_score: 0.8, label: 'Solo alta calidad (>80%)' },
    MEDIUM: { min_quality_score: 0.6, label: 'Calidad media y alta (>60%)' },
    EXCLUDE_POOR: { exclude_poor_quality: true, label: 'Excluir calidad pobre' }
  },
  DATA_TYPES: {
    ALL: { label: 'Todos los tipos' },
    PROCESSED_ONLY: { only_processed: true, label: 'Solo datos procesados' },
    MANUAL_ONLY: { only_manual_verified: true, label: 'Solo verificados manualmente' },
    EXCLUDE_DEFECTIVE: { exclude_defective: true, label: 'Excluir defectuosos' }
  },
  TIME_RANGES: {
    ALL: { label: 'Todos los períodos' },
    LAST_MONTH: { days_back: 30, label: 'Último mes' },
    LAST_3_MONTHS: { days_back: 90, label: 'Últimos 3 meses' },
    LAST_6_MONTHS: { days_back: 180, label: 'Últimos 6 meses' },
    CUSTOM: { label: 'Rango personalizado' }
  }
};

/**
 * Inicia entrenamiento con configuración avanzada (SRP)
 * @param {string} modelType - 'regression' | 'vision'
 * @param {Object} config - Configuración de entrenamiento
 * @param {Object} dataFilters - Filtros de datos
 * @param {Object} experimentData - Información del experimento
 * @returns {Promise<Object>} Job de entrenamiento iniciado
 */
const startAdvancedTraining = async (modelType, config, dataFilters = {}, experimentData = {}) => {
  try {
    // Combinar configuración con filtros de datos (DRY)
    const trainingParams = {
      ...config,
      ...dataFilters,
      // Metadatos del experimento
      experiment_name: experimentData.name || `${modelType}_${new Date().toISOString().split('T')[0]}`,
      experiment_description: experimentData.description || '',
      experiment_tags: experimentData.tags || [],
      // Configuraciones adicionales
      save_checkpoints: true,
      tensorboard_logging: true,
      model_versioning: true
    };
    
    console.log(`Iniciando entrenamiento avanzado de ${modelType}:`, trainingParams);
    
    // Usar funciones base pero con parámetros extendidos (DRY)
    if (modelType === 'regression') {
      return await baseTrainRegression(trainingParams);
    } else if (modelType === 'vision') {
      return await baseTrainVision(trainingParams);
    } else {
      throw new Error(`Tipo de modelo no soportado: ${modelType}`);
    }
    
  } catch (error) {
    console.error('Error en entrenamiento avanzado:', error);
    throw error;
  }
};

/**
 * Obtiene historial completo de entrenamientos con filtros (SRP)
 * @param {Object} filters - Filtros para el historial
 * @returns {Promise<Array>} Lista de entrenamientos históricos
 */
const getTrainingHistory = async (filters = {}) => {
  try {
    // Obtener token de autenticación
    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    
    // Construir parámetros de consulta
    const queryParams = new URLSearchParams();
    if (filters.model_type) queryParams.append('job_type', filters.model_type);
    if (filters.status) queryParams.append('status', filters.status);
    
    // API_BASE_URL ya incluye /api/v1, no duplicar
    const url = `${API_BASE_URL}/train/jobs/?${queryParams}`;
    
    const headers = {
      'Content-Type': 'application/json'
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(url, {
      method: 'GET',
      headers
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: response.statusText }));
      throw new Error(errorData.error || errorData.message || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    // Retornar los resultados (el backend ya aplica filtros)
    return data.results || data || [];
    
  } catch (error) {
    console.error('Error obteniendo historial de entrenamiento:', error);
    throw error;
  }
};

/**
 * Obtiene estado detallado de múltiples jobs (DRY)
 * @param {Array<string>} jobIds - IDs de los jobs
 * @returns {Promise<Array>} Estados de los jobs
 */
const getMultipleJobStatus = async (jobIds) => {
  try {
    const statusPromises = jobIds.map(jobId => baseGetJobStatus(jobId));
    const results = await Promise.allSettled(statusPromises);
    
    return results.map((result, index) => ({
      job_id: jobIds[index],
      success: result.status === 'fulfilled',
      data: result.status === 'fulfilled' ? result.value : null,
      error: result.status === 'rejected' ? result.reason.message : null
    }));
    
  } catch (error) {
    console.error('Error obteniendo estados múltiples:', error);
    throw error;
  }
};

/**
 * Cancela un job de entrenamiento (SRP)
 * @param {string} jobId - ID del job a cancelar
 * @returns {Promise<Object>} Resultado de la cancelación
 */
const cancelTrainingJob = async (jobId) => {
  try {
    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    
    const headers = {
      'Content-Type': 'application/json'
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    // API_BASE_URL ya incluye /api/v1
    const url = `${API_BASE_URL}/train/jobs/${jobId}/cancel/`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: response.statusText }));
      throw new Error(errorData.error || errorData.message || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error cancelando job:', error);
    throw error;
  }
};

/**
 * Obtiene métricas detalladas de un modelo entrenado (SRP)
 * @param {string} jobId - ID del job completado
 * @returns {Promise<Object>} Métricas del modelo
 */
const getModelMetrics = async (jobId) => {
  try {
    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    
    const headers = {
      'Content-Type': 'application/json'
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    // API_BASE_URL ya incluye /api/v1
    const url = `${API_BASE_URL}/train/jobs/${jobId}/metrics/`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: response.statusText }));
      throw new Error(errorData.error || errorData.message || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error obteniendo métricas:', error);
    throw error;
  }
};

/**
 * Compara múltiples modelos entrenados (SRP)
 * @param {Array<string>} jobIds - IDs de los jobs a comparar
 * @returns {Promise<Object>} Comparación de modelos
 */
const compareModels = async (jobIds) => {
  try {
    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    
    const headers = {
      'Content-Type': 'application/json'
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    // API_BASE_URL ya incluye /api/v1
    const url = `${API_BASE_URL}/train/jobs/compare/`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify({ job_ids: jobIds })
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: response.statusText }));
      throw new Error(errorData.error || errorData.message || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error comparando modelos:', error);
    throw error;
  }
};

// ==========================================
// GESTIÓN DE EXPERIMENTOS (SRP)
// ==========================================

/**
 * Crea un nuevo experimento de entrenamiento (SRP)
 * @param {Object} experimentData - Datos del experimento
 * @returns {Promise<Object>} Experimento creado
 */
const createExperiment = async (experimentData) => {
  try {
    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    
    const headers = {
      'Content-Type': 'application/json'
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const url = `${API_BASE_URL}/images/admin/experiments/`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(experimentData)
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: response.statusText }));
      throw new Error(errorData.error || errorData.message || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error creando experimento:', error);
    throw error;
  }
};

/**
 * Obtiene lista de experimentos (SRP)
 * @param {Object} filters - Filtros para experimentos
 * @returns {Promise<Array>} Lista de experimentos
 */
const getExperiments = async (filters = {}) => {
  try {
    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    
    const headers = {
      'Content-Type': 'application/json'
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value);
      }
    });
    
    const url = `${API_BASE_URL}/images/admin/experiments/?${params}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: response.statusText }));
      throw new Error(errorData.error || errorData.message || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error obteniendo experimentos:', error);
    throw error;
  }
};

// ==========================================
// UTILIDADES Y VALIDACIONES (DRY)
// ==========================================

/**
 * Valida configuración de entrenamiento (KISS)
 * @param {string} modelType - Tipo de modelo
 * @param {Object} config - Configuración a validar
 * @returns {Object} Resultado de validación
 */
const validateTrainingConfig = (modelType, config) => {
  const errors = [];
  
  // Validaciones básicas
  if (!config.epochs || config.epochs < 1 || config.epochs > 1000) {
    errors.push('Épocas debe estar entre 1 y 1000');
  }
  
  if (!config.learning_rate || config.learning_rate <= 0 || config.learning_rate > 1) {
    errors.push('Learning rate debe estar entre 0 y 1');
  }
  
  if (!config.batch_size || config.batch_size < 1 || config.batch_size > 256) {
    errors.push('Batch size debe estar entre 1 y 256');
  }
  
  if (config.validation_split && (config.validation_split <= 0 || config.validation_split >= 1)) {
    errors.push('Validation split debe estar entre 0 y 1');
  }
  
  // Validaciones específicas por tipo de modelo
  if (modelType === 'vision') {
    if (config.batch_size > 64) {
      errors.push('Para modelos de visión, el batch size recomendado es máximo 64');
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Estima tiempo de entrenamiento (KISS)
 * @param {string} modelType - Tipo de modelo
 * @param {Object} config - Configuración de entrenamiento
 * @param {number} datasetSize - Tamaño del dataset
 * @returns {Object} Estimación de tiempo
 */
const estimateTrainingTime = (modelType, config, datasetSize) => {
  // Factores base por tipo de modelo (estimaciones aproximadas)
  const timeFactors = {
    regression: 0.1, // 0.1 segundos por época por 1000 muestras
    vision: 2.0      // 2 segundos por época por 1000 muestras
  };
  
  const factor = timeFactors[modelType] || 1.0;
  const epochsPerBatch = Math.ceil(datasetSize / config.batch_size);
  const estimatedSecondsPerEpoch = (epochsPerBatch * factor * datasetSize) / 1000;
  const totalSeconds = estimatedSecondsPerEpoch * config.epochs;
  
  // Convertir a formato legible
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = Math.floor(totalSeconds % 60);
  
  return {
    totalSeconds: Math.round(totalSeconds),
    formatted: (() => {
      if (hours > 0) {
        return `${hours}h ${minutes}m ${seconds}s`
      } else if (minutes > 0) {
        return `${minutes}m ${seconds}s`
      }
      return `${seconds}s`
    })(),
    estimatedCompletion: new Date(Date.now() + totalSeconds * 1000)
  };
};

/**
 * Formatea métricas de entrenamiento avanzadas para visualización (DRY)
 * @param {Object} metrics - Métricas brutas
 * @returns {Object} Métricas formateadas
 */
const formatAdvancedTrainingMetrics = (metrics) => {
  return {
    // Métricas principales (usando función importada)
    loss: formatNumber(metrics.final_loss, 4),
    accuracy: formatNumber(metrics.final_accuracy, 4),
    val_loss: formatNumber(metrics.final_val_loss, 4),
    val_accuracy: formatNumber(metrics.final_val_accuracy, 4),
    
    // Métricas específicas por tipo
    r2_score: formatNumber(metrics.r2_score, 4),
    mse: formatNumber(metrics.mse, 4),
    mae: formatNumber(metrics.mae, 4),
    
    // Información de entrenamiento
    total_epochs: metrics.total_epochs || 0,
    training_time: metrics.training_time || 0,
    best_epoch: metrics.best_epoch || 0,
    
    // Estado
    converged: metrics.converged || false,
    early_stopped: metrics.early_stopped || false
  };
};

/**
 * Configuración exportable para componentes (KISS)
 */
const ADMIN_TRAINING_CONFIG = {
  // Intervalos de actualización
  STATUS_REFRESH_INTERVAL: 2000,   // 2 segundos
  METRICS_REFRESH_INTERVAL: 5000,  // 5 segundos
  
  // Límites
  MAX_CONCURRENT_JOBS: 3,
  MAX_EXPERIMENT_NAME_LENGTH: 100,
  MAX_DESCRIPTION_LENGTH: 500,
  
  // Colores para estados
  STATUS_COLORS: {
    pending: 'yellow',
    running: 'blue', 
    completed: 'green',
    failed: 'red',
    cancelled: 'gray'
  },
  
  // Iconos para tipos de modelo
  MODEL_ICONS: {
    regression: 'chart-line',
    vision: 'eye'
  }
};

/**
 * Inicia entrenamiento ML usando el endpoint simplificado /api/v1/ml/train/
 * Esta función usa la configuración mejorada (150 épocas, validación de crops, etc.)
 * @param {Object} config - Configuración opcional del entrenamiento
 * @returns {Promise<Object>} Job de entrenamiento iniciado
 */
const startMLTraining = async (config = {}) => {
  try {
    // Obtener token de autenticación del localStorage
    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    
    const headers = {
      'Content-Type': 'application/json'
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Configuración por defecto con las mejoras implementadas
    const defaultConfig = {
      job_type: 'regression',
      model_name: 'cacao_regression_models',
      dataset_size: 0, // Se calculará automáticamente
      epochs: 150, // 150 épocas para mejor aprendizaje
      batch_size: 16,
      learning_rate: 0.001,
      config_params: {
        multi_head: false,
        model_type: 'resnet18',
        img_size: 224,
        early_stopping_patience: 25,
        // Mejoras avanzadas
        scheduler_type: 'cosine_warmup',
        warmup_epochs: 10,
        loss_type: 'huber',
        max_grad_norm: 1.0,
        use_advanced_augmentation: true,
        validate_crops_quality: true,
        regenerate_bad_crops: true,
        improvement_threshold: 1e-5,
        min_epochs: 50
      }
    };
    
    // Combinar con configuración proporcionada
    const trainingConfig = {
      ...defaultConfig,
      ...config,
      config_params: {
        ...defaultConfig.config_params,
        ...(config.config_params || {})
      }
    };
    
    console.log('Iniciando entrenamiento ML con configuración mejorada:', trainingConfig);
    
    const response = await fetch(`${API_BASE_URL}/ml/train/`, {
      method: 'POST',
      headers,
      body: JSON.stringify(trainingConfig)
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Error desconocido' }));
      throw new Error(errorData.error || errorData.message || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Entrenamiento iniciado exitosamente:', data);
    return data;
    
  } catch (error) {
    console.error('Error iniciando entrenamiento ML:', error);
    throw error;
  }
};

// Re-exportar funciones base necesarias para compatibilidad (DRY)
export { 
  baseTrainRegression as trainRegressionModel,
  baseTrainVision as trainVisionModel,
  baseGetJobStatus as getTrainingJobStatus,
  baseGetJobs as getTrainingJobs
};

// Exportar funciones avanzadas
export {
  startAdvancedTraining,
  startMLTraining,
  getTrainingHistory,
  getMultipleJobStatus,
  cancelTrainingJob,
  getModelMetrics,
  compareModels,
  createExperiment,
  getExperiments,
  validateTrainingConfig,
  estimateTrainingTime,
  formatAdvancedTrainingMetrics
};

// Exportar configuraciones
export {
  TRAINING_PRESETS,
  DATA_FILTERS,
  ADMIN_TRAINING_CONFIG
};

// Exportación por defecto con funciones principales
export default {
  // Entrenamiento avanzado
  startAdvancedTraining,
  startMLTraining,
  getTrainingHistory,
  getMultipleJobStatus,
  cancelTrainingJob,
  getModelMetrics,
  compareModels,
  
  // Experimentos
  createExperiment,
  getExperiments,
  
  // Utilidades
  validateTrainingConfig,
  estimateTrainingTime,
  formatAdvancedTrainingMetrics,
  
  // Re-exportación de funciones base
  trainRegressionModel: baseTrainRegression,
  trainVisionModel: baseTrainVision,
  getTrainingJobStatus: baseGetJobStatus,
  getTrainingJobs: baseGetJobs
  
  // Nota: TRAINING_PRESETS, DATA_FILTERS y ADMIN_TRAINING_CONFIG 
  // están disponibles como named exports arriba
};
