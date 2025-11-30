/**
 * API service para predicciones de granos de cacao
 * 
 * Proporciona funciones para interactuar con el backend de predicción ML
 * incluyendo subida de imágenes y obtención de resultados de análisis.
 */

import { apiPost, apiGet, apiDelete } from './apiClient'
import { validateImageFile, getImageValidationError } from '@/utils/imageValidationUtils'
import { handleApiError } from './apiErrorHandler'

// Endpoints de la API
const API_ENDPOINTS = {
  predict: '/scan/measure/',
  predictYolo: '/scan/measure/',  // Usar el mismo endpoint unificado
  predictSmart: '/scan/measure/', // Usar el mismo endpoint unificado
  images: '/images/',
  stats: '/images/stats/'
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
      throw new Error('No se ha proporcionado ninguna imagen para procesar')
    }
    
    const imageFile = formData.get('image')
    if (!imageFile || imageFile.size === 0) {
      throw new Error('El archivo de imagen está vacío o corrupto')
    }

    // Validar imagen usando utilidad compartida
    const validationError = getImageValidationError(imageFile, {
      allowedTypes: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    })
    if (validationError) {
      throw new Error(validationError)
    }

    // Emitir evento de loading
    globalThis.dispatchEvent(new CustomEvent('api-loading-start', {
      detail: { type: 'prediction', message: 'Analizando imagen de cacao...' }
    }))

    console.log('📤 Enviando imagen para predicción:', {
      fileName: imageFile.name,
      fileSize: `${(imageFile.size / 1024).toFixed(1)}KB`,
      fileType: imageFile.type
    })

    const response = await apiPost(API_ENDPOINTS.predict, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 60000 // 60 segundos para procesamiento ML
    })

    console.log('✅ Predicción completada:', response)

    return {
      success: true,
      data: response
    }

  } catch (error) {
    const errorInfo = handleApiError(error, {
      logError: true
    })

    return {
      success: false,
      error: errorInfo.message
    }
  } finally {
    // Emitir evento de fin de loading
    globalThis.dispatchEvent(new CustomEvent('api-loading-end'))
  }
}

/**
 * Realiza predicción usando YOLOv8 con detección de objetos
 * @param {FormData} formData - Datos del formulario con la imagen y metadatos
 * @returns {Promise<Object>} - Resultado de la predicción YOLOv8
 */
export async function predictImageYolo(formData) {
  try {
    // Validar que FormData contiene una imagen
    if (!formData.has('image')) {
      throw new Error('No se ha proporcionado ninguna imagen para procesar')
    }
    
    const imageFile = formData.get('image')
    if (!imageFile || imageFile.size === 0) {
      throw new Error('El archivo de imagen está vacío o corrupto')
    }

    // Validar imagen usando utilidad compartida
    const validationError = getImageValidationError(imageFile, {
      allowedTypes: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp']
    })
    if (validationError) {
      throw new Error(validationError)
    }

    // Emitir evento de loading
    globalThis.dispatchEvent(new CustomEvent('api-loading-start', {
      detail: { type: 'yolo-prediction', message: 'Analizando imagen con YOLOv8...' }
    }))

    console.log('📤 Enviando imagen para predicción YOLOv8:', {
      fileName: imageFile.name,
      fileSize: `${(imageFile.size / 1024).toFixed(1)}KB`,
      fileType: imageFile.type
    })

    const response = await apiPost(API_ENDPOINTS.predictYolo, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 120000 // 120 segundos para YOLOv8
    })

    console.log('✅ Predicción YOLOv8 completada:', response)

    return {
      success: true,
      data: response
    }

  } catch (error) {
    const errorInfo = handleApiError(error, {
      logError: true
    })

    return {
      success: false,
      error: errorInfo.message
    }
  } finally {
    // Emitir evento de fin de loading
    globalThis.dispatchEvent(new CustomEvent('api-loading-end'))
  }
}

/**
 * Realiza predicción usando YOLOv8 con recorte inteligente estilo iPhone
 * @param {FormData} formData - Datos del formulario con la imagen y metadatos
 * @param {Object} options - Opciones adicionales
 * @returns {Promise<Object>} - Resultado de la predicción con recorte inteligente
 */
