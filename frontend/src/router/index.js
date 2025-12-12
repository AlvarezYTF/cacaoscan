import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/Pages/HomeView.vue'

//Vistas Admin
import AdminAnalisis from '../views/common/Analisis.vue'
import AdminConfiguracion from '../views/Admin/AdminConfiguracion.vue'
import AdminDashboard from '../views/Admin/AdminDashboard.vue'
import AdminAgricultores from '../views/Admin/AdminAgricultores.vue'
import AdminTraining from '../views/Admin/AdminTraining.vue'
import AdminUsuarios from '../views/Admin/AdminUsuarios.vue'

import DetalleAnalisisView from '../views/DetalleAnalisisView.vue'
import LoginView from '../views/Auth/LoginView.vue'
import RegisterView from '../views/Auth/RegisterView.vue'
import Reportes from '../views/Reportes.vue'
import ReportsManagement from '../views/ReportsManagement.vue'
import AgricultorDashboard from '../views/Agricultor/AgricultorDashboard.vue'
import Historial from '../views/Agricultor/AgricultorHistorial.vue'
import AgricultorReportes from '../views/Agricultor/AgricultorReportes.vue'
import AgricultorConfiguracion from '../views/Agricultor/AgricultorConfiguracion.vue'
import PredictionView from '../views/PredictionView.vue'
import UserPrediction from '../views/UserPrediction.vue'
import SubirDatosEntrenamiento from '../views/SubirDatosEntrenamiento.vue'
import FincasView from '../views/common/FincasView.vue'
import LotesView from '../views/LotesView.vue'

// Importar auth store
import { useAuthStore } from '@/stores/auth'

