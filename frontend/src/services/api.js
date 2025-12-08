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
    // Validar que baseURL sea una URL absoluta
    if (config.baseURL && !config.baseURL.startsWith('http://') && !config.baseURL.startsWith('https://')) {
      // Invalid baseURL format
    }
    
    return config
  },
  (error) => {
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
  for (const prom of failedRequestsQueue) {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  }
  failedRequestsQueue = []
}

// Helper functions for error handling
const isConfigEndpoint = (url) => url?.includes('/config/')
const isStatsEndpoint = (url) => url?.includes('/stats/')
const isNonCriticalEndpoint = (url) => isConfigEndpoint(url) || isStatsEndpoint(url)

const handleSilent500Error = (originalRequest, error) => {
  // Don't silently handle errors for stats endpoint - we need to see the actual error
  if (error.response?.status === 500 && isNonCriticalEndpoint(originalRequest.url) && !isStatsEndpoint(originalRequest.url)) {
    return {
      data: {},
      status: 200,
      config: originalRequest
    }
  }
  return null
}

const handleAuthEndpointError = (originalRequest) => {
  const authEndpoints = [
    '/auth/login/', 
    '/auth/register/', 
    '/auth/refresh/', 
    '/auth/verify-email/', 
    '/auth/resend-verification/', 
    '/auth/forgot-password/', 
    '/auth/reset-password/', 
    '/auth/send-otp/', 
    '/auth/verify-otp/'
  ]
  const isAuthEndpoint = authEndpoints.some(endpoint => originalRequest.url?.includes(endpoint))
  
  if (isAuthEndpoint && originalRequest.url?.includes('/auth/refresh/')) {
    showSessionExpiredModal()
    throw new Error('Refresh token expired')
  }
  
  return isAuthEndpoint
}

