<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="text-center">
        <svg class="mx-auto h-12 w-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Verificar Email
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Confirma tu dirección de correo electrónico
        </p>
      </div>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        
        <!-- Estado de verificación automática -->
        <div v-if="autoVerifying" class="text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p class="text-gray-600">Verificando tu email automáticamente...</p>
        </div>

        <!-- Verificación exitosa -->
        <div v-else-if="verificationStatus === 'success'" class="text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
            <svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">¡Email Verificado!</h3>
          <p class="text-gray-600 mb-6">Tu dirección de correo ha sido verificada exitosamente.</p>
          <router-link
            :to="getRedirectPath()"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            Continuar a mi Dashboard
          </router-link>
        </div>

        <!-- Error en verificación -->
        <div v-else-if="verificationStatus === 'error'" class="text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
            <svg class="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Error en Verificación</h3>
          <p class="text-gray-600 mb-6">{{ errorMessage }}</p>
          <button
            @click="resendVerification"
            :disabled="isLoading"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
          >
            {{ isLoading ? 'Enviando...' : 'Reenviar Email de Verificación' }}
          </button>
        </div>

        <!-- Estado inicial - mostrar información -->
        <div v-else class="space-y-6">
          <!-- Estado del usuario actual -->
          <div v-if="authStore.user" class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="h-10 w-10 rounded-full bg-green-600 flex items-center justify-center text-white font-medium">
                  {{ authStore.userInitials }}
                </div>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-900">{{ authStore.userFullName }}</p>
                <p class="text-sm text-gray-500">{{ authStore.user.email }}</p>
                <div class="flex items-center mt-1">
                  <span v-if="authStore.isVerified" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                    <svg class="mr-1 h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    Verificado
                  </span>
                  <span v-else class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                    <svg class="mr-1 h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                    </svg>
                    No verificado
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Información sobre verificación -->
          <div v-if="!authStore.isVerified">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Verificación Requerida</h3>
            <div class="bg-yellow-50 border border-yellow-200 rounded-md p-4 mb-6">
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg class="h-5 w-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                  </svg>
                </div>
                <div class="ml-3">
                  <h3 class="text-sm font-medium text-yellow-800">Verificación Pendiente</h3>
                  <div class="mt-2 text-sm text-yellow-700">
                    <p>Para acceder a todas las funcionalidades de CacaoScan, necesitas verificar tu dirección de correo electrónico.</p>
                    <ul class="list-disc list-inside mt-2 space-y-1">
                      <li>Revisa tu bandeja de entrada en <strong>{{ authStore.user?.email }}</strong></li>
                      <li>Busca también en la carpeta de spam o correo no deseado</li>
                      <li>Haz clic en el enlace de verificación en el email</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <!-- Botón para reenviar -->
            <button
              @click="resendVerification"
              :disabled="isLoading || recentlySent"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg v-if="isLoading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ getButtonText() }}
            </button>

            <p v-if="recentlySent" class="mt-2 text-sm text-gray-500 text-center">
              Podrás solicitar otro email en {{ countdown }} segundos
            </p>
          </div>

          <!-- Ya verificado -->
          <div v-else>
            <div class="text-center">
              <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
                <svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </div>
              <h3 class="text-lg font-medium text-gray-900 mb-2">¡Tu email ya está verificado!</h3>
              <p class="text-gray-600 mb-6">Tienes acceso completo a todas las funcionalidades de CacaoScan.</p>
              <router-link
                :to="getRedirectPath()"
                class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                Ir a mi Dashboard
              </router-link>
            </div>
          </div>

          <!-- Mensaje de estado -->
          <div v-if="statusMessage" class="rounded-md p-4" :class="statusMessageClass">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg v-if="statusType === 'success'" class="h-5 w-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                <svg v-else class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium" :class="statusType === 'success' ? 'text-green-800' : 'text-red-800'">
                  {{ statusMessage }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Enlaces útiles -->
      <div class="mt-6 text-center">
        <div class="space-y-2">
          <router-link
            to="/perfil"
            class="text-sm text-green-600 hover:text-green-500"
          >
            Ir a mi perfil
          </router-link>
          <span class="text-gray-300">·</span>
          <router-link
            :to="getRedirectPath()"
            class="text-sm text-green-600 hover:text-green-500"
          >
            Ir al dashboard
          </router-link>
          <span class="text-gray-300">·</span>
          <button
            @click="authStore.logout()"
            class="text-sm text-gray-500 hover:text-gray-400"
          >
            Cerrar sesión
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Store y router
const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

// Estado del componente
const verificationStatus = ref(null) // null, 'success', 'error'
const autoVerifying = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')
const statusMessage = ref('')
const statusType = ref('info')
const recentlySent = ref(false)
const countdown = ref(60)
const countdownInterval = ref(null)

// Computed
const statusMessageClass = computed(() => {
  return statusType.value === 'success' 
    ? 'bg-green-50 border border-green-200'
    : 'bg-red-50 border border-red-200'
})

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

const getButtonText = () => {
  if (isLoading.value) return 'Enviando...'
  if (recentlySent.value) return `Espera ${countdown.value}s`
  return 'Reenviar Email de Verificación'
}

const setStatusMessage = (message, type = 'info') => {
  statusMessage.value = message
  statusType.value = type
  
  setTimeout(() => {
    statusMessage.value = ''
  }, 5000)
}

const startCountdown = () => {
  recentlySent.value = true
  countdown.value = 60
  
  countdownInterval.value = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      recentlySent.value = false
      clearInterval(countdownInterval.value)
    }
  }, 1000)
}

const resendVerification = async () => {
  if (isLoading.value || recentlySent.value) return

  isLoading.value = true
  
  try {
    const result = await authStore.resendEmailVerification()
    
    if (result.success) {
      setStatusMessage('Email de verificación enviado exitosamente. Revisa tu bandeja de entrada.', 'success')
      startCountdown()
    } else {
      setStatusMessage(result.error || 'Error al enviar email de verificación', 'error')
    }
  } catch (error) {
    setStatusMessage('Error inesperado al enviar email', 'error')
  } finally {
    isLoading.value = false
  }
}

const verifyEmailFromUrl = async () => {
  // Obtener token desde la URL (path params o query params)
  const token = route.params.token || route.query.token
  
  if (!token) {
    return
  }

  autoVerifying.value = true
  
  try {
    const result = await authStore.verifyEmailFromToken(token)
    
    if (result.success) {
      verificationStatus.value = 'success'
      
      // Limpiar query params de la URL
      router.replace({ query: {} })
      
      // Redirigir después de 3 segundos
      setTimeout(() => {
        router.push(getRedirectPath())
      }, 3000)
    } else {
      verificationStatus.value = 'error'
      errorMessage.value = result.error || 'Token de verificación inválido o expirado'
    }
  } catch (error) {
    verificationStatus.value = 'error'
    errorMessage.value = 'Error inesperado al verificar email'
  } finally {
    autoVerifying.value = false
  }
}

// Lifecycle
onMounted(async () => {
  // Mostrar mensaje desde query params si existe
  if (route.query.message) {
    setStatusMessage(route.query.message, 'info')
  }
  
  // Si hay token en la URL (path o query), intentar verificar automáticamente
  if (route.params.token || route.query.token) {
    await verifyEmailFromUrl()
  }
})

onUnmounted(() => {
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value)
  }
})
</script>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
