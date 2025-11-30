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
      // Skip non-field errors
      if (serverField === 'error' || serverField === 'status' || serverField === 'error_detail') {
        continue
      }

      const formField = fieldMapping[serverField] || serverField
      
      // Handle different error formats
      if (Array.isArray(errorValue) && errorValue.length > 0) {
        errors[formField] = errorValue[0]
      } else if (typeof errorValue === 'string') {
        errors[formField] = errorValue
      } else if (errorValue && typeof errorValue === 'object') {
        // If nested object, extract first message
        const firstKey = Object.keys(errorValue)[0]
        if (firstKey && errorValue[firstKey]) {
          const msg = Array.isArray(errorValue[firstKey]) ? errorValue[firstKey][0] : errorValue[firstKey]
          errors[formField] = msg
        }
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
    scrollToFirstError
  }
}

