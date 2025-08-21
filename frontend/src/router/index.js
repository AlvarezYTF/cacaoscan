import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import NuevoAnalisis from '../views/NuevoAnalisis.vue'
import AnalisisDetalle from '../views/AnalisisDetalle.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import Agricultores from '../views/Agricultores.vue'
import Analisis from '../views/Analisis.vue'
import Reportes from '../views/Reportes.vue'
import AgricultorDashboard from '../views/AgricultorDashboard.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: {
        title: 'Iniciar sesión | CacaoScan',
        hideForAuth: true
      }
    },
    {
      path: '/registro',
      name: 'register',
      component: RegisterView,
      meta: {
        title: 'Registro | CacaoScan',
        hideForAuth: true
      }
    },
    {
      path: '/nuevo-analisis',
      name: 'nuevo-analisis',
      component: NuevoAnalisis,
      meta: {
        title: 'Nuevo Análisis de Lote | CacaoScan'
      }
    },
    {
      path: '/analisis/:id',
      name: 'analisis-detalle',
      component: AnalisisDetalle,
      meta: {
        title: 'Detalle de Análisis | CacaoScan',
        requiresAuth: true
      },
      props: true
    },
    {
      path: '/admin',
      name: 'admin-dashboard',
      component: AdminDashboard,
      meta: {
        title: 'Panel de Administración | CacaoScan',
        requiresAdmin: true
      }
    },
    {
      path: '/admin/agricultores',
      name: 'agricultores',
      component: Agricultores,
      meta: {
        title: 'Gestión de Agricultores | CacaoScan',
        requiresAdmin: true
      }
    },
    {
      path: '/admin/analisis',
      name: 'analisis',
      component: Analisis,
      meta: {
        title: 'Gestión de Análisis | CacaoScan',
        requiresAdmin: true
      }
    },
    {
      path: '/admin/reportes',
      name: 'reportes',
      component: Reportes,
      meta: {
        title: 'Reportes | CacaoScan',
        requiresAdmin: true
      }
    },
    {
      path: '/agricultor',
      name: 'agricultor-dashboard',
      component: AgricultorDashboard,
      meta: {
        title: 'Dashboard de Agricultor | CacaoScan',
        requiresAuth: true
      }
    }
  ],
})

// // Guardián de navegación para autenticación y títulos de página
// router.beforeEach((to, from, next) => {
//   // Actualizar el título de la página
//   document.title = to.meta?.title || 'CacaoScan';

//   // Verificar si el usuario está autenticado
//   const isAuthenticated = localStorage.getItem('auth_token');
//   const userRole = localStorage.getItem('user_role'); // Asume que guardas el rol del usuario

//   // Si la ruta requiere autenticación y el usuario no está autenticado
//   if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
//     // Redirigir al inicio de sesión si intenta acceder a una ruta protegida
//     next({ name: 'login' });
//   } 
//   // Si la ruta es solo para administradores y el usuario no es administrador
//   else if (to.matched.some(record => record.meta.requiresAdmin) && (!isAuthenticated || userRole !== 'admin')) {
//     // Redirigir al inicio si no tiene permisos de administrador
//     next({ path: '/' });
//   }
//   // Si el usuario está autenticado y trata de acceder a login/registro
//   else if (to.matched.some(record => record.meta.hideForAuth) && isAuthenticated) {
//     // Redirigir al dashboard de administrador si es admin, de lo contrario al inicio
//     next(userRole === 'admin' ? { name: 'admin-dashboard' } : { path: '/' });
//   } 
//   // En cualquier otro caso, permitir la navegación
//   else {
//     next();
//   }
// });

export default router
