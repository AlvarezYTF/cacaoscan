<template>
  <div class="fixed inset-0 bg-white bg-opacity-75 flex items-center justify-center z-50">
    <div class="text-center">
      <!-- Spinner de carga -->
      <div class="relative">
        <div class="animate-spin rounded-full h-16 w-16 border-4 border-green-200 border-t-green-600 mx-auto mb-4"></div>
        <!-- Logo pequeño en el centro -->
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="h-6 w-6 bg-green-600 rounded-full flex items-center justify-center">
            <svg class="h-3 w-3 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2M21 9V7L15 1V3H9V1L3 7V9H5V19C5 20.1 5.9 21 7 21H17C18.1 21 19 20.1 19 19V9H21Z"/>
            </svg>
          </div>
        </div>
      </div>
      
      <!-- Texto de carga -->
      <h3 class="text-lg font-medium text-gray-900 mb-2">{{ title }}</h3>
      <p class="text-sm text-gray-500">{{ message }}</p>
      
      <!-- Barra de progreso (opcional) -->
      <div v-if="showProgress" class="w-64 bg-gray-200 rounded-full h-2 mx-auto mt-4">
        <div 
          class="bg-green-600 h-2 rounded-full transition-all duration-300 ease-out"
          :style="{ width: `${progress}%` }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Props
const props = defineProps({
  title: {
    type: String,
    default: 'Cargando...'
  },
  message: {
    type: String,
    default: 'Preparando la página'
  },
  showProgress: {
    type: Boolean,
    default: false
  },
  autoProgress: {
    type: Boolean,
    default: false
  }
})

// Estado
const progress = ref(0)

// Auto-progress simulation
onMounted(() => {
  if (props.autoProgress) {
    const interval = setInterval(() => {
      if (progress.value < 90) {
        progress.value += Math.random() * 15
      } else {
        clearInterval(interval)
      }
    }, 200)
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
