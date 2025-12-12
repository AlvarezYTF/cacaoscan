<template>
  <div>
    <!-- Header con mejor presentación visual -->
    <div class="text-center mb-10">
      <img src="@/assets/sena-logo.png" alt="Logo CacaoScan" class="mx-auto h-16 w-auto mb-5 animate-fade-in drop-shadow-lg">
      <h2 class="text-3xl font-bold text-gray-900 mb-2">Iniciar Sesión</h2>
      <p class="text-gray-600 text-base">Accede a tu cuenta de CacaoScan</p>
    </div>

    <!-- Mensaje de estado mejorado con ícono -->
    <Transition
      enter-active-class="transform ease-out duration-300 transition"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="statusMessage" class="mb-6 p-4 rounded-xl flex items-start gap-3" :class="statusMessageClass">
        <svg v-if="statusMessageClass.includes('green')" class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <svg v-else class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-sm font-medium">{{ statusMessage }}</p>
      </div>
    </Transition>

    <!-- Formulario con inputs mejorados -->
    <form @submit.prevent="handleSubmit" class="space-y-5">
      <!-- Email/Username con ícono y mejor presentación -->
      <div>
        <label for="email" class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          Email o Usuario
        </label>
        <div class="relative">
          <input
            id="email"
            v-model="form.email"
            type="text"
            autocomplete="email"
            required
            :disabled="isLoading"
            class="w-full pl-4 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
            :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/50': errors.email, 'border-green-300': form.email && !errors.email }"
            placeholder="usuario@ejemplo.com"
          />
          <!-- Indicador de validación -->
          <div v-if="form.email && !errors.email && isLoading === false" class="absolute inset-y-0 right-0 pr-3 flex items-center">
            <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>
        <Transition
          enter-active-class="transform ease-out duration-200"
          enter-from-class="opacity-0 -translate-y-1"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition ease-in duration-150"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
        >
          <p v-if="errors.email" class="mt-1.5 text-sm text-red-600 font-medium flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {{ errors.email }}
          </p>
        </Transition>
      </div>

      <!-- Contraseña con mejor interacción visual -->
      <div>
        <label for="password" class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          Contraseña
        </label>
        <div class="relative">
          <input
            id="password"
            :type="showPassword ? 'text' : 'password'"
            v-model="form.password"
            :autocomplete="showPassword ? 'username' : 'current-password'"
            required
            :disabled="isLoading"
            class="w-full pl-4 pr-12 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
            :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/50': errors.password, 'border-green-300': form.password && !errors.password }"
            placeholder="••••••••••••"
          />
          <button
            type="button"
            @click="showPassword = !showPassword"
            class="absolute inset-y-0 right-0 pr-3 flex items-center hover:bg-gray-50 rounded-r-lg transition-all duration-200"
            :disabled="isLoading"
            :title="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
          >
            <svg
              v-if="showPassword"
              class="h-5 w-5 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <svg
              v-else
              class="h-5 w-5 text-gray-400 hover:text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L12 12m-3.122-3.122l4.243 4.243M12 12l3 3m0 0l6-6" />
            </svg>
          </button>
        </div>
        <Transition
          enter-active-class="transform ease-out duration-200"
          enter-from-class="opacity-0 -translate-y-1"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition ease-in duration-150"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
        >
          <p v-if="errors.password" class="mt-1.5 text-sm text-red-600 font-medium flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {{ errors.password }}
          </p>
        </Transition>
      </div>

      <!-- Recordar sesión y recuperación de contraseña con mejor estilo -->
      <div class="flex items-center justify-between pt-1">
        <div class="flex items-center group">
          <input
            id="remember"
            v-model="form.remember"
            type="checkbox"
            class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded cursor-pointer"
            :disabled="isLoading"
          />
          <label for="remember" class="ml-2.5 block text-sm text-gray-700 cursor-pointer group-hover:text-gray-900 transition-colors">
            Recordar sesión
          </label>
        </div>
        <router-link
          to="/reset-password"
          class="text-sm font-medium text-green-600 hover:text-green-700 transition-colors flex items-center gap-1 group/link"
        >
          <span>¿Olvidaste tu contraseña?</span>
          <svg class="w-4 h-4 group-hover/link:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </router-link>
      </div>

      <!-- Botón de envío mejorado con mejor feedback visual -->
      <button
        type="submit"
        :disabled="isLoading"
        class="w-full flex justify-center items-center gap-2 py-3.5 px-4 border border-transparent rounded-xl shadow-lg text-base font-semibold text-white bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 focus:outline-none focus:ring-4 focus:ring-green-500/50 disabled:opacity-60 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-xl active:scale-[0.97] group"
      >
        <BaseSpinner 
          v-if="isLoading"
          size="md"
          color="white"
        />
        <svg v-if="!isLoading" class="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
        </svg>
        <span>{{ isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión' }}</span>
      </button>
    </form>

    <!-- Separador para Google Login -->
    <div class="mt-6">
      <div class="relative">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t border-gray-200"></div>
        </div>
        <div class="relative flex justify-center text-sm">
          <span class="px-4 bg-white text-gray-500">o</span>
        </div>
      </div>
    </div>

    <!-- Botón de Google Login -->
    <div class="mt-6">
      <div id="google-login-button" class="w-full"></div>
    </div>

    <!-- Separador con mejor presentación -->
    <div class="mt-8">
      <div class="relative">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t border-gray-200"></div>
        </div>
        <div class="relative flex justify-center text-sm">
          <span class="px-4 bg-white text-gray-500 flex items-center gap-2">
            <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
            ¿No tienes cuenta?
          </span>
        </div>
      </div>
    </div>

    <!-- Link a registro con estilo mejorado -->
    <div class="mt-6">
      <router-link
        to="/registro"
        class="w-full flex justify-center items-center gap-2 py-3 px-4 border-2 border-gray-200 rounded-xl shadow-sm text-base font-semibold text-gray-700 bg-white hover:bg-gray-50 hover:border-green-300 focus:outline-none focus:ring-4 focus:ring-green-500/30 transition-all duration-200 hover:shadow-md active:scale-[0.97] group"
      >
        <svg class="w-5 h-5 group-hover:scale-110 group-hover:rotate-12 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
        </svg>
        <span class="group-hover:text-green-600 transition-colors">Crear nueva cuenta</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useAuthForm } from '@/composables/useAuthForm'
import BaseSpinner from '@/components/common/BaseSpinner.vue'
import { setupGoogleLogin } from '@/utils/googleAuth'
import authApi from '@/services/authApi'
import { useAuthStore } from '@/stores/auth'

// Route and Router
const route = useRoute()
const router = useRouter()

// Use auth composable
const { login: loginUser, loading, error, clearError } = useAuth()

// Auth store
const authStore = useAuthStore()

// Form state using useAuthForm for validation
const authForm = useAuthForm({
  initialValues: {
    email: '',
    password: '',
    remember: false
  },
  onSubmit: async (formData) => {
    try {
      globalThis.dispatchEvent(new CustomEvent('api-loading-start', {
        detail: { type: 'login', message: 'Verificando credenciales...' }
      }))

      const result = await loginUser({
        email: formData.email.trim(),
        password: formData.password
      })

      if (result.success) {
        authForm.setStatusMessage('¡Bienvenido de vuelta a CacaoScan! 🌱', 'success')
      }
      
      return result
    } catch (err) {
      const errorMessage = err.message || 
                          err.response?.data?.error ||
                          err.response?.data?.message || 
                          err.response?.data?.detail ||
                          'Error inesperado al iniciar sesión'
      authForm.setStatusMessage(errorMessage, 'error')
      throw err
    } finally {
      globalThis.dispatchEvent(new CustomEvent('api-loading-end'))
    }
  }
})

// Extract form properties
const form = authForm.form
const errors = authForm.errors
const statusMessage = authForm.statusMessage
const statusMessageClass = authForm.statusMessageClass
const setStatusMessage = authForm.setStatusMessage

// Local state
const showPassword = ref(false)
const googleLoginLoading = ref(false)

// Handle Google Login
const handleGoogleCredential = async (credential) => {
  try {
    googleLoginLoading.value = true
    
    globalThis.dispatchEvent(new CustomEvent('api-loading-start', {
      detail: { type: 'google-login', message: 'Verificando con Google...' }
    }))

    const result = await authApi.googleLogin(credential)
    
    if (result.success) {
      // Guardar tokens
      authStore.setTokens({
        access: result.access,
        refresh: result.refresh
      })
      
      // Guardar usuario (el backend retorna user completo con todos los campos)
      const userData = result.user || {
        email: result.email,
        name: result.name,
        picture: result.picture
      }
      
      // Asegurar que todos los campos críticos estén presentes
      // Incluir has_password si viene en la respuesta
      if (result.has_password !== undefined) {
        userData.has_password = result.has_password
      }
      
      // PRIORIDAD: login_provider y password_allowed desde result (ya normalizados)
      // Estos valores tienen prioridad porque vienen directamente de la respuesta del backend
      if (result.login_provider !== undefined) {
        userData.login_provider = result.login_provider
      }
      if (result.password_allowed !== undefined) {
        userData.password_allowed = result.password_allowed
      }
      
      // Si no vienen en result, intentar desde userData
      if (!userData.login_provider && result.user?.login_provider) {
        userData.login_provider = result.user.login_provider
      }
      if (userData.password_allowed === undefined && result.user?.password_allowed !== undefined) {
        userData.password_allowed = result.user.password_allowed
      }
      
      // Si aún no están definidos, calcular desde login_provider
      if (!userData.login_provider) {
        userData.login_provider = 'local' // Default
      }
      if (userData.password_allowed === undefined) {
        userData.password_allowed = userData.login_provider !== 'google'
      }
      
      console.log('🔐 Google Login - User data being saved:', {
        login_provider: userData.login_provider,
        password_allowed: userData.password_allowed,
        has_password: userData.has_password
      })
      
      authStore.setUser(userData)
      
      authForm.setStatusMessage('¡Bienvenido a CacaoScan! 🌱', 'success')
      
      // Redirigir al dashboard
      router.push('/dashboard')
    }
  } catch (err) {
    const errorMessage = err.message || 
                        err.response?.data?.error ||
                        err.response?.data?.message || 
                        err.response?.data?.detail ||
                        'Error al iniciar sesión con Google'
    authForm.setStatusMessage(errorMessage, 'error')
  } finally {
    googleLoginLoading.value = false
    globalThis.dispatchEvent(new CustomEvent('api-loading-end'))
  }
}

// Handle form submission
const handleSubmit = async () => {
  try {
    await authForm.handleAuthSubmit()
  } catch (err) {
    // Error is already handled by useAuthForm
  }
}

// Computed
const isLoading = computed(() => loading.value || authForm.isSubmitting.value)

// Initialize component
onMounted(async () => {
  // Show messages from query params
  if (route.query.message) {
    const type = route.query.expired ? 'error' : 'info'
    setStatusMessage(route.query.message, type)
  }
  
  // Clear error if exists
  if (error.value) {
    setStatusMessage(error.value, 'error')
    clearError()
  }
  
  // Inicializar Google Login
  try {
    await setupGoogleLogin('google-login-button', handleGoogleCredential)
  } catch (error) {
    console.error('Error inicializando Google Login:', error)
    // No mostrar error al usuario si falla la inicialización, solo en consola
  }
})

onUnmounted(() => {
  // Limpiar el contenedor del botón de Google al desmontar
  const container = document.getElementById('google-login-button')
  if (container) {
    container.innerHTML = ''
  }
})
</script>

<style scoped>
/* Estilos adicionales si son necesarios */
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

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.6s ease-out;
}
</style>

