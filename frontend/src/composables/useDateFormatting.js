/**
 * Composable for date formatting utilities
 * Provides reusable date formatting functions to eliminate code duplication
 */

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
 * Composable function that returns all date formatting utilities
 * @returns {Object} Object with all date formatting functions
 */
export function useDateFormatting() {
  return {
    formatDateTime,
    formatDate,
    formatRelativeTime,
    formatDuration
  }
}

