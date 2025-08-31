/**
 * API service para predicciones de granos de cacao
 * 
 * Proporciona funciones para interactuar con el backend de predicción ML
 * incluyendo subida de imágenes y obtención de resultados de análisis.
 */

// Configuración base de la API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_ENDPOINTS = {
  predict: '/api/images/predict/',
  images: '/api/images/',
  stats: '/api/images/stats/'
};

/**
 * Maneja errores de red y HTTP de manera consistente
 * @param {Response} response - Respuesta de fetch
 * @returns {Promise<Object>} - Datos de respuesta o lanza error
 */
async function handleResponse(response) {
  const contentType = response.headers.get('content-type');
  
  // Verificar si la respuesta es JSON
  if (contentType && contentType.includes('application/json')) {
    const data = await response.json();
    
    if (!response.ok) {
      // Si la respuesta tiene formato de error del backend
      if (data.success === false || data.error) {
        throw new Error(data.message || data.error || `Error HTTP ${response.status}`);
      }
      
      // Error HTTP genérico
      throw new Error(`Error HTTP ${response.status}: ${response.statusText}`);
    }
    
    return data;
  } else {
    // Respuesta no JSON
    if (!response.ok) {
      throw new Error(`Error HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.text();
  }
}

/**
 * Realiza predicción de características físicas de un grano de cacao
 * @param {FormData} formData - Datos del formulario con la imagen y metadatos
 * @returns {Promise<Object>} - Resultado de la predicción
 */
export async function predictImage(formData) {
  try {
    // Validar que FormData contiene una imagen
    if (!formData.has('image')) {
      throw new Error('No se ha proporcionado ninguna imagen para procesar');
    }
    
    const imageFile = formData.get('image');
    if (!imageFile || imageFile.size === 0) {
      throw new Error('El archivo de imagen está vacío o corrupto');
    }
    
    // Validar tipo de archivo
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff'];
    if (!validTypes.includes(imageFile.type)) {
      throw new Error('Formato de imagen no soportado. Use JPG, PNG, BMP o TIFF');
    }
    
    // Validar tamaño (10MB máximo como en el backend)
    const maxSize = 10 * 1024 * 1024; // 10MB en bytes
    if (imageFile.size > maxSize) {
      throw new Error(`El archivo es demasiado grande. Tamaño máximo permitido: ${Math.round(maxSize / (1024 * 1024))}MB`);
    }
    
    console.log('Enviando imagen para predicción:', {
      nombre: imageFile.name,
      tamaño: `${Math.round(imageFile.size / 1024)}KB`,
      tipo: imageFile.type
    });
    
    // Realizar petición al backend
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.predict}`, {
      method: 'POST',
      body: formData
      // No establecer Content-Type para FormData, el navegador lo hace automáticamente
    });
    
    const result = await handleResponse(response);
    
    // Validar estructura de respuesta esperada
    if (!result.success) {
      throw new Error(result.message || 'Error desconocido en la predicción');
    }
    
    // Validar que contiene los campos esperados
    const requiredFields = ['id', 'width', 'height', 'thickness', 'predicted_weight'];
    const missingFields = requiredFields.filter(field => result[field] === undefined);
    
    if (missingFields.length > 0) {
      console.warn('Campos faltantes en la respuesta:', missingFields);
    }
    
    console.log('Predicción completada exitosamente:', {
      id: result.id,
      dimensiones: `${result.width}x${result.height}x${result.thickness}mm`,
      peso: `${result.predicted_weight}g`,
      confianza: result.confidence_level,
      tiempo: `${result.processing_time}s`
    });
    
    return result;
    
  } catch (error) {
    console.error('Error en predicción de imagen:', error);
    
    // Re-lanzar errores conocidos
    if (error.message.includes('TypeError') && error.message.includes('fetch')) {
      throw new Error('No se pudo conectar con el servidor. Verifique su conexión a internet.');
    }
    
    throw error;
  }
}

/**
 * Obtiene una imagen específica por ID
 * @param {number} imageId - ID de la imagen
 * @returns {Promise<Object>} - Datos completos de la imagen
 */
export async function getImage(imageId) {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.images}${imageId}/`);
    return await handleResponse(response);
  } catch (error) {
    console.error('Error obteniendo imagen:', error);
    throw error;
  }
}

/**
 * Obtiene el historial de predicciones con filtros opcionales
 * @param {Object} filters - Filtros para la búsqueda
 * @param {boolean} filters.processed - Solo imágenes procesadas
 * @param {string} filters.quality - Filtro por calidad
 * @param {string} filters.batch - Filtro por lote
 * @param {string} filters.dateFrom - Fecha desde (YYYY-MM-DD)
 * @param {string} filters.dateTo - Fecha hasta (YYYY-MM-DD)
 * @param {number} filters.page - Número de página
 * @returns {Promise<Object>} - Lista paginada de predicciones
 */
export async function getImageHistory(filters = {}) {
  try {
    const params = new URLSearchParams();
    
    // Agregar filtros válidos
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value);
      }
    });
    
    const url = `${API_BASE_URL}${API_ENDPOINTS.images}${params.toString() ? `?${params.toString()}` : ''}`;
    const response = await fetch(url);
    
    return await handleResponse(response);
  } catch (error) {
    console.error('Error obteniendo historial:', error);
    throw error;
  }
}

/**
 * Obtiene estadísticas de predicciones
 * @returns {Promise<Object>} - Estadísticas de predicciones
 */
export async function getPredictionStats() {
  try {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.stats}`);
    return await handleResponse(response);
  } catch (error) {
    console.error('Error obteniendo estadísticas:', error);
    throw error;
  }
}

