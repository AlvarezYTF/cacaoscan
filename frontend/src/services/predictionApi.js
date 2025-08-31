/**
 * API service para predicciones de granos de cacao
 * 
 * Proporciona funciones para interactuar con el backend de predicción ML
 * incluyendo subida de imágenes y obtención de resultados de análisis.
 */

import api from './api'

// Endpoints de la API
const API_ENDPOINTS = {
  predict: '/images/predict/',
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

    // Validar formato de imagen
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if (!allowedTypes.includes(imageFile.type)) {
      throw new Error('Formato de imagen no válido. Use JPEG, PNG o WebP')
    }

    // Validar tamaño máximo (5MB)
    const maxSize = 5 * 1024 * 1024
    if (imageFile.size > maxSize) {
      throw new Error('La imagen es demasiado grande. Máximo 5MB permitido')
    }

    // Emitir evento de loading
    window.dispatchEvent(new CustomEvent('api-loading-start', {
      detail: { type: 'prediction', message: 'Analizando imagen de cacao...' }
    }))

    console.log('📤 Enviando imagen para predicción:', {
      fileName: imageFile.name,
      fileSize: `${(imageFile.size / 1024).toFixed(1)}KB`,
      fileType: imageFile.type
    })

    const response = await api.post(API_ENDPOINTS.predict, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 60000 // 60 segundos para procesamiento ML
    })

    console.log('✅ Predicción completada:', response.data)

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error en predicción:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error inesperado al procesar la imagen'

    return {
      success: false,
      error: errorMessage
    }
  } finally {
    // Emitir evento de fin de loading
    window.dispatchEvent(new CustomEvent('api-loading-end'))
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

    const response = await api.get(API_ENDPOINTS.images, { params })

    console.log('✅ Imágenes obtenidas:', {
      count: response.data.results?.length || 0,
      total: response.data.count || 0
    })

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error obteniendo imágenes:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener el historial de imágenes'

    return {
      success: false,
      error: errorMessage
    }
  }
}

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

    const response = await api.get(`${API_ENDPOINTS.images}${imageId}/`)

    console.log('✅ Detalles de imagen obtenidos')

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error obteniendo detalles de imagen:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener los detalles de la imagen'

    return {
      success: false,
      error: errorMessage
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

    await api.delete(`${API_ENDPOINTS.images}${imageId}/`)

    console.log('✅ Imagen eliminada exitosamente')

    return {
      success: true,
      message: 'Imagen eliminada exitosamente'
    }

  } catch (error) {
    console.error('❌ Error eliminando imagen:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al eliminar la imagen'

    return {
      success: false,
      error: errorMessage
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
    console.error('❌ Error obteniendo estadísticas:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener las estadísticas'

    return {
      success: false,
      error: errorMessage
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
    console.error('❌ Error actualizando metadatos:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al actualizar los metadatos'

    return {
      success: false,
      error: errorMessage
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
    const url = window.URL.createObjectURL(blob)
    
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
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    console.log('✅ Descarga completada')

    return {
      success: true,
      message: 'Descarga completada exitosamente'
    }

  } catch (error) {
    console.error('❌ Error descargando imagen:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al descargar la imagen'

    return {
      success: false,
      error: errorMessage
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
    const url = window.URL.createObjectURL(blob)
    
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
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    console.log('✅ Exportación completada')

    return {
      success: true,
      message: 'Exportación completada exitosamente'
    }

  } catch (error) {
    console.error('❌ Error exportando resultados:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al exportar los resultados'

    return {
      success: false,
      error: errorMessage
    }
  }
}

// Función auxiliar para validar formatos de imagen
export function validateImageFile(file) {
  const errors = []

  if (!file) {
    errors.push('Archivo requerido')
    return errors
  }

  // Validar tipo
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    errors.push('Formato no válido. Use JPEG, PNG o WebP')
  }

  // Validar tamaño (5MB máximo)
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    errors.push('Archivo demasiado grande. Máximo 5MB')
  }

  // Validar tamaño mínimo (1KB)
  const minSize = 1024
  if (file.size < minSize) {
    errors.push('Archivo demasiado pequeño')
  }

  return errors
}

// Exportar API client configurado para uso directo
export const predictionApiClient = api

export default {
  predictImage,
  getImages,
  getImageDetails,
  deleteImage,
  updateImageMetadata,
  downloadImage,
  exportResults,
  getStats,
  validateImageFile
}