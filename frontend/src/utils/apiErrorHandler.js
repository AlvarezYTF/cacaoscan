/**
 * Utility functions for consistent API error handling
 * Provides reusable error extraction and handling to eliminate code duplication
 */

/**
 * Extracts error message from API error response
 * @param {Error} error - Error object from API call
 * @param {string} defaultMessage - Default message if no error found
 * @returns {string} Extracted error message
 */
export function extractErrorMessage(error, defaultMessage = 'Error inesperado') {
  if (!error) {
    return defaultMessage
  }

  // Try different error response formats
  if (error.response?.data?.detail) {
    return error.response.data.detail
  }

  if (error.response?.data?.error) {
    return error.response.data.error
  }

  if (error.response?.data?.message) {
    return error.response.data.message
  }

  if (error.message) {
    return error.message
  }

  return defaultMessage
}

/**
 * Formats API response to consistent structure
 * @param {Object} response - API response data
 * @param {boolean} wrapInSuccess - Whether to wrap in success object
 * @returns {Object} Formatted response
 */
export function formatApiResponse(response, wrapInSuccess = false) {
  if (wrapInSuccess) {
    return {
      success: true,
      data: response
    }
  }
  return response
}

/**
 * Handles API error with context
 * @param {Error} error - Error object from API call
 * @param {string} context - Context description for logging
 * @param {string} defaultMessage - Default error message
 * @returns {Object} Error object with consistent structure
 */
export function handleApiError(error, context = '', defaultMessage = 'Error inesperado') {
  const errorMessage = extractErrorMessage(error, defaultMessage)
  
  if (context) {
    console.error(`[${context}]`, errorMessage, error)
  } else {
    console.error('❌ API Error:', errorMessage, error)
  }

  return {
    success: false,
    error: errorMessage,
    status: error.response?.status,
    statusText: error.response?.statusText,
    originalError: error
  }
}

/**
 * Creates standardized error response
 * @param {string} message - Error message
 * @param {number} status - HTTP status code
 * @param {Error} originalError - Original error object
 * @returns {Object} Standardized error response
 */
export function createErrorResponse(message, status = null, originalError = null) {
  return {
    success: false,
    error: message,
    status,
    originalError
  }
}
