/**
 * Security utilities for sanitizing and escaping content.
 */

/**
 * Sanitizes HTML content to prevent XSS attacks.
 * Uses DOMParser to create a safe DOM structure and extracts text content.
 * For more complex HTML, consider using DOMPurify library.
 * 
 * @param {string} html - HTML content to sanitize
 * @returns {string} - Sanitized HTML string
 */
export function sanitizeHTML(html) {
  if (!html || typeof html !== 'string') {
    return ''
  }

  // Create a temporary container element
  const container = document.createElement('div')
  
  // Set text content which automatically escapes HTML
  // Then we'll allow only safe tags
  container.textContent = html
  
  // If we need to preserve some HTML, parse and filter
  // For now, we'll use a simple approach: escape all HTML
  return container.innerHTML
}

/**
 * Escapes HTML special characters to prevent XSS.
 * 
 * @param {string} text - Text to escape
 * @returns {string} - Escaped HTML string
 */
export function escapeHTML(text) {
  if (!text || typeof text !== 'string') {
    return ''
  }

  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  }

  return text.replace(/[&<>"']/g, (char) => map[char])
}

/**
 * Validates that a filename is safe (no path traversal or dangerous characters).
 * 
 * @param {string} filename - Filename to validate
 * @returns {boolean} - True if filename is safe
 */
export function isValidFilename(filename) {
  if (!filename || typeof filename !== 'string') {
    return false
  }

  // Check for path traversal attempts
  if (filename.includes('..') || filename.includes('/') || filename.includes('\\')) {
    return false
  }

  // Check for null bytes
  if (filename.includes('\0')) {
    return false
  }

  // Check for dangerous characters
  const dangerousChars = /[<>:"|?*\x00-\x1f]/
  if (dangerousChars.test(filename)) {
    return false
  }

  // Filename should not be empty or only whitespace
  if (filename.trim().length === 0) {
    return false
  }

  return true
}

/**
 * Sanitizes a filename by removing dangerous characters.
 * 
 * @param {string} filename - Filename to sanitize
 * @returns {string} - Sanitized filename
 */
export function sanitizeFilename(filename) {
  if (!filename || typeof filename !== 'string') {
    return 'file'
  }

  // Remove path components
  let sanitized = filename.replace(/^.*[\\/]/, '')
  
  // Remove dangerous characters
  sanitized = sanitized.replace(/[<>:"|?*\x00-\x1f]/g, '_')
  
  // Remove path traversal attempts
  sanitized = sanitized.replace(/\.\./g, '_')
  
  // Trim whitespace
  sanitized = sanitized.trim()
  
  // If empty after sanitization, use default
  if (sanitized.length === 0) {
    sanitized = 'file'
  }

  // Limit length
  if (sanitized.length > 255) {
    const ext = sanitized.substring(sanitized.lastIndexOf('.'))
    sanitized = sanitized.substring(0, 255 - ext.length) + ext
  }

  return sanitized
}

