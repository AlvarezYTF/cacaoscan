/**
 * Servicio API para gestión administrativa de datasets
 * 
 * Principios aplicados:
 * - DRY: Funciones reutilizables con lógica centralizada
 * - KISS: Interface simple y directa
 * - SRP: Una responsabilidad por función
 */

/**
 * Servicio API para gestión administrativa de datasets
 * Usa apiClient para reducir duplicación de código
 * Mantiene fetch directo para operaciones con FormData
 */
import { fetchGet, fetchPost, fetchPatch, fetchDelete } from './apiClient'
import { validateImageFileSingleError } from '@/utils/imageValidationUtils'
import { getApiBaseUrlWithoutPath } from '@/utils/apiConfig'

// Configuración base reutilizable
const API_BASE_URL = getApiBaseUrlWithoutPath();

// ==========================================
// GESTIÓN DE IMÁGENES DE DATASET
// ==========================================

/**
 * Obtiene lista completa de imágenes (admin)
 * @param {Object} filters - Filtros de búsqueda
 * @param {number} page - Número de página
 * @param {number} pageSize - Tamaño de página
 * @returns {Promise<Object>} Lista paginada de imágenes
 */
export const getDatasetImages = async (filters = {}, page = 1, pageSize = 20) => {
  const params = {
    ...filters,
    page,
    page_size: pageSize
  }
  return await fetchGet('/api/images/admin/images/', params)
}

/**
 * Obtiene detalles de una imagen específica
 * @param {number} imageId - ID de la imagen
 * @returns {Promise<Object>} Detalles de la imagen
 */
export const getDatasetImage = async (imageId) => {
  return await fetchGet(`/api/images/admin/images/${imageId}/`)
}

/**
 * Actualiza una imagen del dataset
 * @param {number} imageId - ID de la imagen
 * @param {Object} updateData - Datos a actualizar
 * @returns {Promise<Object>} Imagen actualizada
 */
export const updateDatasetImage = async (imageId, updateData) => {
  return await fetchPatch(`/api/images/admin/images/${imageId}/`, updateData)
}

/**
 * Elimina una imagen del dataset
 * @param {number} imageId - ID de la imagen
 * @returns {Promise<void>}
 */
export const deleteDatasetImage = async (imageId) => {
  await fetchDelete(`/api/images/admin/images/${imageId}/`)
}

/**
 * Actualización masiva de imágenes
 * @param {Array<number>} imageIds - IDs de imágenes a actualizar
 * @param {Object} updateData - Datos a aplicar
 * @returns {Promise<Object>} Resultado de la operación
 */
export const bulkUpdateDatasetImages = async (imageIds, updateData) => {
  return await fetchPost('/api/images/admin/images/bulk-update/', {
    image_ids: imageIds,
    ...updateData
  })
}

// ==========================================
// SUBIDA Y GESTIÓN DE ARCHIVOS
// ==========================================

/**
 * Sube nuevas imágenes al dataset
 * @param {FileList|Array<File>} files - Archivos a subir
 * @param {Object} metadata - Metadatos comunes
 * @param {Function} onProgress - Callback de progreso (opcional)
 * @returns {Promise<Array>} Resultados de subida
 */
export const uploadDatasetImages = async (files, metadata = {}, onProgress = null) => {
  const results = [];
  const fileArray = Array.from(files);
  
  for (let i = 0; i < fileArray.length; i++) {
    const file = fileArray[i];
    
    try {
      // Validar archivo
      const validation = validateImageFileSingleError(file);
      if (!validation.isValid) {
        results.push({
          file: file.name,
          success: false,
          error: validation.error
        });
        continue;
      }
      
      // Crear FormData
      const formData = new FormData();
      formData.append('image', file);
      
      // Agregar metadatos
      for (const [key, value] of Object.entries(metadata)) {
        if (value !== undefined && value !== null && value !== '') {
          formData.append(key, value);
        }
      }
      
      // Subir archivo
      const response = await fetch(`${API_BASE_URL}/api/images/predict/`, {
        method: 'POST',
        body: formData
      });
      
      const result = await handleResponse(response);
      
      results.push({
        file: file.name,
        success: true,
        data: result
      });
      
      // Reportar progreso
      if (onProgress) {
        onProgress({
          completed: i + 1,
          total: fileArray.length,
          percentage: Math.round(((i + 1) / fileArray.length) * 100)
        });
      }
      
    } catch (error) {
      results.push({
        file: file.name,
        success: false,
        error: error.message
      });
    }
  }
  
  return results;
};

// Re-export validateImageFile from utils for backward compatibility
export const validateImageFile = validateImageFileSingleError

// ==========================================
// ESTADÍSTICAS Y REPORTES
// ==========================================

/**
 * Obtiene estadísticas administrativas del dataset
 * @returns {Promise<Object>} Estadísticas completas
 */
export const getDatasetStats = async () => {
  return await fetchGet('/api/images/admin/images/admin-stats/')
}

