/**
 * Configuración principal de Axios para CacaoScan
 * Incluye interceptores para Token Authentication, manejo de errores y rate limiting
 */

import axios from 'axios'
import router from '@/router'

// Configuración base de Axios
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000, // 30 segundos
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Variables para manejar el refresh token concurrente
let isRefreshing = false
let failedRequestsQueue = []

// Función para procesar la cola de peticiones fallidas
const processQueue = (error, token = null) => {
  failedRequestsQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedRequestsQueue = []
}

// Función para obtener el store de auth dinámicamente
const getAuthStore = () => {
  // Importación dinámica para evitar dependencias circulares
  const { useAuthStore } = require('@/stores/auth')
  return useAuthStore()
}

// Interceptor de Request
api.interceptors.request.use(
  (config) => {
    // Obtener token de localStorage
    const token = localStorage.getItem('access_token')
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Agregar timestamp para debugging
    config.metadata = { startTime: new Date() }

    // Log de request en desarrollo
    if (import.meta.env.DEV) {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
        data: config.data,
        params: config.params
      })
    }

    return config
  },
  (error) => {
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  }
)

// Interceptor de Response
api.interceptors.response.use(
  (response) => {
    // Calcular tiempo de respuesta
    const endTime = new Date()
    const duration = endTime - response.config.metadata.startTime

    // Log de response en desarrollo
    if (import.meta.env.DEV) {
      console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        duration: `${duration}ms`,
        data: response.data
      })
    }

    // Actualizar actividad del usuario
    try {
      const authStore = getAuthStore()
      if (authStore.isAuthenticated) {
        authStore.updateLastActivity()
      }
    } catch (error) {
      // Ignorar errores del store en caso de que no esté disponible
    }

    return response
  },
  async (error) => {
    const originalRequest = error.config

    // Calcular tiempo de error
    if (originalRequest.metadata) {
      const endTime = new Date()
      const duration = endTime - originalRequest.metadata.startTime
      
      // Endpoints que pueden fallar normalmente (configuración, stats)
      const isConfigEndpoint = originalRequest.url?.includes('/config/')
      const isStatsEndpoint = originalRequest.url?.includes('/stats/')
      
      // Determinar si es un error esperado (500 o 403 en endpoints no críticos)
      const isExpectedFailure = (isConfigEndpoint || isStatsEndpoint) && 
                                 (error.response?.status === 403 || error.response?.status === 500)
      
      // Solo loggear errores críticos o no esperados
      if (!isExpectedFailure) {
        console.error(`❌ API Error: ${originalRequest.method?.toUpperCase()} ${originalRequest.url}`, {
          status: error.response?.status,
          duration: `${duration}ms`,
          message: error.response?.data?.message || error.response?.data?.detail || error.message
        })
      }
    }

    // Manejar errores 401 (No autorizado) - JWT Refresh Token Flow
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Verificar si es un endpoint de auth que no requiere manejo especial
      const authEndpoints = ['/auth/login/', '/auth/register/', '/auth/refresh/']
      const isAuthEndpoint = authEndpoints.some(endpoint => 
        originalRequest.url.includes(endpoint)
      )

      if (isAuthEndpoint) {
        // Si falla en el refresh token, limpiar todo y redirigir
        if (originalRequest.url.includes('/auth/refresh/')) {
          console.error('🚫 Refresh token inválido o expirado, cerrando sesión.')
          localStorage.clear()
          router.replace({ 
            name: 'Login',
            query: {
              message: 'Tu sesión ha expirado. Por favor inicia sesión nuevamente.',
              expired: 'true'
            }
          })
        }
        return Promise.reject(error)
      }

      const refreshToken = localStorage.getItem('refresh_token')

      // Si no hay refresh token → cerrar sesión
      if (!refreshToken) {
        console.warn('⚠️ No hay refresh token disponible, redirigiendo a login...')
        localStorage.clear()
        router.replace({ 
          name: 'Login',
          query: {
            message: 'Tu sesión ha expirado. Inicia sesión nuevamente.',
            expired: 'true'
          }
        })
        return Promise.reject(error)
      }

      // Si ya se está refrescando, agregar a la cola
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedRequestsQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers.Authorization = 'Bearer ' + token
          return api(originalRequest)
        }).catch(err => {
          return Promise.reject(err)
        })
      }

      // Marcar que estamos refrescando
      originalRequest._retry = true
      isRefreshing = true

      // Crear instancia base de axios sin interceptores para evitar loops
      const baseAxios = axios.create({
        baseURL: api.defaults.baseURL,
        headers: {
          'Content-Type': 'application/json'
        }
      })

      try {
        // Intentar refrescar el token
        const response = await baseAxios.post('/auth/refresh/', {
          refresh: refreshToken,
        })

        const newAccessToken = response.data.access
        const newRefreshToken = response.data.refresh

        // Guardar los nuevos tokens
        localStorage.setItem('access_token', newAccessToken)
        if (newRefreshToken) {
          localStorage.setItem('refresh_token', newRefreshToken)
        }

        // Actualizar header por defecto
        api.defaults.headers.Authorization = 'Bearer ' + newAccessToken

        // Actualizar el token en el store
        const authStore = getAuthStore()
        authStore.setTokens({ access: newAccessToken, refresh: newRefreshToken })

        console.log('🔄 Token JWT refrescado automáticamente')

        // Procesar la cola de peticiones fallidas
        processQueue(null, newAccessToken)

        // Reintentar la petición original con el nuevo token
        originalRequest.headers.Authorization = 'Bearer ' + newAccessToken
        return api(originalRequest)
      } catch (refreshError) {
        console.error('❌ Error refrescando token:', refreshError)
        
        // Procesar la cola con error
        processQueue(refreshError, null)

        // Si el refresh falla, limpiar todo y redirigir
        localStorage.clear()
        router.replace({ 
          name: 'Login',
          query: {
            message: 'Tu sesión ha expirado. Por favor inicia sesión nuevamente.',
            expired: 'true'
          }
        })
        
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // Manejar errores 403 (Prohibido)
    if (error.response?.status === 403) {
      const errorMessage = error.response.data?.detail || 'No tienes permisos para realizar esta acción'
      const isConfigEndpoint = originalRequest?.url?.includes('/config/')
      
      // Solo mostrar notificación para endpoints críticos
      if (!isConfigEndpoint) {
        console.warn('🚫 Acceso denegado:', errorMessage)
      }
      
      // Si es falta de verificación, redirigir a página de verificación
      if (errorMessage.includes('verificada')) {
        router.push({
          name: 'EmailVerification',
          query: { message: errorMessage }
        })
      }
    }

    // Manejar errores 429 (Rate Limited)
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after']
      const errorMessage = error.response.data?.detail || 'Demasiadas solicitudes. Intenta más tarde.'
      
      console.warn('🐌 Rate limited:', errorMessage, retryAfter ? `Reintentar en ${retryAfter}s` : '')
      
      // Mostrar notificación específica para rate limiting
      if (typeof window !== 'undefined' && window.showNotification) {
        window.showNotification({
          type: 'warning',
          title: 'Límite de solicitudes',
          message: errorMessage,
          duration: 5000
        })
      }
    }

    // Manejar errores 500 (Error del servidor)
    if (error.response?.status >= 500) {
      const isConfigEndpoint = originalRequest?.url?.includes('/config/')
      const isStatsEndpoint = originalRequest?.url?.includes('/stats/')
      
      // No mostrar notificación para endpoints de configuración o estadísticas
      if (!isConfigEndpoint && !isStatsEndpoint) {
        console.error('🔥 Server Error:', error.response?.data)
        
        if (typeof window !== 'undefined' && window.showNotification) {
          window.showNotification({
            type: 'error',
            title: 'Error del servidor',
            message: 'Ocurrió un error interno. Por favor intenta más tarde.',
            duration: 8000
          })
        }
      }
    }

    // Manejar errores de red
    if (!error.response) {
      console.error('🌐 Network Error:', error.message)
      
      if (typeof window !== 'undefined' && window.showNotification) {
        window.showNotification({
          type: 'error',
          title: 'Error de conexión',
          message: 'No se pudo conectar al servidor. Verifica tu conexión a internet.',
          duration: 8000
        })
      }
    }

    return Promise.reject(error)
  }
)

