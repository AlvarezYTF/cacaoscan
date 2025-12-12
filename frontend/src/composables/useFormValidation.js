/**
 * Composable para validación de formularios reutilizable
 * 
 * SECURITY NOTE: This file contains password validation logic only.
 * No hardcoded passwords or credentials are present in this file.
 * All password values are validated dynamically from user input.
 * 
 * SonarQube S2068: This is a false positive. The word "password" appears
 * only in validation functions and error messages, not as hardcoded credentials.
 */
import { reactive, ref } from 'vue'

/**
 * Validation error messages constants
 * These are error messages only, not hardcoded credentials
 * SonarQube S2068: These are error message strings, not actual passwords
 */
// NOSONAR - S2068: These are validation error messages, not hardcoded passwords
const ERROR_MESSAGES = {
  PASSWORD_REQUIRED: 'La contraseña es requerida', // NOSONAR
  PASSWORD_WEAK: 'La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número', // NOSONAR
  PASSWORD_CONFIRMATION_REQUIRED: 'La confirmación de contraseña es requerida', // NOSONAR
  PASSWORDS_MISMATCH: 'Las contraseñas no coinciden' // NOSONAR
}

export function useFormValidation() {
  const errors = reactive({})
  const validatingFields = ref(new Set())
  const formState = reactive({
    dirty: false,
    touched: {},
    valid: true
  })

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
    if (!password) {
      return {
        length: false,
        uppercase: false,
        lowercase: false,
        number: false,
        isValid: false
      }
    }
    return {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /\d/.test(password),
      isValid: password.length >= 8 && /[A-Z]/.test(password) && 
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
        const successResult = onSuccess(result)
        return successResult === undefined ? result : successResult
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
    if (!value?.trim()) {
      let fieldLabel = 'campo'
      if (fieldName === 'firstName') {
        fieldLabel = 'nombre'
      } else if (fieldName === 'lastName') {
        fieldLabel = 'apellido'
      }
      return `El ${fieldLabel} es requerido`
    }
    if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/.test(value)) {
      let fieldLabel = 'campo'
      if (fieldName === 'firstName') {
        fieldLabel = 'nombre'
      } else if (fieldName === 'lastName') {
        fieldLabel = 'apellido'
      }
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
    if (!value?.trim()) {
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
    if (!value?.trim()) {
      return 'El número de documento es requerido'
    }
    if (!isValidDocument(value)) {
      return 'El documento debe tener entre 6 y 11 dígitos'
    }
    return null
  }

  /**
   * Validates password fields (password and confirm password)
   * @param {string} password - Password value from user input (not hardcoded)
   * @param {string} confirmPassword - Confirm password value from user input (not hardcoded)
   * @returns {Object} Object with password and confirmPassword error messages
   * 
   * SonarQube S2068: This function validates user-provided passwords dynamically.
   * No hardcoded passwords are present in this function.
   * NOSONAR - False positive: This is password validation logic, not hardcoded credentials
   */
  // eslint-disable-next-line sonarjs/no-hardcoded-password
  const validatePasswordFields = (password, confirmPassword) => {
    const result = {
      password: null,
      confirmPassword: null
    }

    if (!password) {
      // NOSONAR - S2068: Error message constant, not a hardcoded password
      result.password = ERROR_MESSAGES.PASSWORD_REQUIRED // NOSONAR
      return result
    }

    const passwordChecks = validatePassword(password)
    if (!passwordChecks.isValid) {
      // NOSONAR - S2068: Error message constant, not a hardcoded password
      result.password = ERROR_MESSAGES.PASSWORD_WEAK // NOSONAR
      return result
    }

    if (!confirmPassword) {
      // NOSONAR - S2068: Error message constant, not a hardcoded password
      result.confirmPassword = ERROR_MESSAGES.PASSWORD_CONFIRMATION_REQUIRED // NOSONAR
      return result
    }

    if (password !== confirmPassword) {
      // NOSONAR - S2068: Error message constant, not a hardcoded password
      result.confirmPassword = ERROR_MESSAGES.PASSWORDS_MISMATCH // NOSONAR
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

  /**
   * Validation rule presets
   */
  const validationPresets = {
    email: {
      required: true,
      validator: (value) => {
        if (!value?.trim()) {
          return 'El email es requerido'
        }
        if (!isValidEmail(value)) {
          return 'Ingresa un email válido'
        }
        return null
      }
    },
    // NOSONAR - S2068: This is a validation preset name, not a hardcoded password
    password: {
      required: true,
      validator: (value) => {
        // SonarQube S2068: This validates user-provided password, not a hardcoded one
        if (!value) {
          // NOSONAR - S2068: Error message constant, not a hardcoded password
          return ERROR_MESSAGES.PASSWORD_REQUIRED // NOSONAR
        }
        const checks = validatePassword(value)
        if (!checks.isValid) {
          // NOSONAR - S2068: Error message constant, not a hardcoded password
          return ERROR_MESSAGES.PASSWORD_WEAK // NOSONAR
        }
        return null
      }
    },
    phone: {
      required: false,
      validator: (value) => {
        if (value && !isValidPhone(value)) {
          return 'El teléfono debe tener entre 7 y 15 dígitos'
        }
        return null
      }
    },
    document: {
      required: true,
      validator: (value) => {
        if (!value?.trim()) {
          return 'El número de documento es requerido'
        }
        if (!isValidDocument(value)) {
          return 'El documento debe tener entre 6 y 11 dígitos'
        }
        return null
      }
    },
    name: {
      required: true,
      validator: (value, fieldName = 'nombre') => {
        return validateNameField(value, fieldName)
      }
    },
    birthdate: {
      required: false,
      validator: (value) => {
        return validateBirthdateField(value)
      }
    }
  }

  /**
   * Validates a field using a preset
   * @param {string} fieldName - Field name
   * @param {*} value - Field value
   * @param {string} preset - Preset name
   * @returns {string|null} Error message or null
   */
  const validateWithPreset = (fieldName, value, preset) => {
    const presetRule = validationPresets[preset]
    if (!presetRule) {
      throw new Error(`Preset "${preset}" not found`)
    }

    if (presetRule.required && (!value || (typeof value === 'string' && !value.trim()))) {
      return `${fieldName} es requerido`
    }

    if (presetRule.validator) {
      return presetRule.validator(value, fieldName)
    }

    return null
  }

  /**
   * Async validation support
   * @param {string} fieldName - Field name
   * @param {Function} validatorFn - Async validator function
   * @returns {Promise<void>}
   */
  const validateFieldAsync = async (fieldName, validatorFn) => {
    validatingFields.value.add(fieldName)
    removeError(fieldName)

    try {
      const errorMessage = await validatorFn()
      if (errorMessage) {
        setError(fieldName, errorMessage)
      }
    } catch (error) {
      setError(fieldName, error.message || 'Error de validación')
    } finally {
      validatingFields.value.delete(fieldName)
    }
  }

  /**
   * Checks if a field is currently being validated
   * @param {string} fieldName - Field name
   * @returns {boolean} True if field is validating
   */
  const isFieldValidating = (fieldName) => {
    return validatingFields.value.has(fieldName)
  }

  /**
   * Cross-field validation
   * @param {Object} fields - Object with field names as keys and values
   * @param {Function} validatorFn - Validator function that receives all fields
   * @returns {Object} Object with field names as keys and error messages as values
   */
  const validateCrossFields = (fields, validatorFn) => {
    const crossFieldErrors = validatorFn(fields)
    
    if (crossFieldErrors && typeof crossFieldErrors === 'object') {
      for (const [fieldName, errorMessage] of Object.entries(crossFieldErrors)) {
        if (errorMessage) {
          setError(fieldName, errorMessage)
        } else {
          removeError(fieldName)
        }
      }
    }

    return crossFieldErrors || {}
  }

  /**
   * Marks a field as touched
   * @param {string} fieldName - Field name
   * @returns {void}
   */
  const markFieldTouched = (fieldName) => {
    formState.touched[fieldName] = true
    formState.dirty = true
  }

  /**
   * Checks if a field has been touched
   * @param {string} fieldName - Field name
   * @returns {boolean} True if field has been touched
   */
  const isFieldTouched = (fieldName) => {
    return !!formState.touched[fieldName]
  }

  /**
   * Marks form as dirty
   * @returns {void}
   */
  const markFormDirty = () => {
    formState.dirty = true
  }

  /**
   * Checks if form is dirty
   * @returns {boolean} True if form is dirty
   */
  const isFormDirty = () => {
    return formState.dirty
  }

  /**
   * Validates entire form
   * @param {Object} formData - Form data object
   * @param {Object} rules - Validation rules object
   * @returns {boolean} True if form is valid
   */
  const validateForm = (formData, rules) => {
    clearErrors()
    let isValid = true

    for (const [fieldName, value] of Object.entries(formData)) {
      const rule = rules[fieldName]
      if (!rule) continue

      let error = null

      if (rule.preset) {
        error = validateWithPreset(fieldName, value, rule.preset)
      } else if (rule.validator) {
        error = rule.validator(value, formData)
      } else if (rule.required && (!value || (typeof value === 'string' && !value.trim()))) {
        error = `${fieldName} es requerido`
      }

      if (error) {
        setError(fieldName, error)
        isValid = false
      }
    }

    // Cross-field validation
    if (rules._crossField) {
      const crossFieldErrors = validateCrossFields(formData, rules._crossField)
      if (Object.keys(crossFieldErrors).length > 0) {
        isValid = false
      }
    }

    formState.valid = isValid
    return isValid
  }

  /**
   * Resets form state
   * @returns {void}
   */
  const resetFormState = () => {
    clearErrors()
    formState.dirty = false
    formState.touched = {}
    formState.valid = true
    validatingFields.value.clear()
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
    hasFieldError,
    // New features
    validationPresets,
    validateWithPreset,
    validateFieldAsync,
    isFieldValidating,
    validateCrossFields,
    markFieldTouched,
    isFieldTouched,
    markFormDirty,
    isFormDirty,
    validateForm,
    resetFormState,
    // Form state
    formState,
    validatingFields
  }
}


