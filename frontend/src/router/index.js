import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import NuevoAnalisis from '../views/NuevoAnalisis.vue'
import DetalleAnalisisView from '../views/DetalleAnalisisView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import Agricultores from '../views/Agricultores.vue'
import Analisis from '../views/Analisis.vue'
import Reportes from '../views/Reportes.vue'
import AgricultorDashboard from '../views/AgricultorDashboard.vue'
import PredictionView from '../views/PredictionView.vue'
import UserPrediction from '../views/UserPrediction.vue'
import AdminDataset from '../views/AdminDataset.vue'
import AdminTraining from '../views/AdminTraining.vue'

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
      path: '/login',
      name: 'Login',
      component: LoginView,
      beforeEnter: ROUTE_GUARDS.guest,
      meta: {
        title: 'Iniciar sesión | CacaoScan'
      }
    },
    {
      path: '/registro',
      name: 'Register',
      component: RegisterView,
      beforeEnter: ROUTE_GUARDS.guest,
      meta: {
        title: 'Registro | CacaoScan'
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
    {
      path: '/admin/dashboard',
      name: 'AdminDashboard',
      component: AdminDashboard,
      beforeEnter: ROUTE_GUARDS.admin,
      meta: {
        title: 'Panel de Administración | CacaoScan'
      }
    },
    {
      path: '/admin/agricultores',
      name: 'Agricultores',
      component: Agricultores,
      beforeEnter: ROUTE_GUARDS.admin,
      meta: {
        title: 'Gestión de Agricultores | CacaoScan'
      }
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
      path: '/admin/configuracion',
      name: 'Configuracion',
      component: () => import('../views/Configuracion.vue'),
      beforeEnter: ROUTE_GUARDS.admin,
      meta: {
        title: 'Configuración | CacaoScan'
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
      beforeEnter: ROUTE_GUARDS.canUpload,
      meta: {
        title: 'Análisis de Granos de Cacao | CacaoScan',
        requiresVerification: true
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
      path: '/admin/dataset',
      name: 'AdminDataset',
      component: AdminDataset,
      beforeEnter: ROUTE_GUARDS.admin,
      meta: {
        title: 'Gestión de Dataset | CacaoScan'
      }
    },
    {
      path: '/admin/training',
      name: 'AdminTraining',
      component: AdminTraining,
      beforeEnter: ROUTE_GUARDS.admin,
      meta: {
        title: 'Panel de Reentrenamiento | CacaoScan'
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
    
    // Verificar estado de autenticación si se requiere
    if (to.meta.requiresAuth || to.matched.some(record => record.meta.requiresAuth)) {
      const { useAuthStore } = await import('@/stores/auth')
      const authStore = useAuthStore()
      
      // Si no hay token pero está intentando acceder a ruta protegida
      if (!authStore.isAuthenticated) {
        console.warn('🚫 Intento de acceso a ruta protegida sin autenticación')
        next({
          name: 'Login',
          query: { 
            redirect: to.fullPath,
            message: 'Debes iniciar sesión para acceder a esta página'
          }
        })
        return
      }
      
      // Verificar que el usuario esté completamente cargado
      if (!authStore.user) {
        try {
          await authStore.getCurrentUser()
        } catch (error) {
          console.error('Error cargando datos de usuario:', error)
          authStore.clearAll()
          next({
            name: 'Login',
            query: { 
              redirect: to.fullPath,
              message: 'Tu sesión ha expirado. Inicia sesión nuevamente.'
            }
          })
          return
        }
      }
    }
    
    next()
  } catch (error) {
    console.error('Error en navigation guard:', error)
    next('/acceso-denegado')
  } finally {
    // Pequeño delay para mejor UX
    setTimeout(() => {
      isNavigating = false
      // Emit loading end event
      window.dispatchEvent(new CustomEvent('route-loading-end'))
    }, 100)
  }
})

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
