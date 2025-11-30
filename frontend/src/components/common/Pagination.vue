<template>
  <div v-if="totalPages > 1" class="bg-gradient-to-r from-green-50 to-green-50 px-6 py-4 border-t border-gray-200">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
      <!-- Información de resultados -->
      <div class="flex justify-center sm:justify-start">
        <p class="text-sm font-medium text-gray-600">
          Mostrando <span class="font-bold text-gray-900">{{ startItem }}</span> a <span class="font-bold text-gray-900">{{ endItem }}</span> de <span class="font-bold text-gray-900">{{ totalItems }}</span> resultados
        </p>
      </div>
      
      <!-- Navegación de paginación -->
      <div class="flex justify-center sm:justify-end">
        <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
          <!-- Botón Anterior -->
          <button 
            @click="goToPage(currentPage - 1)"
            :disabled="currentPage === 1"
            class="relative inline-flex items-center px-4 py-2 rounded-l-lg border border-gray-300 bg-white text-sm font-semibold text-gray-700 hover:bg-green-50 hover:text-green-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            :class="{ 'hover:bg-green-100': currentPage !== 1 }"
          >
            <span class="sr-only">Anterior</span>
            <svg class="h-3 w-3 sm:h-4 sm:w-4 md:h-5 md:w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </button>
          
          <!-- Números de página -->
          <template v-for="page in visiblePages" :key="page">
            <!-- Página actual -->
            <button 
              v-if="page === currentPage"
              class="relative inline-flex items-center px-4 py-2 border-2 border-green-500 bg-green-100 text-sm font-bold text-green-700 shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              {{ page }}
            </button>
            
            <!-- Otras páginas -->
            <button 
              v-else
              @click="goToPage(page)"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-semibold text-gray-700 hover:bg-green-50 hover:text-green-700 hover:border-green-300 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              {{ page }}
            </button>
          </template>
          
          <!-- Separador de páginas -->
          <span v-if="showPageSeparator" class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-400">
            ...
          </span>
          
          <!-- Botón Siguiente -->
          <button 
            @click="goToPage(currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="relative inline-flex items-center px-4 py-2 rounded-r-lg border border-gray-300 bg-white text-sm font-semibold text-gray-700 hover:bg-green-50 hover:text-green-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            :class="{ 'hover:bg-green-100': currentPage !== totalPages }"
          >
            <span class="sr-only">Siguiente</span>
            <svg class="h-3 w-3 sm:h-4 sm:w-4 md:h-5 md:w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
          </button>
        </nav>
      </div>
      
      <!-- Selector de elementos por página (opcional) -->
      <div v-if="showItemsPerPage" class="flex items-center space-x-2">
        <label for="pagination-items-per-page" class="text-xs sm:text-sm text-gray-700">Mostrar:</label>
        <select 
          id="pagination-items-per-page"
          :value="itemsPerPage"
          @change="handleItemsPerPageChange(Number.parseInt($event.target.value))"
          class="text-xs sm:text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-green-500"
        >
          <option value="5">5</option>
          <option value="10">10</option>
          <option value="20">20</option>
          <option value="50">50</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import { usePagination } from '@/composables/usePagination'

const props = defineProps({
  currentPage: {
    type: Number,
    required: true
  },
  totalPages: {
    type: Number,
    required: true
  },
  totalItems: {
    type: Number,
    required: true
  },
  itemsPerPage: {
    type: Number,
    default: 10
  },
  showItemsPerPage: {
    type: Boolean,
    default: false
  },
  maxVisiblePages: {
    type: Number,
    default: 5
  }
})

const emit = defineEmits(['page-change', 'items-per-page-change'])

// Use pagination composable for computed values
const pagination = usePagination({
  initialPage: props.currentPage,
  initialItemsPerPage: props.itemsPerPage,
  maxVisiblePages: props.maxVisiblePages
})

// Sync composable state with props
watch(() => props.currentPage, (newPage) => {
  if (newPage !== pagination.currentPage.value) {
    pagination.goToPage(newPage)
  }
}, { immediate: true })

watch(() => props.totalItems, (newTotal) => {
  pagination.setTotalItems(newTotal)
}, { immediate: true })

watch(() => props.itemsPerPage, (newSize) => {
  if (newSize !== pagination.itemsPerPage.value) {
    pagination.setItemsPerPage(newSize)
  }
}, { immediate: true })

// Use computed values from composable, but override visiblePages to use props.totalPages
const startItem = computed(() => {
  return (props.currentPage - 1) * props.itemsPerPage + 1
})

const endItem = computed(() => {
  return Math.min(props.currentPage * props.itemsPerPage, props.totalItems)
})

const visiblePages = computed(() => {
  const pages = []
  
  if (props.totalPages <= props.maxVisiblePages) {
    for (let i = 1; i <= props.totalPages; i++) {
      pages.push(i)
    }
  } else if (props.currentPage <= 3) {
    for (let i = 1; i <= 3; i++) {
      pages.push(i)
    }
  } else if (props.currentPage >= props.totalPages - 2) {
    for (let i = props.totalPages - 2; i <= props.totalPages; i++) {
      pages.push(i)
    }
  } else {
    for (let i = props.currentPage - 1; i <= props.currentPage + 1; i++) {
      pages.push(i)
    }
  }
  
  return pages
})

const showPageSeparator = computed(() => {
  return props.totalPages > props.maxVisiblePages && 
         (props.currentPage > 3 && props.currentPage < props.totalPages - 2)
})

// Methods
const goToPage = (page) => {
  if (page >= 1 && page <= props.totalPages && page !== props.currentPage) {
    emit('page-change', page)
  }
}

const handleItemsPerPageChange = (newSize) => {
  emit('items-per-page-change', newSize)
}
</script>

<style scoped>
/* Responsive adjustments */
@media (max-width: 768px) {
  .md\:px-6 {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .md\:py-4 {
    padding-top: 0.75rem;
    padding-bottom: 0.75rem;
  }
  
  .text-xs {
    font-size: 0.75rem;
    line-height: 1rem;
  }
}

@media (max-width: 640px) {
  .px-3 {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
  }
  
  .py-3 {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }
  
  .text-xs {
    font-size: 0.75rem;
    line-height: 1rem;
  }
  
  .space-y-3 > * + * {
    margin-top: 0.5rem;
  }
}

@media (max-width: 480px) {
  .px-3 {
    padding-left: 0.375rem;
    padding-right: 0.375rem;
  }
  
  .py-3 {
    padding-top: 0.375rem;
    padding-bottom: 0.375rem;
  }
  
  .text-xs {
    font-size: 0.75rem;
    line-height: 1rem;
  }
}

/* Transiciones suaves */
* {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* Mejoras para dispositivos táctiles */
@media (hover: none) and (pointer: coarse) {
  button {
    min-height: 44px;
    min-width: 44px;
  }
  
  select {
    min-height: 44px;
    font-size: 16px;
  }
}

/* Efectos de hover mejorados */
button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.1);
}

button:focus:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

/* Animación de entrada */
@keyframes slideInFromBottom {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.bg-gradient-to-r {
  animation: slideInFromBottom 0.3s ease-out;
}

/* Mejoras para accesibilidad */
button:focus-visible {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}

/* Estados de hover para botones deshabilitados */
button:disabled:hover {
  transform: none;
  box-shadow: none;
}
</style>