/**
 * Exporta datos del dataset a CSV
 * @param {Object} filters - Filtros a aplicar en la exportación
 * @returns {Promise<Blob>} Archivo CSV
 */
export const exportDatasetCSV = async (filters = {}) => {
  // Para descargas de archivos, necesitamos usar fetch directamente
  // ya que apiClient devuelve JSON por defecto
  const token = localStorage.getItem('access_token') || localStorage.getItem('token')
  const queryParams = new URLSearchParams()
  
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, value)
    }
  }
  
  const url = `${API_BASE_URL}/api/images/admin/images/export-csv/${queryParams.toString() ? `?${queryParams}` : ''}`
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'text/csv'
    }
  })
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }
  
  return await response.blob()
}

// ==========================================
// ENTRENAMIENTO DE MODELOS
// ==========================================

/**
 * Inicia entrenamiento de modelo de regresión
 * @param {Object} trainingParams - Parámetros de entrenamiento
 * @returns {Promise<Object>} Información del job iniciado
 */
export const trainRegressionModel = async (trainingParams) => {
  return await fetchPost('/api/train/jobs/create/', {
    job_type: 'regression',
    ...trainingParams
  })
}

/**
 * Inicia entrenamiento de modelo de visión
 * @param {Object} trainingParams - Parámetros de entrenamiento
 * @returns {Promise<Object>} Información del job iniciado
 */
export const trainVisionModel = async (trainingParams) => {
  return await fetchPost('/api/train/jobs/create/', {
    job_type: 'vision',
    ...trainingParams
  })
}

/**
 * Obtiene estado de un job de entrenamiento
 * @param {string} jobId - ID del job
 * @returns {Promise<Object>} Estado del job
 */
export const getTrainingJobStatus = async (jobId) => {
  return await fetchGet(`/api/train/jobs/${jobId}/status/`)
}

/**
 * Obtiene lista de todos los jobs de entrenamiento
 * @returns {Promise<Array>} Lista de jobs
 */
export const getTrainingJobs = async () => {
  const data = await fetchGet('/api/train/jobs/')
  return data.results || []
}

// ==========================================
// GESTIÓN DE DATOS
// ==========================================

/**
 * Valida integridad de los datos del dataset
 * @returns {Promise<Object>} Reporte de integridad
 */
export const validateDataIntegrity = async () => {
  return await fetchPost('/api/images/admin/data/validate-integrity/')
}

// ==========================================
// UTILIDADES Y HELPERS
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
  
  return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Formatea número con decimales específicos
 * @param {number} value - Valor a formatear
 * @param {number} decimals - Número de decimales
 * @returns {string} Número formateado
 */
export const formatNumber = (value, decimals = 2) => {
  if (value === null || value === undefined || Number.isNaN(value)) return 'N/A';
  return Number.parseFloat(value).toFixed(decimals);
};

/**
 * Genera filtros comunes para el dataset
 * @returns {Object} Filtros predefinidos
 */
export const getCommonFilters = () => ({
  // Calidad de datos
  DATA_QUALITY: {
    complete: 'complete',
    incomplete: 'incomplete',
    all: ''
  },
  
  // Calidad predicha
  PREDICTED_QUALITY: {
    excellent: 'excellent',
    good: 'good',
    fair: 'fair',
    poor: 'poor'
  },
  
  // Defectos
  DEFECT_TYPE: {
    none: 'none',
    crack: 'crack',
    hole: 'hole',
    stain: 'stain',
    deformation: 'deformation'
  },
  
  // Estados de procesamiento
  PROCESSING_STATUS: {
    processed: true,
    unprocessed: false,
    all: null
  }
});

/**
 * Configuración exportable para componentes
 */
export const DATASET_CONFIG = {
  // Límites
  MAX_FILE_SIZE: 20 * 1024 * 1024,  // 20MB
  MAX_BULK_OPERATIONS: 100,         // Máximo imágenes por operación masiva
  
  // Formatos soportados
  SUPPORTED_FORMATS: ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff'],
  
  // Paginación por defecto
  DEFAULT_PAGE_SIZE: 20,
  
  // Intervalos de actualización (ms)
  STATS_REFRESH_INTERVAL: 30000,    // 30 segundos
  JOB_STATUS_REFRESH_INTERVAL: 2000 // 2 segundos
};

// Exportación por defecto con todas las funciones principales
export default {
  // Gestión de imágenes
  getDatasetImages,
  getDatasetImage,
  updateDatasetImage,
  deleteDatasetImage,
  bulkUpdateDatasetImages,
  
  // Subida de archivos
  uploadDatasetImages,
  validateImageFile,
  
  // Estadísticas y reportes
  getDatasetStats,
  exportDatasetCSV,
  
  // Entrenamiento
  trainRegressionModel,
  trainVisionModel,
  getTrainingJobStatus,
  getTrainingJobs,
  
  // Gestión de datos
  validateDataIntegrity,
  
  // Utilidades
  formatFileSize,
  formatNumber,
  getCommonFilters,
  
  // Configuración
  DATASET_CONFIG
};
