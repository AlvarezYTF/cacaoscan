<template>
  <!-- Vista de restablecimiento con diseño profesional -->
  <div class="auth-background min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative">
    <!-- Elementos decorativos de fondo animados -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <!-- Círculos decorativos verdes con animación suave -->
      <div class="absolute top-20 left-10 w-72 h-72 bg-green-500/10 rounded-full blur-3xl animate-pulse-slow"></div>
      <div class="absolute bottom-20 right-10 w-96 h-96 bg-green-600/10 rounded-full blur-3xl animate-pulse-slow animation-delay-2000"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-green-400/5 rounded-full blur-3xl animate-pulse-slow animation-delay-4000"></div>
      
      <!-- Líneas decorativas sutiles -->
      <div class="absolute top-0 left-1/4 w-px h-96 bg-gradient-to-b from-transparent via-green-500/20 to-transparent"></div>
      <div class="absolute bottom-0 right-1/4 w-px h-96 bg-gradient-to-t from-transparent via-green-500/20 to-transparent"></div>
    </div>

    <!-- Contenedor principal con animación de entrada -->
    <div class="auth-form-container w-full max-w-md relative z-10 animate-slide-up">
      <!-- Badge superior mejorado -->
      <div class="absolute -top-4 left-1/2 -translate-x-1/2">
        <div class="group relative bg-gradient-to-r from-green-500 to-green-600 text-white px-5 py-2 rounded-full shadow-xl flex items-center gap-2 text-sm font-semibold hover:shadow-2xl hover:scale-105 transition-all duration-300">
          <div class="absolute inset-0 rounded-full bg-white/20 opacity-0 group-hover:opacity-100 blur-xl transition-opacity duration-300"></div>
          <svg class="w-4 h-4 relative z-10 group-hover:rotate-180 transition-transform duration-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          <span class="relative z-10">Recuperación Segura</span>
        </div>
      </div>

      <!-- Contenido del formulario -->
      <div class="py-10 px-6 sm:px-10">
        <!-- Formulario de solicitud -->
        <div v-if="!emailSent">
          <!-- Header -->
          <div class="text-center mb-8">
            <div class="mx-auto w-16 h-16 bg-green-100 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
              <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-6.586l4.686-4.686a2 2 0 012.828 0L16 8a2 2 0 012 2z" />
              </svg>
            </div>
            <h2 class="text-3xl font-bold text-gray-900 mb-2">Restablecer Contraseña</h2>
            <p class="text-gray-600 text-base">Ingresa tu email para recibir instrucciones</p>
          </div>

          <!-- Componente de formulario -->
          <PasswordResetForm 
            ref="resetFormRef"
            :is-loading="isLoading"
            :error="errors.email"
            :initial-email="form.email"
            @submit="handleSubmit"
          />
        </div>

        <!-- Confirmación de envío -->
        <PasswordResetConfirmation
          v-else
          :email="form.email"
          :is-loading="isLoading"
          :recently-sent="recentlySent"
          :countdown="countdown"
          :button-text="getResendButtonText()"
          @resend="sendAnother"
        />
      </div>

      <!-- Mensaje de error -->
      <Transition
        enter-active-class="transform ease-out duration-300 transition"
        enter-from-class="opacity-0 translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition ease-in duration-200"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="errorMessage && !emailSent" class="px-6 sm:px-10 pb-6">
          <div class="bg-red-50 border-2 border-red-200 rounded-xl p-4 flex items-start gap-3">
            <svg class="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 class="text-sm font-semibold text-red-800">Error</h3>
              <p class="mt-1 text-sm text-red-700">{{ errorMessage }}</p>
            </div>
          </div>
        </div>
      </Transition>

      <!-- Footer con enlaces adicionales -->
      <div class="border-t border-gray-200 px-6 sm:px-10 py-4 bg-gradient-to-b from-gray-50/50 to-gray-100/30 rounded-b-2xl">
        <div class="text-center space-y-3">
          <p class="text-xs text-gray-500">¿Recordaste tu contraseña?</p>
          <div class="flex justify-center gap-3">
            <router-link
              to="/login"
              class="text-sm font-semibold text-green-600 hover:text-green-700 transition-colors flex items-center gap-1"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
              </svg>
              Iniciar Sesión
            </router-link>
            <span class="text-gray-300">·</span>
            <router-link
              to="/registro"
              class="text-sm font-semibold text-green-600 hover:text-green-700 transition-colors"
            >
              Crear Cuenta
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Link de retorno -->
    <div class="absolute bottom-4 left-1/2 -translate-x-1/2 z-10">
      <router-link 
        to="/login"
        class="group bg-white/10 backdrop-blur-sm hover:bg-white/20 text-white hover:text-white px-5 py-2.5 rounded-full flex items-center gap-2 text-sm font-medium transition-all duration-300 border border-white/20 hover:border-white/40"
      >
        <svg class="w-4 h-4 group-hover:-translate-x-1.5 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        <span class="group-hover:translate-x-0.5 transition-transform duration-300">Volver al login</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import PasswordResetForm from '@/components/auth/PasswordResetForm.vue'
