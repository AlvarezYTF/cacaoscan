/**
 * Composable para validación de formularios reutilizable
 */
import { reactive } from 'vue'

export function useFormValidation() {
  const errors = reactive({})

  /**
   * Valida las etiquetas del dominio
   * @param {string[]} labels - Etiquetas del dominio
   * @returns {boolean}
   */
  const isValidDomainLabels = (labels) => {
    for (const label of labels) {
      if (label.length === 0 || label.length > 63) return false
      // Allow only letters, digits and hyphen in each label; no leading/trailing hyphen
      if (!/^[A-Za-z0-9-]+$/.test(label)) return false
      if (label.startsWith('-') || label.endsWith('-')) return false
    }
    return true
  }

  /**
   * Valida un email
   * @param {string} email - Email a validar
   * @returns {boolean}
   */
  const isValidEmail = (email) => {
    // Avoid complex/ambiguous regexes that can exhibit catastrophic
    // backtracking. Implement simple, bounded checks instead.
    if (!email) return false
    // Overall length limits per RFC-like guidance
    if (email.length > 320) return false

    const parts = email.split('@')
    if (parts.length !== 2) return false

    const [local, domain] = parts

    // Length checks for local and domain parts
    if (local.length === 0 || local.length > 64) return false
    if (domain.length === 0 || domain.length > 255) return false

    // No whitespace allowed
    if (/\s/.test(local) || /\s/.test(domain)) return false

    // Domain must contain at least one dot and consist of valid labels
    if (!domain.includes('.')) return false
    const labels = domain.split('.')
    if (!isValidDomainLabels(labels)) return false

    // Local part: allow common unquoted atoms (letters, digits and a small set of symbols)
    // Keep regex simple (no nested quantifiers) and bounded by local length check above.
    if (!/^[A-Za-z0-9!#$%&'*+\-/=?^_`{|}~.]+$/.test(local)) return false

    // Reject consecutive dots in local or domain
    if (local.includes('..') || domain.includes('..')) return false

    return true
  }

  /**
   * Valida un teléfono
   * @param {string} phone - Teléfono a validar
   * @returns {boolean}
   */
  const isValidPhone = (phone) => {
    if (!phone) return true // Opcional
    const cleanPhone = phone.replaceAll(/[\s\-()]/g, '')
    return /^\+?\d{7,15}$/.test(cleanPhone)
  }

  /**
   * Valida un número de documento
   * @param {string} documento - Documento a validar
   * @returns {boolean}
   */
  const isValidDocument = (documento) => {
    if (!documento) return false
    const cleanDoc = documento.trim()
    return /^\d+$/.test(cleanDoc) && cleanDoc.length >= 6 && cleanDoc.length <= 11
  }

  /**
   * Valida una fecha de nacimiento (mínimo 14 años)
   * @param {string} fechaNacimiento - Fecha en formato YYYY-MM-DD
   * @returns {boolean}
   */
  const isValidBirthdate = (fechaNacimiento) => {
    if (!fechaNacimiento) return true // Opcional
    const birthDate = new Date(fechaNacimiento)
    const today = new Date()
    const age = today.getFullYear() - birthDate.getFullYear() - 
                ((today.getMonth() < birthDate.getMonth()) || 
                 (today.getMonth() === birthDate.getMonth() && today.getDate() < birthDate.getDate()) ? 1 : 0)
    return age >= 14 && birthDate <= today
  }

  /**
   * Valida una contraseña
   * @param {string} password - Contraseña a validar
   * @returns {object} - Objeto con checks de validación
   */
  const validatePassword = (password) => {
    return {
      length: password && password.length >= 8,
      uppercase: password && /[A-Z]/.test(password),
      lowercase: password && /[a-z]/.test(password),
      number: password && /\d/.test(password),
      isValid: password && password.length >= 8 && /[A-Z]/.test(password) && 
               /[a-z]/.test(password) && /\d/.test(password)
    }
  }

  /**
   * Limpia todos los errores
   */
  const clearErrors = () => {
    for (const key of Object.keys(errors)) {
      delete errors[key]
    }
  }

  /**
   * Establece un error
   * @param {string} field - Campo
   * @param {string} message - Mensaje de error
   */
  const setError = (field, message) => {
    errors[field] = message
  }

  /**
   * Remueve un error específico
   * @param {string} field - Campo
   */
  const removeError = (field) => {
    delete errors[field]
  }

  /**
   * Verifica si hay errores
   * @returns {boolean}
   */
  const hasErrors = () => {
    return Object.keys(errors).length > 0
  }

  /**
   * Checks if a field name should be skipped (non-field errors)
   * @param {string} fieldName - Field name to check
   * @returns {boolean}
   */
  const shouldSkipField = (fieldName) => {
    const nonFieldKeys = new Set(['error', 'status', 'error_detail'])
    return nonFieldKeys.has(fieldName)
  }

  /**
   * Extracts error message from different error value formats
   * @param {*} errorValue - Error value (can be array, string, or object)
   * @returns {string|null} - Extracted error message or null
   */
  const extractErrorMessage = (errorValue) => {
    if (Array.isArray(errorValue) && errorValue.length > 0) {
      return errorValue[0]
    }
    
    if (typeof errorValue === 'string') {
      return errorValue
    }
    
    if (errorValue && typeof errorValue === 'object') {
      const firstKey = Object.keys(errorValue)[0]
      if (firstKey && errorValue[firstKey]) {
        return Array.isArray(errorValue[firstKey]) 
          ? errorValue[firstKey][0] 
          : errorValue[firstKey]
      }
    }
    
    return null
  }

  /**
   * Maps server validation errors to form fields
   * @param {Object} serverErrors - Server error response
   * @param {Object} fieldMapping - Optional mapping from server field names to form field names
   * @returns {void}
   */
  const mapServerErrors = (serverErrors, fieldMapping = {}) => {
    clearErrors()
    
    if (!serverErrors || typeof serverErrors !== 'object') {
      return
    }

    for (const [serverField, errorValue] of Object.entries(serverErrors)) {
      if (shouldSkipField(serverField)) {
        continue
      }

      const formField = fieldMapping[serverField] || serverField
      const errorMessage = extractErrorMessage(errorValue)
      
      if (errorMessage) {
        errors[formField] = errorMessage
      }
    }
  }

  /**
   * Resets form errors (alias for clearErrors for consistency)
   * @returns {void}
   */
  const resetFormErrors = () => {
    clearErrors()
  }

  /**
   * Handles form submission with validation and error mapping
   * @param {Function} submitFn - Async function to execute on submit
   * @param {Function} validateFn - Optional validation function
   * @param {Function} onSuccess - Optional success callback
   * @param {Function} onError - Optional error callback
   * @returns {Promise<void>}
   */
  const handleFormSubmit = async (submitFn, validateFn = null, onSuccess = null, onError = null) => {
    // Clear previous errors
    clearErrors()

    // Run validation if provided
    if (validateFn) {
      const isValid = validateFn()
      if (!isValid) {
        return
      }
    }

    try {
      const result = await submitFn()
      
      if (onSuccess) {
        onSuccess(result)
      }
      
      return result
    } catch (error) {
      // Map server errors if available
      if (error.response?.data) {
        const serverErrors = error.response.data.details || error.response.data
        mapServerErrors(serverErrors)
      }

      if (onError) {
        onError(error)
      } else {
        throw error
      }
    }
  }

  /**
   * Scrolls to first error field
   * @param {string} prefix - Optional prefix for field name selector
   * @returns {void}
   */
  const scrollToFirstError = (prefix = '') => {
    const firstErrorField = Object.keys(errors)[0]
    if (firstErrorField) {
      setTimeout(() => {
        const fieldName = prefix ? `${prefix}-${firstErrorField}` : firstErrorField
        const errorElement = document.querySelector(`[name="${firstErrorField}"]`) || 
                            document.querySelector(`#${fieldName}`) ||
                            document.querySelector(`[id*="${firstErrorField}"]`)
        
        if (errorElement) {
          errorElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
          errorElement.focus()
        }
      }, 300)
    }
  }

  /**
   * Validates a name field (first name, last name, etc.)
   * @param {string} value - Name value to validate
   * @param {string} fieldName - Field name for error message
   * @returns {string|null} Error message or null if valid
   */
  const validateNameField = (value, fieldName) => {
    if (!value || !value.trim()) {
      const fieldLabel = fieldName === 'firstName' ? 'nombre' : 
                        fieldName === 'lastName' ? 'apellido' : 'campo'
      return `El ${fieldLabel} es requerido`
    }
    if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/.test(value)) {
      const fieldLabel = fieldName === 'firstName' ? 'nombre' : 
                        fieldName === 'lastName' ? 'apellido' : 'campo'
      return `El ${fieldLabel} solo puede contener letras`
    }
    return null
  }

  /**
   * Validates email field with error message
   * @param {string} value - Email value to validate
   * @returns {string|null} Error message or null if valid
   */
  const validateEmailField = (value) => {
    if (!value || !value.trim()) {
      return 'El email es requerido'
    }
    if (!isValidEmail(value)) {
      return 'Ingresa un email válido'
    }
    return null
  }

  /**
   * Validates phone field with error message
   * @param {string} value - Phone value to validate
   * @returns {string|null} Error message or null if valid
   */
  const validatePhoneField = (value) => {
    if (value && !isValidPhone(value)) {
      return 'El teléfono debe tener entre 7 y 15 dígitos'
    }
    return null
  }

  /**
   * Validates document field with error message
   * @param {string} value - Document value to validate
   * @returns {string|null} Error message or null if valid
   */
  const validateDocumentField = (value) => {
    if (!value || !value.trim()) {
      return 'El número de documento es requerido'
    }
    if (!isValidDocument(value)) {
      return 'El documento debe tener entre 6 y 11 dígitos'
    }
    return null
  }

  /**
   * Validates password fields (password and confirm password)
   * @param {string} password - Password value
   * @param {string} confirmPassword - Confirm password value
   * @returns {Object} Object with password and confirmPassword error messages
   */
  const validatePasswordFields = (password, confirmPassword) => {
    const result = {
      password: null,
      confirmPassword: null
    }

    if (!password) {
      result.password = 'La contraseña es requerida'
      return result
    }

    const passwordChecks = validatePassword(password)
    if (!passwordChecks.isValid) {
      result.password = 'La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número'
      return result
    }

    if (!confirmPassword) {
      result.confirmPassword = 'La confirmación de contraseña es requerida'
      return result
    }

    if (password !== confirmPassword) {
      result.confirmPassword = 'Las contraseñas no coinciden'
      return result
    }

    return result
  }

  /**
   * Validates birthdate field with error message
   * @param {string} value - Birthdate value to validate
   * @returns {string|null} Error message or null if valid
   */
  const validateBirthdateField = (value) => {
    if (value && !isValidBirthdate(value)) {
      return 'Debes tener al menos 14 años'
    }
    return null
  }

  /**
   * Gets error message for a specific field
   * @param {string} fieldName - Field name
   * @returns {string|null} Error message or null
   */
  const getFieldError = (fieldName) => {
    return errors[fieldName] || null
  }

  /**
   * Checks if a specific field has an error
   * @param {string} fieldName - Field name
   * @returns {boolean} True if field has error
   */
  const hasFieldError = (fieldName) => {
    return !!errors[fieldName]
  }

  return {
    errors,
    isValidEmail,
    isValidPhone,
    isValidDocument,
    isValidBirthdate,
    validatePassword,
    clearErrors,
    setError,
    removeError,
    hasErrors,
    mapServerErrors,
    resetFormErrors,
    handleFormSubmit,
    scrollToFirstError,
    // New helper methods
    validateNameField,
    validateEmailField,
    validatePhoneField,
    validateDocumentField,
    validatePasswordFields,
    validateBirthdateField,
    getFieldError,
    hasFieldError
  }
}