export async function predictImageSmart(formData, options = {}) {
  try {
    // Validar que FormData contiene una imagen
    if (!formData.has('image')) {
      throw new Error('No se ha proporcionado ninguna imagen para procesar')
    }
    
    const imageFile = formData.get('image')
    if (!imageFile || imageFile.size === 0) {
      throw new Error('El archivo de imagen está vacío o corrupto')
    }

    // Validar imagen usando utilidad compartida
    const validationError = getImageValidationError(imageFile, {
      allowedTypes: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp']
    })
    if (validationError) {
      throw new Error(validationError)
    }

    // Agregar opciones al FormData
    if (options.returnCroppedImage) {
      formData.append('return_cropped_image', 'true')
    }
    if (options.returnTransparentImage) {
      formData.append('return_transparent_image', 'true')
    }

    // Emitir evento de loading
    globalThis.dispatchEvent(new CustomEvent('api-loading-start', {
      detail: { type: 'smart-prediction', message: 'Analizando imagen con recorte inteligente...' }
    }))

    console.log('📤 Enviando imagen para predicción con recorte inteligente:', {
      fileName: imageFile.name,
      fileSize: `${(imageFile.size / 1024).toFixed(1)}KB`,
      fileType: imageFile.type,
      options
    })

    const response = await apiPost(API_ENDPOINTS.predictSmart, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 150000 // 150 segundos para recorte inteligente
    })

    console.log('✅ Predicción con recorte inteligente completada:', response)

    return {
      success: true,
      data: response
    }

  } catch (error) {
    const errorInfo = handleApiError(error, {
      logError: true
    })

    return {
      success: false,
      error: errorInfo.message
    }
  } finally {
    // Emitir evento de fin de loading
    globalThis.dispatchEvent(new CustomEvent('api-loading-end'))
  }
}

/**
 * Obtiene lista de imágenes procesadas por el usuario
 * @param {Object} params - Parámetros de consulta (paginación, filtros)
 * @returns {Promise<Object>} - Lista de imágenes y metadatos
 */
export async function getImages(params = {}) {
  try {
    console.log('📋 Obteniendo lista de imágenes:', params)

    const response = await apiGet(API_ENDPOINTS.images, params)

    console.log('✅ Imágenes obtenidas:', {
      count: response.results?.length || 0,
      total: response.count || 0
    })

    return {
      success: true,
      data: response
    }

  } catch (error) {
    const errorInfo = handleApiError(error, {
      logError: true
    })

    return {
      success: false,
      error: errorInfo.message
    }
  }
}

/**
 * Alias para getImages para compatibilidad con componentes existentes
 * @param {Object} params - Parámetros de consulta
 * @returns {Promise<Object>} - Historial de imágenes
 */
export const getImageHistory = getImages

/**
 * Alias para getStats para compatibilidad con componentes existentes
 * @param {Object} params - Parámetros de consulta
 * @returns {Promise<Object>} - Estadísticas de predicciones
 */
export const getPredictionStats = getStats

/**
 * Obtiene detalles de una imagen específica
 * @param {string} imageId - ID de la imagen
 * @returns {Promise<Object>} - Detalles de la imagen y predicción
 */
export async function getImageDetails(imageId) {
  try {
    if (!imageId) {
      throw new Error('ID de imagen requerido')
    }

    console.log('🔍 Obteniendo detalles de imagen:', imageId)

    const response = await apiGet(`${API_ENDPOINTS.images}${imageId}/`)

    console.log('✅ Detalles de imagen obtenidos')

    return {
      success: true,
      data: response
    }
    
  } catch (error) {
    const errorInfo = handleApiError(error, {
      logError: true
    })

    return {
      success: false,
      error: errorInfo.message
    }
  }
}

/**
 * Elimina una imagen del sistema
 * @param {string} imageId - ID de la imagen a eliminar
 * @returns {Promise<Object>} - Resultado de la operación
 */
export async function deleteImage(imageId) {
  try {
    if (!imageId) {
      throw new Error('ID de imagen requerido')
    }

    console.log('🗑️ Eliminando imagen:', imageId)

    await apiDelete(`${API_ENDPOINTS.images}${imageId}/`)

    console.log('✅ Imagen eliminada exitosamente')

    return {
      success: true,
      message: 'Imagen eliminada exitosamente'
    }

  } catch (error) {
    const errorInfo = handleApiError(error, {
      logError: true
    })

    return {
      success: false,
      error: errorInfo.message
    }
  }
}

