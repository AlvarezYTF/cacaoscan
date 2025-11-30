/**
 * Unified HTTP client with error handling and response formatting
 * Centralizes all HTTP request logic to eliminate duplication
 */
import axios from 'axios'
import router from '@/router'
import { getApiBaseUrl } from '@/utils/apiConfig'
import { extractErrorMessage } from '@/utils/apiErrorHandler'
import { normalizeApiResponse } from '@/utils/apiResponseFormatter'

/**
 * Creates a standardized error object
 * @param {Error} error - Axios error
 * @returns {Object} Standardized error
 */
function createStandardError(error) {
  const message = extractErrorMessage(error)
  const status = error.response?.status || 0
  const data = error.response?.data || {}

  const standardError = new Error(message)
  standardError.status = status
  standardError.data = data
  standardError.originalError = error
  
  return standardError
}

/**
 * Creates and configures the HTTP client
 * @returns {AxiosInstance} Configured axios instance
 */
function createHttpClient() {
  const apiBaseUrl = getApiBaseUrl()

  const client = axios.create({
    baseURL: apiBaseUrl,
    timeout: 15000,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  })

  // Request interceptor - Add auth token
  client.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('auth_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error) => {
      const standardError = error instanceof Error ? error : createStandardError(error)
      return Promise.reject(standardError instanceof Error ? standardError : new Error(String(standardError)))
    }
  )

  // Response interceptor - Format responses and handle errors
  client.interceptors.response.use(
    (response) => {
      // Normalize successful response
      return {
        ...response,
        data: normalizeApiResponse(response.data, false)
      }
    },
    (error) => {
      const standardError = createStandardError(error)

      // Handle specific status codes
      if (error.response) {
        switch (error.response.status) {
          case 401:
            // Unauthorized - clear auth and redirect to login
            localStorage.removeItem('auth_token')
            localStorage.removeItem('refresh_token')
            localStorage.removeItem('user_data')
            router.push('/login')
            break

          case 403:
            // Forbidden - show access denied
            console.warn('Access denied:', standardError.message)
            break

          case 404:
            // Not found
            console.warn('Resource not found:', standardError.message)
            break

          case 422:
            // Validation error - return error with details
            break

          case 500:
            // Server error
            console.error('Server error:', standardError.message)
            break

          default:
            console.error('API error:', standardError.message)
        }
      } else if (error.request) {
        // Network error
        standardError.message = 'Error de conexión. Verifica tu conexión a internet.'
      } else {
        // Request setup error
        standardError.message = 'Error al configurar la petición.'
      }

      return Promise.reject(standardError instanceof Error ? standardError : new Error(String(standardError)))
    }
  )

  return client
}

// Create singleton instance
const httpClient = createHttpClient()

/**
 * GET request
 * @param {string} url - Request URL
 * @param {Object} config - Axios config
 * @returns {Promise} Response promise
 */
export const get = async (url, config = {}) => {
  try {
    const response = await httpClient.get(url, config)
    return response.data
  } catch (error) {
    throw createStandardError(error)
  }
}

/**
 * POST request
 * @param {string} url - Request URL
 * @param {Object} data - Request data
 * @param {Object} config - Axios config
 * @returns {Promise} Response promise
 */
export const post = async (url, data = {}, config = {}) => {
  try {
    const response = await httpClient.post(url, data, config)
    return response.data
  } catch (error) {
    throw createStandardError(error)
  }
}

/**
 * PUT request
 * @param {string} url - Request URL
 * @param {Object} data - Request data
 * @param {Object} config - Axios config
 * @returns {Promise} Response promise
 */
export const put = async (url, data = {}, config = {}) => {
  try {
    const response = await httpClient.put(url, data, config)
    return response.data
  } catch (error) {
    throw createStandardError(error)
  }
}

/**
 * PATCH request
 * @param {string} url - Request URL
 * @param {Object} data - Request data
 * @param {Object} config - Axios config
 * @returns {Promise} Response promise
 */
export const patch = async (url, data = {}, config = {}) => {
  try {
    const response = await httpClient.patch(url, data, config)
    return response.data
  } catch (error) {
    throw createStandardError(error)
  }
}

/**
 * DELETE request
 * @param {string} url - Request URL
 * @param {Object} config - Axios config
 * @returns {Promise} Response promise
 */
export const del = async (url, config = {}) => {
  try {
    const response = await httpClient.delete(url, config)
    return response.data
  } catch (error) {
    throw createStandardError(error)
  }
}

/**
 * Upload file request
 * @param {string} url - Request URL
 * @param {FormData} formData - Form data with file
 * @param {Function} onProgress - Progress callback
 * @returns {Promise} Response promise
 */
export const upload = async (url, formData, onProgress = null) => {
  try {
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }

    if (onProgress) {
      config.onUploadProgress = (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(percentCompleted)
      }
    }

    const response = await httpClient.post(url, formData, config)
    return response.data
  } catch (error) {
    throw createStandardError(error)
  }
}

/**
 * Download file request
 * @param {string} url - Request URL
 * @param {Object} config - Axios config
 * @returns {Promise} Response promise
 */
export const download = async (url, config = {}) => {
  try {
    const response = await httpClient.get(url, {
      ...config,
      responseType: 'blob'
    })
    return response
  } catch (error) {
    throw createStandardError(error)
  }
}

// Export the client instance for advanced usage
export { httpClient }

// Export default object with all methods
export default {
  get,
  post,
  put,
  patch,
  delete: del,
  upload,
  download,
  client: httpClient
}

