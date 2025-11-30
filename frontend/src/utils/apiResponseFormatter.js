/**
 * Utility functions for standardizing API service responses
 * Provides consistent response formatting across all services
 */

/**
 * Formats successful API response
 * @param {Object} data - Response data
 * @param {string} message - Optional success message
 * @returns {Object} Formatted success response
 */
export function formatSuccessResponse(data, message = null) {
  const response = {
    success: true,
    data
  }

  if (message) {
    response.message = message
  }

  return response
}

/**
 * Formats error API response
 * @param {string} error - Error message
 * @param {Object} details - Optional error details
 * @returns {Object} Formatted error response
 */
export function formatErrorResponse(error, details = null) {
  const response = {
    success: false,
    error
  }

  if (details) {
    response.details = details
  }

  return response
}

/**
 * Normalizes API response to consistent format
 * @param {Object} responseData - Raw API response
 * @param {boolean} alwaysWrap - Whether to always wrap in success/error structure
 * @returns {Object} Normalized response
 */
export function normalizeApiResponse(responseData, alwaysWrap = false) {
  // If already in standard format, return as is
  if (responseData && typeof responseData === 'object' && 'success' in responseData) {
    return responseData
  }

  // If alwaysWrap is true, wrap in success structure
  if (alwaysWrap) {
    return formatSuccessResponse(responseData)
  }

  // Otherwise return as is (for backward compatibility)
  return responseData
}

