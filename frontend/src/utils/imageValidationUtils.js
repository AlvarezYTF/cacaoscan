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

/**
 * Validate image dimensions (requires image load)
 * @param {File} file - File to validate
 * @param {Object} options - Validation options
 * @param {number} options.minWidth - Minimum width in pixels
 * @param {number} options.maxWidth - Maximum width in pixels
 * @param {number} options.minHeight - Minimum height in pixels
 * @param {number} options.maxHeight - Maximum height in pixels
 * @returns {Promise<Object>} Object with isValid and errors properties
 */
export function validateImageDimensions(file, options = {}) {
  return new Promise((resolve) => {
    if (!file) {
      resolve({ isValid: false, errors: ['Archivo requerido'] })
      return
    }

    const {
      minWidth = 0,
      maxWidth = Infinity,
      minHeight = 0,
      maxHeight = Infinity
    } = options

    const img = new Image()
    const url = URL.createObjectURL(file)

    img.onload = () => {
      URL.revokeObjectURL(url)
      const errors = []

      if (img.width < minWidth) {
        errors.push(`Ancho mínimo: ${minWidth}px`)
      }
      if (img.width > maxWidth) {
        errors.push(`Ancho máximo: ${maxWidth}px`)
      }
      if (img.height < minHeight) {
        errors.push(`Alto mínimo: ${minHeight}px`)
      }
      if (img.height > maxHeight) {
        errors.push(`Alto máximo: ${maxHeight}px`)
      }

      resolve({
        isValid: errors.length === 0,
        errors,
        dimensions: {
          width: img.width,
          height: img.height
        }
      })
    }

    img.onerror = () => {
      URL.revokeObjectURL(url)
      resolve({
        isValid: false,
        errors: ['No se pudo cargar la imagen para validar dimensiones']
      })
    }

    img.src = url
  })
}

/**
 * Validate multiple image files
 * @param {File[]} files - Array of files to validate
 * @param {Object} options - Validation options
 * @returns {Object} Object with results array
 */
export function validateMultipleImages(files, options = {}) {
  if (!Array.isArray(files)) {
    return {
      isValid: false,
      errors: ['Se esperaba un array de archivos'],
      results: []
    }
  }

  const results = files.map((file, index) => {
    const validation = validateImageFile(file, options)
    return {
      index,
      file,
      isValid: validation.length === 0,
      errors: validation
    }
  })

  const allValid = results.every(r => r.isValid)
  const allErrors = results.flatMap(r => r.errors)

  return {
    isValid: allValid,
    errors: allErrors,
    results
  }
}

/**
 * Get file size in human-readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} Human-readable size
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

/**
 * Check if file is an image based on extension
 * @param {string} filename - File name
 * @returns {boolean} True if image extension
 */
export function isImageFile(filename) {
  if (!filename) return false
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']
  const extension = filename.toLowerCase().substring(filename.lastIndexOf('.'))
  return imageExtensions.includes(extension)
}

