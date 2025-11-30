/**
 * Data Transfer Objects for authentication responses
 * Normalizes auth data structures for consistent frontend consumption
 */

/**
 * @typedef {Object} LoginResponseDTO
 * @property {string} token - Access token
 * @property {string} refresh - Refresh token
 * @property {Object} user - User object
 * @property {number|null} access_expires_at - Access token expiration timestamp
 * @property {number|null} refresh_expires_at - Refresh token expiration timestamp
 * @property {string|null} message - Response message
 */

/**
 * Normalizes login response from backend
 * @param {Object} rawResponse - Raw response from backend
 * @returns {LoginResponseDTO} Normalized login response
 */
export function normalizeLoginResponse(rawResponse) {
  const data = rawResponse.data || rawResponse
  
  return {
    token: data.access || data.token,
    refresh: data.refresh,
    user: data.user || data.user_data,
    access_expires_at: data.access_expires_at || null,
    refresh_expires_at: data.refresh_expires_at || null,
    message: data.message || 'Login exitoso'
  }
}

/**
 * @typedef {Object} RegisterResponseDTO
 * @property {boolean} success - Registration success
 * @property {boolean} verification_required - Whether email verification is required
 * @property {string} email - User email
 * @property {string} message - Response message
 */

/**
 * Normalizes registration response from backend
 * @param {Object} rawResponse - Raw response from backend
 * @param {Object} userData - Original user data
 * @returns {RegisterResponseDTO} Normalized registration response
 */
export function normalizeRegisterResponse(rawResponse, userData = {}) {
  const data = rawResponse.data || rawResponse
  
  return {
    success: true,
    verification_required: data.verification_required !== false,
    email: data.email || userData.email,
    message: data.message || 'Registro exitoso. Por favor verifica tu correo electrónico.'
  }
}

/**
 * @typedef {Object} UserDTO
 * @property {number} id - User ID
 * @property {string} email - User email
 * @property {string} username - Username
 * @property {string} first_name - First name
 * @property {string} last_name - Last name
 * @property {string} role - User role
 * @property {boolean} is_active - Is user active
 * @property {boolean} is_verified - Is email verified
 * @property {string|null} date_joined - Registration date
 */

/**
 * Normalizes user object from backend
 * @param {Object} rawUser - Raw user object
 * @returns {UserDTO} Normalized user object
 */
export function normalizeUser(rawUser) {
  if (!rawUser) return null
  
  return {
    id: rawUser.id,
    email: rawUser.email,
    username: rawUser.username || rawUser.email?.split('@')[0] || '',
    first_name: rawUser.first_name || rawUser.primer_nombre || '',
    last_name: rawUser.last_name || rawUser.primer_apellido || '',
    role: rawUser.role || rawUser.user_role || 'farmer',
    is_active: rawUser.is_active !== false,
    is_verified: rawUser.is_verified || rawUser.is_email_verified || false,
    date_joined: rawUser.date_joined || rawUser.created_at || null
  }
}

/**
 * Extracts error message from error data
 * @param {Object|string} errorData - Error data object
 * @returns {string|null} Error message
 */
function extractNonFieldErrors(nonFieldErrors) {
  return Array.isArray(nonFieldErrors)
    ? nonFieldErrors[0]
    : nonFieldErrors
}

function extractErrorMessage(errorData) {
  if (typeof errorData === 'string') {
    return errorData
  }
  
  // Check error fields in priority order
  const errorFields = ['detail', 'error', 'non_field_errors']
  for (const field of errorFields) {
    if (errorData[field]) {
      return field === 'non_field_errors' 
        ? extractNonFieldErrors(errorData[field])
        : errorData[field]
    }
  }
  
  return null
}

/**
 * Gets error message from HTTP status code
 * @param {number} status - HTTP status code
 * @returns {string} Error message
 */
function getStatusMessage(status) {
  const statusMessages = {
    400: 'Datos inválidos',
    401: 'Credenciales inválidas',
    403: 'No tienes permisos',
    404: 'Recurso no encontrado',
    422: 'Error de validación',
    500: 'Error del servidor'
  }
  return statusMessages[status] || 'Error de autenticación'
}

/**
 * Extracts field errors from error data
 * @param {Object} errorData - Error data object
 * @returns {Object|null} Field errors object
 */
function extractFieldErrors(errorData) {
  const fieldErrors = {}
  const excludedFields = new Set(['detail', 'error', 'non_field_errors'])
  
  for (const [field, errors] of Object.entries(errorData)) {
    if (excludedFields.has(field)) {
      continue
    }
    
    if (Array.isArray(errors)) {
      fieldErrors[field] = errors[0]
    } else if (typeof errors === 'string') {
      fieldErrors[field] = errors
    }
  }
  
  return Object.keys(fieldErrors).length > 0 ? fieldErrors : null
}

/**
 * Normalizes error response from auth API
 * @param {Error} error - Error object
 * @returns {Object} Normalized error object
 */
export function normalizeAuthError(error) {
  if (!error.response?.data) {
    return {
      message: error.message || 'Error de autenticación',
      type: 'unknown'
    }
  }
  
  const errorData = error.response.data
  const status = error.response.status
  
  const message = extractErrorMessage(errorData) || 
                  (status ? getStatusMessage(status) : 'Error de autenticación')
  const fieldErrors = extractFieldErrors(errorData)
  
  return {
    message,
    type: status === 401 ? 'authentication' : 'validation',
    status,
    fieldErrors
  }
}

