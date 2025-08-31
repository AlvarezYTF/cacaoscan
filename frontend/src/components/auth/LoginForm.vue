<template>
  <div class="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
    <!-- Header -->
    <div class="text-center mb-6">
      <h2 class="text-2xl font-bold text-gray-900">Iniciar Sesión</h2>
      <p class="text-gray-600 mt-2">Accede a tu cuenta de CacaoScan</p>
    </div>

    <!-- Mensaje de estado -->
    <div v-if="statusMessage" class="mb-4 p-3 rounded-md" :class="statusMessageClass">
      {{ statusMessage }}
    </div>

    <!-- Formulario -->
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <!-- Email/Username -->
      <div>
        <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
          Email o Usuario
        </label>
        <input
          id="email"
          v-model="form.email"
          type="text"
          autocomplete="email"
          required
          :disabled="isLoading"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100"
          :class="{ 'border-red-500': errors.email }"
          placeholder="usuario@ejemplo.com"
        />
        <p v-if="errors.email" class="mt-1 text-sm text-red-600">{{ errors.email }}</p>
      </div>

      <!-- Contraseña -->
      <div>
        <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
          Contraseña
        </label>
        <div class="relative">
          <input
            id="password"
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            autocomplete="current-password"
            required
            :disabled="isLoading"
            class="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100"
            :class="{ 'border-red-500': errors.password }"
            placeholder="Ingresa tu contraseña"
          />
          <button
            type="button"
            @click="showPassword = !showPassword"
            class="absolute inset-y-0 right-0 pr-3 flex items-center"
            :disabled="isLoading"
          >
            <svg
              v-if="showPassword"
              class="h-5 w-5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <svg
              v-else
              class="h-5 w-5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L12 12m-3.122-3.122l4.243 4.243M12 12l3 3m0 0l6-6" />
            </svg>
          </button>
        </div>
        <p v-if="errors.password" class="mt-1 text-sm text-red-600">{{ errors.password }}</p>
      </div>

      <!-- Recordar sesión -->
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <input
            id="remember"
            v-model="form.remember"
            type="checkbox"
            class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
            :disabled="isLoading"
          />
          <label for="remember" class="ml-2 block text-sm text-gray-700">
            Recordar sesión
          </label>
        </div>
        <div class="text-sm">
          <router-link
            to="/reset-password"
            class="font-medium text-green-600 hover:text-green-500"
          >
            ¿Olvidaste tu contraseña?
          </router-link>
        </div>
      </div>

      <!-- Botón de envío -->
      <button
        type="submit"
        :disabled="isLoading"
        class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <svg
          v-if="isLoading"
          class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        {{ isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión' }}
      </button>
    </form>

    <!-- Separador -->
    <div class="mt-6">
      <div class="relative">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t border-gray-300" />
        </div>
        <div class="relative flex justify-center text-sm">
          <span class="px-2 bg-white text-gray-500">¿No tienes cuenta?</span>
        </div>
      </div>
    </div>

    <!-- Link a registro -->
    <div class="mt-6">
      <router-link
        to="/registro"
        class="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
      >
        Crear nueva cuenta
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Store y route
const authStore = useAuthStore()
const route = useRoute()

// Estado del formulario
const form = ref({
  email: '',
  password: '',
  remember: false
})

const showPassword = ref(false)
const errors = ref({})

// Estado de carga
const isLoading = computed(() => authStore.isLoading)

// Mensaje de estado (desde query params o errores)
const statusMessage = ref('')
const statusMessageClass = ref('')

// Validación del formulario
const validateForm = () => {
  errors.value = {}
  
  if (!form.value.email.trim()) {
    errors.value.email = 'El email es requerido'
  } else if (!isValidEmail(form.value.email) && !isValidUsername(form.value.email)) {
    errors.value.email = 'Ingresa un email válido o nombre de usuario'
  }
  
  if (!form.value.password) {
    errors.value.password = 'La contraseña es requerida'
  } else if (form.value.password.length < 6) {
    errors.value.password = 'La contraseña debe tener al menos 6 caracteres'
  }
  
  return Object.keys(errors.value).length === 0
}

// Validadores
const isValidEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

const isValidUsername = (username) => {
  // Username alfanumérico, guiones y guiones bajos, 3-30 caracteres
  const re = /^[a-zA-Z0-9_-]{3,30}$/
  return re.test(username)
}

// Manejar envío del formulario
const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  // Emitir evento de loading
  window.dispatchEvent(new CustomEvent('api-loading-start', {
    detail: { type: 'login', message: 'Verificando credenciales...' }
  }))

  try {
    const result = await authStore.login({
      email: form.value.email.trim(),
      password: form.value.password
    })

    if (result.success) {
      // Éxito manejado por el store (redirección automática)
      setStatusMessage('Inicio de sesión exitoso', 'success')
    } else {
      setStatusMessage(result.error || 'Error al iniciar sesión', 'error')
    }
  } catch (error) {
    console.error('Error en login:', error)
    setStatusMessage('Error inesperado al iniciar sesión', 'error')
  } finally {
    // Emitir evento de fin de loading
    window.dispatchEvent(new CustomEvent('api-loading-end'))
  }
}

// Configurar mensaje de estado
const setStatusMessage = (message, type) => {
  statusMessage.value = message
  statusMessageClass.value = type === 'success' 
    ? 'bg-green-100 border border-green-400 text-green-700'
    : 'bg-red-100 border border-red-400 text-red-700'
  
  // Limpiar mensaje después de 5 segundos
  setTimeout(() => {
    statusMessage.value = ''
  }, 5000)
}

// Inicializar componente
onMounted(() => {
  // Mostrar mensajes desde query params
  if (route.query.message) {
    const type = route.query.expired ? 'error' : 'info'
    setStatusMessage(route.query.message, type)
  }
  
  // Limpiar error del store si existe
  if (authStore.error) {
    setStatusMessage(authStore.error, 'error')
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
</style>
