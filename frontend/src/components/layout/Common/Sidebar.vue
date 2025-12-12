<template>
  <aside 
    id="sidebar" 
    :class="[
      'fixed top-0 left-0 z-40 h-screen transition-all duration-300',
      collapsed ? 'w-20' : 'w-64'
    ]"
    aria-label="Sidebar"
  >
    <div class="h-full px-3 py-6 overflow-y-auto bg-gray-50 border-r border-gray-200 shadow-sm">
      <!-- Logo y Branding -->
      <div class="flex items-center justify-between mb-8" :class="collapsed ? 'justify-center' : ''">
        <div class="flex items-center justify-center" :class="collapsed ? 'w-full' : ''">
          <div 
            class="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center shadow-md hover:shadow-lg" 
            :class="collapsed ? 'cursor-pointer hover:bg-green-700 transition-all duration-200' : ''"
            @click="handleLogoClick"
          >
            <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path>
            </svg>
          </div>
          <span v-if="!collapsed" class="ml-3 text-xl font-bold text-gray-900">{{ brandName }}</span>
        </div>
        <!-- Toggle Button -->
        <button 
          v-if="!collapsed"
          @click="toggleCollapse"
          class="p-2 text-gray-500 hover:text-green-700 hover:bg-green-50 rounded-lg transition-all duration-200"
          title="Colapsar menú"
          type="button"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
          </svg>
        </button>
      </div>

      <!-- Navigation Menu -->
      <nav class="space-y-1">
        <div v-for="item in menuItems" :key="item.id">
          <button
            type="button"
            @click="handleMenuClick(item)"
            @keydown="handleKeyboardAction($event, item)"
            @keyup="handleKeyboardAction($event, item)"
            @keypress="handleKeyboardAction($event, item)"
            :class="[
              'flex items-center rounded-lg group transition-all duration-200 cursor-pointer w-full text-left border-0 bg-transparent',
              collapsed ? 'px-2 py-2 justify-center' : 'px-3 py-3',
              getMenuItemClass(item)
            ]"
          >
            <svg 
              :class="['transition-colors duration-200', collapsed ? 'w-5 h-5' : 'w-5 h-5', getIconClass(item)]"
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path :d="item.iconPath" :fill-rule="item.fillRule || 'evenodd'" :clip-rule="item.clipRule || 'evenodd'"></path>
            </svg>
            <span v-if="!collapsed" class="ml-3 flex-1 text-sm font-semibold">{{ item.label }}</span>
            <span v-if="!collapsed && item.badge" class="ml-auto inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold text-white bg-green-600">
              {{ item.badge }}
            </span>
          </button>
        </div>
      </nav>

      <!-- User Section -->
      <div class="absolute bottom-0 left-0 right-0 border-t border-gray-200 bg-white"
           :class="collapsed ? 'p-3' : 'p-5'">
        <div :class="collapsed ? 'flex flex-col items-center space-y-2' : 'flex items-center space-x-3'">
          <div class="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center shadow-md hover:shadow-lg transition-all duration-200">
            <span class="text-sm font-bold text-white">{{ userInitials }}</span>
          </div>
          <div v-if="!collapsed" class="flex-1 min-w-0">
            <p class="text-sm font-bold text-gray-900 truncate">{{ userName }}</p>
            <p class="text-xs text-gray-600 font-medium truncate capitalize">{{ userRole }}</p>
          </div>
          <button 
            @click="handleLogout"
            :class="[
              'p-2.5 text-gray-500 hover:text-white hover:bg-red-600 rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-green-500',
              collapsed ? 'w-full' : ''
            ]"
            :title="collapsed ? 'Cerrar Sesión' : 'Cerrar Sesión'"
            type="button"
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

<script setup>
import { computed } from 'vue'
import { normalizeRole } from '@/utils/roleUtils'

