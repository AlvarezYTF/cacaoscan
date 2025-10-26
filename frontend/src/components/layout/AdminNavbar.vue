<template>
  <div class="p-4 sm:ml-64">
    <div class="p-6 border border-gray-200 rounded-lg bg-white shadow-sm mb-6">
      <div class="flex items-center justify-between">
        <!-- Header Info -->
        <div>
          <h1 class="text-2xl font-bold text-gray-900">{{ title }}</h1>
          <p class="text-gray-600 mt-1">{{ subtitle }}</p>
        </div>
        
        <!-- Actions Section -->
        <div class="flex items-center space-x-4">
          <!-- Search Input -->
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"></path>
              </svg>
            </div>
            <input 
              type="text" 
              v-model="searchQuery"
              @input="handleSearch"
              class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-green-500 focus:border-green-500 block w-80 pl-10 p-2.5 transition-colors duration-200" 
              :placeholder="searchPlaceholder"
            >
          </div>
          
          <!-- Period Selector -->
          <select 
            v-model="selectedPeriod" 
            @change="handlePeriodChange" 
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-green-500 focus:border-green-500 block p-2.5 transition-colors duration-200"
          >
            <option value="7">Últimos 7 días</option>
            <option value="30">Últimos 30 días</option>
            <option value="90">Últimos 90 días</option>
          </select>
          
          <!-- Refresh Button -->
          <button 
            @click="handleRefresh"
            :disabled="loading"
            class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
          >
            <svg class="w-4 h-4 mr-2" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            {{ refreshButtonText }}
          </button>
          
          <!-- User Avatar -->
          <div class="flex items-center ml-3">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                <span class="text-sm font-semibold text-white">{{ userInitials }}</span>
              </div>
              <div class="hidden md:block">
                <p class="text-sm font-semibold text-gray-900">{{ userName }}</p>
                <p class="text-xs text-gray-600">{{ userRole }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, ref, watch } from 'vue'

export default {
  name: 'AdminNavbar',
  props: {
    title: {
      type: String,
      default: 'Dashboard de Administración'
    },
    subtitle: {
      type: String,
      default: 'Panel de control completo del sistema CacaoScan'
    },
    userName: {
      type: String,
      default: 'Admin User'
    },
    userRole: {
      type: String,
      default: 'Administrador'
    },
    searchPlaceholder: {
      type: String,
      default: 'Buscar...'
    },
    refreshButtonText: {
      type: String,
      default: 'Actualizar'
    },
    loading: {
      type: Boolean,
      default: false
    },
    initialPeriod: {
      type: String,
      default: '30'
    },
    initialSearchQuery: {
      type: String,
      default: ''
    }
  },
  emits: ['search', 'period-change', 'refresh', 'search-clear'],
  setup(props, { emit }) {
    // Reactive data
    const searchQuery = ref(props.initialSearchQuery)
    const selectedPeriod = ref(props.initialPeriod)

    // Computed properties
    const userInitials = computed(() => {
      const names = props.userName.split(' ')
      return names.map(name => name.charAt(0)).join('').toUpperCase()
    })

    // Methods
    const handleSearch = () => {
      emit('search', searchQuery.value)
    }

    const handlePeriodChange = () => {
      emit('period-change', selectedPeriod.value)
    }

    const handleRefresh = () => {
      emit('refresh')
    }

    // Watch for prop changes
    watch(() => props.initialSearchQuery, (newValue) => {
      searchQuery.value = newValue
    })

    watch(() => props.initialPeriod, (newValue) => {
      selectedPeriod.value = newValue
    })

    return {
      searchQuery,
      selectedPeriod,
      userInitials,
      handleSearch,
      handlePeriodChange,
      handleRefresh
    }
  }
}
</script>

<style scoped>
/* Estilos específicos para el navbar */
.search-input:focus {
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .search-input {
    width: 200px;
  }
}

@media (max-width: 768px) {
  .search-input {
    width: 150px;
  }
}

@media (max-width: 640px) {
  .search-input {
    width: 120px;
  }
}

/* Animation for loading spinner */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Mejoras de accesibilidad */
button:focus-visible {
  outline: 2px solid rgb(34 197 94);
  outline-offset: 2px;
}

/* Transiciones suaves */
.transition-colors {
  transition-property: color, background-color, border-color, text-decoration-color, fill, stroke;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}
</style>
