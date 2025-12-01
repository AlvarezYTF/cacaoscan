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
import { createRouteMeta, createPublicRoute, createAuthRoute, createGuestRoute } from '@/utils/routeHelpers'

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
    {
      path: '/login',
      name: 'Login',
      component: LoginView,
      meta: createRouteMeta('Iniciar sesión', { requiresGuest: true })
    },
    {
      path: '/registro',
      name: 'Register',
      component: RegisterView,
      meta: createRouteMeta('Registro', { requiresGuest: true })
    },
    {
      path: '/auth/forgot-password',
      name: 'ForgotPassword',
      component: () => import('../views/Auth/PasswordReset.vue'),
      meta: createRouteMeta('Recuperar Contraseña', { requiresGuest: true })
    },
    {
      path: '/auth/reset-password',
      name: 'ResetPassword',
      component: () => import('../views/Auth/ResetPassword.vue'),
      meta: createRouteMeta('Restablecer Contraseña', { requiresGuest: true })
    },

    // DOCUMENTOS LEGALES
    {
      path: '/legal/terms',
      name: 'LegalTerms',
      component: () => import('@/views/Pages/LegalTermsView.vue'),
      meta: createRouteMeta('Términos y Condiciones', { requiresAuth: false })
    },
    {
      path: '/legal/privacy',
      name: 'PrivacyPolicy',
      component: () => import('@/views/Pages/PrivacyPolicyView.vue'),
      meta: createRouteMeta('Política de Privacidad', { requiresAuth: false })
    },

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


    {
      path: '/detalle-analisis/:id?',
      name: 'DetalleAnalisis',
      component: DetalleAnalisisView,
      meta: createRouteMeta('Detalle del Análisis de Cacao', { requiresAuth: true })
    },
    {
      path: '/analisis',
      name: 'Analisis',
      component: AdminAnalisis,
      meta: createRouteMeta('Análisis de Datos', { requiresAuth: true })
    },
    {
      path: '/reportes',
      name: 'Reportes',
      component: Reportes,
      meta: createRouteMeta('Reportes', { requiresAuth: true, requiresRole: 'analyst' })
    },
    {
      path: '/reportes/management',
      name: 'ReportsManagement',
      component: ReportsManagement,
      meta: createRouteMeta('Gestión de Reportes', { requiresAuth: true, requiresRole: 'analyst' })
    },
    {
      path: '/agricultor-dashboard',
      name: 'AgricultorDashboard',
      component: AgricultorDashboard,
      meta: createRouteMeta('Dashboard de Agricultor', { requiresAuth: true, requiresRole: 'farmer' })
    },
    {
      path: '/agricultor/historial',
      name: 'Historial',
      component: Historial,
      meta: createRouteMeta('Historial de Análisis', { requiresAuth: true, requiresRole: 'farmer' })
    },
    {
      path: '/agricultor/reportes',
      name: 'AgricultorReportes',
      component: AgricultorReportes,
      meta: createRouteMeta('Reportes de Análisis', { requiresAuth: true, requiresRole: 'farmer' })
    },
    {
      path: '/agricultor/configuracion',
      name: 'AgricultorConfiguracion',
      component: AgricultorConfiguracion,
      meta: createRouteMeta('Configuración', { requiresAuth: true, requiresRole: 'farmer' })
    },
    {
      path: '/prediccion',
      name: 'Prediction',
      component: PredictionView,
      meta: createRouteMeta('Análisis de Granos de Cacao', { requiresAuth: true, requiresVerification: false })
    },
    {
      path: '/user/prediction',
      name: 'UserPrediction',
      component: UserPrediction,
      meta: createRouteMeta('Predicción de Usuario', { requiresAuth: true, requiresVerification: true })
    },
    {
      path: '/upload-images',
      name: 'UploadImages',
      component: () => import('../views/UploadImagesView.vue'),
      meta: createRouteMeta('Subir Imágenes de Cacao', { requiresAuth: true })
    },
    {
      path: '/entrenamiento-incremental',
      name: 'SubirDatosEntrenamiento',
      component: SubirDatosEntrenamiento,
      meta: createRouteMeta('Entrenamiento Incremental', { requiresAuth: true, requiresVerification: true })
    },
    // Redirección de ruta antigua de agricultor a la nueva ruta unificada
    {
      path: '/agricultor/fincas',
      redirect: '/fincas'
    },
    // Rutas de gestión de fincas y lotes
    {
      path: '/fincas',
      name: 'Fincas',
      component: FincasView,
      meta: createRouteMeta('Gestión de Fincas', { requiresAuth: true })
    },
    {
      path: '/fincas/:id',
      name: 'FincaDetail',
      component: () => import('../views/FincaDetailView.vue'),
      meta: createRouteMeta('Detalle de Finca', { requiresAuth: true, requiresRole: 'farmer', requiresVerification: true })
    },
    {
      path: '/fincas/:id/lotes',
      name: 'FincaLotes',
      component: () => import('../views/FincaLotesView.vue'),
      meta: createRouteMeta('Lotes de Finca', { requiresAuth: true, requiresRole: 'farmer', requiresVerification: true })
    },
    {
      path: '/lotes',
      name: 'Lotes',
      component: LotesView,
      meta: createRouteMeta('Gestión de Lotes', { requiresAuth: true, requiresRole: 'farmer', requiresVerification: true })
    },
    {
      path: '/lotes/:id',
      name: 'LoteDetail',
      component: () => import('../views/LoteDetailView.vue'),
      meta: createRouteMeta('Detalle de Lote', { requiresAuth: true, requiresRole: 'farmer', requiresVerification: true })
    },
    {
      path: '/lotes/:id/analisis',
      name: 'LoteAnalisis',
      component: () => import('../views/LoteAnalisisView.vue'),
      meta: createRouteMeta('Análisis de Lote', { requiresAuth: true, requiresRole: 'farmer', requiresVerification: true })
    },
    // Rutas adicionales para autenticación
    {
      path: '/verificar-email',
      name: 'EmailVerification',
      component: () => import('../views/EmailVerification.vue'),
      meta: createRouteMeta('Verificar Email', { requiresAuth: false })
    },
    {
      path: '/verify-email-otp',
      name: 'VerifyEmailOTP',
      component: () => import('../views/VerifyEmailView.vue'),
      meta: createRouteMeta('Verificar Código OTP', { requiresGuest: true })
    },
    {
      path: '/verify-email/:token',
      name: 'VerifyEmail',
      component: () => import('../views/EmailVerification.vue'),
      meta: createRouteMeta('Verificando Email', { requiresAuth: false })
    },
    {
      path: '/verify-prompt',
      name: 'VerifyPrompt',
      component: () => import('../views/VerifyPrompt.vue'),
      meta: createRouteMeta('Verifica tu correo', { requiresAuth: false })
    },
    {
      path: '/reset-password',
      name: 'PasswordReset',
      component: () => import('../views/Auth/PasswordReset.vue'),
      meta: createRouteMeta('Restablecer Contraseña', { requiresGuest: true })
    },
    {
      path: '/reset-password/confirm',
      name: 'PasswordResetConfirm',
      component: () => import('../views/PasswordResetConfirm.vue'),
      meta: createRouteMeta('Confirmar Nueva Contraseña', { requiresGuest: true })
    },
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
      console.error('Error obteniendo usuario en guard:', error)
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

  const requiredRole = to.meta.requiresRole
  if (requiredRole) {
    const userRole = authStore.userRole?.toLowerCase().trim()
    const normalizedRequiredRole = typeof requiredRole === 'string' 
      ? requiredRole.toLowerCase().trim()
      : String(requiredRole).toLowerCase().trim()
    const normalizedUserRole = normalizeRole(userRole)

    if (normalizedUserRole !== normalizedRequiredRole) {
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
    
    console.error('Navigation guard error:', {
      message: errorMessage,
      stack: errorStack,
      route: to.path,
      error
    })
    
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
