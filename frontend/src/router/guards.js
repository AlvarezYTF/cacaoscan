/**
 * Guards de rutas para CacaoScan
 * Controla el acceso a rutas según autenticación, roles y verificación
 */

// Función helper para obtener el store dinámicamente y evitar dependencias circulares
const getAuthStore = async () => {
  const { useAuthStore } = await import('@/stores/auth')
  return useAuthStore()
}

/**
 * Guard principal que verifica autenticación y validez del token
 */
export const requireAuth = async (to, from, next) => {
  const authStore = await getAuthStore()

  // Si no hay token, redirigir al login
  if (!authStore.accessToken) {
    console.warn('🚫 Acceso denegado: No hay token de acceso')
    next({
      name: 'Login',
      query: { 
        redirect: to.fullPath,
        message: 'Debes iniciar sesión para acceder a esta página'
      }
    })
    return
  }

  // Si hay token pero no hay usuario, intentar obtenerlo
  if (!authStore.user) {
    try {
      console.log('🔄 Verificando token y obteniendo datos de usuario...')
      await authStore.getCurrentUser()
    } catch (error) {
      console.warn('❌ Token inválido o expirado:', error)
      // Limpiar todo y redirigir
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

  // Verificar si la sesión ha expirado por inactividad
  if (authStore.checkSessionTimeout()) {
    console.warn('⏰ Sesión expirada por inactividad')
    return
  }

  // Actualizar actividad del usuario
  authStore.updateLastActivity()

  next()
}

/**
 * Guard que requiere que el usuario NO esté autenticado
 */
export const requireGuest = async (to, from, next) => {
  const authStore = await getAuthStore()

  if (authStore.isAuthenticated) {
    console.log('👤 Usuario ya autenticado, redirigiendo...')
    
    // Redirigir según rol usando router.replace para evitar historial
    const redirectPath = getRedirectPathByRole(authStore.userRole)
    next({ path: redirectPath, replace: true })
    return
  }

  next()
}

/**
 * Guard que requiere rol específico
 */
export const requireRole = (allowedRoles) => {
  return async (to, from, next) => {
    const authStore = await getAuthStore()

    if (!authStore.isAuthenticated) {
      console.warn('🚫 Acceso denegado: Usuario no autenticado')
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
      console.warn(`🚫 Acceso denegado: Rol '${userRole}' no autorizado. Roles permitidos: ${allowedRoles.join(', ')}`)
      
      // Redirigir a página de error o dashboard según rol
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
 * Guard que requiere usuario verificado
 */
export const requireVerified = async (to, from, next) => {
  const authStore = await getAuthStore()

  if (!authStore.isAuthenticated) {
    console.warn('🚫 Acceso denegado: Usuario no autenticado')
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
    console.warn('📧 Acceso denegado: Usuario no verificado')
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

/**
 * Guard que requiere permiso específico
 */
export const requirePermission = (permission) => {
  return async (to, from, next) => {
    const authStore = await getAuthStore()

    if (!authStore.isAuthenticated) {
      console.warn('🚫 Acceso denegado: Usuario no autenticado')
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
      console.warn(`🚫 Acceso denegado: Sin permiso '${permission}'`)
      
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
 * Guard combinado para agricultores (autenticado + verificado + rol farmer)
 */
export const requireFarmer = async (to, from, next) => {
  const authStore = await getAuthStore()

  // Verificar autenticación
  if (!authStore.isAuthenticated) {
    next({
      name: 'Login',
      query: { 
        redirect: to.fullPath,
        message: 'Debes iniciar sesión como agricultor'
      }
    })
    return
  }

  // Verificar rol
  if (!authStore.isFarmer && !authStore.isAdmin) {
    next({
      path: '/acceso-denegado',
      replace: true,
      query: {
        message: 'Esta área está destinada solo para agricultores'
      }
    })
    return
  }

  // Verificar verificación de email para ciertas funcionalidades
  if (to.meta.requiresVerification && !authStore.isVerified) {
    next({
      name: 'EmailVerification',
      query: {
        message: 'Debes verificar tu email para acceder a todas las funcionalidades'
      }
    })
    return
  }

  next()
}

/**
 * Guard para analistas
 */
export const requireAnalyst = async (to, from, next) => {
  const authStore = await getAuthStore()

  if (!authStore.isAuthenticated) {
    next({
      name: 'Login',
      query: { 
        redirect: to.fullPath,
        message: 'Debes iniciar sesión como analista'
      }
    })
    return
  }

  if (!authStore.isAnalyst && !authStore.isAdmin) {
    next({
      path: '/acceso-denegado',
      replace: true,
      query: {
        message: 'Esta área está destinada solo para analistas'
      }
    })
    return
  }

  next()
}

/**
 * Guard para administradores
 */
export const requireAdmin = async (to, from, next) => {
  const authStore = await getAuthStore()

  if (!authStore.isAuthenticated) {
    next({
      name: 'Login',
      query: { 
        redirect: to.fullPath,
        message: 'Debes iniciar sesión como administrador'
      }
    })
    return
  }

  if (!authStore.isAdmin) {
    next({
      path: '/acceso-denegado',
      replace: true,
      query: {
        message: 'Esta área está destinada solo para administradores'
      }
    })
    return
  }

  next()
}

/**
 * Guard para verificar si el usuario puede subir imágenes
 */
export const requireCanUpload = async (to, from, next) => {
  const authStore = await getAuthStore()

  if (!authStore.isAuthenticated) {
    next({
      name: 'Login',
      query: { 
        redirect: to.fullPath,
        message: 'Debes iniciar sesión para subir imágenes'
      }
    })
    return
  }

  if (!authStore.canUploadImages) {
    if (!authStore.isVerified) {
      next({
        name: 'EmailVerification',
        query: {
          message: 'Debes verificar tu email para subir imágenes'
        }
      })
    } else {
      next({
        path: '/acceso-denegado',
        replace: true,
        query: {
          message: 'No tienes permisos para subir imágenes'
        }
      })
    }
    return
  }

  next()
}

/**
 * Guard que actualiza actividad del usuario
 */
export const updateActivity = async (to, from, next) => {
  const authStore = await getAuthStore()

  if (authStore.isAuthenticated) {
    authStore.updateLastActivity()
    
    // Log de actividad en desarrollo
    if (import.meta.env.DEV) {
      console.log(`👤 Activity updated for ${authStore.user?.email} on ${to.path}`)
    }
  }

  next()
}

/**
 * Guard que verifica el estado del token en tiempo real
 */
export const checkTokenValidity = async (to, from, next) => {
  const authStore = await getAuthStore()

  if (authStore.isAuthenticated && authStore.accessToken) {
    try {
      // Verificar token haciendo una petición ligera
      await authStore.getCurrentUser()
      next()
    } catch (error) {
      console.warn('Token inválido, limpiando sesión y redirigiendo al login')
      authStore.clearAll()
      
      // Evitar loops de redirección
      if (to.name !== 'Login') {
        next({
          name: 'Login',
          replace: true,
          query: {
            message: 'Tu sesión ha expirado. Por favor inicia sesión nuevamente.',
            expired: 'true',
            redirect: to.fullPath
          }
        })
      } else {
        next()
      }
    }
  } else {
    next()
  }
}

// Funciones auxiliares

/**
 * Obtiene la ruta de redirección según el rol del usuario
 */
const getRedirectPathByRole = (role) => {
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
 * Obtiene la ruta de error según el rol del usuario
 */
const getErrorPathByRole = (role) => {
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
 * Guard compuesto que combina múltiples verificaciones
 */
export const createCompositeGuard = (...guards) => {
  return async (to, from, next) => {
    for (const guard of guards) {
      await new Promise((resolve) => {
        guard(to, from, (result) => {
          if (result === undefined || result === true) {
            resolve()
          } else {
            next(result)
            return
          }
        })
      })
    }
    next()
  }
}

// Guards específicos combinados para casos comunes
export const requireFarmerVerified = createCompositeGuard(requireAuth, requireRole(['farmer', 'admin']), requireVerified)
export const requireAnalystAuth = createCompositeGuard(requireAuth, requireRole(['analyst', 'admin']))
export const requireAdminAuth = createCompositeGuard(requireAuth, requireRole(['admin']))

// Exportar configuraciones de guards por ruta
export const ROUTE_GUARDS = {
  // Rutas públicas
  public: [],
  
  // Rutas que requieren no estar autenticado
  guest: [requireGuest],
  
  // Rutas que requieren autenticación básica
  auth: [requireAuth, updateActivity],
  
  // Rutas que requieren verificación
  verified: [requireAuth, requireVerified, updateActivity],
  
  // Rutas específicas por rol
  farmer: [requireAuth, requireRole(['farmer', 'admin']), updateActivity],
  farmerVerified: [requireAuth, requireRole(['farmer', 'admin']), requireVerified, updateActivity],
  analyst: [requireAuth, requireRole(['analyst', 'admin']), updateActivity],
  admin: [requireAuth, requireRole(['admin']), updateActivity],
  
  // Rutas con permisos específicos
  canUpload: [requireAuth, requireCanUpload, updateActivity],
  canViewAll: [requireAuth, requirePermission('view_all_predictions'), updateActivity],
  canManageUsers: [requireAuth, requirePermission('manage_users'), updateActivity]
}
