/**
 * Shared form data utilities
 * Provides consistent form data transformation and serialization
 */

/**
 * Appends array items to FormData
 * @param {FormData} formData - FormData object
 * @param {string} key - Key name
 * @param {Array} arrayValue - Array value
 * @returns {void}
 */
function appendArrayItem(formData, itemKey, item) {
  if (item instanceof File || item instanceof Blob) {
    formData.append(itemKey, item)
  } else if (typeof item === 'object' && item !== null) {
    formData.append(itemKey, JSON.stringify(item))
  } else {
    formData.append(itemKey, item)
  }
}

function appendArrayToFormData(formData, key, arrayValue) {
  for (let index = 0; index < arrayValue.length; index++) {
    const item = arrayValue[index]
    const itemKey = `${key}[${index}]`
    appendArrayItem(formData, itemKey, item)
  }
}

/**
 * Appends a value to FormData based on its type
 * @param {FormData} formData - FormData object
 * @param {string} key - Key name
 * @param {*} value - Value to append
 * @returns {void}
 */
function appendValueToFormData(formData, key, value) {
  if (value instanceof File || value instanceof Blob) {
    formData.append(key, value)
  } else if (Array.isArray(value)) {
    appendArrayToFormData(formData, key, value)
  } else if (typeof value === 'object' && value !== null) {
    formData.append(key, JSON.stringify(value))
  } else {
    formData.append(key, value)
  }
}

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
    if (exclude.includes(key) || value === null || value === undefined) {
      continue
    }

    const transformedValue = transform ? transform(key, value) : value
    appendValueToFormData(formData, key, transformedValue)
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
    // Use [^[]+ instead of .+ to avoid backtracking (ReDoS prevention)
    const arrayMatch = key.match(/^([^[]+)\[(\d+)\]$/)
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
      for (const item of value) {
        params.append(key, item)
      }
    } else if (typeof value === 'object') {
      params.append(key, JSON.stringify(value))
    } else {
      params.append(key, value)
    }
  }

  return params.toString()
}

/**
 * Checks if value is empty
 * @param {*} value - Value to check
 * @returns {boolean} True if value is empty
 */
function isEmpty(value) {
  return value === null || value === undefined || value === ''
}

/**
 * Validates required field
 * @param {*} value - Field value
 * @param {Object} rule - Validation rule
 * @param {string} key - Field key
 * @returns {string|null} Error message or null
 */
function validateRequired(value, rule, key) {
  if (rule.required && isEmpty(value)) {
    return rule.message || `${key} es requerido`
  }
  return null
}

/**
 * Validates field type
 * @param {*} value - Field value
 * @param {Object} rule - Validation rule
 * @param {string} key - Field key
 * @returns {string|null} Error message or null
 */
function validateType(value, rule, key) {
  if (rule.type && typeof value !== rule.type) {
    return rule.message || `${key} debe ser de tipo ${rule.type}`
  }
  return null
}

/**
 * Validates string length
 * @param {*} value - Field value
 * @param {Object} rule - Validation rule
 * @param {string} key - Field key
 * @returns {string|null} Error message or null
 */
function validateLength(value, rule, key) {
  const strValue = String(value)
  
  if (rule.minLength && strValue.length < rule.minLength) {
    return rule.message || `${key} debe tener al menos ${rule.minLength} caracteres`
  }
  
  if (rule.maxLength && strValue.length > rule.maxLength) {
    return rule.message || `${key} no puede exceder ${rule.maxLength} caracteres`
  }
  
  return null
}

/**
 * Validates numeric range
 * @param {*} value - Field value
 * @param {Object} rule - Validation rule
 * @param {string} key - Field key
 * @returns {string|null} Error message or null
 */
function validateRange(value, rule, key) {
  const numValue = Number(value)
  
  if (rule.min !== undefined && numValue < rule.min) {
    return rule.message || `${key} debe ser mayor o igual a ${rule.min}`
  }
  
  if (rule.max !== undefined && numValue > rule.max) {
    return rule.message || `${key} debe ser menor o igual a ${rule.max}`
  }
  
  return null
}

/**
 * Validates pattern
 * @param {*} value - Field value
 * @param {Object} rule - Validation rule
 * @param {string} key - Field key
 * @returns {string|null} Error message or null
 */
function validatePattern(value, rule, key) {
  if (rule.pattern && !rule.pattern.test(String(value))) {
    return rule.message || `${key} no cumple con el formato requerido`
  }
  return null
}

/**
 * Validates custom validator
 * @param {*} value - Field value
 * @param {Object} rule - Validation rule
 * @param {string} key - Field key
 * @param {Object} data - Full form data
 * @returns {string|null} Error message or null
 */
function validateCustom(value, rule, key, data) {
  if (rule.validator && typeof rule.validator === 'function') {
    const customResult = rule.validator(value, data)
    if (customResult !== true) {
      return typeof customResult === 'string' 
        ? customResult 
        : (rule.message || `${key} no es válido`)
    }
  }
  return null
}

/**
 * Validates a single field
 * @param {*} value - Field value
 * @param {Object} rule - Validation rule
 * @param {string} key - Field key
 * @param {Object} data - Full form data
 * @returns {string|null} Error message or null
 */
function validateField(value, rule, key, data) {
  const requiredError = validateRequired(value, rule, key)
  if (requiredError) {
    return requiredError
  }

  if (!rule.required && isEmpty(value)) {
    return null
  }

  const typeError = validateType(value, rule, key)
  if (typeError) {
    return typeError
  }

  const lengthError = validateLength(value, rule, key)
  if (lengthError) {
    return lengthError
  }

  const rangeError = validateRange(value, rule, key)
  if (rangeError) {
    return rangeError
  }

  const patternError = validatePattern(value, rule, key)
  if (patternError) {
    return patternError
  }

  const customError = validateCustom(value, rule, key, data)
  if (customError) {
    return customError
  }

  return null
}

/**
 * Validates form data before submission
 * @param {Object} data - Form data
 * @param {Object} rules - Validation rules
 * @returns {Object} Validation result with isValid and errors
 */
export function validateFormData(data, rules) {
  const errors = {}

  for (const [key, rule] of Object.entries(rules)) {
    const value = data[key]
    const error = validateField(value, rule, key, data)
    
    if (error) {
      errors[key] = error
    }
  }

  return { 
    isValid: Object.keys(errors).length === 0, 
    errors 
  }
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

/**
 * Creates FormData for image upload with file and metadata
 * @param {File} file - Image file
 * @param {Object} metadata - Additional metadata
 * @returns {FormData} FormData object with image and metadata
 */
export function createImageFormData(file, metadata = {}) {
  const formData = new FormData()
  
  // Add image file
  if (file) {
    formData.append('image', file)
  }
  
  // Add metadata
  for (const [key, value] of Object.entries(metadata)) {
    if (value !== null && value !== undefined && value !== '') {
      formData.append(key, value)
    }
  }
  
  return formData
}
