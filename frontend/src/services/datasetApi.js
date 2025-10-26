/**
 * Servicio API para gestión administrativa de datasets
 * 
 * Principios aplicados:
 * - DRY: Funciones reutilizables con lógica centralizada
 * - KISS: Interface simple y directa
 * - SRP: Una responsabilidad por función
 */

// Configuración base reutilizable
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

/**
 * Construye parámetros de consulta de manera consistente (DRY)
 * @param {Object} filters - Filtros a aplicar
 * @returns {URLSearchParams} Parámetros de consulta
 */
const buildQueryParams = (filters = {}) => {
  const params = new URLSearchParams();
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, value);
    }
  });
  
  return params;
};

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
  try {
    const queryParams = buildQueryParams({
      ...filters,
      page,
      page_size: pageSize
    });
    
    const url = `${API_BASE_URL}/api/images/admin/images/?${queryParams}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: getCommonHeaders()
    });
    
    return await handleResponse(response);
  } catch (error) {
    console.error('Error obteniendo imágenes del dataset:', error);
    throw error;
  }
};

/**
 * Obtiene detalles de una imagen específica
 * @param {number} imageId - ID de la imagen
 * @returns {Promise<Object>} Detalles de la imagen
 */
export const getDatasetImage = async (imageId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/images/admin/images/${imageId}/`, {
      method: 'GET',
      headers: getCommonHeaders()
    });
    
    return await handleResponse(response);
  } catch (error) {
    console.error('Error obteniendo imagen:', error);
    throw error;
  }
};

/**
 * Actualiza una imagen del dataset
 * @param {number} imageId - ID de la imagen
 * @param {Object} updateData - Datos a actualizar
 * @returns {Promise<Object>} Imagen actualizada
 */
export const updateDatasetImage = async (imageId, updateData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/images/admin/images/${imageId}/`, {
      method: 'PATCH',
      headers: getCommonHeaders(),
      body: JSON.stringify(updateData)
    });
    
    return await handleResponse(response);
  } catch (error) {
    console.error('Error actualizando imagen:', error);
    throw error;
  }
};

/**
 * Elimina una imagen del dataset
 * @param {number} imageId - ID de la imagen
 * @returns {Promise<void>}
 */
export const deleteDatasetImage = async (imageId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/images/admin/images/${imageId}/`, {
      method: 'DELETE',
      headers: getCommonHeaders()
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
  } catch (error) {
    console.error('Error eliminando imagen:', error);
    throw error;
  }
};

/**
 * Actualización masiva de imágenes
 * @param {Array<number>} imageIds - IDs de imágenes a actualizar
 * @param {Object} updateData - Datos a aplicar
 * @returns {Promise<Object>} Resultado de la operación
 */
export const bulkUpdateDatasetImages = async (imageIds, updateData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/images/admin/images/bulk-update/`, {
      method: 'POST',
      headers: getCommonHeaders(),
      body: JSON.stringify({
        image_ids: imageIds,
        ...updateData
      })
    });
    
    return await handleResponse(response);
  } catch (error) {
    console.error('Error en actualización masiva:', error);
    throw error;
  }
};

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
      const validation = validateImageFile(file);
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
      Object.entries(metadata).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          formData.append(key, value);
        }
      });
      
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

/**
 * Valida un archivo de imagen
 * @param {File} file - Archivo a validar
 * @returns {Object} Resultado de validación
 */
export const validateImageFile = (file) => {
  // Validar tipo
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff'];
  if (!validTypes.includes(file.type)) {
    return {
      isValid: false,
      error: 'Formato no soportado. Use JPG, PNG, BMP o TIFF'
    };
  }
  
  // Validar tamaño (máximo 20MB)
  const maxSize = 20 * 1024 * 1024;
  if (file.size > maxSize) {
    return {
      isValid: false,
      error: `Archivo demasiado grande. Máximo ${Math.round(maxSize / (1024 * 1024))}MB`
    };
  }
  
  return { isValid: true };
};

// ==========================================
// ESTADÍSTICAS Y REPORTES
// ==========================================

/**
 * Obtiene estadísticas administrativas del dataset
 * @returns {Promise<Object>} Estadísticas completas
 */
export const getDatasetStats = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/images/admin/images/admin-stats/`, {
      method: 'GET',
      headers: getCommonHeaders()
    });
    
    return await handleResponse(response);
  } catch (error) {
    console.error('Error obteniendo estadísticas:', error);
    throw error;
  }
};

/**
 * Exporta datos del dataset a CSV
 * @param {Object} filters - Filtros a aplicar en la exportación
 * @returns {Promise<Blob>} Archivo CSV
 */
export const exportDatasetCSV = async (filters = {}) => {
  try {
    const queryParams = buildQueryParams(filters);
    const url = `${API_BASE_URL}/api/images/admin/images/export-csv/?${queryParams}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        ...getCommonHeaders(),
        'Accept': 'text/csv'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.blob();
  } catch (error) {
    console.error('Error exportando CSV:', error);
    throw error;
  }
};

// ==========================================
// ENTRENAMIENTO DE MODELOS
// ==========================================

/**
 * Inicia entrenamiento de modelo de regresión
 * @param {Object} trainingParams - Parámetros de entrenamiento
 * @returns {Promise<Object>} Información del job iniciado
 */
export const trainRegressionModel = async (trainingParams) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/train/jobs/create/`, {
      method: 'POST',
      headers: getCommonHeaders(),
      body: JSON.stringify({
        job_type: 'regression',
        ...trainingParams
      })
    });
    
    return await handleResponse(response);
  } catch (error) {
    console.error('Error iniciando entrenamiento de regresión:', error);
    throw error;
  }
};

/**
 * Inicia entrenamiento de modelo de visión
 * @param {Object} trainingParams - Parámetros de entrenamiento
 * @returns {Promise<Object>} Información del job iniciado
 */
export const trainVisionModel = async (trainingParams) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/train/jobs/create/`, {
      method: 'POST',
      headers: getCommonHeaders(),
      body: JSON.stringify({
        job_type: 'vision',
        ...trainingParams
      })
    });
    
    return await handleResponse(response);
  } catch (error) {
    console.error('Error iniciando entrenamiento de visión:', error);
    throw error;
  }
};

/**
 * Obtiene estado de un job de entrenamiento
 * @param {string} jobId - ID del job
 * @returns {Promise<Object>} Estado del job
 */
export const getTrainingJobStatus = async (jobId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/train/jobs/${jobId}/status/`, {
      method: 'GET',
      headers: getCommonHeaders()
    });
    
    return await handleResponse(response);
  } catch (error) {
    console.error('Error obteniendo estado del job:', error);
    throw error;
  }
};

/**
 * Obtiene lista de todos los jobs de entrenamiento
 * @returns {Promise<Array>} Lista de jobs
 */
export const getTrainingJobs = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/train/jobs/`, {
      method: 'GET',
      headers: getCommonHeaders()
    });
    
    const data = await handleResponse(response);
    return data.results || [];
  } catch (error) {
    console.error('Error obteniendo lista de jobs:', error);
    throw error;
  }
};

// ==========================================
// GESTIÓN DE DATOS
// ==========================================

/**
 * Valida integridad de los datos del dataset
 * @returns {Promise<Object>} Reporte de integridad
 */
export const validateDataIntegrity = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/images/admin/data/validate-integrity/`, {
      method: 'POST',
      headers: getCommonHeaders()
    });
    
    return await handleResponse(response);
  } catch (error) {
    console.error('Error validando integridad:', error);
    throw error;
  }
};

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
