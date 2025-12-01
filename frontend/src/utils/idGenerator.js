/**
 * Utility for generating cryptographically secure unique IDs
 * Uses crypto.getRandomValues() for security instead of Math.random()
 */

/**
 * Generates a cryptographically secure unique ID
 * Uses crypto.getRandomValues() for security instead of Math.random()
 * @param {string} prefix - Prefix for the ID
 * @returns {string} Unique ID
 */
export function generateSecureId(prefix = 'id') {
  const prefixStr = prefix
  
  // Use crypto.getRandomValues() if available (cryptographically secure)
  if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
    const array = new Uint8Array(9)
    crypto.getRandomValues(array)
    // Convert to base36 string (similar to Math.random().toString(36))
    const randomStr = Array.from(array, byte => byte.toString(36)).join('').substring(0, 9)
    return `${prefixStr}-${randomStr}`
  }
  
  // Fallback: use timestamp and counter (not cryptographically secure but acceptable for DOM IDs)
  const timestamp = Date.now().toString(36)
  const counter = (generateSecureId.counter = (generateSecureId.counter || 0) + 1)
  return `${prefixStr}-${timestamp}-${counter.toString(36)}`
}

