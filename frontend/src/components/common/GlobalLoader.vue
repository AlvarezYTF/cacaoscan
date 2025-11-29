<template>
  <!-- Global loading overlay -->
  <teleport to="body">
    <transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="isLoading" class="fixed inset-0 z-50 flex items-center justify-center">
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-white bg-opacity-80 backdrop-blur-sm"></div>
        
        <!-- Loading content -->
        <div class="relative text-center">
          <!-- Logo animado -->
          <div class="relative mb-6">
            <div class="animate-pulse">
              <div class="h-16 w-16 mx-auto bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center shadow-lg">
                <svg class="h-8 w-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
              </div>
            </div>
            
            <!-- Círculos animados alrededor -->
            <div class="absolute inset-0 animate-spin">
              <div class="h-20 w-20 border-2 border-green-200 border-t-green-500 rounded-full"></div>
            </div>
          </div>
          
          <!-- Texto de carga -->
          <div class="space-y-2">
            <h3 class="text-lg font-semibold text-gray-900">{{ loadingText }}</h3>
            <p class="text-sm text-gray-600">{{ loadingMessage }}</p>
          </div>
          
          <!-- Barra de progreso -->
          <div class="mt-4 w-64 mx-auto">
            <div class="bg-gray-200 rounded-full h-1.5 overflow-hidden">
              <div 
                class="bg-gradient-to-r from-green-400 to-green-600 h-full rounded-full transition-all duration-300 ease-out"
                :style="{ width: `${progress}%` }"
              ></div>
            </div>
          </div>
          
          <!-- Dots animados -->
          <div class="mt-4 flex justify-center space-x-1">
            <div
              v-for="i in 3"
              :key="i"
              class="w-2 h-2 bg-green-500 rounded-full animate-bounce"
              :style="{ animationDelay: `${(i - 1) * 0.1}s` }"
            ></div>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// Estado
const isLoading = ref(false)
const loadingText = ref('Cargando...')
const loadingMessage = ref('Por favor espera')
const progress = ref(0)

// Timers
let progressTimer = null
let loadingTimer = null

// Configurar loading state
const showLoading = (text = 'Cargando...', message = 'Por favor espera') => {
  isLoading.value = true
  loadingText.value = text
  loadingMessage.value = message
  progress.value = 0
  
  // Simular progreso
  startProgress()
}

const hideLoading = () => {
  // Completar progreso antes de ocultar
  progress.value = 100
  
  setTimeout(() => {
    isLoading.value = false
    clearTimers()
  }, 200)
}

const startProgress = () => {
  clearTimers()
  
  // Use deterministic progress increment for visual effect
  // NOSONAR: This is for UI progress bar animation, not cryptographic use
  // Increment counter for deterministic variation
  let stepCounter = 0
  
  progressTimer = setInterval(() => {
    if (progress.value < 90) {
      // Deterministic increment with variation: cycles through values 2-9
      // This provides smooth, predictable progress without using PRNG
      const increment = 2 + (stepCounter % 8) // Values from 2 to 9
      progress.value += increment
      stepCounter++
    }
  }, 150)
}

const clearTimers = () => {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
  
  if (loadingTimer) {
    clearTimeout(loadingTimer)
    loadingTimer = null
  }
}

// Event listeners para eventos de navegación
const handleRouteLoadingStart = (event) => {
  const { to } = event.detail
  
  // Determinar texto según la ruta de destino
  let text = 'Cargando...'
  let message = 'Preparando la página'
  
  if (to.meta?.title) {
    text = 'Cargando'
    message = to.meta.title.replace(' | CacaoScan', '')
  } else if (to.name) {
    const routeNames = {
      'Login': 'Iniciando sesión',
      'Register': 'Preparando registro',
      'AdminDashboard': 'Cargando panel de administración',
      'AgricultorDashboard': 'Cargando dashboard',
      'Prediction': 'Preparando análisis de cacao',
      'Profile': 'Cargando perfil de usuario',
      'EmailVerification': 'Verificando email'
    }
    
    text = routeNames[to.name] || 'Cargando página'
    message = 'Un momento por favor...'
  }
  
  showLoading(text, message)
}

const handleRouteLoadingEnd = () => {
  hideLoading()
}

// API loading events
const handleAPILoadingStart = (event) => {
  const { type, message } = event.detail || {}
  
  const apiMessages = {
    'login': 'Iniciando sesión...',
    'register': 'Creando cuenta...',
    'upload': 'Subiendo imagen...',
    'prediction': 'Analizando imagen...',
    'profile': 'Guardando perfil...'
  }
  
  showLoading(
    apiMessages[type] || 'Procesando...',
    message || 'Por favor espera'
  )
}

const handleAPILoadingEnd = () => {
  hideLoading()
}

// Lifecycle
onMounted(() => {
  // Eventos de navegación
  globalThis.addEventListener('route-loading-start', handleRouteLoadingStart)
  globalThis.addEventListener('route-loading-end', handleRouteLoadingEnd)
  
  // Eventos de API
  globalThis.addEventListener('api-loading-start', handleAPILoadingStart)
  globalThis.addEventListener('api-loading-end', handleAPILoadingEnd)
})

onUnmounted(() => {
  // Limpiar event listeners
  globalThis.removeEventListener('route-loading-start', handleRouteLoadingStart)
  globalThis.removeEventListener('route-loading-end', handleRouteLoadingEnd)
  globalThis.removeEventListener('api-loading-start', handleAPILoadingStart)
  globalThis.removeEventListener('api-loading-end', handleAPILoadingEnd)
  
  clearTimers()
})

// Exponer métodos globalmente
globalThis.showGlobalLoading = showLoading
globalThis.hideGlobalLoading = hideLoading
</script>

<style scoped>
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.animate-spin {
  animation: spin 3s linear infinite;
}

.animate-bounce {
  animation: bounce 1s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: .7;
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(-25%);
    animation-timing-function: cubic-bezier(0.8,0,1,1);
  }
  50% {
    transform: none;
    animation-timing-function: cubic-bezier(0,0,0.2,1);
  }
}
</style>
