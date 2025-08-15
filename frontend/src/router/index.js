import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import NuevoAnalisis from '../views/NuevoAnalisis.vue'
import AnalisisDetalle from '../views/AnalisisDetalle.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

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
        title: 'Detalle de Análisis | CacaoScan'
      },
      props: true
    }
  ],
})

// Navigation guard for authentication and page titles
router.beforeEach((to, from, next) => {
  // Update page title
  document.title = to.meta?.title || 'CacaoScan';

  // Check if the route requires authentication
  const isAuthenticated = localStorage.getItem('auth_token'); // Update this based on your auth implementation

  if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
    // Redirect to login if trying to access protected route
    next({ name: 'login' });
  } else if (to.matched.some(record => record.meta.hideForAuth) && isAuthenticated) {
    // Prevent accessing login page when already authenticated
    next({ path: '/' });
  } else {
    next();
  }
});

export default router
