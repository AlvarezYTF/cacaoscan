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
  const userData = data.user || data.user_data
  
  // Extraer login_provider y password_allowed desde data o userData
  const loginProvider = data.login_provider || userData?.login_provider || 'local'
  const passwordAllowed = data.password_allowed !== undefined 
    ? data.password_allowed 
    : (userData?.password_allowed !== undefined 
      ? userData.password_allowed 
      : loginProvider !== 'google')
  
  return {
    token: data.access || data.token,
    refresh: data.refresh,
    user: userData,
    has_password: data.has_password !== undefined ? data.has_password : (userData?.has_password ?? true),
    login_provider: loginProvider,
    password_allowed: passwordAllowed,
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
    success: data.success !== false,
    verification_required: data.verification_required !== false,
    email: data.email || userData.email,
    message: data.message || 'Registro exitoso. Por favor verifica tu correo electrónico.',
    access: data.access || null,
    refresh: data.refresh || null,
    user: data.user || null,
    token: data.access || data.token || null
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
  
  // Generate username from email only if email contains @
  const generateUsernameFromEmail = (email) => {
    if (!email?.includes('@')) {
      return ''
    }
    return email.split('@')[0]
  }
  
  // 🔥 FIX CRÍTICO: Incluir login_provider, password_allowed y has_password si vienen del backend
  // Estos campos son críticos para determinar si el usuario puede cambiar contraseña
  return {
    id: rawUser.id,
    email: rawUser.email,
    username: rawUser.username || generateUsernameFromEmail(rawUser.email) || '',
    first_name: rawUser.first_name || rawUser.primer_nombre || '',
    last_name: rawUser.last_name || rawUser.primer_apellido || '',
    role: rawUser.role || rawUser.user_role || 'farmer',
    is_active: rawUser.is_active !== false,
    is_verified: rawUser.is_verified || rawUser.is_email_verified || false,
    date_joined: rawUser.date_joined || rawUser.created_at || null,
    // 🔥 Preservar campos de autenticación si vienen del backend
    // NO establecer valores por defecto aquí - dejar que setUser() los maneje
    ...(rawUser.login_provider !== undefined && { login_provider: rawUser.login_provider }),
    ...(rawUser.password_allowed !== undefined && { password_allowed: rawUser.password_allowed }),
    ...(rawUser.has_password !== undefined && { has_password: rawUser.has_password })
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
  
  if (!errorData || typeof errorData !== 'object') {
    return null
  }
  
  // Check error fields in priority order
  // Backend uses 'error' in create_error_response, but also check other common fields
  const errorFields = ['error', 'message', 'detail', 'non_field_errors']
  for (const field of errorFields) {
    if (errorData[field]) {
      const value = errorData[field]
      if (typeof value === 'string') {
        return value
      }
      if (field === 'non_field_errors') {
        return extractNonFieldErrors(value)
      }
      // If it's an array, get first element
      if (Array.isArray(value) && value.length > 0) {
        return typeof value[0] === 'string' ? value[0] : String(value[0])
      }
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
  // If no response, return error message directly
  if (!error.response?.data) {
    return {
      message: error.message || 'Error de autenticación',
      type: 'unknown',
      status: error.response?.status || 0
    }
  }
  
  const errorData = error.response.data
  const status = error.response.status
  
  // Extract message with priority: error, message, detail, non_field_errors
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

