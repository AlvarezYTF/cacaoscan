<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="text-center">
        <svg class="mx-auto h-12 w-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
        </svg>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Crear Cuenta
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Únete a CacaoScan para comenzar a analizar tus granos de cacao
        </p>
      </div>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Nombres -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label for="firstName" class="block text-sm font-medium text-gray-700">
                Nombre *
              </label>
              <div class="mt-1">
                <input
                  id="firstName"
                  v-model="form.firstName"
                  type="text"
                  autocomplete="given-name"
                  required
                  :disabled="isLoading"
                  class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm disabled:bg-gray-100"
                  :class="{ 'border-red-500': errors.firstName }"
                  placeholder="Juan"
                />
              </div>
              <p v-if="errors.firstName" class="mt-2 text-sm text-red-600">{{ errors.firstName }}</p>
            </div>

            <div>
              <label for="lastName" class="block text-sm font-medium text-gray-700">
                Apellido *
              </label>
              <div class="mt-1">
                <input
                  id="lastName"
                  v-model="form.lastName"
                  type="text"
                  autocomplete="family-name"
                  required
                  :disabled="isLoading"
                  class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm disabled:bg-gray-100"
                  :class="{ 'border-red-500': errors.lastName }"
                  placeholder="Pérez"
                />
              </div>
              <p v-if="errors.lastName" class="mt-2 text-sm text-red-600">{{ errors.lastName }}</p>
            </div>
          </div>

          <!-- Email -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">
              Email *
            </label>
            <div class="mt-1">
              <input
                id="email"
                v-model="form.email"
                type="email"
                autocomplete="email"
                required
                :disabled="isLoading"
                class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm disabled:bg-gray-100"
                :class="{ 'border-red-500': errors.email }"
                placeholder="juan@ejemplo.com"
              />
            </div>
            <p v-if="errors.email" class="mt-2 text-sm text-red-600">{{ errors.email }}</p>
          </div>

          <!-- Teléfono (opcional) -->
          <div>
            <label for="phoneNumber" class="block text-sm font-medium text-gray-700">
              Teléfono
            </label>
            <div class="mt-1">
              <input
                id="phoneNumber"
                v-model="form.phoneNumber"
                type="tel"
                autocomplete="tel"
                :disabled="isLoading"
                class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm disabled:bg-gray-100"
                :class="{ 'border-red-500': errors.phoneNumber }"
                placeholder="+57 300 123 4567"
              />
            </div>
            <p v-if="errors.phoneNumber" class="mt-2 text-sm text-red-600">{{ errors.phoneNumber }}</p>
          </div>

          <!-- Rol -->
          <div>
            <label for="role" class="block text-sm font-medium text-gray-700">
              Tipo de Usuario *
            </label>
            <div class="mt-1">
              <select
                id="role"
                v-model="form.role"
                required
                :disabled="isLoading"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm disabled:bg-gray-100"
                :class="{ 'border-red-500': errors.role }"
              >
                <option value="">Selecciona tu tipo de usuario</option>
                <option value="farmer">Agricultor - Productor de cacao</option>
                <option value="analyst">Analista - Investigador o técnico</option>
              </select>
            </div>
            <p v-if="errors.role" class="mt-2 text-sm text-red-600">{{ errors.role }}</p>
            <p class="mt-1 text-xs text-gray-500">
              Los usuarios administradores son creados por el sistema
            </p>
          </div>

          <!-- Contraseñas -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">
              Contraseña *
            </label>
            <div class="mt-1 relative">
              <input
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="new-password"
                required
                :disabled="isLoading"
                class="appearance-none block w-full px-3 py-2 pr-10 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm disabled:bg-gray-100"
                :class="{ 'border-red-500': errors.password }"
                placeholder="••••••••"
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
            <p v-if="errors.password" class="mt-2 text-sm text-red-600">{{ errors.password }}</p>
          </div>

          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700">
              Confirmar Contraseña *
            </label>
            <div class="mt-1">
              <input
                id="confirmPassword"
                v-model="form.confirmPassword"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="new-password"
                required
                :disabled="isLoading"
                class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm disabled:bg-gray-100"
                :class="{ 'border-red-500': errors.confirmPassword }"
                placeholder="••••••••"
              />
            </div>
            <p v-if="errors.confirmPassword" class="mt-2 text-sm text-red-600">{{ errors.confirmPassword }}</p>
          </div>

          <!-- Validador de contraseña -->
          <div v-if="form.password" class="bg-gray-50 rounded-md p-4">
            <h4 class="text-sm font-medium text-gray-900 mb-2">Requisitos de la contraseña:</h4>
            <ul class="space-y-1">
              <li class="flex items-center text-sm" :class="passwordChecks.length ? 'text-green-600' : 'text-gray-500'">
                <svg class="mr-2 h-4 w-4" :class="passwordChecks.length ? 'text-green-500' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="passwordChecks.length ? 'M5 13l4 4L19 7' : 'M6 18L18 6M6 6l12 12'"></path>
                </svg>
                Al menos 8 caracteres
              </li>
              <li class="flex items-center text-sm" :class="passwordChecks.uppercase ? 'text-green-600' : 'text-gray-500'">
                <svg class="mr-2 h-4 w-4" :class="passwordChecks.uppercase ? 'text-green-500' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="passwordChecks.uppercase ? 'M5 13l4 4L19 7' : 'M6 18L18 6M6 6l12 12'"></path>
                </svg>
                Una letra mayúscula
              </li>
              <li class="flex items-center text-sm" :class="passwordChecks.lowercase ? 'text-green-600' : 'text-gray-500'">
                <svg class="mr-2 h-4 w-4" :class="passwordChecks.lowercase ? 'text-green-500' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="passwordChecks.lowercase ? 'M5 13l4 4L19 7' : 'M6 18L18 6M6 6l12 12'"></path>
                </svg>
                Una letra minúscula
              </li>
              <li class="flex items-center text-sm" :class="passwordChecks.number ? 'text-green-600' : 'text-gray-500'">
                <svg class="mr-2 h-4 w-4" :class="passwordChecks.number ? 'text-green-500' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="passwordChecks.number ? 'M5 13l4 4L19 7' : 'M6 18L18 6M6 6l12 12'"></path>
                </svg>
                Un número
              </li>
            </ul>
          </div>

          <!-- Términos y condiciones -->
          <div class="flex items-center">
            <input
              id="acceptTerms"
              v-model="form.acceptTerms"
              type="checkbox"
              required
              :disabled="isLoading"
              class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
            />
            <label for="acceptTerms" class="ml-2 block text-sm text-gray-900">
              Acepto los 
              <a href="#" class="text-green-600 hover:text-green-500">términos y condiciones</a> 
              y la 
              <a href="#" class="text-green-600 hover:text-green-500">política de privacidad</a>
            </label>
          </div>
          
          <div class="flex items-center">
            <input
              id="emailNotifications"
              v-model="form.emailNotifications"
              type="checkbox"
              :disabled="isLoading"
              class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
            />
            <label for="emailNotifications" class="ml-2 block text-sm text-gray-900">
              Quiero recibir notificaciones por email sobre mi cuenta
            </label>
          </div>

          <!-- Botón de envío -->
          <div>
            <button
              type="submit"
              :disabled="isLoading || !isFormValid"
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
              {{ isLoading ? 'Creando cuenta...' : 'Crear Cuenta' }}
            </button>
          </div>
        </form>

        <!-- Mensaje de estado -->
        <div v-if="statusMessage" class="mt-4 rounded-md p-4" :class="statusMessageClass">
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

      <!-- Enlaces adicionales -->
      <div class="mt-6 text-center">
        <p class="text-sm text-gray-600">
          ¿Ya tienes una cuenta?
          <router-link
            to="/login"
            class="font-medium text-green-600 hover:text-green-500"
          >
            Inicia sesión aquí
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Router y store
const router = useRouter()
const authStore = useAuthStore()

