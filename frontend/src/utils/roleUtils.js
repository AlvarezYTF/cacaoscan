/**
 * Utility functions for role normalization and management
 */

/**
 * Normalizes a role string to a standard format
 * @param {string|null|undefined} role - Role to normalize
 * @returns {string|null} Normalized role or null if invalid
 */
export function normalizeRole(role) {
  if (!role) return null
  const normalized = String(role).toLowerCase().trim()

  // Map common role variants
  switch (normalized) {
    case 'administrador':
    case 'administrator':
    case 'admin':
      return 'admin'
    case 'analista':
    case 'analyst':
      return 'analyst'
    case 'agricultor':
    case 'farmer':
      return 'farmer'
    default:
      return normalized
  }
}

/**
 * Gets redirect path by role
 * @param {string} role - User role
 * @returns {string} Redirect path
 */
export function getRedirectPathByRole(role) {
  const normalizedRole = normalizeRole(role)

  switch (normalizedRole) {
    case 'admin':
      return '/admin/dashboard'
    case 'analyst':
      return '/analisis'
    case 'farmer':
      return '/agricultor-dashboard'
    default:
      return '/admin/dashboard'
  }
}

