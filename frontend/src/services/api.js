/**
 * Configuración principal de Axios para CacaoScan
 * Incluye interceptores para Token Authentication, manejo de errores y rate limiting
 */

import axios from 'axios'
import router from '@/router'
import { getApiBaseUrl } from '@/utils/apiConfig'

// Obtener URL del API (se evalúa en tiempo de importación)
const apiBaseUrl = getApiBaseUrl()

// Log de configuración inicial
console.log('🚀 [API Service] Initializing with baseURL:', apiBaseUrl)

// Configuración base de Axios
const api = axios.create({
  baseURL: apiBaseUrl,
  timeout: 15000, // 15 segundos (reducido para evitar bloqueos)
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Interceptor para loggear todas las peticiones (SIEMPRE en producción para debug)
api.interceptors.request.use(
  (config) => {
    const fullUrl = config.baseURL ? `${config.baseURL}${config.url}` : config.url
    console.log('📤 [API Request]', config.method?.toUpperCase(), fullUrl)
    console.log('📤 [API Request] baseURL:', config.baseURL, 'url:', config.url)
    
    // Validar que baseURL sea una URL absoluta
    if (config.baseURL && !config.baseURL.startsWith('http://') && !config.baseURL.startsWith('https://')) {
      console.error('❌ [API Error] baseURL no es una URL absoluta:', config.baseURL)
      console.error('❌ [API Error] Esto causará que las peticiones vayan al frontend en lugar del backend')
    }
    
    return config
  },
  (error) => {
    console.error('❌ [API Request Error]', error)
    return Promise.reject(error)
  }
)

// Contador de peticiones activas para evitar sobrecarga
let activeRequests = 0
const MAX_CONCURRENT_REQUESTS = 10  // Aumentado de 5 a 10 para permitir más peticiones simultáneas

// Interceptor para limitar peticiones concurrentes (con timeout más corto)
api.interceptors.request.use(
  (config) => {
    // Esperar si hay demasiadas peticiones activas (con timeout más corto)
    if (activeRequests >= MAX_CONCURRENT_REQUESTS) {
      return new Promise((resolve, reject) => {
        let checkInterval = null
        let timeoutId = null
        let resolved = false
        
        const cleanup = () => {
          if (checkInterval) clearInterval(checkInterval)
          if (timeoutId) clearTimeout(timeoutId)
        }
        
        checkInterval = setInterval(() => {
          if (activeRequests < MAX_CONCURRENT_REQUESTS && !resolved) {
            resolved = true
            cleanup()
            activeRequests++
            resolve(config)
          }
        }, 50)  // Verificar cada 50ms (más frecuente)
        
        // Timeout de seguridad más corto (2 segundos en lugar de 5)
        timeoutId = setTimeout(() => {
          if (!resolved) {
            resolved = true
            cleanup()
            activeRequests++
            resolve(config)  // Permitir la petición aunque esté en límite
          }
        }, 2000)
      })
    }
    
    activeRequests++
    return config
  },
  (error) => {
    activeRequests = Math.max(0, activeRequests - 1)
    return Promise.reject(error)
  }
)

// Interceptor de respuesta para decrementar contador
api.interceptors.response.use(
  (response) => {
    activeRequests = Math.max(0, activeRequests - 1)
    return response
  },
  (error) => {
    activeRequests = Math.max(0, activeRequests - 1)
    return Promise.reject(error)
  }
)

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

// Interceptor de Request (segundo - autenticación y logging)
api.interceptors.request.use(
  (config) => {
    // SIEMPRE actualizar baseURL dinámicamente en cada petición
    const currentApiUrl = getApiBaseUrl()
    
    // Forzar actualización de baseURL si no es una URL absoluta
    if (!currentApiUrl.startsWith('http://') && !currentApiUrl.startsWith('https://')) {
      console.error('❌ [API] baseURL no es absoluta, forzando actualización')
      const fallbackUrl = 'https://cacaoscan-backend.onrender.com/api/v1'
      console.warn('⚠️ [API] Usando fallback absoluto:', fallbackUrl)
      api.defaults.baseURL = fallbackUrl
      config.baseURL = fallbackUrl
    } else {
      // Actualizar si cambió
      if (api.defaults.baseURL !== currentApiUrl) {
        console.log('🔄 [API] Updating baseURL from', api.defaults.baseURL, 'to', currentApiUrl)
        api.defaults.baseURL = currentApiUrl
      }
      // Asegurar que config.baseURL sea absoluta
      config.baseURL = currentApiUrl
    }
    
    // Validación final: asegurar que config.baseURL sea absoluta
    if (config.baseURL && !config.baseURL.startsWith('http://') && !config.baseURL.startsWith('https://')) {
      console.error('❌ [API] CRITICAL: baseURL sigue siendo relativa:', config.baseURL)
      console.error('❌ [API] Forzando URL absoluta del backend')
      config.baseURL = 'https://cacaoscan-backend.onrender.com/api/v1'
    }
    
    // Obtener token de localStorage
    const token = localStorage.getItem('access_token')
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Agregar timestamp para debugging
    config.metadata = { startTime: new Date() }

    // Log de request (siempre para debug)
    const fullUrl = config.baseURL ? `${config.baseURL}${config.url}` : config.url
    console.log(`🚀 [API Request] ${config.method?.toUpperCase()} ${fullUrl}`)

    return config
  },
  (error) => {
    activeRequests = Math.max(0, activeRequests - 1)
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

    // Validar que la respuesta sea JSON, no HTML
    const contentType = response.headers['content-type'] || ''
    if (contentType.includes('text/html')) {
      console.error('❌ [API Error] Respuesta es HTML en lugar de JSON!')
      console.error('❌ [API Error] URL:', response.config.baseURL + response.config.url)
      console.error('❌ [API Error] Esto significa que la petición fue interceptada por Nginx del frontend')
      console.error('❌ [API Error] baseURL debería ser:', getApiBaseUrl())
      throw new Error('La respuesta del servidor es HTML en lugar de JSON. Verifica que baseURL esté configurada correctamente.')
    }

    // Log de response
    console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.baseURL}${response.config.url}`, {
      status: response.status,
      duration: `${duration}ms`,
      contentType: contentType
    })

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
      
      // Solo loggear errores críticos o no esperados - silenciado
      
      // Manejar errores 500 para endpoints no críticos silenciosamente
      if (error.response?.status === 500) {
        // No loggear ni mostrar notificación para endpoints de stats o config
        if (isStatsEndpoint || isConfigEndpoint) {
          return {
            data: {},
            status: 200,
            config: originalRequest
          }
        }
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
        // Si falla en el refresh token, mostrar modal
        if (originalRequest.url.includes('/auth/refresh/')) {
          console.error('🚫 Refresh token inválido o expirado, cerrando sesión.')
          if (typeof window !== 'undefined' && window.showSessionExpiredModal) {
            window.showSessionExpiredModal()
          } else {
            localStorage.clear()
            router.replace({ 
              name: 'Login',
              query: {
                message: 'Tu sesión ha expirado. Por favor inicia sesión nuevamente.',
                expired: 'true'
              }
            })
          }
        }
        throw error
      }

      const refreshToken = localStorage.getItem('refresh_token')

      // Si no hay refresh token → mostrar modal
      if (!refreshToken) {
        console.warn('⚠️ No hay refresh token disponible, mostrando modal...')
        if (typeof window !== 'undefined' && window.showSessionExpiredModal) {
          window.showSessionExpiredModal()
        } else {
          localStorage.clear()
          router.replace({ 
            name: 'Login',
            query: {
              message: 'Tu sesión ha expirado. Inicia sesión nuevamente.',
              expired: 'true'
            }
          })
        }
        throw error
      }

      // Si ya se está refrescando, agregar a la cola
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedRequestsQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers.Authorization = 'Bearer ' + token
          return api(originalRequest)
        }).catch(err => {
          throw err
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

        // Si el refresh falla, mostrar modal de sesión expirada
        if (typeof window !== 'undefined' && window.showSessionExpiredModal) {
          window.showSessionExpiredModal()
        } else {
          // Fallback de redirección directa si no hay modal disponible
          localStorage.clear()
          router.replace({ 
            name: 'Login',
            query: {
              message: 'Tu sesión ha expirado. Por favor inicia sesión nuevamente.',
              expired: 'true'
            }
          })
        }
        
        throw refreshError
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
      if (typeof window !== 'undefined' && window.showNotification) {
        window.showNotification({
          type: 'error',
          title: 'Error de conexión',
          message: 'No se pudo conectar al servidor. Verifica tu conexión a internet.',
          duration: 8000
        })
      }
    }

    throw error
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

    return response.data

  } catch (error) {
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