/**
 * Crea FormData para envío de imagen con metadatos opcionales
 * @param {File} imageFile - Archivo de imagen
 * @param {Object} metadata - Metadatos opcionales
 * @param {string} metadata.batch_number - Número de lote
 * @param {string} metadata.origin - Origen del grano
 * @param {string} metadata.notes - Notas adicionales
 * @returns {FormData} - FormData listo para envío
 */
export function createImageFormData(imageFile, metadata = {}) {
  const formData = new FormData();
  
  // Agregar imagen (obligatorio)
  formData.append('image', imageFile);
  
  // Agregar metadatos opcionales
  if (metadata.batch_number) {
    formData.append('batch_number', metadata.batch_number);
  }
  
  if (metadata.origin) {
    formData.append('origin', metadata.origin);
  }
  
  if (metadata.notes) {
    formData.append('notes', metadata.notes);
  }
  
  return formData;
}

/**
 * Valida un archivo de imagen antes del envío
 * @param {File} file - Archivo a validar
 * @returns {Object} - Resultado de validación {isValid: boolean, error?: string}
 */
export function validateImageFile(file) {
  if (!file) {
    return { isValid: false, error: 'No se ha seleccionado ningún archivo' };
  }
  
  // Validar tipo de archivo
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff'];
  if (!validTypes.includes(file.type)) {
    return { 
      isValid: false, 
      error: 'Formato no soportado. Use archivos JPG, PNG, BMP o TIFF' 
    };
  }
  
  // Validar tamaño (10MB máximo)
  const maxSize = 10 * 1024 * 1024;
  if (file.size > maxSize) {
    return { 
      isValid: false, 
      error: `Archivo demasiado grande. Tamaño máximo: ${Math.round(maxSize / (1024 * 1024))}MB` 
    };
  }
  
  // Validar dimensiones mínimas (al menos 32x32 como en backend)
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      if (img.width < 32 || img.height < 32) {
        resolve({ 
          isValid: false, 
          error: 'Imagen demasiado pequeña. Dimensiones mínimas: 32x32 píxeles' 
        });
      } else if (img.width > 4096 || img.height > 4096) {
        resolve({ 
          isValid: false, 
          error: 'Imagen demasiado grande. Dimensiones máximas: 4096x4096 píxeles' 
        });
      } else {
        resolve({ isValid: true });
      }
    };
    img.onerror = () => {
      resolve({ 
        isValid: false, 
        error: 'No se pudo cargar la imagen. Archivo posiblemente corrupto' 
      });
    };
    img.src = URL.createObjectURL(file);
  });
}

/**
 * Formatea los resultados de predicción para mostrar en UI
 * @param {Object} prediction - Resultado crudo de predicción
 * @returns {Object} - Resultado formateado para UI
 */
export function formatPredictionResult(prediction) {
  return {
    id: prediction.id,
    dimensions: {
      width: {
        value: parseFloat(prediction.width).toFixed(2),
        unit: 'mm',
        label: 'Ancho'
      },
      height: {
        value: parseFloat(prediction.height).toFixed(2),
        unit: 'mm',
        label: 'Alto'
      },
      thickness: {
        value: parseFloat(prediction.thickness).toFixed(2),
        unit: 'mm',
        label: 'Grosor'
      }
    },
    weight: {
      value: parseFloat(prediction.predicted_weight).toFixed(3),
      unit: 'g',
      label: 'Peso Predicho'
    },
    quality: {
      level: prediction.confidence_level,
      score: prediction.confidence_score ? (prediction.confidence_score * 100).toFixed(1) : null,
      method: prediction.prediction_method
    },
    processing: {
      time: prediction.processing_time ? parseFloat(prediction.processing_time).toFixed(3) : null,
      timestamp: prediction.created_at
    },
    image: {
      url: prediction.image_url,
      id: prediction.id
    },
    metadata: {
      derived_metrics: prediction.derived_metrics,
      weight_comparison: prediction.weight_comparison
    }
  };
}

// Exportar constantes útiles
export const PREDICTION_API_CONFIG = {
  maxFileSize: 10 * 1024 * 1024, // 10MB
  supportedFormats: ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff'],
  minDimensions: { width: 32, height: 32 },
  maxDimensions: { width: 4096, height: 4096 }
};

export default {
  predictImage,
  getImage,
  getImageHistory,
  getPredictionStats,
  createImageFormData,
  validateImageFile,
  formatPredictionResult,
  PREDICTION_API_CONFIG
};
