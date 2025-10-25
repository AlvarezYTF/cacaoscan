/**
 * Servicio API para sistema de calibración
 * 
 * Maneja todas las operaciones relacionadas con la calibración de modelos:
 * - Estado de calibración
 * - Realizar calibración
 * - Análisis calibrado
 * 
 * La calibración permite ajustar los modelos con datos de referencia
 * para mejorar la precisión de las predicciones.
 */

import api from './api'

// Endpoints de la API
const API_ENDPOINTS = {
  status: '/calibration/status/',
  calibrate: '/calibration/',
  scanCalibrated: '/scan/measure/calibrated/'
}

/**
 * Obtiene el estado actual de calibración del sistema
 * @returns {Promise<Object>} - Estado de calibración
 */
export async function getCalibrationStatus() {
  try {
    console.log('⚖️ Obteniendo estado de calibración')

    const response = await api.get(API_ENDPOINTS.status)

    console.log('✅ Estado de calibración obtenido:', response.data)

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error obteniendo estado de calibración:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al obtener el estado de calibración'

    return {
      success: false,
      error: errorMessage
    }
  }
}

/**
 * Realiza calibración del sistema con datos de referencia
 * @param {FormData|Object} calibrationData - Datos de calibración
 * @param {File} calibrationData.reference_image - Imagen de referencia (opcional)
 * @param {number} calibrationData.reference_weight - Peso de referencia en gramos
 * @param {number} calibrationData.reference_length - Longitud de referencia en mm
 * @param {number} calibrationData.reference_width - Ancho de referencia en mm
 * @param {number} calibrationData.reference_thickness - Grosor de referencia en mm
 * @param {string} calibrationData.calibration_type - Tipo de calibración ('weight', 'size', 'full')
 * @returns {Promise<Object>} - Resultado de la calibración
 */
export async function performCalibration(calibrationData) {
  try {
    console.log('⚖️ Realizando calibración del sistema')

    // Emitir evento de loading
    window.dispatchEvent(new CustomEvent('api-loading-start', {
      detail: { type: 'calibration', message: 'Calibrando sistema...' }
    }))

    // Determinar si es FormData o JSON
    const isFormData = calibrationData instanceof FormData
    const headers = isFormData ? { 'Content-Type': 'multipart/form-data' } : {}

    const response = await api.post(API_ENDPOINTS.calibrate, calibrationData, {
      headers,
      timeout: 60000 // 60 segundos
    })

    console.log('✅ Calibración completada exitosamente')

    return {
      success: true,
      data: response.data,
      message: 'Calibración realizada exitosamente'
    }

  } catch (error) {
    console.error('❌ Error realizando calibración:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error al realizar la calibración'

    return {
      success: false,
      error: errorMessage
    }
  } finally {
    window.dispatchEvent(new CustomEvent('api-loading-end'))
  }
}

/**
 * Realiza análisis calibrado de una imagen
 * @param {FormData} formData - Datos del formulario con la imagen
 * @returns {Promise<Object>} - Resultado del análisis calibrado
 */
export async function scanWithCalibration(formData) {
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

    // Validar tamaño máximo (20MB)
    const maxSize = 20 * 1024 * 1024
    if (imageFile.size > maxSize) {
      throw new Error('La imagen es demasiado grande. Máximo 20MB permitido')
    }

    // Emitir evento de loading
    window.dispatchEvent(new CustomEvent('api-loading-start', {
      detail: { type: 'calibrated-scan', message: 'Analizando imagen con calibración...' }
    }))

    console.log('📤 Enviando imagen para análisis calibrado:', {
      fileName: imageFile.name,
      fileSize: `${(imageFile.size / 1024).toFixed(1)}KB`,
      fileType: imageFile.type
    })

    const response = await api.post(API_ENDPOINTS.scanCalibrated, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 60000 // 60 segundos
    })

    console.log('✅ Análisis calibrado completado:', response.data)

    return {
      success: true,
      data: response.data
    }

  } catch (error) {
    console.error('❌ Error en análisis calibrado:', error)
    
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        error.message || 
                        'Error inesperado al procesar la imagen con calibración'

    return {
      success: false,
      error: errorMessage
    }
  } finally {
    window.dispatchEvent(new CustomEvent('api-loading-end'))
  }
}

/**
 * Tipos de calibración disponibles
 */
export const CALIBRATION_TYPES = {
  WEIGHT: 'weight',      // Calibración de peso
  SIZE: 'size',          // Calibración de dimensiones
  FULL: 'full'           // Calibración completa
}

/**
 * Estados de calibración
 */
export const CALIBRATION_STATUS = {
  NOT_CALIBRATED: 'not_calibrated',
  CALIBRATED: 'calibrated',
  EXPIRED: 'expired',
  IN_PROGRESS: 'in_progress'
}

/**
 * Valida datos de calibración antes de envío
 * @param {Object} calibrationData - Datos a validar
 * @returns {Object} - Resultado de la validación
 */
