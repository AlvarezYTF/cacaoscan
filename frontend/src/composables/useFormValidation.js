/**
 * Composable para validación de formularios reutilizable
 */
import { reactive } from 'vue'

export function useFormValidation() {
  const errors = reactive({})

  /**
   * Valida un email
   * @param {string} email - Email a validar
   * @returns {boolean}
   */
  const isValidEmail = (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
  }

  /**
   * Valida un teléfono
   * @param {string} phone - Teléfono a validar
   * @returns {boolean}
   */
  const isValidPhone = (phone) => {
    if (!phone) return true // Opcional
    const cleanPhone = phone.replace(/[\s\-\(\)]/g, '')
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
    Object.keys(errors).forEach(key => delete errors[key])
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
    hasErrors
  }
}

