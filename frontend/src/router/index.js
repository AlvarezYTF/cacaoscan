import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import NuevoAnalisis from '../views/NuevoAnalisis.vue'
import AnalisisDetalle from '../views/AnalisisDetalle.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
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

// Update page title based on route meta
router.beforeEach((to, from, next) => {
  document.title = to.meta?.title || 'CacaoScan';
  next();
});

export default router
