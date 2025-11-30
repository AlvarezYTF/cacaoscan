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
  requireNumber: true,
  requireSpecialChar: false
}

/**
 * Password validation error messages
 */
const ERROR_MESSAGES = {
  required: 'La contraseña es requerida',
  minLength: 'La contraseña debe tener al menos 8 caracteres',
  uppercase: 'La contraseña debe contener al menos una letra mayúscula',
  lowercase: 'La contraseña debe contener al menos una letra minúscula',
  number: 'La contraseña debe contener al menos un número',
  specialChar: 'La contraseña debe contener al menos un carácter especial',
  confirmRequired: 'La confirmación de contraseña es requerida',
  confirmMismatch: 'Las contraseñas no coinciden'
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
        number: false,
        specialChar: false
      }
    }
    return {
      length: 0,
      hasUpperCase: false,
      hasLowerCase: false,
      hasNumber: false,
      hasSpecialChar: false,
      isValid: false
    }
  }
  
  const lengthCheck = password.length >= PASSWORD_RULES.minLength
  const hasUpperCase = /[A-Z]/.test(password)
  const hasLowerCase = /[a-z]/.test(password)
  const hasNumber = /\d/.test(password)
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password)
  
  const isValid = lengthCheck && 
    hasUpperCase && 
    hasLowerCase && 
    hasNumber && 
    (!PASSWORD_RULES.requireSpecialChar || hasSpecialChar)
  
  if (format === 'simple') {
    return {
      length: lengthCheck,
      uppercase: hasUpperCase,
      lowercase: hasLowerCase,
      number: hasNumber,
      specialChar: hasSpecialChar
    }
  }
  
  return {
    length: password.length,
    hasUpperCase,
    hasLowerCase,
    hasNumber,
    hasSpecialChar,
    isValid
  }
}

/**
 * Get password validation error messages
 * @param {string} password - Password to validate
 * @param {Object} options - Options for error messages
 * @returns {string|null} Error message or null if valid
 */
export function getPasswordValidationError(password, options = {}) {
  const { fieldName = 'contraseña' } = options
  
  if (!password) {
    return `La ${fieldName} es requerida`
  }
  
  if (password.length < PASSWORD_RULES.minLength) {
    return ERROR_MESSAGES.minLength
  }
  
  if (PASSWORD_RULES.requireUpperCase && !/[A-Z]/.test(password)) {
    return ERROR_MESSAGES.uppercase
  }
  
  if (PASSWORD_RULES.requireLowerCase && !/[a-z]/.test(password)) {
    return ERROR_MESSAGES.lowercase
  }
  
  if (PASSWORD_RULES.requireNumber && !/\d/.test(password)) {
    return ERROR_MESSAGES.number
  }
  
  if (PASSWORD_RULES.requireSpecialChar && !/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    return ERROR_MESSAGES.specialChar
  }
  
  return null
}

/**
 * Validate password confirmation matches
 * @param {string} password - Original password
 * @param {string} confirmPassword - Confirmation password
 * @param {Object} options - Options for validation
 * @returns {string|null} Error message or null if valid
 */
export function validatePasswordConfirmation(password, confirmPassword, options = {}) {
  const { required = true, fieldName = 'confirmación de contraseña' } = options
  
  if (required && !confirmPassword) {
    return `La ${fieldName} es requerida`
  }
  
  if (password !== confirmPassword) {
    return ERROR_MESSAGES.confirmMismatch
  }
  
  return null
}

/**
 * Get password requirements checklist
 * @param {string} password - Password to check
 * @returns {Array} Array of requirement objects with status
 */
export function getPasswordRequirements(password) {
  if (!password) {
    return [
      { text: `Al menos ${PASSWORD_RULES.minLength} caracteres`, met: false },
      { text: 'Al menos una letra mayúscula', met: false },
      { text: 'Al menos una letra minúscula', met: false },
      { text: 'Al menos un número', met: false }
    ]
  }
  
  const checks = validatePasswordStrength(password, { format: 'simple' })
  
  return [
    { text: `Al menos ${PASSWORD_RULES.minLength} caracteres`, met: checks.length },
    { text: 'Al menos una letra mayúscula', met: checks.uppercase },
    { text: 'Al menos una letra minúscula', met: checks.lowercase },
    { text: 'Al menos un número', met: checks.number }
  ]
}

/**
 * Validate password with all rules
 * @param {string} password - Password to validate
 * @param {string} confirmPassword - Confirmation password (optional)
 * @param {Object} options - Validation options
 * @returns {Object} Validation result with errors object
 */
export function validatePassword(password, confirmPassword = null, options = {}) {
  const { requireConfirm = false } = options
  const errors = {}
  
  const passwordError = getPasswordValidationError(password, options)
  if (passwordError) {
    errors.password = passwordError
  }
  
  if (requireConfirm && confirmPassword !== null) {
    const confirmError = validatePasswordConfirmation(password, confirmPassword, options)
    if (confirmError) {
      errors.confirmPassword = confirmError
    }
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  }
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
    getPasswordRequirements,
    validatePassword,
    PASSWORD_RULES,
    ERROR_MESSAGES
  }
}

