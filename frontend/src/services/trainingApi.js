/**
 * Servicio API para entrenamiento de modelos ML
 * 
 * Principios aplicados:
 * - SRP: Solo responsabilidades de entrenamiento
 * - DRY: Funciones reutilizables
 * - KISS: Interfaces simples
 */

// Configuración base
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Configuración común para todas las peticiones
 * @returns {Object} Headers comunes
 */
const getCommonHeaders = () => ({
  'Content-Type': 'application/json'
  // TODO: Agregar token de autenticación cuando esté implementado
  // 'Authorization': `Bearer ${getAuthToken()}`
});

/**
 * Maneja respuestas HTTP de manera consistente (DRY)
 * @param {Response} response - Respuesta de fetch
 * @returns {Promise<Object>} Datos de respuesta o error
 */
const handleResponse = async (response) => {
  const contentType = response.headers.get('content-type');
  
  if (contentType && contentType.includes('application/json')) {
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.message || data.error || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return data;
  }
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  
  return await response.text();
};

// ==========================================
// ENTRENAMIENTO DE MODELOS ML
// ==========================================

/**
 * Envía datos de entrenamiento al backend
 * @param {FormData} formData - Datos del formulario con imágenes y métricas
 * @returns {Promise<Object>} Resultado del envío
 */
export const submitTrainingData = async (formData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ml/train/`, {
      method: 'POST',
      body: formData
      // No incluir Content-Type para FormData, el navegador lo maneja automáticamente
    });
    
    return await handleResponse(response);
  } catch (error) {
    console.error('Error enviando datos de entrenamiento:', error);
    throw error;
  }
};

/**
 * Obtiene estadísticas del dataset
 * @returns {Promise<Object>} Estadísticas del dataset
 */
export const getDatasetStats = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ml/dataset/stats/`, {
      method: 'GET',
      headers: getCommonHeaders()
    });
    
    return await handleResponse(response);
  } catch (error) {
    console.error('Error obteniendo estadísticas del dataset:', error);
    // Retornar datos mock en caso de error
    return {
      totalSamples: 0,
      avgWeight: 0,
      avgHeight: 0,
      lastUpdate: 'N/A'
    };
  }
};

/**
 * Obtiene muestras recientes del dataset
 * @param {Object} filters - Filtros para las muestras
 * @returns {Promise<Array>} Lista de muestras recientes
 */
export const getRecentSamples = async (filters = {}) => {
  try {
    const queryParams = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value);
      }
    });
    
    const url = `${API_BASE_URL}/api/ml/dataset/samples/?${queryParams}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: getCommonHeaders()
    });
    
    const data = await handleResponse(response);
    return data.results || [];
  } catch (error) {
    console.error('Error obteniendo muestras recientes:', error);
    // Retornar datos mock en caso de error
    return [];
  }
};

/**
 * Inicia entrenamiento de modelo
 * @param {Object} trainingConfig - Configuración del entrenamiento
 * @returns {Promise<Object>} Información del entrenamiento iniciado
 */
export const startModelTraining = async (trainingConfig) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ml/train/start/`, {
      method: 'POST',
      headers: getCommonHeaders(),
      body: JSON.stringify(trainingConfig)
    });
    
    return await handleResponse(response);
  } catch (error) {
    console.error('Error iniciando entrenamiento:', error);
    throw error;
  }
};

/**
 * Obtiene estado del entrenamiento
 * @param {string} trainingId - ID del entrenamiento
 * @returns {Promise<Object>} Estado del entrenamiento
 */
export const getTrainingStatus = async (trainingId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ml/train/status/${trainingId}/`, {
      method: 'GET',
      headers: getCommonHeaders()
    });
    
    return await handleResponse(response);
  } catch (error) {
    console.error('Error obteniendo estado del entrenamiento:', error);
    throw error;
  }
};

/**
 * Detiene un entrenamiento en curso
 * @param {string} trainingId - ID del entrenamiento
 * @returns {Promise<Object>} Resultado de la detención
 */
export const stopTraining = async (trainingId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ml/train/stop/${trainingId}/`, {
      method: 'POST',
      headers: getCommonHeaders()
    });
    
    return await handleResponse(response);
  } catch (error) {
    console.error('Error deteniendo entrenamiento:', error);
    throw error;
  }
};

