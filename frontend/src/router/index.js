import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import NuevoAnalisis from '../views/NuevoAnalisis.vue'
import DetalleAnalisisView from '../views/DetalleAnalisisView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import ChartDashboard from '../views/ChartDashboard.vue'
import Agricultores from '../views/Agricultores.vue'
import Analisis from '../views/Analisis.vue'
import Reportes from '../views/Reportes.vue'
import ReportsManagement from '../views/ReportsManagement.vue'
import AgricultorDashboard from '../views/AgricultorDashboard.vue'
import PredictionView from '../views/PredictionView.vue'
import UserPrediction from '../views/UserPrediction.vue'
import AdminDataset from '../views/AdminDataset.vue'
import AdminTraining from '../views/AdminTraining.vue'
import SubirDatosEntrenamiento from '../views/SubirDatosEntrenamiento.vue'
import FincasView from '../views/FincasView.vue'
import LotesView from '../views/LotesView.vue'

// Importar guards
import { ROUTE_GUARDS } from './guards'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: HomeView,
      meta: {
        title: 'CacaoScan - Sistema de Análisis de Cacao',
        requiresAuth: false
      }
    },
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
        requiresAuth: true
      }
    },
    {
      path: '/login',
      name: 'Login',
      component: LoginView,
      beforeEnter: ROUTE_GUARDS.guest,
      meta: {
        title: 'Iniciar sesión | CacaoScan',
        requiresGuest: true
      }
    },
    {
      path: '/registro',
      name: 'Register',
      component: RegisterView,
      beforeEnter: ROUTE_GUARDS.guest,
      meta: {
        title: 'Registro | CacaoScan',
        requiresGuest: true
      }
    },
    {
      path: '/nuevo-analisis',
      name: 'NuevoAnalisis',
      component: NuevoAnalisis,
      beforeEnter: ROUTE_GUARDS.farmerVerified,
      meta: {
        title: 'Nuevo Análisis de Lote | CacaoScan',
        requiresVerification: true
      }
    },
    {
      path: '/detalle-analisis/:id?',
      name: 'DetalleAnalisis',
      component: DetalleAnalisisView,
      beforeEnter: ROUTE_GUARDS.auth,
      meta: {
        title: 'Detalle del Análisis de Cacao | CacaoScan'
      }
    },
    // Rutas de administración (optimizadas con subrutas)
    {
      path: '/admin',
      children: [
        {
          path: 'dashboard',
          name: 'AdminDashboard',
          component: AdminDashboard,
          beforeEnter: ROUTE_GUARDS.admin,
          meta: {
            title: 'Panel de Administración | CacaoScan'
          }
        },
        {
          path: 'charts',
          name: 'ChartDashboard',
          component: ChartDashboard,
          beforeEnter: ROUTE_GUARDS.admin,
          meta: {
            title: 'Dashboard de Gráficas | CacaoScan'
          }
        },
        {
          path: 'agricultores',
          name: 'Agricultores',
          component: Agricultores,
          beforeEnter: ROUTE_GUARDS.admin,
          meta: {
            title: 'Gestión de Agricultores | CacaoScan'
          }
        },
        {
          path: 'configuracion',
          name: 'Configuracion',
          component: () => import('../views/Configuracion.vue'),
          beforeEnter: ROUTE_GUARDS.admin,
          meta: {
            title: 'Configuración | CacaoScan'
          }
        },
        {
          path: 'dataset',
          name: 'AdminDataset',
          component: AdminDataset,
          beforeEnter: ROUTE_GUARDS.admin,
          meta: {
            title: 'Gestión de Dataset | CacaoScan'
          }
        },
        {
          path: 'training',
          name: 'AdminTraining',
          component: AdminTraining,
          beforeEnter: ROUTE_GUARDS.admin,
          meta: {
            title: 'Panel de Reentrenamiento | CacaoScan'
          }
        }
      ]
    },
    {
      path: '/analisis',
      name: 'Analisis',
      component: Analisis,
      beforeEnter: ROUTE_GUARDS.analyst,
      meta: {
        title: 'Análisis de Datos | CacaoScan'
      }
    },
    {
      path: '/reportes',
      name: 'Reportes',
      component: Reportes,
      beforeEnter: ROUTE_GUARDS.analyst,
      meta: {
        title: 'Reportes | CacaoScan'
      }
    },
    {
      path: '/reportes/management',
      name: 'ReportsManagement',
      component: ReportsManagement,
      beforeEnter: ROUTE_GUARDS.analyst,
      meta: {
        title: 'Gestión de Reportes | CacaoScan'
      }
    },
    {
      path: '/agricultor-dashboard',
      name: 'AgricultorDashboard',
      component: AgricultorDashboard,
      beforeEnter: ROUTE_GUARDS.farmer,
      meta: {
        title: 'Dashboard de Agricultor | CacaoScan'
      }
    },
    {
      path: '/prediccion',
      name: 'Prediction',
      component: PredictionView,
      beforeEnter: ROUTE_GUARDS.auth,
      meta: {
        title: 'Análisis de Granos de Cacao | CacaoScan',
        requiresVerification: false
      }
    },
    {
      path: '/user/prediction',
      name: 'UserPrediction',
      component: UserPrediction,
      beforeEnter: ROUTE_GUARDS.canUpload,
      meta: {
        title: 'Predicción de Usuario | CacaoScan',
        requiresVerification: true
      }
    },
    {
      path: '/entrenamiento-incremental',
      name: 'SubirDatosEntrenamiento',
      component: SubirDatosEntrenamiento,
      beforeEnter: ROUTE_GUARDS.canUpload,
      meta: {
        title: 'Entrenamiento Incremental | CacaoScan',
        requiresVerification: true
      }
    },
    // Rutas de gestión de fincas y lotes
    {
      path: '/fincas',
      name: 'Fincas',
      component: FincasView,
      beforeEnter: ROUTE_GUARDS.farmer,
      meta: {
        title: 'Gestión de Fincas | CacaoScan',
        requiresVerification: true
      }
    },
    {
      path: '/fincas/:id',
      name: 'FincaDetail',
      component: () => import('../views/FincaDetailView.vue'),
      beforeEnter: ROUTE_GUARDS.farmer,
      meta: {
        title: 'Detalle de Finca | CacaoScan',
        requiresVerification: true
      }
    },
    {
      path: '/fincas/:id/lotes',
      name: 'FincaLotes',
      component: () => import('../views/FincaLotesView.vue'),
      beforeEnter: ROUTE_GUARDS.farmer,
      meta: {
        title: 'Lotes de Finca | CacaoScan',
        requiresVerification: true
      }
    },
    {
      path: '/lotes',
      name: 'Lotes',
      component: LotesView,
      beforeEnter: ROUTE_GUARDS.farmer,
      meta: {
        title: 'Gestión de Lotes | CacaoScan',
        requiresVerification: true
      }
    },
    {
      path: '/lotes/:id',
      name: 'LoteDetail',
      component: () => import('../views/LoteDetailView.vue'),
      beforeEnter: ROUTE_GUARDS.farmer,
      meta: {
        title: 'Detalle de Lote | CacaoScan',
        requiresVerification: true
      }
    },
    {
      path: '/lotes/:id/analisis',
      name: 'LoteAnalisis',
      component: () => import('../views/LoteAnalisisView.vue'),
      beforeEnter: ROUTE_GUARDS.farmer,
      meta: {
        title: 'Análisis de Lote | CacaoScan',
        requiresVerification: true
      }
    },
    // Rutas adicionales para autenticación
    {
      path: '/verificar-email',
      name: 'EmailVerification',
      component: () => import('../views/EmailVerification.vue'),
      beforeEnter: ROUTE_GUARDS.auth,
      meta: {
        title: 'Verificar Email | CacaoScan'
      }
    },
    {
      path: '/reset-password',
      name: 'PasswordReset',
      component: () => import('../views/PasswordReset.vue'),
      beforeEnter: ROUTE_GUARDS.guest,
      meta: {
        title: 'Restablecer Contraseña | CacaoScan'
      }
    },
    {
      path: '/reset-password/confirm',
      name: 'PasswordResetConfirm',
      component: () => import('../views/PasswordResetConfirm.vue'),
      beforeEnter: ROUTE_GUARDS.guest,
      meta: {
        title: 'Confirmar Nueva Contraseña | CacaoScan'
      }
    },
    {
      path: '/perfil',
      name: 'Profile',
      component: () => import('../views/Profile.vue'),
      beforeEnter: ROUTE_GUARDS.auth,
      meta: {
        title: 'Mi Perfil | CacaoScan'
      }
    },
    {
      path: '/acceso-denegado',
      name: 'AccessDenied',
      component: () => import('../views/AccessDenied.vue'),
      meta: {
        title: 'Acceso Denegado | CacaoScan'
      }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('../views/NotFound.vue'),
      meta: {
        title: 'Página no encontrada | CacaoScan'
      }
    }
  ],
})

