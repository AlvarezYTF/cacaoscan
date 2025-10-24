<template>
  <nav class="bg-white shadow-lg border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- Logo y navegación principal -->
        <div class="flex items-center">
          <!-- Logo -->
          <router-link to="/" class="flex-shrink-0 flex items-center">
            <img
              class="h-8 w-auto"
              src="@/assets/Logos/logo-cacaoscan.png"
              alt="CacaoScan"
            />
            <span class="ml-2 text-xl font-bold text-green-600">CacaoScan</span>
          </router-link>

          <!-- Navegación principal (desktop) -->
          <div class="hidden md:ml-6 md:flex md:space-x-8">
            <!-- Links públicos -->
            <router-link
              v-if="!authStore.isAuthenticated"
              to="/"
              class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              active-class="border-green-500 text-gray-900"
            >
              Inicio
            </router-link>

            <!-- Links para usuarios autenticados -->
            <template v-if="authStore.isAuthenticated">
              <!-- Dashboard según rol -->
              <router-link
                v-if="authStore.isFarmer"
                to="/agricultor-dashboard"
                class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                active-class="border-green-500 text-gray-900"
              >
                Mi Dashboard
              </router-link>
              
              <router-link
                v-if="authStore.isAnalyst"
                to="/analisis"
                class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                active-class="border-green-500 text-gray-900"
              >
                Análisis
              </router-link>
              
              <router-link
                v-if="authStore.isAdmin"
                to="/admin/dashboard"
                class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                active-class="border-green-500 text-gray-900"
              >
                Administración
              </router-link>

              <!-- Predicción (farmers y admins verificados) -->
              <router-link
                v-if="authStore.canUploadImages"
                to="/prediccion"
                class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                active-class="border-green-500 text-gray-900"
              >
                <svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Analizar Cacao
              </router-link>

              <!-- Reportes (analysts y admins) -->
              <router-link
                v-if="authStore.canViewAllPredictions"
                to="/reportes"
                class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                active-class="border-green-500 text-gray-900"
              >
                <svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Reportes
              </router-link>
            </template>
          </div>
        </div>

        <!-- Menu de usuario -->
        <div class="flex items-center">
          <!-- Usuario no autenticado -->
          <div v-if="!authStore.isAuthenticated" class="flex items-center space-x-4">
            <router-link
              to="/login"
              class="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium"
            >
              Iniciar Sesión
            </router-link>
            <router-link
              to="/registro"
              class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Registrarse
            </router-link>
          </div>

          <!-- Usuario autenticado -->
          <div v-else class="flex items-center space-x-4">
            <!-- Indicator de verificación -->
            <div v-if="!authStore.isVerified" class="flex items-center">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                <svg class="mr-1 h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                No verificado
              </span>
            </div>

            <!-- Notificaciones (placeholder) -->
            <button class="p-1 rounded-full text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
              <span class="sr-only">Ver notificaciones</span>
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5v-5zM10 6V4a2 2 0 00-2-2H6a2 2 0 00-2 2v2m16 8a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>

            <!-- Dropdown de usuario -->
            <div class="relative" ref="userMenuRef">
              <button
                @click="showUserMenu = !showUserMenu"
                class="bg-white flex text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                id="user-menu-button"
                aria-expanded="false"
                aria-haspopup="true"
              >
                <span class="sr-only">Abrir menú de usuario</span>
                <div class="h-8 w-8 rounded-full bg-green-600 flex items-center justify-center text-white text-sm font-medium">
                  {{ authStore.userInitials }}
                </div>
              </button>

              <!-- Dropdown menu -->
              <transition
                enter-active-class="transition ease-out duration-200"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <div
                  v-show="showUserMenu"
                  class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50"
                  role="menu"
                  aria-orientation="vertical"
                  aria-labelledby="user-menu-button"
                  tabindex="-1"
                >
                  <!-- Info del usuario -->
                  <div class="px-4 py-2 border-b border-gray-100">
                    <p class="text-sm font-medium text-gray-900">{{ authStore.userFullName }}</p>
                    <p class="text-sm text-gray-500">{{ authStore.user?.email }}</p>
                    <p class="text-xs text-gray-400 capitalize">{{ getRoleText(authStore.userRole) }}</p>
                  </div>

                  <!-- Menu items -->
                  <router-link
                    to="/perfil"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    role="menuitem"
                    @click="showUserMenu = false"
                  >
                    <svg class="inline mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    Mi Perfil
                  </router-link>

                  <router-link
                    v-if="!authStore.isVerified"
                    to="/verificar-email"
                    class="block px-4 py-2 text-sm text-yellow-700 hover:bg-yellow-50"
                    role="menuitem"
                    @click="showUserMenu = false"
                  >
                    <svg class="inline mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    Verificar Email
                  </router-link>

                  <div class="border-t border-gray-100"></div>
                  
                  <button
                    @click="handleLogout"
                    class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    role="menuitem"
                  >
                    <svg class="inline mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    Cerrar Sesión
                  </button>
                </div>
              </transition>
            </div>
          </div>

          <!-- Mobile menu button -->
          <div class="md:hidden">
            <button
              @click="showMobileMenu = !showMobileMenu"
              type="button"
              class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-green-500"
              aria-controls="mobile-menu"
              aria-expanded="false"
            >
              <span class="sr-only">Abrir menú principal</span>
              <svg
                v-if="!showMobileMenu"
                class="block h-6 w-6"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              <svg
                v-else
                class="block h-6 w-6"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile menu -->
    <div v-show="showMobileMenu" class="md:hidden" id="mobile-menu">
      <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3 border-t border-gray-200">
        <!-- Links móviles -->
        <template v-if="authStore.isAuthenticated">
          <router-link
            v-if="authStore.isFarmer"
            to="/agricultor-dashboard"
            class="text-gray-500 hover:text-gray-700 block px-3 py-2 rounded-md text-base font-medium"
            @click="showMobileMenu = false"
          >
            Mi Dashboard
          </router-link>
          
          <router-link
            v-if="authStore.canUploadImages"
            to="/prediccion"
            class="text-gray-500 hover:text-gray-700 block px-3 py-2 rounded-md text-base font-medium"
            @click="showMobileMenu = false"
          >
            Analizar Cacao
          </router-link>
          
          <router-link
            v-if="authStore.canViewAllPredictions"
            to="/reportes"
            class="text-gray-500 hover:text-gray-700 block px-3 py-2 rounded-md text-base font-medium"
            @click="showMobileMenu = false"
          >
            Reportes
          </router-link>
        </template>
        
        <template v-else>
          <router-link
            to="/login"
            class="text-gray-500 hover:text-gray-700 block px-3 py-2 rounded-md text-base font-medium"
            @click="showMobileMenu = false"
          >
            Iniciar Sesión
          </router-link>
          
          <router-link
            to="/registro"
            class="bg-green-600 text-white block px-3 py-2 rounded-md text-base font-medium"
            @click="showMobileMenu = false"
          >
            Registrarse
          </router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

// Store de autenticación
const authStore = useAuthStore()

// Estado del componente
const showUserMenu = ref(false)
const showMobileMenu = ref(false)
const userMenuRef = ref(null)

// Función para obtener texto del rol
const getRoleText = (role) => {
  const roleTexts = {
    farmer: 'Agricultor',
    analyst: 'Analista',
    admin: 'Administrador'
  }
  return roleTexts[role] || 'Usuario'
}

// Manejar logout
const handleLogout = async () => {
  showUserMenu.value = false
  await authStore.logout()
}

// Manejar clics fuera del menu de usuario
const handleClickOutside = (event) => {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target)) {
    showUserMenu.value = false
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
@reference "tailwindcss";

/* Estilos adicionales si son necesarios */
.router-link-active {
  @apply border-green-500 text-gray-900;
}
</style>