/**
 * Obtiene métricas de un modelo entrenado
 * @param {string} modelId - ID del modelo
 * @returns {Promise<Object>} Métricas del modelo
 */
export const getModelMetrics = async (modelId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ml/models/${modelId}/metrics/`, {
      method: 'GET',
      headers: getCommonHeaders()
    });
    
    return await handleResponse(response);
  } catch (error) {
    console.error('Error obteniendo métricas del modelo:', error);
    throw error;
  }
};

/**
 * Descarga un modelo entrenado
 * @param {string} modelId - ID del modelo
 * @returns {Promise<Blob>} Archivo del modelo
 */
export const downloadModel = async (modelId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ml/models/${modelId}/download/`, {
      method: 'GET'
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.blob();
  } catch (error) {
    console.error('Error descargando modelo:', error);
    throw error;
  }
};

// ==========================================
// VALIDACIÓN DE DATOS
// ==========================================

/**
 * Valida una imagen de grano
 * @param {File} file - Archivo de imagen
 * @returns {Object} Resultado de validación
 */
export const validateGrainImage = (file) => {
  const errors = [];
  
  // Validar tipo de archivo
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff'];
  if (!validTypes.includes(file.type)) {
    errors.push('Formato no soportado. Use JPG, PNG, BMP o TIFF');
  }
  
  // Validar tamaño (máximo 20MB)
  const maxSize = 20 * 1024 * 1024;
  if (file.size > maxSize) {
    errors.push(`Archivo demasiado grande. Máximo ${Math.round(maxSize / (1024 * 1024))}MB`);
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Valida datos de dimensiones de grano
 * @param {Object} grainData - Datos del grano
 * @returns {Object} Resultado de validación
 */
export const validateGrainData = (grainData) => {
  const errors = [];
  
  // Validar ID del grano
  if (!grainData.grainId || grainData.grainId.trim() === '') {
    errors.push('ID del grano es requerido');
  }
  
  // Validar dimensiones
  const dimensions = ['height', 'width', 'thickness'];
  dimensions.forEach(dim => {
    if (!grainData[dim] || grainData[dim] <= 0) {
      errors.push(`${dim} debe ser mayor a 0`);
    }
    if (grainData[dim] > 100) {
      errors.push(`${dim} no puede ser mayor a 100mm`);
    }
  });
  
  // Validar peso
  if (!grainData.weight || grainData.weight <= 0) {
    errors.push('Peso debe ser mayor a 0');
  }
  if (grainData.weight > 50) {
    errors.push('Peso no puede ser mayor a 50g');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

// ==========================================
// UTILIDADES
// ==========================================

/**
 * Formatea tamaño de archivo de manera legible
 * @param {number} bytes - Tamaño en bytes
 * @returns {string} Tamaño formateado
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Formatea número con decimales específicos
 * @param {number} value - Valor a formatear
 * @param {number} decimals - Número de decimales
 * @returns {string} Número formateado
 */
export const formatNumber = (value, decimals = 2) => {
  if (value === null || value === undefined || isNaN(value)) return 'N/A';
  return parseFloat(value).toFixed(decimals);
};

/**
 * Configuración exportable para componentes
 */
export const TRAINING_CONFIG = {
  // Límites
  MAX_FILE_SIZE: 20 * 1024 * 1024,  // 20MB
  MAX_IMAGES_PER_BATCH: 50,          // Máximo imágenes por lote
  
  // Formatos soportados
  SUPPORTED_FORMATS: ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff'],
  
  // Intervalos de actualización (ms)
  STATUS_REFRESH_INTERVAL: 2000,     // 2 segundos
  STATS_REFRESH_INTERVAL: 30000,     // 30 segundos
  
  // Validaciones
  MAX_DIMENSION: 100,                 // mm
  MAX_WEIGHT: 50,                     // g
  MIN_DIMENSION: 0.1,                 // mm
  MIN_WEIGHT: 0.01                    // g
};

// Exportación por defecto con todas las funciones principales
export default {
  // Entrenamiento
  submitTrainingData,
  startModelTraining,
  getTrainingStatus,
  stopTraining,
  
  // Dataset
  getDatasetStats,
  getRecentSamples,
  
  // Modelos
  getModelMetrics,
  downloadModel,
  
  // Validación
  validateGrainImage,
  validateGrainData,
  
  // Utilidades
  formatFileSize,
  formatNumber,
  
  // Configuración
  TRAINING_CONFIG
};