import PasswordResetConfirmation from '@/components/auth/PasswordResetConfirmation.vue'

// Store y route
const authStore = useAuthStore()
const route = useRoute()

// Referencia al formulario
const resetFormRef = ref(null)

// Estado del formulario
const form = ref({
  email: ''
})

const errors = ref({})
const emailSent = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')
const recentlySent = ref(false)
const countdown = ref(60)
const countdownInterval = ref(null)

// Computed
const getResendButtonText = () => {
  if (isLoading.value) return 'Enviando...'
  if (recentlySent.value) return `Esperar ${countdown.value}s`
  return 'Enviar Nuevamente'
}

// Validación
const validateForm = () => {
  errors.value = {}
  
  if (!form.value.email.trim()) {
    errors.value.email = 'El email es requerido'
  } else if (!isValidEmail(form.value.email)) {
    errors.value.email = 'Ingresa un email válido'
  }
  
  return Object.keys(errors.value).length === 0
}

const isValidEmail = (email) => {
  if (!email || typeof email !== 'string') {
    return false
  }
  
  const trimmedEmail = email.trim()
  
  // Limit email length to prevent DoS attacks (RFC 5321 max length)
  if (trimmedEmail.length === 0 || trimmedEmail.length > 254) {
    return false
  }
  
  // Simple, safe email validation without catastrophic backtracking
  // Split by @ to avoid regex backtracking issues
  const parts = trimmedEmail.split('@')
  if (parts.length !== 2) {
    return false
  }
  
  const [localPart, domainPart] = parts
  
  // Validate local part (before @) - max 64 chars (RFC 5321)
  if (!localPart || localPart.length === 0 || localPart.length > 64) {
    return false
  }
  
  // Check for invalid patterns in local part
  if (localPart.includes('..') || localPart.startsWith('.') || localPart.endsWith('.')) {
    return false
  }
  
  // Validate domain part (after @) - max 253 chars (RFC 5321)
  if (!domainPart || domainPart.length === 0 || domainPart.length > 253) {
    return false
  }
  
  // Check for at least one dot in domain
  const domainParts = domainPart.split('.')
  if (domainParts.length < 2 || domainParts.some(part => part.length === 0)) {
    return false
  }
  
  // Validate characters without regex to avoid backtracking
  // Check local part contains only valid characters
  const isValidLocalChar = (char) => {
    const code = char.codePointAt(0)
    if (code === undefined) {
      return false
    }
    return (code >= 48 && code <= 57) || // 0-9
           (code >= 65 && code <= 90) || // A-Z
           (code >= 97 && code <= 122) || // a-z
           char === '.' || char === '_' || char === '+' || char === '-'
  }
  
  // Check domain part contains only valid characters
  const isValidDomainChar = (char) => {
    const code = char.codePointAt(0)
    if (code === undefined) {
      return false
    }
    return (code >= 48 && code <= 57) || // 0-9
           (code >= 65 && code <= 90) || // A-Z
           (code >= 97 && code <= 122) || // a-z
           char === '.' || char === '-'
  }
  
  // Check if all characters are valid
  const hasInvalidLocalChar = Array.from(localPart).some(char => !isValidLocalChar(char))
  const hasInvalidDomainChar = Array.from(domainPart).some(char => !isValidDomainChar(char))
  
  return !hasInvalidLocalChar && !hasInvalidDomainChar
}

// Funciones
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

const handleSubmit = async (email) => {
  // Actualizar el form con el email del componente
  form.value.email = email
  
  if (!validateForm()) {
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    const result = await authStore.requestPasswordReset(form.value.email.trim())
    
    if (result.success) {
      emailSent.value = true
      startCountdown()
    } else {
      errorMessage.value = result.error || 'Error al enviar instrucciones'
    }
  } catch (error) {
    console.error('Error en password reset:', error)
    errorMessage.value = 'Error inesperado. Intenta nuevamente.'
  } finally {
    isLoading.value = false
  }
}

const sendAnother = async () => {
  if (isLoading.value || recentlySent.value) return
  
  // Usar el email del form
  await handleSubmit(form.value.email)
}

// Lifecycle
onMounted(() => {
  // Pre-llenar email si viene en query params
  if (route.query.email) {
    form.value.email = route.query.email
  }
  
  // Mostrar mensaje si viene en query params
  if (route.query.message) {
    errorMessage.value = route.query.message
  }
})

onUnmounted(() => {
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value)
  }
})
</script>

<style scoped>
/* Animaciones reutilizadas */
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
</style>
