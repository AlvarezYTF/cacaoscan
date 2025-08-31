<template>
  <div>
    <!-- Mostrar contenido si pasa las validaciones -->
    <slot v-if="hasAccess" />
    
    <!-- Mensaje de acceso denegado -->
    <div v-else-if="showDeniedMessage" class="auth-guard-denied">
      <div class="bg-yellow-50 border border-yellow-200 rounded-md p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-yellow-800">Acceso Restringido</h3>
            <div class="mt-2 text-sm text-yellow-700">
              <p>{{ getDeniedMessage() }}</p>
            </div>
            <div v-if="showActions" class="mt-4">
              <div class="flex space-x-2">
                <router-link
                  v-if="!authStore.isAuthenticated"
                  to="/login"
                  class="bg-yellow-100 hover:bg-yellow-200 text-yellow-800 px-3 py-1 rounded text-sm font-medium"
                >
                  Iniciar Sesión
                </router-link>
                <router-link
                  v-else-if="!authStore.isVerified && requiresVerification"
                  to="/verificar-email"
                  class="bg-yellow-100 hover:bg-yellow-200 text-yellow-800 px-3 py-1 rounded text-sm font-medium"
                >
                  Verificar Email
                </router-link>
                <router-link
                  v-if="authStore.isAuthenticated"
                  to="/perfil"
                  class="bg-gray-100 hover:bg-gray-200 text-gray-800 px-3 py-1 rounded text-sm font-medium"
                >
                  Ver Perfil
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Loading state mientras verifica -->
    <div v-else-if="isLoading" class="auth-guard-loading">
      <div class="flex items-center justify-center p-4">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
        <span class="ml-2 text-gray-600">Verificando permisos...</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

// Props
const props = defineProps({
  // Requiere autenticación
  requireAuth: {
    type: Boolean,
    default: false
  },
  
  // Roles permitidos
  allowedRoles: {
    type: Array,
    default: () => []
  },
  
  // Requiere verificación de email
  requiresVerification: {
    type: Boolean,
    default: false
  },
  
  // Permisos específicos requeridos
  requiredPermissions: {
    type: Array,
    default: () => []
  },
  
  // Mostrar mensaje de acceso denegado
  showDeniedMessage: {
    type: Boolean,
    default: true
  },
  
  // Mostrar acciones en mensaje denegado
  showActions: {
    type: Boolean,
    default: true
  },
  
  // Mensaje personalizado de acceso denegado
  deniedMessage: {
    type: String,
    default: ''
  },
  
  // Redireccionar en lugar de mostrar mensaje
  redirectOnDenied: {
    type: String,
    default: ''
  },
  
  // Función personalizada de validación
  customValidator: {
    type: Function,
    default: null
  }
})

// Store y estado
const authStore = useAuthStore()
const isLoading = ref(true)

// Computed
const hasAccess = computed(() => {
  if (isLoading.value) return false
  
  // Validación de autenticación
  if (props.requireAuth && !authStore.isAuthenticated) {
    return false
  }
  
  // Validación de roles
  if (props.allowedRoles.length > 0) {
    if (!authStore.isAuthenticated || !props.allowedRoles.includes(authStore.userRole)) {
      return false
    }
  }
  
  // Validación de verificación
  if (props.requiresVerification && !authStore.isVerified) {
    return false
  }
  
  // Validación de permisos específicos
  if (props.requiredPermissions.length > 0) {
    const hasAllPermissions = props.requiredPermissions.every(permission => {
      switch (permission) {
        case 'upload_images':
          return authStore.canUploadImages
        case 'view_all_predictions':
          return authStore.canViewAllPredictions
        case 'manage_users':
          return authStore.isAdmin
        case 'view_analytics':
          return authStore.canViewAllPredictions
        case 'manage_system':
          return authStore.isAdmin
        default:
          return false
      }
    })
    
    if (!hasAllPermissions) {
      return false
    }
  }
  
  // Validación personalizada
  if (props.customValidator) {
    try {
      return props.customValidator(authStore)
    } catch (error) {
      console.error('Error en validación personalizada:', error)
      return false
    }
  }
  
  return true
})

// Métodos
const getDeniedMessage = () => {
  if (props.deniedMessage) {
    return props.deniedMessage
  }
  
  if (!authStore.isAuthenticated) {
    return 'Debes iniciar sesión para acceder a esta funcionalidad.'
  }
  
  if (props.allowedRoles.length > 0 && !props.allowedRoles.includes(authStore.userRole)) {
    const roleTexts = {
      farmer: 'agricultor',
      analyst: 'analista', 
      admin: 'administrador'
    }
    const allowedText = props.allowedRoles.map(role => roleTexts[role]).join(', ')
    return `Esta funcionalidad está disponible solo para usuarios: ${allowedText}.`
  }
  
  if (props.requiresVerification && !authStore.isVerified) {
    return 'Debes verificar tu dirección de email para acceder a esta funcionalidad.'
  }
  
  if (props.requiredPermissions.length > 0) {
    return 'No tienes los permisos necesarios para acceder a esta funcionalidad.'
  }
  
  return 'No tienes acceso a esta funcionalidad.'
}

// Lifecycle
onMounted(async () => {
  try {
    // Asegurar que el usuario esté cargado
    if (authStore.isAuthenticated && !authStore.user) {
      await authStore.getCurrentUser()
    }
  } catch (error) {
    console.error('Error verificando usuario:', error)
  } finally {
    isLoading.value = false
    
    // Redireccionar si es necesario
    if (!hasAccess.value && props.redirectOnDenied) {
      import('@/router').then(({ default: router }) => {
        router.push(props.redirectOnDenied)
      })
    }
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

.auth-guard-denied,
.auth-guard-loading {
  min-height: 80px;
  display: flex;
  align-items: center;
}
</style>