export function validateCalibrationData(calibrationData) {
  const errors = []

  // Validar tipo de calibración
  if (!calibrationData.calibration_type) {
    errors.push('El tipo de calibración es requerido')
  } else if (!Object.values(CALIBRATION_TYPES).includes(calibrationData.calibration_type)) {
    errors.push('Tipo de calibración inválido')
  }

  // Validar según tipo de calibración
  if (calibrationData.calibration_type === CALIBRATION_TYPES.WEIGHT || 
      calibrationData.calibration_type === CALIBRATION_TYPES.FULL) {
    if (!calibrationData.reference_weight || calibrationData.reference_weight <= 0) {
      errors.push('El peso de referencia debe ser mayor a 0')
    }
    if (calibrationData.reference_weight && calibrationData.reference_weight > 10) {
      errors.push('El peso de referencia no puede exceder 10 gramos')
    }
  }

  if (calibrationData.calibration_type === CALIBRATION_TYPES.SIZE || 
      calibrationData.calibration_type === CALIBRATION_TYPES.FULL) {
    if (!calibrationData.reference_length || calibrationData.reference_length <= 0) {
      errors.push('La longitud de referencia debe ser mayor a 0')
    }
    if (!calibrationData.reference_width || calibrationData.reference_width <= 0) {
      errors.push('El ancho de referencia debe ser mayor a 0')
    }
    if (!calibrationData.reference_thickness || calibrationData.reference_thickness <= 0) {
      errors.push('El grosor de referencia debe ser mayor a 0')
    }

    // Validar rangos razonables
    if (calibrationData.reference_length > 50) {
      errors.push('La longitud de referencia no puede exceder 50 mm')
    }
    if (calibrationData.reference_width > 30) {
      errors.push('El ancho de referencia no puede exceder 30 mm')
    }
    if (calibrationData.reference_thickness > 20) {
      errors.push('El grosor de referencia no puede exceder 20 mm')
    }
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}

/**
 * Crea FormData para calibración
 * @param {Object} calibrationData - Datos de calibración
 * @param {File} referenceImage - Imagen de referencia (opcional)
 * @returns {FormData} - FormData preparado
 */
export function createCalibrationFormData(calibrationData, referenceImage = null) {
  const formData = new FormData()

  // Agregar imagen si existe
  if (referenceImage) {
    formData.append('reference_image', referenceImage)
  }

  // Agregar tipo de calibración
  formData.append('calibration_type', calibrationData.calibration_type)

  // Agregar datos según tipo
  if (calibrationData.calibration_type === CALIBRATION_TYPES.WEIGHT || 
      calibrationData.calibration_type === CALIBRATION_TYPES.FULL) {
    formData.append('reference_weight', calibrationData.reference_weight.toString())
  }

  if (calibrationData.calibration_type === CALIBRATION_TYPES.SIZE || 
      calibrationData.calibration_type === CALIBRATION_TYPES.FULL) {
    formData.append('reference_length', calibrationData.reference_length.toString())
    formData.append('reference_width', calibrationData.reference_width.toString())
    formData.append('reference_thickness', calibrationData.reference_thickness.toString())
  }

  // Agregar notas si existen
  if (calibrationData.notes) {
    formData.append('notes', calibrationData.notes)
  }

  // Timestamp
  formData.append('timestamp', new Date().toISOString())

  return formData
}

/**
 * Verifica si la calibración está vigente
 * @param {Object} calibrationStatus - Estado de calibración
 * @returns {boolean} - True si está vigente
 */
export function isCalibrationValid(calibrationStatus) {
  if (!calibrationStatus || !calibrationStatus.is_calibrated) {
    return false
  }

  if (calibrationStatus.status === CALIBRATION_STATUS.EXPIRED) {
    return false
  }

  // Verificar fecha de expiración si existe
  if (calibrationStatus.expiration_date) {
    const expirationDate = new Date(calibrationStatus.expiration_date)
    return expirationDate > new Date()
  }

  return true
}

/**
 * Calcula el tiempo restante de calibración
 * @param {Object} calibrationStatus - Estado de calibración
 * @returns {Object} - Información de tiempo restante
 */
export function getCalibrationTimeRemaining(calibrationStatus) {
  if (!calibrationStatus || !calibrationStatus.expiration_date) {
    return {
      valid: false,
      message: 'No hay calibración activa'
    }
  }

  const now = new Date()
  const expirationDate = new Date(calibrationStatus.expiration_date)
  const diffMs = expirationDate - now

  if (diffMs <= 0) {
    return {
      valid: false,
      expired: true,
      message: 'La calibración ha expirado'
    }
  }

  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))

  return {
    valid: true,
    expired: false,
    days: diffDays,
    hours: diffHours,
    message: diffDays > 0 
      ? `${diffDays} día(s) y ${diffHours} hora(s) restantes`
      : `${diffHours} hora(s) restantes`,
    percentage: Math.max(0, Math.min(100, (diffMs / (30 * 24 * 60 * 60 * 1000)) * 100)) // Asumiendo 30 días de validez
  }
}

/**
 * Configuración del servicio de calibración
 */
export const CALIBRATION_CONFIG = {
  // Intervalo de actualización de estado (ms)
  STATUS_REFRESH_INTERVAL: 60000, // 1 minuto
  
  // Duración típica de calibración (días)
  DEFAULT_CALIBRATION_VALIDITY_DAYS: 30,
  
  // Límites de valores de referencia
  LIMITS: {
    WEIGHT: { min: 0.1, max: 10 },      // gramos
    LENGTH: { min: 5, max: 50 },         // mm
    WIDTH: { min: 3, max: 30 },          // mm
    THICKNESS: { min: 2, max: 20 }       // mm
  },
  
  // Colores por estado
  STATUS_COLORS: {
    not_calibrated: 'gray',
    calibrated: 'green',
    expired: 'red',
    in_progress: 'yellow'
  },
  
  // Iconos por estado
  STATUS_ICONS: {
    not_calibrated: 'exclamation-circle',
    calibrated: 'check-circle',
    expired: 'times-circle',
    in_progress: 'spinner'
  }
}

// Exportación por defecto
export default {
  getCalibrationStatus,
  performCalibration,
  scanWithCalibration,
  validateCalibrationData,
  createCalibrationFormData,
  isCalibrationValid,
  getCalibrationTimeRemaining,
  CALIBRATION_TYPES,
  CALIBRATION_STATUS,
  CALIBRATION_CONFIG
}

