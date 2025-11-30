/**
 * Composable for email validation
 * Provides centralized email validation logic
 */

/**
 * Validates email format without using regex
 * @param {string} email - Email to validate
 * @returns {boolean} True if email is valid
 */
export function isValidEmail(email) {
  if (!email || typeof email !== 'string') {
    return false
  }

  const trimmedEmail = email.trim()
  if (trimmedEmail.length === 0 || trimmedEmail.length > 254) {
    return false
  }

  const parts = trimmedEmail.split('@')
  if (parts.length !== 2) {
    return false
  }

  const [localPart, domainPart] = parts

  // Validate local part
  if (!localPart || localPart.length === 0 || localPart.length > 64) {
    return false
  }

  if (localPart.includes('..') || localPart.startsWith('.') || localPart.endsWith('.')) {
    return false
  }

  // Validate domain part
  if (!domainPart || domainPart.length === 0 || domainPart.length > 253) {
    return false
  }

  const domainParts = domainPart.split('.')
  if (domainParts.length < 2 || domainParts.some((part) => part.length === 0)) {
    return false
  }

  /**
   * Check if character is valid for local part
   * @param {string} char - Character to check
   * @returns {boolean} True if valid
   */
  const isValidLocalChar = (char) => {
    const code = char.codePointAt(0)
    if (code === undefined) {
      return false
    }
    return (
      (code >= 48 && code <= 57) || // 0-9
      (code >= 65 && code <= 90) || // A-Z
      (code >= 97 && code <= 122) || // a-z
      char === '.' ||
      char === '_' ||
      char === '+' ||
      char === '-'
    )
  }

  /**
   * Check if character is valid for domain part
   * @param {string} char - Character to check
   * @returns {boolean} True if valid
   */
  const isValidDomainChar = (char) => {
    const code = char.codePointAt(0)
    if (code === undefined) {
      return false
    }
    return (
      (code >= 48 && code <= 57) || // 0-9
      (code >= 65 && code <= 90) || // A-Z
      (code >= 97 && code <= 122) || // a-z
      char === '.' ||
      char === '-'
    )
  }

  // Check if all characters are valid
  const hasInvalidLocalChar = Array.from(localPart).some((char) => !isValidLocalChar(char))
  const hasInvalidDomainChar = Array.from(domainPart).some((char) => !isValidDomainChar(char))

  return !hasInvalidLocalChar && !hasInvalidDomainChar
}

/**
 * Composable function that returns email validation utilities
 * @returns {Object} Email validation functions
 */
export function useEmailValidation() {
  return {
    isValidEmail
  }
}