// Import route helpers
import { createRouteMeta, createGuestRoute, createAuthRoute, createPublicRoute } from '@/utils/routeHelpers'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [

    //RUTA DEL HOME
    {
      path: '/',
      name: 'Home',
      component: HomeView,
      meta: createRouteMeta('CacaoScan - Sistema de Análisis de Cacao', { requiresAuth: false })
    },

    //RUTA DEL REDIRECCIONAMIENTO DE LA DASHBOARD
    {
      path: '/dashboard',
      name: 'Dashboard',
      redirect: () => {
        // Redirección dinámica según rol del usuario
        const authStore = useAuthStore()
        if (!authStore.isAuthenticated) {
          return '/login'
        }

        switch (authStore.userRole) {
          case 'admin':
            return '/admin/dashboard'
          case 'analyst':
            return '/analisis'
          case 'farmer':
            return '/agricultor-dashboard'
          default:
            return '/'
        }
      },
      meta: createRouteMeta('Dashboard', { requiresAuth: true })
    },

    //LOGIN Y REGISTRO
    createGuestRoute('/login', 'Login', LoginView, 'Iniciar sesión'),
    createGuestRoute('/registro', 'Register', RegisterView, 'Registro'),
    createGuestRoute('/auth/forgot-password', 'ForgotPassword', () => import('../views/Auth/PasswordReset.vue'), 'Recuperar Contraseña'),
    createGuestRoute('/auth/reset-password', 'ResetPassword', () => import('../views/Auth/ResetPassword.vue'), 'Restablecer Contraseña'),

    // DOCUMENTOS LEGALES
    createPublicRoute('/legal/terms', 'LegalTerms', () => import('@/views/Pages/LegalTermsView.vue'), 'Términos y Condiciones'),
    createPublicRoute('/legal/privacy', 'PrivacyPolicy', () => import('@/views/Pages/PrivacyPolicyView.vue'), 'Política de Privacidad'),

    // RUTAS DEL ADMINISTRADOR
    {
      path: '/admin',
      meta: createRouteMeta('', { requiresAuth: true, requiresRole: 'admin' }),
      children: [
        {
          path: 'dashboard',
          name: 'AdminDashboard',
          component: AdminDashboard,
          meta: createRouteMeta('Panel de Administración', { requiresAuth: true, requiresRole: 'admin' })
        },
        {
          path: 'agricultores',
          name: 'AdminAgricultores',
          component: AdminAgricultores,
          meta: createRouteMeta('Gestión de Agricultores')
        },
        {
          path: 'configuracion',
          name: 'AdminConfiguracion',
          component: AdminConfiguracion,
          meta: createRouteMeta('Configuración')
        },
        {
          path: 'entrenamiento',
          name: 'AdminTraining',
          component: AdminTraining,
          meta: createRouteMeta('Panel de Reentrenamiento')
        },
        {
          path: 'usuarios',
          name: 'AdminUsuarios',
          component: AdminUsuarios,
          meta: createRouteMeta('Gestión de Usuarios')
        },
        {
          path: 'analisis',
          name: 'AdminAnalisis',
          component: AdminAnalisis,
          meta: createRouteMeta('Análisis de Lote')
        },
      ],
    },


    createAuthRoute('/detalle-analisis/:id?', 'DetalleAnalisis', DetalleAnalisisView, 'Detalle del Análisis de Cacao'),
    createAuthRoute('/analisis', 'Analisis', AdminAnalisis, 'Análisis de Datos'),
    createAuthRoute('/reportes', 'Reportes', Reportes, 'Reportes', { requiresRole: 'analyst' }),
    createAuthRoute('/reportes/management', 'ReportsManagement', ReportsManagement, 'Gestión de Reportes', { requiresRole: 'analyst' }),
    createAuthRoute('/agricultor-dashboard', 'AgricultorDashboard', AgricultorDashboard, 'Dashboard de Agricultor', { requiresRole: 'farmer' }),
    createAuthRoute('/agricultor/historial', 'Historial', Historial, 'Historial de Análisis', { requiresRole: 'farmer' }),
    createAuthRoute('/agricultor/reportes', 'AgricultorReportes', AgricultorReportes, 'Reportes de Análisis', { requiresRole: 'farmer' }),
    createAuthRoute('/agricultor/configuracion', 'AgricultorConfiguracion', AgricultorConfiguracion, 'Configuración', { requiresRole: 'farmer' }),
    createAuthRoute('/prediccion', 'Prediction', PredictionView, 'Análisis de Granos de Cacao', { requiresVerification: false }),
    createAuthRoute('/user/prediction', 'UserPrediction', UserPrediction, 'Predicción de Usuario', { requiresVerification: true }),
    createAuthRoute('/upload-images', 'UploadImages', () => import('../views/UploadImagesView.vue'), 'Subir Imágenes de Cacao'),
    createAuthRoute('/entrenamiento-incremental', 'SubirDatosEntrenamiento', SubirDatosEntrenamiento, 'Entrenamiento Incremental', { requiresVerification: true }),
    // Redirección de ruta antigua de agricultor a la nueva ruta unificada
    {
      path: '/agricultor/fincas',
      redirect: '/fincas'
    },
    // Rutas de gestión de fincas y lotes
    createAuthRoute('/fincas', 'Fincas', FincasView, 'Gestión de Fincas'),
    createAuthRoute('/fincas/:id', 'FincaDetail', () => import('../views/FincaDetailView.vue'), 'Detalle de Finca', { requiresRole: 'farmer', requiresVerification: true }),
    createAuthRoute('/fincas/:id/lotes', 'FincaLotes', () => import('../views/FincaLotesView.vue'), 'Lotes de Finca', { requiresRole: 'farmer', requiresVerification: true }),
    createAuthRoute('/fincas/:id/lotes/new', 'CreateLote', () => import('../views/CreateLoteView.vue'), 'Crear Lote', { requiresRole: 'farmer', requiresVerification: true }),
    createAuthRoute('/lotes', 'Lotes', LotesView, 'Gestión de Lotes', { requiresRole: 'farmer', requiresVerification: true }),
    createAuthRoute('/lotes/:id', 'LoteDetail', () => import('../views/LoteDetailView.vue'), 'Detalle de Lote', { requiresRole: 'farmer', requiresVerification: true }),
    createAuthRoute('/lotes/:id/analisis', 'LoteAnalisis', () => import('../views/LoteAnalisisView.vue'), 'Análisis de Lote', { requiresRole: 'farmer', requiresVerification: true }),
    // Rutas adicionales para autenticación
    createPublicRoute('/verificar-email', 'EmailVerification', () => import('../views/EmailVerification.vue'), 'Verificar Email'),
    createGuestRoute('/verify-email-otp', 'VerifyEmailOTP', () => import('../views/VerifyEmailView.vue'), 'Verificar Código OTP'),
    createPublicRoute('/verify-email/:token', 'VerifyEmail', () => import('../views/EmailVerification.vue'), 'Verificando Email'),
    createPublicRoute('/verify-prompt', 'VerifyPrompt', () => import('../views/VerifyPrompt.vue'), 'Verifica tu correo'),
    createGuestRoute('/reset-password', 'PasswordReset', () => import('../views/Auth/PasswordReset.vue'), 'Restablecer Contraseña'),
    createGuestRoute('/reset-password/confirm', 'PasswordResetConfirm', () => import('../views/PasswordResetConfirm.vue'), 'Confirmar Nueva Contraseña'),
    {
      path: '/acceso-denegado',
      name: 'AccessDenied',
      component: () => import('../views/AccessDenied.vue'),
      meta: createRouteMeta('Acceso Denegado')
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('../views/Pages/NotFound.vue'),
      meta: createRouteMeta('Página no encontrada')
    },
  ],
})

