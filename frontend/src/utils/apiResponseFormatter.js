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

/**
 * Normalizes API response arrays from paginated or non-paginated endpoints
 * Handles both {results: [...]} and [...] formats
 * For paginated responses, returns the full object with results, count, etc.
 * For array responses, returns an object with results array
 * For custom formats like {lotes: [...], finca: {...}}, returns as is
 * @param {Object|Array} data - Response data (can be paginated object or array)
 * @returns {Object|Array} Normalized response (object for paginated, array for simple lists)
 */
export function normalizeResponse(data) {
  // If it's a paginated response with results, return the full object
  if (data && typeof data === 'object' && 'results' in data && Array.isArray(data.results)) {
    return data
  }
  // If it's a custom object format (like {lotes: [...], finca: {...}}), return as is
  if (data && typeof data === 'object' && !Array.isArray(data)) {
    // Check if it has custom keys that indicate it's not a simple paginated response
    const hasCustomFormat = 'lotes' in data || 'finca' in data || 'total' in data
    if (hasCustomFormat) {
      return data
    }
    // Otherwise return as is for other object formats
    return data
  }
  // If it's a simple array, wrap it in an object for consistency
  if (Array.isArray(data)) {
    return {
      results: data,
      count: data.length,
      page: 1,
      page_size: data.length,
      total_pages: 1
    }
  }
  // Fallback: return empty paginated structure
  return {
    results: [],
    count: 0,
    page: 1,
    page_size: 0,
    total_pages: 0
  }
}