// Variable global para controlar estado de loading
let isNavigating = false

// Guardián global para títulos, loading y configuraciones generales  
router.beforeEach(async (to, from, next) => {
  // Prevenir navegación múltiple simultánea
  if (isNavigating) {
    return
  }
  
  isNavigating = true
  
  try {
    // Actualizar el título de la página
    document.title = to.meta?.title || 'CacaoScan'
    
    // Log de navegación en desarrollo
    if (import.meta.env.DEV) {
      console.log(`🧭 Navigating: ${from.name || from.path} → ${to.name || to.path}`)
    }
    
    // Mostrar loading para navegación entre diferentes rutas
    if (to.path !== from.path && from.name) {
      // Emit loading event
      window.dispatchEvent(new CustomEvent('route-loading-start', {
        detail: { to, from }
      }))
    }
    
    // Importar store de autenticación dinámicamente
    const { useAuthStore } = await import('@/stores/auth')
    const authStore = useAuthStore()
    
    // Verificar estado de autenticación si se requiere
    if (to.meta.requiresAuth || to.matched.some(record => record.meta.requiresAuth)) {
      
      // Si no hay token, redirigir al login
      if (!authStore.accessToken) {
        console.warn('🚫 Intento de acceso a ruta protegida sin token')
        next({
          name: 'Login',
          replace: true,
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
          console.error('❌ Token inválido o expirado:', error)
          // Limpiar todo y redirigir
          authStore.clearAll()
          next({
            name: 'Login',
            replace: true,
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
    }
    
    // Verificar rutas públicas que requieren que el usuario NO esté autenticado
    if (to.meta.requiresGuest || to.matched.some(record => record.meta.requiresGuest)) {
      if (authStore.isAuthenticated) {
        console.log('👤 Usuario ya autenticado, redirigiendo desde ruta pública...')
        
        // Redirigir según rol usando router.replace para evitar historial
        const redirectPath = getRedirectPathByRole(authStore.userRole)
        next({ path: redirectPath, replace: true })
        return
      }
    }
    
    next()
  } catch (error) {
    console.error('Error en navigation guard:', error)
    next({ path: '/acceso-denegado', replace: true })
  } finally {
    // Pequeño delay para mejor UX
    setTimeout(() => {
      isNavigating = false
      // Emit loading end event
      window.dispatchEvent(new CustomEvent('route-loading-end'))
    }, 100)
  }
})

// Función auxiliar para obtener ruta de redirección por rol
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

// Guardián posterior para limpiar estados
router.afterEach((to, from) => {
  // Scroll al top en cambios de ruta
  if (to.path !== from.path) {
    window.scrollTo(0, 0)
  }
  
  // Log de navegación completada en desarrollo
  if (import.meta.env.DEV) {
    console.log(`✅ Navigation completed: ${to.name || to.path}`)
  }
})

export default router
