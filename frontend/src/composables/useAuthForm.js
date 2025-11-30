/**
 * Composable for authentication forms
 * Extends useForm with authentication-specific validations and helpers
 */
import { ref } from 'vue'
import { useForm } from './useForm'

/**
 * Maximum input length to prevent ReDoS attacks
 */
const MAX_EMAIL_LENGTH = 254 // RFC 5321 limit
const MAX_USERNAME_LENGTH = 30

/**
 * Character code validation helpers
 */
const isAlphaNumericCode = (code) => {
  return (code >= 48 && code <= 57) || // 0-9
    (code >= 65 && code <= 90) || // A-Z
    (code >= 97 && code <= 122) // a-z
}

const isValidLocalPartChar = (char) => {
  const code = char.codePointAt(0)
  if (code === undefined) {
    return false
  }
  return code >= 33 && code <= 126 && char !== ' ' && char !== '@'
}

const isValidUsernameChar = (char) => {
  const code = char.codePointAt(0)
  if (code === undefined) {
    return false
  }
  return isAlphaNumericCode(code) || char === '_' || char === '-'
}

const hasValidEmailLength = (emailValue) => {
  return typeof emailValue === 'string' &&
    emailValue.length >= 3 &&
    emailValue.length <= MAX_EMAIL_LENGTH
}

/**
 * Split email into local and domain parts
 * @param {string} email
 * @returns {{ localPart: string, domain: string } | null}
 */
const splitEmailParts = (email) => {
  const atIndex = email.indexOf('@')
  if (atIndex <= 0 || atIndex === email.length - 1) {
    return null
  }

  return {
    localPart: email.slice(0, atIndex),
    domain: email.slice(atIndex + 1)
  }
}

const isValidLocalPartSection = (localPart) => {
  if (localPart.length === 0 || localPart.length > 64) {
    return false
  }

  for (const char of localPart) {
    if (!isValidLocalPartChar(char)) {
      return false
    }
  }

  return true
}

const isValidDomainSection = (domain) => {
  if (domain.length === 0 || domain.length > 253) {
    return false
  }

  const domainParts = domain.split('.')
  if (domainParts.length < 2) {
    return false
  }

  for (let idx = 0; idx < domainParts.length; idx += 1) {
    const part = domainParts[idx]
    if (!isValidDomainPart(part, idx === domainParts.length - 1)) {
      return false
    }
  }

  return true
}

const hasValidDomainPartLength = (length, isTLD) => {
  if (length === 0) {
    return false
  }

  if (isTLD) {
    return length >= 2
  }

  return true
}

const isValidTLDPart = (part) => {
  for (const char of part) {
    const code = char.codePointAt(0)
    if (code === undefined || !isAlphaNumericCode(code)) {
      return false
    }
  }

  return true
}

const isValidSubdomainPart = (part) => {
  const lastIndex = part.length - 1

  for (let idx = 0; idx < part.length; idx += 1) {
    const char = part[idx]
    const code = char.codePointAt(0)
    if (code === undefined) {
      return false
    }

    if (!isAlphaNumericCode(code) && char !== '-') {
      return false
    }

    if (char === '-' && (idx === 0 || idx === lastIndex)) {
      return false
    }
  }

  return true
}

const isValidDomainPart = (part, isTLD) => {
  if (!hasValidDomainPartLength(part.length, isTLD)) {
    return false
  }

  if (isTLD) {
    return isValidTLDPart(part)
  }

  return isValidSubdomainPart(part)
}

/**
 * Validate email using character code validation (ReDoS safe)
 * @param {string} email - Email to validate
 * @returns {boolean}
 */
const isValidEmail = (email) => {
  if (!hasValidEmailLength(email)) {
    return false
  }

  const emailParts = splitEmailParts(email)
  if (!emailParts) {
    return false
  }

  if (!isValidLocalPartSection(emailParts.localPart)) {
    return false
  }

  return isValidDomainSection(emailParts.domain)
}

/**
 * Validate username
 * @param {string} username - Username to validate
 * @returns {boolean}
 */
const isValidUsername = (username) => {
  if (typeof username !== 'string') {
    return false
  }

  if (username.length < 3 || username.length > MAX_USERNAME_LENGTH) {
    return false
  }

  return Array.from(username).every((char) => {
    return isValidUsernameChar(char)
  })
}