// Función helper para crear requests con manejo de archivos
export const createFormDataRequest = (data, progressCallback) => {
  const formData = new FormData()
  
  Object.keys(data).forEach(key => {
    if (data[key] !== null && data[key] !== undefined) {
      formData.append(key, data[key])
    }
  })

  const config = {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }

  if (progressCallback) {
    config.onUploadProgress = (progressEvent) => {
      const progress = Math.round(
        (progressEvent.loaded * 100) / progressEvent.total
      )
      progressCallback(progress)
    }
  }

  return { formData, config }
}

// Función helper para manejar timeouts específicos
export const createTimeoutRequest = (timeoutMs) => {
  return axios.create({
    ...api.defaults,
    timeout: timeoutMs
  })
}

// Función helper para requests sin interceptores (útil para refresh token)
export const createBaseRequest = () => {
  return axios.create({
    baseURL: api.defaults.baseURL,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  })
}

/**
 * Realiza predicción de características físicas de un grano de cacao
 * @param {FormData} formData - Datos del formulario con la imagen y metadatos
 * @returns {Promise<Object>} - Resultado de la predicción con peso, altura, ancho y grosor
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
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp']
    if (!allowedTypes.includes(imageFile.type)) {
      throw new Error('Formato de imagen no válido. Use JPEG, PNG, WebP o BMP')
    }

    // Validar tamaño máximo (20MB)
    const maxSize = 20 * 1024 * 1024
    if (imageFile.size > maxSize) {
      throw new Error('La imagen es demasiado grande. Máximo 20MB permitido')
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

    // Realizar la petición al endpoint de predicción
    const response = await api.post('/api/predict/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 60000 // 60 segundos para procesamiento ML
    })

    console.log('✅ Predicción completada:', response.data)

    return response.data

  } catch (error) {
    console.error('❌ Error al predecir imagen:', error)
    
    // Extraer mensaje de error más descriptivo
    let errorMessage = 'Error inesperado al procesar la imagen'
    
    if (error.response?.data?.error) {
      errorMessage = error.response.data.error
    } else if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail
    } else if (error.message) {
      errorMessage = error.message
    }

    // Crear error personalizado con información útil
    const customError = new Error(errorMessage)
    customError.originalError = error
    customError.status = error.response?.status
    customError.statusText = error.response?.statusText

    throw customError

  } finally {
    // Emitir evento de fin de loading
    window.dispatchEvent(new CustomEvent('api-loading-end'))
  }
}

/**
 * Función auxiliar para crear FormData para predicción
 * @param {File} file - Archivo de imagen
 * @param {Object} metadata - Metadatos adicionales (opcional)
 * @returns {FormData} - FormData preparado para envío
 */
