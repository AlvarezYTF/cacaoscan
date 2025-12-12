<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="text-center">
        <svg class="mx-auto h-16 w-16 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Acceso Denegado
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          No tienes permisos para acceder a esta página
        </p>
      </div>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        
        <!-- Mensaje específico según el contexto -->
        <div class="text-center">
          <div class="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728"></path>
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800">{{ getErrorTitle() }}</h3>
                <div class="mt-2 text-sm text-red-700">
                  <p>{{ getErrorMessage() }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Información del usuario actual -->
          <div v-if="authStore.isAuthenticated" class="bg-gray-50 rounded-lg p-4 mb-6">
            <div class="flex items-center justify-center">
              <div class="flex-shrink-0">
                <div class="h-10 w-10 rounded-full bg-green-600 flex items-center justify-center text-white font-medium">
                  {{ authStore.userInitials }}
                </div>
              </div>
              <div class="ml-4 text-left">
                <p class="text-sm font-medium text-gray-900">{{ authStore.userFullName }}</p>
                <p class="text-sm text-gray-500">{{ authStore.user?.email }}</p>
                <p class="text-xs text-gray-400 capitalize">{{ getRoleText(authStore.userRole) }}</p>
              </div>
            </div>
          </div>

          <!-- Sugerencias de acción -->
          <div class="space-y-4">
            <!-- Si no está autenticado -->
            <div v-if="!authStore.isAuthenticated" class="space-y-3">
              <p class="text-gray-600">Necesitas iniciar sesión para acceder a esta página.</p>
              <router-link
                to="/login"
                class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                Iniciar Sesión
              </router-link>
            </div>

            <!-- Si está autenticado pero sin permisos -->
            <div v-else class="space-y-3">
              <!-- Verificación de email -->
              <div v-if="!authStore.isVerified && needsVerification" class="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                <div class="flex">
                  <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                    </svg>
                  </div>
                  <div class="ml-3">
                    <h3 class="text-sm font-medium text-yellow-800">Verificación Requerida</h3>
                    <div class="mt-2 text-sm text-yellow-700">
                      <p>Esta funcionalidad requiere que verifiques tu email.</p>
                    </div>
                    <div class="mt-3">
                      <router-link
                        to="/verificar-email"
                        class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-yellow-800 bg-yellow-100 hover:bg-yellow-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
                      >
                        Verificar Email
                      </router-link>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Redirigir al dashboard apropiado -->
              <div class="space-y-3">
                <p class="text-gray-600">Puedes acceder a las siguientes áreas:</p>
                
                <router-link
                  :to="getRedirectPath()"
                  class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                >
                  <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5a2 2 0 012-2h2a2 2 0 012 2v2H8V5z"></path>
                  </svg>
                  Ir a mi Dashboard
                </router-link>

                <!-- Links adicionales según el rol -->
                <div class="grid grid-cols-1 gap-2">
                  <router-link
                    v-if="authStore.canUploadImages"
                    to="/prediccion"
                    class="flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                  >
                    <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                    Analizar Cacao
                  </router-link>

                  <router-link
                    to="/perfil"
                    class="flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                  >
                    <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                    </svg>
                    Mi Perfil
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Links adicionales -->
      <div class="mt-6 text-center">
        <div class="space-y-2">
          <router-link
            to="/"
            class="text-sm text-green-600 hover:text-green-500"
          >
            ← Volver al Inicio
          </router-link>
          
          <div v-if="authStore.isAuthenticated" class="flex justify-center space-x-4 text-sm">
            <button
              @click="authStore.logout()"
              class="text-gray-500 hover:text-gray-400"
            >
              Cerrar Sesión
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Store y route
const authStore = useAuthStore()
const route = useRoute()

// Computed
const needsVerification = computed(() => {
  return route.query.error === 'verification_required' || 
         route.query.message?.includes('verificar')
})

// Métodos
const getRoleText = (role) => {
  const roleTexts = {
    farmer: 'Agricultor',
    analyst: 'Analista', 
    admin: 'Administrador'
  }
  return roleTexts[role] || 'Usuario'
}

const getRedirectPath = () => {
  if (!authStore.user) return '/'

  switch (authStore.userRole) {
    case 'admin':
      return '/admin/dashboard'
    case 'analyst':
      return '/analisis'
    case 'farmer':
      return '/agricultor-dashboard'
    default:
      return '/'
  }
}

const getErrorTitle = () => {
  const error = route.query.error
  const message = route.query.message

  if (error === 'access_denied') {
    return 'Acceso Restringido'
  } else if (error === 'insufficient_permissions') {
    return 'Permisos Insuficientes'
  } else if (error === 'verification_required') {
    return 'Verificación Requerida'
  } else if (message) {
    return 'Acceso Denegado'
  } else {
    return 'Sin Permisos'
  }
}

const getErrorMessage = () => {
  const error = route.query.error
  const message = route.query.message

  if (message) {
    return message
  }

  switch (error) {
    case 'access_denied':
      return 'No tienes autorización para acceder a esta página. Verifica que tengas el rol correcto.'
    case 'insufficient_permissions':
      return 'Tu cuenta no tiene los permisos necesarios para realizar esta acción.'
    case 'verification_required':
      return 'Debes verificar tu dirección de email para acceder a esta funcionalidad.'
    default:
      if (authStore.isAuthenticated) {
        return 'Tu cuenta no tiene acceso a este recurso. Contacta al administrador si necesitas permisos adicionales.'
      }
      return 'Necesitas iniciar sesión para acceder a esta página.'
  }
}
</script>
