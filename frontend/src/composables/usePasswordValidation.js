/**
 * Composable for password validation utilities
 * Provides reusable password validation functions to eliminate code duplication
 */

/**
 * Password validation rules
 */
const PASSWORD_RULES = {
  minLength: 8,
  requireUpperCase: true,
  requireLowerCase: true,
  requireNumber: true
}

/**
 * Check password strength and return validation results
 * @param {string} password - Password to validate
 * @param {Object} options - Options for validation format
 * @returns {Object} Validation results with individual checks
 */
export function validatePasswordStrength(password, options = {}) {
  const { format = 'detailed' } = options
  
  if (!password) {
    if (format === 'simple') {
      return {
        length: false,
        uppercase: false,
        lowercase: false,
        number: false
      }
    }
    return {
      length: 0,
      hasUpperCase: false,
      hasLowerCase: false,
      hasNumber: false,
      isValid: false
    }
  }
  
  const lengthCheck = password.length >= PASSWORD_RULES.minLength
  const hasUpperCase = /[A-Z]/.test(password)
  const hasLowerCase = /[a-z]/.test(password)
  const hasNumber = /\d/.test(password)
  const isValid = lengthCheck && hasUpperCase && hasLowerCase && hasNumber
  
  if (format === 'simple') {
    return {
      length: lengthCheck,
      uppercase: hasUpperCase,
      lowercase: hasLowerCase,
      number: hasNumber
    }
  }
  
  return {
    length: password.length,
    hasUpperCase,
    hasLowerCase,
    hasNumber,
    isValid
  }
}

/**
 * Get password validation error messages
 * @param {string} password - Password to validate
 * @returns {string|null} Error message or null if valid
 */
export function getPasswordValidationError(password) {
  if (!password) {
    return 'La nueva contraseña es requerida'
  }
  
  if (password.length < PASSWORD_RULES.minLength) {
    return 'La contraseña debe tener al menos 8 caracteres'
  }
  
  if (!/[A-Z]/.test(password)) {
    return 'La contraseña debe contener al menos una letra mayúscula'
  }
  
  if (!/[a-z]/.test(password)) {
    return 'La contraseña debe contener al menos una letra minúscula'
  }
  
  if (!/\d/.test(password)) {
    return 'La contraseña debe contener al menos un número'
  }
  
  return null
}

/**
 * Validate password confirmation matches
 * @param {string} password - Original password
 * @param {string} confirmPassword - Confirmation password
 * @returns {string|null} Error message or null if valid
 */
export function validatePasswordConfirmation(password, confirmPassword) {
  if (!confirmPassword) {
    return 'La confirmación de contraseña es requerida'
  }
  
  if (password !== confirmPassword) {
    return 'Las contraseñas no coinciden'
  }
  
  return null
}

/**
 * Composable function that returns all password validation utilities
 * @returns {Object} Object with all password validation functions
 */
export function usePasswordValidation() {
  return {
    validatePasswordStrength,
    getPasswordValidationError,
    validatePasswordConfirmation,
    PASSWORD_RULES
  }
}