export function createPredictionFormData(file, metadata = {}) {
  const formData = new FormData()
  
  // Agregar archivo de imagen
  formData.append('image', file)
  
  // Agregar metadatos si se proporcionan
  if (metadata.lote_id) {
    formData.append('lote_id', metadata.lote_id)
  }
  
  if (metadata.finca) {
    formData.append('finca', metadata.finca)
  }
  
  if (metadata.region) {
    formData.append('region', metadata.region)
  }
  
  if (metadata.variedad) {
    formData.append('variedad', metadata.variedad)
  }
  
  if (metadata.fecha_cosecha) {
    formData.append('fecha_cosecha', metadata.fecha_cosecha)
  }
  
  if (metadata.notas) {
    formData.append('notas', metadata.notas)
  }
  
  // Agregar información técnica del archivo
  formData.append('file_name', file.name)
  formData.append('file_size', file.size.toString())
  formData.append('file_type', file.type)
  
  // Timestamp para auditoría
  formData.append('upload_timestamp', new Date().toISOString())
  
  return formData
}

/**
 * Función auxiliar para validar archivos de imagen
 * @param {File} file - Archivo a validar
 * @returns {Object} - Objeto con isValid y errors
 */
export function validateImageFile(file) {
  const errors = []

  if (!file) {
    errors.push('Archivo requerido')
    return { isValid: false, errors }
  }

  // Validar tipo
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp']
  if (!allowedTypes.includes(file.type)) {
    errors.push('Formato no válido. Use JPEG, PNG, WebP o BMP')
  }

  // Validar tamaño (20MB máximo)
  const maxSize = 20 * 1024 * 1024
  if (file.size > maxSize) {
    errors.push('Archivo demasiado grande. Máximo 20MB')
  }

  // Validar tamaño mínimo (1KB)
  const minSize = 1024
  if (file.size < minSize) {
    errors.push('Archivo demasiado pequeño')
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}

// Exportar configuraciones útiles
export const API_CONFIG = {
  BASE_URL: api.defaults.baseURL,
  TIMEOUT: api.defaults.timeout,
  HEADERS: api.defaults.headers
}

export default api