/**
 * Obtiene estadísticas de predicciones del usuario
 * @param {Object} params - Parámetros de consulta (filtros de fecha, etc.)
 * @returns {Promise<Object>} - Estadísticas agregadas
 */
export async function getStats(params = {}) {
  try {
    console.log('📊 Obteniendo estadísticas:', params)

    const response = await api.get(API_ENDPOINTS.stats, { params })

    console.log('✅ Estadísticas obtenidas')

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    const errorInfo = handleApiError(error, {
      logError: true
    })

    return {
      success: false,
      error: errorInfo.message
    }
  }
}

/**
 * Actualiza metadatos de una imagen
 * @param {string} imageId - ID de la imagen
 * @param {Object} data - Nuevos metadatos
 * @returns {Promise<Object>} - Resultado de la operación
 */
export async function updateImageMetadata(imageId, data) {
  try {
    if (!imageId) {
      throw new Error('ID de imagen requerido')
    }

    console.log('✏️ Actualizando metadatos de imagen:', imageId, data)

    const response = await api.patch(`${API_ENDPOINTS.images}${imageId}/`, data)

    console.log('✅ Metadatos actualizados exitosamente')

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    const errorInfo = handleApiError(error, {
      logError: true
    })

    return {
      success: false,
      error: errorInfo.message
    }
  }
}

/**
 * Descarga una imagen procesada
 * @param {string} imageId - ID de la imagen
 * @param {string} type - Tipo de descarga ('original', 'processed', 'report')
 * @returns {Promise<Object>} - Resultado de la operación
 */
export async function downloadImage(imageId, type = 'original') {
  try {
    if (!imageId) {
      throw new Error('ID de imagen requerido')
    }

    console.log('⬇️ Descargando imagen:', imageId, type)

    const response = await api.get(`${API_ENDPOINTS.images}${imageId}/download/`, {
      params: { type },
      responseType: 'blob'
    })

    // Crear URL de descarga
    const blob = new Blob([response.data])
    const url = globalThis.URL.createObjectURL(blob)
    
    // Extraer nombre del archivo de headers o usar default
    const contentDisposition = response.headers['content-disposition']
    let filename = `imagen_${imageId}_${type}.jpg`
    
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/)
      if (filenameMatch) {
        filename = filenameMatch[1]
      }
    }

    // Crear elemento de descarga temporal
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    
    // Limpiar
    link.remove()
    globalThis.URL.revokeObjectURL(url)

    console.log('✅ Descarga completada')

    return {
      success: true,
      message: 'Descarga completada exitosamente'
    }

  } catch (error) {
    const errorInfo = handleApiError(error, {
      logError: true
    })

    return {
      success: false,
      error: errorInfo.message
    }
  }
}

/**
 * Exporta resultados de predicciones en diferentes formatos
 * @param {Object} options - Opciones de exportación (formato, filtros, etc.)
 * @returns {Promise<Object>} - Resultado de la operación
 */
export async function exportResults(options = {}) {
  try {
    console.log('📤 Exportando resultados:', options)

    const response = await api.post(`${API_ENDPOINTS.images}export/`, options, {
      responseType: 'blob'
    })

    // Crear URL de descarga
    const blob = new Blob([response.data])
    const url = globalThis.URL.createObjectURL(blob)
    
    // Determinar nombre del archivo
    const format = options.format || 'csv'
    const timestamp = new Date().toISOString().slice(0, 10)
    const filename = `resultados_cacao_${timestamp}.${format}`

    // Crear elemento de descarga temporal
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    
    // Limpiar
    link.remove()
    globalThis.URL.revokeObjectURL(url)

    console.log('✅ Exportación completada')

    return {
      success: true,
      message: 'Exportación completada exitosamente'
    }

  } catch (error) {
    const errorInfo = handleApiError(error, {
      logError: true
    })

    return {
      success: false,
      error: errorInfo.message
    }
  }
}

// Re-export validateImageFile from utils for backward compatibility
export { validateImageFile } from '@/utils/imageValidationUtils'

// Re-export createImageFormData from utils for backward compatibility
export { createImageFormData } from '@/utils/formDataUtils'

// No exportar api directamente, solo las funciones
export default {
  predictImage,
  predictImageYolo,
  predictImageSmart,
  getImages,
  getImageHistory,
  getPredictionStats,
  getImageDetails,
  deleteImage,
  updateImageMetadata,
  downloadImage,
  exportResults,
  getStats,
  validateImageFile,
  createImageFormData
}