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

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [

    //RUTA DEL HOME
    {
      path: '/',
      name: 'Home',
      component: HomeView,
      meta: {
        title: 'CacaoScan - Sistema de Análisis de Cacao',
        requiresAuth: false
      },
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
      meta: {
        title: 'Dashboard | CacaoScan',
        requiresAuth: true,
      },
    },

    //LOGIN Y REGISTRO
    {
      path: '/login',
      name: 'Login',
      component: LoginView,
      // beforeEnter removido - el guard global maneja requiresGuest
      meta: {
        title: 'Iniciar sesión | CacaoScan',
        requiresGuest: true,
      },
    },
    {
      path: '/registro',
      name: 'Register',
      component: RegisterView,
      // beforeEnter removido - el guard global maneja requiresGuest
      meta: {
        title: 'Registro | CacaoScan',
        requiresGuest: true,
      },
    },
    {
      path: '/auth/forgot-password',
      name: 'ForgotPassword',
      component: () => import('../views/Auth/PasswordReset.vue'),
      meta: {
        title: 'Recuperar Contraseña | CacaoScan',
        requiresGuest: true,
      },
    },
    {
      path: '/auth/reset-password',
      name: 'ResetPassword',
      component: () => import('../views/Auth/ResetPassword.vue'),
      meta: {
        title: 'Restablecer Contraseña | CacaoScan',
        requiresGuest: true,
      },
    },

    // DOCUMENTOS LEGALES
    {
      path: '/legal/terms',
      name: 'LegalTerms',
      component: () => import('@/views/Pages/LegalTermsView.vue'),
      meta: {
        title: 'Términos y Condiciones | CacaoScan',
        requiresAuth: false,
      },
    },
    {
      path: '/legal/privacy',
      name: 'PrivacyPolicy',
      component: () => import('@/views/Pages/PrivacyPolicyView.vue'),
      meta: {
        title: 'Política de Privacidad | CacaoScan',
        requiresAuth: false,
      },
    },

    // RUTAS DEL ADMINISTRADOR
    {
      path: '/admin',
      meta: {
        requiresAuth: true,
        requiresRole: 'admin',
      },
      children: [
        {
          path: 'dashboard',
          name: 'AdminDashboard',
          component: AdminDashboard,
          meta: {
            title: 'Panel de Administración | CacaoScan',
            requiresAuth: true,
            requiresRole: 'admin',
          },
        },
        {
          path: 'agricultores',
          name: 'AdminAgricultores',
          component: AdminAgricultores,
          meta: {
            title: 'Gestión de Agricultores | CacaoScan',
          },
        },
        {
          path: 'configuracion',
          name: 'AdminConfiguracion',
          component: AdminConfiguracion,
          meta: {
            title: 'Configuración | CacaoScan',
          },
        },
        {
          path: 'entrenamiento',
          name: 'AdminTraining',
          component: AdminTraining,
          meta: {
            title: 'Panel de Reentrenamiento | CacaoScan',
          },
        },
        {
          path: 'usuarios',
          name: 'AdminUsuarios',
          component: AdminUsuarios,
          meta: {
            title: 'Gestión de Usuarios | CacaoScan',
          },
        },
        {
          path: 'analisis',
          name: 'AdminAnalisis',
          component: AdminAnalisis,
          meta: {
            title: 'Análisis de Lote | CacaoScan',
          },
        },
      ],
    },


    {
      path: '/detalle-analisis/:id?',
      name: 'DetalleAnalisis',
      component: DetalleAnalisisView,
      meta: {
        title: 'Detalle del Análisis de Cacao | CacaoScan',
        requiresAuth: true,
      },
    },
    {
      path: '/analisis',
      name: 'Analisis',
      component: AdminAnalisis,
      meta: {
        title: 'Análisis de Datos | CacaoScan',
        requiresAuth: true,
      },
    },
    {
      path: '/reportes',
      name: 'Reportes',
      component: Reportes,
      meta: {
        title: 'Reportes | CacaoScan',
        requiresAuth: true,
        requiresRole: 'analyst',
      },
    },
    {
      path: '/reportes/management',
      name: 'ReportsManagement',
      component: ReportsManagement,
      meta: {
        title: 'Gestión de Reportes | CacaoScan',
        requiresAuth: true,
        requiresRole: 'analyst',
      },
    },
    {
      path: '/agricultor-dashboard',
      name: 'AgricultorDashboard',
      component: AgricultorDashboard,
      meta: {
        title: 'Dashboard de Agricultor | CacaoScan',
        requiresAuth: true,
        requiresRole: 'farmer',
      },
    },
    {
      path: '/agricultor/historial',
      name: 'Historial',
      component: Historial,
      meta: {
        title: 'Historial de Análisis | CacaoScan',
        requiresAuth: true,
        requiresRole: 'farmer',
      },
    },
    {
      path: '/agricultor/reportes',
      name: 'AgricultorReportes',
      component: AgricultorReportes,
      meta: {
        title: 'Reportes de Análisis | CacaoScan',
        requiresAuth: true,
        requiresRole: 'farmer',
      },
    },
    {
      path: '/agricultor/configuracion',
      name: 'AgricultorConfiguracion',
      component: AgricultorConfiguracion,
      meta: {
        title: 'Configuración | CacaoScan',
        requiresAuth: true,
        requiresRole: 'farmer',
      },
    },
    {
      path: '/prediccion',
      name: 'Prediction',
      component: PredictionView,
      meta: {
        title: 'Análisis de Granos de Cacao | CacaoScan',
        requiresAuth: true,
        requiresVerification: false,
      },
    },
    {
      path: '/user/prediction',
      name: 'UserPrediction',
      component: UserPrediction,
      meta: {
        title: 'Predicción de Usuario | CacaoScan',
        requiresAuth: true,
        requiresVerification: true,
      },
    },
    {
      path: '/upload-images',
      name: 'UploadImages',
      component: () => import('../views/UploadImagesView.vue'),
      meta: {
        title: 'Subir Imágenes de Cacao | CacaoScan',
        requiresAuth: true,
      },
    },
    {
      path: '/entrenamiento-incremental',
      name: 'SubirDatosEntrenamiento',
      component: SubirDatosEntrenamiento,
      meta: {
        title: 'Entrenamiento Incremental | CacaoScan',
        requiresAuth: true,
        requiresVerification: true,
      },
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
      meta: {
        title: 'Gestión de Fincas | CacaoScan',
        requiresAuth: true,
        // Both admin and farmer can access fincas
      },
    },
    {
      path: '/fincas/:id',
      name: 'FincaDetail',
      component: () => import('../views/FincaDetailView.vue'),
      meta: {
        title: 'Detalle de Finca | CacaoScan',
        requiresAuth: true,
        requiresRole: 'farmer',
        requiresVerification: true,
      },
    },
    {
      path: '/fincas/:id/lotes',
      name: 'FincaLotes',
      component: () => import('../views/FincaLotesView.vue'),
      meta: {
        title: 'Lotes de Finca | CacaoScan',
        requiresAuth: true,
        requiresRole: 'farmer',
        requiresVerification: true,
      },
    },
    {
      path: '/lotes',
      name: 'Lotes',
      component: LotesView,
      meta: {
        title: 'Gestión de Lotes | CacaoScan',
        requiresAuth: true,
        requiresRole: 'farmer',
        requiresVerification: true,
      },
    },
    {
      path: '/lotes/:id',
      name: 'LoteDetail',
      component: () => import('../views/LoteDetailView.vue'),
      meta: {
        title: 'Detalle de Lote | CacaoScan',
        requiresAuth: true,
        requiresRole: 'farmer',
        requiresVerification: true,
      },
    },
    {
      path: '/lotes/:id/analisis',
      name: 'LoteAnalisis',
      component: () => import('../views/LoteAnalisisView.vue'),
      meta: {
        title: 'Análisis de Lote | CacaoScan',
        requiresAuth: true,
        requiresRole: 'farmer',
        requiresVerification: true,
      },
    },
    // Rutas adicionales para autenticación
    {
      path: '/verificar-email',
      name: 'EmailVerification',
      component: () => import('../views/EmailVerification.vue'),
      meta: {
        title: 'Verificar Email | CacaoScan',
        requiresAuth: false, // Permitir acceso sin autenticación para verificar
      },
    },
    {
      path: '/verify-email-otp',
      name: 'VerifyEmailOTP',
      component: () => import('../views/VerifyEmailView.vue'),
      meta: {
        title: 'Verificar Código OTP | CacaoScan',
        requiresGuest: true,
      },
    },
    {
      path: '/verify-email/:token',
      name: 'VerifyEmail',
      component: () => import('../views/EmailVerification.vue'),
      meta: {
        title: 'Verificando Email | CacaoScan',
        requiresAuth: false,
      },
    },
    {
      path: '/verify-prompt',
      name: 'VerifyPrompt',
      component: () => import('../views/VerifyPrompt.vue'),
      meta: {
        title: 'Verifica tu correo | CacaoScan',
        requiresAuth: false,
      },
    },
    {
      path: '/reset-password',
      name: 'PasswordReset',
      component: () => import('../views/Auth/PasswordReset.vue'),
      meta: {
        title: 'Restablecer Contraseña | CacaoScan',
        requiresGuest: true,
      },
    },
    {
      path: '/reset-password/confirm',
      name: 'PasswordResetConfirm',
      component: () => import('../views/PasswordResetConfirm.vue'),
      meta: {
        title: 'Confirmar Nueva Contraseña | CacaoScan',
        requiresGuest: true,
      },
    },
    {
      path: '/acceso-denegado',
      name: 'AccessDenied',
      component: () => import('../views/AccessDenied.vue'),
      meta: {
        title: 'Acceso Denegado | CacaoScan',
      },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('../views/Pages/NotFound.vue'),
      meta: {
        title: 'Página no encontrada | CacaoScan',
      },
    },
  ],
})

// Variable global para controlar estado de loading
let isNavigating = false
let navigationTimeout = null

// Helper function to normalize role (extracted common logic)
const normalizeRole = (role) => {
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

// Función auxiliar para obtener ruta de redirección por rol
const getRedirectPathByRole = (role) => {
  const normalizedRole = normalizeRole(role)

  switch (normalizedRole) {
    case 'admin':
      return '/admin/dashboard'
    case 'analyst':
      return '/analisis'
    case 'farmer':
      return '/agricultor-dashboard'
    default:
      // Por defecto, redirigir a admin dashboard en lugar de home para evitar bucles
      return '/admin/dashboard'
  }
}

// Guardián posterior para limpiar estados
router.afterEach((to, from) => {
  // Scroll al top en cambios de ruta
  if (to.path !== from.path) {
    globalThis.scrollTo(0, 0)
  }

})

export default router
