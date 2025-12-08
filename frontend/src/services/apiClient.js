/**
 * Unified API client for common request patterns
 * Provides consistent error handling, loading states, and response transformation
 * 
 * This is a wrapper that can be used alongside existing api.js, datasetApi.js, and adminApi.js
 * for gradual migration to a unified approach
 */

import api from './api'
import { getApiBaseUrlWithoutPath } from '@/utils/apiConfig'

const API_BASE_URL = getApiBaseUrlWithoutPath()

/**
 * Common headers for API requests
 * @returns {Object} Headers object
 */
const getCommonHeaders = () => {
  const headers = {
    'Content-Type': 'application/json'
  }
  
  const token = localStorage.getItem('access_token') || localStorage.getItem('token')
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  
  return headers
}

/**
 * Builds query parameters from filters object
 * @param {Object} filters - Filters object
 * @returns {URLSearchParams} Query parameters
 */
const buildQueryParams = (filters = {}) => {
  const params = new URLSearchParams()
  
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== null && value !== '') {
      if (Array.isArray(value)) {
        for (const item of value) {
          params.append(key, item)
        }
      } else {
        params.append(key, value)
      }
    }
  }
  
  return params
}

/**
 * Handles API response consistently
 * @param {Response} response - Fetch response
 * @returns {Promise<Object>} Parsed response data
 */
const handleResponse = async (response) => {
  const contentType = response.headers.get('content-type')
  
  if (contentType?.includes('application/json')) {
    const data = await response.json()
    
    if (!response.ok) {
      const error = new Error(data.message || data.error || data.detail || `HTTP ${response.status}: ${response.statusText}`)
      error.status = response.status
      error.data = data
      throw error
    }
    
    return data
  }
  
  if (!response.ok) {
    const error = new Error(`HTTP ${response.status}: ${response.statusText}`)
    error.status = response.status
    throw error
  }
  
  return await response.text()
}

/**
 * Makes a GET request using axios (from api.js)
 * @param {string} endpoint - API endpoint
 * @param {Object} params - Query parameters
 * @param {Object} options - Additional options
 * @returns {Promise<Object>} Response data
 */
export const apiGet = async (endpoint, params = {}, options = {}) => {
  try {
    const response = await api.get(endpoint, { params, ...options })
    return response.data
  } catch (error) {
    throw error
  }
}

/**
 * Makes a POST request using axios
 * @param {string} endpoint - API endpoint
 * @param {Object} data - Request body
 * @param {Object} options - Additional options
 * @returns {Promise<Object>} Response data
 */
export const apiPost = async (endpoint, data = {}, options = {}) => {
  try {
    const response = await api.post(endpoint, data, options)
    return response.data
  } catch (error) {
    throw error
  }
}

/**
 * Makes a PATCH request using axios
 * @param {string} endpoint - API endpoint
 * @param {Object} data - Request body
 * @param {Object} options - Additional options
 * @returns {Promise<Object>} Response data
 */
export const apiPatch = async (endpoint, data = {}, options = {}) => {
  try {
    const response = await api.patch(endpoint, data, options)
    return response.data
  } catch (error) {
    throw error
  }
}

/**
 * Makes a PUT request using axios
 * @param {string} endpoint - API endpoint
 * @param {Object} data - Request body
 * @param {Object} options - Additional options
 * @returns {Promise<Object>} Response data
 */
export const apiPut = async (endpoint, data = {}, options = {}) => {
  try {
    const response = await api.put(endpoint, data, options)
    return response.data
  } catch (error) {
    throw error
  }
}

/**
 * Makes a DELETE request using axios
 * @param {string} endpoint - API endpoint
 * @param {Object} options - Additional options
 * @returns {Promise<Object>} Response data
 */
export const apiDelete = async (endpoint, options = {}) => {
  try {
    const response = await api.delete(endpoint, options)
    return response.data
  } catch (error) {
    throw error
  }
}

/**
 * Makes a GET request using fetch (for compatibility with existing code)
 * @param {string} endpoint - API endpoint (relative or absolute)
 * @param {Object} filters - Query parameters
 * @param {Object} options - Additional fetch options
 * @returns {Promise<Object>} Response data
 */