// Variable global para controlar estado de loading
let isNavigating = false
let navigationTimeout = null

import { normalizeRole, getRedirectPathByRole } from '@/utils/roleUtils'

// Helper functions for navigation guard
const handleGuestRoute = (to, authStore) => {
  if (!authStore.isAuthenticated) {
    return null
  }
  
  const redirectPath = getRedirectPathByRole(authStore.userRole)
  
  if (redirectPath === to.path) {
    return null
  }
  
  const routeExists = router.resolve(redirectPath)
  if (!routeExists.matched.length) {
    return { path: '/', replace: true }
  }
  
  return { path: redirectPath, replace: true }
}

const handleAuthRequired = async (to, authStore) => {
  if (!authStore.accessToken) {
    return {
      name: 'Login',
      replace: true,
      query: {
        redirect: to.fullPath,
        message: 'Debes iniciar sesión para acceder a esta página',
      },
    }
  }

  if (!authStore.user) {
    try {
      await authStore.getCurrentUser()
    } catch (error) {
      authStore.clearAll()
      return {
        name: 'Login',
        replace: true,
        query: {
          redirect: to.fullPath,
          message: 'Tu sesión ha expirado. Inicia sesión nuevamente.',
          expired: 'true',
        },
      }
    }
  }

  if (authStore.checkSessionTimeout()) {
    return false
  }

  // Redirigir usuarios Google-only si intentan acceder a rutas de contraseña
  const loginProvider = authStore.user?.login_provider || 'local'
  const passwordAllowed = authStore.user?.password_allowed !== false && loginProvider !== 'google'
  
  // Si el usuario es Google-only y está intentando acceder a configuración, permitir
  // pero las secciones de contraseña ya están ocultas en los componentes
  // No necesitamos redirección aquí ya que los componentes manejan la visibilidad

  const requiredRole = to.meta.requiresRole
  if (requiredRole) {
    const userRole = authStore.userRole?.toLowerCase().trim()
    const normalizedRequiredRole = typeof requiredRole === 'string' 
      ? requiredRole.toLowerCase().trim()
      : String(requiredRole).toLowerCase().trim()
    const normalizedUserRole = normalizeRole(userRole)

    // Define allowed roles for each required role
    // Admins can access farmer and analyst routes
    const rolePermissions = {
      'farmer': ['farmer', 'admin'],
      'analyst': ['analyst', 'admin'],
      'admin': ['admin']
    }

    const allowedRoles = rolePermissions[normalizedRequiredRole] || [normalizedRequiredRole]
    
    if (!allowedRoles.includes(normalizedUserRole)) {
      return {
        path: '/acceso-denegado',
        replace: true,
        query: {
          reason: 'insufficient_role',
          required: normalizedRequiredRole,
          current: normalizedUserRole,
        },
      }
    }
  }

  authStore.updateLastActivity()
  return null
}

// Guardián global para títulos, loading y configuraciones generales
// Usando formato moderno "return-based" de Vue Router 4
router.beforeEach(async (to, from) => {
  if (navigationTimeout) {
    clearTimeout(navigationTimeout)
    navigationTimeout = null
  }

  if (isNavigating && to.path === from.path) {
    return false
  }

  isNavigating = true

  try {
    document.title = to.meta?.title || 'CacaoScan'

    const authStore = useAuthStore()

    if (to.meta.requiresGuest || to.matched.some((record) => record.meta.requiresGuest)) {
      const guestResult = handleGuestRoute(to, authStore)
      if (guestResult !== null) {
        return guestResult
      }
    }

    if (to.meta.requiresAuth || to.matched.some((record) => record.meta.requiresAuth)) {
      const authResult = await handleAuthRequired(to, authStore)
      if (authResult !== null) {
        return authResult
      }
    }

    return true
  } catch (error) {
    // Handle navigation guard errors by logging and redirecting to error page
    // This catch is necessary to prevent navigation failures from breaking the router
    const errorMessage = error instanceof Error ? error.message : String(error)
    const errorStack = error instanceof Error ? error.stack : undefined
    
    
    // Redirect to access denied page with error context
    return { 
      path: '/acceso-denegado', 
      replace: true,
      query: {
        reason: 'navigation_error',
        error: errorMessage
      }
    }
  } finally {
    navigationTimeout = setTimeout(() => {
      isNavigating = false
      navigationTimeout = null
      globalThis.dispatchEvent(new CustomEvent('route-loading-end'))
    }, 100)
  }
})

// getRedirectPathByRole is now imported from utils/roleUtils

// Guardián posterior para limpiar estados
router.afterEach((to, from) => {
  // Scroll al top en cambios de ruta
  if (to.path !== from.path) {
    globalThis.scrollTo(0, 0)
  }

})

export default router
