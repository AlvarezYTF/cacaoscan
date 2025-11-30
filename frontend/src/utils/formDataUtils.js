/**
 * Shared form data utilities
 * Provides consistent form data transformation and serialization
 */

/**
 * Creates FormData from an object
 * @param {Object} data - Data object
 * @param {Object} options - Options
 * @param {Array<string>} options.exclude - Keys to exclude
 * @param {Function} options.transform - Transform function for values
 * @returns {FormData} FormData object
 */
export function createFormData(data, options = {}) {
  const { exclude = [], transform = null } = options
  const formData = new FormData()

  for (const [key, value] of Object.entries(data)) {
    // Skip excluded keys
    if (exclude.includes(key)) {
      continue
    }

    // Skip null/undefined values
    if (value === null || value === undefined) {
      continue
    }

    // Transform value if transform function provided
    const transformedValue = transform ? transform(key, value) : value

    // Handle different value types
    if (transformedValue instanceof File || transformedValue instanceof Blob) {
      formData.append(key, transformedValue)
    } else if (Array.isArray(transformedValue)) {
      transformedValue.forEach((item, index) => {
        if (item instanceof File || item instanceof Blob) {
          formData.append(`${key}[${index}]`, item)
        } else if (typeof item === 'object' && item !== null) {
          formData.append(`${key}[${index}]`, JSON.stringify(item))
        } else {
          formData.append(`${key}[${index}]`, item)
        }
      })
    } else if (typeof transformedValue === 'object' && transformedValue !== null) {
      formData.append(key, JSON.stringify(transformedValue))
    } else {
      formData.append(key, transformedValue)
    }
  }

  return formData
}

/**
 * Converts FormData to plain object
 * @param {FormData} formData - FormData object
 * @returns {Object} Plain object
 */
export function formDataToObject(formData) {
  const object = {}

  for (const [key, value] of formData.entries()) {
    // Handle array notation (key[0], key[1])
    const arrayMatch = key.match(/^(.+)\[(\d+)\]$/)
    if (arrayMatch) {
      const [, baseKey, index] = arrayMatch
      if (!object[baseKey]) {
        object[baseKey] = []
      }
      object[baseKey][Number.parseInt(index, 10)] = value
    } else {
      object[key] = value
    }
  }

  return object
}

/**
 * Serializes form data to URL-encoded string
 * @param {Object} data - Data object
 * @returns {string} URL-encoded string
 */
export function serializeFormData(data) {
  const params = new URLSearchParams()

  for (const [key, value] of Object.entries(data)) {
    if (value === null || value === undefined) {
      continue
    }

    if (Array.isArray(value)) {
      value.forEach(item => {
        params.append(key, item)
      })
    } else if (typeof value === 'object') {
      params.append(key, JSON.stringify(value))
    } else {
      params.append(key, value)
    }
  }

  return params.toString()
}

/**
 * Validates form data before submission
 * @param {Object} data - Form data
 * @param {Object} rules - Validation rules
 * @returns {Object} Validation result with isValid and errors
 */
export function validateFormData(data, rules) {
  const errors = {}
  let isValid = true

  for (const [key, rule] of Object.entries(rules)) {
    const value = data[key]

    // Required validation
    if (rule.required && (value === null || value === undefined || value === '')) {
      errors[key] = rule.message || `${key} es requerido`
      isValid = false
      continue
    }

    // Skip other validations if value is empty and not required
    if (!rule.required && (value === null || value === undefined || value === '')) {
      continue
    }

    // Type validation
    if (rule.type && typeof value !== rule.type) {
      errors[key] = rule.message || `${key} debe ser de tipo ${rule.type}`
      isValid = false
      continue
    }

    // Min/Max length validation
    if (rule.minLength && String(value).length < rule.minLength) {
      errors[key] = rule.message || `${key} debe tener al menos ${rule.minLength} caracteres`
      isValid = false
      continue
    }

    if (rule.maxLength && String(value).length > rule.maxLength) {
      errors[key] = rule.message || `${key} no puede exceder ${rule.maxLength} caracteres`
      isValid = false
      continue
    }

    // Min/Max value validation
    if (rule.min !== undefined && Number(value) < rule.min) {
      errors[key] = rule.message || `${key} debe ser mayor o igual a ${rule.min}`
      isValid = false
      continue
    }

    if (rule.max !== undefined && Number(value) > rule.max) {
      errors[key] = rule.message || `${key} debe ser menor o igual a ${rule.max}`
      isValid = false
      continue
    }

    // Pattern validation
    if (rule.pattern && !rule.pattern.test(String(value))) {
      errors[key] = rule.message || `${key} no cumple con el formato requerido`
      isValid = false
      continue
    }

    // Custom validator
    if (rule.validator && typeof rule.validator === 'function') {
      const customResult = rule.validator(value, data)
      if (customResult !== true) {
        errors[key] = typeof customResult === 'string' ? customResult : (rule.message || `${key} no es válido`)
        isValid = false
        continue
      }
    }
  }

  return { isValid, errors }
}

/**
 * Cleans form data (removes empty values, trims strings)
 * @param {Object} data - Form data
 * @param {Object} options - Options
 * @param {boolean} options.removeEmpty - Remove empty values
 * @param {boolean} options.trimStrings - Trim string values
 * @returns {Object} Cleaned form data
 */
export function cleanFormData(data, options = {}) {
  const { removeEmpty = true, trimStrings = true } = options
  const cleaned = {}

  for (const [key, value] of Object.entries(data)) {
    let cleanedValue = value

    // Trim strings
    if (trimStrings && typeof value === 'string') {
      cleanedValue = value.trim()
    }

    // Remove empty values
    if (removeEmpty) {
      if (cleanedValue === null || cleanedValue === undefined || cleanedValue === '') {
        continue
      }
    }

    cleaned[key] = cleanedValue
  }

  return cleaned
}

/**
 * Merges form data with defaults
 * @param {Object} data - Form data
 * @param {Object} defaults - Default values
 * @returns {Object} Merged form data
 */
export function mergeFormData(data, defaults) {
  return {
    ...defaults,
    ...data
  }
}

/**
 * Gets form data differences
 * @param {Object} original - Original data
 * @param {Object} current - Current data
 * @returns {Object} Differences object
 */
export function getFormDataDiff(original, current) {
  const diff = {}

  // Check for changed values
  for (const [key, value] of Object.entries(current)) {
    if (original[key] !== value) {
      diff[key] = {
        old: original[key],
        new: value
      }
    }
  }

  // Check for removed keys
  for (const key of Object.keys(original)) {
    if (!(key in current)) {
      diff[key] = {
        old: original[key],
        new: undefined
      }
    }
  }

  return diff
}
