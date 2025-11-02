<template>
  <div class="flex flex-col items-center justify-center min-h-screen bg-gray-50">
    <div class="bg-white rounded-xl shadow-lg p-8 w-full max-w-md text-center">
      <!-- Icono de verificación -->
      <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-4">
        <svg class="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      </div>

      <!-- Título -->
      <h1 class="text-2xl font-bold text-gray-900 mb-4">Verificación de correo electrónico</h1>
      
      <!-- Descripción -->
      <p class="text-gray-600 mb-2">Hemos enviado un código de 6 dígitos a tu correo electrónico.</p>
      <p class="text-sm text-gray-500 mb-6" v-if="email">Escríbelo a continuación para verificar tu cuenta en:</p>
      <p class="text-sm font-semibold text-green-600 mb-6" v-if="email">{{ email }}</p>
      <p class="text-sm text-gray-500 mb-6" v-else>Escríbelo a continuación para verificar tu cuenta.</p>

      <!-- Mensaje de error -->
      <Transition enter-active-class="transform ease-out duration-300" enter-from-class="opacity-0 scale-95" 
        enter-to-class="opacity-100 scale-100" leave-active-class="transition ease-in duration-200" 
        leave-from-class="opacity-100" leave-to-class="opacity-0">
        <div v-if="errorMessage" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div class="flex items-start gap-3">
            <svg class="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="text-sm font-medium text-red-800 text-left">{{ errorMessage }}</p>
          </div>
        </div>
      </Transition>

      <!-- Mensaje de éxito -->
      <Transition enter-active-class="transform ease-out duration-300" enter-from-class="opacity-0 scale-95" 
        enter-to-class="opacity-100 scale-100" leave-active-class="transition ease-in duration-200" 
        leave-from-class="opacity-100" leave-to-class="opacity-0">
        <div v-if="successMessage" class="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div class="flex items-start gap-3">
            <svg class="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="text-sm font-medium text-green-800 text-left">{{ successMessage }}</p>
          </div>
        </div>
      </Transition>

      <!-- Input para código OTP -->
      <div class="mb-6">
        <input 
          id="otpCode" 
          v-model="otpCode" 
          type="text"
          maxlength="6"
          placeholder="000000"
          :disabled="isLoading"
          @input="onOtpInput"
          @keyup.enter="verifyCode"
          class="w-full p-4 border-2 border-gray-300 rounded-lg text-center tracking-widest text-2xl font-mono focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 disabled:cursor-not-allowed transition-all duration-200"
          autocomplete="one-time-code"
          autofocus
        />
        <p class="text-xs text-gray-500 mt-2">Ingresa el código de 6 dígitos</p>
      </div>

      <!-- Botón de verificación -->
      <button 
        @click="verifyCode" 
        :disabled="isLoading || !isCodeValid"
        class="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        <svg v-if="isLoading" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span>{{ isLoading ? 'Verificando...' : 'Verificar Código' }}</span>
      </button>

      <!-- Enlace para reenviar código -->
      <div class="mt-6">
        <p class="text-sm text-gray-600 mb-2">
          ¿No recibiste el código?
        </p>
        <button 
          @click="resendCode" 
          :disabled="isResending || !canResend"
          class="text-green-600 font-semibold hover:underline cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span v-if="isResending">Reenviando...</span>
          <span v-else-if="!canResend">Reenviar código en {{ countdown }}s</span>
          <span v-else>Reenviar código</span>
        </button>
      </div>

      <!-- Enlace para volver al registro -->
      <div class="mt-6 pt-6 border-t border-gray-200">
        <p class="text-sm text-gray-600 mb-2">
          ¿Tienes problemas con la verificación?
        </p>
        <router-link 
          to="/registro" 
          class="text-green-600 font-semibold hover:underline transition-colors"
        >
          Volver al registro
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import authApi from '@/services/authApi'

const route = useRoute()
const router = useRouter()

// Estado
const email = ref('')
const otpCode = ref('')
const isLoading = ref(false)
const isResending = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const canResend = ref(true)
const countdown = ref(60)
const countdownInterval = ref(null)

// Computed
const isCodeValid = computed(() => {
  return otpCode.value.length === 6 && /^\d{6}$/.test(otpCode.value)
})

// Métodos
const onOtpInput = (event) => {
  // Solo permitir números
  const value = event.target.value.replace(/[^0-9]/g, '')
  otpCode.value = value
}

const startCountdown = () => {
  canResend.value = false
  countdown.value = 60
  
  countdownInterval.value = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      canResend.value = true
      clearInterval(countdownInterval.value)
    }
  }, 1000)
}

const clearMessages = () => {
  errorMessage.value = ''
  successMessage.value = ''
}

const verifyCode = async () => {
  if (!isCodeValid.value || isLoading.value) return

  clearMessages()
  isLoading.value = true

  try {
    const response = await authApi.verifyOtp(email.value, otpCode.value)
    
    // El backend puede devolver response.success o verificación directa
    if (response.success || response.message || (response.data && !response.data.error)) {
      successMessage.value = 'Código verificado exitosamente. Redirigiendo...'
      
      // Redirigir al login después de 2 segundos con mensaje de éxito
      setTimeout(() => {
        router.push({
          name: 'Login',
          query: { 
            message: 'Cuenta verificada con éxito. Ya puedes iniciar sesión.',
            verified: 'true'
          }
        })
      }, 2000)
    } else {
      errorMessage.value = response.error || response.message || 'Código incorrecto o expirado'
    }
  } catch (error) {
    console.error('Error verificando código OTP:', error)
    const errorMsg = error.response?.data?.message || error.response?.data?.error || error.response?.data?.detail || 'Código incorrecto o expirado'
    errorMessage.value = errorMsg
  } finally {
    isLoading.value = false
  }
}

const resendCode = async () => {
  if (isResending.value || !canResend.value) return

  clearMessages()
  isResending.value = true

  try {
    const response = await authApi.sendOtp(email.value)
    
    // El backend puede devolver response.success o mensaje directo
    if (response.success || response.message || (response.data && !response.data.error)) {
      successMessage.value = 'Código reenviado exitosamente. Revisa tu correo.'
      startCountdown()
    } else {
      errorMessage.value = response.error || response.message || 'Error al reenviar código'
    }
  } catch (error) {
    console.error('Error reenviando código OTP:', error)
    const errorMsg = error.response?.data?.message || error.response?.data?.error || error.response?.data?.detail || 'Error al reenviar código'
    errorMessage.value = errorMsg
  } finally {
    isResending.value = false
  }
}

// Lifecycle
onMounted(() => {
  // Obtener email de query params o del estado local
  email.value = route.query.email || ''
  
  if (!email.value) {
    // Si no hay email, redirigir al registro
    router.push({ 
      name: 'Register',
      query: { message: 'Por favor completa el registro primero' }
    })
    return
  }

  // Iniciar countdown automáticamente
  startCountdown()
  
  // Limpiar mensajes después de 5 segundos si existen
  const messageTimeout = setTimeout(() => {
    clearMessages()
  }, 5000)
  
  return () => clearTimeout(messageTimeout)
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

