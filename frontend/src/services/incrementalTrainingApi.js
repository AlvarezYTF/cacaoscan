/**
 * API service para entrenamiento incremental del modelo YOLOv8
 * 
 * Proporciona funciones para subir nuevas muestras y entrenar
 * el modelo de forma incremental sin reiniciar el entrenamiento completo.
 */

import api from './api'

// Endpoints de la API
const API_ENDPOINTS = {
  status: '/incremental/status/',
  train: '/incremental/train/',
  upload: '/incremental/upload/',
  models: '/incremental/models/',
  data: '/incremental/data/'
}

/**
 * Realiza entrenamiento incremental con nueva imagen y datos
 * @param {FormData} formData - Datos del formulario con imagen y datos del grano
 * @returns {Promise<Object>} - Resultado del entrenamiento incremental
 */
export async function submitIncrementalTraining(formData) {
  try {
    // Validar que FormData contiene una imagen
    if (!formData.has('image')) {
      throw new Error('No se ha proporcionado ninguna imagen para entrenar')
    }
    
    const imageFile = formData.get('image')
    if (!imageFile || imageFile.size === 0) {
      throw new Error('El archivo de imagen está vacío o corrupto')
    }

    // Validar formato de imagen
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp']
    if (!allowedTypes.includes(imageFile.type)) {
      throw new Error('Formato de imagen no válido. Use JPEG, PNG, WebP o BMP')
    }

    // Validar tamaño máximo (20MB)
    const maxSize = 20 * 1024 * 1024
    if (imageFile.size > maxSize) {
      throw new Error('La imagen es demasiado grande. Máximo 20MB permitido')
    }

    // Validar datos JSON
    if (!formData.has('data')) {
      throw new Error('No se han proporcionado datos del grano')
    }

    let grainData
    try {
      grainData = JSON.parse(formData.get('data'))
    } catch (e) {
      throw new Error('Datos del grano en formato JSON inválido')
    }

    // Validar campos requeridos
    const requiredFields = ['id', 'alto', 'ancho', 'grosor', 'peso']
    const missingFields = requiredFields.filter(field => !grainData[field])
    if (missingFields.length > 0) {
      throw new Error(`Campos faltantes: ${missingFields.join(', ')}`)
    }

    // Emitir evento de loading
    window.dispatchEvent(new CustomEvent('api-loading-start', {
      detail: { type: 'incremental-training', message: 'Entrenando modelo incrementalmente...' }
    }))

    console.log('📤 Enviando datos para entrenamiento incremental:', {
      fileName: imageFile.name,
      fileSize: `${(imageFile.size / 1024).toFixed(1)}KB`,
      fileType: imageFile.type,
      grainData
    })

    const response = await api.post(API_ENDPOINTS.train, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 300000 // 5 minutos para entrenamiento
    })

    console.log('✅ Entrenamiento incremental completado:', response.data)

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error en entrenamiento incremental:', error)
    
    const errorMessage = error.response?.data?.error || 
                        error.response?.data?.detail || 
                        error.message || 
                        'Error inesperado en el entrenamiento incremental'

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
 * Obtiene estado del entrenamiento incremental
 * @param {Object} params - Parámetros de consulta
 * @returns {Promise<Object>} - Estado del sistema de entrenamiento
 */
export async function getIncrementalTrainingStatus(params = {}) {
  try {
    console.log('📊 Obteniendo estado de entrenamiento incremental:', params)

    const response = await api.get(API_ENDPOINTS.status, { params })

    console.log('✅ Estado obtenido')

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error obteniendo estado:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener el estado del entrenamiento incremental'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Obtiene versiones de modelos incrementales
 * @param {Object} params - Parámetros de consulta (paginación, filtros)
 * @returns {Promise<Object>} - Versiones de modelos
 */
export async function getIncrementalModels(params = {}) {
  try {
    console.log('📋 Obteniendo versiones de modelos:', params)

    const response = await api.get(API_ENDPOINTS.models, { params })

    console.log('✅ Versiones de modelos obtenidas')

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error obteniendo versiones de modelos:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener las versiones de modelos'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Obtiene versiones de datos de entrenamiento incremental
 * @param {Object} params - Parámetros de consulta
 * @returns {Promise<Object>} - Versiones de datos
 */
export async function getIncrementalDataVersions(params = {}) {
  try {
    console.log('📋 Obteniendo versiones de datos:', params)

    const response = await api.get(API_ENDPOINTS.data, { params })

    console.log('✅ Versiones de datos obtenidas')

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error obteniendo versiones de datos:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener las versiones de datos'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Sube datos para entrenamiento incremental
 * @param {FormData} formData - Datos a subir
 * @returns {Promise<Object>} - Resultado de la subida
 */
export async function uploadIncrementalData(formData) {
  try {
    console.log('📤 Subiendo datos para entrenamiento incremental')

    const response = await api.post(API_ENDPOINTS.upload, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 120000 // 2 minutos
    })

    console.log('✅ Datos subidos exitosamente')

    return {
      success: true,
      data: response.data,
      message: 'Datos subidos exitosamente'
    }

  } catch (error) {
    console.error('❌ Error subiendo datos:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al subir los datos'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Valida los datos del grano antes del entrenamiento
 * @param {Object} grainData - Datos del grano
 * @returns {Object} - Resultado de la validación
 */
export function validateGrainData(grainData) {
  const errors = []
  
  // Validar campos requeridos
  const requiredFields = ['id', 'alto', 'ancho', 'grosor', 'peso']
  for (const field of requiredFields) {
    if (!grainData[field] || grainData[field] === '') {
      errors.push(`${field} es requerido`)
    }
  }
  
  // Validar tipos numéricos
  if (grainData.id && (!Number.isInteger(Number(grainData.id)) || Number(grainData.id) < 1)) {
    errors.push('ID debe ser un número entero positivo')
  }
  
  if (grainData.peso && (isNaN(Number(grainData.peso)) || Number(grainData.peso) < 0.1 || Number(grainData.peso) > 5.0)) {
    errors.push('Peso debe estar entre 0.1 y 5.0 gramos')
  }
  
  if (grainData.alto && (isNaN(Number(grainData.alto)) || Number(grainData.alto) < 5 || Number(grainData.alto) > 50)) {
    errors.push('Alto debe estar entre 5 y 50 mm')
  }
  
  if (grainData.ancho && (isNaN(Number(grainData.ancho)) || Number(grainData.ancho) < 3 || Number(grainData.ancho) > 30)) {
    errors.push('Ancho debe estar entre 3 y 30 mm')
  }
  
  if (grainData.grosor && (isNaN(Number(grainData.grosor)) || Number(grainData.grosor) < 2 || Number(grainData.grosor) > 20)) {
    errors.push('Grosor debe estar entre 2 y 20 mm')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

/**
 * Crea FormData para entrenamiento incremental
 * @param {File} imageFile - Archivo de imagen
 * @param {Object} grainData - Datos del grano
 * @param {Object} additionalInfo - Información adicional
 * @returns {FormData} - FormData preparado
 */
export function createTrainingFormData(imageFile, grainData, additionalInfo = {}) {
  const formData = new FormData()
  
  // Agregar imagen
  formData.append('image', imageFile)
  
  // Agregar datos del grano como JSON
  formData.append('data', JSON.stringify(grainData))
  
  // Agregar información adicional
  if (additionalInfo.batch_number) {
    formData.append('batch_number', additionalInfo.batch_number)
  }
  if (additionalInfo.origin) {
    formData.append('origin', additionalInfo.origin)
  }
  if (additionalInfo.notes) {
    formData.append('notes', additionalInfo.notes)
  }
  
  return formData
}

/**
 * Valida archivo de imagen para entrenamiento
 * @param {File} file - Archivo de imagen
 * @returns {Object} - Resultado de la validación
 */
export function validateImageFile(file) {
  const errors = []
  
  if (!file) {
    errors.push('No se ha seleccionado ningún archivo')
    return { isValid: false, errors }
  }
  
  // Validar tipo de archivo
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp']
  if (!allowedTypes.includes(file.type)) {
    errors.push('Formato de imagen no válido. Use JPEG, PNG, WebP o BMP')
  }
  
  // Validar tamaño
  const maxSize = 20 * 1024 * 1024 // 20MB
  if (file.size > maxSize) {
    errors.push('La imagen es demasiado grande. Máximo 20MB permitido')
  }
  
  // Validar que no esté vacío
  if (file.size === 0) {
    errors.push('El archivo está vacío')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

export default {
  submitIncrementalTraining,
  getIncrementalTrainingStatus,
  getIncrementalModels,
  getIncrementalDataVersions,
  uploadIncrementalData,
  validateGrainData,
  createTrainingFormData,
  validateImageFile
}