// Props
const props = defineProps({
  brandName: {
    type: String,
    default: 'CacaoScan'
  },
  userName: {
    type: String,
    default: 'Usuario'
  },
  userRole: {
    type: String,
    default: 'admin',
    validator: (value) => ['admin', 'agricultor'].includes(value)
  },
  currentRoute: {
    type: String,
    default: ''
  },
  activeSection: {
    type: String,
    default: 'overview'
  },
  collapsed: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['menu-click', 'logout', 'toggle-collapse'])

// Menu items configuration for both roles
const allMenuItems = {
  admin: [
    {
      id: 'dashboard',
      label: 'Dashboard',
      route: '/admin/dashboard',
      iconPath: 'M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z',
      fillRule: 'evenodd',
      clipRule: 'evenodd',
      roles: ['admin']
    },
    {
      id: 'analisis',
      label: 'Análisis',
      route: '/admin/analisis',
      iconPath: 'M9 2v2h2v10H9v2h6v-2h-2V4h2V2H9z M7 5H2v2h5V5zm0 4H2v2h5V9zm0 4H2v2h5v-2zm13-8h-5v2h5V5zm0 4h-5v2h5V9zm0 4h-5v2h5v-2z',
      fillRule: 'evenodd',
      clipRule: 'evenodd',
      roles: ['admin', 'agricultor']
    },
    {
      id: 'agricultores',
      label: 'Cacaocultores',
      route: '/admin/agricultores',
      iconPath: 'M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z',
      fillRule: 'evenodd',
      clipRule: 'evenodd',
      roles: ['admin']
    },
    {
      id: 'fincas',
      label: 'Fincas',
      route: '/fincas',
      iconPath: 'M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z',
      fillRule: 'evenodd',
      clipRule: 'evenodd',
      roles: ['admin']
    },
    {
      id: 'training',
      label: 'Entrenamiento',
      route: '/admin/entrenamiento',
      iconPath: 'M9 2a1 1 0 000 2h2a1 1 0 100-2H9z M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z',
      fillRule: 'evenodd',
      clipRule: 'evenodd',
      roles: ['admin']
    },
    {
      id: 'configuracion',
      label: 'Configuración',
      route: '/admin/configuracion',
      iconPath: 'M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z',
      fillRule: 'evenodd',
      clipRule: 'evenodd',
      roles: ['admin', 'agricultor']
    }
  ],
  agricultor: [
    {
      id: 'overview',
      label: 'Resumen',
      route: '/agricultor-dashboard',
      iconPath: 'M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z',
      roles: ['agricultor']
    },
    {
      id: 'analysis',
      label: 'Análisis',
      route: '/analisis',
      iconPath: 'M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z',
      roles: ['agricultor']
    },
    {
      id: 'fincas',
      label: 'Fincas',
      route: '/fincas',
      iconPath: 'M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z',
      roles: ['agricultor']
    },
    {
      id: 'reports',
      label: 'Reportes',
      route: '/agricultor/reportes',
      iconPath: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
      roles: ['agricultor']
    },
    {
      id: 'history',
      label: 'Historial',
      route: '/agricultor/historial',
      iconPath: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
      roles: ['agricultor']
    },
    {
      id: 'settings',
      label: 'Configuración',
      route: '/agricultor/configuracion',
      iconPath: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z',
      roles: ['agricultor']
    }
  ]
}

// Computed properties
const menuItems = computed(() => {
  // Normalize role: convert 'farmer' to 'agricultor' for menu lookup
  let normalizedRole = normalizeRole(props.userRole) || 'agricultor'
  // Convert 'farmer' to 'agricultor' for menu items lookup
  if (normalizedRole === 'farmer') {
    normalizedRole = 'agricultor'
  }
  return allMenuItems[normalizedRole] || []
})

const userInitials = computed(() => {
  const names = props.userName.split(' ')
  return names.map(name => name.charAt(0)).join('').toUpperCase()
})

// Methods
// Base function to check if menu item is active (extracted common logic)
const isMenuItemActive = (item) => {
  if (props.userRole === 'admin') {
    // For admin role, check route
    return props.currentRoute === item.route || 
           (item.route !== '/admin/dashboard' && props.currentRoute.startsWith(item.route))
  } else {
    // For agricultor role, check activeSection
    return props.activeSection === item.id
  }
}

const getMenuItemClass = (item) => {
  const isActive = isMenuItemActive(item)
  
  if (isActive) {
    return 'text-green-700 bg-green-100 border-r-3 border-green-600 shadow-sm'
  }
  
  return 'text-gray-700 hover:bg-green-50 hover:text-green-700'
}

const getIconClass = (item) => {
  const isActive = isMenuItemActive(item)
  
  if (isActive) {
    return 'text-green-700'
  }
  
  return 'text-gray-500 group-hover:text-green-600'
}

const toggleCollapse = () => {
  emit('toggle-collapse')
}

const handleLogoClick = () => {
  if (props.collapsed) {
    emit('toggle-collapse')
  }
}

const handleMenuClick = (item) => {
  emit('menu-click', item)
}

const handleKeyboardAction = (event, item) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    handleMenuClick(item)
  }
}

const handleLogout = () => {
  emit('logout')
}
</script>

<style scoped>
/* Estilos específicos para el sidebar con tema verde de CacaoScan */
#sidebar {
  box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.06), 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* Animación suave para los elementos del menú */
.group:hover .group-hover\:text-gray-700 {
  transition: all 0.2s ease-in-out;
}

/* Estilo para elementos activos */
.router-link-active {
  background-color: #dcfce7;
  border-right: 3px solid #16a34a;
  color: #15803d;
  box-shadow: inset 2px 0 0 0 rgba(34, 197, 94, 0.1);
}

/* Border personalizado para items activos */
.border-r-3 {
  border-right-width: 3px;
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

/* Mejoras de accesibilidad */
button:focus-visible {
  outline: 2px solid #16a34a;
  outline-offset: 2px;
  outline-style: solid;
}

/* Transiciones suaves y corporativas */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* Efectos hover mejorados con tema verde */
.hover\:bg-green-50:hover {
  background-color: #f0fdf4;
}

.hover\:text-green-700:hover {
  color: #15803d;
}
</style>