const showSessionExpiredModal = () => {
  if (typeof globalThis !== 'undefined' && globalThis.showSessionExpiredModal) {
    globalThis.showSessionExpiredModal()
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

const handleNoRefreshToken = () => {
  showSessionExpiredModal()
}

const createBaseAxiosInstance = () => {
  return axios.create({
    baseURL: api.defaults.baseURL,
    headers: {
      'Content-Type': 'application/json'
    }
  })
}

const refreshTokenFlow = async (refreshToken) => {
  const baseAxios = createBaseAxiosInstance()
  const response = await baseAxios.post('/auth/refresh/', {
    refresh: refreshToken,
  })
  return response.data
}

const saveTokens = async (accessToken, refreshToken) => {
  localStorage.setItem('access_token', accessToken)
  if (refreshToken) {
    localStorage.setItem('refresh_token', refreshToken)
  }
  api.defaults.headers.Authorization = 'Bearer ' + accessToken
  
  try {
    const authStore = await getAuthStore()
    if (authStore) {
      authStore.setTokens({ access: accessToken, refresh: refreshToken })
    }
  } catch (error) {
    }
}

const handleRefreshSuccess = async (newAccessToken, newRefreshToken, originalRequest) => {
  await saveTokens(newAccessToken, newRefreshToken)
  processQueue(null, newAccessToken)
  
  originalRequest.headers.Authorization = 'Bearer ' + newAccessToken
  return api(originalRequest)
}

const handleRefreshError = (refreshError) => {
  processQueue(refreshError, null)
  showSessionExpiredModal()
  throw refreshError
}

const handle401Error = async (error, originalRequest) => {
  if (error.response?.status !== 401 || originalRequest._retry) {
    return null
  }
  
  const isAuthEndpoint = handleAuthEndpointError(originalRequest)
  if (isAuthEndpoint) {
    throw error
  }
  
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) {
    handleNoRefreshToken()
    throw error
  }
  
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
  
  originalRequest._retry = true
  isRefreshing = true
  
  try {
    const { access: newAccessToken, refresh: newRefreshToken } = await refreshTokenFlow(refreshToken)
    return await handleRefreshSuccess(newAccessToken, newRefreshToken, originalRequest)
  } catch (refreshError) {
    return handleRefreshError(refreshError)
  } finally {
    isRefreshing = false
  }
}

const handle403Error = (error) => {
  if (error.response?.status !== 403) {
    return
  }
  
  const errorMessage = error.response.data?.detail || 'No tienes permisos para realizar esta acción'
  const isConfig = isConfigEndpoint(error.config?.url)
  
  if (!isConfig) {
    }
  
  if (errorMessage.includes('verificada')) {
    router.push({
      name: 'EmailVerification',
      query: { message: errorMessage }
    })
  }
}

const handle429Error = (error) => {
  if (error.response?.status !== 429) {
    return
  }
  
  const errorMessage = error.response.data?.detail || 'Demasiadas solicitudes. Intenta más tarde.'
  if (typeof globalThis !== 'undefined' && globalThis.showNotification) {
    globalThis.showNotification({
      type: 'warning',
      title: 'Límite de solicitudes',
      message: errorMessage,
      duration: 5000
    })
  }
}

const handle500Error = (error, originalRequest) => {
  if (error.response?.status < 500) {
    return
  }
  
  const isConfig = isConfigEndpoint(originalRequest?.url)
  const isStats = isStatsEndpoint(originalRequest?.url)
  
  if (!isConfig && !isStats && typeof globalThis !== 'undefined' && globalThis.showNotification) {
    globalThis.showNotification({
      type: 'error',
      title: 'Error del servidor',
      message: 'Ocurrió un error interno. Por favor intenta más tarde.',
      duration: 8000
    })
  }
}

const handleNetworkError = (error) => {
  if (error.response) {
    return
  }
  
  if (typeof globalThis !== 'undefined' && globalThis.showNotification) {
    globalThis.showNotification({
      type: 'error',
      title: 'Error de conexión',
      message: 'No se pudo conectar al servidor. Verifica tu conexión a internet.',
      duration: 8000
    })
  }
}

// Función para obtener el store de auth dinámicamente
const getAuthStore = async () => {
  // Importación dinámica para evitar dependencias circulares
  try {
    const { useAuthStore } = await import('@/stores/auth')
    return useAuthStore()
  } catch (error) {
    return null
  }
}

// Interceptor de Request (segundo - autenticación y logging)
api.interceptors.request.use(
  (config) => {
    // SIEMPRE actualizar baseURL dinámicamente en cada petición
    const currentApiUrl = getApiBaseUrl()
    
    // Forzar actualización de baseURL si no es una URL absoluta
    if (!currentApiUrl.startsWith('http://') && !currentApiUrl.startsWith('https://')) {
      const fallbackUrl = 'https://cacaoscan-backend.onrender.com/api/v1'
      api.defaults.baseURL = fallbackUrl
      config.baseURL = fallbackUrl
    } else {
      // Actualizar si cambió
      if (api.defaults.baseURL !== currentApiUrl) {
        api.defaults.baseURL = currentApiUrl
      }
      // Asegurar que config.baseURL sea absoluta
      config.baseURL = currentApiUrl
    }
    
    // Validación final: asegurar que config.baseURL sea absoluta
    if (config.baseURL && !config.baseURL.startsWith('http://') && !config.baseURL.startsWith('https://')) {
      config.baseURL = 'https://cacaoscan-backend.onrender.com/api/v1'
    }
    
    // Endpoints de autenticación que NO deben incluir token de autorización
    const authEndpoints = ['/auth/login/', '/auth/register/', '/auth/refresh/', '/auth/verify-email/', '/auth/resend-verification/', '/auth/forgot-password/', '/auth/reset-password/', '/auth/send-otp/', '/auth/verify-otp/']
    const isAuthEndpoint = authEndpoints.some(endpoint => config.url?.includes(endpoint))
    
    // Solo agregar token si NO es un endpoint de autenticación
    if (!isAuthEndpoint) {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    } else {
      // Para endpoints de autenticación, asegurar que NO haya token
      delete config.headers.Authorization
    }

    // Agregar timestamp para debugging
    config.metadata = { startTime: new Date() }

    // Log de request (siempre para debug)
    const fullUrl = config.baseURL ? `${config.baseURL}${config.url}` : config.url

    return config
  },
  (error) => {
    activeRequests = Math.max(0, activeRequests - 1)
    return Promise.reject(error)
  }
)

// Interceptor de Response
api.interceptors.response.use(
  async (response) => {
    // Calcular tiempo de respuesta
    const endTime = new Date()
    const duration = endTime - response.config.metadata.startTime

    // Validar que la respuesta sea JSON, no HTML
    const contentType = response.headers['content-type'] || ''
    if (contentType.includes('text/html')) {
      throw new Error('La respuesta del servidor es HTML en lugar de JSON. Verifica que baseURL esté configurada correctamente.')
    }

    // Actualizar actividad del usuario
    try {
      const authStore = await getAuthStore()
      if (authStore && authStore.isAuthenticated) {
        authStore.updateLastActivity()
      }
    } catch (error) {
      // Log error for debugging transparency - activity update is non-critical
    }

    return response
  },
  async (error) => {
    const originalRequest = error.config

    // Handle silent 500 errors for non-critical endpoints
    if (originalRequest.metadata) {
      const silentError = handleSilent500Error(originalRequest, error)
      if (silentError) {
        return silentError
      }
    }

    // Handle 401 errors (refresh token flow)
    const refreshResult = await handle401Error(error, originalRequest)
    if (refreshResult !== null) {
      return refreshResult
    }

    // Handle other error types
    handle403Error(error)
    handle429Error(error)
    handle500Error(error, originalRequest)
    handleNetworkError(error)

    throw error
  }
)

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
    globalThis.dispatchEvent(new CustomEvent('api-loading-start', {
      detail: { type: 'prediction', message: 'Analizando imagen de cacao...' }
    }))

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
    
    // Ensure error exists before accessing its properties
    if (error) {
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail
      } else if (error.message) {
        errorMessage = error.message
      }
    }

    // Crear error personalizado con información útil
    const customError = new Error(errorMessage)
    if (error) {
      customError.originalError = error
      customError.status = error.response?.status
      customError.statusText = error.response?.statusText
    }

    throw customError

  } finally {
    // Emitir evento de fin de loading
    globalThis.dispatchEvent(new CustomEvent('api-loading-end'))
  }
}

// Re-export validateImageFile from utils for backward compatibility
export { validateImageFileObject as validateImageFile } from '@/utils/imageValidationUtils'

// Exportar configuraciones útiles
export const API_CONFIG = {
  BASE_URL: api.defaults.baseURL,
  TIMEOUT: api.defaults.timeout,
  HEADERS: api.defaults.headers
}

export default api
