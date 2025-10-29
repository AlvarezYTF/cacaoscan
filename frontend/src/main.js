import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

// Importar Ionicons
import 'ionicons/components/ion-icon.js'

import App from './App.vue'
import router from './router'

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
    
    // Cargar configuración del sistema
    console.log('🔄 Cargando configuración del sistema...')
    const configLoaded = await configStore.loadAll()
    if (configLoaded) {
      console.log('✅ Configuración del sistema cargada:', configStore.brandName)
    } else {
      console.warn('⚠️ No se pudo cargar la configuración del sistema, usando valores por defecto')
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
