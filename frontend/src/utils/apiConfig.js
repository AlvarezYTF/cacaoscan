/**
 * Configuración centralizada del API para CacaoScan
 * 
 * Maneja la URL del API en diferentes entornos:
 * - Producción: Runtime injection o build-time variable
 * - Desarrollo: localhost
 * 
 * Prioridad de configuración:
 * 1. Runtime injection (window.__API_BASE_URL__) - mejor para producción
 * 2. Build-time variable (VITE_API_BASE_URL) - para builds estáticos
 * 3. Fallback localhost - solo para desarrollo local
 */

/**
 * Check if globalThis is available
 * @returns {boolean} true if globalThis is available
 */
function isGlobalThisAvailable() {
  return typeof globalThis === 'object' && globalThis !== null
}

/**
 * Obtiene la URL base del API con prioridad correcta
 * @returns {string} URL base del API
 */
export const getApiBaseUrl = () => {
  // URLs por defecto
  const PRODUCTION_BACKEND_URL = 'https://cacaoscan-backend.onrender.com/api/v1'
  const LOCAL_BACKEND_URL = 'http://localhost:8000/api/v1'
  
  // Prioridad 1: Runtime injection (mejor para producción, permite cambios sin rebuild)
  if (isGlobalThisAvailable() && globalThis.__API_BASE_URL__) {
    let url = globalThis.__API_BASE_URL__
    // Validar y corregir si es relativa
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url
    }
    
    // Si es relativa, construir URL absoluta
    if (url.startsWith('/')) {
      // Es una ruta absoluta relativa al dominio actual
      url = `https://${globalThis.location.hostname}${url}`
      return url
    }
    
    // Usar fallback según entorno
    const isLocalhost = isGlobalThisAvailable() && 
                        globalThis.location?.hostname &&
                        (globalThis.location.hostname.includes('localhost') || 
                         globalThis.location.hostname === '127.0.0.1')
    const fallbackUrl = isLocalhost ? LOCAL_BACKEND_URL : PRODUCTION_BACKEND_URL
    return fallbackUrl
  }
  
  // Prioridad 2: Build-time variable (Vite inyecta esto desde .env)
  const buildTimeUrl = import.meta.env.VITE_API_BASE_URL
  if (buildTimeUrl && buildTimeUrl.trim() !== '') {
    let url = buildTimeUrl.trim()
    // Validar y corregir si es relativa
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url
    }
    
    // Continuar con detección automática
  }
  
  // Prioridad 3: Detección automática según hostname
  if (isGlobalThisAvailable() && globalThis.location?.hostname) {
    const isLocalhost = globalThis.location.hostname.includes('localhost') || 
                        globalThis.location.hostname === '127.0.0.1'
    if (isLocalhost) {
      // En localhost, usar backend local
      return LOCAL_BACKEND_URL
    }
    // En producción, usar URL absoluta
    return PRODUCTION_BACKEND_URL
  }

  // Fallback: si no se puede detectar, usar producción
  return PRODUCTION_BACKEND_URL
}

/**
 * Obtiene la URL base del API sin el path /api/v1
 * Útil para servicios que construyen sus propias rutas
 * @returns {string} URL base del API sin /api/v1
 */
export const getApiBaseUrlWithoutPath = () => {
  const baseUrl = getApiBaseUrl()
  // Remover /api/v1 si está presente
  return baseUrl.replace(/\/api\/v1\/?$/, '')
}

/**
 * Obtiene la URL base del API con /api/v1
 * Asegura que siempre termine con /api/v1
 * @returns {string} URL base del API con /api/v1
 */
export const getApiBaseUrlWithPath = () => {
  const baseUrl = getApiBaseUrl()
  // Si ya termina con /api/v1, retornar tal cual
  if (baseUrl.endsWith('/api/v1') || baseUrl.endsWith('/api/v1/')) {
    return baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl
  }
  // Si no, agregar /api/v1
  return `${baseUrl.replace(/\/$/, '')}/api/v1`
}

/**
 * Detecta si estamos en modo desarrollo
 * @returns {boolean} true si está en desarrollo
 */
export const isDevelopment = () => {
  if (import.meta.env.DEV || import.meta.env.MODE === 'development') {
    return true
  }
  if (isGlobalThisAvailable() && globalThis.location?.hostname === 'localhost') {
    return true
  }
  return false
}

/**
 * Detecta si estamos en modo producción
 * @returns {boolean} true si está en producción
 */
export const isProduction = () => {
  if (import.meta.env.PROD || import.meta.env.MODE === 'production') {
    return true
  }
  if (isGlobalThisAvailable() && globalThis.location?.hostname) {
    const isLocalhost = globalThis.location?.hostname?.includes('localhost') ?? false
    return !isLocalhost
  }
  return false
}

/**
 * Get runtime URL if available
 * @returns {string|null} Runtime URL or null
 */
function getRuntimeUrl() {
  if (!isGlobalThisAvailable()) {
    return null
  }
  return globalThis.__API_BASE_URL__ || null
}

// Exportar configuración actual para debugging
export const API_CONFIG = {
  baseUrl: getApiBaseUrl(),
  baseUrlWithoutPath: getApiBaseUrlWithoutPath(),
  baseUrlWithPath: getApiBaseUrlWithPath(),
  isDev: isDevelopment(),
  isProd: isProduction(),
  runtimeUrl: getRuntimeUrl(),
  buildTimeUrl: import.meta.env.VITE_API_BASE_URL || null,
}

// Log de configuración en desarrollo
if (isDevelopment()) {
  }

