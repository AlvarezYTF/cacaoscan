<template>
  <!-- Formulario de solicitud de reset con diseño mejorado -->
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <!-- Email con ícono y validación visual -->
    <div>
      <label for="email" class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
        <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        Dirección de Email *
      </label>
      <div class="relative">
        <input
          id="email"
          v-model="form.email"
          type="email"
          autocomplete="email"
          required
          :disabled="isLoading"
          class="w-full pl-4 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
          :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/50': error, 'border-green-300': form.email && !error }"
          placeholder="usuario@ejemplo.com"
        />
        <div v-if="form.email && !error && isLoading === false" class="absolute inset-y-0 right-0 pr-3 flex items-center">
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
        <p v-if="error" class="mt-1.5 text-sm text-red-600 font-medium flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ error }}
        </p>
      </Transition>
    </div>

    <!-- Información con mejor diseño -->
    <div class="bg-blue-50 border-2 border-blue-200 rounded-xl p-5 shadow-sm">
      <div class="flex items-start gap-3">
        <div class="flex-shrink-0">
          <div class="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
            <svg class="h-5 w-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        <div class="flex-1">
          <h3 class="text-sm font-semibold text-blue-900 mb-2">¿Cómo funciona?</h3>
          <ul class="space-y-2 text-sm text-blue-800">
            <li class="flex items-start gap-2">
              <svg class="w-4 h-4 mt-0.5 text-blue-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span>Ingresa tu dirección de email registrada</span>
            </li>
            <li class="flex items-start gap-2">
              <svg class="w-4 h-4 mt-0.5 text-blue-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span>Recibirás un enlace seguro en tu bandeja de entrada</span>
            </li>
            <li class="flex items-start gap-2">
              <svg class="w-4 h-4 mt-0.5 text-blue-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span>Haz clic en el enlace para crear una nueva contraseña</span>
            </li>
            <li class="flex items-start gap-2">
              <svg class="w-4 h-4 mt-0.5 text-blue-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>El enlace expira en 1 hora por seguridad</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Botón de envío mejorado -->
    <button
      type="submit"
      :disabled="isLoading"
      class="w-full flex justify-center items-center gap-2 py-3.5 px-4 border border-transparent rounded-xl shadow-lg text-base font-semibold text-white bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 focus:outline-none focus:ring-4 focus:ring-green-500/50 disabled:opacity-60 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-xl active:scale-[0.97] group"
    >
      <svg
        v-if="isLoading"
        class="animate-spin h-5 w-5 text-white"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <svg v-else class="w-5 h-5 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
      <span>{{ isLoading ? 'Enviando...' : 'Enviar Instrucciones' }}</span>
    </button>
  </form>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
  isLoading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  initialEmail: {
    type: String,
    default: ''
  }
})

const form = ref({
  email: ''
})

// Sincronizar con email inicial
watch(() => props.initialEmail, (newValue) => {
  if (newValue) {
    form.value.email = newValue
  }
}, { immediate: true })

onMounted(() => {
  if (props.initialEmail) {
    form.value.email = props.initialEmail
  }
})

const emit = defineEmits(['submit'])

const handleSubmit = () => {
  // Asegurarse de que tenemos el email del formulario
  const email = form.value.email?.trim() || ''
  
  if (!email) {
    return // La validación del input required lo manejará
  }
  
  // Emitir el email limpio
  emit('submit', email)
}

defineExpose({
  form
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

