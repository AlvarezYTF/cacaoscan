/**
 * Centralized API error handling
 * Provides consistent error message extraction and formatting
 */
import { extractErrorMessage, extractValidationErrors } from './apiClient'
import { logger } from '@/utils/logger'

/**
 * HTTP status codes constants
 */
const HTTP_STATUS_UNAUTHORIZED = 401
const HTTP_STATUS_FORBIDDEN = 403
const HTTP_STATUS_NOT_FOUND = 404
const HTTP_STATUS_BAD_REQUEST = 400
const HTTP_STATUS_UNPROCESSABLE_ENTITY = 422
const HTTP_STATUS_INTERNAL_SERVER_ERROR = 500

/**
 * Error types for better error handling
 */
export const API_ERROR_TYPES = {
  NETWORK: 'network',
  TIMEOUT: 'timeout',
  VALIDATION: 'validation',
  AUTHENTICATION: 'authentication',
  AUTHORIZATION: 'authorization',
  NOT_FOUND: 'not_found',
  SERVER: 'server',
  UNKNOWN: 'unknown'
}

/**
 * Determine error type from error object
 * @param {Error} error - Error object
 * @returns {string} Error type
 */
export const getErrorType = (error) => {
  // Network errors
  if (error.message?.includes('Network Error') || error.message?.includes('Failed to fetch')) {
    return API_ERROR_TYPES.NETWORK
  }

  // Timeout errors
  if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
    return API_ERROR_TYPES.TIMEOUT
  }

  // HTTP status based errors
  if (error.response) {
    const status = error.response.status

    if (status === HTTP_STATUS_UNAUTHORIZED) {
      return API_ERROR_TYPES.AUTHENTICATION
    }

    if (status === HTTP_STATUS_FORBIDDEN) {
      return API_ERROR_TYPES.AUTHORIZATION
    }

    if (status === HTTP_STATUS_NOT_FOUND) {
      return API_ERROR_TYPES.NOT_FOUND
    }

    if (status === HTTP_STATUS_UNPROCESSABLE_ENTITY || status === HTTP_STATUS_BAD_REQUEST) {
      return API_ERROR_TYPES.VALIDATION
    }

    if (status >= HTTP_STATUS_INTERNAL_SERVER_ERROR) {
      return API_ERROR_TYPES.SERVER
    }
  }

  // Check for validation errors in response data
  if (error.response?.data?.details || error.data?.details) {
    return API_ERROR_TYPES.VALIDATION
  }

  return API_ERROR_TYPES.UNKNOWN
}

/**
 * Get user-friendly error message
 * @param {Error} error - Error object
 * @param {string} defaultMessage - Default message
 * @returns {string} User-friendly error message
 */
export const getErrorMessage = (error, defaultMessage = 'Error inesperado') => {
  const errorType = getErrorType(error)

  switch (errorType) {
    case API_ERROR_TYPES.NETWORK:
      return 'Error de conexión. Verifica tu conexión a internet.'
    case API_ERROR_TYPES.TIMEOUT:
      return 'La solicitud tardó demasiado. Intenta nuevamente.'
    case API_ERROR_TYPES.AUTHENTICATION:
      return 'Tu sesión ha expirado. Por favor inicia sesión nuevamente.'
    case API_ERROR_TYPES.AUTHORIZATION:
      return 'No tienes permisos para realizar esta acción.'
    case API_ERROR_TYPES.NOT_FOUND:
      return 'El recurso solicitado no fue encontrado.'
    case API_ERROR_TYPES.SERVER:
      return 'Error del servidor. Por favor intenta más tarde.'
    case API_ERROR_TYPES.VALIDATION:
      return extractErrorMessage(error, defaultMessage)
    default:
      return extractErrorMessage(error, defaultMessage)
  }
}

/**
 * Get validation errors as object
 * @param {Error} error - Error object
 * @returns {Object} Validation errors object
 */
export const getValidationErrors = (error) => {
  return extractValidationErrors(error)
}

/**
 * Check if error is a validation error
 * @param {Error} error - Error object
 * @returns {boolean} True if validation error
 */
export const isValidationError = (error) => {
  return getErrorType(error) === API_ERROR_TYPES.VALIDATION
}

/**
 * Check if error is an authentication error
 * @param {Error} error - Error object
 * @returns {boolean} True if authentication error
 */
export const isAuthenticationError = (error) => {
  return getErrorType(error) === API_ERROR_TYPES.AUTHENTICATION
}

/**
 * Handle API error with logging and user notification
 * @param {Error} error - Error object
 * @param {Object} options - Options
 * @param {Function} options.onError - Error callback
 * @param {boolean} options.logError - Log error (default: true)
 * @returns {Object} Error information
 */
export const handleApiError = (error, options = {}) => {
  const {
    onError = null,
    logError = true
  } = options

  const errorType = getErrorType(error)
  const message = getErrorMessage(error)
  const validationErrors = isValidationError(error) ? getValidationErrors(error) : null

  if (logError) {
    logger.error(`[API Error] ${errorType}:`, {
      message,
      error,
      validationErrors
    })
  }

  const errorInfo = {
    type: errorType,
    message,
    validationErrors,
    originalError: error
  }

  if (onError && typeof onError === 'function') {
    onError(errorInfo)
  }

  return errorInfo
}

