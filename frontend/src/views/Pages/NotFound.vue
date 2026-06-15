<template>
  <!-- Vista 404 con diseño profesional mejorado -->
  <div class="not-found-background min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative">
    <!-- Elementos decorativos de fondo animados -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <!-- Círculos decorativos verdes con animación suave -->
      <div class="absolute top-20 left-10 w-96 h-96 bg-green-500/10 rounded-full blur-3xl animate-pulse-slow"></div>
      <div class="absolute bottom-20 right-10 w-[500px] h-[500px] bg-green-600/10 rounded-full blur-3xl animate-pulse-slow animation-delay-2000"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-green-400/5 rounded-full blur-3xl animate-pulse-slow animation-delay-4000"></div>
      
      <!-- Líneas decorativas sutiles -->
      <div class="absolute top-0 left-1/4 w-px h-96 bg-gradient-to-b from-transparent via-green-500/20 to-transparent"></div>
      <div class="absolute bottom-0 right-1/4 w-px h-96 bg-gradient-to-t from-transparent via-green-500/20 to-transparent"></div>
    </div>

    <!-- Contenido principal -->
    <div class="w-full max-w-2xl relative z-10">
      <!-- Contenedor de error principal con animación -->
      <div class="text-center mb-12 animate-slide-up">
        <!-- Número 404 mejorado con efecto de glitch sutil -->
        <h1 class="text-[180px] sm:text-[220px] font-black text-green-600 mb-6 leading-none select-none animate-fade-in">
          <span class="relative inline-block">
            404
            <span class="absolute inset-0 text-green-500/30 blur-lg animate-pulse-slow">404</span>
          </span>
        </h1>

        <!-- Ícono de grano de cacao con animación flotante -->
        <div class="relative mx-auto w-32 h-32 mb-8">
          <div class="absolute inset-0 bg-green-100 rounded-full animate-ping opacity-20"></div>
          <div class="relative w-full h-full bg-gradient-to-br from-green-500 to-green-600 rounded-full flex items-center justify-center shadow-2xl animate-bounce-slow">
            <svg class="w-16 h-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 20.25a7.962 7.962 0 01-5.196-1.959m10.392 0a7.962 7.962 0 01-4.392.451 7.962 7.962 0 01-4.392-.451M15 8.25a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <!-- Partículas decorativas -->
          <div class="absolute -top-4 -left-4 w-8 h-8 bg-green-300 rounded-full opacity-60 animate-float"></div>
          <div class="absolute -bottom-6 -right-8 w-6 h-6 bg-green-200 rounded-full opacity-40 animate-float-delayed"></div>
        </div>

        <!-- Título y descripción -->
        <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
          Página No Encontrada
        </h2>
        <p class="text-lg text-gray-600 mb-6 max-w-xl mx-auto leading-relaxed">
          La página que buscas no existe o ha sido movida.
          <br class="hidden sm:block">
          <span class="text-green-600 font-semibold">¡Pero no te preocupes!</span> Te ayudamos a encontrar lo que necesitas.
        </p>
      </div>

      <!-- Card de enlaces rápidos -->
      <div class="bg-white border border-gray-200 rounded-2xl shadow-xl p-6 sm:p-8 animate-slide-up-delayed">
        
        <!-- Búsqueda rápida -->
        <div class="mb-8">
          <h3 class="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            ¿Qué estabas buscando?
          </h3>
          
          <!-- Enlaces rápidos según estado de autenticación con diseño mejorado -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            
            <!-- Para usuarios no autenticados -->
            <template v-if="!authStore.isAuthenticated">
              <router-link
                to="/"
                class="group relative flex items-start gap-4 p-4 border-2 border-gray-200 rounded-xl hover:border-green-300 hover:shadow-lg transition-all duration-200 hover:-translate-y-1"
              >
                <div class="flex-shrink-0 w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center group-hover:bg-green-500 transition-colors">
                  <svg class="w-6 h-6 text-green-600 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
                  </svg>
                </div>
                <div class="flex-1">
                  <p class="font-semibold text-gray-900 group-hover:text-green-600 transition-colors">Página Principal</p>
                  <p class="text-sm text-gray-500 mt-1">Conoce CacaoScan</p>
                </div>
                <svg class="w-5 h-5 text-gray-400 group-hover:text-green-600 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </router-link>
              
              <router-link
                to="/login"
                class="group relative flex items-start gap-4 p-4 border-2 border-gray-200 rounded-xl hover:border-green-300 hover:shadow-lg transition-all duration-200 hover:-translate-y-1"
              >
                <div class="flex-shrink-0 w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center group-hover:bg-green-500 transition-colors">
                  <svg class="w-6 h-6 text-green-600 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
                  </svg>
                </div>
                <div class="flex-1">
                  <p class="font-semibold text-gray-900 group-hover:text-green-600 transition-colors">Iniciar Sesión</p>
                  <p class="text-sm text-gray-500 mt-1">Accede a tu cuenta</p>
                </div>
                <svg class="w-5 h-5 text-gray-400 group-hover:text-green-600 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </router-link>
              
              <router-link
                to="/registro"
                class="group relative flex items-start gap-4 p-4 border-2 border-gray-200 rounded-xl hover:border-green-300 hover:shadow-lg transition-all duration-200 hover:-translate-y-1"
              >
                <div class="flex-shrink-0 w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center group-hover:bg-green-500 transition-colors">
                  <svg class="w-6 h-6 text-green-600 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path>
                  </svg>
                </div>
                <div class="flex-1">
                  <p class="font-semibold text-gray-900 group-hover:text-green-600 transition-colors">Crear Cuenta</p>
                  <p class="text-sm text-gray-500 mt-1">Únete a CacaoScan</p>
                </div>
                <svg class="w-5 h-5 text-gray-400 group-hover:text-green-600 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </router-link>
            </template>

            <!-- Para usuarios autenticados -->
            <template v-else>
              <router-link
                :to="getRedirectPath()"
                class="group relative flex items-start gap-4 p-4 border-2 border-gray-200 rounded-xl hover:border-green-300 hover:shadow-lg transition-all duration-200 hover:-translate-y-1"
              >
                <div class="flex-shrink-0 w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center group-hover:bg-green-500 transition-colors">
                  <svg class="w-6 h-6 text-green-600 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5a2 2 0 012-2h2a2 2 0 012 2v2H8V5z"></path>
                  </svg>
                </div>
                <div class="flex-1">
                  <p class="font-semibold text-gray-900 group-hover:text-green-600 transition-colors">Mi Dashboard</p>
                  <p class="text-sm text-gray-500 mt-1">Panel principal</p>
                </div>
                <svg class="w-5 h-5 text-gray-400 group-hover:text-green-600 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </router-link>

              <router-link
                v-if="authStore.canUploadImages"
                to="/prediccion"
                class="group relative flex items-start gap-4 p-4 border-2 border-gray-200 rounded-xl hover:border-green-300 hover:shadow-lg transition-all duration-200 hover:-translate-y-1"
              >
                <div class="flex-shrink-0 w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center group-hover:bg-green-500 transition-colors">
                  <svg class="w-6 h-6 text-green-600 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
                </div>
                <div class="flex-1">
                  <p class="font-semibold text-gray-900 group-hover:text-green-600 transition-colors">Analizar Cacao</p>
                  <p class="text-sm text-gray-500 mt-1">Predicción de granos</p>
                </div>
                <svg class="w-5 h-5 text-gray-400 group-hover:text-green-600 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </router-link>

              <router-link
                v-if="authStore.canViewAllPredictions"
                to="/reportes"
                class="group relative flex items-start gap-4 p-4 border-2 border-gray-200 rounded-xl hover:border-green-300 hover:shadow-lg transition-all duration-200 hover:-translate-y-1"
              >
                <div class="flex-shrink-0 w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center group-hover:bg-green-500 transition-colors">
                  <svg class="w-6 h-6 text-green-600 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                  </svg>
                </div>
                <div class="flex-1">
                  <p class="font-semibold text-gray-900 group-hover:text-green-600 transition-colors">Reportes</p>
                  <p class="text-sm text-gray-500 mt-1">Análisis de datos</p>
                </div>
                <svg class="w-5 h-5 text-gray-400 group-hover:text-green-600 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </router-link>

              <router-link
                to="/perfil"
                class="group relative flex items-start gap-4 p-4 border-2 border-gray-200 rounded-xl hover:border-green-300 hover:shadow-lg transition-all duration-200 hover:-translate-y-1"
              >
                <div class="flex-shrink-0 w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center group-hover:bg-green-500 transition-colors">
                  <svg class="w-6 h-6 text-green-600 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                  </svg>
                </div>
                <div class="flex-1">
                  <p class="font-semibold text-gray-900 group-hover:text-green-600 transition-colors">Mi Perfil</p>
                  <p class="text-sm text-gray-500 mt-1">Configuración de cuenta</p>
                </div>
                <svg class="w-5 h-5 text-gray-400 group-hover:text-green-600 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </router-link>
            </template>
          </div>
        </div>

        <!-- Información adicional con diseño mejorado -->
        <div class="border-t-2 border-gray-200 pt-6 mt-8">
          <div class="bg-gradient-to-br from-green-50 border-2 border-green-200 rounded-xl p-5 shadow-sm">
            <div class="flex items-start gap-4">
              <div class="flex-shrink-0 w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center">
                <svg class="h-5 w-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="flex-1">
                <h3 class="text-sm font-semibold text-green-900 mb-2">¿Necesitas ayuda?</h3>
                <p class="text-sm text-green-800 mb-3">Si estás buscando algo específico, estas páginas pueden ser útiles:</p>
                <ul class="space-y-2 text-sm text-green-700">
                  <li class="flex items-start gap-2">
                    <svg class="w-4 h-4 mt-0.5 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span v-if="!authStore.isAuthenticated">Crea una cuenta para acceder a todas las funcionalidades</span>
                    <span v-else-if="!authStore.isVerified">Verifica tu email para subir imágenes</span>
                    <span v-else>Explora el análisis de granos de cacao</span>
                  </li>
                  <li class="flex items-start gap-2">
                    <svg class="w-4 h-4 mt-0.5 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span>Revisa tu historial de predicciones</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Botón principal mejorado -->
        <div class="mt-8">
          <router-link
            to="/"
            class="w-full flex justify-center items-center gap-2 py-3.5 px-4 border border-transparent rounded-xl shadow-lg text-base font-semibold text-white bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 focus:outline-none focus:ring-4 focus:ring-green-500/50 transition-all duration-200 hover:shadow-xl active:scale-[0.97] group"
          >
            <svg class="w-5 h-5 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
            </svg>
            Volver al Inicio
          </router-link>
        </div>
      </div>

      <!-- Footer con información mejorado -->
      <div class="mt-6 text-center">
        <div class="bg-white/80 backdrop-blur-sm border border-gray-200 rounded-xl p-5 shadow-sm">
          <p class="text-sm font-medium text-gray-700 mb-2">¿Crees que esto es un error?</p>
          <p class="text-sm text-gray-600">
            La URL solicitada: 
          </p>
          <code class="mt-2 inline-block bg-gray-100 border border-gray-200 px-3 py-1.5 rounded-lg text-xs font-mono text-gray-800">{{ currentPath }}</code>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Store y route
const authStore = useAuthStore()
const route = useRoute()

// Computed
const currentPath = computed(() => route.fullPath)

// Métodos
const getRedirectPath = () => {
  if (!authStore.user) return '/'

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
}
</script>

<style scoped>
/* Animaciones personalizadas */
@keyframes pulse-slow {
  0%, 100% {
    opacity: 0.4;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.05);
  }
}

.animate-pulse-slow {
  animation: pulse-slow 6s ease-in-out infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.animate-slide-up {
  animation: slide-up 0.6s ease-out;
}

@keyframes slide-up-delayed {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.animate-slide-up-delayed {
  animation: slide-up-delayed 0.6s ease-out 0.2s both;
}

@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.animate-fade-in {
  animation: fade-in 1s ease-out;
}

@keyframes bounce-slow {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

.animate-bounce-slow {
  animation: bounce-slow 3s ease-in-out infinite;
}

@media (prefers-reduced-motion: reduce) {
  .animate-bounce-slow,
  .animate-fade-in {
    animation: none;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}

.animate-float-delayed {
  animation: float 3s ease-in-out 1.5s infinite;
}

@keyframes ping {
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}

.animate-ping {
  animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;
}
</style>
