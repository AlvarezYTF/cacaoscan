/**
 * Security utilities for sanitizing and escaping content.
 */

/**
 * Generates a cryptographically secure unique ID
 * Uses crypto.getRandomValues() for security instead of Math.random()
 * This prevents security warnings from static analysis tools (SonarQube S2245)
 * 
 * @param {string} prefix - Prefix for the ID (default: 'id')
 * @returns {string} Unique ID in format: prefix-randomstring
 */
export function generateSecureId(prefix = 'id') {
  // Use crypto.getRandomValues() if available (cryptographically secure)
  if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
    const array = new Uint8Array(9)
    crypto.getRandomValues(array)
    // Convert to base36 string (similar to Math.random().toString(36))
    const randomStr = Array.from(array, byte => byte.toString(36)).join('').substring(0, 9)
    return `${prefix}-${randomStr}`
  }
  
  // Fallback: use timestamp and counter (not cryptographically secure but acceptable for DOM IDs)
  const timestamp = Date.now().toString(36)
  const counter = (generateSecureId.counter = (generateSecureId.counter || 0) + 1)
  return `${prefix}-${timestamp}-${counter.toString(36)}`
}

/**
 * Sanitizes HTML content to prevent XSS attacks.
 * Removes dangerous tags (script, style) and their content, removes event handlers,
 * and escapes remaining HTML to return safe text content.
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
  
  // Parse HTML into DOM structure
  container.innerHTML = html
  
  // Remove dangerous tags and their content
  const dangerousTags = container.querySelectorAll('script, style, iframe, object, embed, form')
  for (const tag of dangerousTags) {
    tag.remove()
  }
  
  // Remove event handler attributes from all elements (including container)
  const allElements = [container, ...Array.from(container.querySelectorAll('*'))]
  for (const element of allElements) {
    // Get all attributes
    const attributes = Array.from(element.attributes)
    for (const attr of attributes) {
      // Remove event handlers (onclick, onerror, etc.)
      if (attr.name.toLowerCase().startsWith('on') && attr.name.length > 2) {
        element.removeAttribute(attr.name)
      }
      // Remove javascript: protocol in href/src
      if ((attr.name === 'href' || attr.name === 'src') && attr.value.toLowerCase().startsWith('javascript:')) {
        element.removeAttribute(attr.name)
      }
    })
  })
  
  // Extract text content and escape it
  const textContent = container.textContent || container.innerText || ''
  return escapeHTML(textContent)
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

  return text.replaceAll(/[&<>"']/g, (char) => map[char])
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
  const dangerousChars = /[<>:"|?*]/
  if (dangerousChars.test(filename)) {
    return false
  }

  // Check for control characters (0x00-0x1F) without using control chars in regex
  for (let i = 0; i < filename.length; i++) {
    const codePoint = filename.codePointAt(i)
    if (codePoint !== undefined && codePoint >= 0x00 && codePoint <= 0x1F) {
      return false
    }
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
  sanitized = sanitized.replaceAll(/[<>:"|?*]/g, '_')
  
  // Remove control characters (0x00-0x1F) without using control chars in regex
  let cleaned = ''
  for (let i = 0; i < sanitized.length; i++) {
    const codePoint = sanitized.codePointAt(i)
    if (codePoint !== undefined && codePoint >= 0x00 && codePoint <= 0x1F) {
      cleaned += '_'
    } else {
      cleaned += sanitized[i]
    }
  }
  sanitized = cleaned
  
  // Remove path traversal attempts
  sanitized = sanitized.replaceAll('..', '_')
  
  // Trim whitespace
  sanitized = sanitized.trim()
  
  // If empty after sanitization or only contains replacement characters, use default
  if (sanitized.length === 0 || sanitized.replaceAll('_', '').length === 0) {
    sanitized = 'file'
  }

  // Limit length
  if (sanitized.length > 255) {
    const ext = sanitized.substring(sanitized.lastIndexOf('.'))
    sanitized = sanitized.substring(0, 255 - ext.length) + ext
  }

  return sanitized
}

