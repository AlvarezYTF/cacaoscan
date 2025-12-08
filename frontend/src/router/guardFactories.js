/**
 * Factory functions for router guards
 * Reduces duplication in guards.js
 */
import { useAuthStore } from '@/stores/auth'

/**
 * Get redirect path by user role
 * @param {string} role - User role
 * @returns {string} Redirect path
 */
export const getRedirectPathByRole = (role) => {
  switch (role) {
    case 'admin':
      return '/admin/dashboard'
    case 'analyst':
      return '/analisis'
    case 'farmer':
      return '/agricultor-dashboard'
    default:
      return '/'
  }
}

/**
 * Get error path by user role
 * @param {string} role - User role
 * @returns {string} Error path
 */
export const getErrorPathByRole = (role) => {
  switch (role) {
    case 'admin':
      return '/admin/dashboard'
    case 'analyst':
      return '/analisis'
    case 'farmer':
      return '/agricultor-dashboard'
    default:
      return '/acceso-denegado'
  }
}

/**
 * Create authentication guard
 * @param {Object} options - Guard options
 * @param {boolean} options.checkSessionTimeout - Check session timeout
 * @param {boolean} options.updateActivity - Update user activity
 * @returns {Function} Guard function
 */
export const createAuthGuard = (options = {}) => {
  const {
    checkSessionTimeout = true,
    updateActivity = true
  } = options

  return async (to, from, next) => {
    const authStore = useAuthStore()

    // Check token
    if (!authStore.accessToken) {
      next({
        name: 'Login',
        query: {
          redirect: to.fullPath,
          message: 'Debes iniciar sesión para acceder a esta página'
        }
      })
      return
    }

    // Get user if not loaded
    if (!authStore.user) {
      try {
        await authStore.getCurrentUser()
      } catch (error) {
        authStore.clearAll()
        next({
          name: 'Login',
          query: {
            redirect: to.fullPath,
            message: 'Tu sesión ha expirado. Inicia sesión nuevamente.',
            expired: 'true'
          }
        })
        return
      }
    }

    // Check session timeout
    if (checkSessionTimeout && authStore.checkSessionTimeout()) {
      return
    }

    // Update activity
    if (updateActivity) {
      authStore.updateLastActivity()
    }

    next()
  }
}

/**
 * Create role guard
 * @param {string[]} allowedRoles - Allowed roles
 * @param {Object} options - Guard options
 * @returns {Function} Guard function
 */
export const createRoleGuard = (allowedRoles, options = {}) => {
  return async (to, from, next) => {
    const authStore = useAuthStore()

    if (!authStore.isAuthenticated) {
      next({
        name: 'Login',
        query: {
          redirect: to.fullPath,
          message: 'Debes iniciar sesión para acceder a esta página'
        }
      })
      return
    }

    const userRole = authStore.userRole
    const hasRequiredRole = allowedRoles.includes(userRole)

    if (!hasRequiredRole) {
      }`)
      
      const errorPath = getErrorPathByRole(userRole)
      next({
        path: errorPath,
        replace: true,
        query: {
          error: 'access_denied',
          message: 'No tienes permisos para acceder a esta página'
        }
      })
      return
    }

    next()
  }
}

/**
 * Create verified user guard
 * @returns {Function} Guard function
 */
export const createVerifiedGuard = () => {
  return async (to, from, next) => {
    const authStore = useAuthStore()

    if (!authStore.isAuthenticated) {
      next({
        name: 'Login',
        query: {
          redirect: to.fullPath,
          message: 'Debes iniciar sesión para acceder a esta página'
        }
      })
      return
    }

    if (!authStore.isVerified) {
      next({
        name: 'EmailVerification',
        query: {
          message: 'Debes verificar tu email para acceder a esta funcionalidad'
        }
      })
      return
    }

    next()
  }
}

/**
 * Create permission guard
 * @param {string} permission - Required permission
 * @returns {Function} Guard function
 */
export const createPermissionGuard = (permission) => {
  return async (to, from, next) => {
    const authStore = useAuthStore()

    if (!authStore.isAuthenticated) {
      next({
        name: 'Login',
        query: {
          redirect: to.fullPath,
          message: 'Debes iniciar sesión para acceder a esta página'
        }
      })
      return
    }

    if (!authStore.hasPermission(permission)) {
      const errorPath = getErrorPathByRole(authStore.userRole)
      next({
        path: errorPath,
        replace: true,
        query: {
          error: 'insufficient_permissions',
          message: 'No tienes los permisos necesarios para acceder a esta página'
        }
      })
      return
    }

    next()
  }
}

/**
 * Create composite guard from multiple guards
 * @param {...Function} guards - Guard functions
 * @returns {Function} Composite guard function
 */
export const createCompositeGuard = (...guards) => {
  return async (to, from, next) => {
    for (const guard of guards) {
      let shouldContinue = true
      await new Promise((resolve) => {
        guard(to, from, (result) => {
          if (result === undefined || result === true) {
            resolve()
          } else {
            shouldContinue = false
            next(result)
            resolve()
          }
        })
      })
      if (!shouldContinue) {
        return
      }
    }
    next()
  }
}