/**
 * Create authentication form composable
 * @param {Object} options - Form options
 * @param {Object} options.initialValues - Initial form values
 * @param {Function} options.onSubmit - Submit handler function
 * @param {Object} options.fieldMapping - Mapping from server field names to form field names
 * @returns {Object} Form state and methods
 */
export function useAuthForm(options = {}) {
  const {
    initialValues = {},
    onSubmit = null,
    fieldMapping = {}
  } = options

  // Use base form composable
  const baseForm = useForm({
    initialValues,
    onSubmit,
    fieldMapping,
    autoLoadCatalogos: false // Auth forms don't need catalogos
  })

  // Get validation helpers (isValidEmail is used directly, not through destructuring)

  // Status message state
  const statusMessage = ref('')
  const statusMessageClass = ref('')

  /**
   * Set status message
   * @param {string} message - Message to display
   * @param {string} type - Message type ('success' | 'error' | 'info')
   */
  const setStatusMessage = (message, type = 'info') => {
    statusMessage.value = message
    let statusClass = 'bg-blue-100 border border-blue-400 text-blue-700'
    if (type === 'success') {
      statusClass = 'bg-green-100 border border-green-400 text-green-700'
    } else if (type === 'error') {
      statusClass = 'bg-red-100 border border-red-400 text-red-700'
    }
    statusMessageClass.value = statusClass

    // Clear message after 5 seconds
    setTimeout(() => {
      statusMessage.value = ''
    }, 5000)
  }

  /**
   * Validate email or username field
   * @param {string} value - Value to validate
   * @returns {string | null} Error message or null if valid
   */
  const validateEmailOrUsername = (value) => {
    if (!value?.trim()) {
      return 'El email o usuario es requerido'
    }

    const trimmedValue = value.trim()
    const isEmail = isValidEmail(trimmedValue)
    const isUser = isValidUsername(trimmedValue)

    if (!isEmail && !isUser) {
      return 'Ingresa un email válido o nombre de usuario'
    }

    return null
  }

  /**
   * Validate password field
   * @param {string} password - Password to validate
   * @param {number} minLength - Minimum length (default: 6)
   * @returns {string | null} Error message or null if valid
   */
  const validatePassword = (password, minLength = 6) => {
    if (!password) {
      return 'La contraseña es requerida'
    }

    if (password.length < minLength) {
      return `La contraseña debe tener al menos ${minLength} caracteres`
    }

    return null
  }

  /**
   * Validate authentication form
   * @returns {boolean} True if valid
   */
  const validateAuthForm = () => {
    baseForm.clearErrors()

    let isValid = true

    // Validate email/username
    if (baseForm.form.email !== undefined) {
      const emailError = validateEmailOrUsername(baseForm.form.email)
      if (emailError) {
        baseForm.setError('email', emailError)
        isValid = false
      }
    }

    // Validate password
    if (baseForm.form.password !== undefined) {
      const passwordError = validatePassword(baseForm.form.password)
      if (passwordError) {
        baseForm.setError('password', passwordError)
        isValid = false
      }
    }

    return isValid
  }

  /**
   * Handle form submission with auth-specific validation
   * @param {Event} event - Form submit event
   * @returns {Promise<boolean>}
   */
  const handleAuthSubmit = async (event = null) => {
    if (event) {
      event.preventDefault()
    }

    if (!validateAuthForm()) {
      baseForm.scrollToFirstError()
      return false
    }

    if (!onSubmit || typeof onSubmit !== 'function') {
      return true
    }

    try {
      const result = await baseForm.handleSubmit(event)
      return result
    } catch (error) {
      console.error('Error in auth form submission:', error)
      setStatusMessage(error.message || 'Error al procesar la solicitud', 'error')
      throw error
    }
  }

  return {
    // Re-export base form properties
    ...baseForm,

    // Auth-specific state
    statusMessage,
    statusMessageClass,

    // Auth-specific methods
    setStatusMessage,
    validateEmailOrUsername,
    validatePassword,
    validateAuthForm,
    handleAuthSubmit,

    // Validation helpers
    isValidEmail,
    isValidUsername
  }
}

