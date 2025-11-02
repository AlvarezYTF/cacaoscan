<template>
  <div class="min-h-screen flex flex-col items-center justify-center text-center bg-gray-50 px-4">
    <div class="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
      <!-- Icono de email -->
      <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-6">
        <svg class="h-10 w-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      </div>

      <!-- Título -->
      <h1 class="text-3xl font-bold text-gray-900 mb-4">¡Verifica tu correo!</h1>
      
      <!-- Mensaje -->
      <p class="text-gray-600 mb-2">
        Hemos enviado un enlace de verificación a:
      </p>
      <p class="text-lg font-semibold text-green-600 mb-6">{{ email }}</p>
      
      <p class="text-gray-600 mb-6">
        Revisa tu bandeja de entrada y haz clic en el enlace para activar tu cuenta.
      </p>

      <!-- Información adicional -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 text-left">
        <div class="flex items-start">
          <svg class="h-5 w-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div class="text-sm text-blue-800">
            <p class="font-medium mb-2">¿No recibiste el correo?</p>
            <ul class="list-disc list-inside space-y-1 text-blue-700">
              <li>Revisa la carpeta de spam o correo no deseado</li>
              <li>Asegúrate de que el correo sea correcto</li>
              <li>Espera unos minutos, puede tardar en llegar</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Botones -->
      <div class="space-y-3">
        <button
          @click="resendEmail"
          :disabled="isLoading || cooldown > 0"
          class="w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <svg v-if="isLoading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isLoading ? 'Enviando...' : cooldown > 0 ? `Espera ${cooldown}s` : 'Reenviar email de verificación' }}
        </button>

        <router-link
          to="/login"
          class="block w-full text-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors"
        >
          Ir al inicio de sesión
        </router-link>
      </div>

      <!-- Mensaje de estado -->
      <div v-if="statusMessage" class="mt-6 rounded-md p-4" :class="statusMessageClass">
        <div class="flex items-center">
          <svg v-if="statusType === 'success'" class="h-5 w-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          <svg v-else class="h-5 w-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
          <p class="text-sm font-medium" :class="statusType === 'success' ? 'text-green-800' : 'text-red-800'">
            {{ statusMessage }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const email = ref(route.query.email || 'tu correo')
const isLoading = ref(false)
const statusMessage = ref('')
const statusType = ref('success')
const cooldown = ref(0)
let cooldownInterval = null

const statusMessageClass = computed(() => {
  return statusType.value === 'success' 
    ? 'bg-green-50 border border-green-200'
    : 'bg-red-50 border border-red-200'
})

const startCooldown = () => {
  cooldown.value = 60
  cooldownInterval = setInterval(() => {
    cooldown.value--
    if (cooldown.value <= 0) {
      clearInterval(cooldownInterval)
    }
  }, 1000)
}

const setStatusMessage = (message, type = 'success') => {
  statusMessage.value = message
  statusType.value = type
  setTimeout(() => {
    statusMessage.value = ''
  }, 5000)
}

const resendEmail = async () => {
  if (isLoading.value || cooldown.value > 0) return

  isLoading.value = true

  try {
    const result = await authStore.resendEmailVerification(email.value)
    
    if (result.success) {
      setStatusMessage('Email de verificación reenviado exitosamente. Revisa tu bandeja de entrada.', 'success')
      startCooldown()
    } else {
      setStatusMessage(result.error || 'Error al reenviar el email', 'error')
    }
  } catch (error) {
    console.error('Error reenviando email:', error)
    setStatusMessage('Error inesperado al reenviar el email', 'error')
  } finally {
    isLoading.value = false
  }
}

onUnmounted(() => {
  if (cooldownInterval) {
    clearInterval(cooldownInterval)
  }
})
</script>

