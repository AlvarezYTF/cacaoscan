<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-all duration-300">
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
            <th scope="col" class="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Agricultor</th>
            <th scope="col" class="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lote</th>
            <th scope="col" class="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
            <th scope="col" class="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Resultado</th>
            <th scope="col" class="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Calidad</th>
            <th scope="col" class="px-3 md:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr 
            v-for="(analysis, index) in analyses" 
            :key="analysis.id || index"
            class="hover:bg-gray-50 transition-all duration-200"
          >
            <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
              <div class="text-xs md:text-sm text-gray-900">{{ analysis.id }}</div>
            </td>
            <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 font-medium text-xs md:text-sm">
                  {{ analysis.farmerInitials }}
                </div>
                <div class="ml-3">
                  <div class="text-xs md:text-sm font-medium text-gray-900">{{ analysis.farmerName }}</div>
                </div>
              </div>
            </td>
            <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
              <div class="text-xs md:text-sm text-gray-900">{{ analysis.batch }}</div>
            </td>
            <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
              <div class="text-xs md:text-sm text-gray-900">{{ analysis.date }}</div>
            </td>
            <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
              <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full" :class="getStatusClasses(analysis.status)">
                {{ analysis.status }}
              </span>
            </td>
            <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="w-16 bg-gray-200 rounded-full h-2.5">
                  <div class="h-2.5 rounded-full" :class="getQualityColor(analysis.quality)" :style="{ width: analysis.quality + '%' }"></div>
                </div>
                <span class="ml-2 text-xs md:text-sm text-gray-900">{{ analysis.quality }}%</span>
              </div>
            </td>
            <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap text-right text-xs md:text-sm font-medium">
              <a href="#" class="text-green-600 hover:text-green-900 mr-3 transition-colors duration-200">Ver</a>
              <a href="#" class="text-blue-600 hover:text-blue-900 mr-3 transition-colors duration-200">Editar</a>
              <a href="#" class="text-red-600 hover:text-red-900 transition-colors duration-200">Eliminar</a>
            </td>
          </tr>
          
          <!-- Fila vacía cuando no hay datos -->
          <tr v-if="analyses.length === 0">
            <td :colspan="7" class="px-3 md:px-6 py-8 text-center text-gray-500">
              <div class="flex flex-col items-center space-y-2">
                <svg class="w-8 h-8 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
                </svg>
                <p class="text-sm font-medium">No hay análisis disponibles</p>
                <p class="text-xs text-gray-400">Intenta ajustar los filtros o agregar nuevos análisis</p>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Paginación -->
    <div class="bg-gray-50 px-3 md:px-6 py-3 md:py-4 border-t border-gray-100 flex items-center justify-between">
      <div class="flex-1 flex justify-between sm:hidden">
        <button class="relative inline-flex items-center px-3 md:px-4 py-2 border border-gray-300 text-xs md:text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors duration-200">
          Anterior
        </button>
        <button class="ml-3 relative inline-flex items-center px-3 md:px-4 py-2 border border-gray-300 text-xs md:text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors duration-200">
          Siguiente
        </button>
      </div>
      <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
        <div>
          <p class="text-xs md:text-sm text-gray-700">
            Mostrando <span class="font-medium">1</span> a <span class="font-medium">{{ analyses.length }}</span> de <span class="font-medium">{{ totalItems }}</span> resultados
          </p>
        </div>
        <div>
          <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
            <button class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-xs md:text-sm font-medium text-gray-500 hover:bg-gray-50 transition-colors duration-200">
              <span class="sr-only">Anterior</span>
              <svg class="h-4 w-4 md:h-5 md:w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
            <button class="relative inline-flex items-center px-3 md:px-4 py-2 border border-gray-300 bg-white text-xs md:text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors duration-200">
              1
            </button>
            <button class="relative inline-flex items-center px-3 md:px-4 py-2 border border-gray-300 bg-white text-xs md:text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors duration-200">
              2
            </button>
            <button class="relative inline-flex items-center px-3 md:px-4 py-2 border border-gray-300 bg-white text-xs md:text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors duration-200">
              3
            </button>
            <button class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-xs md:text-sm font-medium text-gray-500 hover:bg-gray-50 transition-colors duration-200">
              <span class="sr-only">Siguiente</span>
              <svg class="h-4 w-4 md:h-5 md:w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
          </nav>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AnalysisTable',
  props: {
    analyses: {
      type: Array,
      required: true,
      default: () => []
    },
    totalItems: {
      type: Number,
      default: 0
    }
  },
  methods: {
    getStatusClasses(status) {
      const classes = {
        'Aceptado': 'bg-green-100 text-green-800',
        'Condicional': 'bg-yellow-100 text-yellow-800',
        'Rechazado': 'bg-red-100 text-red-800'
      };
      return classes[status] || 'bg-gray-100 text-gray-800';
    },
    getQualityColor(quality) {
      if (quality >= 80) return 'bg-green-600';
      if (quality >= 60) return 'bg-yellow-500';
      return 'bg-red-600';
    }
  }
};
</script>

<style scoped>
/* Mejoras de responsividad para la tabla de análisis */
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
  
  /* Ocultar columnas menos importantes en móviles */
  .mobile-hidden {
    display: none;
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
  
  .rounded-xl {
    border-radius: 0.5rem;
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
  th, td {
    min-height: 44px;
  }
  
  .overflow-x-auto {
    -webkit-overflow-scrolling: touch;
  }
}

/* Efectos de hover mejorados */
tbody tr:hover {
  background-color: #f9fafb;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

/* Animación de entrada para filas */
tbody tr {
  animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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

/* Estados de selección */
tbody tr.selected {
  background-color: #eff6ff;
  border-left: 3px solid #3b82f6;
}

/* Estados de carga */
.loading tbody tr {
  opacity: 0.6;
  pointer-events: none;
}

/* Mejoras para accesibilidad */
th:focus-visible,
td:focus-visible {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}

/* Scrollbar personalizado */
.overflow-x-auto::-webkit-scrollbar {
  height: 6px;
}

.overflow-x-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Mejoras para enlaces de acciones */
a {
  transition: all 0.2s ease-in-out;
}

a:hover {
  transform: translateY(-1px);
}
</style>