// Estado del formulario
const form = ref({
  firstName: '',
  lastName: '',
  email: '',
  phoneNumber: '',
  role: '',
  password: '',
  confirmPassword: '',
  acceptTerms: false,
  emailNotifications: true
})

const errors = ref({})
const isLoading = ref(false)
const showPassword = ref(false)
const statusMessage = ref('')
const statusType = ref('info')

// Computed
const passwordChecks = computed(() => {
  const password = form.value.password
  return {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /\d/.test(password)
  }
})

const isPasswordValid = computed(() => {
  return Object.values(passwordChecks.value).every(check => check)
})

const isFormValid = computed(() => {
  return (
    form.value.firstName.trim() &&
    form.value.lastName.trim() &&
    form.value.email.trim() &&
    form.value.role &&
    isPasswordValid.value &&
    form.value.password === form.value.confirmPassword &&
    form.value.acceptTerms
  )
})

const statusMessageClass = computed(() => {
  return statusType.value === 'success' 
    ? 'bg-green-50 border border-green-200'
    : 'bg-red-50 border border-red-200'
})

// Validación
const validateForm = () => {
  errors.value = {}
  
  if (!form.value.firstName.trim()) {
    errors.value.firstName = 'El nombre es requerido'
  }
  
  if (!form.value.lastName.trim()) {
    errors.value.lastName = 'El apellido es requerido'
  }
  
  if (!form.value.email.trim()) {
    errors.value.email = 'El email es requerido'
  } else if (!isValidEmail(form.value.email)) {
    errors.value.email = 'Ingresa un email válido'
  }
  
  if (form.value.phoneNumber && !isValidPhone(form.value.phoneNumber)) {
    errors.value.phoneNumber = 'Ingresa un número de teléfono válido'
  }
  
  if (!form.value.role) {
    errors.value.role = 'Selecciona tu tipo de usuario'
  }
  
  if (!form.value.password) {
    errors.value.password = 'La contraseña es requerida'
  } else if (!isPasswordValid.value) {
    errors.value.password = 'La contraseña no cumple con los requisitos de seguridad'
  }
  
  if (!form.value.confirmPassword) {
    errors.value.confirmPassword = 'Confirma tu contraseña'
  } else if (form.value.password !== form.value.confirmPassword) {
    errors.value.confirmPassword = 'Las contraseñas no coinciden'
  }
  
  if (!form.value.acceptTerms) {
    errors.value.acceptTerms = 'Debes aceptar los términos y condiciones'
  }
  
  return Object.keys(errors.value).length === 0
}

const isValidEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

const isValidPhone = (phone) => {
  const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/
  return phoneRegex.test(phone.replace(/\s/g, ''))
}

const setStatusMessage = (message, type = 'info') => {
  statusMessage.value = message
  statusType.value = type
  
  setTimeout(() => {
    statusMessage.value = ''
  }, 5000)
}

// Manejar envío del formulario
const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  // Emitir evento de loading
  window.dispatchEvent(new CustomEvent('api-loading-start', {
    detail: { type: 'register', message: 'Creando tu cuenta...' }
  }))

  isLoading.value = true

  try {
    const result = await authStore.register({
      first_name: form.value.firstName.trim(),
      last_name: form.value.lastName.trim(),
      email: form.value.email.trim(),
      phone_number: form.value.phoneNumber.trim() || null,
      role: form.value.role,
      password: form.value.password,
      confirm_password: form.value.confirmPassword,
      email_notifications: form.value.emailNotifications
    })

    if (result.success) {
      setStatusMessage('¡Cuenta creada exitosamente! Revisa tu email para verificar tu cuenta.', 'success')
      
      // Redirigir después de 3 segundos
      setTimeout(() => {
        router.push({
          name: 'Login',
          query: { 
            message: 'Cuenta creada exitosamente. Revisa tu email para verificarla.',
            email: form.value.email
          }
        })
      }, 3000)
    } else {
      setStatusMessage(result.error || 'Error al crear la cuenta', 'error')
    }
  } catch (error) {
    console.error('Error en registro:', error)
    setStatusMessage('Error inesperado. Intenta nuevamente.', 'error')
  } finally {
    isLoading.value = false
    // Emitir evento de fin de loading
    window.dispatchEvent(new CustomEvent('api-loading-end'))
  }
}
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