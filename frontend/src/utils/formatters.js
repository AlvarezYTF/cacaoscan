/**
 * Centralized formatting utilities
 * Provides reusable formatting functions for numbers, dates, percentages, etc.
 */

/**
 * Format number with locale
 * @param {number|string} value - Value to format
 * @param {Object} options - Formatting options
 * @param {string} options.locale - Locale string
 * @param {number} options.minimumFractionDigits - Minimum fraction digits
 * @param {number} options.maximumFractionDigits - Maximum fraction digits
 * @returns {string} Formatted number
 */
export function formatNumber(value, options = {}) {
  const {
    locale = 'es-CO',
    minimumFractionDigits = 0,
    maximumFractionDigits = 2
  } = options

  const numValue = typeof value === 'number' ? value : Number.parseFloat(value)
  
  if (Number.isNaN(numValue)) {
    return String(value)
  }

  return new Intl.NumberFormat(locale, {
    minimumFractionDigits,
    maximumFractionDigits
  }).format(numValue)
}

/**
 * Format currency
 * @param {number|string} value - Value to format
 * @param {Object} options - Formatting options
 * @param {string} options.currency - Currency code
 * @param {string} options.locale - Locale string
 * @returns {string} Formatted currency
 */
export function formatCurrency(value, options = {}) {
  const {
    currency = 'COP',
    locale = 'es-CO'
  } = options

  const numValue = typeof value === 'number' ? value : Number.parseFloat(value)
  
  if (Number.isNaN(numValue)) {
    return String(value)
  }

  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
    useGrouping: false
  }).format(numValue)
}

/**
 * Format percentage
 * @param {number|string} value - Value to format
 * @param {Object} options - Formatting options
 * @param {number} options.decimals - Number of decimals
 * @returns {string} Formatted percentage
 */
export function formatPercentage(value, options = {}) {
  const { decimals = 1 } = options

  const numValue = typeof value === 'number' ? value : Number.parseFloat(value)
  
  if (Number.isNaN(numValue)) {
    return String(value)
  }

  // Return '0%' for zero values instead of '0.0%'
  if (numValue === 0) {
    return '0%'
  }

  return `${numValue.toFixed(decimals)}%`
}

/**
 * Format date
 * @param {string|Date} date - Date to format
 * @param {Object} options - Formatting options
 * @param {string} options.locale - Locale string
 * @param {Object} options.dateStyle - Date style
 * @param {Object} options.timeStyle - Time style
 * @returns {string} Formatted date
 */
export function formatDate(date, options = {}) {
  const {
    locale = 'es-ES',
    dateStyle = 'short',
    timeStyle = undefined
  } = options

  if (!date) {
    return 'N/A'
  }

  const dateObj = date instanceof Date ? date : new Date(date)
  
  if (Number.isNaN(dateObj.getTime())) {
    return 'N/A'
  }

  const formatOptions = { dateStyle }
  if (timeStyle) {
    formatOptions.timeStyle = timeStyle
  }

  return new Intl.DateTimeFormat(locale, formatOptions).format(dateObj)
}

/**
 * Format date time
 * @param {string|Date} date - Date to format
 * @param {Object} options - Formatting options
 * @returns {string} Formatted date time
 */
export function formatDateTime(date, options = {}) {
  return formatDate(date, {
    ...options,
    timeStyle: 'short'
  })
}

/**
 * Format change value (for stats)
 * @param {number|string} change - Change value
 * @param {Object} options - Formatting options
 * @returns {string} Formatted change
 */
export function formatChange(change, options = {}) {
  const { showSign = true } = options

  const numValue = typeof change === 'number' ? change : Number.parseFloat(change)
  
  if (Number.isNaN(numValue)) {
    return String(change)
  }

  if (numValue === 0) {
    return '0%'
  }

  const formatted = formatPercentage(Math.abs(numValue), { decimals: 1 })
  
  if (numValue < 0) {
    return `-${formatted}`
  }
  
  return showSign ? `+${formatted}` : formatted
}

/**
 * Format file size
 * @param {number} bytes - Size in bytes
 * @returns {string} Formatted file size
 */
export function formatFileSize(bytes) {
  if (!bytes || bytes === 0) {
    return '0 B'
  }

  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  const size = bytes / Math.pow(1024, i)
  
  return `${Math.round(size * 100) / 100} ${sizes[i]}`
}

/**
 * Format duration in seconds
 * @param {number} seconds - Duration in seconds
 * @returns {string} Formatted duration
 */
export function formatDuration(seconds) {
  if (!seconds || seconds === 0) {
    return '0s'
  }

  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60

  if (minutes === 0) {
    return `${remainingSeconds}s`
  }

  if (remainingSeconds === 0) {
    return `${minutes}m`
  }

  return `${minutes}m ${remainingSeconds}s`
}

/**
 * Parse change string to number
 * @param {string} change - Change string like '+5%' or '-1.2%'
 * @returns {number} Numeric change value
 */
export function parseChange(change) {
  if (!change || typeof change !== 'string') {
    return 0
  }
  
  const trimmed = change.trim()
  // Use non-capturing group with specific pattern to avoid backtracking (ReDoS prevention)
  const regex = /^([+-]?)(\d+(?:\.\d+)?)/
  const match = regex.exec(trimmed)
  if (!match) {
    return 0
  }
  
  const sign = match[1] === '-' ? -1 : 1
  const value = Number.parseFloat(match[2])
  
  if (Number.isNaN(value)) {
    return 0
  }
  
  return sign * value
}

