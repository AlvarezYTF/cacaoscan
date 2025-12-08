/**
 * Guards de rutas para CacaoScan
 * Controla el acceso a rutas según autenticación, roles y verificación
 * Usa factories para reducir duplicación
 */

import { useAuthStore } from '@/stores/auth'
import {
  createAuthGuard,
  createRoleGuard,
  createVerifiedGuard,
  createPermissionGuard,
  createCompositeGuard,
  getRedirectPathByRole
} from './guardFactories'

/**
 * Guard principal que verifica autenticación y validez del token
 */
export const requireAuth = createAuthGuard({
  checkSessionTimeout: true,
  updateActivity: true
})

/**
 * Guard que requiere que el usuario NO esté autenticado
 */
export const requireGuest = async (to, from, next) => {
  const authStore = useAuthStore()

  if (authStore.isAuthenticated) {
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
  return createRoleGuard(allowedRoles)
}

/**
 * Guard que requiere usuario verificado
 */
export const requireVerified = createVerifiedGuard()

/**
 * Guard que requiere permiso específico
 */
export const requirePermission = (permission) => {
  return createPermissionGuard(permission)
}

/**
 * Guard combinado para agricultores (autenticado + verificado + rol farmer)
 */
export const requireFarmer = async (to, from, next) => {
  const authStore = useAuthStore()

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
export const requireAnalyst = createCompositeGuard(
  createAuthGuard(),
  createRoleGuard(['analyst', 'admin'])
)

/**
 * Guard para administradores
 */
export const requireAdmin = createCompositeGuard(
  createAuthGuard(),
  createRoleGuard(['admin'])
)

/**
 * Guard para verificar si el usuario puede subir imágenes
 */
export const requireCanUpload = async (to, from, next) => {
  const authStore = useAuthStore()

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

  if (authStore.canUploadImages) {
    next()
    return
  }
  
  if (authStore.isVerified) {
    // User is verified but doesn't have upload permission
    next({
      path: '/acceso-denegado',
      replace: true,
      query: {
        message: 'No tienes permisos para subir imágenes'
      }
    })
  } else {
    next({
      name: 'EmailVerification',
      query: {
        message: 'Debes verificar tu email para subir imágenes'
      }
    })
  }
}

/**
 * Guard que actualiza actividad del usuario
 */
export const updateActivity = async (to, from, next) => {
  const authStore = useAuthStore()

  if (authStore.isAuthenticated) {
    authStore.updateLastActivity()
    
    // Log de actividad en desarrollo
    if (import.meta.env.DEV) {
      }
  }

  next()
}

/**
 * Guard que verifica el estado del token en tiempo real
 */
export const checkTokenValidity = async (to, from, next) => {
  const authStore = useAuthStore()

  if (authStore.isAuthenticated && authStore.accessToken) {
    try {
      // Verificar token haciendo una petición ligera
      await authStore.getCurrentUser()
      next()
    } catch (error) {
      authStore.clearAll()
      
      // Evitar loops de redirección
      if (to.name === 'Login') {
        next()
        return
      }
      
      next({
        name: 'Login',
        replace: true
      })
    }
  } else if (to.name === 'Login') {
    // Si no hay token y ya está en login, permitir acceso
    next()
  } else {
    // Si no hay token, redirigir al login
    next({
      name: 'Login',
      replace: true,
      query: {
        message: 'Tu sesión ha expirado. Por favor inicia sesión nuevamente.',
        expired: 'true',
        redirect: to.fullPath
      }
    })
  }
}

// Guards específicos combinados para casos comunes
export const requireFarmerVerified = createCompositeGuard(
  createAuthGuard(),
  createRoleGuard(['farmer', 'admin']),
  createVerifiedGuard()
)
export const requireAnalystAuth = createCompositeGuard(
  createAuthGuard(),
  createRoleGuard(['analyst', 'admin'])
)
export const requireAdminAuth = createCompositeGuard(
  createAuthGuard(),
  createRoleGuard(['admin'])
)

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
