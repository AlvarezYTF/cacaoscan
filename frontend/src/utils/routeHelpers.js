/**
 * Helper functions for creating route configurations
 */

/**
 * Creates a route meta configuration with common defaults
 * @param {string} title - Page title
 * @param {Object} options - Route meta options
 * @param {boolean} options.requiresAuth - Requires authentication
 * @param {boolean} options.requiresGuest - Requires guest (not authenticated)
 * @param {string} options.requiresRole - Required role
 * @param {boolean} options.requiresVerification - Requires email verification
 * @returns {Object} Route meta configuration
 */
export function createRouteMeta(title, options = {}) {
  const {
    requiresAuth = false,
    requiresGuest = false,
    requiresRole = null,
    requiresVerification = false
  } = options

  const meta = {
    title: `${title} | CacaoScan`,
    requiresAuth
  }

  if (requiresGuest) {
    meta.requiresGuest = true
  }

  if (requiresRole) {
    meta.requiresRole = requiresRole
  }

  if (requiresVerification) {
    meta.requiresVerification = requiresVerification
  }

  return meta
}

/**
 * Creates a public route configuration
 * @param {string} path - Route path
 * @param {string} name - Route name
 * @param {Function|Object} component - Route component
 * @param {string} title - Page title
 * @returns {Object} Route configuration
 */
export function createPublicRoute(path, name, component, title) {
  return {
    path,
    name,
    component,
    meta: createRouteMeta(title, { requiresAuth: false })
  }
}

/**
 * Creates an authenticated route configuration
 * @param {string} path - Route path
 * @param {string} name - Route name
 * @param {Function|Object} component - Route component
 * @param {string} title - Page title
 * @param {Object} options - Additional route options
 * @param {string} options.requiresRole - Required role
 * @param {boolean} options.requiresVerification - Requires email verification
 * @returns {Object} Route configuration
 */
export function createAuthRoute(path, name, component, title, options = {}) {
  return {
    path,
    name,
    component,
    meta: createRouteMeta(title, {
      requiresAuth: true,
      requiresRole: options.requiresRole || null,
      requiresVerification: options.requiresVerification || false
    })
  }
}

/**
 * Creates a guest route configuration
 * @param {string} path - Route path
 * @param {string} name - Route name
 * @param {Function|Object} component - Route component
 * @param {string} title - Page title
 * @returns {Object} Route configuration
 */
export function createGuestRoute(path, name, component, title) {
  return {
    path,
    name,
    component,
    meta: createRouteMeta(title, { requiresGuest: true })
  }
}

