<template>
  <aside 
    id="sidebar" 
    class="fixed top-0 left-0 z-40 w-64 h-screen transition-transform -translate-x-full sm:translate-x-0" 
    aria-label="Sidebar"
  >
    <div class="h-full px-3 py-4 overflow-y-auto bg-white border-r border-gray-200">
      <!-- Logo y Branding -->
      <div class="flex items-center pl-2.5 mb-5">
        <svg class="w-8 h-8 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path>
        </svg>
        <span class="ml-2 text-xl font-semibold text-gray-800">{{ brandName }}</span>
      </div>

      <!-- Navigation Menu -->
      <ul class="space-y-2 font-medium">
        <li v-for="item in menuItems" :key="item.id">
          <router-link 
            :to="item.route" 
            class="flex items-center p-2 rounded-lg group transition-colors duration-200"
            :class="getMenuItemClass(item)"
            @click="handleMenuClick(item)"
          >
            <svg 
              class="w-5 h-5 transition duration-75" 
              :class="getIconClass(item)"
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path :d="item.iconPath" :fill-rule="item.fillRule" :clip-rule="item.clipRule"></path>
            </svg>
            <span class="ml-3">{{ item.label }}</span>
            <span v-if="item.badge" class="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
              {{ item.badge }}
            </span>
          </router-link>
        </li>
      </ul>

      <!-- User Section -->
      <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-white">
        <div class="flex items-center space-x-3">
          <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <span class="text-sm font-medium text-white">{{ userInitials }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 truncate">{{ userName }}</p>
            <p class="text-xs text-gray-500 truncate">{{ userRole }}</p>
          </div>
          <button 
            @click="handleLogout"
            class="p-1 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
            title="Cerrar Sesión"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </aside>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'AdminSidebar',
  props: {
    brandName: {
      type: String,
      default: 'CacaoScan'
    },
    userName: {
      type: String,
      default: 'Admin User'
    },
    userRole: {
      type: String,
      default: 'Administrador'
    },
    currentRoute: {
      type: String,
      default: ''
    }
  },
  emits: ['menu-click', 'logout'],
  setup(props, { emit }) {
    const router = useRouter()

    // Menu items configuration
    const menuItems = [
      {
        id: 'dashboard',
        label: 'Dashboard',
        route: '/admin/dashboard',
        iconPath: 'M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z',
        fillRule: 'evenodd',
        clipRule: 'evenodd'
      },
      {
        id: 'users',
        label: 'Usuarios',
        route: '/admin/users',
        iconPath: 'M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z',
        badge: null
      },
      {
        id: 'analysis',
        label: 'Análisis',
        route: '/admin/analysis',
        iconPath: 'M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z',
        fillRule: 'evenodd',
        clipRule: 'evenodd'
      },
      {
        id: 'reports',
        label: 'Reportes',
        route: '/admin/reports',
        iconPath: 'M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z',
        fillRule: 'evenodd',
        clipRule: 'evenodd',
        badge: '3'
      },
      {
        id: 'settings',
        label: 'Configuración',
        route: '/admin/settings',
        iconPath: 'M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-2 0c0 .993-.241 1.929-.668 2.754l-1.524-1.525a3.997 3.997 0 00.078-2.183l1.562-1.562C15.759 8.241 16 9.007 16 10zm-5.165 3.913l1.58 1.58A5.98 5.98 0 0110 16a5.976 5.976 0 01-2.516-.552l1.562-1.562a4.006 4.006 0 001.789.027zm-4.677-2.796a4.002 4.002 0 01-.041-2.08l-.08.08a4 4 0 00.08 2.08zm1.523 1.523a3.99 3.99 0 01-.027-1.789l1.562-1.562A5.98 5.98 0 0110 4a5.976 5.976 0 01.552 2.516l-1.562 1.562a4.006 4.006 0 00-.027 1.789z',
        fillRule: 'evenodd',
        clipRule: 'evenodd'
      }
    ]

    // Computed properties
    const userInitials = computed(() => {
      const names = props.userName.split(' ')
      return names.map(name => name.charAt(0)).join('').toUpperCase()
    })

    // Methods
    const getMenuItemClass = (item) => {
      const isActive = props.currentRoute === item.route || 
                      (item.route !== '/admin/dashboard' && props.currentRoute.startsWith(item.route))
      
      if (isActive) {
        return 'text-gray-900 bg-blue-50'
      }
      return 'text-gray-600 hover:bg-gray-100'
    }

    const getIconClass = (item) => {
      const isActive = props.currentRoute === item.route || 
                      (item.route !== '/admin/dashboard' && props.currentRoute.startsWith(item.route))
      
      if (isActive) {
        return 'text-blue-600'
      }
      return 'text-gray-500 group-hover:text-gray-900'
    }

    const handleMenuClick = (item) => {
      emit('menu-click', item)
    }

    const handleLogout = () => {
      emit('logout')
    }

    return {
      menuItems,
      userInitials,
      getMenuItemClass,
      getIconClass,
      handleMenuClick,
      handleLogout
    }
  }
}
</script>

<style scoped>
/* Estilos específicos para el sidebar */
#sidebar {
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

/* Animación suave para los elementos del menú */
.group:hover .group-hover\:text-gray-900 {
  transition: color 0.2s ease-in-out;
}

/* Responsive behavior */
@media (max-width: 640px) {
  #sidebar {
    transform: translateX(-100%);
  }
  
  #sidebar.show {
    transform: translateX(0);
  }
}
</style>