export const fetchGet = async (endpoint, filters = {}, options = {}) => {
  try {
    const queryParams = buildQueryParams(filters)
    const isAbsoluteUrl = endpoint.startsWith('http')
    const baseUrl = isAbsoluteUrl ? endpoint : `${API_BASE_URL}${endpoint}`
    
    let queryString = ''
    if (queryParams.toString()) {
      queryString = `?${queryParams}`
    } else if (isAbsoluteUrl) {
      // For absolute URLs, always add ? to facilitate adding params later
      queryString = '?'
    }
    
    const url = `${baseUrl}${queryString}`
    
    const response = await fetch(url, {
      method: 'GET',
      headers: getCommonHeaders(),
      ...options
    })
    
    return await handleResponse(response)
  } catch (error) {
    throw error
  }
}

/**
 * Makes a POST request using fetch
 * @param {string} endpoint - API endpoint
 * @param {Object} data - Request body
 * @param {Object} options - Additional fetch options
 * @returns {Promise<Object>} Response data
 */
export const fetchPost = async (endpoint, data = {}, options = {}) => {
  try {
    const url = endpoint.startsWith('http') 
      ? endpoint
      : `${API_BASE_URL}${endpoint}`
    
    const response = await fetch(url, {
      method: 'POST',
      headers: getCommonHeaders(),
      body: JSON.stringify(data),
      ...options
    })
    
    return await handleResponse(response)
  } catch (error) {
    throw error
  }
}

/**
 * Makes a PATCH request using fetch
 * @param {string} endpoint - API endpoint
 * @param {Object} data - Request body
 * @param {Object} options - Additional fetch options
 * @returns {Promise<Object>} Response data
 */
export const fetchPatch = async (endpoint, data = {}, options = {}) => {
  try {
    const url = endpoint.startsWith('http') 
      ? endpoint
      : `${API_BASE_URL}${endpoint}`
    
    const response = await fetch(url, {
      method: 'PATCH',
      headers: getCommonHeaders(),
      body: JSON.stringify(data),
      ...options
    })
    
    return await handleResponse(response)
  } catch (error) {
    throw error
  }
}

/**
 * Makes a DELETE request using fetch
 * @param {string} endpoint - API endpoint
 * @param {Object} options - Additional fetch options
 * @returns {Promise<Object>} Response data
 */
export const fetchDelete = async (endpoint, options = {}) => {
  try {
    const url = endpoint.startsWith('http') 
      ? endpoint
      : `${API_BASE_URL}${endpoint}`
    
    const response = await fetch(url, {
      method: 'DELETE',
      headers: getCommonHeaders(),
      ...options
    })
    
    return await handleResponse(response)
  } catch (error) {
    throw error
  }
}

/**
 * Extracts error message from error object
 * @param {Error} error - Error object
 * @param {string} defaultMessage - Default error message
 * @returns {string} Error message
 */
export const extractErrorMessage = (error, defaultMessage = 'Error inesperado') => {
  if (error.response?.data) {
    const data = error.response.data
    return data.detail || data.error || data.message || defaultMessage
  }
  
  if (error.data) {
    return error.data.detail || error.data.error || error.data.message || defaultMessage
  }
  
  if (error.message) {
    return error.message
  }
  
  return defaultMessage
}

/**
 * Extracts validation errors from error response
 * @param {Error} error - Error object
 * @returns {Object} Validation errors object
 */
export const extractValidationErrors = (error) => {
  if (error.response?.data?.details) {
    return error.response.data.details
  }
  
  if (error.response?.data) {
    const data = error.response.data
    // Check if it's a validation error object
    if (typeof data === 'object' && !data.message && !data.error) {
      return data
    }
  }
  
  if (error.data?.details) {
    return error.data.details
  }
  
  if (error.data && typeof error.data === 'object' && !error.data.message && !error.data.error) {
    return error.data
  }
  
  return {}
}

/**
 * Creates a paginated request helper
 * @param {Function} requestFn - Request function
 * @param {Object} baseParams - Base parameters
 * @param {Object} pagination - Pagination object from usePagination
 * @returns {Promise<Object>} Response data
 */
export const makePaginatedRequest = async (requestFn, baseParams = {}, pagination = {}) => {
  const params = {
    ...baseParams,
    page: pagination.currentPage || 1,
    page_size: pagination.itemsPerPage || 10
  }
  
  return await requestFn(params)
}

// Export utility functions
export { buildQueryParams, getCommonHeaders, handleResponse }

