import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// Verificar configuración del API al iniciar
if (typeof window !== 'undefined') {
  console.log('🔍 [Main] Verificando configuración del API...')
  console.log('🔍 [Main] window.__API_BASE_URL__:', window.__API_BASE_URL__)
  console.log('🔍 [Main] import.meta.env.VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL)
  console.log('🔍 [Main] window.location.hostname:', window.location.hostname)
  
  // Validar que config.js se haya cargado
  if (!window.__API_BASE_URL__ && !import.meta.env.VITE_API_BASE_URL) {
    console.error('❌ [Main] ADVERTENCIA: No se encontró configuración del API!')
    console.error('❌ [Main] El frontend usará localhost por defecto')
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
      console.log('✅ Configuración del sistema cargada:', configStore.brandName)
    } catch (err) {
      // Ignorar errores de configuración - usar valores por defecto
      console.log('ℹ️ Usando configuración por defecto')
    }
    
  } catch (error) {
    console.error('❌ Error inicializando aplicación:', error)
  }

  // Montar la aplicación
  app.mount('#app')
}

// Configurar notificaciones globales
window.showNotification = (notification) => {
  // Placeholder para sistema de notificaciones
  console.log('🔔 Notification:', notification)
  
  // Aquí se puede integrar con una librería de notificaciones
  // como vue-toastification o similar
}

// Inicializar aplicación
initApp()
