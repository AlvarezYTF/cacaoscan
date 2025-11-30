<template>
  <BaseModal
    :show="visible"
    title="Sesión expirada"
    subtitle="Por seguridad, tu sesión ha expirado. Inicia sesión nuevamente para continuar."
    max-width="md"
    :show-close-button="false"
    :close-on-overlay="false"
    @close="redirectToLogin"
    @update:show="handleUpdateShow"
  >
    <template #header>
      <div class="flex items-center justify-center mb-4">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="w-14 h-14 text-red-500 animate-pulse"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 8v4m0 4h.01M21 12A9 9 0 1 1 3 12a9 9 0 0 1 18 0z"
          />
        </svg>
      </div>
    </template>

    <div class="text-center">
      <!-- Indicador de tiempo -->
      <div class="mb-6">
        <div class="text-sm text-gray-500 dark:text-gray-400 mb-2">
          Redirigiendo en {{ countdown }} segundos
        </div>
        <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div
            class="bg-green-600 h-2 rounded-full transition-all duration-1000"
            :style="{ width: `${(countdown / 5) * 100}%` }"
          ></div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-center">
        <button
          @click="redirectToLogin"
          class="w-full px-5 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium shadow-md transition-all duration-200 transform hover:scale-105 active:scale-95"
        >
          Iniciar sesión
        </button>
      </div>
    </template>
  </BaseModal>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BaseModal from './BaseModal.vue'

const visible = ref(false)
const countdown = ref(5)
const router = useRouter()
const authStore = useAuthStore()
let countdownInterval = null

// Función para mostrar el modal (expuesta al componente)
const show = () => {
  visible.value = true
  countdown.value = 5
  
  // Limpiar intervalo anterior si existe
  if (countdownInterval) {
    clearInterval(countdownInterval)
  }
  
  // Contador regresivo
  countdownInterval = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      redirectToLogin()
    }
  }, 1000)
}

function redirectToLogin() {
  // Limpiar intervalo
  if (countdownInterval) {
    clearInterval(countdownInterval)
    countdownInterval = null
  }
  
  visible.value = false
  
  // Dar tiempo para la animación de salida
  setTimeout(() => {
    authStore.logout()
    router.push('/login')
  }, 300)
}

const handleUpdateShow = (value) => {
  visible.value = value
}

// Limpiar intervalo al desmontar
onUnmounted(() => {
  if (countdownInterval) {
    clearInterval(countdownInterval)
  }
})

// Exponer la función show para uso externo
defineExpose({
  show
})
</script>

<script>
// Script adicional para exportar la función globalmente
export function showSessionExpiredModal(modalInstance) {
  if (modalInstance) {
    modalInstance.show()
  }
}
</script>

<style scoped>
/* Styles are now handled by BaseModal */
</style>

