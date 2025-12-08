import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// Verificar configuración del API al iniciar
if (typeof globalThis !== 'undefined') {
  // Validar que config.js se haya cargado
  if (!globalThis.__API_BASE_URL__ && !import.meta.env.VITE_API_BASE_URL) {
    }
}

// Crear la app
const app = createApp(App)

// Configurar Pinia
const pinia = createPinia()
app.use(pinia)

// Configurar router
app.use(router)

// Inicializar stores
import { useAuthStore } from '@/stores/auth'
import { useConfigStore } from '@/stores/config'

// Función para inicializar la aplicación
const initApp = async () => {
  try {
    const authStore = useAuthStore()
    const configStore = useConfigStore()
    
    // Inicializar autenticación completa
    await authStore.initializeAuth()
    
    // Cargar configuración del sistema (silenciar errores esperados)
    try {
      await configStore.loadAll()
      } catch (err) {
      // Ignorar errores de configuración - usar valores por defecto
      }
    
  } catch (error) {
    }

  // Montar la aplicación
  app.mount('#app')
}

// Configurar notificaciones globales
globalThis.showNotification = (notification) => {
  // Placeholder para sistema de notificaciones
  // Aquí se puede integrar con una librería de notificaciones
  // como vue-toastification o similar
}

// Inicializar aplicación
initApp()
