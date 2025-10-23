<template>
  <div v-if="isInitializing" class="auth-initializer">
    <div class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">Verificando sesión...</p>
    </div>
  </div>
  <slot v-else />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const isInitializing = ref(true)

onMounted(async () => {
  try {
    // Inicializar autenticación
    await authStore.initializeAuth()
  } catch (error) {
    console.error('Error inicializando autenticación:', error)
  } finally {
    isInitializing.value = false
  }
})
</script>

<style scoped>
.auth-initializer {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-container {
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #10b981;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

.loading-text {
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
