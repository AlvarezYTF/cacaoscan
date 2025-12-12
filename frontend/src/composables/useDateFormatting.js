/**
 * Composable for date formatting utilities
 * Provides reusable date formatting functions to eliminate code duplication
 */
import { computed } from 'vue'

/**
 * Format date and time to Spanish locale string
 * @param {string|Date|null|undefined} dateString - Date string or Date object
 * @param {Object} options - Formatting options
 * @returns {string} Formatted date string or 'N/A' if invalid
 */
export function formatDateTime(dateString, options = {}) {
  if (!dateString) return 'N/A'
  
  const date = dateString instanceof Date ? dateString : new Date(dateString)
  if (Number.isNaN(date.getTime())) return 'N/A'
  
  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    ...options
  }
  
  return date.toLocaleString('es-ES', defaultOptions)
}

/**
 * Format date only (without time) to Spanish locale string
 * @param {string|Date|null|undefined} dateString - Date string or Date object
 * @param {Object} options - Formatting options
 * @returns {string} Formatted date string or 'N/A' if invalid
 */
export function formatDate(dateString, options = {}) {
  if (!dateString) return 'N/A'
  
  const date = dateString instanceof Date ? dateString : new Date(dateString)
  if (Number.isNaN(date.getTime())) return 'N/A'
  
  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...options
  }
  
  return date.toLocaleDateString('es-ES', defaultOptions)
}

/**
 * Format relative time (e.g., "Hace 5 minutos")
 * @param {string|Date|null|undefined} dateString - Date string or Date object
 * @returns {string} Relative time string or formatted date if older than 7 days
 */
export function formatRelativeTime(dateString) {
  if (!dateString) return 'N/A'
  
  const date = dateString instanceof Date ? dateString : new Date(dateString)
  if (Number.isNaN(date.getTime())) return 'N/A'
  
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'Hace un momento'
  if (diffMins < 60) return `Hace ${diffMins} minuto${diffMins === 1 ? '' : 's'}`
  if (diffHours < 24) return `Hace ${diffHours} hora${diffHours === 1 ? '' : 's'}`
  if (diffDays < 7) return `Hace ${diffDays} día${diffDays === 1 ? '' : 's'}`
  
  return date.toLocaleDateString('es-ES')
}

/**
 * Format duration string (e.g., "1:23:45" to "1h 23m")
 * @param {string|null|undefined} durationString - Duration string in format "HH:MM:SS"
 * @returns {string} Formatted duration or 'N/A' if invalid
 */
export function formatDuration(durationString) {
  if (!durationString) return 'N/A'
  
  const parts = durationString.split(':')
  if (parts.length === 3) {
    const hours = Number.parseInt(parts[0], 10)
    const minutes = Number.parseInt(parts[1], 10)
    const seconds = Number.parseInt(parts[2], 10)
    
    if (Number.isNaN(hours) || Number.isNaN(minutes) || Number.isNaN(seconds)) {
      return durationString
    }
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`
    } else if (minutes > 0) {
      return `${minutes}m ${seconds}s`
    } else {
      return `${seconds}s`
    }
  }
  
  return durationString
}

/**
 * Calculate minimum birthdate (120 years ago)
 * @returns {string} ISO date string for minimum birthdate
 */
export function getMinBirthdate() {
  const today = new Date()
  const minDate = new Date(today.getFullYear() - 120, today.getMonth(), today.getDate())
  return minDate.toISOString().split('T')[0]
}

/**
 * Calculate maximum birthdate (14 years ago)
 * @returns {string} ISO date string for maximum birthdate
 */
export function getMaxBirthdate() {
  const today = new Date()
  const maxDate = new Date(today.getFullYear() - 14, today.getMonth(), today.getDate())
  return maxDate.toISOString().split('T')[0]
}

/**
 * Calculate age from birthdate
 * @param {string|Date} birthdate - Birthdate string or Date object
 * @returns {number|null} Age in years or null if invalid
 */
export function calculateAge(birthdate) {
  if (!birthdate) return null
  
  const birth = birthdate instanceof Date ? birthdate : new Date(birthdate)
  if (Number.isNaN(birth.getTime())) return null
  
  const today = new Date()
  let age = today.getFullYear() - birth.getFullYear()
  const monthDiff = today.getMonth() - birth.getMonth()
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--
  }
  
  return age
}

/**
 * Validate if birthdate is within valid range (14-120 years)
 * @param {string|Date} birthdate - Birthdate to validate
 * @returns {Object} Validation result with isValid and message
 */
export function validateBirthdateRange(birthdate) {
  if (!birthdate) {
    return {
      isValid: false,
      message: 'La fecha de nacimiento es requerida'
    }
  }
  
  const birth = birthdate instanceof Date ? birthdate : new Date(birthdate)
  if (Number.isNaN(birth.getTime())) {
    return {
      isValid: false,
      message: 'Fecha de nacimiento inválida'
    }
  }
  
  const age = calculateAge(birth)
  if (age === null) {
    return {
      isValid: false,
      message: 'No se pudo calcular la edad'
    }
  }
  
  if (age < 14) {
    return {
      isValid: false,
      message: 'Debes tener al menos 14 años'
    }
  }
  
  if (age > 120) {
    return {
      isValid: false,
      message: 'La edad no puede ser mayor a 120 años'
    }
  }
  
  return {
    isValid: true,
    message: null
  }
}

/**
 * Format dimensions string (e.g., "10.5 × 12.3 × 5.2 mm")
 * @param {Object} prediction - Prediction object with width, height, thickness
 * @param {Function} formatNumberFn - Function to format numbers (optional)
 * @returns {string} Formatted dimensions string
 */
export function formatDimensions(prediction, formatNumberFn = null) {
  if (!prediction) return 'N/A'
  
  const formatNum = formatNumberFn || ((value) => {
    if (value === null || value === undefined) return 'N/A'
    const num = Number.parseFloat(value)
    return Number.isNaN(num) ? 'N/A' : num.toFixed(2)
  })
  
  const width = formatNum(prediction.width)
  const height = formatNum(prediction.height)
  const thickness = formatNum(prediction.thickness)
  
  return `${width} × ${height} × ${thickness} mm`
}

/**
 * Composable function that returns all date formatting utilities and birthdate helpers
 * @returns {Object} Object with all date formatting functions and birthdate utilities
 */
export function useDateFormatting() {
  return {
    formatDateTime,
    formatDate,
    formatRelativeTime,
    formatDuration,
    getMinBirthdate,
    getMaxBirthdate,
    calculateAge,
    validateBirthdateRange,
    formatDimensions
  }
}

/**
 * Composable for birthdate range (maintains backward compatibility)
 * @returns {Object} Computed birthdate range values
 */
export function useBirthdateRange() {
  return {
    maxBirthdate: computed(() => getMaxBirthdate()),
    minBirthdate: computed(() => getMinBirthdate())
  }
}

