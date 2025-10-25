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
        id: 'agricultores',
        label: 'Agricultores',
        route: '/admin/agricultores',
        iconPath: 'M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z',
        fillRule: 'evenodd',
        clipRule: 'evenodd'
      },
      {
        id: 'dataset',
        label: 'Dataset',
        route: '/admin/dataset',
        iconPath: 'M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z',
        fillRule: 'evenodd',
        clipRule: 'evenodd'
      },
      {
        id: 'training',
        label: 'Entrenamiento',
        route: '/admin/training',
        iconPath: 'M9 2a1 1 0 000 2h2a1 1 0 100-2H9z M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z',
        fillRule: 'evenodd',
        clipRule: 'evenodd'
      },
      {
        id: 'configuracion',
        label: 'Configuración',
        route: '/admin/configuracion',
        iconPath: 'M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z',
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
