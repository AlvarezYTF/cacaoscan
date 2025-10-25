import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import NuevoAnalisis from '../views/NuevoAnalisis.vue'
import DetalleAnalisisView from '../views/DetalleAnalisisView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AdminDashboard from '../views/Dasnborads/AdminDashboard.vue'
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
import UserManagement from '../views/Dasnborads/UserManagement.vue'

// Importar auth store
import { useAuthStore } from '@/stores/auth'

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
        // requiresGuest removido - Home es accesible para todos
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
      // beforeEnter removido - el guard global maneja requiresGuest
      meta: {
        title: 'Iniciar sesión | CacaoScan',
        requiresGuest: true
      }
    },
    {
      path: '/registro',
      name: 'Register',
      component: RegisterView,
      // beforeEnter removido - el guard global maneja requiresGuest
      meta: {
        title: 'Registro | CacaoScan',
        requiresGuest: true
      }
    },
    {
      path: '/nuevo-analisis',
      name: 'NuevoAnalisis',
      component: NuevoAnalisis,
      meta: {
        title: 'Nuevo Análisis de Lote | CacaoScan',
        requiresAuth: true,
        requiresRole: 'farmer',
        requiresVerification: true
      }
    },
    {
      path: '/detalle-analisis/:id?',
      name: 'DetalleAnalisis',
      component: DetalleAnalisisView,
      meta: {
        title: 'Detalle del Análisis de Cacao | CacaoScan',
        requiresAuth: true
      }
    },
    // Rutas de administración (optimizadas con subrutas)
    {
      path: '/admin',
      meta: {
        requiresAuth: true,
        requiresRole: 'admin'
      },
      children: [
        {
          path: 'dashboard',
          name: 'AdminDashboard',
          component: AdminDashboard,
          // beforeEnter removido - el guard global maneja la autenticación y rol
          meta: {
            title: 'Panel de Administración | CacaoScan',
            requiresAuth: true,
            requiresRole: 'admin'
          }
        },
        {
          path: 'charts',
          name: 'ChartDashboard',
          component: ChartDashboard,
          meta: {
            title: 'Dashboard de Gráficas | CacaoScan'
          }
        },
        {
          path: 'agricultores',
          name: 'Agricultores',
          component: Agricultores,
          meta: {
            title: 'Gestión de Agricultores | CacaoScan'
          }
        },
        {
          path: 'configuracion',
          name: 'Configuracion',
          component: () => import('../views/Configuracion.vue'),
          meta: {
            title: 'Configuración | CacaoScan'
          }
        },
        {
          path: 'dataset',
          name: 'AdminDataset',
          component: AdminDataset,
          meta: {
            title: 'Gestión de Dataset | CacaoScan'
          }
        },
        {
          path: 'training',
          name: 'AdminTraining',
          component: AdminTraining,
          meta: {
            title: 'Panel de Reentrenamiento | CacaoScan'
          }
        },
        {
          path: 'users',
          name: 'AdminUsers',
          component: UserManagement,
          meta: {
            title: 'Gestión de Usuarios | CacaoScan'
          }
        }
      ]
    },
    {
      path: '/analisis',
      name: 'Analisis',
      component: Analisis,
      meta: {
        title: 'Análisis de Datos | CacaoScan',
        requiresAuth: true,
        requiresRole: 'analyst'
      }
    },
    {
      path: '/reportes',
      name: 'Reportes',
      component: Reportes,
      meta: {
        title: 'Reportes | CacaoScan',
        requiresAuth: true,
        requiresRole: 'analyst'
      }
    },
    {
      path: '/reportes/management',
      name: 'ReportsManagement',
      component: ReportsManagement,
      meta: {
        title: 'Gestión de Reportes | CacaoScan',
        requiresAuth: true,
        requiresRole: 'analyst'
      }
    },
    {
      path: '/agricultor-dashboard',
      name: 'AgricultorDashboard',
      component: AgricultorDashboard,
      meta: {
        title: 'Dashboard de Agricultor | CacaoScan',
        requiresAuth: true,
        requiresRole: 'farmer'
      }
    },
    {
      path: '/prediccion',
      name: 'Prediction',
      component: PredictionView,
      meta: {
        title: 'Análisis de Granos de Cacao | CacaoScan',
        requiresAuth: true,
        requiresVerification: false
      }
    },
    {
      path: '/user/prediction',
      name: 'UserPrediction',
      component: UserPrediction,
      meta: {
        title: 'Predicción de Usuario | CacaoScan',
        requiresAuth: true,
        requiresVerification: true
      }
    },
    {
      path: '/entrenamiento-incremental',
      name: 'SubirDatosEntrenamiento',
      component: SubirDatosEntrenamiento,
      meta: {
        title: 'Entrenamiento Incremental | CacaoScan',
        requiresAuth: true,
        requiresVerification: true
      }
    },
    // Rutas de gestión de fincas y lotes
    {
      path: '/fincas',
      name: 'Fincas',
      component: FincasView,
      meta: {
        title: 'Gestión de Fincas | CacaoScan',
        requiresAuth: true,
        requiresRole: 'farmer',
        requiresVerification: true
      }
    },
    {
      path: '/fincas/:id',
      name: 'FincaDetail',
      component: () => import('../views/FincaDetailView.vue'),
      meta: {
        title: 'Detalle de Finca | CacaoScan',
        requiresAuth: true,
        requiresRole: 'farmer',
        requiresVerification: true
      }
    },
    {
      path: '/fincas/:id/lotes',
      name: 'FincaLotes',
      component: () => import('../views/FincaLotesView.vue'),
      meta: {
        title: 'Lotes de Finca | CacaoScan',
        requiresAuth: true,
        requiresRole: 'farmer',
        requiresVerification: true
      }
    },
    {
      path: '/lotes',
      name: 'Lotes',
      component: LotesView,
      meta: {
        title: 'Gestión de Lotes | CacaoScan',
        requiresAuth: true,
        requiresRole: 'farmer',
        requiresVerification: true
      }
    },
    {
      path: '/lotes/:id',
      name: 'LoteDetail',
      component: () => import('../views/LoteDetailView.vue'),
      meta: {
        title: 'Detalle de Lote | CacaoScan',
        requiresAuth: true,
        requiresRole: 'farmer',
        requiresVerification: true
      }
    },
    {
      path: '/lotes/:id/analisis',
      name: 'LoteAnalisis',
      component: () => import('../views/LoteAnalisisView.vue'),
      meta: {
        title: 'Análisis de Lote | CacaoScan',
        requiresAuth: true,
        requiresRole: 'farmer',
        requiresVerification: true
      }
    },
    // Rutas adicionales para autenticación
    {
      path: '/verificar-email',
      name: 'EmailVerification',
      component: () => import('../views/EmailVerification.vue'),
      meta: {
        title: 'Verificar Email | CacaoScan',
        requiresAuth: true
      }
    },
    {
      path: '/reset-password',
      name: 'PasswordReset',
      component: () => import('../views/PasswordReset.vue'),
      meta: {
        title: 'Restablecer Contraseña | CacaoScan',
        requiresGuest: true
      }
    },
    {
      path: '/reset-password/confirm',
      name: 'PasswordResetConfirm',
      component: () => import('../views/PasswordResetConfirm.vue'),
      meta: {
        title: 'Confirmar Nueva Contraseña | CacaoScan',
        requiresGuest: true
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
let navigationTimeout = null

// Guardián global para títulos, loading y configuraciones generales
// Usando formato moderno "return-based" de Vue Router 4
router.beforeEach(async (to, from) => {
  // Limpiar timeout previo si existe
  if (navigationTimeout) {
    clearTimeout(navigationTimeout)
    navigationTimeout = null
  }
  
  // Prevenir navegación múltiple simultánea (solo si es la misma ruta)
  if (isNavigating && to.path === from.path) {
    return false
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
    
    // Usar store de autenticación (ya importado estáticamente)
    const authStore = useAuthStore()
    
    // PRIMERO: Verificar rutas públicas que requieren que el usuario NO esté autenticado
    // Esto debe ir ANTES de verificar requiresAuth para evitar conflictos
    if (to.meta.requiresGuest || to.matched.some(record => record.meta.requiresGuest)) {
      console.log('🔍 Verificando ruta requiresGuest:', to.path)
      console.log('🔍 Estado de autenticación:', {
        isAuthenticated: authStore.isAuthenticated,
        hasToken: !!authStore.accessToken,
        hasUser: !!authStore.user,
        userRole: authStore.userRole
      })
      
      if (authStore.isAuthenticated) {
        console.log('👤 Usuario ya autenticado, redirigiendo desde ruta pública...')
        console.log('📊 Rol del usuario:', authStore.userRole)
        
        // Redirigir según rol
        const redirectPath = getRedirectPathByRole(authStore.userRole)
        console.log('🎯 Redirigiendo a:', redirectPath)
        
        // Evitar bucle infinito: si la ruta de redirección es la misma que la actual
        if (redirectPath === to.path) {
          console.warn('⚠️ Bucle de redirección detectado, permitiendo navegación')
          return true
        }
        
        // Verificar que la ruta de redirección existe
        const routeExists = router.resolve(redirectPath)
        if (!routeExists.matched.length) {
          console.error('❌ Ruta de redirección no existe:', redirectPath)
          console.log('🔄 Redirigiendo a Home como fallback')
          return { path: '/', replace: true }
        }
        
        return { path: redirectPath, replace: true }
      }
    }
    
    // SEGUNDO: Verificar estado de autenticación si se requiere
    if (to.meta.requiresAuth || to.matched.some(record => record.meta.requiresAuth)) {
      
      // Si no hay token, redirigir al login
      if (!authStore.accessToken) {
        console.warn('🚫 Intento de acceso a ruta protegida sin token')
        return {
          name: 'Login',
          replace: true,
          query: { 
            redirect: to.fullPath,
            message: 'Debes iniciar sesión para acceder a esta página'
          }
        }
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
          return {
            name: 'Login',
            replace: true,
            query: { 
              redirect: to.fullPath,
              message: 'Tu sesión ha expirado. Inicia sesión nuevamente.',
              expired: 'true'
            }
          }
        }
      }
      
      // Verificar si la sesión ha expirado por inactividad
      if (authStore.checkSessionTimeout()) {
        console.warn('⏰ Sesión expirada por inactividad')
        // La sesión ha expirado, abortar navegación
        return false
      }
      
      // NUEVO: Verificar rol requerido si la ruta lo especifica
      const requiredRole = to.meta.requiresRole || to.matched.find(record => record.meta.requiresRole)?.meta.requiresRole
      if (requiredRole) {
        const userRole = authStore.userRole?.toLowerCase().trim()
        const normalizedRequiredRole = String(requiredRole).toLowerCase().trim()
        
        console.log('🔐 Verificando rol requerido:', normalizedRequiredRole, '- Rol del usuario:', userRole)
        
        // Verificar si el usuario tiene el rol requerido
        if (userRole !== normalizedRequiredRole) {
          console.warn('⛔ Acceso denegado: Rol insuficiente')
          return {
            path: '/acceso-denegado',
            replace: true,
            query: {
              reason: 'insufficient_role',
              required: normalizedRequiredRole,
              current: userRole
            }
          }
        }
      }
      
      // Actualizar actividad del usuario
      authStore.updateLastActivity()
    }
    
    // Permitir navegación (return undefined o true)
    console.log('✅ Guard completado exitosamente, permitiendo navegación a:', to.path)
    return true
  } catch (error) {
    console.error('Error en navigation guard:', error)
    return { path: '/acceso-denegado', replace: true }
  } finally {
    // Pequeño delay para mejor UX y resetear flag
    navigationTimeout = setTimeout(() => {
      isNavigating = false
      navigationTimeout = null
      // Emit loading end event
      window.dispatchEvent(new CustomEvent('route-loading-end'))
    }, 100)
  }
})

// Función auxiliar para obtener ruta de redirección por rol
const getRedirectPathByRole = (role) => {
  console.log('🔍 getRedirectPathByRole llamado con rol:', role, 'tipo:', typeof role)
  
  // Normalizar el rol a minúsculas para comparación
  const normalizedRole = String(role).toLowerCase().trim()
  
  switch (normalizedRole) {
    case 'admin':
    case 'administrator':
    case 'administrador':
      return '/admin/dashboard'
    case 'analyst':
    case 'analista':
      return '/analisis'
    case 'farmer':
    case 'agricultor':
      return '/agricultor-dashboard'
    default:
      console.warn('⚠️ Rol no reconocido:', role, '- Redirigiendo a /admin/dashboard por defecto')
      // Por defecto, redirigir a admin dashboard en lugar de home para evitar bucles
      return '/admin/dashboard'
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
