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
 * For paginated responses, extracts and returns the results array
 * For array responses, returns the array as is
 * For custom formats like {lotes: [...], finca: {...}}, returns as is
 * @param {Object|Array} data - Response data (can be paginated object or array)
 * @returns {Array} Normalized response array
 */
export function normalizeResponse(data) {
  // If it's a simple array, return it as is (check first, before any other logic)
  if (Array.isArray(data)) {
    return data
  }
  
  // Handle null or undefined explicitly - return empty array immediately
  if (data === null || data === undefined) {
    return []
  }
  
  // If it's not an object, return empty array
  if (typeof data !== 'object') {
    return []
  }
  
  // Handle empty object explicitly - return empty array
  if (Object.keys(data).length === 0) {
    return []
  }
  
  // If it's a paginated response with results, extract the results array
  // This check must come before custom format checks to prioritize paginated responses
  if (data.results !== undefined && Array.isArray(data.results)) {
    return data.results
  }
  
  // If object has pagination properties (count, page, etc.) but no results, return empty array
  const hasPaginationProps = 'count' in data || 'page' in data || 'page_size' in data || 'total_pages' in data
  if (hasPaginationProps && data.results === undefined) {
    return []
  }
  
  // If it's a custom object format (like {lotes: [...], finca: {...}}), return as is
  // Check if it has custom keys that indicate it's not a simple paginated response
  const hasCustomFormat = 'lotes' in data || 'finca' in data || 'total' in data
  if (hasCustomFormat) {
    return data
  }
  
  // Otherwise return empty array for other object formats
  return []
}
