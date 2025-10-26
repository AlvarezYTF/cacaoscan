<template>
  <div class="bg-gradient-to-r from-green-50 to-green-50 px-6 py-4 border-t border-gray-200">
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
            @click="$emit('page-change', currentPage - 1)"
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
              @click="$emit('page-change', page)"
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
            @click="$emit('page-change', currentPage + 1)"
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
        <label class="text-xs sm:text-sm text-gray-700">Mostrar:</label>
        <select 
          :value="itemsPerPage"
          @change="$emit('items-per-page-change', parseInt($event.target.value))"
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

<script>
import { computed } from 'vue';

export default {
  name: 'Pagination',
  props: {
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
      required: true
    },
    showItemsPerPage: {
      type: Boolean,
      default: false
    },
    maxVisiblePages: {
      type: Number,
      default: 5
    }
  },
  computed: {
    startItem() {
      return (this.currentPage - 1) * this.itemsPerPage + 1;
    },
    endItem() {
      return Math.min(this.currentPage * this.itemsPerPage, this.totalItems);
    },
    visiblePages() {
      const pages = [];
      
      if (this.totalPages <= this.maxVisiblePages) {
        // Si hay pocas páginas, mostrar todas
        for (let i = 1; i <= this.totalPages; i++) {
          pages.push(i);
        }
      } else {
        // Lógica para mostrar páginas con separadores
        if (this.currentPage <= 3) {
          // Al inicio
          for (let i = 1; i <= 3; i++) {
            pages.push(i);
          }
        } else if (this.currentPage >= this.totalPages - 2) {
          // Al final
          for (let i = this.totalPages - 2; i <= this.totalPages; i++) {
            pages.push(i);
          }
        } else {
          // En el medio
          for (let i = this.currentPage - 1; i <= this.currentPage + 1; i++) {
            pages.push(i);
          }
        }
      }
      
      return pages;
    },
    showPageSeparator() {
      return this.totalPages > this.maxVisiblePages && 
             (this.currentPage > 3 && this.currentPage < this.totalPages - 2);
    }
  },
  emits: ['page-change', 'items-per-page-change']
};
</script>

<style scoped>
/* Mejoras de responsividad para paginación */
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
  
  /* Ajustar espaciado en móviles */
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
  
  /* Ocultar información de resultados en pantallas muy pequeñas */
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
    font-size: 16px; /* Previene zoom en iOS */
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

.bg-gray-50 {
  animation: slideInFromBottom 0.3s ease-out;
}

/* Responsive para pantallas muy grandes */
@media (min-width: 1280px) {
  .lg\:px-8 {
    padding-left: 2rem;
    padding-right: 2rem;
  }
  
  .lg\:py-6 {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
  }
}

/* Mejoras para orientación landscape en móviles */
@media (max-width: 768px) and (orientation: landscape) {
  .py-3 {
    padding-top: 0.375rem;
    padding-bottom: 0.375rem;
  }
  
  .py-2 {
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
  }
}

/* Estados de carga */
.loading button {
  opacity: 0.6;
  pointer-events: none;
}

/* Mejoras para accesibilidad */
button:focus-visible {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}

/* Estilos para modo oscuro (opcional) */
@media (prefers-color-scheme: dark) {
  .bg-gray-50 {
    background-color: #111827;
  }
  
  .border-gray-100 {
    border-color: #374151;
  }
  
  .text-gray-700 {
    color: #d1d5db;
  }
  
  .bg-white {
    background-color: #1f2937;
  }
  
  .border-gray-300 {
    border-color: #4b5563;
  }
  
  .text-gray-500 {
    color: #9ca3af;
  }
  
  .text-gray-700 {
    color: #d1d5db;
  }
  
  .hover\:bg-gray-50:hover {
    background-color: #1f2937;
  }
  
  .hover\:bg-gray-100:hover {
    background-color: #374151;
  }
}

/* Responsive para diferentes tamaños de botones */
@media (max-width: 640px) {
  .px-2 {
    padding-left: 0.375rem;
    padding-right: 0.375rem;
  }
  
  .px-3 {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
  }
  
  .py-2 {
    padding-top: 0.375rem;
    padding-bottom: 0.375rem;
  }
}

/* Mejoras para navegación por teclado */
button:focus {
  z-index: 10;
  position: relative;
}

/* Estados de hover para botones deshabilitados */
button:disabled:hover {
  transform: none;
  box-shadow: none;
}
</style>
