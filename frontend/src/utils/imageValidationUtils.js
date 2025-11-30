/**
 * Utility functions for image file validation
 * Provides reusable image validation to eliminate code duplication
 */

const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp']
const MAX_IMAGE_SIZE = 20 * 1024 * 1024 // 20MB
const MIN_IMAGE_SIZE = 1024 // 1KB

/**
 * Validate image file type
 * @param {File} file - File to validate
 * @param {string[]} allowedTypes - Allowed MIME types (default: common image types)
 * @returns {boolean} True if valid type
 */
export function validateImageType(file, allowedTypes = ALLOWED_IMAGE_TYPES) {
  if (!file) return false
  return allowedTypes.includes(file.type)
}

/**
 * Validate image file size
 * @param {File} file - File to validate
 * @param {number} maxSize - Maximum size in bytes (default: 20MB)
 * @param {number} minSize - Minimum size in bytes (default: 1KB)
 * @returns {boolean} True if valid size
 */
export function validateImageSize(file, maxSize = MAX_IMAGE_SIZE, minSize = MIN_IMAGE_SIZE) {
  if (!file) return false
  return file.size >= minSize && file.size <= maxSize
}

/**
 * Validate image file completely
 * @param {File} file - File to validate
 * @param {Object} options - Validation options
 * @returns {string[]} Array of error messages (empty if valid)
 */
export function validateImageFile(file, options = {}) {
  const errors = []
  const {
    allowedTypes = ALLOWED_IMAGE_TYPES,
    maxSize = MAX_IMAGE_SIZE,
    minSize = MIN_IMAGE_SIZE
  } = options

  if (!file) {
    errors.push('Archivo requerido')
    return errors
  }

  if (!validateImageType(file, allowedTypes)) {
    const typesList = allowedTypes.map(t => t.split('/')[1].toUpperCase()).join(', ')
    errors.push(`Formato no válido. Use ${typesList}`)
  }

  if (file.size > maxSize) {
    const maxSizeMB = (maxSize / (1024 * 1024)).toFixed(0)
    errors.push(`Archivo demasiado grande. Máximo ${maxSizeMB}MB`)
  }

  if (file.size < minSize) {
    errors.push('Archivo demasiado pequeño')
  }

  return errors
}

/**
 * Get image file validation error message
 * @param {File} file - File to validate
 * @param {Object} options - Validation options
 * @returns {string|null} Error message or null if valid
 */
export function getImageValidationError(file, options = {}) {
  const errors = validateImageFile(file, options)
  return errors.length > 0 ? errors[0] : null
}

/**
 * Validate image file and return object format (for compatibility)
 * @param {File} file - File to validate
 * @param {Object} options - Validation options
 * @returns {Object} Object with isValid and errors properties
 */
export function validateImageFileObject(file, options = {}) {
  const errors = validateImageFile(file, options)
  return {
    isValid: errors.length === 0,
    errors
  }
}

/**
 * Validate image file and return object format with single error (for compatibility)
 * @param {File} file - File to validate
 * @param {Object} options - Validation options
 * @returns {Object} Object with isValid and error properties
 */
export function validateImageFileSingleError(file, options = {}) {
  const errors = validateImageFile(file, options)
  return {
    isValid: errors.length === 0,
    error: errors.length > 0 ? errors[0] : undefined
  }
}

